# -*- coding: utf-8 -*-
"""A3 · Figuras M03: tornado, elasticidades, paneles OAT y márgenes de A*.

Datos: B06 (malla) + resultados/2026-10-06_final_M3/m3_resumen.csv y
m3_cruces.csv (producidos y validados por la fase A4 de M3).
"""
import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from estilo import aplicar_estilo, COLOR_CLASE, recuadro_condiciones
from a3_comun import recuadro_fig, leyenda_fig
from a3_comun import (SEC_VAR, cargar, dispersion, sin_eta_sobre_eje, titulo,
                      titulo_fig, recuadro_oat, guardar_fig, guardar_clases,
                      contar_clases)
from nombres import NOMBRE
from pies import armar_pie

aplicar_estilo()

PUNTOS = cargar()
M3 = pd.read_csv("resultados/2026-10-06_final_M3/m3_resumen.csv")
M3 = M3.set_index("variable")
CRUCES = pd.read_csv("resultados/2026-10-06_final_M3/m3_cruces.csv")
FUENTE = "todos_los_puntos.csv y resultados/2026-10-06_final_M3/"
AST_BASE = ("A* = punto del profesor con T_fuente = 403 K y P_baja = 563.64 kPa "
            "(KALINA, η = 8.48 %)")
ANCLA = PUNTOS[(PUNTOS["bloque_director"] == "B06")
               & (PUNTOS["tipo_punto"] == "ancla")]["eta_pct"].iloc[0]
MALLA = PUNTOS[(PUNTOS["bloque_director"] == "B06")
               & (PUNTOS["tipo_punto"] == "malla")].copy()


def _etiqueta_var(v):
    return {"T_fuente": "T_fuente", "T_sumidero": "T_sumidero", "P_alta": "P_alta",
            "P_baja": "P_baja", "x_b": "x_b", "eta_t": "η_t", "eta_p": "η_p",
            "eps_hrvg": "ε_HRVG", "eps_reg": "ε_reg", "eps_cond": "ε_cond"}[v]


# ---------------------------------------------------------------- FIG-M03-01
def fig_m03_01():
    valid = MALLA[MALLA["genuino"] & MALLA["wnet_pos"]]
    deltas = []
    for v in SEC_VAR:
        sv = valid[valid["variable"] == v]
        if len(sv):
            deltas.append((v, sv["eta_pct"].max() - sv["eta_pct"].min()))
    deltas.sort(key=lambda t: t[1], reverse=True)
    v1, v2 = deltas[0][0], deltas[1][0]
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    ax.barh(range(len(deltas)), [d for _, d in deltas], color="#2E7D32",
            alpha=0.9)
    ax.set_yticks(range(len(deltas)))
    ax.set_yticklabels([_etiqueta_var(v) for v, _ in deltas])
    ax.set_xlabel("Δη (máx − mín) [pp]")
    titulo(ax, f"Cerca de A*, {v1} y {v2} son las que más mueven η en su rango",
           "Bloque B06 · KF-M03 (malla, genuino y W_net > 0)")
    recuadro_oat(ax, ["KF-M03"])
    pie = armar_pie("FIG-M03-01",
                    f"Cerca de A*, {v1} y {v2} son las que más mueven η en su rango",
                    ["KF-M03"], "B06",
                    "B06 (KF-M03), malla, puntos genuinos con W_net > 0",
                    n=len(valid), fuente="todos_los_puntos.csv", base=AST_BASE)
    guardar_fig(fig, "M03", "FIG-M03-01_tornado_delta_eta", pie)
    print("FIG-M03-01: deltas =",
          {v: round(d, 2) for v, d in deltas})


# ---------------------------------------------------------------- FIG-M03-02
def fig_m03_02():
    e = M3.reset_index().copy()
    e["absE"] = e["E_eta"].abs()
    e = e.sort_values("absE", ascending=False)
    v1, e1 = e.iloc[0]["variable"], e.iloc[0]["E_eta"]
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    colores = ["#2E7D32" if x > 0 else "#C62828" for x in e["E_eta"]]
    ax.barh(range(len(e)), e["E_eta"], color=colores, alpha=0.9)
    ax.axvline(0, color="0.35", lw=0.8)
    ax.set_yticks(range(len(e)))
    ax.set_yticklabels([_etiqueta_var(v) for v in e["variable"]])
    ax.set_xlabel("Elasticidad de η, E [–]")
    titulo(ax, f"Pegado a A*, {v1} es la variable más sensible (E = {e1:.1f})",
           "Bloque B06 · KF-M03 (malla, E de la elasticidad)")
    pie = armar_pie("FIG-M03-02",
                    f"Pegado a A*, {v1} es la variable más sensible (E = {e1:.1f})",
                    ["KF-M03"], "B06", "m3_resumen.csv (E_eta de la malla)",
                    n=len(e), fuente="resultados/2026-10-06_final_M3/"
                                     "m3_resumen.csv",
                    base=AST_BASE)
    guardar_fig(fig, "M03", "FIG-M03-02_elasticidades", pie)
    print(f"FIG-M03-02: E máx |E| = {e1:.3f} ({v1})")


