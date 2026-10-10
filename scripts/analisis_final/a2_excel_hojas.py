# -*- coding: utf-8 -*-
"""A2 · Hojas del libro Excel_kalina_final_final_final.xlsx (todas menos el Tablero).

Escrito por el director (Claude) el 2026-10-10 (OpenCode sin modelo disponible).
Formato §6.3: filas 1–6 = encabezado de condiciones; tabla desde la fila 8 con filtro;
notas al final; colores por clase; todo en español.
"""
import glob
import os

import pandas as pd
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from a2_columnas import tipo_por_unidad
from a2_comun import COLOR_CLASE, RAIZ, TABLAS, fmt_excel
from nombres import GLOSARIO

FIG = os.path.join(RAIZ, "analisis_final", "03_figuras")
NEGRITA, TITULO = Font(bold=True), Font(bold=True, size=13)
GRIS = PatternFill("solid", fgColor="DDEBF7")
CLASES_TXT = {"KALINA": "KALINA", "CORREGIBLE": "CORREGIBLE", "Corregible": "CORREGIBLE",
              "INVIABLE": "INVIABLE", "Inviable": "INVIABLE", "NO_CONVERGIO": "NO_CONVERGIO",
              "No convergió": "NO_CONVERGIO", "N2": "N2"}
FIGURAS_DE = {"M02-N1": ["FIG-M02-01"], "M02-N2": ["FIG-M02-02"], "M02R": ["FIG-M02R"],
              "M02S": ["FIG-M02S"], "M03": ["FIG-M03"], "M04": ["FIG-M04-"], "M04c": ["FIG-M04c"],
              "M05": ["FIG-M05-S"], "M05c": ["FIG-M05c"], "M06": ["FIG-M06"], "M07": ["FIG-M07"],
              "M09": ["FIG-M09"], "M10": ["FIG-M10-"], "M10b": ["FIG-M10-01"], "G": ["FIG-G"]}


def nombre_hoja(txt):
    for c in '[]:*?/\\':
        txt = txt.replace(c, "_")
    return txt[:31]


def _anchos(ws, n_col, fila_ini, fila_fin):
    for j in range(1, n_col + 1):
        largo = max((len(str(ws.cell(i, j).value or "")) for i in range(fila_ini, fila_fin + 1)),
                    default=8)
        ws.column_dimensions[get_column_letter(j)].width = min(max(10, largo + 2), 48)


def hoja_tabla(wb, meta, condiciones):
    """Una tabla TAB-* con encabezado (1–6), cuerpo (8…) y notas."""
    carpeta = os.path.join(TABLAS, meta["carpeta"])
    df = pd.read_csv(os.path.join(carpeta, meta["tabla"] + ".csv"))
    ws = wb.create_sheet(nombre_hoja(meta["hoja"]))
    ws["A1"] = f"{meta['tabla']} · {meta['titulo']}"; ws["A1"].font = TITULO
    ws["A2"] = f"Caso(s): {meta['casos']} · Bloque(s): {meta['bloques']}"
    ws["A3"] = f"Punto base: {meta['punto_base']}"
    lineas = condiciones.splitlines() if condiciones else \
        ["Tabla de síntesis: cada fila es un caso con sus propios datos fijos."]
    ws["A4"] = lineas[0]
    ws["A5"] = lineas[1] if len(lineas) > 1 else ""
    ws["A6"] = f"Filtro: {meta['filtro']} · Fuente: {meta['fuente']}"
    for r in range(1, 7):
        ws.cell(r, 1).alignment = Alignment(wrap_text=False)
    for j, col in enumerate(df.columns, 1):
        c = ws.cell(8, j, col); c.font = NEGRITA; c.fill = GRIS
        c.alignment = Alignment(wrap_text=True, vertical="top")
    for i, fila in enumerate(df.itertuples(index=False), 9):
        for j, (col, v) in enumerate(zip(df.columns, fila), 1):
            v = None if (isinstance(v, float) and pd.isna(v)) else v
            if isinstance(v, float) and not float(v).is_integer():
                v = float(f"{v:.5g}")              # 10.87115255 → 10.871
            cel = ws.cell(i, j, v)
            fmt = fmt_excel(tipo_por_unidad(col), v) if isinstance(v, (int, float)) else None
            if fmt:
                cel.number_format = fmt
            clase = CLASES_TXT.get(str(v)) if isinstance(v, str) else None
            if clase:
                cel.fill = PatternFill("solid", fgColor=COLOR_CLASE[clase])
    fin = 8 + len(df)
    if len(df):
        ws.auto_filter.ref = f"A8:{get_column_letter(len(df.columns))}{fin}"
    nota = (f"Notas: n = {meta['n']}. † = fuera del rango confiable (IAPWS G4-01); "
            f"‡ = falso convergido (N2). {meta['notas'] if isinstance(meta['notas'], str) else ''}")
    ws.cell(fin + 2, 1, nota).font = Font(italic=True)
    ws.freeze_panes = "B9"
    _anchos(ws, len(df.columns), 8, fin)
    return ws.title


