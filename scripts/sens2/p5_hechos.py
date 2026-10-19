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
    t0 = pd.read_csv(os.path.join(F1, "p6_pareado_dist.csv"))
    z = t0[(t0["variante"] == "mismo_centro") & (t0["grupo"] == "todos") & (t0["calculo"] == "tramo L1 0.2 a 0.5")].iloc[0]
    h["par.medio.med"], h["par.medio.n"] = float(z["estimador"]), float(z["n"])
    z = t0[(t0["variante"] == "mismo_centro") & (t0["grupo"] == "todos") & (t0["calculo"] == "tramo L1 0.5 a mas")].iloc[0]
    h["par.lejos.todos.med"], h["par.lejos.todos.n"] = float(z["estimador"]), float(z["n"])
    o1 = d[d["grupo"] == "O1"].iloc[0]
    h["par.o1.med"], h["par.o1.lo"], h["par.o1.hi"], h["par.o1.n"] = float(o1["mediana"]), float(o1["ic_med_lo"]), float(o1["ic_med_hi"]), float(o1["n"])
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
        h["ciclo.nin%d" % c] = float(x["n_kalina_dentro"])
        h["ciclo.p%d" % c] = float(x["p_kalina"])
        h["ciclo.pconv%d" % c] = float(x["p_kalina_si_convergio"])
    h["ciclo.nkal.min"] = float(t["n_kalina"].min())
    mostradas = t[t["n_kalina_dentro"] >= 10]
    h["ciclo.n.min"], h["ciclo.n.max"] = float(mostradas["n"].min()), float(mostradas["n"].max())
    from s2_cargar import dataset_dedup
    k = dataset_dedup()
    k = k[k["kalina"] & (k["T_fuente"] >= 433.15)]
    h["ciclo.caliente.n"], h["ciclo.caliente.fuera"] = float(len(k)), float(k["fuera_rango"].sum())
    h["ciclo.caliente.pct"] = 100 * h["ciclo.caliente.fuera"] / h["ciclo.caliente.n"]
    import p4_comun as c4
    e = c4.cargar()
    m = (e[c4.mascara(e, c4.REF_TOP10)]["q4"] - 0.90).to_numpy(float)
    h["e3.med"], h["e3.max"], h["e3.p01"] = float(pd.Series(m).median()), float(m.max()), 100 * float((m <= 0.01).mean())


def _kw(h):
    t = pd.read_csv(os.path.join(R, "2026-10-18_sens2_F1", "p6_equipos_kw.csv"))
    t = t[t["ambito"] == "todos"]
    top = pd.read_csv(os.path.join(R, "2026-10-18_sens2_F1", "p6_equipos_kw.csv"))
    top = top[top["ambito"].str.startswith("10 %")]
    for _, x in top.iterrows():
        for p in ("p5", "p50", "p95"):
            h["kwtop.%s.%s" % (x["magnitud"], p)] = float(x[p])
            h["kwtop100.%s.%s" % (x["magnitud"], p)] = 100 * float(x[p])
    h["kwtop.n"] = float(top["n"].iloc[0])
    for _, x in t.iterrows():
        for p in ("p5", "p50", "p95"):
            h["kw.%s.%s" % (x["magnitud"], p)] = float(x[p])
            h["kw100.%s.%s" % (x["magnitud"], p)] = 100 * float(x[p])
    h["kw.n"] = float(t["n"].iloc[0])


def _ronda6(h):
    F1 = os.path.join(R, "2026-10-18_sens2_F1")
    dist = pd.read_csv(os.path.join(R, "2026-10-17_sens2_P2", "p2_distancia.csv"))
    from s2_cargar import dataset_dedup
    est = dataset_dedup()[["id_punto", "estudio"]].astype({"id_punto": str})
    dist["id_punto"] = dist["id_punto"].astype(str)
    j = dist.merge(est, on="id_punto", how="left")
    una = j["nvars_diff"] == 1
    lhs = j["estudio"].isin([3, 14])
    h["h1.todos"], h["h1.todos.n"] = 100 * float(una.mean()), float(len(j))
    h["h1.nolhs"], h["h1.nolhs.n"] = 100 * float(una[~lhs].mean()), float((~lhs).sum())
    h["h1.lhs"], h["h1.lhs.n"] = 100 * float(una[lhs].mean()), float(lhs.sum())
    t = pd.read_csv(os.path.join(F1, "p6_pareado_dist.csv"))
    t = t[(t["variante"] == "mismo_centro") & (t["calculo"] == "ajuste")]
    for g, tag in (("otros", "otros"), ("LHS", "lhs")):
        x = t[t["grupo"] == g].iloc[0]
        h["par.int.%s" % tag], h["par.int.%s.lo" % tag], h["par.int.%s.hi" % tag] = float(x["estimador"]), float(x["ic_lo"]), float(x["ic_hi"])
    m = pd.read_csv(os.path.join(F1, "p6_m5_lhs.csv"))
    for norma, tag in (("completo", "c"), ("lhs", "l")):
        for _, x in m[m["normalizacion"] == norma].iterrows():
            b = x["bloque"].split(" ")[0]
            h["m5.%s.%s.top" % (tag, b)], h["m5.%s.%s.resto" % (tag, b)] = float(x["mediana_top"]), float(x["mediana_resto"])
            h["m5.%s.%s.p" % (tag, b)], h["m5.%s.%s.pb" % (tag, b)] = float(x["p_ks"]), float(x["p_bonferroni4"])


