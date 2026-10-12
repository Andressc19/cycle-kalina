# -*- coding: utf-8 -*-
"""A2 · Gráficos nativos de Excel, parte A: síntesis (G), M02-N1, M02-N2, M02R, M02S y M03.

Escrito por Claude el 2026-10-11. Cada gráfico replica la figura de Matplotlib del mismo ID
(mismos datos, mismo bloque, mismo título); el pie se copia del .pie.md de esa figura.
"""
import pandas as pd
from openpyxl.styles import Font

from a2_graf_base import (COLOR, ORDEN, Lienzo, barras, disp_clases, lineas, pie_fig)
from a3_comun import SEC_VAR, cargar
from codigos import figura
from nombres import ETIQUETA_CLASE, NOMBRE
from pies import SIMBOLO

P = cargar()
S = lambda v: SIMBOLO.get(v, v)                       # noqa: E731
RES3 = "resultados/2026-10-06_final_M3/"
CASOS_G01 = ["1.1", "2.1", "2.2", "2.3", "2.4", "3.1", "3.2", "3.3", "4.1", "4.2", "4.3", "5.1",
             "6.1", "6.2"]                                 # estudios (nomenclatura 2026-10-12)


def _bloque_fig(lz, prefijo, graficos, por_fila=1, ancho=17.0, alto=8.5):
    tit, pie = pie_fig(prefijo)
    lz.bloque(f"Figura {figura(prefijo)} · {tit}", graficos, por_fila, ancho, alto, pie)


def graf_g(wb):
    lz = Lienzo(wb, "S")
    d = P[P["id_caso"] != "KF-M08"]
    series = []
    for c in ORDEN:
        vals = [int((d[d["estudio"].astype(str) == k]["clase_trazo"] == c).sum()) for k in CASOS_G01]
        series.append((f"{ETIQUETA_CLASE[c]} (n = {sum(vals)})", vals, COLOR[c]))
    tit, _ = pie_fig("FIG-G01")
    b = barras(lz, CASOS_G01, None, tit, "Estudio", "Número de puntos",
               horizontal=True, series=series)
    b.grouping, b.overlap = "stacked", 100
    b.x_axis.scaling.orientation = "maxMin"; b._lbl_alto = True   # M01 arriba, números abajo
    _bloque_fig(lz, "FIG-G01", [b], alto=11)
    lz.ws.cell(lz.fila, 1, "La Figura S-2 (qué se movió en cada barrido) está como tabla con colores "
                          "en la hoja «S-2 Qué se movió en cada barrido».").font = Font(italic=True, size=9)
    return lz.ws.title


def _tiras(lz, sub, col_valor, col_var, titulo_panel):
    gr = []
    for v in [v for v in SEC_VAR if v in set(sub[col_var].dropna())]:
        sv = sub[sub[col_var] == v]
        gr.append(disp_clases(lz, sv, col_valor, None, titulo_panel(v), xt=NOMBRE[v], tira=True))
    return gr


def graf_m02(wb):
    lz = Lienzo(wb, "2")
    b02 = P[P["bloque_director"] == "B02"]
    _bloque_fig(lz, "FIG-M02-01", _tiras(lz, b02, "valor", "variable", S),
                por_fila=3, ancho=10.5, alto=7)
    for pref, bl in (("FIG-M02-02a", "B03-A"), ("FIG-M02-02b", "B03-B")):
        sub = P[P["bloque_director"] == bl]
        var1 = sub["var1"].dropna().iloc[0]
        tit, _ = pie_fig(pref)
        g = disp_clases(lz, sub, "P_baja", "val1", tit, yt=NOMBRE[var1])
        _bloque_fig(lz, pref, [g])
    return lz.ws.title


def graf_m02r(wb):
    lz = Lienzo(wb, "2")
    n1 = P[P["bloque_director"] == "B04-n1"]
    _bloque_fig(lz, "FIG-M02R-n1", _tiras(lz, n1, "val1", "var1", S), por_fila=3, ancho=10.5, alto=7)
    for parte, pref in (("n2a", "FIG-M02R-n2a"), ("n2b", "FIG-M02R-n2b"), ("n3", "FIG-M02R-n3")):
        sub = P[P["bloque_director"] == f"B04-{parte}"]
        v1, v2 = sub["var1"].dropna().iloc[0], sub["var2"].dropna().iloc[0]
        tit, _ = pie_fig(pref)
        _bloque_fig(lz, pref, [disp_clases(lz, sub, "val2", "val1", tit, xt=NOMBRE[v2],
                                           yt=NOMBRE[v1])])
    return lz.ws.title


