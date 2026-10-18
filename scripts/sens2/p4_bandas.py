# -*- coding: utf-8 -*-
"""Sens2 P4 - Paso 4: bandas de diseno por relacion de presiones (rp).

Bandas de rp = [1,1.5), [1.5,2), [2,3), [3,4), [4,6), [6,10]. Por banda y centro,
n de KALINA (total), eta mediana (P10-P90), y medianas de dh_turb, q4, Wt/m_b,
pinch_reg y UA_reg. Responde a que rp la turbina entrega mas dh_turb y a cual mas
eta. Salidas: p4_bandas.csv y p4_bandas.md.

La ultima banda llega hasta 10 exclusivo; los pocos KALINA con rp >= 10 se
informan aparte (no entran en ninguna banda, igual que en el control de P4).
"""
import os

import numpy as np
import pandas as pd

import p4_comun as c

SALIDA = c.SALIDA
EDGES = [1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 10.0]
ETIQUETAS = ["[1, 1.5)", "[1.5, 2)", "[2, 3)", "[3, 4)", "[4, 6)", "[6, 10)"]
MED = ["dh_turb", "q4", "Wt_mb", "pinch_reg", "UA_reg"]
COLS = ["centro", "banda", "rp_lo", "rp_hi", "n", "eta_p50", "eta_p10", "eta_p90",
        "dh_p50", "q4_p50", "wt_p50", "pinch_p50", "ua_p50"]


def med(x):
    v = np.asarray(pd.to_numeric(pd.Series(x), errors="coerce"), float)
    v = v[np.isfinite(v)]
    return float(np.median(v)) if len(v) else np.nan


def banda_de(rp):
    return pd.cut(rp, bins=EDGES, right=False, labels=ETIQUETAS)


def filas_centro(kal, centro):
    b = banda_de(kal["rp"])
    filas = []
    for i, et in enumerate(ETIQUETAS):
        s = kal[b == et]
        if len(s) == 0:
            filas.append([centro, et, EDGES[i], EDGES[i + 1], 0] + [np.nan] * 8)
            continue
        e = s["eta_pct"].to_numpy(float)
        e = e[np.isfinite(e)]
        p10, p90 = (float(np.percentile(e, 10)), float(np.percentile(e, 90))) \
            if len(e) else (np.nan, np.nan)
        filas.append([centro, et, EDGES[i], EDGES[i + 1], len(s), med(e),
                      p10, p90, med(s["dh_turb"]), med(s["q4"]),
                      med(s["Wt_mb"]), med(s["pinch_reg"]), med(s["UA_reg"])])
    return filas


def markdown(tabla, fuera):
    l = ["# Sens2 P4 - Paso 4: bandas de diseno por rp", "",
         "KALINA (total) por banda de rp y centro. eta en %; P10-P90 entre parentesis;",
         "el resto son medianas. La ultima banda es [6, 10).", ""]
    for centro in tabla["centro"].unique():
        s = tabla[tabla["centro"] == centro]
        l += ["## %s" % centro, ""]
        l.append(c.tabla_md(["banda", "n", "eta P50 (P10-P90)", "dh_turb P50",
                             "q4 P50", "Wt/m_b P50", "pinch P50", "UA P50"],
                            [[r["banda"], r["n"],
                              "%s (%s-%s)" % (c.fmt(r["eta_p50"], 3),
                                              c.fmt(r["eta_p10"], 3),
                                              c.fmt(r["eta_p90"], 3)),
                              c.fmt(r["dh_p50"]), c.fmt(r["q4_p50"]),
                              c.fmt(r["wt_p50"]), c.fmt(r["pinch_p50"]),
                              c.fmt(r["ua_p50"])] for _, r in s.iterrows()]))
        l.append("")
    g = tabla[tabla["centro"] == "todos"]
    val = g[g["n"] > 0]
    bdh = val.loc[val["dh_p50"].idxmax()] if len(val) else None
    beta = val.loc[val["eta_p50"].idxmax()] if len(val) else None
    l += ["## Respuesta", ""]
    if bdh is not None:
        l.append("- La turbina entrega el mayor dh_turb mediano en la banda %s "
                 "(%.4g kJ/kg)." % (bdh["banda"], bdh["dh_p50"]))
        l.append("- La mayor eta mediana aparece en la banda %s (%.3f %%)." % (
            beta["banda"], beta["eta_p50"]))
    l += ["", "KALINA con rp valida fuera de las bandas (rp >= 10): %d." % fuera,
          "Se informa aparte; no entra en ninguna banda.", ""]
    return "\n".join(l)


def main():
    d = c.cargar()
    kal = d[c.mask_total(d)]
    filas = []
    for centro in c.grupos(d) + ["todos"]:
        s = kal if centro == "todos" else kal[kal["centro"] == centro]
        filas += filas_centro(s, centro)
    tabla = pd.DataFrame(filas, columns=COLS)
    fuera = int((kal["rp"] >= 10.0).sum())
    os.makedirs(SALIDA, exist_ok=True)
    tabla.to_csv(os.path.join(SALIDA, "p4_bandas.csv"), index=False)
    c.guardar("p4_bandas.md", markdown(tabla, fuera))
    print("p4_bandas.csv:", len(tabla), "filas | KALINA rp>=10:", fuera)
    g = tabla[tabla["centro"] == "todos"]
    b = g[g["n"] > 0]
    print("banda con mayor dh_turb:", b.loc[b["dh_p50"].idxmax()]["banda"])
    print("banda con mayor eta:", b.loc[b["eta_p50"].idxmax()]["banda"])
    print(b[["banda", "n", "eta_p50", "dh_p50"]].to_string(index=False))


if __name__ == "__main__":
    main()
