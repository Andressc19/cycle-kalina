# -*- coding: utf-8 -*-
"""Sens2 - s2_leeme: hoja LEEME (que es el libro, campana, guia, terminologia, centros,
preguntas del profesor y limitaciones)."""
import os
import sys

from openpyxl.styles import Alignment, Font

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))
from x1_cargar import CENTROS  # noqa: E402
from x2_formato import condiciones, nota, subtitulo, tabla, titulo  # noqa: E402

# Parrafo de rango experimental, copiado del libro 1 (x7_construir). No se importa x7_construir
# porque construye el libro entero al importarse.
TEXTO_RANGO = (
    "La ecuación del motor (IAPWS G4-01, §6) fue contrastada con datos experimentales de líquido "
    "hasta 420 K y de vapor hasta 10 MPa. Un punto queda «fuera del rango experimental» cuando "
    "alguno de sus estados de líquido o bifásico supera 420 K (en esta campaña, T2 o T5; ocurre "
    "desde unos 150 °C de fuente). El motor lo calcula y lo clasifica igual, y la guía declara la "
    "ecuación válida hasta el lugar crítico; la marca solo informa que en esa zona no hay datos "
    "experimentales con que contrastar el cálculo. Estos puntos forman parte de los resultados y "
    "de las conclusiones. El lugar crítico no se vigila en el motor (la guía advierte que su "
    "ubicación es incierta); con P_alta <= 5 MPa en esta campaña no se espera cruzarlo, pero no se "
    "comprobó punto por punto.")

GUIA = [
    ("LEEME", "Que es el libro, de que campana viene, terminologia, los 4 centros, las preguntas "
              "del profesor y las limitaciones."),
    ("Conclusion consolidada", "Cifras de cabecera, las conclusiones por categoria, la respuesta "
                               "a las 4 preguntas y su grafico."),
    ("F1 Existencia", "Rango con KALINA (total) por bloque, fronteras de los barridos y P(KALINA) "
                      "por nivel de las variables con 14 niveles o menos."),
    ("F1 Reglas y zonas grises", "Mejores cortes unicos, regresion logistica, reglas del arbol y "
                                 "conteo de zonas grises."),
    ("F1 Margenes de operacion", "Cuanto se puede mover cada variable desde el centro KALINA de cada bloque: "
                                 "una variable, dos (mallas de pares) y varias a la vez."),
    ("F2 CORREGIBLE vs KALINA", "Comparacion de eta, W_net/m_b, r_P, Q_reg/Q_i, dh y q4, violacion "
                                "dominante por bloque y D por cuartil."),
    ("F2 Distancia y rescate", "Variable que rescata a un CORREGIBLE, distribucion de la distancia, "
                               "cambio de eta al rescatar y robustez del optimo."),
    ("F3 Indices globales", "Indices de sensibilidad global por bloque (PRCC, KS, PAWN, delta, HSIC) con piso de ruido."),
    ("F3 Interacciones", "No aditividad de los pares de variables."),
    ("F3 Elasticidades", "Elasticidades locales de eta en el punto base."),
    ("F4 Turbina", "Envolventes, bandas de r_P y dependencias de la turbina."),
    ("F4 Regenerador y condensador", "Envolventes y dependencias del regenerador, el condensador, "
                                     "el HRVG y la bomba; restricciones activas."),
    ("F4 Preseleccion", "Datos para preseleccionar los equipos."),
    ("F4 Regenerador vs T_fuente", "Regenerador y ciclo frente a T_fuente de 70 a 300 C: Q_reg/Q_i, pinch, UA y eta."),
    ("D1 Datos puntos", "Todos los puntos analizados (p2_dataset_dedup.csv)."),
    ("D2 Datos fronteras", "Fronteras de los barridos de una variable (p1_fronteras.csv)."),
    ("D3 Datos zonas grises", "Zonas grises por bloque y violacion dominante (p1_zonas_grises.csv)."),
    ("D4 Datos distancia", "Distancia a la frontera de cada CORREGIBLE (p2_distancia.csv)."),
    ("D5 Datos indices", "Indices de sensibilidad por bloque, respuesta, variable y metodo (p3_indices.csv)."),
    ("D6 Datos equipos", "Turbina y regenerador por banda de r_P (p4_bandas.csv)."),
]

PREGUNTAS = [
    ("En que rangos hay KALINA (total)?", "F1 Existencia; F1 Reglas y zonas grises"),
    ("Partiendo de un KALINA, que pasa si muevo una o dos variables?",
     "F2 CORREGIBLE vs KALINA; F2 Distancia y rescate"),
    ("Como se comporta el regenerador?", "F4 Regenerador vs T_fuente; F4 Regenerador y condensador"),
    ("Que datos necesito para preseleccionar los equipos?", "F4 Preseleccion"),
]

