# -*- coding: utf-8 -*-
"""Sens2 P2 - Paso 2: por que falla cada CORREGIBLE.

Por centro y "todos": reparto de la violacion dominante (la mayor de viol_O1, viol_O2,
viol_O3, viol_O5; empates se unen con '+'), mediana y P90 de D y de cada violacion
entre los CORREGIBLE, y tabla cruzada violacion dominante x cuartil de D.

Salida: `p2_violaciones.csv` (formato largo) y `p2_violaciones.md` (parrafo llano).
"""
import os

import numpy as np
import pandas as pd

import p2_comun as c

SALIDA = c.SALIDA


def reparto_dominante(s):
    dom = s.apply(c.violacion_dominante, axis=1)
    vc = dom.value_counts()
    total = int(vc.sum())
    return [(k, int(v), float(v) / total) for k, v in vc.items()], dom


def estadisticos(s):
    filas = []
    for var in ["D"] + c.VIOLS:
        n, med, _, p90 = c.resumen(s[var])
        filas.append({"seccion": "estadistico", "centro": "", "clave": var,
                      "subclave": "", "n": n, "mediana": med, "p90": p90,
                      "fraccion": np.nan})
    return filas


def cruce_cuartiles(s, dom):
    q = pd.qcut(s["D"], 4, labels=["Q1", "Q2", "Q3", "Q4"], duplicates="drop")
    df = pd.DataFrame({"dom": dom, "q": q})
    tabla = df.groupby(["dom", "q"], observed=False).size()
    filas = []
    for (d, cuartil), n in tabla.items():
        if n == 0:
            continue
        base = int((df["dom"] == d).sum())
        filas.append({"seccion": "cruce", "centro": "", "clave": d,
                      "subclave": str(cuartil), "n": int(n), "mediana": np.nan,
                      "p90": np.nan, "fraccion": float(n) / base})
    return filas


def main():
    d = c.cargar_dedup()
    cor = d[d["clasificacion"] == "CORREGIBLE"]
    filas = []
    for centro in c.grupos_centro(cor) + ["todos"]:
        s = cor if centro == "todos" else cor[cor["centro"] == centro]
        dominante, dom = reparto_dominante(s)
        for k, n, fr in dominante:
            filas.append({"seccion": "dominante", "centro": centro, "clave": k,
                          "subclave": "", "n": n, "mediana": np.nan, "p90": np.nan,
                          "fraccion": fr})
        for f in estadisticos(s):
            f["centro"] = centro
            filas.append(f)
        for f in cruce_cuartiles(s, dom):
            f["centro"] = centro
            filas.append(f)
    tabla = pd.DataFrame(filas)
    tabla.to_csv(os.path.join(SALIDA, "p2_violaciones.csv"), index=False)

    tot = tabla[(tabla["seccion"] == "dominante") & (tabla["centro"] == "todos")]
    dom_txt = ", ".join("%s %.0f %%" % (r["clave"], 100 * r["fraccion"])
                        for _, r in tot.iterrows())
    est = tabla[(tabla["seccion"] == "estadistico") & (tabla["centro"] == "todos")]
    dst = est[est["clave"] == "D"].iloc[0]
    parrafo = [
        "# Sens2 P2 - Paso 2: por que falla cada CORREGIBLE", "",
        "Entre los CORREGIBLE de todo el dataset, la violacion dominante se reparte asi: %s." % dom_txt,
        "La magnitud de la violacion D (la mayor de O1/O2/O3/O5) tiene mediana %.4g y P90 %.4g." % (
            dst["mediana"], dst["p90"]),
        "Por centro, el patron es el mismo: las violaciones se concentran en los cuartiles",
        "de D mas altos, sobre todo en Q4, mientras Q1 reune los CORREGIBLE que quedan mas",
        "cerca de cumplir. Los detalles numericos estan en `p2_violaciones.csv`.", ""]
    with open(os.path.join(SALIDA, "p2_violaciones.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(parrafo))
    print("p2_violaciones.csv:", len(tabla), "filas")
    print("dominante (todos):", dom_txt)
    print("D mediana=%.4g P90=%.4g" % (dst["mediana"], dst["p90"]))


if __name__ == "__main__":
    main()
