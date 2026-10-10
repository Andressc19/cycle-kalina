# -*- coding: utf-8 -*-
"""A3 · Figuras M04: CDF por variable (FIG-M04-01), plano de presiones
(FIG-M04-02), PRCC (FIG-M04-03) e histogramas ΔP y r_P (FIG-M04-04).
"""
import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import ks_2samp

from estilo import aplicar_estilo, recuadro_condiciones
from a3_comun import (SEC_VAR, cargar, dispersion, contar_clases, titulo,
                      titulo_fig, recuadro_oat, guardar_fig, guardar_clases)
from nombres import NOMBRE, ETIQUETA_CLASE
from pies import armar_pie

aplicar_estilo()

PUNTOS = cargar()
FUENTE = "todos_los_puntos.csv y resultados/2026-10-07_final_M4b/"
CAJA_BASE = ("Sin punto base: muestreo en la caja de rangos indicada en "
             "'Datos barridos'")
B07 = PUNTOS[PUNTOS["bloque_director"] == "B07"].copy()
GEN = B07[B07["genuino"]]
KAL = GEN[GEN["clasificacion"] == "KALINA"]
RESTO = GEN[GEN["clasificacion"] != "KALINA"]


def _ecdf(x):
    x = np.sort(x)
    return x, np.arange(1, len(x) + 1) / len(x)


# ---------------------------------------------------------------- FIG-M04-01
def fig_m04_01():
    fig, axs = plt.subplots(2, 5, figsize=(13, 7.2), sharey=True)
    for ax, v in zip(axs.flat, SEC_VAR):
        xk, yk = _ecdf(KAL[v].dropna())
        xr, yr = _ecdf(RESTO[v].dropna())
        ax.plot(xk, yk, color="#2E7D32", lw=1.6)
        ax.plot(xr, yr, color="0.55", ls="--", lw=1.2)
        ks, p = ks_2samp(KAL[v].dropna(), RESTO[v].dropna())
        ax.text(0.04, 0.90, f"KS = {ks:.2f}, p = {p:.1e}", transform=ax.transAxes,
                fontsize=6.5)
        ax.set_title(v, fontsize=8)
        if ax.get_subplotspec().is_last_row():
            pass
        ax.set_xlabel(NOMBRE[v], fontsize=6)
        if ax.get_subplotspec().is_first_col():
            ax.set_ylabel("F(x)")
    axs.flat[0].legend([plt.Line2D([0], [0], color="#2E7D32"),
                        plt.Line2D([0], [0], color="0.55", ls="--")],
                       [f"KALINA (n = {len(KAL)})",
                        f"resto genuino (n = {len(RESTO)})"], loc="upper left",
                       fontsize=7)
    titulo_fig(fig,
               f"Qué variables separan a los KALINA del resto (LHS de {len(GEN)} puntos)",
               "Bloque B07 · KF-M04 + KF-M04b (puntos genuinos)")
    pie = armar_pie("FIG-M04-01",
                    f"Qué variables separan a los KALINA del resto (LHS de "
                    f"{len(GEN)} puntos)",
                    ["KF-M04", "KF-M04b"], "B07",
                    "B07 (KF-M04 + KF-M04b), puntos genuinos", n=len(GEN),
                    fuente="todos_los_puntos.csv", base=CAJA_BASE)
    guardar_fig(fig, "M04", "FIG-M04-01_cdf_por_variable", pie)
    guardar_clases("M04", "FIG-M04-01_cdf_por_variable",
                   {"KALINA": len(KAL), "resto": len(RESTO)})
    print(f"FIG-M04-01: {len(GEN)} genuinos ({len(KAL)} KALINA)")


# ---------------------------------------------------------------- FIG-M04-02
def fig_m04_02():
    rp5, rp95 = np.percentile(KAL["rP"], [5, 95])
    fig, ax = plt.subplots()
    dispersion(ax, B07, "P_alta", "P_baja")
    pa = np.linspace(B07["P_alta"].min(), B07["P_alta"].max(), 50)
    for rp in (rp5, rp95):
        ax.plot(pa, pa / rp, "k--", lw=0.8)
    ax.set_xlabel(NOMBRE["P_alta"])
    ax.set_ylabel(NOMBRE["P_baja"])
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=8, frameon=False)  # fuera: no tapa datos
    titulo(ax,
           f"El 90 % de los KALINA tiene razón de presiones entre {rp5:.1f} y "
           f"{rp95:.1f}",
           "Bloque B07 · KF-M04 + KF-M04b")
    recuadro_oat(ax, ["KF-M04", "KF-M04b"], 3)
    pie = armar_pie("FIG-M04-02",
                    f"El 90 % de los KALINA tiene razón de presiones entre {rp5:.1f} "
                    f"y {rp95:.1f}",
                    ["KF-M04", "KF-M04b"], "B07", "B07 (KF-M04 + KF-M04b)",
                    n=len(B07), fuente="todos_los_puntos.csv", base=CAJA_BASE)
    guardar_fig(fig, "M04", "FIG-M04-02_plano_presiones", pie)
    guardar_clases("M04", "FIG-M04-02_plano_presiones", contar_clases(B07))
    print(f"FIG-M04-02: r_P p5–p95 = {rp5:.2f}–{rp95:.2f}")


