# -*- coding: utf-8 -*-
"""Sens2 - s2_conclusion: hoja `Conclusion consolidada` (BLUF, 29 conclusiones por categoria,
respuesta a las 4 preguntas del profesor y grafico de conclusiones por categoria y confianza)."""
import os
import sys

from openpyxl.styles import Font

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))
from x2_formato import (BORDE, anchos_col, condiciones, descripcion, encabezado,  # noqa: E402
                        fila_datos, nota, subtitulo, tabla, titulo)
from x5_graficos import bloque  # noqa: E402

ANCHOS_CONCL = [6, 6, 40, 62, 44, 10, 38]
ENC_CONCL = ["id", "fase", "afirmacion", "evidencia", "implicacion", "confianza", "fuente"]

PREGUNTAS = [
    ("En que rangos hay KALINA (total)?", "F1 Existencia; F1 Reglas y zonas grises", "D1 a D6"),
    ("Partiendo de un KALINA, que pasa al mover una o dos variables?",
     "F2 CORREGIBLE vs KALINA; F2 Distancia y rescate", "L2; F6"),
    ("Como se comporta el regenerador?", "F4 Regenerador y condensador", "E4"),
    ("Que datos necesito para preseleccionar los equipos?", "F4 Preseleccion",
     "E1, E2, E3, E5, E6, E7"),
]


def bluf(datos):
    """Cifras de cabecera, calculadas de los CSV. Devuelve (etiqueta, valor, fuente)."""
    d = datos["dataset_dedup"]
    n = len(d)
    pct_kal = round(100.0 * int(d["kalina"].sum()) / n, 1)
    eta_in = round(float(d.loc[~d["fuera_rango"].astype(bool), "eta_pct"].max()), 2)
    eta_out = round(float(d.loc[d["fuera_rango"].astype(bool), "eta_pct"].max()), 2)
    v = datos["violaciones"]
    sel = v[(v["seccion"] == "dominante") & (v["centro"] == "todos") & (v["clave"] == "viol_O2")]
    pct_o2 = round(100.0 * float(sel.iloc[0]["fraccion"]), 1)
    u = datos["distancia_resumen"]
    u = u[(u["seccion"] == "univariado") & (u["centro"] == "todos")]
    b = u.loc[u["valor"].idxmax()]
    return [
        ("n de puntos (sin duplicados)", n,
         "p2_dataset_dedup.csv (de 3921 en la campana, p1_dataset.csv)"),
        ("% KALINA (total)", pct_kal, "p2_dataset_dedup.csv"),
        ("eta maxima dentro / fuera del rango experimental (%)",
         "%s / %s" % (eta_in, eta_out), "p2_dataset_dedup.csv"),
        ("% de CORREGIBLE por cavitacion (viol_O2 dominante)", pct_o2,
         "p2_violaciones.csv (centro todos)"),
        ("variable que mas rescata", "%s (%s %%)" % (b["clave"], round(100.0 * float(b["valor"]), 1)),
         "p2_distancia_resumen.csv (univariado, todos)"),
    ]


def _alturas(ws, f, filas, anchos):
    for fila in filas:
        lineas = 1
        for j, v in enumerate(fila):
            if isinstance(v, str) and anchos[j]:
                lineas = max(lineas, len(v) // max(anchos[j] - 2, 4) + 1)
        ws.row_dimensions[f].height = 13 * lineas + 4
        f += 1


def _tabla_texto(ws, f, enc, filas, anchos):
    """Tabla con ajuste de linea y alto de fila calculado para no cortar el texto."""
    r = encabezado(ws, f, enc, anchos)
    for fila in filas:
        fila_datos(ws, r, fila)
        r += 1
    _alturas(ws, r - len(filas), filas, anchos)
    return r


def hoja_conclusion(wb, datos):
    ws = wb.create_sheet("Conclusion consolidada")
    concl = datos["conclusiones"]
    f = 1
    f = titulo(ws, f, "Conclusion consolidada", ancho=12)
    f = subtitulo(ws, f, "Cifras de cabecera")
    f = condiciones(ws, f, ["Que se resume: la campana de Sensibilidad 1 sin duplicados exactos.",
                            "Fuente: p2_dataset_dedup.csv, p2_violaciones.csv y "
                            "p2_distancia_resumen.csv."])
    _, f, _ = tabla(ws, f, ["Cifra", "Valor", "Fuente"], bluf(datos), anchos=[46, 22, 60])
    f += 1

    f = subtitulo(ws, f, "Respuesta a las 4 preguntas del profesor")
    _, f, _ = tabla(ws, f, ["Pregunta del profesor", "Hoja donde se responde",
                            "Conclusion que la contesta"], PREGUNTAS, anchos=[52, 52, 20])
    f += 1

    f = subtitulo(ws, f, "Las 29 conclusiones, por categoria")
    f = nota(ws, f, "7 columnas: id, fase, afirmacion, evidencia, implicacion, confianza y fuente, "
                    "tal como estan en p5_conclusiones.csv.")
    f += 1
    for cat in list(dict.fromkeys(concl["categoria"])):
        sub = concl[concl["categoria"] == cat]
        f = subtitulo(ws, f, "%s (%d conclusiones)" % (cat, len(sub)))
        filas = [[r["id"], r["fase"], r["afirmacion"], r["evidencia"], r["implicacion"],
                  r["confianza"], r["fuente"]] for _, r in sub.iterrows()]
        f = _tabla_texto(ws, f, ENC_CONCL, filas, ANCHOS_CONCL)
        f += 1

    f = subtitulo(ws, f, "Numero de conclusiones por categoria y confianza")
    cats = list(dict.fromkeys(concl["categoria"]))
    confs = list(dict.fromkeys(concl["confianza"]))
    filas = [[c] + [int((concl[(concl["categoria"] == c) & (concl["confianza"] == k)]).shape[0])
                    for k in confs] for c in cats]
    f = bloque(ws, f, titulo="Conclusiones por categoria y confianza",
               encabezados=["Categoria"] + confs, filas=filas, x="Categoria",
               y="Numero de conclusiones", tipo="barras", apiladas=True,
               nota_txt="Fuente: p5_conclusiones.csv. Altura = numero de conclusiones de la "
                        "categoria, repartidas por confianza.", alto=9.0)
    f = descripcion(ws, f, [
        "Cifras de cabecera calculadas de los CSV (no escritas a mano).",
        "Las 29 conclusiones de p5_conclusiones.csv, en el orden DISENO REAL, EQUIPOS, MAXIMA "
        "EFICIENCIA, FLUCTUACION y LIMITES KALINA.",
        "La tabla de preguntas enlaza cada pregunta del profesor con su hoja y su conclusion."])
    return ws
