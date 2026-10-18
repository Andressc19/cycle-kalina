# -*- coding: utf-8 -*-
"""Sens2 P4 - Paso 2: que variable fija cada requisito.

Correlacion de Spearman (con p-valor) de cada cantidad de equipo con cada una de
las 10 entradas, por centro, sobre KALINA (total) de los estudios LHS (3 y 14,
ya deduplicados en P2) para que las entradas varian a la vez. Tabla variable x
cantidad con las 3 asociaciones mas fuertes por cantidad y regresion de dh_turb
sobre rp (minimos cuadrados con numpy: pendiente, intercepto, R2) por centro.
Salidas: p4_dependencias.csv y p4_dependencias.md.
"""
import os
import warnings

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

import p4_comun as c

SALIDA = c.SALIDA
LHS = (3, 14)
COLS = ["tipo", "centro", "cantidad", "variable", "n", "estadistico", "p_valor",
        "pendiente", "intercepto", "r2"]


def spearman(x, y):
    """Rho de Spearman y p-valor con datos finitos; NaN si no hay variacion."""
    x = np.asarray(pd.to_numeric(pd.Series(x), errors="coerce"), float)
    y = np.asarray(pd.to_numeric(pd.Series(y), errors="coerce"), float)
    fin = np.isfinite(x) & np.isfinite(y)
    x, y = x[fin], y[fin]
    if len(x) < 3 or np.nanstd(x) == 0 or np.nanstd(y) == 0:
        return (len(x), np.nan, np.nan)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        r = spearmanr(x, y)
    return (len(x), float(r.statistic), float(r.pvalue))


def regresion(x, y):
    """Minimos cuadrados y = pendiente*x + intercepto; n y R2."""
    x = np.asarray(pd.to_numeric(pd.Series(x), errors="coerce"), float)
    y = np.asarray(pd.to_numeric(pd.Series(y), errors="coerce"), float)
    fin = np.isfinite(x) & np.isfinite(y)
    x, y = x[fin], y[fin]
    if len(x) < 3 or np.nanstd(x) == 0:
        return (len(x), np.nan, np.nan, np.nan)
    m, b = np.polyfit(x, y, 1)
    yp = m * x + b
    ss = np.sum((y - y.mean()) ** 2)
    r2 = 1.0 - np.sum((y - yp) ** 2) / ss if ss > 0 else np.nan
    return (len(x), float(m), float(b), float(r2))


def bloque_spearman(lhs):
    filas = []
    for centro in c.grupos(lhs):
        s = lhs[lhs["centro"] == centro]
        for cant in c.CANT_DEP:
            for var in c.ENTRADAS:
                n, rho, p = spearman(s[var], s[cant])
                filas.append(["spearman", centro, cant, var, n, rho, p,
                              np.nan, np.nan, np.nan])
    return filas


def bloque_regresion(lhs):
    filas = []
    for centro in c.grupos(lhs) + ["todos"]:
        s = lhs if centro == "todos" else lhs[lhs["centro"] == centro]
        n, m, b, r2 = regresion(s["rp"], s["dh_turb"])
        filas.append(["regresion", centro, "dh_turb", "rp", n, np.nan, np.nan,
                      m, b, r2])
    return filas


def top3(tabla, centro, cant):
    s = tabla[(tabla["tipo"] == "spearman") & (tabla["centro"] == centro)
              & (tabla["cantidad"] == cant)].copy()
    s["mag"] = s["estadistico"].abs()
    return s.sort_values("mag", ascending=False).head(3)


def markdown(tabla, lhs):
    l = ["# Sens2 P4 - Paso 2: que variable fija cada requisito", "",
         "Spearman (rho, p) de cada cantidad de equipo con las 10 entradas, por",
         "centro, sobre KALINA (total) de los estudios LHS 3 y 14 (entradas",
         "variando a la vez). Las 3 asociaciones mas fuertes por cantidad:",
         "|rho| mayor, con su signo. `eta_p` es constante en el LHS: sale sin",
         "varianza (n y rho = .).", ""]
    for centro in c.grupos(lhs):
        l += ["## %s" % centro, "",
              c.tabla_md(["cantidad", "1a variable (rho, p)", "2a variable (rho, p)",
                          "3a variable (rho, p)"],
                         [[cant,
                           " / ".join("%s (%+.3f, %.2g)" % (r["variable"],
                                     r["estadistico"], r["p_valor"])
                                     for _, r in top3(tabla, centro, cant).iterrows())
                           ] for cant in c.CANT_DEP]), ""]
    l += ["## Regresion de dh_turb sobre rp (minimos cuadrados)", "",
          c.tabla_md(["centro", "n", "pendiente", "intercepto", "R2"],
                     [[r["centro"], r["n"], c.fmt(r["pendiente"]), c.fmt(r["intercepto"]),
                       c.fmt(r["r2"], 3)]
                      for _, r in tabla[tabla["tipo"] == "regresion"].iterrows()]),
          "", "Lectura: rho > 0 = al subir la entrada sube la cantidad; los p-valores",
          "son indicativos (n y diseno del LHS, no muestreo aleatorio puro).", ""]
    return "\n".join(l)


def main():
    d = c.cargar()
    lhs = d[d["estudio"].isin(LHS) & c.mask_total(d)]
    filas = bloque_spearman(lhs) + bloque_regresion(lhs)
    tabla = pd.DataFrame(filas, columns=COLS)
    os.makedirs(SALIDA, exist_ok=True)
    tabla.to_csv(os.path.join(SALIDA, "p4_dependencias.csv"), index=False)
    c.guardar("p4_dependencias.md", markdown(tabla, lhs))
    print("p4_dependencias.csv:", len(tabla), "filas")
    print("LHS KALINA:", len(lhs), "| por centro:", lhs["centro"].value_counts().to_dict())
    print("regresion dh_turb ~ rp:")
    for _, r in tabla[tabla["tipo"] == "regresion"].iterrows():
        print("  %-24s n=%d pend=%+.4g r2=%.3f" % (
            r["centro"], r["n"], r["pendiente"], r["r2"]))


if __name__ == "__main__":
    main()
