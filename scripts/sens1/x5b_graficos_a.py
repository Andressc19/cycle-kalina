# -*- coding: utf-8 -*-
"""Sensibilidad 1 - x5b: ayudantes comunes y bloques de grafico de los estudios 0 a 3.

Cada grafico sale de la tabla que se escribe a su izquierda (helper `bloque` de x5_graficos);
la tabla y el grafico cuentan lo mismo. Todos los numeros se calculan desde el DataFrame.
Los estudios 4 a 11 viven en x5c_graficos_b.
"""
import os

from x1_cargar import (CENTRO_TXT, ESTUDIOS, PARS, RAIZ, VARIABLES_ORDEN, VAR_TXT)
from x5_graficos import bloque

COLOR_CLASE = {"KALINA": "2E7D32", "CORREGIBLE": "EF8A17", "NO_CONVERGIO": "C62828",
               "INVIABLE": "C9A227"}


def fuente(n):
    """Ruta relativa del CSV de estudio n (para la nota de pie de los graficos)."""
    return os.path.relpath(ESTUDIOS[n]["archivo"], RAIZ).replace("\\", "/")


def contar(d, col):
    return int(d[col].sum())


def _filas_kv(d):
    """Filas [variable, total, dentro, fuera] de KALINA en un centro (incluye la fila base)."""
    filas = []
    for v in VARIABLES_ORDEN:
        s = d[d["variable"] == v]
        if len(s) == 0:
            continue
        filas.append([VAR_TXT[v], contar(s, "kalina"), contar(s, "confiable"), contar(s, "fuera_motor")])
    sb = d[d["variable"] == "base"]
    if len(sb):
        filas.append(["base (punto de referencia)", contar(sb, "kalina"), contar(sb, "confiable"),
                      contar(sb, "fuera_motor")])
    return filas


def bloque_kv(ws, f, d, centro_txt, n_estudio, n_total):
    """Grafico de barras agrupadas: KALINA (total / dentro / fuera) por variable."""
    filas = _filas_kv(d)
    nota = (f"Incluye: los KALINA de cada variable barrida y la fila base (punto de referencia) "
            f"en {centro_txt} (n = {len(d)} puntos del centro; {n_total} del estudio). "
            f"Fuente: {fuente(n_estudio)}.")
    return bloque(ws, f, titulo=f"KALINA por variable en {centro_txt} (total, dentro y fuera "
                  f"del rango experimental)",
                  encabezados=["Variable barrida", "KALINA (total)",
                               "de ellos dentro del rango experimental",
                               "de ellos fuera del rango experimental"],
                  filas=filas, x="Variable barrida", y="Numero de puntos", nota_txt=nota)


def _e0(ws, d, f):
    filas = [[r["id_punto"], round(float(r["eta_pct"]), 4)] for _, r in d.iterrows()]
    nota = (f"Incluye: los {len(d)} puntos de la fase 0 (m_b de 1 a 20 kg/s y eps_cond "
            f"0.80-0.95). Fuente: {fuente(0)}.")
    return bloque(ws, f, titulo="E0. Rendimiento (eta, %) de cada punto de la referencia de Husavik",
                  encabezados=["Punto", "eta (%)"], filas=filas, x="Punto", y="eta (%)",
                  nota_txt=nota)


def _e1(ws, d, f):
    n_total = len(d)
    ca, cb = CENTRO_TXT["C1"], CENTRO_TXT["C2"]
    f = bloque_kv(ws, f, d[d["centro"] == ca], ca, 1, n_total)
    return bloque_kv(ws, f, d[d["centro"] == cb], cb, 1, n_total)


def _e2(ws, d, f):
    filas = []
    for p in ["B1", "B2", "B3", "B4", "B5", "B6"]:
        s = d[d["par"] == p]
        filas.append([PARS[p], contar(s[s["centro"] == CENTRO_TXT["C1"]], "kalina"),
                      contar(s[s["centro"] == CENTRO_TXT["C2"]], "kalina")])
    sb = d[d["par"] == "base"]
    if len(sb):
        filas.append(["base (punto de referencia)",
                      contar(sb[sb["centro"] == CENTRO_TXT["C1"]], "kalina"),
                      contar(sb[sb["centro"] == CENTRO_TXT["C2"]], "kalina")])
    nota = (f"Incluye: los KALINA de los 6 pares de variables (malla 7x7 por par y centro) y la "
            f"fila base. Fuente: {fuente(2)}. n = {len(d)}.")
    return bloque(ws, f, titulo="E2. KALINA por par de variables (C1 Husavik y C2 ancla A*)",
                  encabezados=["Par de variables", CENTRO_TXT["C1"], CENTRO_TXT["C2"]],
                  filas=filas, x="Par de variables", y="Numero de puntos", nota_txt=nota)


def _e3(ws, d, f):
    filas = []
    for c in [CENTRO_TXT["C1"], CENTRO_TXT["C2"]]:
        s = d[d["centro"] == c]
        filas.append([c, contar(s[s["clasificacion"] == "KALINA"], "kalina"),
                      int((s["clasificacion"] == "CORREGIBLE").sum()),
                      int((s["clasificacion"] == "NO_CONVERGIO").sum()),
                      int((s["clasificacion"] == "INVIABLE").sum())])
    nota = (f"Incluye: los {len(d)} puntos del muestreo LHS de 9 variables (250 por centro). "
            f"Fuente: {fuente(3)}.")
    return bloque(ws, f, titulo="E3. Puntos por clase y centro en el muestreo LHS de 9 variables",
                  encabezados=["Centro", "KALINA", "CORREGIBLE", "NO_CONVERGIO", "INVIABLE"],
                  filas=filas, x="Centro", y="Numero de puntos", apiladas=True,
                  colores=[COLOR_CLASE["KALINA"], COLOR_CLASE["CORREGIBLE"],
                           COLOR_CLASE["NO_CONVERGIO"], COLOR_CLASE["INVIABLE"]],
                  nota_txt=nota)


def dibujar_estudio(ws, n, df, f):
    """Escribe los bloques de grafico del estudio n a partir de la fila f."""
    d = df[df["estudio"] == n]
    if n == 0:
        return _e0(ws, d, f)
    if n == 1:
        return _e1(ws, d, f)
    if n == 2:
        return _e2(ws, d, f)
    if n == 3:
        return _e3(ws, d, f)
    from x5c_graficos_b import dibujar_estudio_b
    return dibujar_estudio_b(ws, n, df, f)
