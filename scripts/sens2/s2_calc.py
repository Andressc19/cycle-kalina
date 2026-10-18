# -*- coding: utf-8 -*-
"""Sens2 - s2_calc: calculos de las hojas `F1 Margenes de operacion` y `F4 Regenerador vs T_fuente`.

Todo sale de los CSV de Sensibilidad 1 (via `x1_cargar`); no se escribe ninguna cifra a mano.
"""
import math
import os
import sys

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))
sys.path.insert(0, AQUI)
import x1_cargar as X  # noqa: E402
from p3_interaccion import PARS, malla  # noqa: E402

VARS = ["T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond"]
UNI = {"T_fuente": "K", "T_sumidero": "K", "P_alta": "kPa", "P_baja": "kPa", "x_b": "-", "eta_t": "-",
       "eta_p": "-", "eps_hrvg": "-", "eps_reg": "-", "eps_cond": "-"}
BLOQUES = ["C1 Husavik", "C2 ancla A*", "C3 caliente 150 C", "C4 frio 110 C"]
ALCANCE = [(2, "C1 Husavik", ["B1", "B2", "B3", "B4", "B5", "B6"]),
           (2, "C2 ancla A*", ["B1", "B2", "B3", "B4", "B5", "B6"]),
           (11, "C3 caliente 150 C", ["B1", "B2", "B3", "B4"]),
           (11, "C4 frio 110 C", ["B1", "B2", "B3", "B4"])]
_CACHE = {}


def todo():
    if "d" not in _CACHE:
        _CACHE["d"] = X.cargar_todo()
    return _CACHE["d"]


def margenes_ofat():
    """Por bloque y variable: intervalo contiguo de KALINA alrededor del centro (barridos de una variable)."""
    d = todo()
    o = d[d["estudio"].isin([1, 10])]
    filas = []
    for b in BLOQUES:
        cen = X.CENTROS[b]
        for v in VARS:
            g = o[(o["centro"] == b) & ((o["variable"] == v) | (o["variable"] == "base"))]
            g = g.assign(_v=g[v].round(4)).sort_values("_v").drop_duplicates("_v")
            vals, kal = g["_v"].to_numpy(float), g["kalina"].to_numpy(bool)
            v0 = float(cen[v])
            i0 = int(np.argmin(np.abs(vals - v0)))
            lo = hi = i0
            while lo - 1 >= 0 and kal[lo - 1]:
                lo -= 1
            while hi + 1 < len(vals) and kal[hi + 1]:
                hi += 1
            rango = float(vals.max() - vals.min())
            filas.append({
                "bloque": b, "variable": v, "unidad": UNI[v], "v0": v0, "base_kalina": bool(kal[i0]),
                "ult_abajo": float(vals[lo]), "prim_no_abajo": float(vals[lo - 1]) if lo > 0 else None,
                "ult_arriba": float(vals[hi]), "prim_no_arriba": float(vals[hi + 1]) if hi + 1 < len(vals) else None,
                "rango": rango, "marg_abajo": (vals[lo] - v0) / rango * 100.0,
                "marg_arriba": (vals[hi] - v0) / rango * 100.0, "min_barrido": float(vals.min()),
                "max_barrido": float(vals.max()), "n_niveles": int(len(vals))})
    return pd.DataFrame(filas)


def pares_vecindad():
    """Por par y bloque: celdas de la malla con KALINA y vecindad 3 x 3 del centro (mover 2 variables un paso)."""
    d = todo()
    filas = []
    for est, b, pares in ALCANCE:
        g = d[(d["estudio"] == est) & (d["centro"] == b)].reset_index(drop=True)
        cen = X.CENTROS[b]
        for par in pares:
            a, c = PARS[par]
            _, ind, av, bv = malla(g, cen, a, c)
            fin = np.isfinite(ind)
            i0 = int(np.argmin(np.abs(av - cen[a])))
            j0 = int(np.argmin(np.abs(bv - cen[c])))
            vec = ind[max(i0 - 1, 0):i0 + 2, max(j0 - 1, 0):j0 + 2]
            vf = np.isfinite(vec)
            filas.append({"par": par, "bloque": b, "var1": a, "var2": c, "celdas": int(fin.sum()),
                          "n_kalina": int(np.nansum(ind)), "centro_kalina": bool(ind[i0, j0] == 1.0),
                          "vec_celdas": int(vf.sum()), "vec_kalina": int(np.nansum(vec))})
    return pd.DataFrame(filas)


def k_variables(dedup):
    """P(KALINA) segun cuantas de las 10 variables difieren del centro del bloque."""
    filas = []
    for b in BLOQUES:
        cen = X.CENTROS[b]
        g = dedup[dedup["centro"] == b]
        k = sum((g[v].round(2) != round(float(cen[v]), 2)).astype(int) for v in VARS)
        g = g.assign(k=k)
        for etq, lo, hi in (("1", 1, 1), ("2", 2, 2), ("3", 3, 3), ("4 a 6", 4, 6), ("7 a 9", 7, 9)):
            s = g[(g["k"] >= lo) & (g["k"] <= hi)]
            if len(s):
                filas.append({"bloque": b, "k": etq, "n": int(len(s)), "n_kalina": int(s["kalina"].sum()),
                              "p_kalina": float(s["kalina"].mean())})
    return pd.DataFrame(filas)


