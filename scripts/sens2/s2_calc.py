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
