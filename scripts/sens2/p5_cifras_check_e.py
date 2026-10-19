# -*- coding: utf-8 -*-
"""Sens2 P5 - controles extra (etapa B): D9 (pisos de 25 kPa) y M7 (mejora frente al muestreado), recalculados con pandas desde los CSV crudos.

D9: el piso refinado de cada (centro, x_b) se recalcula de las filas PISOS de `s2b_filas.csv` como el menor P_baja desde el cual todos los puntos corridos
hasta el piso de la malla (el menor P_baja KALINA de la malla, tomado de `p6_pisos25.csv`) son KALINA; se comprueban la mediana y el maximo de la mejora.
M7: la mejora de cada banda de T_fuente (eta maxima de la busqueda menos el maximo muestreado en la ventana [T-10, T+10) K de `p2_dataset_dedup.csv`) se
recalcula de las filas crudas `s2b_opt_*.csv`, y se comprueban el minimo y el maximo de las 12 bandas.
"""
import glob

import numpy as np
import pandas as pd


def extra9(chk, ev, sub, P):
    f = pd.read_csv(P("2026-10-18_sens2_B", "s2b_filas.csv"))
    f = f[f["barrido"] == "PISOS"]
    malla = pd.read_csv(P("2026-10-18_sens2_F1", "p6_pisos25.csv"))
    mej = []
    for r in malla.itertuples():
        g = f[(f["centro"] == r.centro) & ((f["x_b"] - r.x_b).abs() < 1e-6)].sort_values("P_baja", ascending=False)
        ref = float(r.piso_malla)
        for p, c in zip(g["P_baja"], g["clasificacion"]):
            if c != "KALINA":
                break
            ref = float(p)
        mej.append(float(r.piso_malla) - ref)
    mej = np.array(mej)
    t = ev("D9", "afirmacion") + " " + ev("D9")
    ok = sub(t, float(mej.max()), "%.0f") and sub(t, float(np.median(mej)), "%.0f") and sub(t, int((mej > 0).sum()), "%d") and sub(t, len(mej), "%d")
    chk("D", "D9b", ok, "mejora de los 12 pisos recalculada: maxima %.0f, mediana %.0f kPa, %d de %d con mejora" % (mej.max(), np.median(mej), (mej > 0).sum(), len(mej)))

    o = pd.concat([pd.read_csv(x) for x in glob.glob(P("2026-10-18_sens2_B", "s2b_opt_*.csv"))], ignore_index=True)
    k = o[o["clasificacion"] == "KALINA"]
    d = pd.read_csv(P("2026-10-17_sens2_P2", "p2_dataset_dedup.csv"))
    d = d[d["clasificacion"] == "KALINA"]
    mejoras = []
    for b, g in k.groupby("banda"):
        ref = d[(d["T_fuente"] >= b - 10.0) & (d["T_fuente"] < b + 10.0)]["eta_pct"]
        if len(ref):
            mejoras.append(100.0 * float(g["eta"].max()) - float(ref.max()))
    t7 = ev("M7", "afirmacion") + " " + ev("M7")
    chk("M", "M7b", sub(t7, min(mejoras), "%+.2f") and sub(t7, max(mejoras), "%+.2f"),
        "mejora frente al muestreado (ventana semiabierta): %+.2f a %+.2f puntos en %d bandas" % (min(mejoras), max(mejoras), len(mejoras)))
