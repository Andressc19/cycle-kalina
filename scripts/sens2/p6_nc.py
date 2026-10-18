# -*- coding: utf-8 -*-
"""Sens2 F1 (1.3) - sensibilidad de la existencia (Y1) al tratamiento de NO_CONVERGIO.

Tres lecturas de cada LHS: NO_CONVERGIO como no KALINA (la usada hasta ahora), sin las filas NO_CONVERGIO (condicional a haber
convergido) y NO_CONVERGIO como KALINA (cota optimista). Compara los 3 primeros de cada bloque por rango medio de |PRCC| y KS.
Tambien: fraccion de NO_CONVERGIO por estudio y bloque, y la clase por cuartiles de T_fuente con IC de Wilson.
Salidas: p6_sens_nc.csv, p6_nc_cuartiles.csv, p6_nc_fraccion.csv, p6_sens_nc.md.
"""
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp, rankdata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p3_comun as C  # noqa: E402
import p3_metodos as M  # noqa: E402
import p6_comun as K  # noqa: E402

ESC = ["nc_como_no_kalina", "sin_nc", "nc_como_kalina"]


def escenario(g, esc):
    cl = g["clasificacion"]
    if esc == "sin_nc":
        g = g[cl != "NO_CONVERGIO"]
        return g, (g["clasificacion"] == "KALINA").astype(float).to_numpy()
    if esc == "nc_como_kalina":
        return g, cl.isin(["KALINA", "NO_CONVERGIO"]).astype(float).to_numpy()
    return g, (cl == "KALINA").astype(float).to_numpy()


def indices(g, y):
    X = g[K.REALES].to_numpy(float)
    pr = np.abs(M.prcc(X, y))
    ks = np.array([ks_2samp(X[y == 1, j], X[y == 0, j]).statistic if 0 < y.sum() < len(y) else np.nan for j in range(X.shape[1])])
    rk = (rankdata(-pr) + rankdata(-ks)) / 2.0
    return pr, ks, rk


def sensibilidad(bl):
    filas, veredicto = [], []
    for nombre, g0 in bl:
        top = {}
        for esc in ESC:
            g, y = escenario(g0, esc)
            pr, ks, rk = indices(g, y)
            for j, v in enumerate(K.REALES):
                filas.append([nombre, esc, v, len(g), float(y.mean()), float(pr[j]), float(ks[j]), float(rk[j])])
            top[esc] = [K.REALES[j] for j in np.argsort(rk)[:3]]
        base = set(top[ESC[0]])
        veredicto.append([nombre] + [", ".join(top[e]) for e in ESC] +
                         ["si" if set(top[e]) == base else "no" for e in ESC[1:]])
    return pd.DataFrame(filas, columns=["bloque", "escenario", "variable", "n", "frac_kalina", "prcc_abs", "ks", "rango_medio"]), \
        pd.DataFrame(veredicto, columns=["bloque", "top3_" + ESC[0], "top3_" + ESC[1], "top3_" + ESC[2],
                                         "igual_sin_nc", "igual_nc_como_kalina"])


def cuartiles(bl):
    filas = []
    for nombre, g in bl:
        q = pd.qcut(g["T_fuente"], 4, labels=False, duplicates="drop")
        for k in sorted(q.unique()):
            s = g[q == k]
            c = s["clasificacion"].value_counts()
            nk, nn, nc_, ni = (int(c.get(x, 0)) for x in ("KALINA", "NO_CONVERGIO", "CORREGIBLE", "INVIABLE"))
            conv = len(s) - nn
            lo, hi = K.wilson(nk, conv)
            filas.append([nombre, int(k) + 1, float(s["T_fuente"].min()), float(s["T_fuente"].max()), len(s), nk, nc_, ni, nn,
                          nk / len(s), nn / len(s), nk / conv if conv else np.nan, lo, hi, (nk + nn) / len(s)])
    return pd.DataFrame(filas, columns=["bloque", "cuartil_T_fuente", "T_min", "T_max", "n", "KALINA", "CORREGIBLE", "INVIABLE",
                                        "NO_CONVERGIO", "p_kalina_nc_cero", "p_nc", "p_kalina_si_convergio", "ic_lo", "ic_hi", "p_kalina_nc_uno"])


