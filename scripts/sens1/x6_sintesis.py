# -*- coding: utf-8 -*-
"""Sensibilidad 1 - x6: hoja de sintesis dentro de 'Conclusion consolidada'."""

import pandas as pd

from x1_cargar import CENTROS, VAR_TXT, VARIABLES_ORDEN
from x2_formato import tabla
from x5_graficos import grafico_sobre_tabla

COLOR_CLASE = ["2E7D32", "EF8A17", "C62828", "C9A227"]


def _es_num(v):
    return isinstance(v, (int, float)) and not (isinstance(v, float) and pd.isna(v))


def hoja_sintesis(wb, df):
    ws = wb.create_sheet("Conclusion consolidada")
    f = 1
    from x2_formato import titulo, condiciones, nota
    from conclusiones import APENDICE_B
    f = titulo(ws, f, "Conclusion consolidada")
    f = condiciones(ws, f, ["Sintesis de los 12 estudios (salen de los CSV)."])
    # S1: conteo por estudio x clase
    f = titulo(ws, f, "S1. Conteo por estudio y por clase")
    enc1 = f
    conteo = df.groupby(["estudio", "clasificacion"]).size().unstack(fill_value=0)
    conteo = conteo.reindex(columns=["KALINA", "CORREGIBLE", "NO_CONVERGIO", "INVIABLE"], fill_value=0)
    conteo["KALINA_conf"] = df[df["confiable"]].groupby("estudio").size()
    conteo["KALINA_fuera"] = df[df["fuera_motor"]].groupby("estudio").size()
    conteo = conteo.fillna(0).astype(int)
    conteo["Total"] = conteo.sum(axis=1)
    filas = []
    for n, row in conteo.sort_index().iterrows():
        filas.append([int(n), row["KALINA"], row["KALINA_conf"], row["KALINA_fuera"], row["CORREGIBLE"], row["NO_CONVERGIO"], row["INVIABLE"], row["Total"]])
    tabla(ws, f, ["Estudio", "KALINA (total)", "de ellos dentro del rango experimental", "de ellos fuera del rango experimental", "CORREGIBLE", "NO_CONVERGIO", "INVIABLE", "Total"], filas, anchos=[10, 12, 22, 22, 14, 14, 12, 10], clases=None, clave_fila=None)
    f = grafico_sobre_tabla(ws, enc1, len(filas), [2, 5, 6, 7],
                            titulo="S1. Puntos por estudio y por clase",
                            x="Estudio", y="Numero de puntos", apiladas=True,
                            colores=COLOR_CLASE,
                            nota_txt=("Incluye: los 12 estudios (0 a 11). Cada barra apila las "
                                      "clases KALINA (total), CORREGIBLE, NO_CONVERGIO e INVIABLE; "
                                      "la suma es el total de puntos del estudio. Fuente: los CSV "
                                      "de resultados/."))
    # S5: eta maxima por estudio (dentro del rango experimental y todos los KALINA)
    f = titulo(ws, f, "S5. Eta maxima dentro del rango experimental por estudio y punto que la logra")
    enc5 = f
    res = []
    for n in sorted(df["estudio"].unique()):
        sub = df[(df["estudio"] == n) & (df["confiable"])]
        if sub.empty:
            continue
        kal = df[(df["estudio"] == n) & (df["kalina"])]
        r = sub.loc[sub["eta_pct"].idxmax()]
        res.append([int(n), r["eta_pct"], kal["eta_pct"].max(), r["id_punto"], r["centro"]])
    tabla(ws, f, ["Estudio", "eta maxima dentro del rango experimental (%)", "eta maxima entre todos los KALINA (%)", "id_punto", "Centro"], res, anchos=[10, 24, 24, 20, 20], clases=None, clave_fila=None)
    f = grafico_sobre_tabla(ws, enc5, len(res), [2, 3],
                            titulo="S5. Eta maxima del KALINA por estudio",
                            x="Estudio", y="eta (%)", colores=["2E7D32", "1F4E79"],
                            nota_txt=("Incluye: la eta maxima por estudio, dentro del rango "
                                      "experimental y entre todos los KALINA (vacio donde no hay "
                                      "KALINA dentro del rango). Fuente: los CSV de resultados/."))
    # Conclusion consolidada
    f = nota(ws, f, APENDICE_B)
    return ws.title
