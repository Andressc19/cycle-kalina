"""Adapter de la mezcla NH3-H2O sobre `teqp` (Tillner-Roth & Friend 1998),
alternativa más rápida a `AmmoniaWaterAdapter` (el motor `iapws` portado
sigue siendo el camino real por defecto del proyecto — ver CONTEXT.md).

Validado en TASK_CONTEXT 2026-09-18-validar-teqp-nh3h2o contra
`AmmoniaWaterAdapter`: error <0.5% en h/s (un offset de referencia
constante entre bases de datos termodinámicas, se cancela en Δh/Δs de
cualquier cálculo de ciclo) y <0.01% en presiones/temperaturas de
saturación, con ~20x menos tiempo de cómputo por estado. No exhaustivamente
validado contra las Tablas IAPWS G4-01 (a diferencia del motor `iapws`) —
úsese como alternativa experimental de rendimiento, no como reemplazo del
camino real sin verificación adicional del usuario.

Motor en `_teqp_engine.py` (propiedades puntuales) y `_teqp_flash.py`
(equilibrio líquido-vapor). Mismas unidades canónicas que el resto del
proyecto: P en kPa, T en K, h en kJ/kg, s en kJ/kg·K, x = fracción másica
de NH3.
"""

from __future__ import annotations

import math
from typing import Optional

from scipy.optimize import brentq

from .adapter import PropertyBackend, PropertyRangeError
from . import _teqp_engine as _te
from . import _teqp_flash as _tf

__all__ = ["TeqpAdapter"]

_PA_PER_KPA = 1000.0


class TeqpAdapter(PropertyBackend):
    """Propiedades de la mezcla NH3-H2O vía `teqp.AmmoniaWaterTillnerRoth`."""

    def __init__(self, x: float = 0.5):
        if not 0.0 < x < 1.0:
            raise ValueError(
                f"x (fracción másica de NH3) debe estar en (0, 1); se recibió {x!r}."
            )
        self._x = float(x)

    # -- helpers ---------------------------------------------------------------

    @staticmethod
    def _pa(P: float) -> float:
        if P is None or not math.isfinite(P) or P <= 0:
            raise ValueError(f"P debe ser un número positivo [kPa]; se recibió {P!r}.")
        return P * _PA_PER_KPA

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
        try:
            return fn()
        except PropertyRangeError:
            raise
        except (RuntimeError, ValueError, NotImplementedError) as exc:
            raise PropertyRangeError(
                f"{what}: el motor teqp no cubre el estado pedido "
                f"(ver TASK_CONTEXT 2026-09-18-validar-teqp-nh3h2o). "
                f"Detalle: {exc}"
            ) from exc

    def _T_de(self, P_pa: float, w: float, *, h: Optional[float] = None,
             s: Optional[float] = None) -> float:
        """Inversión T tal que estado(T,P,x)[campo] == valor dado (h o s, J/mol)."""
        x = _te.w2m(w)
        campo, val = ("h", h) if h is not None else ("s", s)
        f = lambda T: _tf.estado(T, P_pa, x)[campo] - val
        lo, hi, paso = 230.0, 650.0, 0.0
        flo, fhi = f(lo), f(hi)
        if flo > 0 or fhi < 0:
            raise ValueError(f"{campo}={val:.6g} fuera de dominio a P={P_pa:.5g} Pa, x={x:.4f}")
        T = brentq(f, lo, hi, xtol=1e-6)
        return T

    # -- interfaz PropertyBackend ---------------------------------------------

    def h(self, P: float, T: Optional[float] = None, x: Optional[float] = None,
          s: Optional[float] = None, quality: Optional[float] = None) -> float:
        pa = self._pa(P)
        w = self._w(x)
        if T is not None:
            def calc():
                x_molar = _te.w2m(w)
                h_j_mol = _tf.estado(T, pa, x_molar)["h"]
                return h_j_mol / _te.Mm(x_molar)  # J/mol / (g/mol) = kJ/kg
            return self._wrap(calc, "h(P, T, x)")
        if s is not None:
            def calc():
                x_molar = _te.w2m(w)
                s_j_molK = s * _te.Mm(x_molar)  # kJ/kg-K -> J/mol-K
                T_sol = self._T_de(pa, w, s=s_j_molK)
                return _tf.estado(T_sol, pa, x_molar)["h"] / _te.Mm(x_molar)
            return self._wrap(calc, "h(P, s, x)")
        if quality is not None:
            raise NotImplementedError(
                "TeqpAdapter no acepta el parámetro quality como entrada directa "
                "(igual que AmmoniaWaterAdapter): use (P, T, x) o (P, s, x)."
            )
        raise ValueError(
            "Estado de la mezcla NH3-H2O incompleto — se requiere (P, T, x) o "
            "(P, s, x), con P en kPa, T en K, h en kJ/kg y s en kJ/kg·K."
        )

    def s(self, P: float, T: Optional[float] = None, x: Optional[float] = None) -> float:
        if T is None:
            raise ValueError("s(P, T, x): se requiere T [K].")
        pa = self._pa(P)
        w = self._w(x)

        def calc():
            x_molar = _te.w2m(w)
            return _tf.estado(T, pa, x_molar)["s"] / _te.Mm(x_molar)
        return self._wrap(calc, "s(P, T, x)")

    def T_from_Ph(self, P: float, h: float, x: Optional[float] = None) -> float:
        if h is None:
            raise ValueError("T_from_Ph: se requiere h [kJ/kg].")
        pa = self._pa(P)
        w = self._w(x)

        def calc():
            x_molar = _te.w2m(w)
            return self._T_de(pa, w, h=float(h) * _te.Mm(x_molar))
        return self._wrap(calc, "T_from_Ph(P, h, x)")

    def T_from_Ps(self, P: float, s: float, x: Optional[float] = None) -> float:
        if s is None:
            raise ValueError("T_from_Ps: se requiere s [kJ/kg·K].")
        pa = self._pa(P)
        w = self._w(x)

        def calc():
            x_molar = _te.w2m(w)
            return self._T_de(pa, w, s=float(s) * _te.Mm(x_molar))
        return self._wrap(calc, "T_from_Ps(P, s, x)")

    def bubble_point(self, P: float, x: float) -> float:
        pa = self._pa(P)
        w = self._validar_w(x)
        return self._wrap(lambda: _tf.bubbleT(pa, _te.w2m(w))[0], "bubble_point(P, x)")

    def dew_point(self, P: float, x: float) -> float:
        pa = self._pa(P)
        w = self._validar_w(x)
        return self._wrap(lambda: _tf.dewT(pa, _te.w2m(w))[0], "dew_point(P, x)")

    def equilibrio_liquido_vapor(self, P: float, T: float) -> tuple[float, float]:
        """Flash (P, T) → (x_liquido, x_vapor) másicos (ver PropertyBackend)."""
        pa = self._pa(P)
        par = self._wrap(lambda: _tf.flash_TP(T, pa), "equilibrio_liquido_vapor(P, T)")
        if par is None:
            raise PropertyRangeError(
                f"equilibrio_liquido_vapor(P={P} kPa, T={T} K): no existe "
                "equilibrio bifásico para ninguna composición (T fuera de la "
                "campana binaria a esa P, motor teqp)."
            )
        xL_molar, xV_molar = par
        return _te.m2w(xL_molar), _te.m2w(xV_molar)
