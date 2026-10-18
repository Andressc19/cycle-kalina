# -*- coding: utf-8 -*-
"""Sens2 - p5_hechos: cifras que citan las conclusiones, calculadas desde los CSV y los datos de Sensibilidad 1.

`hechos()` devuelve un diccionario {clave: valor}. Las plantillas de `p5_conclusiones_base.csv` usan
`{{clave}}` o `{{clave|formato}}` (formato de Python, p. ej. `.2f`); `p5_generar.py` las sustituye. Ninguna cifra
de una conclusion con marcador se escribe a mano.
"""
import os
import sys

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))
R = os.path.join(RAIZ, "resultados")
U1 = os.path.join(R, "2026-10-17_sens2_U1")
R1 = os.path.join(R, "2026-10-18_sens2_R1")
P2 = os.path.join(R, "2026-10-17_sens2_P2")
CEN = {"C1": "C1 Husavik", "C2": "C2 ancla A*", "C3": "C3 caliente 150 C", "C4": "C4 frio 110 C"}


def _u1(h):
    r = pd.read_csv(os.path.join(U1, "u1_resumen.csv"))
    for esc, tag in (("U1Ap", "u1p"), ("U1B", "u1b"), ("U1C", "u1c"), ("U1A", "u1a")):
        for _, x in r[r["escenario"] == esc].iterrows():
            for col in ("n", "n_kalina", "p_kalina", "p_lo", "p_hi", "p_eta_1pp", "eta_p5", "eta_p50", "eta_p95",
                        "eta_nominal", "p_m1", "p_m3", "p_m5"):
                h["%s.%s.%s" % (tag, x["centro"], col)] = float(x[col])
    for c in CEN:
        for t in ("u1p", "u1b", "u1c"):
            h["%s.%s.pct" % (t, c)] = 100 * h["%s.%s.p_kalina" % (t, c)]
        h["u1p.%s.pierde" % c] = 100 * (1 - h["u1p.%s.p_kalina" % c])
        p, n = h["u1p.%s.p_kalina" % c], h["u1a.%s.n" % c]
        h["u1a.%s.ee" % c] = float(np.sqrt(p * (1 - p) / n))     # error tipico de P con un lote de 48
    h["u1a.ee_min"] = min(h["u1a.%s.ee" % c] for c in CEN if h["u1p.%s.p_kalina" % c] < 0.999)
    h["u1a.ee_max"] = max(h["u1a.%s.ee" % c] for c in CEN)


def _mo2(h):
    import x1_cargar as X
    d = X.cargar_todo()
    k = d[(d["clasificacion"] == "KALINA") & d["m_O2"].notna()]
    h["mo2.n"] = float(len(k))
    for t in (1, 3, 5):
        h["mo2.todos.p%d" % t] = 100 * float((k["m_O2"] < t).mean())
        s = k[k["centro"].astype(str).str.startswith("C1")]
        h["mo2.C1.p%d" % t] = 100 * float((s["m_O2"] < t).mean())
    for clave, pid in (("n1t170", "N1-T170-14"), ("n10c3", "N10-C3-0016"), ("c1b3", "C1-B3-0127"), ("n7bc4", "N7B-C4-B1-045"), ("c2lhs", "C2-LHS-0005")):
        h["mo2.%s" % clave] = float(d[d["id_punto"] == pid]["m_O2"].iloc[0])
    b = d[d["estudio"].isin([1, 10]) & (d["variable"] == "base") & d["centro"].astype(str).str.startswith("C1")].iloc[0]
    h["c1.base.eta"], h["c1.base.clase"], h["c1.base.eps_cond"] = float(b["eta_pct"]), str(b["clasificacion"]), float(b["eps_cond"])


def _nc(h):
    from s2_cargar import dataset_dedup
    s = dataset_dedup()
    x = s[s["estudio"].isin([3, 14])]
    for c in CEN:
        g = x[x["centro"] == CEN[c]]
        lo = g[g["T_fuente"] <= g["T_fuente"].quantile(0.25)]
        h["nc.%s.n" % c] = float(len(lo))
        h["nc.%s.nc" % c] = float((lo["clasificacion"] == "NO_CONVERGIO").sum())
    h["eta.mediana.lhs"] = float(s[s["kalina"] & s["estudio"].isin([3, 14])]["eta_pct"].median())
    h["nc.total"] = float((s["clasificacion"] == "NO_CONVERGIO").sum())
    h["nc.n"] = float(len(s))
    h["m2.mejor.eta"] = float(s[s["id_punto"] == "C1-B3-0127"]["eta_pct"].iloc[0])
    h["m2.ganancia"] = h["m2.mejor.eta"] - h["c1.base.eta"]


