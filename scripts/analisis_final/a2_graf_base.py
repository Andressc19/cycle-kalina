# -*- coding: utf-8 -*-
"""A2 · Gráficos nativos de Excel (Claude, 2026-10-11). Datos visibles en la hoja "N Datos de
gráficos" de cada pregunta (desde el 2026-10-12; antes en la hoja oculta Aux_graficos);
títulos y pies desde los .pie.md de Matplotlib, para que las dos versiones digan lo mismo."""
import copy
import glob
import math
import os

import numpy as np
from openpyxl.chart import BarChart, Reference, ScatterChart, Series
from openpyxl.chart.marker import DataPoint
from openpyxl.chart.series import SeriesLabel
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter as L

from a2_comun import RAIZ
from a2_excel_hojas import cuadricula
from a2_graf_estilo import acabado, escala as _escala
from codigos import PREGUNTA, figura
from codigos_texto import traducir
from nombres import ETIQUETA_CLASE, NOMBRE

FIG = os.path.join(RAIZ, "analisis_final", "03_figuras")
ORDEN = ["KALINA", "CORREGIBLE", "INVIABLE", "NO_CONVERGIO", "N2"]
COLOR = {"KALINA": "2E7D32", "CORREGIBLE": "EF8A17", "INVIABLE": "C9A227",
         "NO_CONVERGIO": "C62828", "N2": "9E9E9E"}
SIMB = {"KALINA": "circle", "CORREGIBLE": "triangle", "INVIABLE": "square",
        "NO_CONVERGIO": "x", "N2": "x"}
FILA_CLASE = {"N2": 0, "NO_CONVERGIO": 1, "INVIABLE": 2, "CORREGIBLE": 3, "KALINA": 4}
EJE_CLASE = "Clase (4 K · 3 C · 2 I · 1 NC · 0 N2)"
COPIAS = []                          # figuras ya armadas, para colocarlas junto a su tabla
FILA_ROT, FILA_ENC = 4, 5            # en la hoja de datos: rótulo de la figura y encabezados
GRIS = PatternFill("solid", fgColor="DDEBF7")
AZUL = PatternFill("solid", fgColor="1F4E79")
CM_FILA, CM_COL = 0.53, 1.7          # alto de fila y ancho de columna por defecto, en cm


def pie_fig(prefijo):
    """(título, líneas del pie) de la figura de Matplotlib equivalente."""
    f = sorted(glob.glob(os.path.join(FIG, "*", f"Figura_{figura(prefijo)}_*.pie.md")))
    if not f:
        return prefijo, []
    lineas = open(f[0], encoding="utf-8").read().splitlines()
    tit = lineas[0].split(". ", 1)[1].rstrip(".") if ". " in lineas[0] else lineas[0]
    return tit, lineas


