"""`TeqpVerificado` — `TeqpAdapter` con respaldo del motor real SOLO en la zona
de riesgo (opción A de TASK_CONTEXT 2026-09-27-teqp-verificado). No modifica
el motor: es un envoltorio nuevo que se importa por ruta completa
(`from src.properties.teqp_verificado import TeqpVerificado`).

POR QUÉ EXISTE. `_teqp_flash._fase_monofasica`
(src/properties/_teqp_flash.py:138-140) decide la fase con un criterio barato:
si `T` queda fuera de la banda `Ta + 0.3 < T < Tw - 0.3` (Ta, Tw = Tsat de los
puros a esa P) devuelve `"liquido"` si `T <= Ta` y `"vapor"` si `T > Ta`, SIN
resolver el equilibrio L-V. En la franja `Ta < T <= Ta + 0.3` K eso solo es
correcto para mezcla casi pura: en mezclas muy ricas en NH3 (vapor de
turbina, x_molar ~0.976) la mezcla ahí es BIFÁSICA, `s(T)` deja de ser
creciente y la inversión por brentq de `TeqpAdapter._T_de` puede caer en una
raíz falsa sin que ningún criterio lo detecte (p. ej. la salida isentrópica de
turbina sale 139 kJ/kg mal en (x_b=0.60, P_alta=4000, T_fuente=394,
P_baja=423.914831 kPa)).

QUÉ HACE. Hereda de `TeqpAdapter` y, solo cuando el resultado de una llamada
cae en la zona de riesgo, repite ESA MISMA llamada con `AmmoniaWaterAdapter` y
devuelve su valor. Fuera de la zona devuelve exactamente lo de
`TeqpAdapter` (mismo código, mismo resultado bit a bit).

ZONA DE RIESGO (idéntica al prototipo medido en
`scripts/costo_soluciones_teqp.py`): con `Ta, Tw = _te.Tsat_pure(P_Pa)` y
`x_molar = _te.w2m(w)` (fracción molar de NH3; `w` es la másica de la interfaz):

    x_molar >= x_molar_rico  y |T - Ta| < umbral_K     (mezcla rica en NH3)
    x_molar <= x_molar_pobre y |T - Tw| < umbral_K     (mezcla pobre en NH3)

La T a evaluar es la que teqp invirtió (capturada en `_T_de`, sin repetir la
inversión) para `h(P, s, x)`, `T_from_Ph` y `T_from_Ps`; y la T de entrada para
`h(P, T, x)` y `s(P, T, x)` (chequeo posterior a la llamada, sin costo extra).
Si el motor real no cubre el estado, se devuelve el valor de teqp pero el
evento queda registrado con `fallo=True` y `verificacion_incompleta` pasa a
True: no se inventan valores.
"""

from __future__ import annotations

import time
from typing import Optional

from . import _teqp_engine as _te
from .adapter import PropertyRangeError
from .ammonia_water_adapter import AmmoniaWaterAdapter
from .teqp_adapter import TeqpAdapter

__all__ = ["TeqpVerificado"]

_PA_POR_KPA = 1000.0
# El motor real envuelve sus errores de dominio en PropertyRangeError; se
# aceptan también los crudos (RuntimeError/ValueError/NotImplementedError del
# portado) y los aritméticos de numpy, para que un fallo suyo NUNCA tumbe la
# corrida: se registra y se devuelve el valor de teqp.
_EXC_REAL = (PropertyRangeError, RuntimeError, ValueError, NotImplementedError,
             ArithmeticError)


