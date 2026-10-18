# -*- coding: utf-8 -*-
"""Sens2 P3 - Paso 4b: verificacion (una linea OK/FALLA por control).

(a) n por bloque y respuesta coincide con el dataset deduplicado;
(b) indices finitos y en su rango; (c) dummy por debajo de las variables reales;
(d) celdas de malla = eje1 x eje2; (e) 1 - R^2 en [0,1]; (f) sin palabras prohibidas.
"""
import glob
import os
import sys

import numpy as np
import pandas as pd

import p3_comun as C

PROHIBIDAS = ["confiable", "no confiable", "no citable", "fuera de rango del motor"]


def esperado(g, modo):
    if modo == "todos":
        return len(g)
    if modo == "kalina":
        return int((g["clasificacion"] == "KALINA").sum())
    if modo == "kalina_rango":
        return int(((g["clasificacion"] == "KALINA") & (~g["fuera_rango"])).sum())
    return int((g["clasificacion"] == "CORREGIBLE").sum())


def control_a(dedup, ind):
    fallos = []
    for bl, est, centro in C.BLOQUES:
        g = dedup[(dedup["estudio"] == est) & (dedup["centro"] == centro)]
        for cod, lab, modo in C.RESPUESTAS:
            exp = esperado(g, modo)
            got = ind[(ind["bloque"] == bl) & (ind["respuesta"] == lab)]["n"].unique()
            if len(got) != 1 or int(got[0]) != exp:
                fallos.append("%s/%s esperado %d, hallado %s" % (bl, cod, exp, list(got)))
    return (len(fallos) == 0, fallos)


def control_b(ind):
    rangos = {"PRCC": (-1, 1), "PAWN": (0, 1), "PAWN_max": (0, 1), "delta": (0, 1),
              "eta2": (0, 1), "KS": (0, 1), "SRC_R2": (0, 1)}
    fallos = []
    for met, (lo, hi) in rangos.items():
        sub = ind[(ind["metodo"] == met) & ind["valor"].notna()]
        bad = sub[(sub["valor"] < lo - 1e-9) | (sub["valor"] > hi + 1e-9)]
        if len(bad):
            fallos.append("%s fuera de [%s,%s]: %d filas" % (met, lo, hi, len(bad)))
    for met, op in [("HSIC", "ge0"), ("LOGIT", "ge0")]:
        sub = ind[(ind["metodo"] == met) & ind["valor"].notna()]
        if len(sub) and (sub["valor"] < -1e-9).any():
            fallos.append("%s < 0" % met)
    return (len(fallos) == 0, fallos)


def control_c(rank):
    fallos = []
    for (bl, resp), gg in rank.groupby(["bloque", "respuesta"], sort=False):
        real = gg[gg["tipo"] == "real"]["rango_medio"].min()
        dum = gg[gg["tipo"] == "dummy"]["rango_medio"].min()
        if np.isfinite(real) and np.isfinite(dum) and dum < real:
            fallos.append("%s/%s mejor dummy (%.2f) < mejor real (%.2f)" % (bl, resp, dum, real))
        dd = gg[(gg["tipo"] == "dummy") & (gg["distinguible"])]
        if len(dd):
            fallos.append("%s/%s dummy marcada distinguible" % (bl, resp))
    return (len(fallos) == 0, fallos)


def control_d(inter):
    """Celdas halladas <= eje1 x eje2; los huecos son datos y se reportan."""
    fallos = []
    notas = []
    for _, r in inter.iterrows():
        exp, got = int(r["n_celdas_esperadas"]), int(r["n_celdas_ind"])
        if got > exp:
            fallos.append("%s/%s celdas %d > esperadas %d" % (r["par"], r["centro"], got, exp))
        elif got < exp:
            notas.append("nota: %s/%s faltan %d celdas de %d (hueco del muestreo, no de la malla)"
                         % (r["par"], r["centro"], exp - got, exp))
    return (len(fallos) == 0, fallos + notas)


def control_e(inter):
    fallos = []
    for col in ["noadit_eta", "noadit_ind"]:
        v = inter[col].to_numpy(float)
        v = v[np.isfinite(v)]
        if len(v) and ((v < -1e-9) | (v > 1 + 1e-9)).any():
            fallos.append("%s fuera de [0,1]" % col)
    return (len(fallos) == 0, fallos)


def control_f():
    fallos = []
    for f in glob.glob(os.path.join(C.P3, "*")):
        if not os.path.isfile(f):
            continue
        with open(f, encoding="utf-8", errors="ignore") as fh:
            txt = fh.read().lower()
        for w in PROHIBIDAS:
            if w in txt:
                fallos.append("%s contiene '%s'" % (os.path.basename(f), w))
    return (len(fallos) == 0, fallos)


def main():
    dedup = C.cargar_dedup()
    ind = pd.read_csv(os.path.join(C.P3, "p3_indices.csv"))
    rank = pd.read_csv(os.path.join(C.P3, "p3_ranking.csv"))
    inter = pd.read_csv(os.path.join(C.P3, "p3_interaccion.csv"))
    controles = [("a n por bloque/respuesta", control_a(dedup, ind)),
                 ("b indices finitos y en rango", control_b(ind)),
                 ("c dummy por debajo de reales", control_c(rank)),
                 ("d celdas de malla", control_d(inter)),
                 ("e 1-R2 en [0,1]", control_e(inter)),
                 ("f sin palabras prohibidas", control_f())]
    hay_falla = False
    for nombre, (ok, fallos) in controles:
        print("%s - %s" % ("OK" if ok else "FALLA", nombre))
        for x in fallos[:8]:
            print("    " + x)
        hay_falla = hay_falla or not ok
    sys.exit(1 if hay_falla else 0)


if __name__ == "__main__":
    main()
