# -*- coding: utf-8 -*-
"""A3 · FIG-M05-S1…S5 (un escenario por figura, bloques B09-k) y FIG-M05c-01 (bloque B10).

Escrito por el director (Claude) el 2026-10-10: OpenCode quedó sin modelo disponible.
Sigue las reglas del TASK_CONTEXT_af_A3: un bloque por figura, ejes solo con variables
barridas, forma + color por clase, título-conclusión, recuadro de condiciones y pie.
"""
import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from estilo import aplicar_estilo, COLOR_CLASE, MARCADOR_CLASE
from a3_comun import recuadro_fig, leyenda_fig
from a3_comun import (cargar, dispersion, titulo, titulo_fig, recuadro_oat,
                      guardar_fig, guardar_clases, contar_clases)
from nombres import NOMBRE, ETIQUETA_CLASE
from pies import armar_pie

aplicar_estilo()
PUNTOS = cargar()
COND = pd.read_csv("analisis_final/00_inventario/condiciones_por_subcaso.csv")
FUENTE = "todos_los_puntos.csv"
PP = ("PP = datos del enunciado del profesor (T_fuente 623.15 K, P_alta 3000 kPa, "
      "P_baja 400 kPa, x_b 0.50)")
ESCENARIO = {"1": "sus temperaturas (T_fuente y T_sumidero)",
             "2": "sus presiones (P_alta y P_baja)",
             "3": "sus presiones y su clima",
             "4": "su P_alta y sus temperaturas",
             "5": "su fuente y su composición (T_fuente y x_b)"}
ORDEN_X = ["P_alta", "T_fuente", "x_b", "T_sumidero", "eps_cond"]
ORDEN_Y = ["P_baja", "eps_cond", "x_b", "T_fuente"]


def barridas(id_sub):
    c = COND[(COND["id_subcaso"] == id_sub) & (COND["estado"] == "barrido")]
    return set(c["variable"])


def ejes(id_sub):
    b = barridas(id_sub)
    y = next(v for v in ORDEN_Y if v in b)
    x = next(v for v in ORDEN_X if v in b and v != y)
    return x, y


def fig_m05(k):
    id_sub, bloque = f"KF-M05-{k}", f"B09-{k}"
    sub = PUNTOS[PUNTOS["id_subcaso"] == id_sub]
    ev = sub[~sub["omitido"]]
    n_kal = int((ev["clasificacion"] == "KALINA").sum())
    n_conf = int(((ev["clasificacion"] == "KALINA") & ~ev["fuera_rango"]).sum())
    x, y = ejes(id_sub)
    fig, ax = plt.subplots(figsize=(8.5, 5.4))
    dispersion(ax, sub, x, y, s=22)
    ax.set_xlabel(NOMBRE[x]); ax.set_ylabel(NOMBRE[y])
    ax.legend(loc="upper left", fontsize=8)
    t1 = (f"Escenario S{k} (conserva {ESCENARIO[k]}): {n_kal} KALINA de {len(ev)} "
          f"evaluados, {n_conf} confiables")
    titulo(ax, t1, f"Bloque {bloque} · {id_sub}")
    recuadro_oat(ax, [id_sub], 3)
    pie = armar_pie(f"FIG-M05-S{k}", t1, [id_sub], bloque,
                    "todos los puntos evaluados (omitidos no se dibujan; marcador hueco = "
                    "fuera del rango confiable)", n=len(ev), fuente=FUENTE, base=PP)
    guardar_fig(fig, "M05", f"FIG-M05-S{k}_escenario_{k}", pie)
    guardar_clases("M05", f"FIG-M05-S{k}_escenario_{k}", contar_clases(ev))
    print(f"FIG-M05-S{k}: {len(ev)} evaluados, KALINA={n_kal} (confiables {n_conf}); x={x}, y={y}")


def fig_m05c():
    sub = PUNTOS[PUNTOS["bloque_director"] == "B10"]
    climas = sorted(sub["T_sumidero"].round(3).unique())
    fig, axs = plt.subplots(1, len(climas), figsize=(14, 4.6), sharey=True)
    for ax, t in zip(axs, climas):
        g = sub[np.isclose(sub["T_sumidero"], t, atol=1e-3)]
        for c in ["KALINA", "CORREGIBLE", "INVIABLE", "NO_CONVERGIO", "N2"]:
            s2 = g[g["clase_trazo"] == c]
            if len(s2):
                ax.scatter(s2["T_fuente"], s2["eps_cond"], s=120, marker=MARCADOR_CLASE[c]
                           if c != "KALINA" else "s", color=COLOR_CLASE[c],
                           label=f"{ETIQUETA_CLASE[c]} (n = {len(s2)})")
        ax.set_title(f"T_sumidero = piso de O2 = {t:.2f} K", fontsize=9)
        ax.set_xlabel(NOMBRE["T_fuente"])

    axs[0].set_ylabel(NOMBRE["eps_cond"])
    leyenda_fig(fig, sub)
    kal = sub[sub["clasificacion"] == "KALINA"]
    t1 = (f"Con las presiones del profesor hay KALINA desde T_fuente ≈ "
          f"{kal['T_fuente'].min():.0f} K; con su clima (300 K) hace falta ε_cond ≥ 0.875")
    titulo_fig(fig, t1, "Bloque B10 · KF-M05c (malla 11 × 5 × 3)")
    recuadro_fig(fig, ["KF-M05c"])
    pie = armar_pie("FIG-M05c-01", t1, ["KF-M05c"], "B10",
                    "todos los puntos de la malla (cuadrado verde = KALINA)", n=len(sub),
                    fuente=FUENTE, base="PP con P_alta = 3000 kPa y P_baja = 400 kPa conservadas")
    guardar_fig(fig, "M05", "FIG-M05c-01_franja_presiones_profesor", pie)
    guardar_clases("M05", "FIG-M05c-01_franja_presiones_profesor", contar_clases(sub))
    print(f"FIG-M05c-01: {len(sub)} puntos, KALINA={len(kal)}")


if __name__ == "__main__":
    for k in "12345":
        fig_m05(k)
    fig_m05c()
    print("a3_m05: OK")
