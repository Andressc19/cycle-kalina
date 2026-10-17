# -*- coding: utf-8 -*-
"""Sens2 P1 - paso 3: reglas de la region KALINA con los puntos del LHS.

Solo los estudios de muestreo LHS (3 y 14; >= 9 variables moviendose a la vez).
Por centro y "todos": (1) regresion logistica con IRLS en numpy, variables
estandarizadas y ridge 1e-6; (2) mejor corte unico (stump) por variable, por
reduccion de impureza de Gini; (3) arbol de profundidad 2 propio, con sus reglas
mas puras. Salidas: p1_reglas.csv y p1_reglas.md.
"""
import os

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
SALIDA = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P1")

ENTRADAS = ["T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "eta_t", "eta_p",
            "eps_hrvg", "eps_reg", "eps_cond"]
CENTROS = ["C1 Husavik", "C2 ancla A*", "C3 caliente 150 C", "C4 frio 110 C", "todos"]
LHS_ESTUDIOS = [3, 14]
RIDGE, MIN_N_REGLA, PUREZA = 1e-6, 30, 0.9


def sigmoide(z):
    return 1.0 / (1.0 + np.exp(-z))


def gini(y):
    return 2.0 * y.mean() * (1.0 - y.mean())


def logistica(X, y):
    """IRLS; devuelve (nombres, beta, se, convergio). Descarta columnas constantes."""
    sd = X.std(axis=0)
    keep = sd > 0
    if keep.sum() == 0:
        return [], np.array([]), np.array([]), False
    nombres = [ENTRADAS[j] for j in np.where(keep)[0]]
    Z = (X[:, keep] - X[:, keep].mean(axis=0)) / sd[keep]
    Xd = np.column_stack([np.ones(len(y)), Z])
    beta = np.zeros(Xd.shape[1])
    conv, A = False, None
    for _ in range(200):
        eta = Xd @ beta
        p = sigmoide(eta)
        s = np.clip(p * (1 - p), 1e-9, None)
        z = eta + (y - p) / s
        A = Xd.T @ (Xd * s[:, None]) + RIDGE * np.eye(Xd.shape[1])
        try:
            nuevo = np.linalg.solve(A, Xd.T @ (s * z))
        except np.linalg.LinAlgError:
            return nombres, beta, np.full(len(beta), np.nan), False
        if np.max(np.abs(nuevo - beta)) < 1e-8:
            beta, conv = nuevo, True
            break
        beta = nuevo
    try:
        se = np.sqrt(np.diag(np.linalg.inv(A)))
    except np.linalg.LinAlgError:
        se = np.full(len(beta), np.nan)
    return ["(intercepto)"] + nombres, beta, se, conv


def stump(x, y):
    """Mejor corte unico: (umbral, direccion, ganancia). Direccion = lado KALINA."""
    us = np.unique(x[~np.isnan(x)])
    if len(us) < 2:
        return None
    g0, mejor = gini(y), None
    for t in (us[:-1] + us[1:]) / 2.0:
        L = x <= t
        nl, nr = int(L.sum()), int((~L).sum())
        if nl == 0 or nr == 0:
            continue
        gain = g0 - (nl / len(y)) * gini(y[L]) - (nr / len(y)) * gini(y[~L])
        if mejor is None or gain > mejor[2]:
            direccion = "<=" if y[L].mean() >= y[~L].mean() else ">"
            mejor = (float(t), direccion, float(gain))
    return mejor


def mejor_corte(X, y, usadas=()):
    mejor = None
    for j in range(X.shape[1]):
        if j in usadas:
            continue
        r = stump(X[:, j], y)
        if r is not None and (mejor is None or r[2] > mejor[2]):
            mejor = (ENTRADAS[j], r[0], r[2], j)
    return mejor


def crecer(X, y, cond, prof, hojas, usadas=()):
    if prof == 0 or len(np.unique(y)) == 1:
        hojas.append((list(cond), len(y), int(y.sum()))); return
    b = mejor_corte(X, y, usadas)
    if b is None or b[2] <= 0:
        hojas.append((list(cond), len(y), int(y.sum()))); return
    nombre, t, _gain, j = b
    L = X[:, j] <= t
    crecer(X[L], y[L], cond + ["%s <= %g" % (nombre, t)], prof - 1, hojas, usadas + (j,))
    crecer(X[~L], y[~L], cond + ["%s > %g" % (nombre, t)], prof - 1, hojas, usadas + (j,))