def _f6(h):
    c = pd.read_csv(os.path.join(P2, "p2_comparacion.csv"))
    e = c[(c["variable"] == "eta_pct") & (c["ref"] == "KALINA (total)")]
    t = e[(e["ambito"] == "todos los puntos") & (e["centro"] == "todos")].iloc[0]
    h["f6.todos.dif"], h["f6.todos.lo"], h["f6.todos.hi"] = float(t["dif_mediana"]), float(t["ic_lo"]), float(t["ic_hi"])
    h["f6.cor"], h["f6.kal"] = float(t["med_cor"]), float(t["med_kal"])
    b = e[(e["ambito"] == "todos los puntos") & e["centro"].isin(CEN.values())]
    h["f6.bloque.min"], h["f6.bloque.max"] = float(b["dif_mediana"].min()), float(b["dif_mediana"].max())
    sc = e[(e["ambito"] == "todos los puntos") & (e["centro"].str.startswith("Sin"))].iloc[0]
    h["f6.sincentro.dif"] = float(sc["dif_mediana"])
    l = e[(e["ambito"].str.startswith("LHS")) & (e["centro"] == "todos")].iloc[0]
    h["f6.lhs.dif"], h["f6.lhs.lo"], h["f6.lhs.hi"] = float(l["dif_mediana"]), float(l["ic_lo"]), float(l["ic_hi"])
    d = pd.read_csv(os.path.join(P2, "p2_distancia_resumen.csv"))
    p = d[(d["seccion"] == "eta") & (d["centro"] == "todos")]
    if len(p):
        x = p.iloc[0]
        h["l2.pareado"], h["l2.n"] = float(x["mediana"]), float(x["n"])
        for kv in str(x["extra"]).split(";"):
            k, v = kv.split("=")
            h["l2." + k] = float(v)


def _r1(h):
    a = pd.read_csv(os.path.join(R1, "r2_acuerdo_agregado.csv"))
    for i, tag in ((0, "r1"), (1, "r2")):
        for col in a.columns[1:]:
            if pd.notna(a.iloc[i][col]):
                h["%s.agr.%s" % (tag, col)] = float(a.iloc[i][col])
    v = pd.read_csv(os.path.join(R1, "r2_vecinos_resumen.csv")).set_index("grupo")
    for g, tag in (("todos", "todos"), ("vecino cercano (L1 <= P25)", "cerca"), ("vecino lejano (L1 > P75)", "lejos")):
        h["vec.%s.ex" % tag], h["vec.%s.may" % tag] = float(v.loc[g, "exactitud"]), float(v.loc[g, "exactitud_clase_mayoritaria"])
    p = pd.read_csv(os.path.join(R1, "r2_vecinos_puntos.csv"))
    h["vec.p25"], h["vec.p75"] = float(p["dist_vecino"].quantile(0.25)), float(p["dist_vecino"].quantile(0.75))
    r = pd.read_csv(os.path.join(R1, "r1_rangos_fraccion.csv"))
    t = r[r["variable"] == "(las 10 a la vez)"].set_index("centro")
    for c, nom in CEN.items():
        h["l8.%s.n" % c], h["l8.%s.dentro" % c], h["l8.%s.frac" % c] = float(t.loc[nom, "n"]), float(t.loc[nom, "n_dentro"]), 100 * float(t.loc[nom, "fraccion"])
    h["l8.n"], h["l8.dentro"] = float(t["n"].sum()), float(t["n_dentro"].sum())
    h["l8.frac"] = 100 * h["l8.dentro"] / h["l8.n"]
    f = pd.read_csv(os.path.join(R1, "r1_fuera_de_rango_sens2.csv"))
    h["l8.fuera.puntos"] = float(f["id_punto"].nunique())
    h["l8.c2.n"] = float(f[f["variable"] == "T_fuente"]["id_punto"].nunique())
    h["l8.c2.tmin"], h["l8.c2.tmax"], h["l8.c2.lim"] = (float(f[f["variable"] == "T_fuente"]["valor"].min()),
                                                        float(f[f["variable"] == "T_fuente"]["valor"].max()),
                                                        float(f[f["variable"] == "T_fuente"]["min_kalina"].iloc[0]))
    e = f[f["variable"] == "eps_cond"]
    h["l8.c3.n"], h["l8.c3.val"], h["l8.c3.lim"] = float(e["id_punto"].nunique()), float(e["valor"].iloc[0]), float(e["min_kalina"].iloc[0])


