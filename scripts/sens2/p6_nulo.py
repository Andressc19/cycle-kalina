# -*- coding: utf-8 -*-
"""Sens2 F1 (1.1, 1.2, 1.6) - nulo por permutacion y correccion de Benjamini-Hochberg de los indices globales.

Para cada bloque LHS y respuesta (Y1, Y2, Y3) calcula los indices PRCC, SRC, PAWN, delta, HSIC, eta2 (y KS en Y1) de las 9
variables reales y 3 dummy, y su p-valor por B_PERM permutaciones de la respuesta. BH por bloque y respuesta (familia
principal) y por respuesta entre bloques. Una variable es `distinguible_fdr` si pasa BH (q < 0.05) en al menos 2 metodos.
Se repite en la caja comun de rangos de los 4 LHS. Salidas: p6_nulo_perm.csv, p6_indices_fdr.csv, p6_nulo_perm.md.
"""
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p3_comun as C  # noqa: E402
import p3_metodos as M  # noqa: E402
import p6_comun as K  # noqa: E402


def _kern(x):
    return M._centrar(M._kernel(x))


def estadisticos(X, y, es_bin, Kc, nK, Lc, nL, perm):
    """Indices de las columnas de X frente a y[perm]; HSIC con los nucleos precalculados."""
    yp = y[perm]
    p = X.shape[1]
    o = {"PRCC": np.abs(M.prcc(X, yp)), "SRC": np.abs(M.src(X, yp)[0])}
    Lp = Lc[np.ix_(perm, perm)]
    o["PAWN"], o["delta"], o["HSIC"], o["eta2"] = (np.full(p, np.nan) for _ in range(4))
    for j in range(p):
        xj = X[:, j]
        o["PAWN"][j] = M.pawn(xj, yp)[0]
        o["delta"][j] = M.borgonovo(xj, yp)
        o["eta2"][j] = M.eta2(xj, yp)
        o["HSIC"][j] = float((Kc[j] * Lp).sum() / (nK[j] * nL)) if nK[j] * nL > 0 else np.nan
    if es_bin:
        o["KS"] = np.array([M.ks_stat(X[yp == 1, j], X[yp == 0, j]) for j in range(p)])
    return o


def procesar(nombre, g, cod, rng, caja):
    mask, y = K.respuesta(g, cod)
    n0 = int(mask.sum())
    X = np.column_stack([g[K.REALES].to_numpy(float), rng.random((len(g), 3))])[mask]
    y = y[mask]
    if n0 < 30 or np.std(y) == 0:
        return []
    es_bin = cod == "Y1"
    nombres = K.REALES + C.DUMMIES
    Kc = [_kern(X[:, j]) for j in range(X.shape[1])]
    nK = [float(np.sqrt((k * k).sum())) for k in Kc]
    Lc = M._centrar(M._kernel(y))
    nL = float(np.sqrt((Lc * Lc).sum()))
    idn = np.arange(len(y))
    obs = estadisticos(X, y, es_bin, Kc, nK, Lc, nL, idn)
    nulo = {m: [] for m in obs}
    for _ in range(K.B_PERM):
        s = estadisticos(X, y, es_bin, Kc, nK, Lc, nL, rng.permutation(len(y)))
        for m in obs:
            nulo[m].append(s[m])
    filas = []
    for m in obs:
        A = np.array(nulo[m])
        for j, v in enumerate(nombres):
            ob = obs[m][j]
            pv = (1.0 + np.sum(A[:, j] >= ob - 1e-12)) / (K.B_PERM + 1.0) if np.isfinite(ob) else np.nan
            filas.append([caja, nombre, K.RESP[cod], v, "real" if v in K.REALES else "dummy", m, K.FAMILIA[m], n0, ob, pv])
    return filas


