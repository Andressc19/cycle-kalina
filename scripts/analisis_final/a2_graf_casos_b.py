# -*- coding: utf-8 -*-
"""A2 · Gráficos nativos de Excel, parte B: M04, M04c, M05, M05c, M06, M07, M09, M10 y M10b.

Escrito por Claude el 2026-10-11. Mismo criterio que la parte A: cada gráfico replica la figura
de Matplotlib del mismo ID y lleva su pie.
"""
import numpy as np
from openpyxl.drawing.line import LineProperties
import pandas as pd

from a2_graf_base import Lienzo, barras, disp_clases, lineas
from a2_graf_casos_a import P, S, _bloque_fig
from a3_comun import SEC_VAR
from a2_graf_base import pie_fig
from a3_m05 import ejes
from nombres import NOMBRE, grupo_legible

M4B = "resultados/2026-10-07_final_M4b/"
ARR = {"A1": ("A1 · libre (desde el mejor de M4b)", "1565C0"),
       "A2": ("A2 · libre (desde el mejor de M2S)", "EF8A17"),
       "A3": ("A3 · conserva sus temperaturas", "2E7D32"),
       "A4": ("A4 · conserva sus presiones y su clima", "C62828"),
       "A5": ("A5 · conserva su fuente y su x_b (fuera de rango)", "7E57C2")}


def graf_m04(wb):
    lz = Lienzo(wb, "M04_graficos", "KF-M04 + KF-M04b · sensibilidad global (bloque B07, 500 puntos)")
    b07 = P[P["bloque_director"] == "B07"]
    gen = b07[b07["genuino"]]
    kal, resto = gen[gen["clasificacion"] == "KALINA"], gen[gen["clasificacion"] != "KALINA"]
    gr = []
    for v in SEC_VAR:                                          # FIG-M04-01: CDF por variable
        xk, xr = np.sort(kal[v].dropna()), np.sort(resto[v].dropna())
        gr.append(lineas(lz, [(f"KALINA (n = {len(xk)})", xk, np.arange(1, len(xk) + 1) / len(xk),
                               "2E7D32"),
                              (f"resto genuino (n = {len(xr)})", xr,
                               np.arange(1, len(xr) + 1) / len(xr), "9E9E9E")],
                         S(v), NOMBRE[v], "F(x)", punteadas=(f"resto genuino (n = {len(xr)})",),
                         marcador=False))
    _bloque_fig(lz, "FIG-M04-01", gr, por_fila=3, ancho=10.5, alto=7)
    rp5, rp95 = np.percentile(kal["rP"], [5, 95])
    tit, _ = pie_fig("FIG-M04-02")
    g = disp_clases(lz, b07, "P_alta", "P_baja", tit)
    pa = [b07["P_alta"].min(), b07["P_alta"].max()]
    for rp in (rp5, rp95):
        extra = lineas(lz, [(f"r_P = {rp:.2f}", pa, [x / rp for x in pa], "000000")], "", "", "",
                       punteadas=(f"r_P = {rp:.2f}",), marcador=False)
        g.series.append(extra.series[0])
    _bloque_fig(lz, "FIG-M04-02", [g], alto=10)
    pr = pd.read_csv(M4B + "m4b_prcc.csv")
    pr = pr[pr["salida"] == "eta"].assign(a=lambda t: t["prcc"].abs()).sort_values("a")
    tit, _ = pie_fig("FIG-M04-03")
    _bloque_fig(lz, "FIG-M04-03", [barras(lz, [S(v) for v in pr["variable"]], pr["prcc"].tolist(),
                                          tit, "Variable", "PRCC sobre η [–]", horizontal=True,
                                          colores=["2E7D32" if x > 0 else "C62828"
                                                   for x in pr["prcc"]])])
    gr = []
    for col in ("dP", "rP"):                                   # FIG-M04-04: histogramas
        bordes = np.histogram_bin_edges(gen[col], bins=20)
        hk, _ = np.histogram(kal[col], bordes); hr, _ = np.histogram(resto[col], bordes)
        cats = [f"{a:.0f}–{b:.0f}" if col == "dP" else f"{a:.1f}–{b:.1f}"
                for a, b in zip(bordes[:-1], bordes[1:])]
        gr.append(barras(lz, cats, None, NOMBRE[col], NOMBRE[col], "Número de puntos",
                         series=[(f"KALINA (n = {len(kal)})", hk.tolist(), "2E7D32"),
                                 (f"resto (n = {len(resto)})", hr.tolist(), "BDBDBD")]))
    _bloque_fig(lz, "FIG-M04-04", gr, por_fila=2, ancho=15, alto=8)
    return lz.ws.title