def _rob(h):
    r = pd.read_csv(os.path.join(P2, "p2_robustez.csv"))
    x = r[(r["seccion"] == "comparacion") & (r["centro"] == "todos") & (r["clave"] == "dist_frontera")].iloc[0]
    kv = dict(t.split("=") for t in str(x["txt"]).split(";"))
    h["m5.n_top"], h["m5.med_top"], h["m5.med_resto"] = float(kv["n_top"]), float(kv["med_top"]), float(kv["med_resto"])
    u = r[(r["seccion"] == "univariado_top") & (r["centro"] == "todos")]
    h["m5.una_variable"] = float(u["valor"].sum())
    h["m5.p_baja"] = float(u[u["subclave"] == "P_baja"]["valor"].iloc[0])


def _f1(h):
    F1 = os.path.join(R, "2026-10-18_sens2_F1")
    key = {"E3 C1 Husavik": "C1", "E3 C2 ancla A*": "C2", "E14 C3 caliente 150 C": "C3", "E14 C4 frio 110 C": "C4"}
    cu = pd.read_csv(os.path.join(F1, "p6_nc_cuartiles.csv"))
    for _, x in cu[cu["cuartil_T_fuente"] == 1].iterrows():
        c = key[x["bloque"]]
        h["ncq1.%s.n" % c], h["ncq1.%s.nc" % c] = float(x["n"]), float(x["NO_CONVERGIO"])
        h["ncq1.%s.p0" % c], h["ncq1.%s.pconv" % c] = float(x["p_kalina_nc_cero"]), float(x["p_kalina_si_convergio"])
        h["ncq1.%s.lo" % c], h["ncq1.%s.hi" % c] = float(x["ic_lo"]), float(x["ic_hi"])
        for sufijo in ("p0", "pconv", "lo", "hi"):
            h["ncq1.%s.%s_pct" % (c, sufijo)] = 100 * h["ncq1.%s.%s" % (c, sufijo)]
    cd = pd.read_csv(os.path.join(F1, "p6_nc_conductores.csv"))
    top = cd.sort_values("ks_nc_vs_resto", ascending=False).groupby("bloque").head(1)
    h["ncd.ks.min"], h["ncd.ks.max"] = float(top["ks_nc_vs_resto"].min()), float(top["ks_nc_vs_resto"].max())
    h["ncd.todos_T_fuente"] = float((top["variable"] == "T_fuente").sum())
    t = pd.read_csv(os.path.join(F1, "p6_nc_top3.csv"))
    for _, x in t.iterrows():
        c = key[x["bloque"]]
        h["nctop.%s.base" % c], h["nctop.%s.sin" % c] = str(x["top3_nc_como_no_kalina"]), str(x["top3_sin_nc"])
        h["nctop.%s.igual_sin" % c], h["nctop.%s.igual_uno" % c] = str(x["igual_sin_nc"]), str(x["igual_nc_como_kalina"])


def _pareado(h):
    F1 = os.path.join(R, "2026-10-18_sens2_F1")
    t = pd.read_csv(os.path.join(F1, "p6_pareado_dist.csv"))
    x = t[(t["variante"] == "mismo_centro") & (t["grupo"] == "todos") & (t["calculo"] == "tramo L1 0.0 a 0.2")].iloc[0]
    h["par.cerca.med"], h["par.cerca.lo"], h["par.cerca.hi"], h["par.cerca.n"] = (float(x["estimador"]), float(x["ic_lo"]),
                                                                              float(x["ic_hi"]), float(x["n"]))
    y = t[(t["variante"] == "mismo_centro") & (t["grupo"] == "todos") & (t["calculo"] == "tramo L1 0.5 a mas")].iloc[0]
    h["par.lejos.med"], h["par.lejos.n"] = float(y["estimador"]), float(y["n"])
    z = t[(t["variante"] == "mismo_centro") & (t["grupo"] == "LHS") & (t["calculo"] == "ajuste")].iloc[0]
    h["par.lhs.n"] = float(z["n"])
    q = pd.read_csv(os.path.join(F1, "p6_pareado.csv"))
    g = q[(q["variante"] == "mismo_centro") & (q["grupo"] == "LHS") & (q["variable"] == "d_eta")].iloc[0]
    h["par.lhs.med"] = float(g["mediana"])
    g = q[(q["variante"] == "mismo_centro") & (q["grupo"] == "otros") & (q["variable"] == "d_eta")].iloc[0]
    h["par.otros.med"] = float(g["mediana"])


