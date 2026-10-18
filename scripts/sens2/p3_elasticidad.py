# -*- coding: utf-8 -*-
"""Sens2 P3 - Paso 3: elasticidades locales de eta en el punto base.

Con los barridos de una variable (filas con `variable` distinta de `base`) de los
estudios 1, 4-10 que tengan columna `variable` poblada (aqui: 1 y 10), por centro y
variable: elasticidad = (d eta / eta0) / (d v / v0), por diferencia centrada con
los dos niveles vecinos del base si ambos son KALINA; si no, hacia adelante o
hacia atras y se marca; si ninguno es KALINA, "sin KALINA vecino".
"""
import os

import numpy as np
import pandas as pd

import p3_comun as C

ESTUDIOS = [1, 4, 5, 6, 7, 8, 9, 10]


def vecinos(niveles, v0):
    lo = [v for v in niveles if v < v0]
    hi = [v for v in niveles if v > v0]
    return (max(lo) if lo else None, min(hi) if hi else None)


def elasticidad_centro(g, cname, cvals):
    base = g[g["variable"] == "base"]
    if len(base) == 0:
        return []
    eta0 = float(base.iloc[0]["eta"])
    filas = []
    for v, gg in g[g["variable"] != "base"].groupby("variable"):
        if v == "" or v not in cvals:
            continue
        v0 = float(cvals[v])
        vals = gg[["valor", "eta", "clasificacion"]].dropna(subset=["valor"])
        vals = vals.drop_duplicates("valor").sort_values("valor")
        niveles = vals["valor"].to_numpy(float)
        emap = dict(zip(vals["valor"], vals["eta"]))
        cmap = dict(zip(vals["valor"], vals["clasificacion"]))
        vm, vp = vecinos(niveles, v0)
        kl = lambda x: x is not None and cmap.get(x) == "KALINA"  # noqa: E731
        if kl(vm) and kl(vp):
            dv, deta, tipo = vp - vm, emap[vp] - emap[vm], "centrada"
        elif kl(vp):
            dv, deta, tipo = vp - v0, emap[vp] - eta0, "hacia adelante"
        elif kl(vm):
            dv, deta, tipo = vm - v0, emap[vm] - eta0, "hacia atras"
        else:
            dv, deta, tipo = np.nan, np.nan, "sin KALINA vecino"
        ela = (deta / dv) * (v0 / eta0) if np.isfinite(dv) and dv != 0 and eta0 else np.nan
        filas.append([cname, v, round(v0, 6), round(eta0, 6),
                      "" if vm is None else round(vm, 6),
                      "" if vm is None else cmap.get(vm, ""),
                      "" if vp is None else round(vp, 6),
                      "" if vp is None else cmap.get(vp, ""),
                      tipo, round(dv, 6) if np.isfinite(dv) else np.nan, deta,
                      None if not np.isfinite(ela) else round(float(ela), 6)])
    return filas


def main():
    d, centros, txt = C.cargar_todo()
    os.makedirs(C.P3, exist_ok=True)
    usados = []
    for e in ESTUDIOS:
        s = d[d["estudio"] == e]
        if len(s) and ((s["variable"] != "") & (s["variable"] != "base")).any():
            usados.append(e)
    filas = []
    for cname in ["C1 Husavik", "C2 ancla A*", "C3 caliente 150 C", "C4 frio 110 C"]:
        g = d[d["centro"] == cname]
        g = g[g["estudio"].isin(usados)]
        if len(g) == 0:
            continue
        filas += elasticidad_centro(g, cname, centros[cname])
    df = pd.DataFrame(filas, columns=["centro", "variable", "v0", "eta0", "nivel_menos",
                                      "clase_menos", "nivel_mas", "clase_mas", "tipo",
                                      "dv", "deta", "elasticidad"])
    df.to_csv(os.path.join(C.P3, "p3_elasticidad.csv"), index=False)
    piv = df.pivot_table(index="variable", columns="centro", values="elasticidad",
                         aggfunc="first")
    with open(os.path.join(C.P3, "p3_elasticidad.md"), "w", encoding="utf-8") as f:
        f.write(escribir_md(piv, df, usados))
    print("estudios con variable:", usados)
    print("filas elasticidad:", len(df), "sin KALINA vecino:",
          int((df["tipo"] == "sin KALINA vecino").sum()))


def escribir_md(piv, df, usados):
    out = ["# Sens2 P3 - elasticidades locales (Paso 3)", "",
           "Elasticidad = (d eta / eta0) / (d v / v0) en el punto base. Estudios con columna "
           "`variable`:", ", ".join(str(e) for e in usados) + ".", "",
           "## Elasticidad por variable y centro", "",
           "| variable | " + " | ".join(piv.columns) + " |",
           "|" + "---|" * (len(piv.columns) + 1)]
    for v, row in piv.iterrows():
        cel = ["%.3f" % row[c] if np.isfinite(row[c]) else "." for c in piv.columns]
        out.append("| %s | " % v + " | ".join(cel) + " |")
    out.append("")
    out.append("## Detalle (tipo de diferencia por centro y variable)")
    out.append("")
    out.append("| centro | variable | eta0 | nivel menos | nivel mas | tipo | elasticidad |")
    out.append("|---|---|---|---|---|---|---|")
    for _, r in df.iterrows():
        ela = "%.3f" % r["elasticidad"] if r["elasticidad"] is not None and np.isfinite(r["elasticidad"]) else "."
        out.append("| %s | %s | %.4f | %s | %s | %s | %s |" % (
            r["centro"], r["variable"], r["eta0"], r["nivel_menos"], r["nivel_mas"],
            r["tipo"], ela))
    return "\n".join(out)


if __name__ == "__main__":
    main()