def graf_m04c(wb):
    lz = Lienzo(wb, "M04c_graficos", "KF-M04c · techo de P_baja (bloque B08)")
    sub = P[(P["bloque_director"] == "B08") & ~P["omitido"]]
    bordes = np.arange(1500, 2600, 100)
    k = np.digitize(sub["P_baja"], bordes) - 1
    cats, pct = [], []
    for i, lo in enumerate(bordes[:-1]):
        g = sub[k == i]
        if len(g):
            cats.append(f"{lo:.0f}–{lo + 100:.0f}"); pct.append(100 * (g["clasificacion"] == "KALINA").mean())
    tit, _ = pie_fig("FIG-M04c-01")
    _bloque_fig(lz, "FIG-M04c-01", [barras(lz, cats, pct, tit, "Franja de P_baja [kPa]",
                                           "% de puntos KALINA")])
    return lz.ws.title


def graf_m05(wb):
    lz = Lienzo(wb, "M05_graficos", "KF-M05 y KF-M05c · conservación de datos del profesor")
    for k in "12345":
        sub = P[P["id_subcaso"] == f"KF-M05-{k}"]
        x, y = ejes(f"KF-M05-{k}")
        tit, _ = pie_fig(f"FIG-M05-S{k}")
        _bloque_fig(lz, f"FIG-M05-S{k}", [disp_clases(lz, sub, x, y, tit)], alto=9.5)
    b10 = P[P["bloque_director"] == "B10"]
    gr = []
    for t in sorted(b10["T_sumidero"].round(3).unique()):
        g = b10[(b10["T_sumidero"] - t).abs() < 1e-3]
        gr.append(disp_clases(lz, g, "T_fuente", "eps_cond", f"T_sumidero = piso de O2 = {t:.2f} K"))
    _bloque_fig(lz, "FIG-M05c-01", gr, por_fila=3, ancho=10.5, alto=8)
    return lz.ws.title


def graf_m06_m07_m09(wb):
    lz = Lienzo(wb, "M06_M07_M09_graficos", "KF-M06 (motor real), KF-M07 (máxima η) y KF-M09 "
                                            "(escalera de conservación)")
    a = pd.read_csv("resultados/2026-10-08_final_M6/m6_comparacion.csv").assign(f="M6 (300 s)")
    b = pd.read_csv("resultados/2026-10-08_final_M9/m9_motor_real.csv").assign(f="M9 (1500 s)")
    par = pd.concat([a, b]).dropna(subset=["eta_teqp", "eta_real"])
    xs = [0, 17]
    ser = [("1:1", xs, xs, "424242"), ("+0.7 pp", xs, [v + 0.7 for v in xs], "A5D6A7"),
           ("−0.7 pp", xs, [v - 0.7 for v in xs], "A5D6A7")]
    for f, col in (("M6 (300 s)", "1565C0"), ("M9 (1500 s)", "2E7D32")):
        g = par[par["f"] == f]
        ser.append((f"{f} (n = {len(g)})", (100 * g["eta_teqp"]).tolist(),
                    (100 * g["eta_real"]).tolist(), col))
    tit, _ = pie_fig("FIG-M06-01")
    g6 = lineas(lz, ser, tit, "η con teqp [%]", "η con el motor real [%]",
                punteadas=("+0.7 pp", "−0.7 pp"))
    for s in g6.series[3:]:
        s.graphicalProperties.line = LineProperties(noFill=True); s.marker.size = 8   # solo marcador
    for s in g6.series[:3]:
        s.marker.symbol = "none"
    for eje in (g6.x_axis, g6.y_axis):          # mismo rango que la figura de Matplotlib
        eje.scaling.min, eje.scaling.max, eje.majorUnit = 0, 17, 2
    _bloque_fig(lz, "FIG-M06-01", [g6], alto=10)
    t = pd.read_csv("resultados/2026-10-07_final_M7/m7_trayectorias.csv")
    t = t[t["aceptado"].astype(str).str.lower().isin(["true", "1"])]
    ser = [(f"{ARR[k][0]}: {100 * g['eta'].max():.1f} %", g.sort_values("iteracion")["iteracion"].tolist(),
            (100 * g.sort_values("iteracion")["eta"]).tolist(), ARR[k][1]) for k, g in t.groupby("arranque")]
    tit, _ = pie_fig("FIG-M07-01")
    _bloque_fig(lz, "FIG-M07-01", [lineas(lz, ser, tit, "Iteración de la búsqueda",
                                          "Eficiencia térmica del ciclo, η [%]",
                                          punteadas=(ser[-1][0],))], alto=9.5)
    m9 = pd.read_csv("resultados/2026-10-08_final_M9/m9_escalera.csv")
    cats = [f"R{r} · {grupo_legible(c)}" for r, c in zip(m9["ronda"], m9["conservados"])]
    tit, _ = pie_fig("FIG-M09-01")
    _bloque_fig(lz, "FIG-M09-01", [barras(lz, cats, m9["n_kalina_confiable"].tolist(), tit,
                                          "Conjunto conservado (R = ronda)", "KALINA confiables",
                                          colores=["1B5E20" if e else "81C784" for e in m9["elegido"]])],
                alto=9.5)
    lz.ws.cell(lz.fila - 2, 1, "Verde oscuro: conjunto elegido en cada ronda.")
    return lz.ws.title


