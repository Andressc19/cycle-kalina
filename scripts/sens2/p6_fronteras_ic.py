# -*- coding: utf-8 -*-
"""Sens2 F1 - p6_fronteras_ic: frontera de la regresion logistica con intervalo y contraste con el barrido.

Para cada bloque LHS (estudio 3: C1, C2; estudio 14: C3, C4) y cada variante
(`todas`, con NO_CONVERGIO contado como 0, y `sin_nc`, quitando NO_CONVERGIO)
ajusta una regresion logistica con las 9 variables de entrada estandarizadas
(media y desviacion del bloque) por IRLS con ridge 1e-3 sobre los coeficientes
(no sobre el intercepto). Con las otras 8 variables en el centro del bloque
obtiene la frontera de cada variable (probabilidad 0.5), la acota con 1 000
remuestreos bootstrap de filas (semilla 20261018) y la contrasta con la frontera
de los barridos de una variable de P1 (formas escalon o ventana).

Salidas: p6_fronteras_ic.csv y p6_fronteras_ic.md.
"""
import os

import numpy as np
import pandas as pd
from scipy.stats import rankdata

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))

DATOS = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P2", "p2_dataset_dedup.csv")
P1 = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P1", "p1_fronteras.csv")
SALIDA = os.path.join(RAIZ, "resultados", "2026-10-18_sens2_F1")

VARS = ["T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "eta_t", "eps_hrvg", "eps_reg", "eps_cond"]
BLOQUES = [("E3 C1 Husavik", 3, "C1 Husavik"), ("E3 C2 ancla A*", 3, "C2 ancla A*"),
           ("E14 C3 caliente 150 C", 14, "C3 caliente 150 C"), ("E14 C4 frio 110 C", 14, "C4 frio 110 C")]
CENTROS = {
    "C1 Husavik": (394.15, 278.15, 3300, 690, 0.82, 0.85, 0.85, 0.75, 0.95),
    "C2 ancla A*": (403.0, 300.15, 3000, 563.64, 0.50, 0.85, 0.85, 0.75, 0.95),
    "C3 caliente 150 C": (423.15, 280.5, 3150, 950, 0.75, 0.85, 0.85, 0.75, 0.95),
    "C4 frio 110 C": (383.15, 282.5, 3880, 910, 0.88, 0.85, 0.85, 0.75, 0.95)}
COLS = ["bloque", "variante", "variable", "coef_estandar", "error_tipico", "x_frontera", "ic_lo", "ic_hi",
        "fraccion_valida", "auc", "calidad", "frontera_barrido", "barrido_dentro_ic"]
RIDGE, ITMAX, TOL, N_BOOT, SEMILLA = 1e-3, 100, 1e-8, 1000, 20261018


def logistica(X, y, ridge=RIDGE, itmax=ITMAX, tol=TOL):
    """IRLS (Newton) con ridge sobre los coeficientes (no el intercepto): (beta, se, convergio)."""
    n, p = X.shape
    A = np.column_stack([np.ones(n), X])
    pen = np.full(p + 1, float(ridge))
    pen[0] = 0.0
    beta, conv = np.zeros(p + 1), False
    for _ in range(itmax):
        mu = 1.0 / (1.0 + np.exp(-np.clip(A @ beta, -500.0, 500.0)))
        w = np.clip(mu * (1.0 - mu), 1e-9, None)
        H = A.T @ (w[:, None] * A) + np.diag(pen)
        g = A.T @ (y - mu) - pen * beta
        try:
            paso = np.linalg.solve(H, g)
        except np.linalg.LinAlgError:
            return beta, np.full(p + 1, np.nan), False
        beta = beta + paso
        if np.max(np.abs(paso)) < tol:
            conv = True
            break
    mu = 1.0 / (1.0 + np.exp(-np.clip(A @ beta, -500.0, 500.0)))
    w = np.clip(mu * (1.0 - mu), 1e-9, None)
    try:
        se = np.sqrt(np.clip(np.diag(np.linalg.inv(A.T @ (w[:, None] * A) + np.diag(pen))), 0.0, None))
    except np.linalg.LinAlgError:
        se, conv = np.full(p + 1, np.nan), False
    return beta, se, conv


def auc_rangos(y, score):
    """AUC por la formula de rangos (Mann-Whitney)."""
    pos, neg = score[y == 1], score[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return np.nan
    r = rankdata(np.concatenate([pos, neg]))
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2.0) / (len(pos) * len(neg)))


def frontera(beta, v, media, desv, z):
    """x_v* (probabilidad 0.5) con las otras 8 variables en el centro; None si |b_v| < 1e-6."""
    bv = beta[v + 1]
    if abs(bv) < 1e-6:
        return None
    zv = -(beta[0] + sum(beta[j + 1] * z[j] for j in range(len(z)) if j != v)) / bv
    return float(media[v] + desv[v] * zv)


def bloque_variante(d, est, centro, variante):
    g = d[(d["estudio"] == est) & (d["centro"] == centro)]
    if variante == "sin_nc":
        g = g[g["clasificacion"] != "NO_CONVERGIO"]
    return g[VARS].to_numpy(float), (g["clasificacion"] == "KALINA").to_numpy(float)