def hoja_figuras(wb, clave, titulo):
    """Hoja <clave>_figuras con cada PNG (ancho ~16 cm) y su pie debajo."""
    ws = wb.create_sheet(nombre_hoja(f"{clave}_figuras"))
    ws["A1"] = titulo; ws["A1"].font = TITULO
    pngs = []
    for pref in FIGURAS_DE.get(clave, []):
        pngs += sorted(glob.glob(os.path.join(FIG, "*", pref + "*.png")))
    if not pngs:
        ws["A3"] = "Este caso no lleva figura (ver su ficha)."
        return ws.title
    fila = 3
    for p in dict.fromkeys(pngs):
        img = XLImage(p)
        esc = 605 / img.width
        img.width, img.height = int(img.width * esc), int(img.height * esc)
        ws.add_image(img, f"A{fila}")
        fila += int(img.height / 20) + 2
        pie = p[:-4] + ".pie.md"
        texto = open(pie, encoding="utf-8").read() if os.path.exists(pie) else ""
        for linea in texto.splitlines():
            ws.cell(fila, 1, linea).font = Font(size=9, italic=True)
            fila += 1
        fila += 2
    ws.column_dimensions["A"].width = 120
    return ws.title


def hoja_leeme(wb):
    ws = wb.active; ws.title = "LEEME"
    filas = ["Ciclo Kalina KCS-11 — resultados de la campaña final de barridos (M1–M10b)", "",
             "Para qué es este libro: presentar las tablas y figuras del análisis, organizadas por bloque.",
             "Un bloque reúne puntos con las MISMAS variables fijas en los MISMOS valores: solo se comparan "
             "puntos de un mismo bloque.",
             "Cómo leer cada hoja: filas 1–6 = qué caso es, punto base, datos fijos y barridos, filtro y "
             "fuente; la tabla empieza en la fila 8 (con filtros); las notas van al final.",
             "Hoja Tablero: elija un bloque en la celda B2 y se actualizan las cifras, las condiciones y "
             "los gráficos.", "", "Glosario:"]
    filas += [f"• {k}: {v}" for k, v in GLOSARIO.items()]
    filas += ["", "Colores de clase:"]
    for i, t in enumerate(filas, 1):
        ws.cell(i, 1, t)
    ws["A1"].font = TITULO
    r = len(filas) + 1
    for clase, txt in (("KALINA", "KALINA: cumple todos los criterios"),
                       ("CORREGIBLE", "CORREGIBLE: falla un criterio operativo (casi siempre O2)"),
                       ("INVIABLE", "INVIABLE: falla un criterio estructural (O3, O5…)"),
                       ("NO_CONVERGIO", "NO_CONVERGIO: el modelo no encontró un ciclo"),
                       ("N2", "N2: falso convergido (no cuenta)")):
        c = ws.cell(r, 1, txt); c.fill = PatternFill("solid", fgColor=COLOR_CLASE[clase]); r += 1
    ws.column_dimensions["A"].width = 130


def hoja_profesor(wb):
    ws = wb.create_sheet("Punto_profesor")
    datos = [("P_alta", "kPa", 3000, 3000), ("P_baja", "kPa", 400, 563.64), ("x_b", "–", 0.5, 0.5),
             ("T_fuente", "K", 623.15, 403), ("T_sumidero", "K", 300.032917, 300.032917),
             ("η_t", "–", 0.85, 0.85), ("η_p", "–", 0.75, 0.75), ("ε_HRVG", "–", 0.85, 0.85),
             ("ε_reg", "–", 0.75, 0.75), ("ε_cond", "–", 0.80, 0.80), ("m_b", "kg/s", 1, 1)]
    ws.append(["Dato", "Unidad", "Punto del profesor (PP)", "Punto ancla A*"])
    for d in datos:
        ws.append(list(d))
    for c in ws[1]:
        c.font = NEGRITA; c.fill = GRIS
    ws.append([]); ws.append(["A* = PP con solo dos cambios (T_fuente y P_baja). Es KALINA, η = 8.48 %. "
                              "PP no converge (M1)."])
    _anchos(ws, 4, 1, 12)


def hoja_df(wb, nombre, df, oculta=False):
    """Hoja con un DataFrame plano como tabla con filtros (Datos, Condiciones, Bloques)."""
    ws = wb.create_sheet(nombre)
    ws.append(list(df.columns))
    for fila in df.itertuples(index=False):
        ws.append([None if (isinstance(v, float) and pd.isna(v)) else v for v in fila])
    for c in ws[1]:
        c.font = NEGRITA; c.fill = GRIS
    ws.auto_filter.ref = ws.dimensions
    ws.freeze_panes = "A2"
    if oculta:
        ws.sheet_state = "hidden"
    return ws