def reglas_arbol(X, y):
    hojas = []; crecer(X, y, [], 2, hojas)
    kal, nok = [], []
    for cond, n, k in hojas:
        p = k / n if n else 0.0
        pur = max(p, 1 - p)
        reg = " Y ".join(cond) if cond else "(sin condicion)"
        item = (reg, n, k, p, pur)
        if n >= MIN_N_REGLA and pur >= PUREZA:
            (kal if p >= PUREZA else nok).append(item)
    kal.sort(key=lambda r: (-r[4], -r[1]))
    nok.sort(key=lambda r: (-r[4], -r[1]))
    return kal[:3], nok[:3]


def filas(centro, s):
    s = s.dropna(subset=ENTRADAS)
    X = s[ENTRADAS].to_numpy(float)
    y = s["kalina"].to_numpy(float)
    out = []
    nombres, beta, se, conv = logistica(X, y)
    for i, nom in enumerate(nombres):
        out.append({"seccion": "logistica", "centro": centro, "orden": i + 1,
                    "variable": nom, "termino": nom, "coef": beta[i], "se": se[i],
                    "signo": np.sign(beta[i]), "convergio": conv})
    stumps = [(v, r[0], r[1], r[2]) for j, v in enumerate(ENTRADAS)
              for r in [stump(X[:, j], y)] if r is not None]
    stumps.sort(key=lambda r: -r[3])
    for i, (var, t, d, g) in enumerate(stumps):
        out.append({"seccion": "stump", "centro": centro, "orden": i + 1,
                    "variable": var, "umbral": t, "direccion": d, "ganancia": g})
    kal, nok = reglas_arbol(X, y)
    for clase, lista in (("KALINA", kal), ("no-KALINA", nok)):
        for i, (reg, n, k, p, pur) in enumerate(lista):
            out.append({"seccion": "arbol", "centro": centro, "orden": i + 1,
                        "variable": clase, "regla": reg, "n": n, "n_kalina": k,
                        "p_kalina": p, "pureza": pur})
    return out, conv, stumps


def main():
    os.makedirs(SALIDA, exist_ok=True)
    d = pd.read_csv(os.path.join(SALIDA, "p1_dataset.csv"))
    d["kalina"] = d["kalina"].astype(bool)
    lhs = d[d["estudio"].isin(LHS_ESTUDIOS)]
    todas, resumen = [], {}
    for c in CENTROS:
        s = lhs if c == "todos" else lhs[lhs["centro"] == c]
        s = s.dropna(subset=ENTRADAS)
        f, conv, stumps = filas(c, s)
        todas += f
        resumen[c] = (len(s), int(s["kalina"].sum()), conv, stumps)
    pd.DataFrame(todas).to_csv(os.path.join(SALIDA, "p1_reglas.csv"), index=False)
    with open(os.path.join(SALIDA, "p1_reglas.md"), "w", encoding="utf-8") as f:
        f.write(md(resumen, todas))
    for c in CENTROS:
        n, k, conv, st = resumen[c]
        print(c, "n=%d KALINA=%d logistica_convergio=%s" % (n, k, conv),
              "mejor stump:", st[0][0] if st else "-")


def md(resumen, todas):
    L = ["# Sens2 P1 - paso 3: reglas de la region KALINA (solo LHS)", "",
         "Solo puntos de los estudios LHS 3 y 14. Cada seccion se calcula por centro y para",
         "todos los puntos LHS juntos.", ""]
    for c in CENTROS:
        n, k, conv, st = resumen[c]
        L += ["## %s" % c, "",
              "Puntos %d, KALINA %d (%.1f %%). Regresion logistica: %s." % (
                  n, k, 100.0 * k / n if n else 0,
                  "convergio" if conv else "NO convergio"),
              "", "### Cortes unicos (stump), mejor primero", "",
              "| lugar | variable | umbral | lado KALINA | ganancia Gini |", "|---|---|---|---|---|"]
        for i, (var, t, dd, g) in enumerate(st[:5]):
            L.append("| %d | %s | %g | %s | %.4f |" % (i + 1, var, t, dd, g))
        L += ["", "### Reglas del arbol (pureza >= 0.9, n >= 30)", ""]
        for clase in ("KALINA", "no-KALINA"):
            rr = [r for r in todas if r.get("seccion") == "arbol" and r["centro"] == c
                  and r["variable"] == clase]
            L.append("**%s:**" % clase)
            if not rr:
                L.append("- (ninguna regla cumple pureza >= 0.9 con n >= 30)")
            for r in rr:
                L.append("- `%s` -> n = %d, KALINA = %.0f %% (pureza %.2f)" % (
                    r["regla"], r["n"], 100.0 * r["p_kalina"], r["pureza"]))
            L.append("")
    L.append("Nota: el signo de la logistica es el efecto sobre P(KALINA) con las demas variables")
    L.append("fijas en su media (variables estandarizadas); las variables constantes del bloque se")
    L.append("omiten y se listan solo las que quedan.")
    return "\n".join(L)


if __name__ == "__main__":
    main()
