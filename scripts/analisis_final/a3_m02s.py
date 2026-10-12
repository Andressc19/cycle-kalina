# -*- coding: utf-8 -*-
"""A3 · FIG-M02S-01: síntesis de bases B05-B1..B05-B4 (KF-M02S).

Figura de síntesis (excepción de la regla 1): cada línea es una base, rotulada
con lo que la distingue. El pie lista los datos fijos de cada base por separado
y nombra a B4 (0 KALINA) porque no se dibuja.
"""
import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from estilo import aplicar_estilo, recuadro_condiciones
from a3_comun import cargar, titulo_fig, guardar_fig
from nombres import NOMBRE
from pies import SIMBOLO

aplicar_estilo()

PUNTOS = cargar()
FUENTE = "todos_los_puntos.csv"
BASES = [("B05-B1", "KF-M02S-B1", "#2E7D32", "o", "2.4a · T_fuente = 403 K (A*)"),
         ("B05-B2", "KF-M02S-B2", "#1565C0", "^", "2.4b · T_fuente = 420 K"),
         ("B05-B3", "KF-M02S-B3", "#EF8A17", "s",
          "2.4c · ε_HRVG = 0.40 (fuente del profesor)")]


def _texto_base(bloque, id_sub):
    """Datos fijos y barridos de una base, desde condiciones_por_subcaso."""
    cc = pd.read_csv("analisis_final/00_inventario/condiciones_por_subcaso.csv")
    c = cc[cc["id_subcaso"] == id_sub]
    fijos = c[c["estado"] == "fijo"]
    if "motor" in set(fijos["variable"]):
        barr = "; ".join(SIMBOLO.get(x, x) for x in sorted(c[c["estado"] == "barrido"]["variable"].unique()))
        f = "; ".join(f"{SIMBOLO.get(v, v)} = {vf}"
                      for v, vf in fijos[["variable", "valor_fijo"]].values)
        return f"Datos fijos: {f}. Datos barridos: {barr}."
    return ""


def fig_m02s_01():
    ts = np.array([278.15, 283.15, 288.15, 293.15, 300.032917])
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 4.2), sharex=True)
    n_lin = []
    for bloque, id_sub, color, m, label in BASES:
        sub = PUNTOS[PUNTOS["bloque_director"] == bloque]
        sub = sub[sub["clasificacion"] == "KALINA"]
        pmin, emax = [], []
        for t in ts:
            g = sub[np.isclose(sub["T_sumidero"], t)]
            pmin.append(g["P_baja"].min() if len(g) else np.nan)
            emax.append(g["eta_pct"].max() if len(g) else np.nan)
        ax1.plot(ts, pmin, color=color, marker=m, label=label, ms=6, lw=1.6)
        ax2.plot(ts, emax, color=color, marker=m, label=label, ms=6, lw=1.6)
        n_lin.append(len(pmin))
    ax1.set_ylabel("P_baja mínima de KALINA [kPa]")
    ax2.set_ylabel("η máxima de KALINA [%]")
    for ax in (ax1, ax2):
        ax.set_xlabel(NOMBRE["T_sumidero"])
        ax.set_xticks(ts)
        ax.set_xticklabels([f"{t:.2f}" for t in ts], fontsize=7)
    ax1.legend(loc="upper left", fontsize=8)
    ax2.legend(loc="lower left", fontsize=8)   # abajo a la derecha tapaba la línea B3
    recuadro_condiciones(ax2, "Síntesis: cada parte tiene sus propios datos fijos\n"
                              "2.4d (datos del profesor): 0 KALINA — no se dibuja")
    titulo_fig(fig, "Un sumidero más frío baja la P_baja mínima de KALINA y sube η",
               "Estudio 2.4 · síntesis de las partes 2.4a–2.4c")
    lineas = []
    for bloque, id_sub, color, m, label in BASES:
        tag, rest = label.split(" · ", 1)
        lineas.append(f"Parte {tag} ({rest}): {_texto_base(bloque, id_sub)}")
    pie = ("Figura FIG-M02S-01. Un sumidero más frío baja la P_baja mínima de "
           "KALINA y sube η.\n"
           "Estudio 2.4 (figura de síntesis: cada base es una parte con sus "
           "propios datos fijos y cada línea es una parte).\n"
           + "\n".join(lineas)
           + "\nBase B4 (datos del profesor, T_fuente 623.15 K): 0 KALINA; no se "
             "dibuja (queda nombrada en el pie).\n"
           "Filtro: mínimos de P_baja y máximos de η de los KALINA por "
           "(base, T_sumidero).\n"
           f"n = 15 puntos por panel (3 bases × 5 T_sumidero). Fuente: {FUENTE}.")
    guardar_fig(fig, "M02S", "FIG-M02S-01_sumidero_pbaja_eta", pie)
    print(f"FIG-M02S-01: {len(n_lin)} bases graficadas (B1, B2, B3)")


if __name__ == "__main__":
    fig_m02s_01()
    print("a3_m02s: OK")