def procesar(X, y, centro, rng):
    """Ajuste original, AUC, fronteras y bootstrap de las 9 variables."""
    media, desv = X.mean(axis=0), X.std(axis=0)
    desv = np.where(desv > 0, desv, 1.0)
    Xs = (X - media) / desv
    beta, se, _ = logistica(Xs, y)
    auc = auc_rangos(y, Xs @ beta[1:] + beta[0])
    z = [(centro[j] - media[j]) / desv[j] for j in range(len(VARS))]
    x0 = [frontera(beta, v, media, desv, z) for v in range(len(VARS))]
    validos, muestras = [0] * len(VARS), [[] for _ in VARS]
    idxs = rng.integers(0, len(y), size=(N_BOOT, len(y)))
    for k in range(N_BOOT):
        i = idxs[k]
        bb, _, cv = logistica(Xs[i], y[i])
        if not cv:
            continue
        for v in range(len(VARS)):
            xv = frontera(bb, v, media, desv, z)
            if xv is None or x0[v] is None or np.sign(bb[v + 1]) != np.sign(beta[v + 1]):
                continue
            validos[v] += 1
            muestras[v].append(xv)
    return beta, se, auc, x0, validos, muestras


def tabla_barrido(p1):
    """(centro, variable) -> valores de frontera de los barridos escalon o ventana."""
    p1 = p1[p1["forma"].isin(["escalon", "ventana"])]
    return {k: [float(x) for x in g["valor_frontera"]] for k, g in p1.groupby(["centro", "variable"])}


def filas_bloque(d, est, nombre, centro, variante, barrido, rng):
    X, y = bloque_variante(d, est, centro, variante)
    beta, se, auc, x0, validos, muestras = procesar(X, y, CENTROS[centro], rng)
    filas = []
    for v, var in enumerate(VARS):
        if x0[v] is None:
            continue
        vals = muestras[v]
        lo, hi = (np.percentile(vals, [2.5, 97.5]) if vals else (np.nan, np.nan))
        frac = validos[v] / float(N_BOOT)
        calidad = "aceptable" if (frac >= 0.80 and np.isfinite(auc) and auc >= 0.80) else "pobre"
        bvals = barrido.get((centro, var), [])
        dentro = "si" if (bvals and np.isfinite(lo) and np.isfinite(hi)
                          and any(lo <= b <= hi for b in bvals)) else ("no" if bvals else "")
        filas.append({"bloque": nombre, "variante": variante, "variable": var,
                      "coef_estandar": round(float(beta[v + 1]), 6), "error_tipico": round(float(se[v + 1]), 6),
                      "x_frontera": round(x0[v], 4), "ic_lo": round(float(lo), 4) if np.isfinite(lo) else np.nan,
                      "ic_hi": round(float(hi), 4) if np.isfinite(hi) else np.nan,
                      "fraccion_valida": round(frac, 3), "auc": round(float(auc), 5), "calidad": calidad,
                      "frontera_barrido": ";".join("%.6g" % b for b in bvals), "barrido_dentro_ic": dentro})
    return filas


def markdown(tab):
    l = ["# Sens2 F1 - p6_fronteras_ic: frontera con intervalo y contraste con el barrido", "",
         "Regresion logistica (respuesta 1 = KALINA) con 9 variables estandarizadas por bloque;",
         "la frontera es el valor de una variable (probabilidad 0.5) con las otras 8 en el centro.",
         "`todas` cuenta NO_CONVERGIO como 0; `sin_nc` quita las filas NO_CONVERGIO.",
         "El intervalo es el percentil 2.5-97.5 de 1 000 remuestreos bootstrap (semilla 20261018)",
         "donde el ajuste converge y el coeficiente conserva su signo. `calidad` es `aceptable` si",
         "la fraccion valida >= 0.80 y el AUC >= 0.80.", "", "## AUC por bloque y variante", "",
         "| bloque | variante | AUC |", "|---|---|---|"]
    for (bl, va), g in tab.groupby(["bloque", "variante"], sort=False):
        l.append("| %s | %s | %.4f |" % (bl, va, g["auc"].iloc[0]))
    acep = tab[tab["calidad"] == "aceptable"]
    l += ["", "## Fronteras de calidad aceptable (en llano)", "",
          "x_frontera es el valor de la variable donde la probabilidad de KALINA cruza 0.5; el",
          "intervalo es su rango de bootstrap. `barrido` es la frontera de los barridos de una",
          "variable de P1; `coincide` dice si algun valor del barrido cae dentro del intervalo.",
          "", "| bloque | variante | variable | x_frontera (IC 2.5-97.5) | barrido | coincide |",
          "|---|---|---|---|---|---|"]
    for _, r in acep.iterrows():
        l.append("| %s | %s | %s | %.4f [%.4f, %.4f] | %s | %s |" % (
            r["bloque"], r["variante"], r["variable"], r["x_frontera"], r["ic_lo"], r["ic_hi"],
            r["frontera_barrido"] or "-", r["barrido_dentro_ic"] or "-"))
    l.append("")
    return "\n".join(l)


def main():
    d = pd.read_csv(DATOS)
    barrido = tabla_barrido(pd.read_csv(P1))
    filas = []
    for nombre, est, centro in BLOQUES:
        for variante in ("todas", "sin_nc"):
            filas += filas_bloque(d, est, nombre, centro, variante, barrido, np.random.default_rng(SEMILLA))
    tab = pd.DataFrame(filas, columns=COLS)
    os.makedirs(SALIDA, exist_ok=True)
    tab.to_csv(os.path.join(SALIDA, "p6_fronteras_ic.csv"), index=False)
    with open(os.path.join(SALIDA, "p6_fronteras_ic.md"), "w", encoding="utf-8") as fh:
        fh.write(markdown(tab))
    acep = int((tab["calidad"] == "aceptable").sum())
    dentro = int(((tab["calidad"] == "aceptable") & (tab["barrido_dentro_ic"] == "si")).sum())
    print("p6_fronteras_ic.csv:", len(tab), "filas")
    print("  filas aceptables:", acep, "de", len(tab))
    print("  aceptables que coinciden con el barrido:", dentro)


if __name__ == "__main__":
    main()
