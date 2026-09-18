"""Motor NH3-H2O sobre `teqp` (Tillner-Roth & Friend 1998, mismo modelo
físico que IAPWS G4-01, vía `teqp.AmmoniaWaterTillnerRoth`) + CoolProp para
el gas ideal de los puros. Composición x = fracción MOLAR de amoníaco
(índice 0 del modelo — confirmado empíricamente contra CoolProp: el modelo
rechaza x=0 exactamente cuando el índice 0 es cero, ver TASK_CONTEXT
2026-09-18-validar-teqp-nh3h2o). Presiones en Pa, T en K.

Fórmulas verificadas por diferencias finitas y contra `_nh3h2o_engine.py`
(motor de referencia, validado contra IAPWS G4-01 en el proyecto hermano):
    P_total = R*T*rho + get_pr(T, rhovec)        [rhovec = x*rho, mol/m3]
    h_molar = R*T*(1 + Ar01 + Ar10 + Aig10)       [J/mol]
    s_molar = R*(Ar10 + Aig10 - Ar00 - Aig00)     [J/mol-K]
El residuo frente al motor de referencia (~1.3 kJ/kg en h, ~0.006 kJ/kg-K en
s, constante en todo el dominio probado) es un OFFSET de estado de
referencia entre bases de datos termodinámicas distintas, no un error de
física: se cancela en cualquier cálculo de ciclo (solo se usan diferencias
Δh, Δs). Presiones/temperaturas de saturación coinciden a <0.01%.

Búsqueda de raíces de densidad: la isoterma P(ρ) de este modelo tiene un
lazo de van der Waals con raíces espurias entre las ramas líquida y vapor
(ver TASK_CONTEXT). Se busca cada raíz desde un extremo físicamente
inequívoco hacia el centro (igual estrategia que `_nh3h2o_engine.rho_TPx`),
nunca con una semilla genérica en el medio.
"""

from __future__ import annotations

import json

import numpy as np
import teqp
import CoolProp.CoolProp as _CP
from scipy.optimize import brentq

__all__ = ["R", "M_A", "M_W", "w2m", "m2w", "P_total", "h_molar", "s_molar",
          "fugacity_coeffs", "Mm", "rho_liquido", "rho_vapor", "Psat_pure",
          "Tsat_pure"]

R = 8.314471  # J/mol-K
M_A, M_W = 17.03052, 18.01528  # g/mol NH3, H2O (mismos valores que Mm())


def w2m(w: float) -> float:
    """Fraccion masica de NH3 -> fraccion molar."""
    return (w / M_A) / ((w / M_A) + ((1.0 - w) / M_W))


def m2w(x: float) -> float:
    """Fraccion molar de NH3 -> fraccion masica."""
    return x * M_A / (x * M_A + (1.0 - x) * M_W)

_MODEL = teqp.AmmoniaWaterTillnerRoth()
_IDEAL = None


def _ideal_helmholtz():
    global _IDEAL
    if _IDEAL is not None:
        return _IDEAL

    def jig(fluido):
        j = json.loads(_CP.get_fluid_param_string(fluido, "JSON"))[0]
        return teqp.convert_CoolProp_idealgas(json.dumps(j), 0)

    _IDEAL = teqp.IdealHelmholtz([jig("Ammonia"), jig("Water")])
    return _IDEAL


def Mm(x: float) -> float:
    """Masa molar de la mezcla [g/mol] a fracción molar x de NH3."""
    return x * 17.03052 + (1.0 - x) * 18.01528


def P_total(T: float, rhovec) -> float:
    """Presión [Pa] a partir de T [K] y densidades molares parciales [mol/m3]."""
    rhovec = np.asarray(rhovec, dtype=float)
    return R * T * float(rhovec.sum()) + float(_MODEL.get_pr(T, rhovec))


def h_molar(T: float, rho: float, x: float) -> float:
    """Entalpía molar [J/mol] a T[K], densidad molar total rho[mol/m3], x molar NH3."""
    z = np.array([x, 1.0 - x])
    aig = _ideal_helmholtz()
    return R * T * (1.0 + _MODEL.get_Ar01(T, rho, z) + _MODEL.get_Ar10(T, rho, z)
                   + aig.get_Aig10(T, rho, z))


def s_molar(T: float, rho: float, x: float) -> float:
    """Entropía molar [J/mol-K]."""
    z = np.array([x, 1.0 - x])
    aig = _ideal_helmholtz()
    a10 = _MODEL.get_Ar10(T, rho, z) + aig.get_Aig10(T, rho, z)
    a00 = _MODEL.get_Ar00(T, rho, z) + aig.get_Aig00(T, rho, z)
    return R * (a10 - a00)


