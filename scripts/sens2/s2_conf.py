# -*- coding: utf-8 -*-
"""Sens2 - s2_conf: hoja `Confianza` (regla de confianza, criterios de cada conclusion y reparto por categoria)."""
import os
import sys

import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))
sys.path.insert(0, AQUI)
from x2_formato import condiciones, descripcion, nota, subtitulo, tabla, titulo  # noqa: E402
from x5_graficos import bloque  # noqa: E402

P5 = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P5")
CATS = ["DISEÑO REAL", "EQUIPOS", "MÁXIMA EFICIENCIA", "FLUCTUACIÓN", "LÍMITES KALINA"]
REGLA = [
    "Baja: n_min < 10 (salvo cifras deterministas), o ninguna linea de evidencia, o depende del diseño con una sola linea, o cambia al tratar "
    "NO_CONVERGIO y descansa en un solo bloque.",
    "Alta: un recuento directo con n_min >= 30; o una inferencia con >= 2 lineas de evidencia independientes (familias de metodo "
    "distintas, campañas o muestreos distintos), n_min >= 30, robusta a NO_CONVERGIO y al diseño (o con el alcance acotado y dicho en el propio enunciado) y con intervalo o prueba corregida.",
    "No aplica: una declaracion de limites del analisis no es una inferencia y no lleva confianza.",
    "Media: el resto. Cualquier criterio `parcial`, `pendiente` o `no` impide Alta.",
    "La confianza describe la solidez dentro del modelo teqp; no es una validacion experimental."]


def hoja_conf(wb, datos):
    ws = wb.create_sheet("Confianza")
    c = pd.read_csv(os.path.join(P5, "p5_conclusiones.csv"))
    e = pd.read_csv(os.path.join(P5, "p5_evidencia.csv")).set_index("id")
    f = titulo(ws, 1, "Confianza de las conclusiones: regla y criterios", ancho=12)
    f = condiciones(ws, f, [
        "Base: las %d conclusiones de p5_conclusiones.csv y sus criterios en p5_evidencia.csv." % len(c),
        "La confianza se calcula por codigo (p5_confianza.py) desde esos criterios; no se escribe a mano en el texto.",
        "Criterios: tipo, lineas de evidencia, n_min, robustez a NO_CONVERGIO, robustez al diseño, intervalo y si descansa en un solo bloque."])
    f = subtitulo(ws, f, "1. Regla")
    for t in REGLA:
        ws.cell(f, 1, t)
        f += 1
    f += 1
    f = subtitulo(ws, f, "2. Reparto por categoria")
    niveles = ("Alta", "Media", "Baja", "No aplica")
    fl = [[k] + [int(((c["categoria"] == k) & (c["confianza"] == nv)).sum()) for nv in niveles] for k in CATS]
    f = bloque(ws, f, titulo="Conclusiones por categoria y confianza", encabezados=["Categoria"] + list(niveles), filas=fl,
               x="Categoria", y="Conclusiones", apiladas=True, nota_txt="Fuente: p5_conclusiones.csv. La confianza resulta de la regla de la seccion 1.")
    f = subtitulo(ws, f, "3. Criterios de cada conclusion")
    filas = []
    for _, x in c.iterrows():
        r = e.loc[x["id"]]
        filas.append([x["id"], x["categoria"], x["confianza"], x["criterio_confianza"], r["tipo"], int(r["lineas"]), int(r["n_min"]),
                      r["robusto_nc"], r["robusto_diseno"], r["intervalo"], r["un_bloque"], r["alcance_en_enunciado"], r["nota"]])
    _, f, _ = tabla(ws, f, ["Id", "Categoria", "Confianza", "Por que", "Tipo", "Lineas", "n_min", "Robusta a NO_CONVERGIO", "Robusta al diseño",
                            "Intervalo", "Un solo bloque", "Alcance dicho en el enunciado", "Nota"], filas,
                    anchos=[7, 20, 11, 44, 13, 8, 8, 14, 14, 11, 12, 16, 70])
    f += 1
    f = nota(ws, f, "pendiente = aun no comprobado; acotado = el enunciado limita su alcance a la rebanada o escenario donde se midio; "
                    "na = el criterio no aplica a esa conclusion. `acotado` solo permite Alta si el alcance esta dicho en el propio enunciado.")
    descripcion(ws, f + 1, ["Regla de confianza aplicada por codigo y criterios que sostienen cada conclusion.",
                            "Alta es rara a proposito: exige varias lineas de evidencia, robustez e intervalo."])
    return ws


HOJAS_CONF = [hoja_conf]
