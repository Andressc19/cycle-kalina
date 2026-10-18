# -*- coding: utf-8 -*-
"""Sens2 F1 - p6_superficies_cv: validacion cruzada del ajuste cuadratico de eta en las mallas.

Para cada par (B2 = P_baja x x_b, B3 = P_alta x P_baja) y cada bloque replica el
ajuste cuadratico eta ~ 1 + a + b + a^2 + b^2 + ab con a y b estandarizadas (media
y desviacion de las celdas KALINA) y lo valida dejando una celda KALINA fuera:
reajusta sin ella y predice esa celda. Reporta R^2 y RMSE en la muestra, R^2 y
RMSE de la validacion cruzada, la clase de la celda donde cae el maximo del ajuste
sobre toda la malla y si esa celda esta en el borde.

Salidas: p6_superficies_cv.csv y p6_superficies_cv.md.
"""
import os
import sys

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
import s2_calc as C  # noqa: E402

SALIDA = os.path.join(RAIZ, "resultados", "2026-10-18_sens2_F1")
PARS = ["B2", "B3"]
COLS = ["par", "bloque", "n_celdas", "r2", "r2_cv", "rmse", "rmse_cv",
        "clase_celda_max_ajuste", "en_borde", "nota"]


def _fila(za, zb):
    """Matriz de diseno del polinomio cuadratico (1, a, b, a^2, b^2, ab)."""
    return np.column_stack([np.ones(np.size(za)), za, zb, za ** 2, zb ** 2, za * zb])


def _coef(za, zb, y):
    return np.linalg.lstsq(_fila(za, zb), y, rcond=None)[0]


def loo(za, zb, y):
    """Suma de cuadrados de la validacion cruzada dejando una celda fuera."""
    n = len(y)
    sse = 0.0
    for i in range(n):
        m = np.ones(n, bool)
        m[i] = False
        c = _coef(za[m], zb[m], y[m])
        sse += float((y[i] - (_fila(za[i], zb[i]) @ c)[0]) ** 2)
    return sse


def malla(eta, av, bv):
    """Ajuste en la muestra y por validacion cruzada; None si hay menos de 8 celdas KALINA."""
    A, B = np.meshgrid(av, bv, indexing="ij")
    ok = np.isfinite(eta)
    n = int(ok.sum())
    if n < 8:
        return None
    a, b, y = A[ok], B[ok], eta[ok]
    ma, sa, mb, sb = a.mean(), (a.std() or 1.0), b.mean(), (b.std() or 1.0)
    za, zb = (a - ma) / sa, (b - mb) / sb
    coef = _coef(za, zb, y)
    res = y - _fila(za, zb) @ coef
    r2 = 1.0 - (res ** 2).sum() / ((y - y.mean()) ** 2).sum()
    rmse = float(np.sqrt((res ** 2).mean()))
    sse = loo(za, zb, y)
    sst = ((y - y.mean()) ** 2).sum()
    pred = _fila((A - ma).ravel() / sa, (B - mb).ravel() / sb) @ coef
    ig = np.unravel_index(int(np.argmax(pred)), eta.shape)
    return {"n": n, "r2": float(r2), "rmse": rmse, "r2_cv": float(1.0 - sse / sst),
            "rmse_cv": float(np.sqrt(sse / n)), "ig": ig}


def fila_malla(par, b, eta, cls, av, bv, ref, difs):
    r = malla(eta, av, bv)
    if r is None:
        return {"par": par, "bloque": b, "n_celdas": int(np.isfinite(eta).sum()), "r2": np.nan,
                "r2_cv": np.nan, "rmse": np.nan, "rmse_cv": np.nan, "clase_celda_max_ajuste": "",
                "en_borde": "", "nota": "menos de 8 celdas KALINA"}
    if abs(r["r2"] - ref["r2"]) > 1e-6 or abs(r["rmse"] - ref["rmse"]) > 1e-6:
        difs.append((par, b, ref["r2"], r["r2"], ref["rmse"], r["rmse"]))
    ig = r["ig"]
    borde = "si" if (ig[0] in (0, len(av) - 1) or ig[1] in (0, len(bv) - 1)) else "no"
    return {"par": par, "bloque": b, "n_celdas": r["n"], "r2": round(r["r2"], 6), "r2_cv": round(r["r2_cv"], 6),
            "rmse": round(r["rmse"], 6), "rmse_cv": round(r["rmse_cv"], 6),
            "clase_celda_max_ajuste": str(cls[ig]), "en_borde": borde, "nota": ""}


