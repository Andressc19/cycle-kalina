# -*- coding: utf-8 -*-
"""Sens2 U1 - analisis de la propagacion de incertidumbre (P(KALINA), distribucion de eta, causas, sensibilidad).

Entrada: resultados/2026-10-17_sens2_U1/u1_filas.csv. Salidas en la misma carpeta: u1_resumen.csv,
u1_sensibilidad.csv y u1_resumen.md. La banda del modelo de propiedades (+-0.7 pp de eta, G4-01) se anade
como ensanche determinista de P5/P95, no como muestreo.
"""
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp, rankdata

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
from u1_puntos import ESCENARIOS, TOL, VARIABLES  # noqa: E402

OUT = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_U1")
BANDA_MODELO = 0.7
NOM = {"C1": 12.0, "C2": None, "C3": None, "C4": None}


def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def prcc(X, y):
    R = np.column_stack([rankdata(X[:, j]) for j in range(X.shape[1])])
    ry = rankdata(y)
    out = []
    for j in range(R.shape[1]):
        A = np.column_stack([np.ones(len(R)), np.delete(R, j, 1)])
        ex = R[:, j] - A @ np.linalg.lstsq(A, R[:, j], rcond=None)[0]
        ey = ry - A @ np.linalg.lstsq(A, ry, rcond=None)[0]
        out.append(float(np.corrcoef(ex, ey)[0, 1]) if ex.std() > 0 and ey.std() > 0 else np.nan)
    return out


def nominales():
    """eta del punto de partida (base KALINA) de cada centro, de los barridos de una variable."""
    sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))
    import x1_cargar as X
    d = X.cargar_todo()
    b = d[d["estudio"].isin([1, 10]) & (d["variable"] == "base")]
    return {c: float(b[b["centro"] == n]["eta_pct"].iloc[0]) for c, n in
            (("C1", "C1 Husavik"), ("C2", "C2 ancla A*"), ("C3", "C3 caliente 150 C"), ("C4", "C4 frio 110 C"))}


def main():
    d = pd.read_csv(os.path.join(OUT, "u1_filas.csv"))
    d["kal"] = d["clasificacion"] == "KALINA"
    d["eta_pct"] = d["eta"] * 100.0
    viol = d[["viol_O1", "viol_O2", "viol_O3", "viol_O5"]].fillna(0.0)
    d["dominante"] = viol.idxmax(axis=1).where(viol.max(axis=1) > 0, "sin")
    nom = nominales()
    filas, sens = [], []
    for e in ESCENARIOS:
        for c in ("C1", "C2", "C3", "C4"):
            g = d[(d["barrido"] == e) & (d["centro"] == c)]
            if not len(g):
                continue
            k = g[g["kal"]]
            lo, hi = wilson(len(k), len(g))
            q = k["eta_pct"].quantile([0.05, 0.5, 0.95]).to_numpy() if len(k) else [np.nan] * 3
            nc = g[g["clasificacion"] == "CORREGIBLE"]
            filas.append({
                "escenario": e, "centro": c, "n": len(g), "n_kalina": len(k), "p_kalina": len(k) / len(g),
                "p_lo": lo, "p_hi": hi, "n_corregible": len(nc),
                "n_no_conv": int((g["clasificacion"] == "NO_CONVERGIO").sum()),
                "n_inviable": int((g["clasificacion"] == "INVIABLE").sum()),
                "corr_o2": int((nc["dominante"] == "viol_O2").sum()), "corr_o1": int((nc["dominante"] == "viol_O1").sum()),
                "eta_nominal": nom[c], "eta_p5": q[0], "eta_p50": q[1], "eta_p95": q[2],
                "eta_p5_modelo": q[0] - BANDA_MODELO, "eta_p95_modelo": q[2] + BANDA_MODELO,
                "p_eta_1pp": float(((k["eta_pct"] - nom[c]).abs() <= 1.0).mean()) if len(k) else np.nan,
                "p_fuera_rango": float(k["fuera_rango"].astype(bool).mean()) if len(k) else np.nan})
            X = g[list(VARIABLES)].to_numpy(float)
            pr = prcc(X, g["kal"].astype(float).to_numpy())
            for j, v in enumerate(VARIABLES):
                ks = ks_2samp(g[g["kal"]][v], g[~g["kal"]][v]).statistic if 0 < len(k) < len(g) else np.nan
                sens.append({"escenario": e, "centro": c, "variable": v, "prcc_kalina": pr[j], "ks": ks})
    pd.DataFrame(filas).to_csv(os.path.join(OUT, "u1_resumen.csv"), index=False)
    pd.DataFrame(sens).to_csv(os.path.join(OUT, "u1_sensibilidad.csv"), index=False)
    r = pd.DataFrame(filas)
    md = ["# Sens2 U1 - propagacion de incertidumbre", "",
          "Tolerancias del escenario A (uniformes alrededor del centro): " + ", ".join(
              "%s %s" % (v, ("%.0f %%" % (TOL[v] * 100)) if v in ("P_alta", "P_baja") else "%g" % TOL[v]) for v in VARIABLES) +
          ". El escenario B usa el doble.", "",
          "| escenario | centro | n | P(KALINA) | IC 95 % | eta P5-P50-P95 (%) | eta nominal (%) | P(|eta-nom|<=1 pp) |",
          "|---|---|---|---|---|---|---|---|"]
    for _, x in r.iterrows():
        md.append("| %s | %s | %d | %.2f | [%.2f, %.2f] | %.2f - %.2f - %.2f | %.2f | %.2f |" % (
            x["escenario"], x["centro"], x["n"], x["p_kalina"], x["p_lo"], x["p_hi"], x["eta_p5"], x["eta_p50"],
            x["eta_p95"], x["eta_nominal"], x["p_eta_1pp"]))
    with open(os.path.join(OUT, "u1_resumen.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
