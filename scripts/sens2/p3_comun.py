# -*- coding: utf-8 -*-
"""Sens2 P3 - constantes, carga y utilidades compartidas del Paso 1.

Modulo de apoyo para respetar el limite de 200 lineas por archivo: reune rutas,
constantes, cargadores, bootstrap, tablas markdown y el ranking.
"""
import os
import sys

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))
SEMILLA, N_BOOT, N_PERM, BINS = 20261017, 500, 200, 10
P2 = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P2", "p2_dataset_dedup.csv")
P3 = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P3")
# eta_p es constante en los bloques LHS (estudios 3 y 14): no es entrada.
REALES = ["T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "eta_t", "eps_hrvg",
          "eps_reg", "eps_cond"]
DUMMIES = ["dummy_1", "dummy_2", "dummy_3"]
VARS = REALES + DUMMIES
RESPUESTAS = [("Y1", "Y1 KALINA (total)", "todos"), ("Y2", "Y2 eta (%)", "kalina"),
              ("Y3", "Y3 W_net/m_b", "kalina"),
              ("Y2r", "Y2 eta (%) dentro del rango experimental", "kalina_rango"),
              ("Y3r", "Y3 W_net/m_b dentro del rango experimental", "kalina_rango"),
              ("Y4", "Y4 D CORREGIBLE", "corregible")]
BLOQUES = [("E3 C1 Husavik", 3, "C1 Husavik"), ("E3 C2 ancla A*", 3, "C2 ancla A*"),
           ("E14 C3 caliente 150 C", 14, "C3 caliente 150 C"),
           ("E14 C4 frio 110 C", 14, "C4 frio 110 C")]
MET_BASE_RANGO = ["PRCC", "SRC", "PAWN", "delta", "HSIC", "eta2"]
COLUMNAS = ["bloque", "respuesta", "variable", "metodo", "valor", "ic_lo", "ic_hi",
            "n", "p_valor", "motivo"]


def cargar_dedup():
    return pd.read_csv(P2)


def cargar_todo():
    import x1_cargar as x
    return x.cargar_todo(), x.CENTROS, x.CENTRO_TXT


def bootstrap_indices(n, seed=SEMILLA, n_boot=N_BOOT):
    return np.random.default_rng(seed).integers(0, n, size=(n_boot, n))


def tabla_md(mat, filas, cols, fmt="%.4f"):
    lineas = ["| a\\b | " + " | ".join(cols) + " |", "|" + "---|" * (len(cols) + 1)]
    for i, f in enumerate(filas):
        cel = ["." if not np.isfinite(mat[i, j]) else fmt % mat[i, j] for j in range(len(cols))]
        lineas.append("| %s | " % f + " | ".join(cel) + " |")
    return "\n".join(lineas)


def _mag_lo(lo, hi):
    if np.isfinite(lo) and np.isfinite(hi):
        return 0.0 if lo * hi < 0 else min(abs(lo), abs(hi))
    return np.nan


def ranking(filas):
    """Rango medio por variable y piso de ruido segun las 3 dummy."""
    df = pd.DataFrame(filas, columns=COLUMNAS)
    reg = []
    for (bl, resp), gg in df.groupby(["bloque", "respuesta"], sort=False):
        metodos = list(MET_BASE_RANGO)
        if resp.startswith("Y1"):
            metodos += ["KS", "LOGIT"]
        g2 = gg[(gg["metodo"].isin(metodos)) & (gg["valor"].notna())].copy()
        g2["mag"] = g2["valor"].abs()
        g2["mag_lo"] = [_mag_lo(r["ic_lo"], r["ic_hi"]) for _, r in g2.iterrows()]
        acc = {v: {"ranks": [], "sobre": 0, "nmet": 0} for v in VARS}
        for _, mgg in g2.groupby("metodo"):
            dm = mgg[mgg["variable"].isin(DUMMIES)]["mag"].to_numpy(float)
            dmax = np.nanmax(dm) if np.isfinite(dm).any() else np.nan
            orden = mgg.set_index("variable")["mag"].sort_values(ascending=False)
            lov = mgg.set_index("variable")["mag_lo"]
            for rango, (v, _) in enumerate(orden.items(), start=1):
                acc[v]["ranks"].append(rango)
                acc[v]["nmet"] += 1
                if v in lov.index and np.isfinite(lov[v]) and np.isfinite(dmax) and lov[v] > dmax:
                    acc[v]["sobre"] += 1
        for v, a in acc.items():
            if not a["ranks"]:
                continue
            pr = gg[(gg["variable"] == v) & (gg["metodo"] == "PRCC")]["valor"]
            sr = gg[(gg["variable"] == v) & (gg["metodo"] == "SRC")]["valor"]
            base = pr.iloc[0] if len(pr) and np.isfinite(pr.iloc[0]) else (sr.iloc[0] if len(sr) else np.nan)
            signo = "" if not np.isfinite(base) else ("+" if base >= 0 else "-")
            reg.append([bl, resp, v, "real" if v in REALES else "dummy",
                        round(float(np.mean(a["ranks"])), 3), a["nmet"], a["sobre"],
                        bool(a["sobre"] >= 1) and v in REALES, signo])
    return pd.DataFrame(reg, columns=["bloque", "respuesta", "variable", "tipo",
                                      "rango_medio", "n_metodos", "n_sobre_ruido",
                                      "distinguible", "signo"])


def escribir_md(rank):
    out = ["# Sens2 P3 - rankings de indices (Paso 1)", "",
           "Rango 1 = mayor indice (magnitud) en cada metodo. `distinguible` = el limite",
           "inferior del IC de magnitud supera el maximo de las 3 dummy en al menos un metodo.", ""]
    for (bl, resp), gg in rank.groupby(["bloque", "respuesta"], sort=False):
        out.append("## %s - %s" % (bl, resp))
        out.append("")
        out.append("| variable | rango medio | signo (PRCC/SRC) | n sobre ruido | distinguible |")
        out.append("|---|---|---|---|---|")
        for _, r in gg[gg["tipo"] == "real"].sort_values("rango_medio").head(5).iterrows():
            out.append("| %s | %.2f | %s | %d/%d | %s |" % (
                r["variable"], r["rango_medio"], r["signo"] or "?",
                r["n_sobre_ruido"], r["n_metodos"], "si" if r["distinguible"] else "no"))
        dum = gg[gg["tipo"] == "dummy"]
        if len(dum):
            b = dum.sort_values("rango_medio").iloc[0]
            out.append("")
            out.append("Mejor dummy: %s (rango medio %.2f)." % (b["variable"], b["rango_medio"]))
        out.append("")
    return "\n".join(out)
