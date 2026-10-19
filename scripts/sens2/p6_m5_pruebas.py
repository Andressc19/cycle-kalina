# -*- coding: utf-8 -*-
"""Sens2 F1 - M5 con dos pruebas: el 10 % de KALINA de mayor eta frente al resto, distancia a la frontera no-KALINA.

Copia el patron de `p6_m5_lhs.py`: reusa `p2_robustez.puntos_frontera` sobre las filas LHS (estudios 3 y 14) con las dos
normalizaciones (`completo` y `lhs`). Para cada normalizacion y bloque calcula n, medianas, p de KS (`ks_2samp`) y p de
Mann-Whitney (`mannwhitneyu`, alternativa two-sided), cada p con Bonferroni (x4, tope 1). Control: las columnas p_ks deben
coincidir con las de `p6_m5_lhs.csv` (tolerancia 1e-9). Salidas: p6_m5_pruebas.csv y p6_m5_pruebas.md.
"""
import os
import sys

import pandas as pd
from scipy.stats import ks_2samp, mannwhitneyu

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
            top = g[g["zona"] == "Top10"]["dist_frontera"]
            resto = g[g["zona"] == "resto"]["dist_frontera"]
            if len(top) and len(resto):
                p_ks = float(ks_2samp(top, resto).pvalue)
                p_mw = float(mannwhitneyu(top, resto, alternative="two-sided").pvalue)
            else:
                p_ks = p_mw = float("nan")
            filas.append([norma, b, len(top), len(resto), float(top.median()), float(resto.median()),
                          p_ks, min(1.0, 4 * p_ks), p_mw, min(1.0, 4 * p_mw)])
    t = pd.DataFrame(filas, columns=["normalizacion", "bloque", "n_top", "n_resto", "med_top", "med_resto",
                                     "p_ks", "p_ks_bonf", "p_mw", "p_mw_bonf"])
    os.makedirs(K.OUT, exist_ok=True)
    t.to_csv(os.path.join(K.OUT, "p6_m5_pruebas.csv"), index=False)

    ref = pd.read_csv(os.path.join(K.OUT, "p6_m5_lhs.csv")).set_index(["normalizacion", "bloque"])
    dif = []
    for r in t.itertuples(index=False):
        rk = float(ref.loc[(r.normalizacion, r.bloque), "p_ks"])
        dif.append(abs(rk - r.p_ks))
    difmax = max(dif)

    n_ks = int((t["p_ks"] < 0.05).sum())
    n_mw = int((t["p_mw"] < 0.05).sum())
    n_ksb = int((t["p_ks_bonf"] < 0.05).sum())
    n_mwb = int((t["p_mw_bonf"] < 0.05).sum())

    md = ["# Sens2 F1 - M5 con dos pruebas (KS y Mann-Whitney)", "",
          "Distancia L1 normalizada a la frontera no-KALINA del 10 % de KALINA de mayor eta frente al resto, por bloque, solo con las filas LHS (estudios 3 y 14).",
          "`completo` normaliza con los limites del conjunto completo (la del libro); `lhs`, con los de las propias filas LHS. Bonferroni por 4 bloques (tope 1).", "",
          "| normalizacion | bloque | n top | n resto | mediana top | mediana resto | p (KS) | p (KS, Bonf) | p (MW) | p (MW, Bonf) |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    md += ["| %s | %s | %d | %d | %.2f | %.2f | %.3f | %.3f | %.3f | %.3f |" % tuple(r) for r in t.itertuples(index=False)]
    md += ["",
           "De las 8 combinaciones (2 normalizaciones x 4 bloques), sale p < 0.05 en %d con KS y en %d con Mann-Whitney." % (n_ks, n_mw),
           "Con Bonferroni (x4) sigue saliendo p < 0.05 en %d con KS y en %d con Mann-Whitney." % (n_ksb, n_mwb),
           "Control: la mayor diferencia de p_ks frente a p6_m5_lhs.csv es %.2e (tolerancia 1e-9)." % difmax]
    with open(os.path.join(K.OUT, "p6_m5_pruebas.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
