"""M4 — PAWN (10 franjas) y PRCC (rangos, residuos y prueba t), MATEMATICA §6.3-6.4.

**PAWN:** sobre η de los genuinos con `Wnet > 0` y sobre D de los genuinos, el
rango de `u_i` se divide en 10 franjas; en cada una, `KS_{i,c}` compara la CDF
de y de toda la muestra con la CDF de y solo en esa franja. El índice de la
variable es `T_i = mediana_c KS_{i,c}` (y el máximo).

**PRCC:** cada valor se reemplaza por su rango; los residuos de la variable i y
de la salida, una vez quitado por regresión lineal lo que explican las otras 9,
dan `PRCC_i = corr(r_x, r_y)`. Significancia con
`t = PRCC·√[(n−2−p)/(1−PRCC²)]`, p = 9 variables de control; el IC95 % usa
`t_{0.975}` con n−2−p grados de libertad.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import ks_2samp, rankdata, t as tdist

from m4_datos import VARS10, genu, u_de

N_FRANJAS = 10
P_CTRL = 9
CPAWN = ["salida", "variable", "n", *[f"ks_f{c + 1}" for c in range(N_FRANJAS)],
         "franjas_vacias", "T_mediana", "T_max"]
CPRCC = ["salida", "variable", "n", "prcc", "t", "p_valor", "ic_lo", "ic_hi"]


def poblas(filas: list) -> dict:
    """Las cuatro poblaciones del PRCC (η y cada margen)."""
    eta = [f for f in filas if genu(f) and f["eta"] is not None
           and f["Wnet"] is not None and f["Wnet"] > 0]
    return {"eta": (eta, "eta"),
            "m_O1": ([f for f in filas if genu(f) and f["m_O1"] is not None], "m_O1"),
            "m_O2": ([f for f in filas if genu(f) and f["m_O2"] is not None], "m_O2"),
            "m_O5": ([f for f in filas if genu(f) and f["m_O5"] is not None], "m_O5")}


def poblas_pawn(filas: list) -> dict:
    """Las dos poblaciones del PAWN: η (genuinos con W_net > 0) y D (genuinos)."""
    eta = [f for f in filas if genu(f) and f["eta"] is not None
           and f["Wnet"] is not None and f["Wnet"] > 0]
    dd = [f for f in filas if genu(f) and f["D"] is not None]
    return {"eta": (eta, "eta"), "D": (dd, "D")}


def _ks(a: np.ndarray, b: np.ndarray):
    if len(b) < 1 or len(a) < 2:
        return None
    return float(ks_2samp(a, b).statistic)


def filas_pawn(filas: list) -> list:
    """Una fila por (salida, variable) con los 10 KS, la mediana y el máximo."""
    out = []
    for salida, (pob, clave) in poblas_pawn(filas).items():
        y = np.array([f[clave] for f in pob], dtype=float)
        for v in VARS10:
            u = np.array([u_de(f, v) for f in pob], dtype=float)
            ks = []
            for c in range(N_FRANJAS):
                sel = (u >= c / N_FRANJAS) & (u < (c + 1) / N_FRANJAS)
                if c == N_FRANJAS - 1:
                    sel = u >= c / N_FRANJAS
                ks.append(_ks(y, y[sel]))
            ok = [k for k in ks if k is not None]
            out.append(dict(salida=salida, variable=v, n=len(y),
                            **{f"ks_f{c + 1}": ks[c] for c in range(N_FRANJAS)},
                            franjas_vacias=N_FRANJAS - len(ok),
                            T_mediana=float(np.median(ok)) if ok else None,
                            T_max=max(ok) if ok else None))
    return out


def prcc_uno(xs: dict, y: np.ndarray):
    """`(PRCC, t, p, ic_lo, ic_hi)` de una variable contra la salida `y`."""
    n = len(y)
    dof = n - 2 - P_CTRL
    ry = rankdata(y)
    res = {}
    for v in VARS10:
        X = np.column_stack([np.ones(n)] +
                            [rankdata(np.array([xs[w][i] for i in range(n)]))
                             for w in VARS10 if w != v])
        rx = rankdata(np.array(xs[v], dtype=float))
        ex = rx - X @ np.linalg.lstsq(X, rx, rcond=None)[0]
        ey = ry - X @ np.linalg.lstsq(X, ry, rcond=None)[0]
        res[v] = (float(np.corrcoef(ex, ey)[0, 1])
                  if ex.std() > 0 and ey.std() > 0 else None)
    out = {}
    for v, r in res.items():
        if r is None or dof <= 0 or abs(r) >= 1.0:
            out[v] = (r, None, None, None, None)
            continue
        tt = r * np.sqrt(dof / (1.0 - r * r))
        se = np.sqrt((1.0 - r * r) / dof)
        ic = tdist.ppf(0.975, dof) * se
        out[v] = (r, float(tt), float(2.0 * tdist.sf(abs(tt), dof)),
                  max(-1.0, r - ic), min(1.0, r + ic))
    return out


def filas_prcc(filas: list) -> list:
    """Una fila por (salida, variable) con PRCC, t, valor p e IC95 %."""
    out = []
    for salida, (pob, clave) in poblas(filas).items():
        y = np.array([f[clave] for f in pob], dtype=float)
        xs = {v: [f[v] for f in pob] for v in VARS10}
        for v, (r, tt, p, lo, hi) in prcc_uno(xs, y).items():
            out.append(dict(salida=salida, variable=v, n=len(y), prcc=r, t=tt,
                            p_valor=p, ic_lo=lo, ic_hi=hi))
    return out
