# -*- coding: utf-8 -*-
"""Sens2 P3 - Paso 1: indices given-data con IC bootstrap.

Genera p3_indices.csv (formato largo), p3_ranking.csv y p3_ranking.md. Un bloque
por centro de los LHS de los estudios 3 (C1, C2) y 14 (C3, C4), ya deduplicados.
Entradas: las 9 variables no constantes del bloque + 3 dummy uniformes [0,1].
Respuestas Y1 (KALINA total), Y2 (eta), Y3 (W_net/m_b), Y2r/Y3r (en rango) e Y4 (D).
"""
import os

import numpy as np
import pandas as pd

import p3_comun as C
import p3_metodos as M


def seleccion(g, modo):
    if modo == "todos":
        return np.ones(len(g), bool)
    if modo == "kalina":
        return (g["clasificacion"] == "KALINA").to_numpy()
    if modo == "kalina_rango":
        return ((g["clasificacion"] == "KALINA") & (~g["fuera_rango"])).to_numpy()
    return (g["clasificacion"] == "CORREGIBLE").to_numpy()


def respuesta(sub, cod):
    if cod == "Y1":
        return (sub["clasificacion"] == "KALINA").astype(float).to_numpy()
    if cod in ("Y2", "Y2r"):
        return sub["eta_pct"].to_numpy(float)
    if cod in ("Y3", "Y3r"):
        return sub["wnet_mb"].to_numpy(float)
    return sub["D"].to_numpy(float)


def indices_punto(X, y, es_bin):
    p = X.shape[1]
    out = {}

    def safe(f):
        try:
            return f()
        except Exception:
            return None

    out["PRCC"] = safe(lambda: M.prcc(X, y))
    sc = safe(lambda: M.src(X, y))
    out["SRC"] = sc[0] if sc is not None else None
    out["_R2"] = sc[1] if sc is not None else np.nan
    med, mx, dl = np.full(p, np.nan), np.full(p, np.nan), np.full(p, np.nan)
    hs, et = np.full(p, np.nan), np.full(p, np.nan)
    for j in range(p):
        xj = X[:, j]
        a = safe(lambda xj=xj: M.pawn(xj, y))
        if a is not None:
            med[j], mx[j] = a
        b = safe(lambda xj=xj: M.borgonovo(xj, y))
        if b is not None:
            dl[j] = b
        c = safe(lambda xj=xj: M.hsic(xj, y))
        if c is not None:
            hs[j] = c
        d = safe(lambda xj=xj: M.eta2(xj, y))
        if d is not None:
            et[j] = d
    out.update(PAWN=med, PAWN_max=mx, delta=dl, HSIC=hs, eta2=et)
    if es_bin:
        ks = np.full(p, np.nan)
        for j in range(p):
            v = safe(lambda j=j: M.ks_stat(X[y == 1, j], X[y == 0, j]))
            if v is not None:
                ks[j] = v
        out["KS"] = ks
        lg = safe(lambda: M.logistica(X, y))
        out["LOGIT"] = np.abs(lg[0]) if lg is not None else None
    return out


def procesar(bloque, est, centro, dedup, semilla):
    g = dedup[(dedup["estudio"] == est) & (dedup["centro"] == centro)].reset_index(drop=True)
    n0 = len(g)
    rng = np.random.default_rng(C.SEMILLA + 1000 + semilla)
    X = np.column_stack([g[C.REALES].to_numpy(float), rng.random((n0, 3))])
    filas = []
    for cod, lab, modo in C.RESPUESTAS:
        mask = seleccion(g, modo)
        Xs, ys = X[mask], respuesta(g[mask], cod)
        n = len(ys)
        metodos = list(C.MET_BASE_RANGO) + ["PAWN_max"]
        es_bin = (cod == "Y1") and len(np.unique(ys)) == 2
        if cod == "Y1":
            metodos += ["KS", "LOGIT"]
        punto = indices_punto(Xs, ys, es_bin) if n >= 4 else {}
        pv = {}
        if n >= 4:
            if punto.get("HSIC") is not None:
                for j in range(len(C.VARS)):
                    pv[("HSIC", j)] = M.hsic_pval(Xs[:, j], ys)
            if es_bin:
                for j in range(len(C.VARS)):
                    pv[("KS", j)] = M.ks_pvalor(Xs[ys == 1, j], Xs[ys == 0, j])
        boot = {}
        if n >= 4:
            B = C.bootstrap_indices(n, seed=C.SEMILLA + semilla)
            for b in range(C.N_BOOT):
                o = indices_punto(Xs[B[b]], ys[B[b]], es_bin)
                for met in metodos:
                    if o.get(met) is not None:
                        boot.setdefault(met, []).append(o[met])
        for j, v in enumerate(C.VARS):
            for met in metodos:
                arr = punto.get(met) if punto else None
                if arr is None:
                    filas.append([bloque, lab, v, "no_aplica", np.nan, np.nan, np.nan,
                                  n, np.nan, "metodo no aplicable (n pequeno o varianza cero)"])
                    continue
                val = arr[j]
                if not np.isfinite(val):
                    filas.append([bloque, lab, v, "no_aplica", np.nan, np.nan, np.nan,
                                  n, np.nan, "indice no finito (varianza cero o n pequeno)"])
                    continue
                lo = hi = np.nan
                if metro := boot.get(met):
                    A = np.array(metro)[:, j]
                    A = A[np.isfinite(A)]
                    if len(A) > 0:
                        lo, hi = float(np.percentile(A, 2.5)), float(np.percentile(A, 97.5))
                filas.append([bloque, lab, v, met, float(val), lo, hi, n,
                              pv.get((met, j), np.nan), ""])
        if punto and "_R2" in punto:
            filas.append([bloque, lab, "(modelo)", "SRC_R2", punto["_R2"], np.nan, np.nan,
                          n, np.nan, ""])
    return filas


def main():
    dedup = C.cargar_dedup()
    filas = []
    for k, (bl, est, centro) in enumerate(C.BLOQUES):
        print("bloque:", bl)
        filas += procesar(bl, est, centro, dedup, 10 * k)
    os.makedirs(C.P3, exist_ok=True)
    df = pd.DataFrame(filas, columns=C.COLUMNAS)
    df.to_csv(os.path.join(C.P3, "p3_indices.csv"), index=False)
    rank = C.ranking(filas)
    rank.to_csv(os.path.join(C.P3, "p3_ranking.csv"), index=False)
    with open(os.path.join(C.P3, "p3_ranking.md"), "w", encoding="utf-8") as f:
        f.write(C.escribir_md(rank))
    print("filas indices:", len(df), "filas ranking:", len(rank))


if __name__ == "__main__":
    main()
