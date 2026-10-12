# -*- coding: utf-8 -*-
"""A2 · Acabado de los gráficos nativos de Excel (Claude, 2026-10-11): escalas "redondas",
etiquetas de eje en el borde, un color por serie y tamaños de letra según el tamaño del gráfico."""
import math

import numpy as np
from openpyxl.chart.text import RichText
from openpyxl.drawing.text import CharacterProperties, Paragraph, ParagraphProperties


def escala(eje, vals, desde_cero=False):
    """Límites y paso "redondos" (1, 2, 2.5 o 5 × 10^k) para ~5 divisiones."""
    v = np.asarray([x for x in vals if x is not None and np.isfinite(x)], dtype=float)
    if not len(v):
        return
    lo, hi = (0.0 if desde_cero else float(v.min())), float(v.max())
    d = (hi - lo) or abs(hi) or 1.0
    paso = min((m * 10 ** math.floor(math.log10(d / 5)) for m in (1, 2, 2.5, 5, 10)),
               key=lambda p: abs(d / p - 5))
    eje.scaling.min = math.floor(lo / paso) * paso
    eje.scaling.max = math.ceil(hi / paso) * paso
    if eje.scaling.max == eje.scaling.min:
        eje.scaling.max += paso
    eje.majorUnit = paso


def _texto(sz, negrita=False):
    cp = CharacterProperties(sz=sz, b=negrita)
    return RichText(p=[Paragraph(pPr=ParagraphProperties(defRPr=cp), endParaRPr=cp)])


def _titulo(t, sz, negrita):
    """Tamaño de letra de un título ya creado (chart.title o eje.title)."""
    if t is None or t.tx is None or t.tx.rich is None:
        return
    t.overlay = False          # sin este atributo Excel superpone el título al área de datos
    for p in t.tx.rich.p:
        p.pPr = ParagraphProperties(defRPr=CharacterProperties(sz=sz, b=negrita))
        for r in p.r or []:
            r.rPr = CharacterProperties(sz=sz, b=negrita)


def acabado(g, chico=False):
    """Etiquetas de eje en el borde, leyenda fuera del área, un color por serie (no por punto) y
    letra más pequeña en los paneles (con 10 pt los títulos tapaban los números)."""
    g.varyColors = False
    t_tit, t_eje, t_num = (900, 800, 700) if chico else (1100, 900, 800)
    _titulo(g.title, t_tit, True)
    for eje in (g.x_axis, g.y_axis):
        eje.delete = False
        eje.tickLblPos = "low"
        eje.crosses = "min"
        eje.txPr = _texto(t_num)
        _titulo(eje.title, t_eje, False)
    if g.legend is not None:
        g.legend.overlay = False
        g.legend.txPr = _texto(t_num)
    return g