def regenerador(d):
    """Columnas derivadas del regenerador (contraflujo: 5->6 caliente, 10->1 frio)."""
    r = d.copy()
    dA, dB = r["T_e5"] - r["T_e1"], r["T_e6"] - r["T_e10"]
    ok = (dA > 0) & (dB > 0)
    lm = np.where(np.isclose(dA, dB), dA, (dA - dB) / np.log(np.where(ok, dA / dB.where(dB != 0), 1.0)))
    r["pinch"] = np.where(ok, np.minimum(dA, dB), np.nan)
    r["ua"] = np.where(ok, (r["Qreg"] / r["m_b"]) / lm, np.nan)
    r["t_c"] = r["T_fuente"] - 273.15
    r["qreg_qi2"] = r["Qreg"] / r["Qi"]
    return r


def barrido_fuente():
    """KALINA de los barridos de T_fuente (estudios 1 y 10) con metricas del regenerador."""
    d = todo()
    o = d[d["estudio"].isin([1, 10]) & ((d["variable"] == "T_fuente") | (d["variable"] == "base"))]
    o = regenerador(o).drop_duplicates(["centro", "T_fuente"])
    return o[o["centro"].isin(BLOQUES)]


def estudio4():
    """Estudio 4: T_fuente de 70 a 300 C con P_alta, P_baja, x_b y T_sumidero en muestreo (resto fijo)."""
    d = todo()
    return regenerador(d[d["estudio"] == 4])


def num(x, n=4):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return None
    return round(float(x), n)


def malla_clases(b, par):
    """Matriz de la malla de un par: (eta de KALINA, clase por celda, niveles a, niveles b)."""
    est = {"C1 Husavik": 2, "C2 ancla A*": 2, "C3 caliente 150 C": 11, "C4 frio 110 C": 11}[b]
    d = todo()
    g = d[(d["estudio"] == est) & (d["centro"] == b)].reset_index(drop=True)
    cen = X.CENTROS[b]
    a, c = PARS[par]
    mask = np.ones(len(g), bool)
    for v in VARS:
        if v not in (a, c):
            mask &= np.round(g[v].to_numpy(float), 2) == round(float(cen[v]), 2)
    sub = g[mask]
    av = np.sort(np.unique(np.round(sub[a].to_numpy(float), 2)))
    bv = np.sort(np.unique(np.round(sub[c].to_numpy(float), 2)))
    eta = np.full((len(av), len(bv)), np.nan)
    cls = np.full((len(av), len(bv)), "-", dtype=object)
    ia = {v: i for i, v in enumerate(av)}
    ib = {v: j for j, v in enumerate(bv)}
    for _, r in sub.iterrows():
        i, j = ia[np.round(r[a], 2)], ib[np.round(r[c], 2)]
        cls[i, j] = {"KALINA": "K", "CORREGIBLE": "C", "NO_CONVERGIO": "NC", "INVIABLE": "I"}[r["clasificacion"]]
        if r["clasificacion"] == "KALINA":
            eta[i, j] = r["eta_pct"]
    return eta, cls, av, bv


def ajuste_cuadratico(eta, av, bv):
    """Superficie cuadratica eta ~ a, b, a^2, b^2, ab sobre las celdas KALINA (variables estandarizadas)."""
    A, B = np.meshgrid(av, bv, indexing="ij")
    ok = np.isfinite(eta)
    a, b, y = A[ok], B[ok], eta[ok]
    if len(y) < 8:
        return None
    ma, sa, mb, sb = a.mean(), a.std() or 1.0, b.mean(), b.std() or 1.0
    za, zb = (a - ma) / sa, (b - mb) / sb
    M = np.column_stack([np.ones(len(y)), za, zb, za ** 2, zb ** 2, za * zb])
    coef, *_ = np.linalg.lstsq(M, y, rcond=None)
    res = y - M @ coef
    r2 = 1.0 - (res ** 2).sum() / ((y - y.mean()) ** 2).sum()
    p = M.shape[1]
    adj = 1.0 - (1.0 - r2) * (len(y) - 1) / (len(y) - p)
    ia, ib = np.unravel_index(np.nanargmax(np.where(ok, eta, -np.inf)), eta.shape)
    # maximo del ajuste sobre la malla completa (celdas KALINA y no KALINA) para ver hacia donde apunta
    za_g, zb_g = (A - ma) / sa, (B - mb) / sb
    Mg = np.stack([np.ones_like(za_g), za_g, zb_g, za_g ** 2, zb_g ** 2, za_g * zb_g], axis=-1)
    pred = Mg @ coef
    ig = np.unravel_index(np.argmax(pred), pred.shape)
    return {"n": int(len(y)), "r2": float(r2), "r2_aj": float(adj), "rmse": float(np.sqrt((res ** 2).mean())),
            "coef": [float(c) for c in coef], "max_malla": (float(av[ia]), float(bv[ib]), float(eta[ia, ib])),
            "max_ajuste": (float(av[ig[0]]), float(bv[ig[1]]), float(pred[ig]))}
