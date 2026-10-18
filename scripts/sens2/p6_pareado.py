# -*- coding: utf-8 -*-
"""Sens2 F1 - A2b, Parte 1: comparacion pareada CORREGIBLE <-> KALINA mas cercano.

Para cada CORREGIBLE de los cuatro bloques con centro se busca el KALINA (total) mas
cercano por distancia L1 sobre las 10 entradas normalizadas al min/max del dataset
completo, en dos variantes: mismo centro, y mismo centro y mismo diseno (LHS =
estudios 3 y 14; otros = el resto). Se resume d_eta = eta_vecino - eta_corregible y
d_wnet = wnet_vecino - wnet_corregible por grupo, con IC 95 % por bootstrap percentil
(1000 remuestreos, semilla 20261018). Salidas: p6_pareado.csv y p6_pareado.md.

Control: la variante mismo_centro, grupo todos (solo los cuatro bloques con centro),
debe dar una mediana de d_eta dentro de +/-0.05 de -0.6404857320312551 (fila
seccion=eta, centro=todos de p2_distancia_resumen.csv). Si no, se reporta.
"""
import os

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
P2 = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P2", "p2_dataset_dedup.csv")
SALIDA = os.path.join(RAIZ, "resultados", "2026-10-18_sens2_F1")
ENTRADAS = ["T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "eta_t", "eta_p",
            "eps_hrvg", "eps_reg", "eps_cond"]
CENTROS = ["C1 Husavik", "C2 ancla A*", "C3 caliente 150 C", "C4 frio 110 C"]
SIN_CENTRO = "Sin centro (muestreo o malla)"
LHS_ESTUDIOS = [3, 14]
DISENOS = ["LHS", "otros"]
VIOLS = ["O1", "O2", "otra"]
VARIABLES = ["d_eta", "d_wnet"]
SEMILLA = 20261018
N_BOOT = 1000
BLOQUE = 200
CONTROL = -0.6404857320312551
TOL_CONTROL = 0.05
COLS = ["variante", "grupo", "variable", "n", "mediana", "ic_med_lo", "ic_med_hi",
        "media", "ic_media_lo", "ic_media_hi"]


def cargar():
    d = pd.read_csv(P2)
    d["centro"] = d["centro"].fillna(SIN_CENTRO)
    d["diseno"] = np.where(d["estudio"].isin(LHS_ESTUDIOS), "LHS", "otros")
    return d.reset_index(drop=True)


def matriz_norm(d):
    m = np.empty((len(d), len(ENTRADAS)), float)
    for j, v in enumerate(ENTRADAS):
        col = d[v].to_numpy(float)
        lo, hi = np.nanmin(col), np.nanmax(col)
        m[:, j] = (col - lo) / (hi - lo) if hi > lo else 0.0
    return m


def vecino(M, cor_idx, kal_idx):
    """Indice (posicional) del KALINA mas cercano por L1 para cada CORREGIBLE."""
    c = M[cor_idx]
    k = M[kal_idx]
    pos = np.empty(len(c), dtype=np.int64)
    for i in range(0, len(c), BLOQUE):
        blk = c[i:i + BLOQUE]
        dist = np.abs(blk[:, None, :] - k[None, :, :]).sum(axis=2)
        pos[i:i + BLOQUE] = dist.argmin(axis=1)
    return kal_idx[pos]


def violacion(fila):
    v1 = float(fila["viol_O1"])
    v2 = float(fila["viol_O2"])
    if np.isfinite(v1) and np.isfinite(v2):
        if v2 >= v1 and v2 > 0:
            return "O2"
        if v1 > v2:
            return "O1"
    return "otra"


def pares(d, M, variante):
    clave = ["centro"] if variante == "mismo_centro" else ["centro", "diseno"]
    filas = []
    for _, g in d.groupby(clave, sort=True):
        cor = g[g["clasificacion"] == "CORREGIBLE"]
        kal = g[g["kalina"]]
        if len(cor) == 0 or len(kal) == 0:
            continue
        v = vecino(M, cor.index.to_numpy(), kal.index.to_numpy())
        eta_c = cor["eta_pct"].to_numpy(float)
        eta_v = d["eta_pct"].to_numpy(float)[v]
        w_c = cor["wnet_mb"].to_numpy(float)
        w_v = d["wnet_mb"].to_numpy(float)[v]
        for i in range(len(cor)):
            filas.append({"centro": cor["centro"].iloc[i],
                          "diseno": cor["diseno"].iloc[i],
                          "viol": violacion(cor.iloc[i]),
                          "d_eta": eta_v[i] - eta_c[i],
                          "d_wnet": w_v[i] - w_c[i]})
    return pd.DataFrame(filas)


