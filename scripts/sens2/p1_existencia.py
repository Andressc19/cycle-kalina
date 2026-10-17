# -*- coding: utf-8 -*-
"""Sens2 P1 - paso 2: existencia por variable y centro, y P(KALINA) por nivel.

Rangos de existencia (min/max) de cada entrada entre los KALINA (total), entre los
KALINA dentro del rango experimental y entre todos los puntos probados. Ademas
P(KALINA) por nivel exacto (<= 14 valores) o por 8 cuantiles, con n y su intervalo
de Wilson al 95 %. Se calcula con todos los disenos y, aparte, solo con el LHS.
"""
import math
import os

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
SALIDA = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P1")

ENTRADAS = ["T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "eta_t", "eta_p",
            "eps_hrvg", "eps_reg", "eps_cond"]
CENTROS = ["C1 Husavik", "C2 ancla A*", "C3 caliente 150 C", "C4 frio 110 C", "todos"]
LHS_ESTUDIOS = [3, 14]
MAX_NIVELES = 14
Z = 1.959963984540054


def wilson(n, k):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1.0 + Z * Z / n
    centro = (p + Z * Z / (2 * n)) / den
    semi = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / den
    return (centro - semi, centro + semi)


def etiquetas(valores):
    """Etiquetas y mascaras de nivel: exactas si <= 14 valores, si no 8 cuantiles."""
    v = np.asarray(valores, dtype=float)
    u = np.unique(v[~np.isnan(v)])
    if len(u) <= MAX_NIVELES:
        out = [("%g" % x, v == x) for x in u]
    else:
        cuant = np.unique(np.quantile(v[~np.isnan(v)], np.linspace(0, 1, 9)))
        out = []
        for i in range(len(cuant) - 1):
            lo, hi = cuant[i], cuant[i + 1]
            if i < len(cuant) - 2:
                m = (v >= lo) & (v < hi)
            else:
                m = (v >= lo) & (v <= hi)
            out.append(("[%g, %g)" % (lo, hi), m))
    if np.isnan(v).any():
        out.append(("sin dato", np.isnan(v)))
    return out


def fila_rango(centro, variable, s):
    kal = s[s["kalina"]]
    kalr = kal[~kal["fuera_rango"]]
    return {
        "centro": centro, "variable": variable, "n_puntos": len(s),
        "n_kalina": len(kal), "n_kalina_rango": len(kalr),
        "min_todos": s[variable].min(), "max_todos": s[variable].max(),
        "min_kalina": kal[variable].min(), "max_kalina": kal[variable].max(),
        "min_kalina_rango": kalr[variable].min(), "max_kalina_rango": kalr[variable].max(),
    }


def filas_prob(centro, muestra, s):
    out = []
    for var in ENTRADAS:
        for nivel, mask in etiquetas(s[var].values):
            sub = s[mask]
            n, k = len(sub), int(sub["kalina"].sum())
            lo, hi = wilson(n, k)
            out.append({"centro": centro, "muestra": muestra, "variable": var,
                        "nivel": nivel, "n": n, "n_kalina": k,
                        "p_kalina": (k / n if n else float("nan")),
                        "wilson_lo": lo, "wilson_hi": hi})
    return out


def main():
    os.makedirs(SALIDA, exist_ok=True)
    d = pd.read_csv(os.path.join(SALIDA, "p1_dataset.csv"))
    d["kalina"] = d["kalina"].astype(bool)
    d["fuera_rango"] = d["fuera_rango"].astype(bool)
    lhs = d[d["estudio"].isin(LHS_ESTUDIOS)]

    rangos, probs = [], []
    for c in CENTROS:
        s = d if c == "todos" else d[d["centro"] == c]
        sl = lhs if c == "todos" else lhs[lhs["centro"] == c]
        for var in ENTRADAS:
            rangos.append(fila_rango(c, var, s))
        probs += filas_prob(c, "todos", s)
        probs += filas_prob(c, "lhs", sl)

    pd.DataFrame(rangos).to_csv(os.path.join(SALIDA, "p1_existencia_rangos.csv"), index=False)
    pd.DataFrame(probs).to_csv(os.path.join(SALIDA, "p1_existencia_prob.csv"), index=False)

    ids = sorted(lhs["id_punto"].unique())
    lineas = [
        "# Sens2 P1 - paso 2: existencia y P(KALINA)", "",
        "Rangos en `p1_existencia_rangos.csv`; P(KALINA) por nivel en `p1_existencia_prob.csv`.",
        "", "## Advertencia sobre la P(KALINA) por nivel", "",
        "Los puntos probados mezclan tres disenos distintos: barridos OFAT (una variable),",
        "mallas de pares/mapas y muestreos LHS. Por eso la P(KALINA) por nivel de una variable",
        "**depende del diseno**: en un OFAT el resto de variables esta fijo y el nivel aisla su",
        "efecto, mientras que en el LHS todas se mueven a la vez y el nivel es un promedio sobre",
        "las demas. La columna `muestra` distingue `todos` (los 3 921 puntos) de `lhs`.",
        "",         "El LHS usado son los estudios **3** (ids `C1-LHS-*`/`C2-LHS-*`, LHS de 9 variables en",
        "C1 y C2) y **14** (ids `N8-C3-*`/`N8-C4-*`, LHS de 9 variables en C3 y C4): %d puntos" % len(lhs),
        "en total, con >= 9 variables moviendose a la vez en cada punto.",
        "Estudios N1 y N2 tambien usan LHS, pero de 4 y 5 variables: quedan fuera de esta",
        "seleccion por no mover 9 variables a la vez.",
        "", "## Niveles", "",
        "Se usa el nivel exacto de la variable si tiene <= %d valores distintos; si tiene mas," % MAX_NIVELES,
        "se divide en 8 cuantiles (tramos `[lo, hi)`). Cada fila lleva su n y el intervalo de",
        "Wilson al 95 %. Los puntos con la variable sin dato (2 casos de `eta_p`) entran como",
        "nivel `sin dato`, para que el n por nivel sume el total del centro.", "",
    ]
    with open(os.path.join(SALIDA, "p1_existencia.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))

    print("rangos:", len(rangos), "filas")
    print("prob:", len(probs), "filas")
    print("LHS puntos:", len(lhs), "estudios:", LHS_ESTUDIOS,
          "primer id:", ids[0], "ultimo id:", ids[-1])


if __name__ == "__main__":
    main()
