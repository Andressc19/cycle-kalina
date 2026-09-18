"""Equilibrio líquido-vapor NH3-H2O sobre `_teqp_engine`: mismo algoritmo
(sustitución sucesiva con inicialización de Raoult) que `_nh3h2o_engine.py`
`_flashP`/`bubbleP`/`dewP`/`_satT` y `_kalina_flash.py::flash_TP`, solo que
evaluando propiedades vía teqp en vez del motor `iapws` portado. Composición
molar de amoníaco en todo este módulo.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import brentq, fsolve

from . import _teqp_engine as ng

__all__ = ["bubbleP", "dewP", "bubbleT", "dewT", "flash_TP", "estado"]

DQ = 1e-3  # margen de calidad para clasificar liquido/vapor/bifasico


def _flashP(T: float, z: float, kind: str, tol: float = 1e-10, nmax: int = 300
           ) -> tuple[float, float, bool]:
    """kind='bub': z=x_liquido -> (P_burbuja, x_vapor, conv).
    kind='dew': z=x_vapor -> (P_rocio, x_liquido, conv)."""
    pa, pw = ng.Psat_pure(T)
    if kind == "bub":
        P = z * pa + (1 - z) * pw
        y = z * pa / P
    else:
        P = 1.0 / (z / pa + (1 - z) / pw)
        y = z * P / pa
    y = float(np.clip(y, 1e-8, 1 - 1e-8))
    P = max(P, 1e-3)
    for _ in range(nmax):
        xl, xv = (z, y) if kind == "bub" else (y, z)
        try:
            rL = ng.rho_liquido(T, P, xl)
            rV = ng.rho_vapor(T, P, xv)
            phiL = ng.fugacity_coeffs(T, rL, xl)
            phiV = ng.fugacity_coeffs(T, rV, xv)
            KA, KW = phiL[0] / phiV[0], phiL[1] / phiV[1]
        except Exception:
            return P, y, False
        if not (np.isfinite(KA) and np.isfinite(KW) and KA > 0 and KW > 0):
            return P, y, False
        if kind == "bub":
            S = z * KA + (1 - z) * KW
            yn = z * KA / S
        else:
            S = z / KA + (1 - z) / KW
            yn = (z / KA) / S
        Pn = P * S if kind == "bub" else P / S
        if not (np.isfinite(Pn) and np.isfinite(yn)):
            return P, y, False
        yn = float(np.clip(yn, 1e-8, 1 - 1e-8))
        Pn = max(Pn, 1e-3)
        err = abs(Pn - P) / P + abs(yn - y)
        P, y = 0.6 * P + 0.4 * Pn, 0.6 * y + 0.4 * yn
        if err < tol:
            return P, y, True
    return P, y, False


def bubbleP(T: float, x: float) -> tuple[float, float, bool]:
    return _flashP(T, x, "bub")


def dewP(T: float, x: float) -> tuple[float, float, bool]:
    return _flashP(T, x, "dew")


def _satT(P: float, x: float, kind: str) -> tuple[float, float, bool]:
    Ta, Tw = ng.Tsat_pure(P)
    lo, hi = Ta + 0.05, Tw - 0.05
    fl = bubbleP if kind == "bub" else dewP
    f = lambda T: fl(T, x)[0] - P
    T = brentq(f, lo, hi, xtol=1e-6)
    Pc, y, ok = fl(T, x)
    return T, y, ok


def bubbleT(P: float, x: float) -> tuple[float, float, bool]:
    return _satT(P, x, "bub")


def dewT(P: float, x: float) -> tuple[float, float, bool]:
    return _satT(P, x, "dew")


def flash_TP(T: float, P: float):
    """Equilibrio a (T,P) fijos: (x_liquido, x_vapor) molares, o None si no
    hay región bifásica a esa (T,P) para ninguna composición."""
    Ta, Tw = ng.Tsat_pure(P)
    if T <= Ta + 0.3 or T >= Tw - 0.3:
        return None
    pa, pw = ng.Psat_pure(T)
    raoult = float(np.clip((P - pw) / (pa - pw), 1e-4, 1 - 1e-4))
    raoult = (raoult, float(np.clip(raoult * pa / P, 1e-4, 1 - 1e-4)))

    def F(v):
        a = min(max(v[0], 1e-9), 1 - 1e-9)
        b = min(max(v[1], 1e-9), 1 - 1e-9)
        try:
            rL, rV = ng.rho_liquido(T, P, a), ng.rho_vapor(T, P, b)
            phiL, phiV = ng.fugacity_coeffs(T, rL, a), ng.fugacity_coeffs(T, rV, b)
        except ValueError:
            return [1e3, 1e3]
        return [np.log(a * phiL[0]) - np.log(b * phiV[0]),
               np.log((1 - a) * phiL[1]) - np.log((1 - b) * phiV[1])]

    sol, _, ier, _ = fsolve(F, list(raoult), full_output=True, xtol=1e-12)
    if ier != 1 or not (0 < sol[0] < sol[1] < 1):
        return None
    return float(sol[0]), float(sol[1])


def estado(T: float, P: float, x: float) -> dict:
    """Estado completo a (T, P, x molar): h,s [J/mol, J/mol-K], q, fase.

    Mismo criterio que `_kalina_flash.estado`: si (T,P) cae en la región
    bifásica del flash y x queda entre las composiciones de equilibrio,
    interpola por regla de la palanca; si no, resuelve como monofásico
    (probando líquido y luego vapor).
    """
    par = flash_TP(T, P)
    if par is not None:
        xL, xV = par
        if xL < x < xV:
            rL, rV = ng.rho_liquido(T, P, xL), ng.rho_vapor(T, P, xV)
            hL, sL = ng.h_molar(T, rL, xL), ng.s_molar(T, rL, xL)
            hV, sV = ng.h_molar(T, rV, xV), ng.s_molar(T, rV, xV)
            q = (x - xL) / (xV - xL)
            return dict(h=q * hV + (1 - q) * hL, s=q * sV + (1 - q) * sL,
                       q=q, fase="bifasico")
    try:
        rho = ng.rho_liquido(T, P, x)
        return dict(h=ng.h_molar(T, rho, x), s=ng.s_molar(T, rho, x),
                   q=0.0, fase="liquido")
    except ValueError:
        rho = ng.rho_vapor(T, P, x)
        return dict(h=ng.h_molar(T, rho, x), s=ng.s_molar(T, rho, x),
                   q=1.0, fase="vapor")
