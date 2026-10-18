# -*- coding: utf-8 -*-
"""Sens2 F1 - modulo comun de los calculos p6_*: bloques LHS, respuestas, caja comun, Wilson y Benjamini-Hochberg."""
import os
import sys

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
import p3_comun as C  # noqa: E402

OUT = os.path.join(RAIZ, "resultados", "2026-10-18_sens2_F1")
SEMILLA = 20261018
B_PERM = 2000
Q = 0.05
REALES = C.REALES
RESP = {"Y1": "Y1 KALINA (total)", "Y2": "Y2 eta (%)", "Y3": "Y3 W_net/m_b"}
FAMILIA = {"PRCC": "correlacion", "SRC": "correlacion", "PAWN": "dependencia", "delta": "dependencia",
           "HSIC": "dependencia", "eta2": "dependencia", "KS": "dependencia"}


def bloques(caja=False):
    """Lista de (nombre, DataFrame) con el LHS de cada bloque; con `caja`, solo las filas dentro de la caja comun."""
    d = C.cargar_dedup()
    bl = [(n, d[(d["estudio"] == e) & (d["centro"] == c)].reset_index(drop=True)) for n, e, c in C.BLOQUES]
    if not caja:
        return bl
    lo = {v: max(g[v].min() for _, g in bl) for v in REALES}
    hi = {v: min(g[v].max() for _, g in bl) for v in REALES}
    out = []
    for n, g in bl:
        m = np.ones(len(g), bool)
        for v in REALES:
            m &= ((g[v] >= lo[v]) & (g[v] <= hi[v])).to_numpy()
        out.append((n, g[m].reset_index(drop=True)))
    return out


def respuesta(g, cod):
    """(mascara, y) de la respuesta Y1 (todas las filas), Y2 o Y3 (solo KALINA)."""
    kal = (g["clasificacion"] == "KALINA").to_numpy()
    if cod == "Y1":
        return np.ones(len(g), bool), kal.astype(float)
    col = "eta_pct" if cod == "Y2" else "wnet_mb"
    return kal, g[col].to_numpy(float)


def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def bh(p):
    """q-valores de Benjamini-Hochberg (NaN se conservan)."""
    p = np.asarray(p, float)
    q = np.full(len(p), np.nan)
    ok = np.where(np.isfinite(p))[0]
    if len(ok) == 0:
        return q
    o = ok[np.argsort(p[ok])]
    m = len(o)
    vals = p[o] * m / np.arange(1, m + 1)
    vals = np.minimum.accumulate(vals[::-1])[::-1]
    q[o] = np.clip(vals, 0, 1)
    return q
