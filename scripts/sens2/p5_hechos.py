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


def hechos():
    h = {}
    for f in (_u1, _mo2, _nc, _f6, _r1, _rob):
        f(h)
    return h


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for k, v in sorted(hechos().items()):
        print("%-28s %s" % (k, round(v, 4) if isinstance(v, float) else v))
