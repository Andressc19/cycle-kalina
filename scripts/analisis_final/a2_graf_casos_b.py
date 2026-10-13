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
from codigos import figura
from a3_comun import SEC_VAR
from a2_graf_base import pie_fig
from a3_m05 import ejes
from nombres import NOMBRE, grupo_legible

M4B = "resultados/2026-10-07_final_M4b/"
ARR = {"A1": ("5.1a · libre (desde el mejor de 3.2)", "1565C0"),
       "A2": ("5.1b · libre (desde el mejor de 2.4)", "EF8A17"),
       "A3": ("5.1c · conserva sus temperaturas", "2E7D32"),
       "A4": ("5.1d · conserva sus presiones y su clima", "C62828"),
       "A5": ("5.1e · conserva su fuente y su x_b (fuera de rango)", "7E57C2")}


def graf_m04(wb):
    lz = Lienzo(wb, "3")
    b07 = P[P["bloque_director"] == "B07"]
    gen = b07[b07["genuino"]]
    kal, resto = gen[gen["clasificacion"] == "KALINA"], gen[gen["clasificacion"] != "KALINA"]
    nogen = b07[~b07["genuino"] & ~b07["omitido"]]     # los de la tabla que no tienen resultado
    gr = []
    for v in SEC_VAR:                                          # FIG-M04-01: CDF por variable
        xk, xr = np.sort(kal[v].dropna()), np.sort(resto[v].dropna())
        xn = np.sort(nogen[v].dropna())
        nom_r, nom_n = f"resto genuino (n = {len(xr)})", f"sin resultado (n = {len(xn)})"
        gr.append(lineas(lz, [(f"KALINA (n = {len(xk)})", xk, np.arange(1, len(xk) + 1) / len(xk),
                               "2E7D32"),
                              (nom_r, xr, np.arange(1, len(xr) + 1) / len(xr), "9E9E9E"),
                              (nom_n, xn, np.arange(1, len(xn) + 1) / len(xn), "C62828")],
                         S(v), NOMBRE[v], "F(x)", punteadas=(nom_r, nom_n), marcador=False))
    tit, pie = pie_fig("FIG-M04-01")                           # 2026-10-12: se agregan los no genuinos
    nt = len(kal) + len(resto) + len(nogen)
    tit = tit.replace("LHS de 452 puntos", f"LHS de {nt} puntos")
    pie = [l.replace("(LHS de 452 puntos)", f"(LHS de {nt} puntos)")
            .replace("n = 452.", f"n = {nt} ({len(kal) + len(resto)} genuinos y {len(nogen)} sin resultado: "
                                 "no convergió o falso convergido).") for l in pie]
    lz.bloque(f"Figura {figura('FIG-M04-01')} · {tit}", gr, 3, 10.5, 7, pie, fig=figura("FIG-M04-01"))
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
        hn, _ = np.histogram(nogen[col].dropna(), bordes)
        cats = [f"{a:.0f}–{b:.0f}" if col == "dP" else f"{a:.1f}–{b:.1f}"
                for a, b in zip(bordes[:-1], bordes[1:])]
        gr.append(barras(lz, cats, None, NOMBRE[col], NOMBRE[col], "Número de puntos",
                         series=[(f"KALINA (n = {len(kal)})", hk.tolist(), "2E7D32"),
                                 (f"resto (n = {len(resto)})", hr.tolist(), "BDBDBD"),
                                 (f"sin resultado (n = {len(nogen)})", hn.tolist(), "C62828")]))
    tit, pie = pie_fig("FIG-M04-04")
    pie = [l.replace("n = 452.", f"n = {nt} ({len(kal) + len(resto)} genuinos y {len(nogen)} sin resultado).")
           for l in pie]
    lz.bloque(f"Figura {figura('FIG-M04-04')} · {tit}", gr, 2, 15, 8, pie, fig=figura("FIG-M04-04"))
    return lz.ws.title


