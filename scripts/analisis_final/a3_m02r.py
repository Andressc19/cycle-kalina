# -*- coding: utf-8 -*-
"""A3 · Figuras M2R: FIG-M02R-n1, n2a, n2b y n3 (bloques B04-n1..B04-n3).

Un bloque por figura. n1 repite el esquema de tira (una variable a la vez, sin
var2); las partes n2a/n2b/n3 son dispersiones en el plano (var1 en y, var2 en x).
"""
import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pies import SIMBOLO
from a3_comun import recuadro_fig, leyenda_fig
from a3_comun import (SEC_VAR, cargar, dispersion, tira, contar_clases, titulo,
                      titulo_fig, recuadro_oat, guardar_fig, guardar_clases)
from nombres import NOMBRE
from pies import armar_pie
from estilo import aplicar_estilo

aplicar_estilo()

PUNTOS = cargar()
FUENTE = "todos_los_puntos.csv"
PP_BASE = ("PP = datos del enunciado del profesor (T_fuente 623.15 K, "
           "P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50)")
TIT = "Parte {p}: {n} KALINA con η y ε en [0.40, 0.95]"


def _pie(id_fig, parte, bloque, id_sub, n_kal, n_pts):
    return armar_pie(id_fig, TIT.format(p=parte, n=n_kal), [id_sub], bloque,
                     f"bloque {bloque} ({id_sub})", n=n_pts, fuente=FUENTE,
                     base=PP_BASE)


# ---------------------------------------------------------------- FIG-M02R-n1
def fig_m02r_n1():
    sub = PUNTOS[PUNTOS["bloque_director"] == "B04-n1"]
    vars_ = [v for v in SEC_VAR if v in set(sub["var1"].dropna())]
    n_kal = int((sub["clasificacion"] == "KALINA").sum())
    fig, axs = plt.subplots(1, len(vars_), figsize=(13, 4.6))
    if len(vars_) == 1:
        axs = [axs]
    for ax, v in zip(axs, vars_):
        sv = sub[sub["var1"] == v]
        tira(ax, sv, "val1", etiquetas=(v == vars_[0]))
        ax.set_title(SIMBOLO.get(v, v), fontsize=8)
        ax.set_xlabel(NOMBRE[v], fontsize=7)
    leyenda_fig(fig, sub)
    recuadro_fig(fig, ["KF-M02R-n1"])
    titulo_fig(fig, TIT.format(p="2.3a", n=n_kal), "Bloque B04-n1 · KF-M02R-n1")
    n = contar_clases(sub)
    pie = _pie("FIG-M02R-n1", "2.3a", "B04-n1", "KF-M02R-n1", n_kal, len(sub))
    guardar_fig(fig, "M02R", "FIG-M02R-n1_oat_eta_eps", pie)
    guardar_clases("M02R", "FIG-M02R-n1_oat_eta_eps", n)
    print(f"FIG-M02R-n1: {len(sub)} pts, KALINA={n_kal}")


def _disp_r(bloque, id_sub, parte, nombre):
    sub = PUNTOS[PUNTOS["bloque_director"] == bloque]
    var1, var2 = sub["var1"].dropna().iloc[0], sub["var2"].dropna().iloc[0]
    n_kal = int((sub["clasificacion"] == "KALINA").sum())
    fig, ax = plt.subplots()
    dispersion(ax, sub, "val2", "val1")
    ax.set_xlabel(NOMBRE[var2])
    ax.set_ylabel(NOMBRE[var1])
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=8, frameon=False)  # fuera: no tapa datos
    titulo(ax, TIT.format(p=parte, n=n_kal), f"Bloque {bloque} · {id_sub}")
    recuadro_oat(ax, [id_sub])
    n = contar_clases(sub)
    pie = _pie(nombre, parte, bloque, id_sub, n_kal, len(sub))
    guardar_fig(fig, "M02R", f"{nombre}_dispersión", pie)
    guardar_clases("M02R", f"{nombre}_dispersión", n)
    print(f"{nombre}: {len(sub)} pts, KALINA={n_kal} "
          f"(x={var2}, y={var1})")


def fig_m02_r():
    _disp_r("B04-n2a", "KF-M02R-n2a", "2.3b", "FIG-M02R-n2a_eps_hrvg_eps_cond")
    _disp_r("B04-n2b", "KF-M02R-n2b", "2.3c", "FIG-M02R-n2b_eps_hrvg_pbaja")
    _disp_r("B04-n3", "KF-M02R-n3", "2.3d", "FIG-M02R-n3_tfuente_eps_cond")


if __name__ == "__main__":
    fig_m02r_n1()
    fig_m02_r()
    print("a3_m02r: OK")