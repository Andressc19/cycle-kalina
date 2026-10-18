# -*- coding: utf-8 -*-
"""Sens2 F1 (1.4, ampliacion del director) - la diferencia pareada de eta depende de la distancia al vecino KALINA.

Reusa `p6_pareado` (carga, normalizacion, vecino). Para cada CORREGIBLE de los 4 bloques con centro: d_eta = eta del
KALINA mas cercano - eta del CORREGIBLE, y la distancia L1 normalizada al vecino. Resume d_eta por tramos de distancia
y ajusta d_eta = a + b*L1 por minimos cuadrados (a = diferencia a distancia cero) con IC 95 % por bootstrap.
Salidas: p6_pareado_dist.csv y p6_pareado_dist.md.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p6_pareado as P  # noqa: E402

TRAMOS = [(0.0, 0.2), (0.2, 0.5), (0.5, 99.0)]


def pares_dist(d, M, variante):
    clave = ["centro"] if variante == "mismo_centro" else ["centro", "diseno"]
    filas = []
    for _, g in d[d["centro"].isin(P.CENTROS)].groupby(clave, sort=True):
        cor, kal = g[g["clasificacion"] == "CORREGIBLE"], g[g["kalina"]]
        if len(cor) == 0 or len(kal) == 0:
            continue
        v = P.vecino(M, cor.index.to_numpy(), kal.index.to_numpy())
        dist = np.abs(M[cor.index.to_numpy()] - M[v]).sum(axis=1)
        de = d["eta_pct"].to_numpy(float)[v] - cor["eta_pct"].to_numpy(float)
        for i in range(len(cor)):
            filas.append({"centro": cor["centro"].iloc[i], "diseno": cor["diseno"].iloc[i], "l1": dist[i], "d_eta": de[i]})
    r = pd.DataFrame(filas)
    return r[np.isfinite(r["d_eta"])].reset_index(drop=True)


def ajuste(l1, de, rng, B=1000):
    A = np.column_stack([np.ones(len(l1)), l1])
    coef = np.linalg.lstsq(A, de, rcond=None)[0]
    ba = []
    for _ in range(B):
        i = rng.integers(0, len(l1), len(l1))
        ba.append(np.linalg.lstsq(A[i], de[i], rcond=None)[0][0])
    return coef[0], coef[1], float(np.percentile(ba, 2.5)), float(np.percentile(ba, 97.5))


def main():
    d = P.cargar()
    M = P.matriz_norm(d)
    filas = []
    for variante in ("mismo_centro", "mismo_centro_y_diseno"):
        pp = pares_dist(d, M, variante)
        for nom, sub in [("todos", pp)] + [(x, pp[pp["diseno"] == x]) for x in P.DISENOS]:
            if len(sub) < 10:
                continue
            a, b, lo, hi = ajuste(sub["l1"].to_numpy(), sub["d_eta"].to_numpy(), np.random.default_rng(P.SEMILLA))
            filas.append([variante, nom, "ajuste", len(sub), np.nan, np.nan, a, lo, hi, b])
            for t0, t1 in TRAMOS:
                s = sub[(sub["l1"] >= t0) & (sub["l1"] < t1)]["d_eta"].to_numpy()
                if len(s) >= 5:
                    med, mlo, mhi, *_ = P.boot(s, np.random.default_rng(P.SEMILLA))
                    filas.append([variante, nom, "tramo L1 %.1f a %s" % (t0, "mas" if t1 > 50 else "%.1f" % t1), len(s), t0, t1, med, mlo, mhi, np.nan])
    t = pd.DataFrame(filas, columns=["variante", "grupo", "calculo", "n", "l1_min", "l1_max", "estimador", "ic_lo", "ic_hi", "pendiente"])
    t.to_csv(os.path.join(P.SALIDA, "p6_pareado_dist.csv"), index=False)
    md = ["# Sens2 F1 - la diferencia pareada de eta segun la distancia al vecino KALINA", "",
          "d_eta = eta del KALINA mas cercano - eta del CORREGIBLE. `ajuste`: d_eta = a + b*L1; el estimador es a (diferencia a distancia cero, pp de eta).",
          "`tramo`: mediana de d_eta en cada tramo de distancia L1 (normalizada). IC 95 %% por bootstrap (1000, semilla %d)." % P.SEMILLA, "",
          "| variante | grupo | calculo | n | estimador | IC 95 % |", "|---|---|---|---|---|---|"]
    md += ["| %s | %s | %s | %d | %.3f | [%.3f, %.3f] |" % (r.variante, r.grupo, r.calculo, r.n, r.estimador, r.ic_lo, r.ic_hi) for r in t.itertuples()]
    with open(os.path.join(P.SALIDA, "p6_pareado_dist.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