def _ronda8(h):
    F1 = os.path.join(R, "2026-10-18_sens2_F1")
    t = pd.read_csv(os.path.join(F1, "p6_calibra_regla.csv"))
    x = t[(t["tabla"] == "A_por_respuesta") & (t["grupo"] == "Total")].iloc[0]
    h["cal.dummy.n"], h["cal.dummy.marcadas"] = float(x["n_unidades"]), float(x["marcadas"])
    h["cal.dummy.lo"], h["cal.dummy.hi"] = 100 * float(x["ic_lo"]), 100 * float(x["ic_hi"])
    g = t[t["tabla"] == "C_global"].iloc[-1]
    h["cal.global.bloque"], h["cal.global.mezcla"] = float(g["reales_bloque"]), float(g["reales_global_mezcla"])
    h["cal.global.n"] = float(g["n_unidades"])
    m = pd.read_csv(os.path.join(F1, "p6_m5_pruebas.csv"))
    for norma, tag in (("completo", "c"), ("lhs", "l")):
        for _, y in m[m["normalizacion"] == norma].iterrows():
            h["m5.mw.%s.%s.p" % (tag, y["bloque"].split(" ")[0])] = float(y["p_mw"])
    h["m5.mw.n_sig"] = float((m["p_mw"] < 0.05).sum())
    h["m5.ks.n_sig"] = float((m["p_ks"] < 0.05).sum())


def _ronda9(h):
    F1 = os.path.join(R, "2026-10-18_sens2_F1")
    p = pd.read_csv(os.path.join(F1, "p6_pisos25.csv"))
    for x in p.itertuples():
        k = "pisos.%s.%03d" % (x.centro, round(x.x_b * 100))
        h[k + ".ref"], h[k + ".malla"] = float(x.piso_refinado), float(x.piso_malla)
    h["pisos.n"], h["pisos.n_mejora"] = float(len(p)), float((p["mejora_kpa"] > 0).sum())
    h["pisos.mejora.max"], h["pisos.mejora.med"] = float(p["mejora_kpa"].max()), float(p["mejora_kpa"].median())
    h["pisos.n_puntos"] = float(p["n_puntos"].sum())
    r = pd.read_csv(os.path.join(F1, "p6_reintento_nc.csv"))
    h["reint.n"] = float(len(r))
    h["reint.tmax"], h["reint.tmean"] = float(r["t_s_nuevo"].max()), float(r["t_s_nuevo"].mean())
    c6 = r[r["t_s_original"] >= 590]
    h["reint.n600"], h["reint.n600.tmin"], h["reint.n600.tmax"] = float(len(c6)), float(c6["t_s_nuevo"].min()), float(c6["t_s_nuevo"].max())
    h["reint.n_lento"], h["reint.n_ctrl"] = float((r["grupo"] == "lento").sum()), float((r["grupo"] == "control").sum())
    h["reint.conv"] = float((~r["clase_nueva"].isin(["NO_CONVERGIO", "ERROR_MOTOR"])).sum())
    h["reint.n_nc"], h["reint.n_err"] = float((r["clase_nueva"] == "NO_CONVERGIO").sum()), float((r["clase_nueva"] == "ERROR_MOTOR").sum())
    c = r[r["clase_nueva"] == "NO_CONVERGIO"]["causa_nueva"].fillna("")
    h["reint.c_bracket"], h["reint.c_balance"] = float(c.str.startswith("sin dos extremos").sum()), float(c.str.startswith("N2").sum())
    h["reint.c_lazo"] = float(c.str.startswith("lazo interior").sum())
    h["reint.c_otras"] = float(len(c)) - h["reint.c_bracket"] - h["reint.c_balance"] - h["reint.c_lazo"]


