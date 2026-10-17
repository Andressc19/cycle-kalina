# -*- coding: utf-8 -*-
"""Sens2 P3 - Paso 2: interacciones (no aditividad) desde las mallas de pares.

Un punto pertenece a la malla de un par si TODAS las variables distintas de las
dos del par valen lo del centro (redondeo a 2 decimales); no se usa la etiqueta
`par`. Por par y centro: tabla de eta de los KALINA y matriz de indicador KALINA,
e indice de no aditividad 1 - R^2 del modelo aditivo (media de fila + media de
columna - media global). Umbrales declarados: < 0.05 aditivo; >= 0.25 fuerte.
"""
import os

import numpy as np
import pandas as pd

import p3_comun as C

ENTRADAS = ["T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "eta_t", "eta_p",
            "eps_hrvg", "eps_reg", "eps_cond"]
PARS = {"B1": ("T_fuente", "P_baja"), "B2": ("P_baja", "x_b"),
        "B3": ("P_alta", "P_baja"), "B4": ("eps_cond", "T_sumidero"),
        "B5": ("eps_reg", "eta_t"), "B6": ("eps_hrvg", "T_fuente")}
ADITIVO = 0.05
FUERTE = 0.25


def clasif(noadit, signo):
    if not np.isfinite(noadit):
        return "no_aplica"
    if noadit < ADITIVO:
        return "aditivo"
    base = "sinergico" if signo > 0 else "antagonico"
    return base + " (fuerte)" if noadit >= FUERTE else base


def no_aditividad(mat):
    """(1 - R^2, signo, n) del modelo aditivo fila+columna-global sobre celdas con valor."""
    fin = np.isfinite(mat)
    if fin.sum() < 4:
        return (np.nan, np.nan, int(fin.sum()))
    mm = np.where(fin, mat, 0.0)
    rn, rs = fin.sum(axis=1), mm.sum(axis=1)
    cn, cs = fin.sum(axis=0), mm.sum(axis=0)
    r = np.where(rn > 0, rs / np.where(rn > 0, rn, 1), np.nan)
    c = np.where(cn > 0, cs / np.where(cn > 0, cn, 1), np.nan)
    gm = mm.sum() / fin.sum()
    pred = r[:, None] + c[None, :] - gm
    res = np.where(fin, mat - pred, np.nan)
    sse = np.nansum(res ** 2)
    sst = np.nansum((np.where(fin, mat, np.nan) - gm) ** 2)
    if sst <= 0:
        return (np.nan, np.nan, int(fin.sum()))
    r2 = 1.0 - sse / sst
    return (float(1.0 - r2), float(np.sign(np.nanmean(res))), int(fin.sum()))


def malla(g, cvals, a, b):
    """Matrices (eta, indicador) de la malla del par (a, b) en el centro."""
    otros = [v for v in ENTRADAS if v not in (a, b)]
    mask = np.ones(len(g), bool)
    for v in otros:
        mask &= np.round(g[v].to_numpy(float), 2) == round(float(cvals[v]), 2)
    sub = g[mask]
    av = np.sort(np.unique(np.round(sub[a].to_numpy(float), 2)))
    bv = np.sort(np.unique(np.round(sub[b].to_numpy(float), 2)))
    eta = np.full((len(av), len(bv)), np.nan)
    ind = np.full((len(av), len(bv)), np.nan)
    ia = {v: i for i, v in enumerate(av)}
    ib = {v: j for j, v in enumerate(bv)}
    for _, row in sub.iterrows():
        i = ia[np.round(row[a], 2)]
        j = ib[np.round(row[b], 2)]
        kal = row["clasificacion"] == "KALINA"
        ind[i, j] = 1.0 if kal else 0.0
        if kal:
            eta[i, j] = row["eta_pct"]
    return eta, ind, av, bv


def main():
    d, centros, txt = C.cargar_todo()
    os.makedirs(C.P3, exist_ok=True)
    alcance = [(2, "C1", ["B1", "B2", "B3", "B4", "B5", "B6"]),
               (2, "C2", ["B1", "B2", "B3", "B4", "B5", "B6"]),
               (11, "C3", ["B1", "B2", "B3", "B4"]),
               (11, "C4", ["B1", "B2", "B3", "B4"])]
    filas = []
    bloques_md = []
    for est, code, pares in alcance:
        cname = txt[code]
        g = d[(d["estudio"] == est) & (d["centro"] == cname)].reset_index(drop=True)
        cvals = centros[cname]
        for par in pares:
            a, b = PARS[par]
            eta, ind, av, bv = malla(g, cvals, a, b)
            ne, se, nce = no_aditividad(eta)
            ni, si, nci = no_aditividad(ind)
            filas.append([par, cname, a, b, len(av), len(bv), len(av) * len(bv),
                          nce, ne, se, clasif(ne, se), nci, ni, si, clasif(ni, si)])
            bloques_md.append((par, cname, a, b, av, bv, eta, ind, ne, se, ni, si))
    df = pd.DataFrame(filas, columns=["par", "centro", "var1", "var2", "n_eje1",
                                      "n_eje2", "n_celdas_esperadas", "n_celdas_eta",
                                      "noadit_eta", "signo_eta", "clasificacion",
                                      "n_celdas_ind", "noadit_ind", "signo_ind",
                                      "clasificacion_ind"])
    df.to_csv(os.path.join(C.P3, "p3_interaccion.csv"), index=False)
    with open(os.path.join(C.P3, "p3_interaccion.md"), "w", encoding="utf-8") as f:
        f.write(escribir_md(df, bloques_md, d, alcance, txt))
    print("pares-analizados:", len(df))
    print("con interaccion fuerte:", int(((df["noadit_eta"] >= FUERTE) |
                                          (df["noadit_ind"] >= FUERTE)).sum()))


def escribir_md(df, bloques, d, alcance, txt):
    out = ["# Sens2 P3 - interacciones de pares (Paso 2)", "",
           "No aditividad = 1 - R^2 del modelo aditivo. Umbrales: < 0.05 aditivo; "
           ">= 0.25 fuerte.",
           "Un punto entra en la malla del par si las otras 8 variables valen lo del centro "
           "(2 decimales).", "",
           "## Resumen", "",
           "| par | centro | celdas | eta noadit | clasif eta | ind noadit | clasif ind |",
           "|---|---|---|---|---|---|---|"]
    for _, r in df.iterrows():
        out.append("| %s | %s | %d/%d | %.3f | %s | %.3f | %s |" % (
            r["par"], r["centro"], r["n_celdas_eta"], r["n_celdas_esperadas"],
            r["noadit_eta"], r["clasificacion"], r["noadit_ind"], r["clasificacion_ind"]))
    out.append("")
    out.append("## Mallas (eta de los KALINA y matriz de indicador KALINA)")
    for par, cname, a, b, av, bv, eta, ind, ne, se, ni, si in bloques:
        out.append("")
        out.append("### %s - %s (%s x %s)" % (par, cname, a, b))
        out.append("")
        out.append("eta (%) de los KALINA (punto = sin KALINA en la celda):")
        out.append("")
        out.append(C.tabla_md(eta, ["%.4g" % v for v in av], ["%.4g" % v for v in bv]))
        out.append("")
        out.append("indicador KALINA (1 / 0; punto = celda ausente):")
        out.append("")
        out.append(C.tabla_md(ind, ["%.4g" % v for v in av], ["%.4g" % v for v in bv], "%.0f"))
    return "\n".join(out)


if __name__ == "__main__":
    main()
