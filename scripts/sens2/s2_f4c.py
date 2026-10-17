# -*- coding: utf-8 -*-
"""Sens2 - s2_f4c: hoja `F4 Regenerador vs T_fuente` (regenerador y ciclo de 70 a 300 C)."""
import os
import sys

from openpyxl.chart import Reference, ScatterChart, Series

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))
sys.path.insert(0, AQUI)
from x2_formato import condiciones, descripcion, nota, subtitulo, tabla, titulo  # noqa: E402
from x5_graficos import COL_GRAF, FILAS_GRAF, bloque, celda_grafico  # noqa: E402
from s2_calc import BLOQUES, barrido_fuente, estudio4, num  # noqa: E402
from s2_comun import COLORES  # noqa: E402
from a2_graf_estilo import acabado, escala  # noqa: E402

CORTO = {"C1 Husavik": "C1", "C2 ancla A*": "C2", "C3 caliente 150 C": "C3", "C4 frio 110 C": "C4"}
COLS = [("eta_pct", "eta (%)", 3), ("qreg_qi2", "Q_reg/Q_i (-)", 4), ("pinch", "Pinch regenerador (K)", 5),
        ("ua", "UA regenerador (kW/K por kg/s)", 6)]


def _scatter(ws, fila_enc, col, titulo_g, y, rangos, filas_y):
    """Grafico de dispersion con una serie por bloque (cada una con su propio eje x)."""
    ch = ScatterChart()
    ch.title, ch.style = titulo_g, 13
    ch.x_axis.title, ch.y_axis.title = "T_fuente (°C)", y
    xs = []
    for k, (b, (r0, r1)) in enumerate(rangos.items()):
        s = Series(Reference(ws, min_col=col, min_row=r0, max_row=r1),
                   Reference(ws, min_col=2, min_row=r0, max_row=r1), title=CORTO[b])
        c = COLORES[k % len(COLORES)]
        s.graphicalProperties.line.solidFill = c
        s.graphicalProperties.line.width = 22000
        s.marker.symbol = "circle"
        s.marker.size = 5
        s.marker.graphicalProperties.solidFill = c
        s.marker.graphicalProperties.line.solidFill = c
        s.smooth = False
        ch.series.append(s)
    escala(ch.x_axis, [70.0, 300.0])
    escala(ch.y_axis, filas_y)
    ch.legend.position = "b"
    ch.width, ch.height = 18.0, 8.0
    acabado(ch)
    ws.add_chart(ch, celda_grafico(ws.title, fila_enc, COL_GRAF))