# ---------------------------------------------------------------- FIG-M04-03
def fig_m04_03():
    pr = pd.read_csv("resultados/2026-10-07_final_M4b/m4b_prcc.csv")
    pr = pr[pr["salida"] == "eta"].copy()
    pr["abs"] = pr["prcc"].abs()
    pr = pr.sort_values("abs", ascending=False)
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    colores = ["#2E7D32" if x > 0 else "#C62828" for x in pr["prcc"]]
    ax.barh(range(len(pr)), pr["prcc"], color=colores, alpha=0.9)
    ax.errorbar(pr["prcc"], range(len(pr)), xerr=[pr["prcc"] - pr["ic_lo"],
               pr["ic_hi"] - pr["prcc"]], fmt="none", ecolor="0.25", lw=0.7)
    ax.axvline(0, color="0.35", lw=0.8)
    ax.set_yticks(range(len(pr)))
    ax.set_yticklabels(pr["variable"])
    ax.set_xlabel("PRCC [–]")
    ax.set_xlim(-1, 1)
    n = int(pr["n"].iloc[0])
    titulo(ax, f"Influencia de cada variable sobre η (PRCC, {n} puntos)",
           "Bloque B07 · KF-M04b (LHS, salida η)")
    recuadro_oat(ax, ["KF-M04b"], 3)
    pie = armar_pie("FIG-M04-03",
                    f"Influencia de cada variable sobre η (PRCC, {n} puntos)",
                    ["KF-M04b"], "B07", "m4b_prcc.csv (fila de salida = η)", n=n,
                    fuente="resultados/2026-10-07_final_M4b/m4b_prcc.csv",
                    base=CAJA_BASE)
    guardar_fig(fig, "M04", "FIG-M04-03_prcc_eta", pie)
    print("FIG-M04-03: PRCC de η calculado (10 variables)")


# ---------------------------------------------------------------- FIG-M04-04
def fig_m04_04():
    a, b = np.percentile(KAL["dP"], [5, 95])
    c, d = np.percentile(KAL["rP"], [5, 95])
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.2))
    for ax, col, xlab in ((ax1, "dP", NOMBRE["dP"]), (ax2, "rP", NOMBRE["rP"])):
        ax.hist(RESTO[col], bins=25, color="0.6", alpha=0.45,
                label=f"resto (n = {len(RESTO)})")
        ax.hist(KAL[col], bins=25, color="#2E7D32", alpha=0.45,
                label=f"KALINA (n = {len(KAL)})")
        ax.set_xlabel(xlab)
    ax1.legend(loc="upper right", fontsize=8)
    ax2.legend(loc="upper right", fontsize=8)
    recuadro_condiciones(ax2, "Puntos genuinos de B07\nKALINA vs resto")
    titulo_fig(fig,
               f"El 90 % de los KALINA tiene ΔP {a:.0f}–{b:.0f} kPa y r_P "
               f"{c:.1f}–{d:.1f}",
               "Bloque B07 · KF-M04 + KF-M04b (p5–p95 de los KALINA)")
    pie = armar_pie("FIG-M04-04",
                    f"El 90 % de los KALINA tiene ΔP {a:.0f}–{b:.0f} kPa y r_P "
                    f"{c:.1f}–{d:.1f}",
                    ["KF-M04", "KF-M04b"], "B07", "B07, puntos genuinos",
                    n=len(GEN), fuente="todos_los_puntos.csv", base=CAJA_BASE)
    guardar_fig(fig, "M04", "FIG-M04-04_hist_dP_rP", pie)
    print(f"FIG-M04-04: ΔP p5–p95 = {a:.0f}–{b:.0f} kPa; r_P p5–p95 = {c:.2f}–{d:.2f}")


if __name__ == "__main__":
    fig_m04_01()
    fig_m04_02()
    fig_m04_03()
    fig_m04_04()
    print("a3_m04: OK")