def _f1b(h):
    F1 = os.path.join(R, "2026-10-18_sens2_F1")
    cv = pd.read_csv(os.path.join(F1, "p6_superficies_cv.csv"))
    h["cv.r2cv.min"], h["cv.r2cv.max"] = float(cv["r2_cv"].min()), float(cv["r2_cv"].max())
    h["cv.r2.min"], h["cv.r2.max"] = float(cv["r2"].min()), float(cv["r2"].max())
    h["cv.caida.max"] = float((cv["r2"] - cv["r2_cv"]).max())
    h["cv.max_en_C"] = float((cv["clase_celda_max_ajuste"] == "C").sum())
    h["cv.max_en_borde"] = float((cv["en_borde"].astype(str) == "True").sum() + (cv["en_borde"].astype(str) == "si").sum())
    h["cv.mallas"] = float(len(cv))
    eq = pd.read_csv(os.path.join(F1, "p6_equipos_diseno.csv"))
    dep = ["rp", "dh_turb", "Wt_mb", "q4", "UA_reg", "pinch_reg", "qreg_qi", "Qout_mb", "aprox_cond_sal", "Qi_mb", "Wp_Wt"]
    sens = eq[(eq["sensible"].astype(str) == "si")]
    por = {a: g["cantidad"].nunique() for a, g in sens[sens["cantidad"].isin(dep)].groupby("ambito")}
    h["eqd.todos"] = float(por.get("todos", 0))
    bl = [v for k, v in por.items() if k != "todos"]
    h["eqd.bloque.min"], h["eqd.bloque.max"] = float(min(bl)), float(max(bl))
    pw = pd.read_csv(os.path.join(F1, "p6_potencia_u1.csv"))
    h["pot.mdd_peor"] = float(pw[pw["tabla"] == "entre_lotes"]["d_min_peor"].iloc[0])
    fi = pd.read_csv(os.path.join(F1, "p6_fronteras_ic.csv"))
    key = {"E3 C1 Husavik": "C1", "E3 C2 ancla A*": "C2", "E14 C3 caliente 150 C": "C3", "E14 C4 frio 110 C": "C4"}
    for _, x in fi.iterrows():
        k = "fic.%s.%s.%s" % (key[x["bloque"]], x["variable"], x["variante"])
        h[k + ".x"], h[k + ".lo"], h[k + ".hi"] = float(x["x_frontera"]), float(x["ic_lo"]), float(x["ic_hi"])
    au = fi.groupby(["bloque", "variante"])["auc"].first()
    for (b, v), a in au.items():
        h["fic.%s.%s.auc" % (key[b], v)] = float(a)


def _fdr(h):
    F1 = os.path.join(R, "2026-10-18_sens2_F1")
    f = pd.read_csv(os.path.join(F1, "p6_indices_fdr.csv"))
    key = {"E3 C1 Husavik": "C1", "E3 C2 ancla A*": "C2", "E14 C3 caliente 150 C": "C3", "E14 C4 frio 110 C": "C4"}
    for y in ("Y1", "Y2", "Y3"):
        g = f[f["respuesta"].str.startswith(y)]
        h["fdr.%s.n_fdr" % y] = float(g["distinguible_fdr"].astype(bool).sum())
        h["fdr.%s.n_p3" % y] = float(g["distinguible_p3"].fillna(False).astype(bool).sum())
        for b, c in key.items():
            v = g[(g["bloque"] == b) & g["distinguible_fdr"].astype(bool)]
            h["fdr.%s.%s.vars" % (y, c)] = ", ".join(v.sort_values("q_min")["variable"]) or "ninguna"
    nul = pd.read_csv(os.path.join(F1, "p6_nulo_perm.csv"))
    d = nul[nul["tipo"] == "dummy"]
    n2 = f[f["respuesta"].str.startswith("Y2")]["n"]
    h["fdr.Y2.nmin"], h["fdr.Y2.nmax"] = float(n2.min()), float(n2.max())
    h["fdr.calib_pct"] = 100 * float((d["p_perm"] < 0.05).mean())
    h["fdr.B"] = 2000.0