def hoja_f4_regen_t(wb, datos):
    ws = wb.create_sheet("F4 Regenerador vs T_fuente")
    o = barrido_fuente()
    k = o[o["kalina"]].copy()
    k["_o"] = k["centro"].map({b: i for i, b in enumerate(BLOQUES)})
    k = k.sort_values(["_o", "T_fuente"])
    f = titulo(ws, 1, "F4 Regenerador y ciclo frente a T_fuente (70 a 300 °C)", ancho=10)
    f = condiciones(ws, f, [
        "Base: barridos de T_fuente de una variable (estudios 1 y 10, resto en el centro de cada bloque) y estudio 4 "
        "(T_fuente de 70 a 300 °C con P_alta, P_baja, x_b y T_sumidero en muestreo).",
        "Solo puntos KALINA (total). Regenerador en contraflujo: lado caliente 5 a 6, lado frio 10 a 1; UA = Q_reg / LMTD, por kg/s de m_b.",
        "Fuente: CSV de Sensibilidad 1 (x1_cargar)."])
    f = subtitulo(ws, f, "1. Rango de T_fuente con KALINA por bloque (barridos de una variable)")
    res = []
    for b in BLOQUES:
        a = o[o["centro"] == b]
        s = a[a["kalina"]]
        res.append([CORTO[b], len(a), len(s), num(s["t_c"].min(), 1), num(s["t_c"].max(), 1),
                    int((s["fuera_rango"]).sum())])
    _, f, _ = tabla(ws, f, ["Bloque", "Niveles probados", "Niveles KALINA", "T_fuente minima KALINA (°C)",
                            "T_fuente maxima KALINA (°C)", "KALINA fuera del rango experimental"], res,
                    anchos=[8, 14, 14, 20, 20, 22])
    f += 1
    f = subtitulo(ws, f, "2. Metricas del regenerador y del ciclo en cada nivel KALINA")
    filas, rangos, r = [], {}, f + 1
    for b in BLOQUES:
        s = k[k["centro"] == b]
        rangos[b] = (r, r + len(s) - 1)
        r += len(s)
        for _, x in s.iterrows():
            filas.append([CORTO[b], num(x["t_c"], 2), num(x["eta_pct"], 3), num(x["qreg_qi2"], 4),
                          num(x["pinch"], 3), num(x["ua"], 3), num(x["dh_turb"], 2), num(x["T_e3"], 2),
                          "no" if not x["fuera_rango"] else "si"])
    enc, ult, _ = tabla(ws, f, ["Bloque", "T_fuente (°C)", "eta (%)", "Q_reg/Q_i (-)", "Pinch regenerador (K)",
                                "UA regenerador (kW/K por kg/s)", "dh_turb (kJ/kg)", "T3 entrada de turbina (K)",
                                "Fuera del rango experimental"], filas,
                        anchos=[8, 12, 10, 12, 14, 18, 12, 10, 16])
    for i, (col_k, nom, col) in enumerate(COLS):
        _scatter(ws, enc + i * FILAS_GRAF, col, "%s frente a T_fuente (KALINA, una variable)" % nom, nom,
                 rangos, [x[col - 1] for x in filas])
    f = max(ult + 2, enc + 4 * FILAS_GRAF) + 1
    f = nota(ws, f, "Fuente: barridos de T_fuente de los estudios 1 y 10. Cada serie es un bloque; los niveles sin KALINA no "
                    "aparecen. Pinch y UA solo donde no hay cruce de temperaturas.") + 1
    f = subtitulo(ws, f, "3. Estudio 4: T_fuente de 70 a 300 °C con otras 4 variables en muestreo (mediana de los KALINA)")
    e = estudio4()
    e["_t"] = e["t_c"].round(0)
    gr = e.groupby("_t")
    tot = gr.size()
    kal = e[e["kalina"]].groupby("_t")
    tab = [[int(t), int(tot[t]), int(kal.size().get(t, 0)),
            num(100.0 * kal.size().get(t, 0) / tot[t], 1)] for t in tot.index]
    _, f, _ = tabla(ws, f, ["T_fuente (°C)", "Puntos", "KALINA", "% KALINA"], tab, anchos=[14, 10, 10, 10])
    f += 1
    f = bloque(ws, f, titulo="% de puntos KALINA frente a T_fuente (estudio 4)",
               encabezados=["T_fuente (°C)", "% KALINA"], filas=[[r[0], r[3]] for r in tab], x="T_fuente (°C)",
               y="% KALINA", tipo="linea", nota_txt="Fuente: estudio 4; 13 niveles de T_fuente.")
    ks = kal.agg(eta=("eta_pct", "median"), qr=("qreg_qi2", "median"), pin=("pinch", "median"),
                 ua=("ua", "median"), n=("eta_pct", "size"))
    for col, nom in (("eta", "eta mediana (%)"), ("qr", "Q_reg/Q_i mediana (-)"),
                     ("pin", "Pinch del regenerador mediana (K)"), ("ua", "UA del regenerador mediana (kW/K por kg/s)")):
        fl = [[int(t), num(x[col], 4)] for t, x in ks.iterrows() if x[col] == x[col]]
        f = bloque(ws, f, titulo="%s frente a T_fuente (KALINA, estudio 4)" % nom,
                   encabezados=["T_fuente (°C)", nom], filas=fl, x="T_fuente (°C)", y=nom, tipo="linea",
                   nota_txt="Fuente: estudio 4. Mediana de los KALINA de cada nivel (n entre 2 y 20 por nivel).")
    descripcion(ws, f, ["Como cambian el regenerador y el ciclo al subir la temperatura de la fuente de 70 a 300 °C.",
                        "El regenerador pierde peso al subir T_fuente: baja Q_reg/Q_i y UA, y sube el pinch."])
    return ws


HOJAS_F4C = [hoja_f4_regen_t]