def main():
    t0 = time.time()
    todas = []
    for caja in (False,):   # la caja comun de los 4 LHS queda con 1 a 9 puntos por bloque (ver nota_caja): no se calcula
        rng = np.random.default_rng(K.SEMILLA + (1 if caja else 0))
        for nombre, g in K.bloques(caja):
            for cod in ("Y1", "Y2", "Y3"):
                todas += procesar(nombre, g, cod, rng, "si" if caja else "no")
            print("caja=%s %s listo (%.0f s)" % (caja, nombre, time.time() - t0), flush=True)
    df = pd.DataFrame(todas, columns=["caja", "bloque", "respuesta", "variable", "tipo", "metodo", "familia_metodo", "n", "obs", "p_perm"])
    df["q_bloque"] = np.nan
    df["q_respuesta"] = np.nan
    r = df["tipo"] == "real"
    for _, ix in df[r].groupby(["caja", "bloque", "respuesta"]).groups.items():
        df.loc[ix, "q_bloque"] = K.bh(df.loc[ix, "p_perm"])
    for _, ix in df[r].groupby(["caja", "respuesta"]).groups.items():
        df.loc[ix, "q_respuesta"] = K.bh(df.loc[ix, "p_perm"])
    os.makedirs(K.OUT, exist_ok=True)
    df.to_csv(os.path.join(K.OUT, "p6_nulo_perm.csv"), index=False)
    resumen(df)
    print("listo en %.0f s; filas %d" % (time.time() - t0, len(df)))


def nota_caja():
    """Tamaño de cada LHS dentro de la caja comun de rangos de los 4 bloques (1.6): inviable si queda con menos de 30 puntos."""
    n = [(nombre, len(g)) for nombre, g in K.bloques(True)]
    return ["## Caja comun de rangos (comparar magnitudes entre bloques)", "",
            "Puntos de cada LHS que caen dentro del rango comun de las 9 variables de los 4 bloques: " +
            ", ".join("%s %d" % x for x in n) + ".",
            "Quedan menos de 30 puntos por bloque, asi que no se calculan indices en la caja comun: las magnitudes de los indices no se "
            "comparan entre bloques; solo se usan los rangos y las pruebas dentro de cada bloque.", ""]


def resumen(df):
    rk = pd.read_csv(os.path.join(C.P3, "p3_ranking.csv"))
    inv = {v: k for k, v in K.RESP.items()}
    sal = []
    for (caja, bl, rs, v), g in df[df["tipo"] == "real"].groupby(["caja", "bloque", "respuesta", "variable"]):
        sig = g[g["q_bloque"] < K.Q]
        old = rk[(rk["bloque"] == bl) & (rk["respuesta"].str.startswith(inv[rs])) & (rk["variable"] == v)]
        sal.append([caja, bl, rs, v, int(g["n"].iloc[0]), len(sig), ";".join(sig["metodo"]), len(sig) >= 2,
                    bool(old["distinguible"].iloc[0]) if len(old) else np.nan,
                    float(g["p_perm"].min()), float(g["q_bloque"].min())])
    s = pd.DataFrame(sal, columns=["caja", "bloque", "respuesta", "variable", "n", "n_metodos_sig", "metodos_sig",
                                   "distinguible_fdr", "distinguible_p3", "p_min", "q_min"])
    s.to_csv(os.path.join(K.OUT, "p6_indices_fdr.csv"), index=False)
    d = df[df["tipo"] == "dummy"]
    cal = d.groupby("caja")["p_perm"].apply(lambda p: float((p < 0.05).mean()))
    md = ["# Sens2 F1 - nulo por permutacion y Benjamini-Hochberg", "",
          "%d permutaciones por indice; semilla %d; q = %.2f por bloque y respuesta; distinguible = q < %.2f en al menos 2 metodos."
          % (K.B_PERM, K.SEMILLA, K.Q, K.Q), "",
          "Calibracion: fraccion de pruebas con p < 0.05 en las 3 variables dummy (debe ser cercana a 0.05): " +
          ", ".join("caja=%s %.3f" % (k, v) for k, v in cal.items()), ""]
    for caja in ("no",):
        t = s[(s["caja"] == caja) & (s["respuesta"].notna())]
        md.append("## Caja comun = %s" % caja)
        md.append("")
        md.append("| respuesta | distinguibles con BH | distinguibles con el criterio anterior (P3) | en ambos |")
        md.append("|---|---|---|---|")
        for rs, g in t.groupby("respuesta"):
            a, b = g["distinguible_fdr"].astype(bool), g["distinguible_p3"].fillna(False).astype(bool)
            md.append("| %s | %d | %d | %d |" % (rs, a.sum(), b.sum(), (a & b).sum()))
        md.append("")
    md += nota_caja()
    with open(os.path.join(K.OUT, "p6_nulo_perm.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")


if __name__ == "__main__":
    main()
