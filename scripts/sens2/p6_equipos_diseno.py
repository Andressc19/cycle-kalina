# -*- coding: utf-8 -*-
"""Sens2 F1 - A2b, Parte 2: envolventes de equipos por diseno.

Para cada cantidad de `p4_comun.CANTIDADES` y cada ambito (todos y los cuatro bloques
con centro) calcula P5, P50 y P95 sobre los KALINA (total) en tres conjuntos:
a_todos (todos los KALINA), b_solo_LHS (solo estudios 3 y 14) y c_peso_igual (todos
con peso 1 / n(centro, estudio), para que cada combinacion centro-estudio aporte lo
mismo). Compara a_todos con p4_envolventes.csv y calcula
desplazamiento = (p50_x - p50_a) / (p95_a - p5_a) para x = b, c; marca
sensible = "si" si algun |desplazamiento| > 0.15. Salidas: p6_equipos_diseno.csv y
p6_equipos_diseno.md.
"""
import os
import sys

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
import p4_comun as c  # noqa: E402

SALIDA = os.path.join(RAIZ, "resultados", "2026-10-18_sens2_F1")
ENVOLVENTES = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P4", "p4_envolventes.csv")
CONJ = ["a_todos", "b_solo_LHS", "c_peso_igual"]
UMBRAL = 0.15
COLS = ["ambito", "cantidad", "conjunto", "n", "p5", "p50", "p95",
        "desplazamiento", "sensible"]


def percentiles(val):
    v = np.asarray(pd.to_numeric(pd.Series(val), errors="coerce"), float)
    v = v[np.isfinite(v)]
    if len(v) == 0:
        return 0, np.nan, np.nan, np.nan
    return (int(len(v)), float(np.percentile(v, 5)), float(np.percentile(v, 50)),
            float(np.percentile(v, 95)))


def pct_ponderado(val, peso, p):
    v = np.asarray(val, float)
    w = np.asarray(peso, float)
    m = np.isfinite(v) & np.isfinite(w)
    v, w = v[m], w[m]
    if len(v) == 0:
        return np.nan
    orden = np.argsort(v, kind="mergesort")
    vs, ws = v[orden], w[orden]
    cum = np.cumsum(ws)
    idx = int(np.searchsorted(cum, p / 100.0 * cum[-1], side="left"))
    return float(vs[min(idx, len(vs) - 1)])


def pesos(s):
    cnt = s.groupby(["centro", "estudio"]).size()
    return np.array([1.0 / cnt[(r["centro"], r["estudio"])] for _, r in s.iterrows()])


def filas_ambito(d, ambito):
    s = d[d["centro"] == ambito] if ambito != "todos" else d
    s = s[c.mask_total(s)]
    lhs = s[s["estudio"].isin([3, 14])]
    w = pesos(s)
    filas = []
    for q in c.CANTIDADES:
        na, p5a, p50a, p95a = percentiles(s[q])
        nb, p5b, p50b, p95b = percentiles(lhs[q])
        vc = np.asarray(pd.to_numeric(s[q], errors="coerce"), float)
        mc = np.isfinite(vc) & np.isfinite(w)
        nc = int(mc.sum())
        if nc:
            p5c = pct_ponderado(vc, w, 5)
            p50c = pct_ponderado(vc, w, 50)
            p95c = pct_ponderado(vc, w, 95)
        else:
            p5c = p50c = p95c = np.nan
        rango = p95a - p5a
        if not np.isfinite(rango) or rango == 0:
            desp_b = desp_c = np.nan
        else:
            desp_b = (p50b - p50a) / rango
            desp_c = (p50c - p50a) / rango
        if np.isfinite(desp_b) and np.isfinite(desp_c):
            sensible = "si" if max(abs(desp_b), abs(desp_c)) > UMBRAL else "no"
        else:
            sensible = ""
        filas.append([ambito, q, "a_todos", na, p5a, p50a, p95a, np.nan, ""])
        filas.append([ambito, q, "b_solo_LHS", nb, p5b, p50b, p95b, desp_b, sensible])
        filas.append([ambito, q, "c_peso_igual", nc, p5c, p50c, p95c, desp_c, sensible])
    return filas


def comparar(tab):
    env = pd.read_csv(ENVOLVENTES)
    env = env[env["conjunto"] == c.REF_TOTAL].set_index(["centro", "cantidad"])
    mal = 0
    for _, r in tab[tab["conjunto"] == "a_todos"].iterrows():
        p4 = env.loc[(r["ambito"], r["cantidad"]), "p50"]
        if abs(r["p50"] - p4) > 1e-6:
            mal += 1
    return mal


def markdown(tab, mal):
    l = ["# Sens2 F1 - A2b, Parte 2: envolventes de equipos por diseno", "",
         "P5, P50 y P95 de cada cantidad de equipo sobre los KALINA (total), por ambito,",
         "en tres conjuntos: a_todos (todos los KALINA), b_solo_LHS (solo estudios 3 y 14)",
         "y c_peso_igual (peso 1 / n(centro, estudio): cada combinacion centro-estudio",
         "aporta lo mismo). desplazamiento = (p50_conjunto - p50_a) / (p95_a - p5_a);",
         "sensible si el mayor |desplazamiento| de b y c pasa de %.2f." % UMBRAL, "",
         "a_todos reproduce p4_envolventes.csv: %d filas con P50 distinta en mas de 1e-6."
         % mal, "", "## Cantidades sensibles por ambito", ""]
    l.append("| ambito | sensibles | de las de equipo (CANT_DEP) |")
    l.append("|---|---|---|")
    for ambito in ["todos"] + c.CENTROS[:4]:
        sub = tab[(tab["ambito"] == ambito) & (tab["sensible"] == "si")
                  & (tab["conjunto"] == "b_solo_LHS")]
        sens = list(dict.fromkeys(sub["cantidad"]))
        dep = [q for q in sens if q in c.CANT_DEP]
        l.append("| %s | %s | %d de %d |" % (
            ambito, ", ".join(sens) if sens else "ninguna", len(dep), len(c.CANT_DEP)))
    l += ["", "Lectura: si al restringir a los estudios LHS o al dar el mismo peso a cada",
          "combinacion centro-estudio la mediana se corre mas de %.2f veces el ancho" % UMBRAL,
          "P5-P95, la envolvente depende del diseno de muestreo y hay que citarla con esa",
          "precision. Los numeros completos estan en `p6_equipos_diseno.csv`.", ""]
    return "\n".join(l)


def main():
    d = c.cargar()
    filas = []
    for ambito in ["todos"] + c.CENTROS[:4]:
        filas += filas_ambito(d, ambito)
    tab = pd.DataFrame(filas, columns=COLS)
    mal = comparar(tab)
    os.makedirs(SALIDA, exist_ok=True)
    tab.to_csv(os.path.join(SALIDA, "p6_equipos_diseno.csv"), index=False)
    with open(os.path.join(SALIDA, "p6_equipos_diseno.md"), "w", encoding="utf-8") as f:
        f.write(markdown(tab, mal))
    print("p6_equipos_diseno.csv:", len(tab), "filas")
    print("filas a_todos con P50 distinta de p4 en mas de 1e-6:", mal)
    for ambito in ["todos"] + c.CENTROS[:4]:
        s = tab[(tab["ambito"] == ambito) & (tab["sensible"] == "si")
                & (tab["conjunto"] == "b_solo_LHS")]
        print("  %-20s sensibles: %d" % (ambito, s["cantidad"].nunique()))


if __name__ == "__main__":
    main()