def graf_m02s(wb):
    lz = Lienzo(wb, "2")
    ts = [278.15, 283.15, 288.15, 293.15, 300.032917]
    bases = [("B05-B1", "2.4a · T_fuente = 403 K (A*)", "2E7D32"),
             ("B05-B2", "2.4b · T_fuente = 420 K", "1565C0"),
             ("B05-B3", "2.4c · ε_HRVG = 0.40 (fuente del profesor)", "EF8A17")]
    s1, s2 = [], []
    for bl, etq, col in bases:
        k = P[(P["bloque_director"] == bl) & (P["clasificacion"] == "KALINA")]
        pm = [k[(k["T_sumidero"] - t).abs() < 1e-3]["P_baja"].min() for t in ts]
        em = [k[(k["T_sumidero"] - t).abs() < 1e-3]["eta_pct"].max() for t in ts]
        s1.append((etq, ts, pm, col)); s2.append((etq, ts, em, col))
    g1 = lineas(lz, s1, "P_baja mínima de KALINA según el clima", NOMBRE["T_sumidero"],
                "P_baja mínima de KALINA [kPa]")
    g2 = lineas(lz, s2, "η máxima de KALINA según el clima", NOMBRE["T_sumidero"],
                "η máxima de KALINA [%]")
    _bloque_fig(lz, "FIG-M02S-01", [g1, g2], por_fila=2, ancho=15, alto=8.5)
    return lz.ws.title


def graf_m03(wb):
    lz = Lienzo(wb, "3")
    malla = P[(P["bloque_director"] == "B06") & (P["tipo_punto"] == "malla")]
    ok = malla[malla["genuino"] & malla["wnet_pos"]]
    dl = sorted(((v, ok[ok["variable"] == v]["eta_pct"].max() - ok[ok["variable"] == v]["eta_pct"].min())
                 for v in SEC_VAR if (ok["variable"] == v).any()), key=lambda t: t[1])
    tit, _ = pie_fig("FIG-M03-01")
    _bloque_fig(lz, "FIG-M03-01", [barras(lz, [S(v) for v, _ in dl], [x for _, x in dl], tit,
                                          "Variable", "Δη (máx − mín) [pp]", horizontal=True)])
    m3 = pd.read_csv(RES3 + "m3_resumen.csv").set_index("variable")
    e = m3["E_eta"].reindex(m3["E_eta"].abs().sort_values().index)
    tit, _ = pie_fig("FIG-M03-02")
    _bloque_fig(lz, "FIG-M03-02", [barras(lz, [S(v) for v in e.index], e.tolist(), tit, "Variable",
                                          "Elasticidad de η, E [–]", horizontal=True,
                                          colores=["2E7D32" if x > 0 else "C62828" for x in e])])
    gr = []
    for v in SEC_VAR:                         # sin η (no genuino o W_net ≤ 0): ✕ en η = −0.6
        sv = malla[malla["variable"] == v].copy()
        sv.loc[~(sv["genuino"] & sv["wnet_pos"]), "eta_pct"] = -0.6
        if len(sv):
            gr.append(disp_clases(lz, sv, "valor", "eta_pct", S(v), xt=NOMBRE[v],
                                  yt="η [%] (−0.6 = sin η)"))
    _bloque_fig(lz, "FIG-M03-03", gr, por_fila=3, ancho=10.5, alto=7)
    cr = pd.read_csv(RES3 + "m3_cruces.csv")
    cr = cr[cr["tipo"] == "margen"]
    dist = sorted(((r["variable"], abs(r["v_cruce"] - m3.loc[r["variable"], "valor_ancla"])
                    / (m3.loc[r["variable"], "b"] - m3.loc[r["variable"], "a"]))
                   for _, r in cr.iterrows()), key=lambda t: -t[1])
    tit, _ = pie_fig("FIG-M03-04")
    _bloque_fig(lz, "FIG-M03-04", [barras(lz, [S(v) for v, _ in dist], [x for _, x in dist], tit,
                                          "Variable", "Distancia a la frontera / rango [–]",
                                          horizontal=True,
                                          colores=["C62828" if x < 0.06 else "2E7D32"
                                                   for _, x in dist])])
    lz.ws.cell(lz.fila - 2, 1, "Rojo: frontera a menos del 6 % del rango.").font = \
        Font(italic=True, size=9)
    return lz.ws.title
