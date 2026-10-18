# -*- coding: utf-8 -*-
"""Sens2 P1 - paso 5: resumen (p1_resumen.md) y verificacion de los controles.

Genera `p1_resumen.md` a partir de los CSV del paso 1-4 y comprueba: total 3 921,
suma de clases, min <= max, P(KALINA) en [0,1], n por nivel igual al total del
centro, y ausencia de las palabras prohibidas en los .md/.csv nuevos. Imprime una
linea OK/FALLA por control.
"""
import glob
import os

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
SALIDA = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P1")

PROHIBIDAS = ["confiable", "no citable", "fuera de rango del motor"]
CENTROS = ["C1 Husavik", "C2 ancla A*", "C3 caliente 150 C", "C4 frio 110 C", "todos"]


def leer(nombre, **kw):
    return pd.read_csv(os.path.join(SALIDA, nombre), **kw)


def resumen(d, rangos, reglas, fronteras, gris, q25):
    L = ["# Sens2 P1 - resumen", "",
         "Dataset unificado: **%d** puntos de los estudios 0-11 y 14-16." % len(d), "",
         "## Rangos de existencia por variable y centro", "",
         "min / max entre los KALINA (total), entre los KALINA dentro del rango experimental",
         "y entre todos los puntos probados. `-` = no hay puntos KALINA en ese grupo.", ""]
    for c in CENTROS:
        L += ["### %s" % c, "",
              "| variable | min KALINA | max KALINA | min KALINA en rango | max KALINA en rango | min todos | max todos |",
              "|---|---|---|---|---|---|---|"]
        for _, r in rangos[rangos["centro"] == c].iterrows():
            L.append("| %s | %s | %s | %s | %s | %s | %s |" % (
                r["variable"], v(r["min_kalina"]), v(r["max_kalina"]),
                v(r["min_kalina_rango"]), v(r["max_kalina_rango"]),
                v(r["min_todos"]), v(r["max_todos"])))
        L.append("")
    st = reglas[reglas["seccion"] == "stump"].sort_values("ganancia", ascending=False)
    L += ["## Las 5 reglas (stump) mas fuertes", "",
          "| lugar | centro | variable | umbral | lado KALINA | ganancia Gini |",
          "|---|---|---|---|---|---|"]
    for i, (_, r) in enumerate(st.head(5).iterrows()):
        L.append("| %d | %s | %s | %g | %s | %.4f |" % (
            i + 1, r["centro"], r["variable"], r["umbral"], r["direccion"], r["ganancia"]))
    ar = reglas[reglas["seccion"] == "arbol"]
    L += ["", "Reglas del arbol (pureza >= 0.9, n >= 30):"]
    if len(ar) == 0:
        L.append("- (ninguna cumple el criterio)")
    for _, r in ar.iterrows():
        L.append("- [%s, %s] `%s` -> n = %d, KALINA = %.0f %%" % (
            r["centro"], r["variable"], r["regla"], r["n"], 100.0 * r["p_kalina"]))
    L += ["", "## Fronteras por variable (OFAT)", "",
          "Cambios de clase en los barridos de una variable; %d fronteras en total." % len(fronteras),
          "", "| centro | variable | forma | direccion | frontera |", "|---|---|---|---|---|"]
    for _, r in fronteras.iterrows():
        L.append("| %s | %s | %s | %s | %g |" % (
            r["centro"], r["variable"], r["forma"], r["direccion"], r["valor_frontera"]))
    L += ["", "## Zonas grises", "",
          "Cuantil 25 %% de D entre los CORREGIBLE: %.4f." % q25,
          "Zonas grises (CORREGIBLE con D <= ese cuantil): **%d** puntos." % len(gris)]
    return "\n".join(L)


def v(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "-"
    return ("%.4g" % x)


def chequeo(nombre, ok, detalle=""):
    print("%s  %s%s" % ("OK  " if ok else "FALLA", nombre, ("  " + detalle) if detalle else ""))
    return ok


def main():
    d = leer("p1_dataset.csv")
    rangos = leer("p1_existencia_rangos.csv")
    prob = leer("p1_existencia_prob.csv")
    reglas = leer("p1_reglas.csv")
    fronteras = leer("p1_fronteras.csv")
    gris = leer("p1_zonas_grises.csv")
    q25 = float(d[d["clasificacion"] == "CORREGIBLE"]["D"].quantile(0.25))

    with open(os.path.join(SALIDA, "p1_resumen.md"), "w", encoding="utf-8") as f:
        f.write(resumen(d, rangos, reglas, fronteras, gris, q25))

    todo_ok = True
    todo_ok &= chequeo("total de puntos = 3921", len(d) == 3921, "total=%d" % len(d))
    sumc = int(d["clasificacion"].value_counts().sum())
    todo_ok &= chequeo("suma de clases = total", sumc == len(d),
                       "clases=%d total=%d" % (sumc, len(d)))
    ok = True
    for a, b in [("min_todos", "max_todos"), ("min_kalina", "max_kalina"),
                 ("min_kalina_rango", "max_kalina_rango")]:
        par = rangos[[a, b]].dropna()
        if (par[a] > par[b]).any():
            ok = False
    todo_ok &= chequeo("min <= max en cada rango", ok)
    pk = prob["p_kalina"].dropna()
    todo_ok &= chequeo("P(KALINA) en [0,1]", bool(((pk >= 0) & (pk <= 1)).all()),
                       "min=%.3f max=%.3f" % (pk.min(), pk.max()))
    cnt = d.copy()
    cnt["lhs"] = cnt["estudio"].isin([3, 14])
    esperado = {}
    for c in CENTROS:
        sub = cnt if c == "todos" else cnt[cnt["centro"] == c]
        esperado[(c, "todos")] = len(sub)
        esperado[(c, "lhs")] = int(sub["lhs"].sum())
    suma = prob.groupby(["centro", "muestra", "variable"])["n"].sum()
    ok = True
    for (c, m, var), n in suma.items():
        if int(n) != esperado[(c, m)]:
            ok = False
    todo_ok &= chequeo("n por nivel suma al total del centro", ok)
    archivos = (glob.glob(os.path.join(SALIDA, "*.md"))
                + glob.glob(os.path.join(SALIDA, "*.csv")))
    malos = []
    for ruta in archivos:
        with open(ruta, "r", encoding="utf-8") as f:
            txt = f.read().lower()
        if any(p in txt for p in PROHIBIDAS):
            malos.append(os.path.basename(ruta))
    todo_ok &= chequeo("sin palabras prohibidas en .md/.csv nuevos", not malos,
                       "archivos: %s" % (", ".join(malos) if malos else "ninguno"))
    print("RESULTADO:", "OK" if todo_ok else "FALLA")


if __name__ == "__main__":
    main()