VARS_CENTRO = ["T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "eta_t", "eta_p",
               "eps_hrvg", "eps_reg", "eps_cond"]


def _centros_filas():
    filas = []
    for bloque in ("C1 Husavik", "C2 ancla A*", "C3 caliente 150 C", "C4 frio 110 C"):
        c = CENTROS[bloque]
        filas.append([bloque] + [c[v] for v in VARS_CENTRO])
    return filas


def hoja_leeme(wb, datos):
    ws = wb.create_sheet("LEEME")
    ws.column_dimensions["A"].width = 34
    ws.column_dimensions["B"].width = 90
    f = 1
    f = titulo(ws, f, "Libro 2 - Analisis de sensibilidad sobre la campana de Sensibilidad 1", ancho=12)
    f = subtitulo(ws, f, "Que es este libro y de que campana viene")
    for linea in [
            "Este libro analiza, sin corridas nuevas del motor, los 3 921 puntos de la campana de "
            "Sensibilidad 1 (libro 1).",
            "Se quitan los duplicados exactos (mismas 10 entradas y mismo centro): quedan 3 663 "
            "puntos, que son los que usa el analisis.",
            "Base por hoja: F1 usa los 3 921 puntos (con duplicados); F2, F3 y F4 usan los 3 663 sin "
            "duplicados; por eso los n difieren (p. ej. C1: 502 KALINA en F1 y 454 en F2).",
            "Cavitacion (O2) = margen m_O2 = T_burbuja(P_baja, x_b) - T9 (subenfriamiento a la entrada de la bomba, "
            "minimo 1 K); no es un calculo de NPSH. 'Confianza' de cada conclusion = robustez dentro del modelo teqp.",
            "Todos los numeros salen de los CSV de resultados/ (P1 a P4 y p5_conclusiones.csv); "
            "ninguno se escribe a mano.",
            "Clases: KALINA, CORREGIBLE, NO_CONVERGIO e INVIABLE. Un KALINA puede estar dentro o "
            "fuera del rango experimental (ver terminologia)."]:
        ws.cell(f, 1, linea).font = Font(size=10)
        f += 1
    f += 1

    f = subtitulo(ws, f, "Guia de hojas")
    f = condiciones(ws, f, ["Fuente: estructura del libro.", "Que se lista: todas las hojas, en su orden."])
    _, f, _ = tabla(ws, f, ["Hoja", "Contenido"], [[n, d] for n, d in GUIA], anchos=[34, 90])
    f += 1

    f = subtitulo(ws, f, "Terminologia: el rango experimental")
    ws.cell(f, 1, TEXTO_RANGO).alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=f, start_column=1, end_row=f, end_column=2)
    ws.row_dimensions[f].height = 15 * (len(TEXTO_RANGO) // 110 + 1) + 6
    f += 2

    f = subtitulo(ws, f, "Los 4 centros de bloque y sus constantes")
    f = condiciones(ws, f, ["Que quedo fijo: las constantes de cada bloque (las mismas del libro 1).",
                            "Que se barrio: en Sensibilidad 2 no se barre nada; se analizan los "
                            "puntos ya calculados alrededor de estos centros."])
    enc = ["Bloque"] + [v + " (" + u + ")" for v, u in (
        ("T_fuente", "K"), ("T_sumidero", "K"), ("P_alta", "kPa"), ("P_baja", "kPa"), ("x_b", "-"),
        ("eta_t", "-"), ("eta_p", "-"), ("eps_HRVG", "-"), ("eps_reg", "-"), ("eps_cond", "-"))]
    _, f, _ = tabla(ws, f, enc, _centros_filas(),
                    anchos=[20] + [11] * 10)
    f += 1

    f = subtitulo(ws, f, "Preguntas del profesor y donde se responden")
    _, f, _ = tabla(ws, f, ["Pregunta del profesor", "Hoja que la responde"], PREGUNTAS,
                    anchos=[60, 60])
    f += 1

    f = subtitulo(ws, f, "Limitaciones")
    l5 = datos["conclusiones"]
    r = l5[l5["id"] == "L5"].iloc[0]
    ws.cell(f, 1, "Conclusión L5 - " + str(r["afirmacion"])).font = Font(size=10, bold=True)
    f += 1
    ws.cell(f, 1, str(r["evidencia"])).alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=f, start_column=1, end_row=f, end_column=2)
    ws.row_dimensions[f].height = 15 * (len(str(r["evidencia"])) // 110 + 1) + 6
    f += 2
    f = nota(ws, f, "Implicacion (L5): " + str(r["implicacion"]))
    f = nota(ws, f, "Fuente: p5_conclusiones.csv (L5).")
    return ws
