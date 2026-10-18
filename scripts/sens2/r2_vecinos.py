# -*- coding: utf-8 -*-
"""Sens2 R2b - prediccion fuera de muestra: la clase (KALINA / no KALINA) de cada punto del libro viejo
(`r1_puntos.csv`) se predice con los k vecinos mas cercanos del dataset deduplicado de Sens2 (10 variables
normalizadas por su rango en Sens2, norma L1). Se compara con la clase mayoritaria como predictor trivial."""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_filtro import SALIDA, V10  # noqa: E402
from s2_cargar import dataset_dedup  # noqa: E402

K = 5


def main():
    s = dataset_dedup()
    p = pd.read_csv(os.path.join(SALIDA, "r1_puntos.csv"))
    lo, hi = s[V10].min().to_numpy(float), s[V10].max().to_numpy(float)
    A = (s[V10].to_numpy(float) - lo) / (hi - lo)
    B = (p[V10].to_numpy(float) - lo) / (hi - lo)
    ya = s["kalina"].to_numpy(bool)
    pred = np.zeros(len(p), bool)
    dmin = np.zeros(len(p))
    for i0 in range(0, len(p), 200):
        D = np.abs(B[i0:i0 + 200, None, :] - A[None, :, :]).sum(axis=2)
        idx = np.argsort(D, axis=1)[:, :K]
        pred[i0:i0 + 200] = ya[idx].mean(axis=1) > 0.5
        dmin[i0:i0 + 200] = np.take_along_axis(D, idx[:, :1], axis=1)[:, 0]
    real = (p["clasificacion"] == "KALINA").to_numpy(bool)
    p["pred_kalina"], p["dist_vecino"] = pred, dmin
    p[["id_punto", "Estudio", "centro", "dist", "clasificacion", "pred_kalina", "dist_vecino"]].to_csv(
        os.path.join(SALIDA, "r2_vecinos_puntos.csv"), index=False)
    q = np.quantile(dmin, [0.25, 0.5, 0.75])
    grupos = [("todos", np.ones(len(p), bool)), ("cerca (dist <= 0.15)", p["cerca"].to_numpy(bool)),
              ("vecino cercano (L1 <= P25)", dmin <= q[0]), ("vecino lejano (L1 > P75)", dmin > q[2])]
    for c in sorted(p["centro"].unique()):
        grupos.append(("centro " + c, (p["centro"] == c).to_numpy(bool)))
    filas = []
    for nom, m in grupos:
        n = int(m.sum())
        if n == 0:
            continue
        tp = int((pred & real & m).sum())
        fp = int((pred & ~real & m).sum())
        fn = int((~pred & real & m).sum())
        may = max(real[m].mean(), 1 - real[m].mean())
        filas.append([nom, n, float(real[m].mean()), float((pred == real)[m].mean()), float(may),
                      tp / (tp + fp) if tp + fp else np.nan, tp / (tp + fn) if tp + fn else np.nan])
    r = pd.DataFrame(filas, columns=["grupo", "n", "frac_kalina_real", "exactitud", "exactitud_clase_mayoritaria",
                                     "precision_kalina", "exhaustividad_kalina"])
    r.to_csv(os.path.join(SALIDA, "r2_vecinos_resumen.csv"), index=False)
    print("k = %d; distancia L1 al vecino mas cercano P25/P50/P75 = %.2f / %.2f / %.2f" % (K, *q))
    print(r.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
