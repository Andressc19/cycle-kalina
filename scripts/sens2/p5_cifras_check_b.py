# -*- coding: utf-8 -*-
"""Sens2 P5 - controles de cifras adicionales (E4, E8, D7, D8, U4): recalculo independiente y subcadena en la conclusion."""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def extra(chk, ev, sub, P):
    import p4_comun as c4
    import s2_calc as C
    e = c4.cargar()
    k4 = e[c4.mascara(e, c4.REF_TOTAL)]
    # E8: regenerador frente a T_fuente (estudio 4, mediana por nivel)
    s = k4[k4["estudio"] == 4]
    lv = sorted(s["T_fuente"].unique())
    lo, hi = s[s["T_fuente"] == lv[0]], s[s["T_fuente"] == lv[-1]]
    v = [float(lo["qreg_qi"].median()), float(hi["qreg_qi"].median()), float(lo["UA_reg"].median()), float(hi["UA_reg"].median())]
    t = ev("E8")
    chk("E", "E8", sub(t, v[0], "%.3f") and sub(t, v[1], "%.3f") and sub(t, v[2], "%.2f") and sub(t, v[3], "%.2f"),
        "estudio 4: Q_reg/Q_i %.3f -> %.3f; UA %.2f -> %.2f" % tuple(v))
    # E4: pinch y UA del regenerador en todos los KALINA
    p5, p95, ua = (float(k4["pinch_reg"].quantile(0.05)), float(k4["pinch_reg"].quantile(0.95)), float(k4["UA_reg"].median()))
    t = ev("E4")
    chk("E", "E4", sub(t, p5, "%.2f") and sub(t, p95, "%.1f") and sub(t, ua, "%.2f"), "pinch P5 %.2f P95 %.1f; UA mediana %.2f" % (p5, p95, ua))
    # U4: frontera del barrido fino de eps_cond (primer nivel KALINA)
    sc = pd.read_csv(P("2026-10-17_sens2_U1", "u1_scan_eps_cond.csv"))
    f = {c: float(sc[(sc["centro"] == c) & (sc["clasificacion"] == "KALINA")]["eps_cond"].min()) for c in ("C1", "C4")}
    chk("U", "U4", sub(ev("U4"), f["C1"], "%.3f") and sub(ev("U4"), f["C4"], "%.3f"),
        "primer eps_cond KALINA: C1 %.3f, C4 %.3f" % (f["C1"], f["C4"]))
    # D8: piso de P_baja en C1 para x_b 0.82, 0.90 y 0.95 (malla P_baja x x_b)
    eta, cls, av, bv = C.malla_clases("C1 Husavik", "B2")
    pisos = []
    for xb in (0.82, 0.90, 0.95):
        j = [i for i, b in enumerate(bv) if abs(b - xb) < 1e-6]
        col = [i for i in range(len(av)) if j and cls[i, j[0]] == "K"]
        pisos.append(float(av[min(col)]) if col else float("nan"))
    chk("D", "D8", all(sub(ev("D8"), x, "%.0f") for x in pisos), "piso P_baja C1 en x_b 0.82/0.90/0.95: %s" % pisos)
    # D7: margenes de una variable en C1 (ultimo nivel KALINA)
    m = C.margenes_ofat()
    r = m[(m["bloque"] == "C1 Husavik") & (m["variable"] == "P_baja")].iloc[0]
    r2 = m[(m["bloque"] == "C1 Husavik") & (m["variable"] == "T_fuente")].iloc[0]
    chk("D", "D7", sub(ev("D7"), r["ult_abajo"], "%.0f") and sub(ev("D7"), r2["ult_abajo"], "%.2f") and sub(ev("D7"), r2["ult_arriba"], "%.2f"),
        "C1 P_baja %.0f; T_fuente %.2f a %.2f" % (r["ult_abajo"], r2["ult_abajo"], r2["ult_arriba"]))


