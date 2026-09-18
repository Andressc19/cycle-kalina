"""Adapter de la mezcla NH3-H2O sobre el motor portado del proyecto hermano.

El motor vive en `_nh3h2o_engine.py` (IAPWS G4-01, Tillner-Roth & Friend 1998,
clase `iapws.ammonia.H2ONH3` con correcciones) y `_kalina_flash.py` (flash
T,P,w -> h,s,fase,q y su inversión h/s -> T). Este adapter envuelve ese motor
detrás de la interfaz canónica `PropertyBackend` (P en kPa, T en K, h en
kJ/kg, s en kJ/kg·K, x = fracción másica de NH3) y traduce las unidades en la
frontera: el motor usa P en **MPa** (P_kPa / 1000) y la misma composición
másica que la interfaz.

Es el **camino real** para todo cálculo de la mezcla NH3-H2O (ver CONTEXT.md):
pyfluids/CoolProp no cubre el par binario amoníaco-agua en este entorno y el
solver nunca debería importar `iapws`/el motor directamente, solo esta interfaz.
"""

from __future__ import annotations

import math
from typing import Optional

from .adapter import PropertyBackend, PropertyRangeError
from . import _kalina_flash as _kf
from . import _nh3h2o_engine as _ng

__all__ = ["AmmoniaWaterAdapter"]

_KPA_PER_MPA = 0.001


