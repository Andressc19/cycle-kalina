# -*- coding: utf-8 -*-
"""Sens2 F1 - A7t: eficiencia del ciclo frente a T_fuente por bandas de 20 K (datos ya calculados).

Sin corridas nuevas del motor: describe lo ya muestreado. Para cada banda de T_fuente de
20 K ([340, 360) a [560, 580)) calcula el conteo de clases, P(KALINA) (con y sin los
NO_CONVERGIO en el denominador), el maximo de eta (con las condiciones de ese punto) y el
maximo solo dentro del rango experimental (fuera_rango == False), P90, mediana, W_net/m_b
y la mediana del muestreo LHS (estudios 3 y 14). Salidas: p6_ciclo_T.csv y p6_ciclo_T.md.
"""
import os
import sys

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)

SALIDA = os.path.join(RAIZ, "resultados", "2026-10-18_sens2_F1")
DATOS = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P2", "p2_dataset_dedup.csv")
LHS = [3, 14]
MIN_KALINA = 10
COLS = ["banda", "T_centro_C", "n", "n_kalina", "n_corregible", "n_inviable", "n_no_convergio",
        "p_kalina", "p_kalina_si_convergio", "eta_max", "id_punto", "T_fuente", "P_alta", "P_baja",
        "x_b", "eta_t", "eps_reg", "eps_cond", "fuera_rango", "eta_max_dentro", "eta_p90",
        "eta_mediana", "wnet_mb_max", "wnet_mb_mediana", "eta_mediana_lhs", "n_kalina_lhs", "n_kalina_dentro", "eta_p90_dentro", "eta_mediana_dentro"]


def _pct(v, p):
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    return float(np.percentile(v, p)) if len(v) else np.nan


def fila_banda(sub, lo, hi):
    """Estadisticos de una banda de T_fuente; devuelve los valores tras banda y T_centro_C."""
    n = int(len(sub))
    cl = sub["clasificacion"]
    kal = sub[cl == "KALINA"]
    nk = int(len(kal))
    ncorr = int((cl == "CORREGIBLE").sum())
    ninv = int((cl == "INVIABLE").sum())
    nnc = int((cl == "NO_CONVERGIO").sum())
    p_kal = nk / n if n else np.nan
    den = n - nnc
    p_kal_c = nk / den if den > 0 else np.nan

    kv = kal[np.isfinite(kal["eta_pct"].to_numpy(float))]
    eta = kv["eta_pct"].to_numpy(float)
    if len(kv):
        mx = kv.iloc[int(np.nanargmax(eta))]
        emax = float(mx["eta_pct"])
        pto = [mx["id_punto"], float(mx["T_fuente"]), float(mx["P_alta"]), float(mx["P_baja"]),
               float(mx["x_b"]), float(mx["eta_t"]), float(mx["eps_reg"]), float(mx["eps_cond"]),
               bool(mx["fuera_rango"])]
    else:
        emax = np.nan
        pto = [np.nan] * 8 + [""]

    dentro = kv[kv["fuera_rango"] == False]["eta_pct"].to_numpy(float)  # noqa: E712
    emax_d = float(np.max(dentro)) if len(dentro) else np.nan
    w = kv["wnet_mb"].to_numpy(float)
    w = w[np.isfinite(w)]
    lhs = kv[kv["estudio"].isin(LHS)]["eta_pct"].to_numpy(float)
    return ([n, nk, ncorr, ninv, nnc, p_kal, p_kal_c, emax] + pto +
            [emax_d, _pct(eta, 90), _pct(eta, 50),
             float(np.max(w)) if len(w) else np.nan,
             float(np.median(w)) if len(w) else np.nan,
             float(np.median(lhs)) if len(lhs) else np.nan, int(len(lhs)), int(len(dentro)), _pct(dentro, 90), _pct(dentro, 50)])


def tablas(d):
    bins = list(range(340, 600, 20))
    b = pd.cut(d["T_fuente"], bins=bins, right=False)
    filas = []
    for iv in pd.IntervalIndex.from_breaks(bins, closed="left"):
        sub = d[b == iv]
        lo, hi = iv.left, iv.right
        filas.append([str(iv), (lo + hi) / 2.0 - 273.15] + fila_banda(sub, lo, hi))
    return pd.DataFrame(filas, columns=COLS)


def markdown(tab):
    l = ["# Sens2 F1 - A7t: eficiencia del ciclo frente a T_fuente", "",
         "Bandas de T_fuente de 20 K sobre los %d puntos de `p2_dataset_dedup.csv`." % int(tab["n"].sum()),
         "eta en % y P(KALINA) = KALINA/n. El maximo es el mayor valor muestreado (esta tabla",
         "describe lo ya calculado; el optimo por banda esta en p6_opt_T.md).", "",
         "## Mejor eta dentro del rango experimental por banda", "",
         "| Banda (T_centro, C) | n | P(KALINA) | eta maxima dentro del rango (%) |"
         " P_alta del maximo (kPa) | x_b del maximo (-) |",
         "|---|---|---|---|---|---|"]
    for _, x in tab.iterrows():
        l.append("| %.1f | %d | %.3f | %s | %s | %s |" % (
            x["T_centro_C"], int(x["n"]), x["p_kalina"],
            "" if not np.isfinite(x["eta_max_dentro"]) else "%.3f" % x["eta_max_dentro"],
            "" if not np.isfinite(x["P_alta"]) else "%.3f" % x["P_alta"],
            "" if not np.isfinite(x["x_b"]) else "%.3f" % x["x_b"]))
    n_pocos = int((tab["n_kalina_dentro"] < MIN_KALINA).sum())
    l += ["", "Notas:", "",
          "- El maximo por banda es el mayor valor muestreado y no el optimo del ciclo.",
          "- Las bandas con menos de %d KALINA dentro del rango experimental: %d de %d bandas; en ellas el maximo"
          " dentro del rango no concluye (columna n_kalina_dentro del CSV)." % (MIN_KALINA, n_pocos, len(tab)),
          "- Sobre ~150 C el limite de 420 K del liquido deja casi todos los KALINA fuera del rango experimental: la caida del maximo"
          " dentro del rango en las bandas calientes coincide con ese corte y no es una caida del ciclo.",
          "- El maximo de un conjunto crece con su tamano y las bandas tienen tamanos y disenos de muestreo distintos.",
          "- NO_CONVERGIO sesga hacia abajo la P(KALINA) de las bandas frias;",
          "  p_kalina_si_convergio usa (n - NO_CONVERGIO) como denominador.", ""]
    return "\n".join(l)


def main():
    d = pd.read_csv(DATOS)
    tab = tablas(d)
    os.makedirs(SALIDA, exist_ok=True)
    tab.to_csv(os.path.join(SALIDA, "p6_ciclo_T.csv"), index=False)
    with open(os.path.join(SALIDA, "p6_ciclo_T.md"), "w", encoding="utf-8") as f:
        f.write(markdown(tab))
    print("p6_ciclo_T.csv:", len(tab), "bandas; puntos:", int(tab["n"].sum()))
    print("bandas con menos de", MIN_KALINA, "KALINA:", int((tab["n_kalina"] < MIN_KALINA).sum()))
    print("eta maxima global (muestreada):", round(tab["eta_max"].max(), 3), "%")
    print("eta maxima dentro del rango:", round(tab["eta_max_dentro"].max(), 3), "%")


if __name__ == "__main__":
    main()