def fraccion():
    d = C.cargar_dedup()
    g = d.groupby(["estudio", "centro"])["clasificacion"].agg(n="size", nc=lambda s: int((s == "NO_CONVERGIO").sum())).reset_index()
    g["frac_nc"] = g["nc"] / g["n"]
    return g


def conductores(bl):
    """KS entre NO_CONVERGIO y el resto, por variable: que empuja a no converger."""
    filas = []
    for nombre, g in bl:
        nc = (g["clasificacion"] == "NO_CONVERGIO").to_numpy()
        for v in K.REALES:
            r = ks_2samp(g.loc[nc, v], g.loc[~nc, v]) if 3 < nc.sum() < len(g) - 3 else None
            filas.append([nombre, v, int(nc.sum()), np.nan if r is None else r.statistic, np.nan if r is None else r.pvalue])
    return pd.DataFrame(filas, columns=["bloque", "variable", "n_nc", "ks_nc_vs_resto", "p"])


def main():
    bl = K.bloques()
    s, ver = sensibilidad(bl)
    cu, fr, cond = cuartiles(bl), fraccion(), conductores(bl)
    os.makedirs(K.OUT, exist_ok=True)
    s.to_csv(os.path.join(K.OUT, "p6_sens_nc.csv"), index=False)
    ver.to_csv(os.path.join(K.OUT, "p6_nc_top3.csv"), index=False)
    cu.to_csv(os.path.join(K.OUT, "p6_nc_cuartiles.csv"), index=False)
    fr.to_csv(os.path.join(K.OUT, "p6_nc_fraccion.csv"), index=False)
    cond.to_csv(os.path.join(K.OUT, "p6_nc_conductores.csv"), index=False)
    md = ["# Sens2 F1 - NO_CONVERGIO y la existencia", "",
          "Tres lecturas de Y1 en cada LHS. Los 3 primeros se ordenan por el rango medio de |PRCC| y KS (1 = mayor).", "",
          "| bloque | 3 primeros (NO_CONVERGIO = no KALINA) | 3 primeros sin NO_CONVERGIO | 3 primeros (NO_CONVERGIO = KALINA) | igual sin NC | igual NC=KALINA |",
          "|---|---|---|---|---|---|"]
    md += ["| " + " | ".join(str(x) for x in r) + " |" for r in ver.values]
    md += ["", "## Clase por cuartil de T_fuente (LHS)", "",
           "| bloque | cuartil | T_fuente (K) | n | NO_CONVERGIO | P(KALINA), NC = 0 | P(KALINA) si convergio [IC] |", "|---|---|---|---|---|---|---|"]
    for r in cu.itertuples():
        md.append("| %s | %d | %.1f a %.1f | %d | %d | %.2f | %.2f [%.2f, %.2f] |" % (
            r.bloque, r.cuartil_T_fuente, r.T_min, r.T_max, r.n, r.NO_CONVERGIO, r.p_kalina_nc_cero, r.p_kalina_si_convergio, r.ic_lo, r.ic_hi))
    top = cond.sort_values("ks_nc_vs_resto", ascending=False).groupby("bloque").head(1)
    md += ["", "## Variable que mas separa NO_CONVERGIO del resto (KS)", "", "| bloque | variable | KS | n NO_CONVERGIO |", "|---|---|---|---|"]
    md += ["| %s | %s | %.2f | %d |" % (r.bloque, r.variable, r.ks_nc_vs_resto, r.n_nc) for r in top.itertuples()]
    with open(os.path.join(K.OUT, "p6_sens_nc.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