class TeqpVerificado(TeqpAdapter):
    """`TeqpAdapter` + respaldo del motor real en la zona de riesgo.

    Además de lo de `TeqpAdapter` expone `recurrencias` (un dict por llamada
    respaldada), `n_recurrencias`, `n_fallos`, `t_real` (segundos gastados en el
    motor real), `verificacion_incompleta` y `reiniciar_registro()`.
    """

    def __init__(self, x: float = 0.5, umbral_K: float = 1.0,
                 x_molar_rico: float = 0.9, x_molar_pobre: float = 0.1):
        super().__init__(x)
        self.umbral_K = float(umbral_K)
        self.x_molar_rico = float(x_molar_rico)
        self.x_molar_pobre = float(x_molar_pobre)
        self.recurrencias: list[dict] = []
        self.n_recurrencias = 0
        self.n_fallos = 0
        self.t_real = 0.0
        self._real: Optional[AmmoniaWaterAdapter] = None   # perezoso
        self._ultima: Optional[tuple] = None   # (P_Pa, w, T) última inversión

    # -- zona de riesgo --------------------------------------------------------

    def _criterio(self, P_pa: float, w: float, T: float):
        """None si (P_Pa, w, T) está fuera de zona; si no, (etiqueta, Ta, Tw, x_molar)."""
        Ta, Tw = _te.Tsat_pure(P_pa)
        xm = _te.w2m(w)
        if xm >= self.x_molar_rico and abs(T - Ta) < self.umbral_K:
            return "rico_NH3", Ta, Tw, xm
        if xm <= self.x_molar_pobre and abs(T - Tw) < self.umbral_K:
            return "pobre_NH3", Ta, Tw, xm
        return None

    # -- registro y respaldo ---------------------------------------------------

    @property
    def verificacion_incompleta(self) -> bool:
        """True si alguna recurrencia no pudo verificarse con el motor real."""
        return self.n_fallos > 0

    def reiniciar_registro(self) -> None:
        """Vacía `recurrencias`, los contadores y `verificacion_incompleta`."""
        self.recurrencias, self.n_recurrencias = [], 0
        self.n_fallos, self.t_real = 0, 0.0

    def _motor_real(self) -> AmmoniaWaterAdapter:
        """Instancia perezosa de `AmmoniaWaterAdapter` (solo si hace falta)."""
        if self._real is None:
            self._real = AmmoniaWaterAdapter(x=self._x)
        return self._real

    def _respaldo(self, metodo, P, w, T, origen, v_teqp, repetir):
        """Repite la llamada con el motor real si (P, w, T) cae en zona.

        `repetir` es un cierre sin argumentos que rehace la MISMA llamada; su
        resultado es el que se devuelve. Si el motor real falla se devuelve
        `v_teqp` y el evento queda con `fallo=True`.
        """
        crit = self._criterio(P * _PA_POR_KPA, w, T)
        if crit is None:
            return v_teqp
        etiqueta, Ta, Tw, xm = crit
        t0, valor, error = time.perf_counter(), None, ""
        try:
            valor = float(repetir())
        except _EXC_REAL as exc:
            error = f"{type(exc).__name__}: {exc}"[:120]
        dt = time.perf_counter() - t0
        self.n_recurrencias += 1
        self.n_fallos += 1 if error else 0
        self.t_real += dt
        self.recurrencias.append(dict(
            metodo=metodo, P=round(P, 6), x=round(w, 6), x_molar=round(xm, 6),
            T_teqp=round(T, 4), Ta=round(Ta, 4), Tw=round(Tw, 4),
            criterio=etiqueta, origen=origen, valor_teqp=round(v_teqp, 6),
            valor_real=None if valor is None else round(valor, 6),
            error=error, fallo=bool(error), t_real_s=round(dt, 4)))
        return v_teqp if valor is None else valor

    # -- captura de la T invertida (no cuesta una segunda inversión) -----------

    def _T_de(self, P_pa: float, w: float, *, h=None, s=None) -> float:
        T = super()._T_de(P_pa, w, h=h, s=s)
        self._ultima = (P_pa, w, T)
        return T

    def _T_invertida(self):
        """(T, w) de la inversión de esta llamada, o (None, None)."""
        return (None, None) if self._ultima is None else (self._ultima[2], self._ultima[1])

    # -- interfaz PropertyBackend (zona de riesgo) -----------------------------

    def h(self, P, T=None, x=None, s=None, quality=None) -> float:
        self._ultima = None
        v = super().h(P, T=T, x=x, s=s, quality=quality)
        if T is not None:
            return self._respaldo("h(P,T,x)", P, self._w(x), float(T), "T_entrada", v,
                                  lambda: self._motor_real().h(P, T=T, x=x))
        if s is not None:
            T_inv, w = self._T_invertida()
            if T_inv is not None:
                return self._respaldo("h(P,s,x)", P, w, T_inv, "T_invertida", v,
                                      lambda: self._motor_real().h(P, s=s, x=x))
        return v

    def s(self, P, T=None, x=None) -> float:
        self._ultima = None
        v = super().s(P, T=T, x=x)
        return self._respaldo("s(P,T,x)", P, self._w(x), float(T), "T_entrada", v,
                              lambda: self._motor_real().s(P, T=T, x=x))

    def T_from_Ph(self, P, h, x=None) -> float:
        self._ultima = None
        v = super().T_from_Ph(P, h, x)
        T_inv, w = self._T_invertida()
        if T_inv is None:
            return v
        return self._respaldo("T_from_Ph", P, w, T_inv, "T_invertida", v,
                              lambda: self._motor_real().T_from_Ph(P, h, x))

    def T_from_Ps(self, P, s, x=None) -> float:
        self._ultima = None
        v = super().T_from_Ps(P, s, x)
        T_inv, w = self._T_invertida()
        if T_inv is None:
            return v
        return self._respaldo("T_from_Ps", P, w, T_inv, "T_invertida", v,
                              lambda: self._motor_real().T_from_Ps(P, s, x))
