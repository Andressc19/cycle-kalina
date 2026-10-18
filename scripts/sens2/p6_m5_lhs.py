# -*- coding: utf-8 -*-
"""Sens2 F1 - M5 solo con el muestreo LHS: el 10 % de KALINA de mayor eta frente al resto, distancia a la frontera no-KALINA.

Reusa `p2_robustez.puntos_frontera` sobre las filas LHS (estudios 3 y 14). Dos normalizaciones: `completo` (limites del conjunto
completo, la del libro) y `lhs` (limites de las propias filas LHS). Por bloque: n, medianas, KS (scipy) y p, y p con Bonferroni (x4).
Salidas: p6_m5_lhs.csv y p6_m5_lhs.md.
"""
import os
import sys

import pandas as pd
from scipy.stats import ks_2samp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p2_comun as c  # noqa: E402
import p2_robustez as R  # noqa: E402
import p6_comun as K  # noqa: E402

BLOQUES = ["C1 Husavik", "C2 ancla A*", "C3 caliente 150 C", "C4 frio 110 C"]


def main():
    d = c.cargar_dedup()
    lhs = d[d["estudio"].isin([3, 14])].reset_index(drop=True)
    filas = []
    for norma, lim in (("completo", c.limites_normalizacion(d)), ("lhs", c.limites_normalizacion(lhs))):
        pt = R.puntos_frontera(lhs, lim)
        for b in BLOQUES:
            g = pt[pt["centro"] == b]
            top, resto = g[g["zona"] == "Top10"]["dist_frontera"], g[g["zona"] == "resto"]["dist_frontera"]
            p = float(ks_2samp(top, resto).pvalue) if len(top) and len(resto) else float("nan")
            filas.append([norma, b, len(top), len(resto), float(top.median()), float(resto.median()), p, min(1.0, 4 * p)])
    t = pd.DataFrame(filas, columns=["normalizacion", "bloque", "n_top", "n_resto", "mediana_top", "mediana_resto", "p_ks", "p_bonferroni4"])
    os.makedirs(K.OUT, exist_ok=True)
    t.to_csv(os.path.join(K.OUT, "p6_m5_lhs.csv"), index=False)
    md = ["# Sens2 F1 - M5 con el muestreo LHS solo", "",
          "Distancia L1 normalizada a la frontera no-KALINA del 10 % de KALINA de mayor eta frente al resto, por bloque, solo con las filas LHS (estudios 3 y 14).",
          "`completo` normaliza con los limites del conjunto completo (la del libro); `lhs`, con los de las propias filas LHS. KS de dos muestras; Bonferroni por 4 bloques.", "",
          "| normalizacion | bloque | n top | n resto | mediana top | mediana resto | p (KS) | p (Bonferroni x4) |", "|---|---|---|---|---|---|---|---|"]
    md += ["| %s | %s | %d | %d | %.2f | %.2f | %.3f | %.3f |" % tuple(r) for r in t.itertuples(index=False)]
    with open(os.path.join(K.OUT, "p6_m5_lhs.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
