# -*- coding: utf-8 -*-
"""Sens2 - s2_comun: utilidades compartidas (redondeo, orden de niveles, etiqueta de centro y un
grafico de barras que admite valores negativos, que `x5_graficos` recortaria a cero)."""
import math
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "analisis_final"))
from openpyxl.chart import BarChart, Reference  # noqa: E402
from openpyxl.chart.series import SeriesLabel  # noqa: E402
from a2_graf_estilo import acabado, escala  # noqa: E402
from x1_cargar import SIN_CENTRO  # noqa: E402
from x2_formato import encabezado, fila_datos  # noqa: E402
from x5_graficos import COL_GRAF, FILAS_GRAF, celda_grafico  # noqa: E402

COLORES = ["2E7D32", "1F4E79", "C0392B", "B9770E", "6A1B9A", "00838F", "4E342E"]


def numero(x, n=4):
    if x is None:
        return None
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        return None
    return round(float(x), n)


def nivel_lo(s):
    """Limite inferior de una etiqueta de nivel ('[lo, hi)' o valor exacto); +inf si no es numero."""
    t = str(s).strip()
    try:
        if t.startswith("["):
            return float(t[1:].split(",")[0])
        return float(t)
    except ValueError:
        return float("inf")


def centro_txt(c):
    if c is None or (isinstance(c, float) and math.isnan(c)) or c == "":
        return SIN_CENTRO
    return c


def prob_lhs(datos, variable, bloques):
    """P(KALINA) por nivel del muestreo LHS de una variable, ordenada por nivel, por bloque."""
    p = datos["existencia_prob"]
    p = p[(p["muestra"] == "lhs") & (p["variable"] == variable) & (p["centro"].isin(bloques))]
    out = {}
    for b in bloques:
        s = p[p["centro"] == b].copy()
        s["_lo"] = s["nivel"].map(nivel_lo)
        out[b] = s.sort_values("_lo")["p_kalina"].tolist()
    return out


def niveles_lhs(datos, variable, bloques):
    """Texto del intervalo de cada banda del muestreo LHS de una variable, ordenado por nivel, por bloque."""
    p = datos["existencia_prob"]
    p = p[(p["muestra"] == "lhs") & (p["variable"] == variable) & (p["centro"].isin(bloques))]
    out = {}
    for b in bloques:
        s = p[p["centro"] == b].copy()
        s["_lo"] = s["nivel"].map(nivel_lo)
        out[b] = s.sort_values("_lo")["nivel"].astype(str).tolist()
    return out


def barras_con_signo(ws, fila, encabezados, filas, *, titulo, x, y, anchos=None):
    """Tabla + grafico de barras de Excel cuyos valores pueden ser negativos (escala propia)."""
    encabezado(ws, fila, list(encabezados), anchos)
    r = fila + 1
    for f in filas:
        fila_datos(ws, r, list(f))
        r += 1
    ultima = fila + len(filas)
    ch = BarChart()
    ch.type, ch.title, ch.style = "col", titulo, 10
    ch.x_axis.title, ch.y_axis.title = x, y
    for k in range(len(encabezados) - 1):
        col = 2 + k
        ch.add_data(Reference(ws, min_col=col, min_row=fila + 1, max_col=col, max_row=ultima),
                    titles_from_data=False)
        ser = ch.series[-1]
        color = COLORES[k % len(COLORES)]
        ser.graphicalProperties.solidFill = color
        ser.graphicalProperties.line.solidFill = color
        ser.invertIfNegative = False
        ser.tx = SeriesLabel(v=encabezados[k + 1])
    ch.set_categories(Reference(ws, min_col=1, min_row=fila + 1, max_col=1, max_row=ultima))
    vals = [f[k + 1] for f in filas for k in range(len(encabezados) - 1)]
    escala(ch.y_axis, vals, desde_cero=False)
    ch.legend.position = "b"
    ch.width, ch.height = 18.0, 9.0
    ch.visible_cells_only = False
    acabado(ch)
    ws.add_chart(ch, celda_grafico(ws.title, fila, COL_GRAF))
    return max(ultima + 2, fila + FILAS_GRAF) + 2