def _eqic(h):
    t = pd.read_csv(os.path.join(R, "2026-10-18_sens2_F1", "p6_equipos_ic.csv")).set_index("cantidad")
    x = t.loc["pendiente dh_turb sobre rp (LHS)"]
    h["eqic.pend"], h["eqic.pend.lo"], h["eqic.pend.hi"], h["eqic.r2"], h["eqic.n"] = (float(x["estimador"]), float(x["ic_lo"]),
                                                                                  float(x["ic_hi"]), float(x["r2"]), float(x["n"]))
    for q, tag in (("rp", "rp"), ("dh_turb", "dh")):
        for pc in (5, 95):
            y = t.loc["%s P%d (todos los KALINA)" % (q, pc)]
            h["eqic.%s.p%d" % (tag, pc)], h["eqic.%s.p%d.lo" % (tag, pc)], h["eqic.%s.p%d.hi" % (tag, pc)] = (
                float(y["estimador"]), float(y["ic_lo"]), float(y["ic_hi"]))


def _ronda2(h):
    F1 = os.path.join(R, "2026-10-18_sens2_F1")
    q = pd.read_csv(os.path.join(F1, "p6_pareado.csv"))
    x = q[(q["variante"] == "mismo_centro") & (q["grupo"] == "todos") & (q["variable"] == "d_eta")].iloc[0]
    h["par4.med"], h["par4.lo"], h["par4.hi"], h["par4.n"] = float(x["mediana"]), float(x["ic_med_lo"]), float(x["ic_med_hi"]), float(x["n"])
    t = pd.read_csv(os.path.join(F1, "p6_pareado_dist.csv"))
    a = t[(t["variante"] == "mismo_centro") & (t["grupo"] == "todos") & (t["calculo"] == "ajuste")].iloc[0]
    h["par.int"], h["par.int.lo"], h["par.int.hi"] = float(a["estimador"]), float(a["ic_lo"]), float(a["ic_hi"])
    u = pd.read_csv(os.path.join(U1, "u1_filas.csv"))
    u = u[u["barrido"].isin(["U1A", "U1A2"])]
    for c, thr, tag in (("C1", 0.922, "a"), ("C1", 0.93, "b"), ("C4", 0.906, "a"), ("C4", 0.91, "b")):
        g = u[(u["centro"] == c) & (u["eps_cond"] >= thr)]
        h["u1x.%s.%s.n" % (c, tag)] = float(len(g))
        h["u1x.%s.%s.perdidos" % (c, tag)] = float((g["clasificacion"] != "KALINA").sum())
        h["u1x.%s.%s.thr" % (c, tag)] = thr
        pe = g[g["clasificacion"] != "KALINA"]
        if tag == "a" and len(pe):
            h["u1x.%s.a.pb_min" % c], h["u1x.%s.a.pb_max" % c] = float(pe["P_baja"].min()), float(pe["P_baja"].max())
            h["u1x.%s.a.ts_min" % c], h["u1x.%s.a.xb_min" % c] = float(pe["T_sumidero"].min()), float(pe["x_b"].min())
    sc = pd.read_csv(os.path.join(U1, "u1_scan_eps_cond.csv"))
    for c in ("C1", "C4"):
        g = sc[(sc["centro"] == c) & sc["m_O2"].notna()].sort_values("eps_cond")
        h["u1s.%s.media" % c] = float(np.polyfit(g["eps_cond"], g["m_O2"], 1)[0] * 0.01)
        k = g[g["m_O2"] >= 0]
        a0, a1 = k.iloc[0], g.iloc[-1]
        h["u1s.%s.cerca" % c] = float((a1["m_O2"] - a0["m_O2"]) / (a1["eps_cond"] - a0["eps_cond"]) * 0.01)
    u2 = pd.read_csv(os.path.join(U1, "u1_filas.csv"))
    h["u1.nc_clase"] = float((u2["clasificacion"] == "NO_CONVERGIO").sum())
    h["u1.n"] = float(len(u2))
    import p6_comun as K
    fi = pd.read_csv(os.path.join(F1, "p6_fronteras_ic.csv"))
    rng = {n: {v: (g[v].min(), g[v].max()) for v in K.REALES} for n, g in K.bloques()}
    cuenta = 0
    for _, x in fi.iterrows():
        lo, hi = rng[x["bloque"]][x["variable"]]
        cota_baja = 0.0 if x["variable"] in ("P_alta", "P_baja") else lo * 0.0 - 1e9
        cota_alta = 1.0 if x["variable"] in ("x_b", "eps_cond", "eps_hrvg", "eps_reg", "eta_t") else 1e9
        ok = (x["ic_lo"] >= cota_baja) and (x["ic_hi"] <= cota_alta) and (x["ic_hi"] - x["ic_lo"] <= 0.5 * (hi - lo))
        cuenta += int(ok)
        key = {"E3 C1 Husavik": "C1", "E3 C2 ancla A*": "C2", "E14 C3 caliente 150 C": "C3", "E14 C4 frio 110 C": "C4"}[x["bloque"]]
        h["fic.%s.%s.%s.info" % (key, x["variable"], x["variante"])] = "si" if ok else "no"
    h["fic.informativas"], h["fic.filas"] = float(cuenta), float(len(fi))