def markdown(tab, difs):
    l = ["# Sens2 F1 - p6_superficies_cv: validacion cruzada del ajuste cuadratico de eta", "",
         "Ajuste eta ~ 1 + a + b + a^2 + b^2 + ab con a y b estandarizadas (media y desviacion de",
         "las celdas KALINA). `r2` y `rmse` son en la muestra; `r2_cv` y `rmse_cv` son dejando una",
         "celda KALINA fuera. `clase_celda_max_ajuste` es la clase de la celda donde cae el maximo",
         "del ajuste sobre toda la malla y `en_borde` si esa celda es la primera o la ultima fila",
         "o columna. `nota` avisa de las mallas con menos de 8 celdas KALINA.", ""]
    l.append("| par | bloque | n celdas | R2 | R2 cv | RMSE | RMSE cv | clase del maximo | en borde |")
    l.append("|---|---|---|---|---|---|---|---|---|")
    for _, r in tab.iterrows():
        f = "%.4f" % r["r2"] if np.isfinite(r["r2"]) else "-"
        fc = "%.4f" % r["r2_cv"] if np.isfinite(r["r2_cv"]) else "-"
        rm = "%.4f" % r["rmse"] if np.isfinite(r["rmse"]) else "-"
        rmc = "%.4f" % r["rmse_cv"] if np.isfinite(r["rmse_cv"]) else "-"
        l.append("| %s | %s | %d | %s | %s | %s | %s | %s | %s |" % (
            r["par"], r["bloque"], r["n_celdas"], f, fc, rm, rmc,
            r["clase_celda_max_ajuste"] or "-", r["en_borde"] or "-"))
    l += ["", "## Lectura por par", ""]
    for par in PARS:
        g = tab[(tab["par"] == par) & tab["r2"].notna()]
        if len(g) == 0:
            l.append("En el par %s ninguna malla tiene 8 celdas KALINA o mas." % par)
            continue
        caida = (g["r2"] - g["r2_cv"]).max()
        mal = g[(g["r2"] - g["r2_cv"]) > 0.2]
        if len(mal) == 0:
            l.append("En el par %s la validacion cruzada casi no degrada el R2: la mayor caida es %.3f "
                     "(por debajo de 0.2), asi que el ajuste cuadratico no depende de celdas sueltas."
                     % (par, caida))
        else:
            l.append("En el par %s la validacion cruzada degrada el R2 en %d malla(s) mas de 0.2 "
                     "(caida mayor %.3f): %s." % (par, len(mal), caida, ", ".join(mal["bloque"])))
    if difs:
        l += ["", "Aviso: el R2 o el RMSE en la muestra no coinciden a 1e-6 con `ajuste_cuadratico` en:"]
        l += ["- %s / %s" % (p, b) for p, b, _, _, _, _ in difs]
    l.append("")
    return "\n".join(l)


def main():
    difs = []
    filas = []
    for par in PARS:
        for b in C.BLOQUES:
            eta, cls, av, bv = C.malla_clases(b, par)
            filas.append(fila_malla(par, b, eta, cls, av, bv, C.ajuste_cuadratico(eta, av, bv), difs))
    tab = pd.DataFrame(filas, columns=COLS)
    os.makedirs(SALIDA, exist_ok=True)
    tab.to_csv(os.path.join(SALIDA, "p6_superficies_cv.csv"), index=False)
    with open(os.path.join(SALIDA, "p6_superficies_cv.md"), "w", encoding="utf-8") as fh:
        fh.write(markdown(tab, difs))
    print("p6_superficies_cv.csv:", len(tab), "filas")
    for _, r in tab.iterrows():
        print("  %s %-20s n=%d r2=%s r2_cv=%s borde=%s" % (
            r["par"], r["bloque"], r["n_celdas"], r["r2"], r["r2_cv"], r["en_borde"] or "-"))
    print("  avisos de coincidencia (1e-6):", len(difs))


if __name__ == "__main__":
    main()