def graf_m04c(wb):
    lz = Lienzo(wb, "3")
    sub = P[(P["bloque_director"] == "B08") & ~P["omitido"]]
    kal = sub["clasificacion"] == "KALINA"
    n1, n2 = int((kal & ~sub["fuera_rango"]).sum()), int((kal & sub["fuera_rango"]).sum())
    fr = sub.assign(k=np.digitize(sub["P_baja"], np.arange(1500, 2600, 100)) - 1).groupby("k")
    cats = [f"{1500 + 100 * i:.0f}–{1600 + 100 * i:.0f}" for i, _ in fr]
    pct = [100 * (x["clasificacion"] == "KALINA").mean() for _, x in fr]
    conf = [100 * ((x["clasificacion"] == "KALINA") & ~x["fuera_rango"]).sum() / len(x) for _, x in fr]
    tit, _ = pie_fig("FIG-M04c-01")
    b = barras(lz, cats, None, tit, "Franja de P_baja [kPa]", "% de puntos KALINA",
               series=[(f"KALINA dentro del rango (n = {n1})", conf, "2E7D32"),
                       (f"KALINA fuera de rango (n = {n2})",
                        [p - c for p, c in zip(pct, conf)], "A5D6A7")])
    b.grouping, b.overlap = "stacked", 100
    _bloque_fig(lz, "FIG-M04c-01", [b])
    return lz.ws.title


def graf_m05(wb):
    lz = Lienzo(wb, "4")
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
    lz = Lienzo(wb, "6")                                   # 6.1: motor de referencia
    a = pd.read_csv("resultados/2026-10-08_final_M6/m6_comparacion.csv").assign(f="6.1a · motor real con 300 s")
    b = pd.read_csv("resultados/2026-10-08_final_M9/m9_motor_real.csv").assign(f="6.1d · motor real con 1500 s")
    par = pd.concat([a, b]).dropna(subset=["eta_teqp", "eta_real"])
    xs = [0, 17]
    ser = [("1:1", xs, xs, "424242"), ("+0.7 pp", xs, [v + 0.7 for v in xs], "A5D6A7"),
           ("−0.7 pp", xs, [v - 0.7 for v in xs], "A5D6A7")]
    for f, col in (("6.1a · motor real con 300 s", "1565C0"), ("6.1d · motor real con 1500 s", "2E7D32")):
        g = par[par["f"] == f]
        ser.append((f"{f} (n = {len(g)})", (100 * g["eta_teqp"]).tolist(), (100 * g["eta_real"]).tolist(), col))
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
    lz = Lienzo(wb, "5")                                   # 5.1: búsqueda de la η máxima
    t = pd.read_csv("resultados/2026-10-07_final_M7/m7_trayectorias.csv")
    t = t[t["aceptado"].astype(str).str.lower().isin(["true", "1"])]
    gs = {k: g.sort_values("iteracion") for k, g in t.groupby("arranque")}
    paso = {k: (f" · último paso {100 * (g['eta'].iloc[-1] - g['eta'].iloc[-2]):+.2f} pp"
                if len(g) > 1 else " · sin pasos previos") for k, g in gs.items()}
    ser = [(f"{ARR[k][0]}: {100 * g['eta'].max():.1f} %{paso[k]}", g["iteracion"].tolist(),
            (100 * g["eta"]).tolist(), ARR[k][1]) for k, g in gs.items()]
    tit, pie = pie_fig("FIG-M07-01")
    g7 = lineas(lz, ser, tit, "Iteración de la búsqueda", "Eficiencia térmica del ciclo, η [%]",
                punteadas=(ser[-1][0],))
    ev = pd.read_csv("resultados/2026-10-07_final_M7/m7_evaluaciones.csv")   # 2026-10-12: las 560
    ev = ev[~ev["aceptado"].astype(str).str.lower().isin(["true", "1"]) & ev["eta"].notna()]
    nom = f"evaluados y no aceptados (n = {len(ev)})"
    gris = lineas(lz, [(nom, ev["iteracion"].tolist(), (100 * ev["eta"]).tolist(), "BDBDBD")], "", "", "")
    s = gris.series[0]; s.graphicalProperties.line = LineProperties(noFill=True); s.marker.size = 4
    g7.series.insert(0, s)                                   # debajo de las trayectorias
    for i, s_ in enumerate(g7.series):
        s_.idx = s_.order = i
    pie = [l.replace("n = 41 pasos aceptados.", f"n = {41 + len(ev)} evaluaciones (41 pasos aceptados y "
                                                f"{len(ev)} no aceptados; las 10 evaluaciones sin η no se dibujan).") for l in pie]
    lz.bloque(f"Figura {figura('FIG-M07-01')} · {tit}", [g7], 1, 17.0, 9.5, pie, fig=figura("FIG-M07-01"))
    lz = Lienzo(wb, "4")                                   # 4.3: escalera de conservación
    m9 = pd.read_csv("resultados/2026-10-08_final_M9/m9_escalera.csv")
    cats = [f"R{r} · {grupo_legible(c)}" for r, c in zip(m9["ronda"], m9["conservados"])]
    tit, _ = pie_fig("FIG-M09-01")
    _bloque_fig(lz, "FIG-M09-01", [barras(lz, cats, m9["n_kalina_confiable"].tolist(), tit,
                                          "Conjunto conservado (R = ronda)", "KALINA confiables",
                                          colores=["1B5E20" if e else "81C784" for e in m9["elegido"]])], alto=9.5)
    lz.ws.cell(lz.fila - 2, 1, "Verde oscuro: conjunto elegido en cada ronda.")
    return lz.ws.title


