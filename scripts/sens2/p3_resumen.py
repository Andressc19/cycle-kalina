# -*- coding: utf-8 -*-
"""Sens2 P3 - Paso 4a: p3_resumen.md en lenguaje llano, con cifras de los CSV.

Lee p3_ranking.csv, p3_indices.csv, p3_interaccion.csv y p3_elasticidad.csv.
"""
import os

import numpy as np
import pandas as pd

import p3_comun as C

LY1 = "Y1 KALINA (total)"
LY2 = "Y2 eta (%)"
LY3 = "Y3 W_net/m_b"
LY4 = "Y4 D CORREGIBLE"


def top(rank, bloque, resp, n=3):
    gg = rank[(rank["bloque"] == bloque) & (rank["respuesta"] == resp) &
              (rank["tipo"] == "real")].sort_values("rango_medio")
    return gg.head(n)


def linea_top(rank, bloque, resp):
    g = top(rank, bloque, resp)
    if len(g) == 0:
        return "sin datos"
    return ", ".join("%s (rango %.1f, %s)" % (r["variable"], r["rango_medio"],
                                              "si" if r["distinguible"] else "no")
                     for _, r in g.iterrows())


def main():
    base = C.P3
    rank = pd.read_csv(os.path.join(base, "p3_ranking.csv"))
    ind = pd.read_csv(os.path.join(base, "p3_indices.csv"))
    inter = pd.read_csv(os.path.join(base, "p3_interaccion.csv"))
    ela = pd.read_csv(os.path.join(base, "p3_elasticidad.csv"))
    out = ["# Sens2 P3 - resumen (Paso 4)", "",
           "Indices given-data con 3 variables dummy como piso de ruido y IC bootstrap "
           "(500 remuestreos de filas, 95 %). Un indice es `distinguible del ruido` si su "
           "limite inferior del IC supera el maximo de las dummy. `rango medio` = puesto medio "
           "entre metodos (1 = mas importante).", ""]
    bloques = [b[0] for b in C.BLOQUES]
    for bl in bloques:
        centro = bl.split(" ", 1)[1]
        out.append("## %s" % centro)
        gk = rank[(rank["bloque"] == bl) & (rank["respuesta"] == LY1)]
        dum = gk[gk["tipo"] == "dummy"].sort_values("rango_medio")
        mej_dum = ("%.1f" % dum.iloc[0]["rango_medio"]) if len(dum) else "n/a"
        out.append("- Que decide que haya KALINA (Y1): %s. Mejor dummy: rango %s."
                   % (linea_top(rank, bl, LY1), mej_dum))
        out.append("- Que mueve eta (Y2): %s." % linea_top(rank, bl, LY2))
        out.append("- Que mueve W_net/m_b (Y3): %s." % linea_top(rank, bl, LY3))
        gd = ind[(ind["bloque"] == bl) & (ind["respuesta"] == LY4) &
                 (ind["metodo"] == "PRCC") & (ind["variable"].isin(C.REALES)) &
                 (ind["valor"] < 0)].copy()
        gd["mag"] = gd["valor"].abs()
        gd = gd.sort_values("mag", ascending=False).head(3)
        out.append("- Bajan D (Y4, PRCC negativo): %s."
                   % (", ".join("%s (PRCC %.2f)" % (r["variable"], r["valor"])
                                for _, r in gd.iterrows()) if len(gd) else "ninguna"))
        gp = inter[(inter["centro"] == centro) &
                   ((inter["noadit_eta"] >= 0.25) | (inter["noadit_ind"] >= 0.25))]
        out.append("- Pares con interaccion fuerte: %s."
                   % (", ".join("%s (eta 1-R2=%.2f, ind 1-R2=%.2f, %s)"
                                % (r["par"], r["noadit_eta"], r["noadit_ind"], r["clasificacion"])
                                for _, r in gp.iterrows()) if len(gp) else "ninguno"))
        ge = ela[(ela["centro"] == centro) & ela["elasticidad"].notna()].copy()
        ge["mag"] = ge["elasticidad"].abs()
        ge = ge.sort_values("mag", ascending=False).head(3)
        out.append("- Elasticidades mayores en el base: %s."
                   % (", ".join("%s (%.2f, %s)" % (r["variable"], r["elasticidad"], r["tipo"])
                                for _, r in ge.iterrows()) if len(ge) else "sin KALINA vecino"))
        out.append("")
    out.append("## Metodos: coincidencias y discrepancias")
    out.append("")
    for bl in bloques:
        for resp in [LY1, LY2, LY3]:
            g = rank[(rank["bloque"] == bl) & (rank["respuesta"] == resp)]
            real = g[g["tipo"] == "real"].sort_values("rango_medio")
            dum = g[g["tipo"] == "dummy"].sort_values("rango_medio")
            if len(real) and len(dum):
                out.append("- %s / %s: mejor real %s (rango %.1f) frente a mejor dummy %s "
                           "(rango %.1f); variables distinguibles: %d de %d."
                           % (bl, resp, real.iloc[0]["variable"], real.iloc[0]["rango_medio"],
                              dum.iloc[0]["variable"], dum.iloc[0]["rango_medio"],
                              int(real["distinguible"].sum()), len(real)))
    with open(os.path.join(base, "p3_resumen.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("p3_resumen.md escrito")


if __name__ == "__main__":
    main()