def graf_m10(wb):
    lz = Lienzo(wb, "M10_graficos", "KF-M10 y KF-M10b · Húsavík (bloques B14)")
    sub = P[P["bloque_director"] == "B14-MALLA"]
    tit, _ = pie_fig("FIG-M10-01")
    g = disp_clases(lz, sub, "x_b", "P_baja", tit)
    k = sub[sub["clasificacion"] == "KALINA"]
    pmin = k.groupby(k["x_b"].round(3))["P_baja"].min()
    g.series.append(lineas(lz, [("P_baja mínima KALINA", pmin.index.tolist(), pmin.tolist(), "000000")],
                           "", "", "", punteadas=("P_baja mínima KALINA",), marcador=False).series[0])
    _bloque_fig(lz, "FIG-M10-01", [g], alto=10)
    of = P[P["bloque_director"] == "B14-OFAT"]
    gr = []
    for v in SEC_VAR:
        sv = of[of["variable"] == v].copy()
        sv.loc[~(sv["genuino"] & sv["wnet_pos"]), "eta_pct"] = 0.0
        if len(sv):
            gr.append(disp_clases(lz, sv, v, "eta_pct", S(v), yt="η [%] (0 = sin η)"))
    _bloque_fig(lz, "FIG-M10-02", gr, por_fila=3, ancho=10.5, alto=7)
    ob = P[P["bloque_director"] == "B14-OFATb"].copy()
    ob.loc[~(ob["genuino"] & ob["wnet_pos"]), "eta_pct"] = 0.0
    lz.bloque("KF-M10b-OFAT · η según x_b con P_baja = 690 kPa (ancla de Húsavík; 0 = sin η)",
              [disp_clases(lz, ob, "x_b", "eta_pct", "Húsavík con poco amoníaco: η según x_b",
                           yt="η [%] (0 = sin η)")],
              pie=["Caso: KF-M10b-OFAT (bloque B14-OFATb). Datos fijos: ancla de Húsavík con "
                   "P_baja = 690 kPa. Datos barridos: x_b 0.30–0.70 (17 valores). Por debajo de "
                   "x_b = 0.50 no hay ningún punto genuino. Fuente: todos_los_puntos.csv."])
    return lz.ws.title


def construir_graficos(wb):
    """Crea todas las hojas de gráficos y devuelve [(hoja, caso, qué muestra)]."""
    from a2_graf_casos_a import graf_g, graf_m02, graf_m02r, graf_m02s, graf_m03
    hojas = [(graf_g, "síntesis", "FIG-G01"), (graf_m02, "KF-M02-N1, KF-M02-N2", "FIG-M02-01, -02a, -02b"),
             (graf_m02r, "KF-M02R", "FIG-M02R-n1 … n3"), (graf_m02s, "KF-M02S", "FIG-M02S-01"),
             (graf_m03, "KF-M03", "FIG-M03-01 … -04"), (graf_m04, "KF-M04 + KF-M04b", "FIG-M04-01 … -04"),
             (graf_m04c, "KF-M04c", "FIG-M04c-01"), (graf_m05, "KF-M05, KF-M05c", "FIG-M05-S1 … S5, FIG-M05c-01"),
             (graf_m06_m07_m09, "KF-M06, KF-M07, KF-M09", "FIG-M06-01, FIG-M07-01, FIG-M09-01"),
             (graf_m10, "KF-M10, KF-M10b", "FIG-M10-01, -02 y M10b-OFAT")]
    return [(f(wb), caso, f"Gráficos nativos de Excel: {que}") for f, caso, que in hojas]
