# -*- coding: utf-8 -*-
"""Sensibilidad 1 - x4a: calculos de la Ronda 3 para las hojas E14, E15 y E16.

Ventanas p10/mediana/p90 de las 9 variables, PRCC con eta (rangos con promedio en empates y
residuos de minimos cuadrados, en numpy) y estadistico KS (scipy.stats.ks_2samp), como en
`scripts/sens1/ronda3_reporte3.py`; agrupacion de las causas de los NO_CONVERGIO y armado de
las matrices de clase y de eta. No escribe nada: solo numeros desde el DataFrame.
"""

import numpy as np
from scipy.stats import ks_2samp

# Las 9 variables del muestreo LHS (N8): mismas de ronda3_reporte3.py.
VARS_N8 = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "eta_t", "eps_hrvg",
           "eps_reg", "eps_cond")

VAR_TXT_LARGO = {"T_fuente": "T_fuente (K)", "T_sumidero": "T_sumidero (K)",
                 "P_alta": "P_alta (kPa)", "P_baja": "P_baja (kPa)", "x_b": "x_b (-)",
                 "eta_t": "η_t (-)", "eps_hrvg": "ε_HRVG (-)", "eps_reg": "ε_reg (-)",
                 "eps_cond": "ε_cond (-)"}

# Categorias de las causas de NO_CONVERGIO (agrupa el mensaje del motor).
CAUSAS = ["sin dos extremos evaluables de T1", "balance global de energía no cierra",
          "sin cambio de signo de F", "punto interior no evaluable",
          "PropertyRangeError del motor", "tiempo agotado", "otros"]


def causa(mensaje):
    """Categoria de una causa a partir del mensaje del motor."""
    m = (mensaje or "").lower()
    if "extremos" in m:
        return "sin dos extremos evaluables de T1"
    if "balance global" in m:
        return "balance global de energía no cierra"
    if "cambio de signo" in m:
        return "sin cambio de signo de F"
    if "punto interior" in m:
        return "punto interior no evaluable"
    if "propertyrange" in m:
        return "PropertyRangeError del motor"
    if "agotado" in m:
        return "tiempo agotado"
    return "otros"


def causas_por_centro(d):
    """Filas [causa, C3, C4, Total] de los NO_CONVERGIO de un estudio de dos centros."""
    nc = d[d["clasificacion"] == "NO_CONVERGIO"]
    centros = list(dict.fromkeys(d["centro"]))
    filas = []
    for ca in CAUSAS:
        cuenta = [int((nc[(nc["centro"] == c) & (nc["mensaje"].map(causa) == ca)]).shape[0])
                  for c in centros]
        filas.append([ca] + cuenta + [sum(cuenta)])
    return filas, centros


def ventana(vals):
    """(p10, mediana, p90, n) de una lista de valores."""
    x = np.asarray([v for v in vals if v is not None], float)
    if len(x) == 0:
        return (None, None, None, 0)
    q = np.percentile(x, [10, 50, 90])
    return (float(q[0]), float(q[1]), float(q[2]), len(x))


def _rank(x):
    """Rangos 1..n con promedio en empates (solo numpy)."""
    order = np.argsort(x, kind="mergesort")
    r = np.empty(len(x), float)
    s, i, n = x[order], 0, len(x)
    while i < n:
        j = i
        while j + 1 < n and s[j + 1] == s[i]:
            j += 1
        r[order[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    return r


def _resid(A, y):
    return y - A @ np.linalg.lstsq(A, y, rcond=None)[0]


def prcc(kal):
    """{variable: PRCC con eta} entre los KALINA (solo numpy). None si no hay datos."""
    fs = kal[kal["eta"].notna()]
    n = len(fs)
    if n < len(VARS_N8) + 2:
        return {v: None for v in VARS_N8}
    Y = _rank(fs["eta"].values.astype(float))
    X = np.column_stack([_rank(fs[v].values.astype(float)) for v in VARS_N8])
    out = {}
    for i, v in enumerate(VARS_N8):
        otros = [j for j in range(len(VARS_N8)) if j != i]
        A = np.column_stack([np.ones(n), X[:, otros]])
        rx, ry = _resid(A, X[:, i]), _resid(A, Y)
        if np.std(rx) < 1e-12 or np.std(ry) < 1e-12:
            out[v] = None
        else:
            out[v] = float(np.corrcoef(rx, ry)[0, 1])
    return out


def ks_d(kal, resto):
    """{variable: estadistico KS} entre KALINA y el resto de puntos genuinos."""
    out = {}
    for v in VARS_N8:
        a = kal[v].values.astype(float)
        b = resto[v].values.astype(float)
        out[v] = float(ks_2samp(a, b).statistic) if len(a) > 1 and len(b) > 1 else None
    return out


def etiqueta(var, v):
    """Etiqueta de una fila/columna de matriz: T en °C y lo demas con 2 decimales."""
    if var in ("T_fuente", "T_sumidero"):
        return round(float(v) - 273.15, 1)
    return round(float(v), 2)


def valores(d, var):
    """Valores distintos (redondeados a 2) de `var` en `d`, ordenados."""
    return sorted({round(float(x), 2) for x in d[var].dropna()})


def matriz(d, fvar, cvar, fila_vals, col_vals, modo):
    """Matriz [etiqueta_fila, celdas]: clase (texto) o eta (%) maxima entre los KALINA."""
    filas = []
    for fv in fila_vals:
        sf = d[d[fvar].round(2) == round(float(fv), 2)]
        fila = [etiqueta(fvar, fv)]
        for cv in col_vals:
            s = sf[sf[cvar].round(2) == round(float(cv), 2)]
            if modo == "clase":
                fila.append(str(s["clasificacion"].iloc[0]) if len(s) else "")
            else:
                k = s[s["kalina"]]
                fila.append(round(float(k["eta_pct"].max()), 2) if len(k) else None)
        filas.append(fila)
    return filas


__all__ = ["VARS_N8", "VAR_TXT_LARGO", "CAUSAS", "causa", "causas_por_centro", "ventana",
           "prcc", "ks_d", "etiqueta", "valores", "matriz"]