def boot(v, rng):
    n = len(v)
    med = float(np.median(v))
    mean = float(np.mean(v))
    if n <= 1:
        return med, med, med, mean, mean, mean
    s = v[rng.integers(0, n, size=(N_BOOT, n))]
    bm = np.median(s, axis=1)
    ba = s.mean(axis=1)
    return (med, float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5)),
            mean, float(np.percentile(ba, 2.5)), float(np.percentile(ba, 97.5)))


def grupos(pp):
    g = [("todos", pp)]
    g += [(cen, pp[pp["centro"] == cen]) for cen in CENTROS]
    g += [(dis, pp[pp["diseno"] == dis]) for dis in DISENOS]
    g += [(vi, pp[pp["viol"] == vi]) for vi in VIOLS]
    return g


def resumir(pp, variante):
    filas = []
    for nombre, sub in grupos(pp):
        for var in VARIABLES:
            v = sub[var].to_numpy(float)
            v = v[np.isfinite(v)]
            if len(v) == 0:
                continue
            med, mlo, mhi, mean, alo, ahi = boot(v, np.random.default_rng(SEMILLA))
            filas.append({"variante": variante, "grupo": nombre, "variable": var,
                          "n": len(v), "mediana": med, "ic_med_lo": mlo,
                          "ic_med_hi": mhi, "media": mean, "ic_media_lo": alo,
                          "ic_media_hi": ahi})
    return filas


def markdown(tab, med4, med5):
    ok = abs(med4 - CONTROL) <= TOL_CONTROL
    e = tab[(tab["variable"] == "d_eta")]
    filas = []
    for _, r in e.iterrows():
        filas.append([r["variante"], r["grupo"], int(r["n"]),
                      "%.4f" % r["mediana"],
                      "[%.4f, %.4f]" % (r["ic_med_lo"], r["ic_med_hi"])])
    l = ["# Sens2 F1 - A2b, Parte 1: comparacion pareada CORREGIBLE frente a KALINA", "",
         "Para cada CORREGIBLE con centro se toma el KALINA (total) mas cercano por",
         "distancia L1 (10 entradas al rango [0, 1] del dataset completo). d_eta es",
         "eta(vecino) - eta(CORREGIBLE): positivo quiere decir que el KALINA cercano rinde",
         "mas que el CORREGIBLE. IC 95 % por bootstrap percentil (1000, semilla 20261018).", "",
         "## d_eta por grupo", ""]
    l.append("| variante | grupo | n | mediana | IC 95 % mediana |")
    l.append("|---|---|---|---|---|")
    for f in filas:
        l.append("| " + " | ".join(str(c) for c in f) + " |")
    l += ["", "## Control", ""]
    l.append("Mediana de d_eta (mismo_centro, grupo todos, solo los cuatro bloques con "
             "centro): **%.4f** (objetivo %.4f +/- %.2f)." % (med4, CONTROL, TOL_CONTROL))
    l.append("Se cumple el control." if ok else
             "No se cumple el control: la mediana queda fuera del margen.")
    l.append("Si se incluye ademas el bloque sin centro (los cinco bloques juntos), la "
             "mediana de d_eta es %.4f, que es el valor de la fila de referencia." % med5)
    l += ["", "d_wnet (mismo esquema de grupos y de IC) esta en `p6_pareado.csv`, junto con",
          "la media y los limites de cada grupo.", ""]
    return "\n".join(l), ok


def main():
    d = cargar()
    M = matriz_norm(d)
    pp1 = pares(d, M, "mismo_centro")
    pp2 = pares(d, M, "mismo_centro_y_diseno")
    base1 = pp1[pp1["centro"].isin(CENTROS)]
    base2 = pp2[pp2["centro"].isin(CENTROS)]
    filas = resumir(base1, "mismo_centro") + resumir(base2, "mismo_centro_y_diseno")
    tab = pd.DataFrame(filas)[COLS]
    med4 = float(np.median(base1["d_eta"].dropna().to_numpy(float)))
    med5 = float(np.median(pp1["d_eta"].dropna().to_numpy(float)))
    os.makedirs(SALIDA, exist_ok=True)
    tab.to_csv(os.path.join(SALIDA, "p6_pareado.csv"), index=False)
    texto, ok = markdown(tab, med4, med5)
    with open(os.path.join(SALIDA, "p6_pareado.md"), "w", encoding="utf-8") as f:
        f.write(texto)
    print("p6_pareado.csv:", len(tab), "filas")
    print("control mismo_centro/todos mediana d_eta: %.4f -> %s" % (
        med4, "OK" if ok else "FUERA"))
    print("mismo_centro/todos con el bloque sin centro:", "%.4f" % med5)


if __name__ == "__main__":
    main()
