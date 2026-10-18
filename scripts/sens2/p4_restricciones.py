# -*- coding: utf-8 -*-
"""Sens2 P4 - Paso 3: restricciones activas y cruces.

Para KALINA (total) por centro: fraccion con q4 < 0.90 (deberia ser 0 por la
restriccion O1), fraccion con pinch_reg <= 0 (cruce del regenerador) y fraccion
con pinch_reg en los cuartiles inferiores (<= P25 y <= P50 del propio centro),
mas la distribucion de pinch_reg (P5, P50, P95). Entre los CORREGIBLE: lo mismo
mas la fraccion con (T9 - T_sumidero) por debajo de la mediana de los KALINA
(sintoma de O2). Tabla comparativa y salidas p4_restricciones.csv/.md.

Los estados T_e5, T_e6, T_e1, T_e10 y T_e9 existen en KALINA y en CORREGIBLE, de
modo que pinch_reg y T9 - T_sumidero se pueden derivar en ambos grupos.
"""
import os

import numpy as np
import pandas as pd

import p4_comun as c

SALIDA = c.SALIDA
COLS = ["centro", "grupo", "n", "frac_q4_lt_090", "frac_pinch_le0", "thr_p25",
        "frac_pinch_le_p25", "thr_p50", "frac_pinch_le_p50", "pinch_p5",
        "pinch_p50", "pinch_p95", "med_T9_sub", "frac_T9_sub_med"]


def medidas(s, K, p25, p50):
    """Fracciones y distribucion de pinch_reg; T9_sub = aprox_cond_sal."""
    n = len(s)
    if n == 0:
        return dict(n=0, fq4=np.nan, f0=np.nan, fp25=np.nan, fp50=np.nan,
                    p5=np.nan, m50=np.nan, p95=np.nan, fv=np.nan)
    pinch = s["pinch_reg"].to_numpy(float)
    fin = np.isfinite(pinch)
    fq4 = float((s["q4"] < 0.90).mean()) if s["q4"].notna().any() else np.nan
    f0 = float((pinch[fin] <= 0).mean()) if fin.any() else np.nan
    fp25 = float((pinch[fin] <= p25).mean()) if fin.any() else np.nan
    fp50 = float((pinch[fin] <= p50).mean()) if fin.any() else np.nan
    if fin.any():
        p5, m50, p95 = (float(np.percentile(pinch, q)) for q in (5, 50, 95))
    else:
        p5 = m50 = p95 = np.nan
    v = s["aprox_cond_sal"].to_numpy(float)
    fv = float((v < K).mean()) if np.isfinite(v).any() else np.nan
    return dict(n=n, fq4=fq4, f0=f0, fp25=fp25, fp50=fp50, p5=p5, m50=m50,
                p95=p95, fv=fv)


def filas_centro(d, centro):
    s = d if centro == "todos" else d[d["centro"] == centro]
    kal = s[c.mask_total(s)]
    cor = s[s["clasificacion"] == "CORREGIBLE"]
    pk = kal["pinch_reg"].to_numpy(float)
    pk = pk[np.isfinite(pk)]
    p25 = float(np.percentile(pk, 25)) if len(pk) else np.nan
    p50 = float(np.median(pk)) if len(pk) else np.nan
    K = (float(np.nanmedian(kal["aprox_cond_sal"].to_numpy(float)))
         if kal["aprox_cond_sal"].notna().any() else np.nan)
    a = medidas(kal, K, p25, p50)
    b = medidas(cor, K, p25, p50)
    filas = []
    filas.append([centro, "KALINA (total)", a["n"], a["fq4"], a["f0"], p25, a["fp25"],
                  p50, a["fp50"], a["p5"], a["m50"], a["p95"], K, np.nan])
    filas.append([centro, "CORREGIBLE", b["n"], b["fq4"], b["f0"], p25, b["fp25"],
                  p50, b["fp50"], b["p5"], b["m50"], b["p95"], K, b["fv"]])
    return filas


def markdown(tabla):
    l = ["# Sens2 P4 - Paso 3: restricciones activas y cruces", "",
         "Sobre KALINA (total) y CORREGIBLE. `frac_pinch_le_p25` y `frac_pinch_le_p50`",
         "usan los cuartiles del propio centro calculados sobre su KALINA (total).",
         "`frac_T9_sub_med` = fraccion con (T9 - T_sumidero) por debajo de la mediana",
         "de los KALINA del centro (sintoma de O2); para los KALINA es la referencia.",
         "", "## Comparativa KALINA frente a CORREGIBLE", "",
         c.tabla_md(["centro", "grupo", "n", "q4<0.90", "pinch<=0", "pinch<=P25",
                     "pinch<=P50", "P5 pinch", "P50 pinch", "P95 pinch",
                     "med T9-Tsum", "T9-Tsum<med"],
                    [[r["centro"], r["grupo"], r["n"], c.fmt(r["frac_q4_lt_090"]),
                      c.fmt(r["frac_pinch_le0"]), c.fmt(r["frac_pinch_le_p25"]),
                      c.fmt(r["frac_pinch_le_p50"]), c.fmt(r["pinch_p5"]),
                      c.fmt(r["pinch_p50"]), c.fmt(r["pinch_p95"]),
                      c.fmt(r["med_T9_sub"]), c.fmt(r["frac_T9_sub_med"])]
                     for _, r in tabla.iterrows()]), ""]
    return "\n".join(l)


def main():
    d = c.cargar()
    filas = []
    for centro in c.grupos(d) + ["todos"]:
        filas += filas_centro(d, centro)
    tabla = pd.DataFrame(filas, columns=COLS)
    os.makedirs(SALIDA, exist_ok=True)
    tabla.to_csv(os.path.join(SALIDA, "p4_restricciones.csv"), index=False)
    c.guardar("p4_restricciones.md", markdown(tabla))
    print("p4_restricciones.csv:", len(tabla), "filas")
    for _, r in tabla.iterrows():
        print("  %-28s %-15s n=%4d q4<.9=%s pinch<=0=%s pin<=P25=%s T9<med=%s" % (
            r["centro"], r["grupo"], r["n"], c.fmt(r["frac_q4_lt_090"]),
            c.fmt(r["frac_pinch_le0"]), c.fmt(r["frac_pinch_le_p25"]),
            c.fmt(r["frac_T9_sub_med"])))


if __name__ == "__main__":
    main()