def _ronda12(h):
    t = pd.read_csv(os.path.join(R, "2026-10-18_sens2_F1", "p6_opt_T.csv"))
    for x in t.itertuples():
        k = "opt.%d" % round(x.T_fuente_C)
        h[k + ".eta"], h[k + ".pa"], h[k + ".pb"], h[k + ".xb"] = float(x.eta_max_pct), float(x.P_alta), float(x.P_baja), float(x.x_b)
        h[k + ".dentro"] = float(x.eta_max_dentro_pct)
        h[k + ".mej"] = float(x.mejora_pp)
        h[k + ".n"], h[k + ".nk"] = float(x.n_eval), float(x.n_kalina)
    b = t[t["T_fuente_C"] < 165]
    h["opt.pb.min"], h["opt.pb.max"] = float(b["P_baja"].min()), float(b["P_baja"].max())
    h["opt.xb.min"], h["opt.xb.max"] = float(b["x_b"].min()), float(b["x_b"].max())
    h["opt.mej.min"], h["opt.mej.max"] = float(t["mejora_pp"].min()), float(t["mejora_pp"].max())
    h["opt.160.mejd"] = float(t[t["T_fuente_C"].round() == 160]["mejora_dentro_pp"].iloc[0])
    h["opt.neval.min"], h["opt.neval.max"] = float(t["n_eval"].min()), float(t["n_eval"].max())
    h["opt.n_eval"], h["opt.n_kalina"] = float(t["n_eval"].sum()), float(t["n_kalina"].sum())
    h["opt.eta.min_alta"], h["opt.eta.max_alta"] = float(t[t["T_fuente_C"] > 165]["eta_max_pct"].min()), float(t[t["T_fuente_C"] > 165]["eta_max_pct"].max())


def _ronda11(h):
    t = pd.read_csv(os.path.join(R, "2026-10-18_sens2_F1", "p6_sim.csv"))
    for x in t.itertuples():
        k = "simb.%s.%s" % (x.centro, "s" if x.escenario.startswith("SIM") else "u")
        h[k + ".p"], h[k + ".lo"], h[k + ".hi"] = float(x.p_kalina), float(x.ic_lo), float(x.ic_hi)
        h[k + ".n"], h[k + ".k"] = float(x.n), float(x.n_kalina)
    sc = pd.read_csv(os.path.join(R, "2026-10-17_sens2_U1", "u1_scan_eps_cond.csv"))
    for c in ("C1", "C4"):
        fr = float(sc[(sc["centro"] == c) & (sc["clasificacion"] == "KALINA")]["eps_cond"].min())
        h["simb.%s.fr" % c] = 100.0 * (fr - 0.85) / 0.10


def _ronda10(h):
    b = pd.read_csv(os.path.join(R, "2026-10-17_sens2_P4", "p4_bandas.csv"))
    b = b[b["centro"] == "todos"].set_index("banda")
    h["bandas.dh1"], h["bandas.dh6"] = float(b.loc["[1, 1.5)", "dh_p50"]), float(b.loc["[6, 10)", "dh_p50"])
    h["bandas.eta1"], h["bandas.eta6"] = float(b.loc["[1, 1.5)", "eta_p50"]), float(b.loc["[6, 10)", "eta_p50"])
    F1 = os.path.join(R, "2026-10-18_sens2_F1")
    t = pd.read_csv(os.path.join(F1, "p6_dens.csv"))
    for x in t[t["ambito"] == "todos"].itertuples():
        h["dens.%s.p5" % x.magnitud], h["dens.%s.p50" % x.magnitud], h["dens.%s.p95" % x.magnitud] = float(x.p5), float(x.p50), float(x.p95)
        h["dens.n"] = float(x.n)
    d = pd.read_csv(os.path.join(R, "2026-10-18_sens2_B", "s2b_dens_filas.csv"))
    h["dens.n_filas"] = float(len(d))
    h["dens.wnet_min"], h["dens.eta_med"] = float(d["Wnet"].min()), float(100.0 * d["eta"].median())
    h["dens.n_bifasico"] = float((d["fase4"] == "bifasico").sum())
    h["dens.repro_pp"] = float((100.0 * d["eta"] - d["val1"]).abs().max())


def hechos():
    h = {}
    for f in (_u1, _mo2, _nc, _f6, _r1, _rob, _f1, _pareado, _f1b, _fdr, _eqic, _ronda2, _ronda3, _ciclo, _kw, _ronda6, _ronda8, _ronda9, _ronda10, _ronda11, _ronda12):
        f(h)
    return h


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for k, v in sorted(hechos().items()):
        print("%-28s %s" % (k, round(v, 4) if isinstance(v, float) else v))