class Lienzo:
    """Hoja de gráficos de una pregunta + sus datos visibles en "N Datos de gráficos"."""

    def __init__(self, wb, pregunta):
        """Una hoja por pregunta ("2 Gráficos"); si ya existe, se sigue escribiendo debajo."""
        self.pregunta = pregunta
        nom_aux = f"{pregunta} Datos de gráficos"
        self.aux = wb[nom_aux] if nom_aux in wb.sheetnames else self._aux(wb, nom_aux, pregunta)
        nombre = f"{pregunta} Gráficos"
        if nombre in wb.sheetnames:
            self.ws = wb[nombre]; self.fila = self.ws._fila
            return
        self.ws = wb.create_sheet(nombre)
        tit = "Síntesis de toda la campaña" if pregunta == "S" else f"Pregunta {pregunta} · {PREGUNTA[pregunta]}"
        self.ws["A1"] = tit; self.ws["A1"].font = Font(bold=True, size=14)
        self.ws["A2"] = ("Gráficos nativos de Excel: pase el cursor sobre un punto para ver su valor. "
                         f"Los números de cada gráfico están en la hoja «{nom_aux}» "
                         "(el subtítulo de cada figura lleva un vínculo a su bloque).")
        self.fila = self.ws._fila = 4

    @staticmethod
    def _aux(wb, nombre, pregunta):
        a = wb.create_sheet(nombre)
        tit = "síntesis" if pregunta == "S" else f"pregunta {pregunta}"
        a["A1"] = f"Datos de los gráficos de la {tit}"; a["A1"].font = Font(bold=True, size=14)
        a["A2"] = ("Cada bloque de columnas es una figura; cada serie ocupa dos columnas "
                   "(valores de x y de y, o categoría y valor).")
        a._sig = a._ini = 1
        return a

    def datos(self, nombre, valores):
        """Escribe una columna en la hoja de datos y devuelve su Reference (o None si vacía)."""
        col = self.aux._sig; self.aux._sig += 1
        c = self.aux.cell(FILA_ENC, col, nombre)
        c.font = Font(bold=True); c.fill = GRIS
        c.alignment = Alignment(wrap_text=True, vertical="top")
        self.aux.column_dimensions[L(col)].width = 16
        vals = [None if (v is None or (isinstance(v, float) and math.isnan(v))) else
                (round(float(v), 6) if isinstance(v, (int, float, np.floating, np.integer)) else v)
                for v in valores]
        for i, v in enumerate(vals, FILA_ENC + 1):
            self.aux.cell(i, col, v)
        n = max(len(vals), 1)
        self.aux._alto = max(getattr(self.aux, "_alto", 0), n)
        return Reference(self.aux, min_col=col, min_row=FILA_ENC + 1, max_row=FILA_ENC + n)

    def _cerrar_datos(self, subtitulo):
        """Rotula el bloque de columnas escrito desde la figura anterior; devuelve su celda."""
        a = self.aux
        ini, fin = a._ini, a._sig - 1
        if fin < ini:
            return None
        c = a.cell(FILA_ROT, ini, traducir(subtitulo))
        c.font = Font(bold=True, color="FFFFFF"); c.fill = AZUL
        for j in range(ini, fin + 1):
            a.cell(FILA_ROT, j).fill = AZUL
        cuadricula(a, FILA_ENC, ini, FILA_ENC + getattr(a, "_alto", 0), fin)
        a._alto = 0
        a._sig += 1                                   # una columna en blanco entre figuras
        a._ini = a._sig
        return f"{L(ini)}{FILA_ROT}"

    # ------------------------------------------------------------- colocación
    def bloque(self, subtitulo, graficos, por_fila=1, ancho=17.0, alto=8.5, pie=(), fig=None):
        """Coloca una fila (o rejilla) de gráficos con su subtítulo arriba y el pie abajo.
        Además guarda una copia de cada gráfico en COPIAS (id de figura `fig`) para ponerla junto
        a la tabla de la que salen sus datos (a2_excel_copias, 2026-10-12)."""
        copias = []
        c0 = self.ws.cell(self.fila, 1, traducir(subtitulo)); c0.font = Font(bold=True, size=11)
        ref = self._cerrar_datos(subtitulo)
        if ref:
            c0.hyperlink = f"#'{self.aux.title}'!{ref}"
        self.fila += 1
        cols_graf = math.ceil(ancho / CM_COL) + 1
        filas_graf = math.ceil(alto / CM_FILA) + 1
        for i, g in enumerate(graficos):
            g.width, g.height = ancho, alto
            g.visible_cells_only = False
            acabado(g, chico=ancho < 12)
            if isinstance(g, BarChart):
                g.x_axis.crosses = g.y_axis.crosses = "autoZero"
                if getattr(g, "_lbl_alto", False):      # categorías invertidas: números abajo
                    g.y_axis.tickLblPos = "high"
            copias.append(copy.deepcopy(g))
            r = self.fila + (i // por_fila) * filas_graf
            c = 1 + (i % por_fila) * cols_graf
            self.ws.add_chart(g, f"{L(c)}{r}")
        COPIAS.append({"fig": fig, "subtitulo": traducir(subtitulo), "charts": copias,
                       "por_fila": por_fila, "ancho": ancho, "alto": alto,
                       "pie": [traducir(x) for x in pie]})
        self.fila += math.ceil(len(graficos) / por_fila) * filas_graf
        for linea in pie:
            self.ws.cell(self.fila, 1, traducir(linea)).font = Font(size=9, italic=True)
            self.fila += 1
        self.fila += 2
        self.ws._fila = self.fila


def disp_clases(lz, sub, x, y, titulo, xt=None, yt=None, tira=False, n_max=None):
    """Dispersión con una serie por clase (forma + color); fuera de rango = marcador hueco.
    tira=True: el eje y es la fila de la clase (para barridos sin η que graficar)."""
    sc = ScatterChart(); sc.title = titulo; sc.style = 13
    sc.x_axis.title = xt or NOMBRE.get(x, x)
    sc.y_axis.title = EJE_CLASE if tira else (yt or NOMBRE.get(y, y))
    sub = sub[~sub["omitido"].astype(bool)] if "omitido" in sub else sub
    for c in ORDEN:
        g = sub[sub["clase_trazo"] == c]
        if g.empty:
            continue
        fuera = g["fuera_rango"].astype(bool) if c not in ("NO_CONVERGIO", "N2") else g.index != g.index
        for hueco, parte in ((False, g[~fuera]), (True, g[fuera])):
            if parte.empty:
                continue
            ys = ([FILA_CLASE[c] + 0.1 * (k % 3) for k in range(len(parte))] if tira
                  else parte[y].tolist())
            etq = f"{ETIQUETA_CLASE[c]}{', fuera de rango' if hueco else ''} (n = {len(parte)})"
            pre = f"{titulo} · " if titulo else ""
            ny = "fila de la clase (solo para dibujar)" if tira else (yt or NOMBRE.get(y, y))
            s = Series(lz.datos(f"{pre}{etq} · y: {ny}", ys),
                       lz.datos(f"{pre}{etq} · x: {xt or NOMBRE.get(x, x)}", parte[x].tolist()), title=etq)
            s.marker.symbol, s.marker.size = SIMB[c], 6
            if SIMB[c] == "x":                         # el ✕ se dibuja solo con la línea
                s.marker.size = 7
                s.marker.graphicalProperties.noFill = True
            elif hueco:
                s.marker.graphicalProperties.noFill = True
            else:
                s.marker.graphicalProperties.solidFill = COLOR[c]
            s.marker.graphicalProperties.line.solidFill = COLOR[c]
            s.graphicalProperties.line.noFill = True
            sc.series.append(s)
    _escala(sc.x_axis, sub[x].tolist())
    if tira:
        sc.y_axis.scaling.min, sc.y_axis.scaling.max, sc.y_axis.majorUnit = 0, 4.5, 1
    else:
        _escala(sc.y_axis, sub[y].tolist())
    sc.legend.position = "b"
    return sc


def lineas(lz, series, titulo, xt, yt, punteadas=(), marcador=True):
    """series: [(nombre, xs, ys, color)]. Líneas con marcador; 'punteadas' = nombres a trazos."""
    sc = ScatterChart(); sc.title = titulo; sc.style = 13
    sc.x_axis.title, sc.y_axis.title = xt, yt
    todos_x, todos_y = [], []
    for nombre, xs, ys, color in series:
        pre = f"{titulo} · " if titulo else ""
        s = Series(lz.datos(f"{pre}{nombre} · y: {yt}", ys), lz.datos(f"{pre}{nombre} · x: {xt}", xs),
                   title=nombre)
        s.graphicalProperties.line.solidFill = color
        s.graphicalProperties.line.width = 22000
        if nombre in punteadas:
            s.graphicalProperties.line.dashStyle = "dash"
        s.marker.symbol = "circle" if marcador else "none"
        s.marker.size = 5
        s.marker.graphicalProperties.solidFill = color
        s.marker.graphicalProperties.line.solidFill = color
        s.smooth = False
        sc.series.append(s)
        todos_x += list(xs); todos_y += list(ys)
    _escala(sc.x_axis, todos_x); _escala(sc.y_axis, todos_y)
    sc.legend.position = "b"
    return sc


def barras(lz, cats, vals, titulo, xt, yt, horizontal=False, colores=None, series=None):
    """Barras simples (una serie, color por barra) o agrupadas/apiladas (series=[(nombre, vals,
    color)])."""
    b = BarChart(); b.type = "bar" if horizontal else "col"; b.title = titulo; b.style = 10
    b.x_axis.title, b.y_axis.title = xt, yt
    cat = lz.datos(f"{titulo} · categoría: {xt}", cats)
    for nombre, vs, color in (series or [(yt, vals, "2E7D32")]):
        b.add_data(lz.datos(f"{titulo} · {nombre}", vs), titles_from_data=False)
        s = b.series[-1]; s.graphicalProperties.solidFill = color
        s.invertIfNegative = False                # si no, Excel pinta en blanco las barras < 0
        s.graphicalProperties.line.solidFill = color
        s.tx = SeriesLabel(v=nombre)
    b.set_categories(cat)
    if colores and not series:
        for i, col in enumerate(colores):
            p = DataPoint(idx=i, invertIfNegative=False); p.graphicalProperties.solidFill = col
            b.series[0].dPt.append(p)
    if series and len(series) > 1:
        b.legend.position = "b"
    else:
        b.legend = None
    return b
