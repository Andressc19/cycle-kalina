# -*- coding: utf-8 -*-
"""Sensibilidad 1 - x5b: ayudantes comunes y bloques de grafico de los estudios 0 a 3.

Cada grafico sale de la tabla que se escribe a su izquierda (helper `bloque` de x5_graficos);
la tabla y el grafico cuentan lo mismo. Todos los numeros se calculan desde el DataFrame.
Los estudios 4 a 11 viven en x5c_graficos_b.
"""
import os

from x1_cargar import (CENTROS, CENTRO_TXT, ESTUDIOS, PARS, RAIZ,
                       VARIABLES_ORDEN, VAR_TXT, bases_por_centro)
from x5_graficos import bloque

COLOR_CLASE = {"KALINA": "2E7D32", "CORREGIBLE": "EF8A17", "NO_CONVERGIO": "C62828",
               "INVIABLE": "C9A227"}

# Variables que se mueven en cada par (las demas quedan fijas en el valor del centro). Es el
# mismo reparto que usan las corridas de Fase B (E2) y N7B (E11) para armar las mallas.
PARS_VARS = {"B1": ("T_fuente", "P_baja"), "B2": ("P_baja", "x_b"),
             "B3": ("P_alta", "P_baja"), "B4": ("eps_cond", "T_sumidero"),
             "B5": ("eps_reg", "eta_t"), "B6": ("eps_hrvg", "T_fuente")}


def fuente(n):
    """Ruta relativa del CSV del estudio n (para la nota de pie de los graficos)."""
    for e in ESTUDIOS:
        if e["n"] == n:
            return os.path.relpath(e["archivo"], RAIZ).replace("\\", "/")
    return ""


def contar(d, col):
    return int(d[col].sum())


def _base_suma(base, col):
    return int(base[col]) if base is not None else 0


def kalina_con_base(s, cen, base):
    """KALINA de un subconjunto mas el punto base del centro (si lo hay)."""
    n = contar(s[s["centro"] == cen], "kalina")
    return n + _base_suma(base, "kalina")


def kalina_malla(d, cen, a, b):
    """KALINA del centro `cen` que pertenecen a la malla del par (a, b), no por etiqueta.

    Un punto pertenece a la malla si todas las variables distintas de a y b valen lo del
    centro (redondeo a 2 decimales); a y b recorren la rejilla del par. Cuenta el punto base,
    que es una celda de todas las mallas (en el CSV queda etiquetado como base o como una celda
    del primer par). Evita la subcuenta de las lineas que comparten pares (el CSV asigna cada
    punto compartido al primer par que lo genero).
    """
    base = CENTROS.get(cen, {})
    s = d[d["centro"] == cen]
    for v in VARIABLES_ORDEN:
        if v in (a, b):
            continue
        s = s[s[v].round(2) == round(float(base[v]), 2)]
    return contar(s, "kalina")


def _filas_kv(d, base):
    """[variable, total, dentro, fuera] de KALINA en un centro; el base va dentro de cada fila."""
    filas = []
    for v in VARIABLES_ORDEN:
        s = d[d["variable"] == v]
        if len(s) == 0:
            continue
        filas.append([VAR_TXT[v], contar(s, "kalina") + _base_suma(base, "kalina"),
                      contar(s, "confiable") + _base_suma(base, "confiable"),
                      contar(s, "fuera_motor") + _base_suma(base, "fuera_motor")])
    return filas


def bloque_kv(ws, f, d, centro_txt, n_estudio, n_total, bases=None):
    """Grafico de barras agrupadas: KALINA (total / dentro / fuera) por variable."""
    from x2_formato import subtitulo
    base = (bases or {}).get(centro_txt)
    f = subtitulo(ws, f, "KALINA (total, dentro y fuera del rango experimental) por variable "
                         f"barrida en {centro_txt}")
    filas = _filas_kv(d, base)
    nota = (f"Incluye: los KALINA de cada variable barrida y el punto base (punto de referencia) "
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


def _e1(ws, d, f, bases):
    n_total = len(d)
    ca, cb = CENTRO_TXT["C1"], CENTRO_TXT["C2"]
    f = bloque_kv(ws, f, d[d["centro"] == ca], ca, 1, n_total, bases)
    return bloque_kv(ws, f, d[d["centro"] == cb], cb, 1, n_total, bases)


def _e2(ws, d, f, bases):
    filas = []
    for p in ["B1", "B2", "B3", "B4", "B5", "B6"]:
        a, b = PARS_VARS[p]
        filas.append([PARS[p], kalina_malla(d, CENTRO_TXT["C1"], a, b),
                      kalina_malla(d, CENTRO_TXT["C2"], a, b)])
    nota = (f"Incluye: los KALINA de los 6 pares de variables (malla 7x7 por par y centro) y el "
            f"punto base de cada centro. Fuente: {fuente(2)}. n = {len(d)}.")
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
    bases = bases_por_centro(df)
    if n == 0:
        return _e0(ws, d, f)
    if n == 1:
        return _e1(ws, d, f, bases)
    if n == 2:
        return _e2(ws, d, f, bases)
    if n == 3:
        return _e3(ws, d, f)
    from x5c_graficos_b import dibujar_estudio_b
    return dibujar_estudio_b(ws, n, df, f, bases)