class AmmoniaWaterAdapter(PropertyBackend):
    """Propiedades de la mezcla NH3-H2O vía el motor portado (IAPWS G4-01).

    ``x`` es la composición por defecto de la instancia: si una llamada no pasa
    ``x``, se usa ese valor. Combos soportados: ``(P, T, x)``, ``(P, s, x)``,
    ``(P, h, x)``, ``bubble_point`` y ``dew_point``. El parámetro ``quality`` de
    la interfaz no se acepta como entrada: el título q se obtiene como salida de
    ``estado()`` del motor; invertir h(P, quality, x) costaría ~25 s por estado.
    Los errores de dominio del motor portado (``RuntimeError``/``ValueError``)
    se envuelven en ``PropertyRangeError``; los argumentos inválidos lanzan
    ``ValueError`` directo y los combos no soportados ``NotImplementedError``.
    """

    def __init__(self, x: float = 0.5):
        if not 0.0 < x < 1.0:
            raise ValueError(
                f"x (fracción másica de NH3) debe estar en (0, 1); se recibió {x!r}."
            )
        self._x = float(x)

    # -- helpers ---------------------------------------------------------------

    @staticmethod
    def _mpa(P: float) -> float:
        """Valida P en kPa y la convierte a MPa (unidad del motor portado)."""
        if P is None or not math.isfinite(P) or P <= 0:
            raise ValueError(f"P debe ser un número positivo [kPa]; se recibió {P!r}.")
        return P * _KPA_PER_MPA

    @staticmethod
    def _validar_w(w: float) -> float:
        if w is None or not math.isfinite(w) or not 0.0 < w < 1.0:
            raise ValueError(
                f"x (fracción másica de NH3) debe estar en (0, 1); se recibió {w!r}."
            )
        return float(w)

    def _w(self, x: Optional[float]) -> float:
        return self._validar_w(self._x if x is None else x)

    @staticmethod
    def _wrap(fn, what: str):
        """Ejecuta una llamada al motor portado envolviendo sus errores de dominio.

        ``RuntimeError`` (equilibrio no resoluble) y ``ValueError`` (sin raíz de
        vapor/líquido, dominio fuera de la campana, brentq sin cambio de signo)
        se convierten en ``PropertyRangeError``; nunca se propagan crudos. Los
        ``ValueError`` de validación de argumentos se lanzan ANTES de llegar aquí.
        """
        try:
            return fn()
        except PropertyRangeError:
            raise
        except (RuntimeError, ValueError, NotImplementedError) as exc:
            raise PropertyRangeError(
                f"{what}: el motor NH3-H2O portado no cubre el estado pedido "
                f"(ver CONTEXT.md, IAPWS G4-01). Detalle del motor: {exc}"
            ) from exc

    # -- interfaz PropertyBackend ---------------------------------------------

    def h(self, P: float, T: Optional[float] = None, x: Optional[float] = None,
          s: Optional[float] = None, quality: Optional[float] = None) -> float:
        mpa = self._mpa(P)
        w = self._w(x)
        if T is not None:
            return self._wrap(lambda: _kf.estado(T, mpa, w)["h"], "h(P, T, x)")
        if s is not None:
            return self._wrap(lambda: _kf.estado_de(mpa, w, s=s)["h"], "h(P, s, x)")
        if quality is not None:
            if not math.isfinite(quality) or not 0.0 <= quality <= 1.0:
                raise ValueError(
                    f"quality (título másico) debe estar en [0, 1]; se recibió "
                    f"{quality!r}."
                )
            raise NotImplementedError(
                "AmmoniaWaterAdapter no acepta el parámetro quality como entrada: "
                "el motor portado resuelve (P, T, x) y (P, h/s, x), y la "
                "inversión h(P, quality, x) requiere un brentq sobre flash de "
                "equilibrio de ~25 s por estado (medido). El solver no lo "
                "necesita: el título q se obtiene como salida de estado(). Use "
                "(P, T, x) o (P, s, x)."
            )
        raise ValueError(
            "Estado de la mezcla NH3-H2O incompleto — se requiere (P, T, x) o "
            "(P, s, x), con P en kPa, T en K, h en kJ/kg y s en kJ/kg·K. El "
            "parámetro quality no es soportado por este adapter (NotImplementedError)."
        )

    def s(self, P: float, T: Optional[float] = None, x: Optional[float] = None) -> float:
        if T is None:
            raise ValueError(
                "s(P, T, x): se requiere T [K] para evaluar la entropía de la "
                "mezcla NH3-H2O."
            )
        mpa = self._mpa(P)
        w = self._w(x)
        return self._wrap(lambda: _kf.estado(T, mpa, w)["s"], "s(P, T, x)")

    def T_from_Ph(self, P: float, h: float, x: Optional[float] = None) -> float:
        if h is None:
            raise ValueError("T_from_Ph: se requiere h [kJ/kg].")
        mpa = self._mpa(P)
        w = self._w(x)
        return self._wrap(lambda: _kf.estado_de(mpa, w, h=float(h))["T"],
                          "T_from_Ph(P, h, x)")

    def T_from_Ps(self, P: float, s: float, x: Optional[float] = None) -> float:
        if s is None:
            raise ValueError("T_from_Ps: se requiere s [kJ/kg·K].")
        mpa = self._mpa(P)
        w = self._w(x)
        return self._wrap(lambda: _kf.estado_de(mpa, w, s=float(s))["T"],
                          "T_from_Ps(P, s, x)")

    def bubble_point(self, P: float, x: float) -> float:
        mpa = self._mpa(P)
        w = self._validar_w(x)
        return self._wrap(lambda: _ng.bubbleT(mpa, _ng.w2m(w))[0],
                          "bubble_point(P, x)")

    def dew_point(self, P: float, x: float) -> float:
        mpa = self._mpa(P)
        w = self._validar_w(x)
        return self._wrap(lambda: _ng.dewT(mpa, _ng.w2m(w))[0],
                          "dew_point(P, x)")

    def equilibrio_liquido_vapor(self, P: float, T: float) -> tuple[float, float]:
        """Flash (P, T) → (x_liquido, x_vapor) másicos (ver PropertyBackend)."""
        mpa = self._mpa(P)
        par = self._wrap(lambda: _kf.flash_TP(T, mpa),
                         "equilibrio_liquido_vapor(P, T)")
        if par is None:
            raise PropertyRangeError(
                f"equilibrio_liquido_vapor(P={P} kPa, T={T} K): no existe "
                "equilibrio bifásico para ninguna composición (T fuera de la "
                "campana binaria a esa P, motor IAPWS G4-01)."
            )
        xL_molar, xV_molar = par
        return _ng.m2w(float(xL_molar)), _ng.m2w(float(xV_molar))