def graf_m10(wb):
    lz = Lienzo(wb, "6")
    sub = P[P["bloque_director"] == "B14-MALLA"]
    tit, _ = pie_fig("FIG-M10-01")
    g = disp_clases(lz, sub, "x_b", "P_baja", tit)
    k = sub[sub["clasificacion"] == "KALINA"]
    pmin = k.groupby(k["x_b"].round(3))["P_baja"].min()
    g.series.append(lineas(lz, [("P_baja mínima KALINA", pmin.index.tolist(), pmin.tolist(), "000000")], "", "", "", punteadas=("P_baja mínima KALINA",), marcador=False).series[0])
    _bloque_fig(lz, "FIG-M10-01", [g], alto=10)
    of = P[P["bloque_director"] == "B14-OFAT"]
    gr = []
    for v in SEC_VAR:
        sv = of[of["variable"] == v].copy()
        sv.loc[~(sv["genuino"] & sv["wnet_pos"]), "eta_pct"] = 0.0
        if len(sv): gr.append(disp_clases(lz, sv, v, "eta_pct", S(v), yt="η [%] (0 = sin η)"))
    _bloque_fig(lz, "FIG-M10-02", gr, por_fila=3, ancho=10.5, alto=7)
    ob = P[P["bloque_director"] == "B14-OFATb"].copy()
    ob.loc[~(ob["genuino"] & ob["wnet_pos"]), "eta_pct"] = 0.0
    lz.bloque("KF-M10b-OFAT · η según x_b con P_baja = 690 kPa (ancla de Húsavík; 0 = sin η)",
              [disp_clases(lz, ob, "x_b", "eta_pct", "Húsavík con poco amoníaco: η según x_b",
                           yt="η [%] (0 = sin η)")],
              pie=["Caso: KF-M10b-OFAT (bloque B14-OFATb). Datos fijos: ancla de Húsavík con "
                   "P_baja = 690 kPa. Datos barridos: x_b 0.30–0.70 (17 valores). Por debajo de "
                   "x_b = 0.50 no hay ningún punto genuino. Fuente: todos_los_puntos.csv."],
              fig="6.2d")
    return lz.ws.title


def construir_graficos(wb):
    """Crea las hojas de gráficos (una por pregunta) y devuelve [(hoja, estudio(s), qué muestra)]."""
    from a2_graf_casos_a import graf_g, graf_m02, graf_m02r, graf_m02s, graf_m03
    for f in (graf_g, graf_m02, graf_m02r, graf_m02s, graf_m03, graf_m04, graf_m04c, graf_m05, graf_m06_m07_m09, graf_m10):
        f(wb)
    que = {"S": "síntesis", "2": "2.1–2.4", "3": "3.1–3.3", "4": "4.1–4.3", "5": "5.1", "6": "6.1–6.2"}
    return [(f"{k} Gráficos", v, "gráficos nativos de Excel de cada figura") for k, v in que.items()]
