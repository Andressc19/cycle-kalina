# -*- coding: utf-8 -*-
"""A3 · FIG-M06-01 (paridad teqp vs motor real, bloque B12) y FIG-M07-01 (búsqueda de η, B11).

Escrito por el director (Claude) el 2026-10-10: OpenCode quedó sin modelo disponible.
"""
import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from estilo import aplicar_estilo, recuadro_condiciones
from a3_comun import titulo, guardar_fig

aplicar_estilo()
M6 = "resultados/2026-10-08_final_M6/m6_comparacion.csv"
M9 = "resultados/2026-10-08_final_M9/m9_motor_real.csv"
M7 = "resultados/2026-10-07_final_M7/m7_trayectorias.csv"
ARRANQUE = {"A1": "A1 · libre (desde el mejor de M4b)",
            "A2": "A2 · libre (desde el mejor de M2S)",
            "A3": "A3 · conserva sus temperaturas",
            "A4": "A4 · conserva sus presiones y su clima",
            "A5": "A5 · conserva su fuente y su x_b (fuera de rango)"}


def fig_m06():
    a = pd.read_csv(M6).assign(fuente="M6 (motor real con 300 s)")
    b = pd.read_csv(M9).assign(fuente="M9 (motor real con 1500 s)")
    d = pd.concat([a, b], ignore_index=True)
    par = d.dropna(subset=["eta_teqp", "eta_real"])
    sin = d[d["eta_real"].isna()]
    fig, ax = plt.subplots(figsize=(6.6, 5.6))
    lo, hi = 0, 17
    xs = np.linspace(lo, hi, 2)
    ax.plot(xs, xs, color="0.3", lw=0.8, label="1:1")
    ax.fill_between(xs, xs - 0.7, xs + 0.7, color="#2E7D32", alpha=0.12,
                    label="banda ±0.7 pp")
    for f, m, c in (("M6 (motor real con 300 s)", "o", "#1565C0"),
                    ("M9 (motor real con 1500 s)", "s", "#2E7D32")):
        g = par[par["fuente"] == f]
        ax.scatter(100 * g["eta_teqp"], 100 * g["eta_real"], marker=m, s=60, color=c,
                   label=f"{f} (n = {len(g)})", zorder=3)
        for _, r in g.iterrows():
            ax.annotate(str(r["id"]), (100 * r["eta_teqp"], 100 * r["eta_real"]),
                        fontsize=7, xytext=(4, -10), textcoords="offset points")
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    ax.set_xlabel("η con teqp [%]"); ax.set_ylabel("η con el motor real [%]")
    ax.legend(loc="upper left", fontsize=8)
    t1 = f"teqp y el motor real coinciden en los {len(par)} puntos que el motor real resolvió"
    titulo(ax, t1, "Bloque B12 · KF-M06 y KF-M09-REAL (puntos de control)")
    recuadro_condiciones(ax, "Cada punto conserva sus datos de origen\n"
                             f"Sin η real (cortados por tiempo, 300 s): {len(sin)}")
    pie = ("Figura FIG-M06-01. " + t1 + ".\n"
           "Caso(s): KF-M06-VER y KF-M09-REAL (bloque B12; puntos de control, cada uno con "
           "sus propios datos, no comparables entre sí).\n"
           "Puntos: " + "; ".join(f"{r['id']} = {r['origen']}" for _, r in par.iterrows()) + ".\n"
           "Sin η real (motor real cortado por el límite de 300 s, no por la física): "
           + ", ".join(str(i) for i in sin["id"]) + ".\n"
           "Filtro: pares con η de ambos motores. Marcas: recta 1:1 y banda ±0.7 pp "
           "(incertidumbre del modelo de propiedades).\n"
           f"n = {len(par)}. Fuente: m6_comparacion.csv y m9_motor_real.csv.")
    guardar_fig(fig, "M06", "FIG-M06-01_paridad_teqp_real", pie)
    print(f"FIG-M06-01: {len(par)} pares; sin η real: {len(sin)}")


def fig_m07():
    t = pd.read_csv(M7)
    t = t[t["aceptado"].astype(str).str.lower().isin(["true", "1"])] if "aceptado" in t else t
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    estilos = {"A1": "-", "A2": "-", "A3": "-", "A4": "-", "A5": "--"}
    for a, g in t.groupby("arranque"):
        g = g.sort_values("iteracion")
        ax.plot(g["iteracion"], 100 * g["eta"], estilos.get(a, "-"), marker="o", ms=4,
                label=f"{ARRANQUE.get(a, a)}: {100 * g['eta'].max():.1f} %")
    ax.set_xlabel("Iteración de la búsqueda"); ax.set_ylabel("Eficiencia térmica del ciclo, η [%]")
    ax.legend(loc="lower right", fontsize=8)
    emax = 100 * t["eta"].max()
    t1 = (f"La búsqueda llega a η = {emax:.1f} % dentro de la región KALINA "
          "(equipos a 0.95)")
    titulo(ax, t1, "Bloques B11-A1 … B11-A5 · KF-M07 (una línea por arranque)")
    recuadro_condiciones(ax, "Cada arranque conserva datos distintos del profesor\n"
                             "A5 (línea discontinua): todos sus KALINA fuera de rango")
    pie = ("Figura FIG-M07-01. " + t1 + ".\n"
           "Caso(s): KF-M07-A1 … A5 (bloques B11-A1 … B11-A5; figura de síntesis: cada línea "
           "es un arranque con sus propios datos conservados).\n"
           + "\n".join(f"{v}." for v in ARRANQUE.values()) + "\n"
           "Filtro: pasos aceptados de cada búsqueda (cada uno es KALINA genuino, D = 0).\n"
           f"n = {len(t)} pasos aceptados. Fuente: m7_trayectorias.csv.")
    guardar_fig(fig, "M07", "FIG-M07-01_busqueda_eta", pie)
    print(f"FIG-M07-01: η máx = {emax:.2f} %")


if __name__ == "__main__":
    fig_m06()
    fig_m07()
    print("a3_m07: OK")