def extra2(chk, ev, sub, P):
    """M6 (mayor eta por banda de T_fuente) y E9 (requisitos por kW neto), recalculados desde los datos."""
    import numpy as np
    d = pd.read_csv(P("2026-10-17_sens2_P2", "p2_dataset_dedup.csv"))
    k = d[d["kalina"] & ~d["fuera_rango"].astype(bool)]
    t6, ok, det = ev("M6"), True, []
    for lo in (340, 360, 380, 400, 420, 440):
        b = k[(k["T_fuente"] >= lo) & (k["T_fuente"] < lo + 20)]
        ok &= sub(t6, float(b["eta_pct"].max()), "%.1f") and sub(t6, len(b), "%d")
        det.append("%d: %.1f (%d)" % (lo, float(b["eta_pct"].max()), len(b)))
    chk("M", "M6", ok, "eta max dentro por banda: " + "; ".join(det))
    import p4_comun as c4
    e = c4.cargar()
    k4 = e[c4.mascara(e, c4.REF_TOTAL) & (e["wnet_mb"] > 0)]
    qi = (k4["Qi_mb"] / k4["wnet_mb"]).to_numpy(float)
    mb = (1.0 / k4["wnet_mb"]).to_numpy(float)
    t9 = ev("E9")
    vals = [float(np.percentile(qi, 5)), float(np.percentile(qi, 50)), float(np.percentile(qi, 95))]
    chk("E", "E9", all(sub(t9, v, "%.1f") for v in vals) and sub(t9, float(np.percentile(mb, 5)), "%.3f") and sub(t9, len(k4), "%d"),
        "Q_i por kW neto P5/P50/P95 = %.1f/%.1f/%.1f; n = %d" % (vals[0], vals[1], vals[2], len(k4)))


def extra3(chk, ev, sub, P):
    """L2: fraccion de CORREGIBLE a una variable de un KALINA, global y por tipo de diseño (recalculada de p2_distancia y el dataset)."""
    dist = pd.read_csv(P("2026-10-17_sens2_P2", "p2_distancia.csv"))
    est = pd.read_csv(P("2026-10-17_sens2_P2", "p2_dataset_dedup.csv"))[["id_punto", "estudio"]]
    j = dist.merge(est, on="id_punto", how="left")
    una = j["nvars_diff"] == 1
    lhs = j["estudio"].isin([3, 14])
    v = [100 * float(una.mean()), 100 * float(una[~lhs].mean()), 100 * float(una[lhs].mean())]
    t = ev("L2")
    chk("L", "L2c", all(sub(t, x, "%.0f") for x in v), "a una variable: global %.1f, barridos y mallas %.1f, LHS %.1f" % tuple(v))


def extra4(chk, ev, sub, P):
    """L5 y M5 (ronda 8): tasa de la regla en las dummy y familia global (BH propio) y p de Mann-Whitney de M5 recalculados."""
    import numpy as np
    from scipy.stats import mannwhitneyu
    from p5_cifras_check_c import bh
    n = pd.read_csv(P("2026-10-18_sens2_F1", "p6_nulo_perm.csv"))
    n = n[n["caja"] == "no"].copy()
    n["q"] = np.nan
    for _, ix in n.groupby(["bloque", "respuesta"]).groups.items():
        n.loc[ix, "q"] = bh(n.loc[ix, "p_perm"])
    s = n[n["q"] < 0.05].groupby(["bloque", "respuesta", "variable", "tipo"]).size()
    marc = int((s[s.index.get_level_values("tipo") == "dummy"] >= 2).sum())
    nd = n[n["tipo"] == "dummy"].groupby(["bloque", "respuesta", "variable"]).ngroups
    n["qg"] = bh(n["p_perm"])                      # una sola familia con todas las pruebas, reales y dummy
    r = n[n["tipo"] == "real"]
    sg = r[r["qg"] < 0.05].groupby(["bloque", "respuesta", "variable"]).size()
    t = ev("L5")
    chk("L", "L5c", sub(t, "%d de %d variables dummy" % (marc, nd), "%s") and sub(t, int((sg >= 2).sum()), "%d"),
        "dummy marcadas %d de %d; reales distinguibles con una sola familia (reales y dummy mezcladas): %d" % (marc, nd, int((sg >= 2).sum())))
