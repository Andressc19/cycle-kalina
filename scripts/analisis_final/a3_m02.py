# -*- coding: utf-8 -*-
"""A3 · Figuras M02: FIG-M02-01 (OAT del bloque B02), FIG-M02-02a y FIG-M02-02b.

Un bloque por figura (regla 1). Los pies usan pies.armar_pie, que para los
barridos OAT (B02) devuelve "Punto base (las demás variables quedan fijas en)".
"""
import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from a3_comun import recuadro_fig, leyenda_fig
from a3_comun import (SEC_VAR, cargar, dispersion, tira, contar_clases,
                      titulo, titulo_fig, recuadro_oat, guardar_fig,
                      guardar_clases)
from nombres import NOMBRE
from pies import armar_pie
from estilo import aplicar_estilo

aplicar_estilo()

PUNTOS = cargar()
FUENTE = "todos_los_puntos.csv"
PP_BASE = ("PP = datos del enunciado del profesor (T_fuente 623.15 K, "
           "P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50)")


# ---------------------------------------------------------------- FIG-M02-01
def fig_m02_01():
    sub = PUNTOS[PUNTOS["bloque_director"] == "B02"]
    vars_ = [v for v in SEC_VAR if v in set(sub["variable"].dropna())]
    n_kal = int((sub["clasificacion"] == "KALINA").sum())
    fig, axs = plt.subplots(2, 5, figsize=(12.5, 6))
    for ax, v in zip(axs.flat, vars_):
        sv = sub[sub["variable"] == v]
        tira(ax, sv, "valor")
        ax.set_title(v, fontsize=8)
        ax.set_yticks([])
        ax.set_ylabel("")
        vi = ax.get_ylim()[1]
        ax.set_ylim(-0.6, 0.6)
        ax.set_xlabel(NOMBRE[v], fontsize=7)
        if ax.get_subplotspec().is_first_col():
            ax.set_ylabel("…", fontsize=7)
    leyenda_fig(fig, sub)
    recuadro_fig(fig, ["KF-M02-N1"])
    titulo_fig(fig,
               f"Con un solo cambio sobre los datos del profesor hay {n_kal} KALINA",
               "Bloque B02 · KF-M02-N1 (barrido de una variable a la vez)")
    n = contar_clases(sub)
    pie = armar_pie("FIG-M02-01",
                    f"Con un solo cambio sobre los datos del profesor hay {n_kal} KALINA",
                    ["KF-M02-N1"], "B02",
                    "bloque B02 (KF-M02-N1), barrido de una variable a la vez",
                    n=len(sub), fuente=FUENTE, base=PP_BASE)
    guardar_fig(fig, "M02", "FIG-M02-01_oat_datos_profesor", pie)
    guardar_clases("M02", "FIG-M02-01_oat_datos_profesor", n)
    print(f"FIG-M02-01: {len(sub)} pts, KALINA={n_kal}, clases={n}")


def _disp_02a(bloque, id_sub, nombre):
    sub = PUNTOS[PUNTOS["bloque_director"] == bloque]
    var1 = sub["var1"].dropna().iloc[0]
    n_kal = int((sub["clasificacion"] == "KALINA").sum())
    fig, ax = plt.subplots()
    dispersion(ax, sub, "P_baja", "val1")
    ax.set_xlabel(NOMBRE["P_baja"])
    ax.set_ylabel(NOMBRE[var1])
    ax.legend(loc="upper left", fontsize=8)
    return sub, n_kal, fig, ax


# ---------------------------------------------------------------- FIG-M02-02a
def fig_m02_02a():
    sub, n_kal, fig, ax = _disp_02a("B03-A", "KF-M02-N2-A", "A")
    titulo(ax,
           f"Ruta A: conservando la fuente del profesor (623 K), {n_kal} KALINA",
           "Bloque B03-A · KF-M02-N2-A")
    recuadro_oat(ax, ["KF-M02-N2-A"])
    n = contar_clases(sub)
    pie = armar_pie("FIG-M02-02a",
                    f"Ruta A: conservando la fuente del profesor (623 K), "
                    f"{n_kal} KALINA",
                    ["KF-M02-N2-A"], "B03-A", "bloque B03-A (KF-M02-N2-A)",
                    n=len(sub), fuente=FUENTE, base=PP_BASE)
    guardar_fig(fig, "M02", "FIG-M02-02a_ruta_a_fuente_profesor", pie)
    guardar_clases("M02", "FIG-M02-02a_ruta_a_fuente_profesor", n)
    print(f"FIG-M02-02a: {len(sub)} pts, KALINA={n_kal}")


# ---------------------------------------------------------------- FIG-M02-02b
def fig_m02_02b():
    sub = PUNTOS[PUNTOS["bloque_director"] == "B03-B"]
    km = sub[sub["clasificacion"] == "KALINA"]
    n_kal = len(km)
    tmin, tmax = km["val1"].min(), km["val1"].max()
    fig, ax = plt.subplots()
    dispersion(ax, sub, "P_baja", "val1")
    ax.set_xlabel(NOMBRE["P_baja"])
    ax.set_ylabel(NOMBRE["T_fuente"])
    ax.legend(loc="upper left", fontsize=8)
    titulo(ax,
           f"Ruta B: KALINA con T_fuente entre {tmin:.0f} y {tmax:.0f} K",
           "Bloque B03-B · KF-M02-N2-B")
    recuadro_oat(ax, ["KF-M02-N2-B"])
    n = contar_clases(sub)
    pie = armar_pie("FIG-M02-02b",
                    f"Ruta B: KALINA con T_fuente entre {tmin:.0f} y {tmax:.0f} K",
                    ["KF-M02-N2-B"], "B03-B", "bloque B03-B (KF-M02-N2-B)",
                    n=len(sub), fuente=FUENTE, base=PP_BASE)
    guardar_fig(fig, "M02", "FIG-M02-02b_ruta_b_tfuente", pie)
    guardar_clases("M02", "FIG-M02-02b_ruta_b_tfuente", n)
    print(f"FIG-M02-02b: {len(sub)} pts, KALINA={n_kal} "
          f"(T_fuente {tmin:.0f}–{tmax:.0f} K)")


if __name__ == "__main__":
    fig_m02_01()
    fig_m02_02a()
    fig_m02_02b()
    print("a3_m02: OK")