def fugacity_coeffs(T: float, rho: float, x: float) -> np.ndarray:
    """[phi_NH3, phi_H2O] a T[K], densidad molar total rho[mol/m3], x molar NH3."""
    z = np.array([x, 1.0 - x])
    return np.asarray(_MODEL.get_fugacity_coefficients(T, z * rho), dtype=float)


def rho_liquido(T: float, P_Pa: float, x: float) -> float:
    """Raíz de densidad molar [mol/m3] de la fase líquida a (T, P, x molar).

    Arranca en un extremo denso e inequívoco (60000 mol/m3, por encima de
    cualquier líquido NH3-H2O real) y reduce la densidad hasta un cambio de
    signo, para no caer en la región inestable intermedia de la isoterma.
    """
    z = np.array([x, 1.0 - x])
    g = lambda rho: P_total(T, z * rho) - P_Pa
    b = 60000.0
    while not np.isfinite(g(b)) or g(b) < 0:
        b -= 1000.0
        if b < 5000.0:
            raise ValueError(f"sin raiz de liquido (teqp): T={T:.2f} P={P_Pa:.5g} x={x:.4f}")
    a = b
    for _ in range(300):
        a *= 0.97
        v = g(a)
        if np.isfinite(v) and v < 0:
            return brentq(g, a, b, xtol=1e-6, rtol=1e-12)
        if a < 500.0:
            break
    raise ValueError(f"sin raiz de liquido (teqp): T={T:.2f} P={P_Pa:.5g} x={x:.4f}")


def rho_vapor(T: float, P_Pa: float, x: float) -> float:
    """Raíz de densidad molar [mol/m3] de la fase vapor a (T, P, x molar)."""
    z = np.array([x, 1.0 - x])
    g = lambda rho: P_total(T, z * rho) - P_Pa
    a = P_Pa / (R * T) * 0.98
    b = a
    for _ in range(200):
        b *= 1.06
        v = g(b)
        if not np.isfinite(v):
            b /= 1.06
            break
        if v > 0:
            return brentq(g, a, b, xtol=1e-6, rtol=1e-12)
    raise ValueError(f"sin raiz de vapor (teqp): T={T:.2f} P={P_Pa:.5g} x={x:.4f}")


_psat_cache: dict[float, tuple[float, float]] = {}

# Mismos limites y misma extrapolacion de Clausius-Clapeyron para NH3 que
# `_nh3h2o_engine.Psat_pure` (constante 2500, sin justificacion fisica mas
# alla de "semilla razonable de Raoult" en el motor original — se preserva
# tal cual, no se inventa una nueva). Agua: clamped al rango valido de
# CoolProp, igual que el motor original hace con IAPWS95.
_TC_NH3 = 405.3
_T_MIN_H2O, _T_MAX_H2O = 273.17, 646.9
_P_MIN_H2O, _P_MAX_H2O = 700.0, 2.2e7


def Psat_pure(T: float) -> tuple[float, float]:
    """Presiones de saturación [Pa] de NH3 y H2O puros a T[K] (init. Raoult)."""
    k = round(T, 6)
    if k in _psat_cache:
        return _psat_cache[k]
    pa = _CP.PropsSI("P", "T", min(T, _TC_NH3), "Q", 0, "Ammonia")
    if T > _TC_NH3:
        pa *= np.exp(-2500.0 * (1.0 / T - 1.0 / _TC_NH3))
    Tw = max(min(T, _T_MAX_H2O), _T_MIN_H2O)
    pw = _CP.PropsSI("P", "T", Tw, "Q", 0, "Water")
    _psat_cache[k] = (pa, pw)
    return pa, pw


def Tsat_pure(P_Pa: float) -> tuple[float, float]:
    """Temperaturas de saturación [K] de NH3 y H2O puros a P[Pa]."""
    if P_Pa < _CP.PropsSI("Pcrit", "Ammonia"):
        Ta = _CP.PropsSI("T", "P", P_Pa, "Q", 0, "Ammonia")
    else:
        Ta = _CP.PropsSI("Tcrit", "Ammonia")
    Pw = max(min(P_Pa, _P_MAX_H2O), _P_MIN_H2O)
    Tw = _CP.PropsSI("T", "P", Pw, "Q", 0, "Water")
    return Ta, Tw