def _ronda3(h):
    F1 = os.path.join(R, "2026-10-18_sens2_F1")
    q = pd.read_csv(os.path.join(F1, "p6_pareado.csv"))
    d = q[(q["variante"] == "mismo_centro") & (q["variable"] == "d_eta")]
    x = d[d["grupo"] == "todos"].iloc[0]
    h["par4.media"], h["par4.media.lo"], h["par4.media.hi"] = float(x["media"]), float(x["ic_media_lo"]), float(x["ic_media_hi"])
    cruza = [g for g in ("C1 Husavik", "C2 ancla A*", "C3 caliente 150 C", "C4 frio 110 C")
             if (d[d["grupo"] == g]["ic_media_lo"].iloc[0] <= 0 <= d[d["grupo"] == g]["ic_media_hi"].iloc[0])]
    h["par4.cruza0"] = " y ".join(g.split(" ")[0] for g in cruza) or "ningun bloque"
    t = pd.read_csv(os.path.join(F1, "p6_pareado_dist.csv"))
    t = t[t["variante"] == "mismo_centro"]
    y = t[(t["grupo"] == "otros") & (t["calculo"] == "tramo L1 0.5 a mas")].iloc[0]
    h["par.otros.lejos"], h["par.otros.lejos.lo"], h["par.otros.lejos.hi"], h["par.otros.lejos.n"] = (
        float(y["estimador"]), float(y["ic_lo"]), float(y["ic_hi"]), float(y["n"]))


def _ciclo(h):
    t = pd.read_csv(os.path.join(R, "2026-10-18_sens2_F1", "p6_ciclo_T.csv"))
    for _, x in t.iterrows():
        c = int(round(x["T_centro_C"]))
        if pd.notna(x["eta_max_dentro"]):
            h["ciclo.eta%d" % c] = float(x["eta_max_dentro"])
        h["ciclo.n%d" % c] = float(x["n"])
        h["ciclo.nkal%d" % c] = float(x["n_kalina"])
        h["ciclo.p%d" % c] = float(x["p_kalina"])
        h["ciclo.pconv%d" % c] = float(x["p_kalina_si_convergio"])
    h["ciclo.nkal.min"] = float(t["n_kalina"].min())
    h["ciclo.n.min"], h["ciclo.n.max"] = float(t["n"].min()), float(t["n"].max())
    from s2_cargar import dataset_dedup
    k = dataset_dedup()
    k = k[k["kalina"] & (k["T_fuente"] >= 483.15)]
    h["ciclo.caliente.n"], h["ciclo.caliente.fuera"] = float(len(k)), float(k["fuera_rango"].sum())


def _kw(h):
    t = pd.read_csv(os.path.join(R, "2026-10-18_sens2_F1", "p6_equipos_kw.csv"))
    t = t[t["ambito"] == "todos"]
    for _, x in t.iterrows():
        for p in ("p5", "p50", "p95"):
            h["kw.%s.%s" % (x["magnitud"], p)] = float(x[p])
            h["kw100.%s.%s" % (x["magnitud"], p)] = 100 * float(x[p])
    h["kw.n"] = float(t["n"].iloc[0])


def hechos():
    h = {}
    for f in (_u1, _mo2, _nc, _f6, _r1, _rob, _f1, _pareado, _f1b, _fdr, _eqic, _ronda2, _ronda3, _ciclo, _kw):
        f(h)
    return h


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for k, v in sorted(hechos().items()):
        print("%-28s %s" % (k, round(v, 4) if isinstance(v, float) else v))
