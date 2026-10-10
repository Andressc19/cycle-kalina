# -*- coding: utf-8 -*-
"""A3 · FIG-M10-01 (malla x_b × P_baja, bloque B14-MALLA) y FIG-M10-02 (OFAT, B14-OFAT).

Escrito por el director (Claude) el 2026-10-10: OpenCode quedó sin modelo disponible.
"""
import matplotlib
matplotlib.use("Agg")

import numpy as np
import matplotlib.pyplot as plt

from estilo import aplicar_estilo
from a3_comun import recuadro_fig, leyenda_fig
from a3_comun import (cargar, dispersion, sin_eta_sobre_eje, titulo, titulo_fig,
                      recuadro_oat, guardar_fig, guardar_clases, contar_clases, SEC_VAR)
from nombres import NOMBRE
from pies import armar_pie

aplicar_estilo()
PUNTOS = cargar()
FUENTE = "todos_los_puntos.csv"
HUS = ("Ancla de Húsavík (Fase 3): P_alta 3300 kPa, P_baja 690 kPa, T_fuente 394.15 K, "
       "T_sumidero 278.15 K")


def fig_m10_01():
    sub = PUNTOS[PUNTOS["bloque_director"] == "B14-MALLA"]
    fig, ax = plt.subplots(figsize=(8.5, 5.4))
    dispersion(ax, sub, "x_b", "P_baja", s=40)
    kal = sub[sub["clasificacion"] == "KALINA"]
    pmin = kal.groupby(kal["x_b"].round(3))["P_baja"].min()
    ax.plot(pmin.index, pmin.values, "k--", lw=1, label="P_baja mínima KALINA")
    ax.axvspan(0.28, 0.475, color="0.85", zorder=0)
    ax.text(0.30, sub["P_baja"].max() * 0.97, "sin ciclo\n(x_b ≤ 0.475)", fontsize=8, va="top")
    ax.set_xlabel(NOMBRE["x_b"]); ax.set_ylabel(NOMBRE["P_baja"])
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=8, frameon=False)  # fuera: no tapa datos
    t1 = "Húsavík: la P_baja mínima de KALINA sube con la fracción de amoníaco x_b"
    titulo(ax, t1, "Bloque B14-MALLA · KF-M10-MALLA + KF-M10b-MALLA")
    recuadro_oat(ax, ["KF-M10-MALLA", "KF-M10b-MALLA"], 3)
    pie = armar_pie("FIG-M10-01", t1, ["KF-M10-MALLA", "KF-M10b-MALLA"], "B14-MALLA",
                    "todos los puntos de las dos mallas (mismos datos fijos); línea = P_baja "
                    "mínima KALINA por x_b; x_b = 0.50 es KALINA con η < 1.3 %",
                    n=len(sub), fuente=FUENTE, base=HUS)
    guardar_fig(fig, "M10", "FIG-M10-01_malla_xb_pbaja", pie)
    guardar_clases("M10", "FIG-M10-01_malla_xb_pbaja", contar_clases(sub))
    print(f"FIG-M10-01: {len(sub)} puntos; P_baja mín por x_b = {pmin.to_dict()}")


def fig_m10_02():
    sub = PUNTOS[PUNTOS["bloque_director"] == "B14-OFAT"]
    vs = [v for v in SEC_VAR if (sub["variable"] == v).any()]
    fig, axs = plt.subplots(2, 5, figsize=(16, 6.4), sharey=True)
    for ax, v in zip(axs.flat, vs):
        g = sub[sub["variable"] == v]
        ok = g[g["genuino"] & g["wnet_pos"]]
        dispersion(ax, ok, v, "eta_pct", s=18)
        sin_eta_sobre_eje(ax, g, v, 0.0)
        ax.set_xlabel(NOMBRE[v], fontsize=7.5)
    for ax in axs[:, 0]:
        ax.set_ylabel("η [%]")
    for ax in list(axs.flat)[len(vs):]:
        ax.set_visible(False)
    leyenda_fig(fig, sub)
    recuadro_fig(fig, ["KF-M10-OFAT"])
    t1 = "Húsavík: eficiencia según cada variable, una a la vez (casi todas rompen por O2)"
    titulo_fig(fig, t1, "Bloque B14-OFAT · KF-M10-OFAT (15 valores por variable)")
    pie = armar_pie("FIG-M10-02", t1, ["KF-M10-OFAT"], "B14-OFAT",
                    "η solo en genuinos con W_net > 0; ✕ sobre el eje = no genuino",
                    n=len(sub), fuente=FUENTE, base=HUS)
    guardar_fig(fig, "M10", "FIG-M10-02_ofat_husavik", pie)
    guardar_clases("M10", "FIG-M10-02_ofat_husavik", contar_clases(sub))
    print(f"FIG-M10-02: {len(sub)} puntos en {len(vs)} paneles")


if __name__ == "__main__":
    fig_m10_01()
    fig_m10_02()
    print("a3_m10: OK")
