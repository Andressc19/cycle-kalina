# -*- coding: utf-8 -*-
"""Sens2 P5 - controles extra (ronda 6): cifras recalculadas con pandas desde p2_dataset_dedup.csv.

Cada control compara una cifra recalculada (con el formato del texto) con la subcadena de la
conclusion indicada. Usa solo pandas/numpy (sin importar otros modulos del proyecto). No modifica
conclusiones ni CSV: si una cifra no coincide, el control sale FALLA y se reporta tal cual.
"""
import numpy as np
import pandas as pd

BLOQUES = ["C1 Husavik", "C2 ancla A*", "C3 caliente 150 C", "C4 frio 110 C"]


def extra6(chk, ev, sub, P):
    d = pd.read_csv(P("2026-10-17_sens2_P2", "p2_dataset_dedup.csv"))
    k = d[d["kalina"] & d["eta_pct"].notna()]
    kl = k[k["estudio"].isin([3, 14])]
    cor = d[d["clasificacion"] == "CORREGIBLE"]
    cl = cor[cor["estudio"].isin([3, 14])]
    fuera = k["fuera_rango"].astype(bool)

    # E1: envolventes de la turbina (KALINA total) y del 10 % de mayor eta
    t = ev("E1")
    rp = k["rp"].quantile([0.05, 0.5, 0.95]).to_numpy(float)
    dh = k["dh_turb"].quantile([0.05, 0.5, 0.95]).to_numpy(float)
    chk("E", "E1rp", sub(t, rp[0], "%.2f") and sub(t, rp[1], "%.2f") and sub(t, rp[2], "%.2f"),
        "r_P P5/P50/P95 = %.2f/%.2f/%.2f" % tuple(rp))
    chk("E", "E1dh", sub(t, dh[0], "%.0f") and sub(t, dh[1], "%.1f") and sub(t, dh[2], "%.0f"),
        "dh_turb P5/P50/P95 = %.1f/%.1f/%.1f kJ/kg" % tuple(dh))
    top = k[k["eta_pct"] >= k["eta_pct"].quantile(0.9)]
    rt = top["rp"].quantile([0.05, 0.95]).to_numpy(float)
    ht = top["dh_turb"].quantile([0.05, 0.95]).to_numpy(float)
    chk("E", "E1top_rp", sub(t, rt[0], "%.2f") and sub(t, rt[1], "%.2f"),
        "10 pct mayor eta (n=%d): r_P P5/P95 = %.2f/%.2f" % (len(top), rt[0], rt[1]))
    chk("E", "E1top_dh", sub(t, ht[0], "%.0f") and sub(t, ht[1], "%.0f"),
        "10 pct mayor eta: dh P5/P95 = %.1f/%.1f kJ/kg" % (ht[0], ht[1]))

    # E2: pendiente y R2 de dh_turb sobre rp en el muestreo LHS; medianas por banda de rp
    t = ev("E2")
    x, y = kl["rp"].to_numpy(float), kl["dh_turb"].to_numpy(float)
    pend = float(np.polyfit(x, y, 1)[0])
    r2 = float(np.corrcoef(x, y)[0, 1] ** 2)
    chk("E", "E2reg", sub(t, pend, "%.1f") and sub(t, r2, "%.2f") and sub(t, len(kl), "%d"),
        "pendiente = %.1f; R2 = %.2f; n = %d (LHS)" % (pend, r2, len(kl)))
    b1 = k[(k["rp"] >= 1) & (k["rp"] < 1.5)]
    b6 = k[(k["rp"] >= 6) & (k["rp"] < 10)]
    chk("E", "E2dh1", sub(t, b1["dh_turb"].median(), "%.0f"),
        "dh mediana [1,1.5) = %.2f kJ/kg (texto: 47)" % b1["dh_turb"].median())
    chk("E", "E2dh6", sub(t, b6["dh_turb"].median(), "%.0f"),
        "dh mediana [6,10) = %.2f kJ/kg (texto: 236)" % b6["dh_turb"].median())
    chk("E", "E2eta1", sub(t, b1["eta_pct"].median(), "%.1f"),
        "eta mediana [1,1.5) = %.3f %% (texto: 2.5)" % b1["eta_pct"].median())
    chk("E", "E2eta6", sub(t, b6["eta_pct"].median(), "%.1f"),
        "eta mediana [6,10) = %.3f %% (texto: 10.1)" % b6["eta_pct"].median())

    # E3: titulo de salida q4 en KALINA, 10 pct de mayor eta y margen 0.90
    t = ev("E3")
    q4 = top["q4"]
    chk("E", "E3min", sub(t, k["q4"].min(), "%.4f"), "q4 minimo KALINA = %.4f" % k["q4"].min())
    chk("E", "E3med", sub(t, k["q4"].median(), "%.3f"), "q4 mediana KALINA = %.4f" % k["q4"].median())
    chk("E", "E3top", sub(t, q4.quantile(0.05), "%.4f") and sub(t, q4.median(), "%.4f"),
        "q4 top10 P5/P50 = %.4f/%.4f" % (q4.quantile(0.05), q4.median()))
    ti = ev("E3", "implicacion")                       # los margenes estan en la implicacion
    mg = q4 - 0.90
    chk("E", "E3marg", sub(ti, mg.median(), "%.3f") and sub(ti, mg.max(), "%.3f") and sub(ti, (mg <= 0.01).mean() * 100, "%.0f %%"),
        "margen top10 mediana %.4f, max %.4f, <=0.01 %.2f %%" % (mg.median(), mg.max(), (mg <= 0.01).mean() * 100))
    mp = d[d["id_punto"].isin(["C1-B3-0127", "N1-T170-14", "N10-C3-0016"])]["q4"] - 0.90
    chk("E", "E3marg_pt", sub(ti, mp.min(), "%.3f") and sub(ti, mp.max(), "%.3f"),
        "margen M1/M2 min %.4f, max %.4f" % (mp.min(), mp.max()))

    # E6: Q_i por kg/s de m_b, mediana de KALINA
    qi = float((k["Qi"] / k["m_b"]).median())
    chk("E", "E6med", sub(ev("E6"), qi, "%.0f"), "Q_i/m_b mediana KALINA = %.2f (790)" % qi)

    # M1: maximos dentro y fuera del rango; mediana y P90 de eta en KALINA
    t = ev("M1")
    den, fue = k[~fuera]["eta_pct"].max(), k[fuera]["eta_pct"].max()
    chk("M", "M1txt", sub(t, fue, "%.2f") and sub(t, den, "%.2f"),
        "eta max fuera = %.2f, dentro = %.2f" % (fue, den))
    chk("M", "M1med", sub(t, k["eta_pct"].median(), "%.1f") and sub(t, k["eta_pct"].quantile(0.9), "%.1f"),
        "eta mediana = %.2f, P90 = %.2f" % (k["eta_pct"].median(), k["eta_pct"].quantile(0.9)))

    # M2, M3: puntos concretos del texto (eta y W_net por kg/s de m_b)
    p = d.set_index("id_punto")
    chk("M", "M2txt", sub(ev("M2"), p.loc["C1-B3-0127", "eta_pct"], "%.2f"),
        "C1-B3-0127 eta = %.2f" % p.loc["C1-B3-0127", "eta_pct"])
    t = ev("M3")
    chk("M", "M3txt", sub(t, p.loc["C1-B5-0228", "eta_pct"], "%.2f") and sub(t, p.loc["C1-B5-0228", "wnet_mb"], "%.1f"),
        "C1-B5-0228 eta = %.2f; W_net/m_b = %.1f" % (p.loc["C1-B5-0228", "eta_pct"], p.loc["C1-B5-0228", "wnet_mb"]))

    # M4: maximos KALINA de los bloques C4 y C2 (dentro y fuera del rango)
    t = ev("M4")
    c4 = k[k["centro"].str.startswith("C4")]
    c2 = k[k["centro"].str.startswith("C2")]
    chk("M", "M4c4", sub(t, c4["eta_pct"].max(), "%.2f"), "C4 max eta KALINA = %.3f" % c4["eta_pct"].max())
    chk("M", "M4c2", sub(t, c2[~c2["fuera_rango"]]["eta_pct"].max(), "%.2f")
        and sub(t, c2[c2["fuera_rango"]]["eta_pct"].max(), "%.2f"),
        "C2 max dentro = %.3f; fuera = %.3f" % (c2[~c2["fuera_rango"]]["eta_pct"].max(), c2[c2["fuera_rango"]]["eta_pct"].max()))

    # F6: medianas sin parear (W_net/m_b, eta) y diferencias
    t = ev("F6")
    cm, km = cor["wnet_mb"].median(), k["wnet_mb"].median()
    chk("F", "F6w", sub(t, cm, "%.1f") and sub(t, km, "%.1f") and sub(t, cm - km, "%+.1f"),
        "W_net/m_b medianas COR=%.2f KAL=%.2f dif=%+.2f" % (cm, km, cm - km))
    ce, ke = cor["eta_pct"].median(), k["eta_pct"].median()
    chk("F", "F6eta", sub(t, ce - ke, "%+.2f"), "eta dif COR-KAL = %+.3f" % (ce - ke))
    dl = cl["eta_pct"].median() - kl["eta_pct"].median()
    chk("F", "F6lhs", sub(t, dl, "%+.1f"), "eta dif LHS = %+.3f" % dl)
    difs = [cor[cor["centro"] == b]["eta_pct"].median() - k[k["centro"] == b]["eta_pct"].median() for b in BLOQUES]
    chk("F", "F6bloques", sub(t, min(difs), "%+.1f") and sub(t, max(difs), "%+.1f"),
        "dif por bloque min %+.3f max %+.3f" % (min(difs), max(difs)))
    sc = cor[cor["centro"].str.startswith("Sin centro")]["eta_pct"].median() - \
        k[k["centro"].str.startswith("Sin centro")]["eta_pct"].median()
    chk("F", "F6sinc", sub(t, sc, "%+.1f"), "dif sin centro = %+.3f" % sc)

    # L1, L4, L5: conteos del conjunto de datos
    chk("L", "L1n", sub(ev("L1"), len(cor), "%d"), "CORREGIBLE en dedup = %d" % len(cor))
    fr = 100.0 * float(fuera.mean())
    chk("L", "L4pct", sub(ev("L4"), fr, "%.0f %%"), "KALINA fuera de rango = %.2f %%" % fr)
    chk("L", "L4n", sub(ev("L4"), len(k), "%d"), "KALINA con eta = %d" % len(k))
    nc = int((d["clasificacion"] == "NO_CONVERGIO").sum())
    chk("L", "L5nc", "%d de %d" % (nc, len(d)) in ev("L5"), "NO_CONVERGIO %d de %d puntos" % (nc, len(d)))