# ---------------------------------------------------------------- FIG-M03-03
def fig_m03_03():
    fig, axs = plt.subplots(2, 5, figsize=(13, 7.2), sharey=True)
    for ax, v in zip(axs.flat, SEC_VAR):
        sv = MALLA[MALLA["variable"] == v]
        disp = sv[sv["genuino"] & sv["wnet_pos"]]
        val_ancla = M3.loc[v, "valor_ancla"]
        dispersion(ax, disp, "valor", "eta_pct", s=12)
        ymin = -0.6   # misma altura en todos los paneles (eje y compartido): ✕ = sin η
        sin_eta_sobre_eje(ax, sv, "valor", ymin, s=12)
        ax.axvline(val_ancla, color="0.3", ls="--", lw=0.8, zorder=1)
        ax.axhline(ANCLA, color="0.55", ls=":", lw=0.8, zorder=1)
        ax.axhspan(ANCLA - 0.7, ANCLA + 0.7, color="#2E7D32", alpha=0.10,
                   zorder=0)
        ax.set_title(_etiqueta_var(v), fontsize=8)
        ax.set_xlabel(NOMBRE[v], fontsize=6)
        if ax.get_subplotspec().is_first_col():
            ax.set_ylabel("η [%]")
    leyenda_fig(fig, MALLA)
    recuadro_fig(fig, ["KF-M03"])
    titulo_fig(fig, "Eficiencia según cada variable, una a la vez, alrededor de A*",
               "Bloque B06 · KF-M03 (malla; línea punteada: valor en A*)")
    pie = armar_pie("FIG-M03-03",
                    "Eficiencia según cada variable, una a la vez, alrededor de A*",
                    ["KF-M03"], "B06", "B06 (KF-M03), malla", n=len(MALLA),
                    fuente="todos_los_puntos.csv", base=AST_BASE)
    guardar_fig(fig, "M03", "FIG-M03-03_oat_alrededor_de_A", pie)
    guardar_clases("M03", "FIG-M03-03_oat_alrededor_de_A",
                   contar_clases(MALLA))
    print("FIG-M03-03: 10 paneles de la malla (η de genuinos con W_net > 0)")


# ---------------------------------------------------------------- FIG-M03-04
def fig_m03_04():
    mc = CRUCES[CRUCES["tipo"] == "margen"].copy()
    filas = []
    for _, r in mc.iterrows():
        v = r["variable"]
        dist = abs(r["v_cruce"] - M3.loc[v, "valor_ancla"]) / (M3.loc[v, "b"]
                                                                - M3.loc[v, "a"])
        filas.append((v, dist, r["criterio"]))
    filas.sort(key=lambda t: t[1])
    k = sum(1 for _, d, _ in filas if d < 0.06)
    m = len(filas)
    col_crit = {"m_O2": "#2E7D32", "m_O1": "#1565C0", "m_O3": "#EF8A17"}
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    for i, (v, d, crit) in enumerate(filas):
        ax.scatter(d, i, s=60, color=col_crit.get(crit, "#333333"), zorder=3)
    ax.axvline(0.06, color="0.3", ls="--", lw=1.0)
    ax.set_yticks(range(m))
    ax.set_yticklabels([_etiqueta_var(v) for v, _, _ in filas])
    ax.set_xlabel("distancia = |v_cruce − valor_ancla| / (b − a) [–]")
    ax.set_xlim(0, max(0.35, max(d for _, d, _ in filas) * 1.1))
    titulo(ax,
           f"A* está a menos del 6 % del rango de la frontera de O2 en {k} de {m} variables",
           "Bloque B06 · KF-M03 (cruces de margen de O2)")
    ax.legend([plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=
                          col_crit["m_O2"], markersize=8)],
              ["frontera de O2 (m_O2)"], loc="lower right", fontsize=8)
    recuadro_condiciones(ax, "Punto base: A* (η = 8.48 %)\n"
                             "Línea punteada: 6 % del rango")
    pie = armar_pie("FIG-M03-04",
                    f"A* está a menos del 6 % del rango de la frontera de O2 en "
                    f"{k} de {m} variables",
                    ["KF-M03"], "B06", "m3_cruces.csv (tipo = margen)", n=m,
                    fuente="resultados/2026-10-06_final_M3/m3_cruces.csv",
                    base=AST_BASE)
    guardar_fig(fig, "M03", "FIG-M03-04_margenes_frontera_O2", pie)
    print(f"FIG-M03-04: {k} de {m} variables a menos del 6 % del rango")


if __name__ == "__main__":
    fig_m03_01()
    fig_m03_02()
    fig_m03_03()
    fig_m03_04()
    print("a3_m03: OK")