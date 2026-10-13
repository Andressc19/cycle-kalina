# -*- coding: utf-8 -*-
"""A3 · FIG-M04c-01: fracción de KALINA por franja de P_baja (bloque B08).

Puntos evaluados = no omitidos. El % de KALINA se calcula por franja de
100 kPa entre 1500 y 2500 kPa.
"""
import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from estilo import aplicar_estilo, recuadro_condiciones
from a3_comun import cargar, titulo, recuadro_oat, guardar_fig
from nombres import NOMBRE
from pies import armar_pie

aplicar_estilo()

PUNTOS = cargar()
CAJA_BASE = ("Sin punto base: muestreo en la caja de rangos indicada en "
             "'Datos barridos'")


def fig_m04c_01():
    sub = PUNTOS[PUNTOS["bloque_director"] == "B08"].copy()
    sub = sub[~sub["omitido"]]
    n_eval = len(sub)
    bordes = np.arange(1500, 2600, 100)
    k = np.digitize(sub["P_baja"], bordes) - 1
    etiquetas, pcts, conf, fuera = [], [], [], []
    for i, lo in enumerate(bordes[:-1]):
        g = sub[k == i]
        if len(g):
            kal = g["clasificacion"] == "KALINA"
            etiquetas.append(f"{lo:.0f}–{lo + 100:.0f}")
            pcts.append(100 * kal.mean())
            conf.append(100 * int((kal & ~g["fuera_rango"]).sum()) / len(g))
            fuera.append(100 * int((kal & g["fuera_rango"]).sum()) / len(g))
    n_conf = int(((sub["clasificacion"] == "KALINA") & ~sub["fuera_rango"]).sum())
    n_fuera = int(((sub["clasificacion"] == "KALINA") & sub["fuera_rango"]).sum())
    fig, ax = plt.subplots(figsize=(9.5, 4.5))
    ax.bar(range(len(pcts)), conf, color="#2E7D32", alpha=0.9,
           label=f"KALINA dentro del rango (n = {n_conf})")
    ax.bar(range(len(pcts)), fuera, bottom=conf, facecolor="none",
           edgecolor="#2E7D32", hatch="//",
           label=f"KALINA fuera de rango (n = {n_fuera})")
    for i, p in enumerate(pcts):
        ax.text(i, p + 1.5, f"{p:.0f}", ha="center", fontsize=8)
    ax.set_xticks(range(len(pcts)))
    ax.set_xticklabels(etiquetas, fontsize=7.5, rotation=30, ha="right")
    ax.set_ylabel("% de puntos KALINA")
    ax.set_xlabel("Franja de P_baja [kPa]")
    ax.set_ylim(0, 110)
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=8, frameon=False)  # fuera: no tapa barras
    titulo(ax, "Fracción de KALINA al subir P_baja entre 1500 y 2500 kPa",
           "Bloque B08 · KF-M04c (puntos evaluados)")
    recuadro_oat(ax, ["KF-M04c"], 3)
    pie = armar_pie("FIG-M04c-01",
                    "Fracción de KALINA al subir P_baja entre 1500 y 2500 kPa",
                    ["KF-M04c"], "B08", "B08 (KF-M04c), puntos evaluados",
                    n=n_eval, fuente="todos_los_puntos.csv", base=CAJA_BASE,
                    marcas="Barra sólida: KALINA dentro del rango; rayada: KALINA fuera de rango")
    guardar_fig(fig, "M04", "FIG-M04c-01_kalina_por_franja_Pbaja", pie)
    print(f"FIG-M04c-01: {n_eval} evaluados; % KALINA por franja = {pcts}")


if __name__ == "__main__":
    fig_m04c_01()
    print("a3_m04c: OK")