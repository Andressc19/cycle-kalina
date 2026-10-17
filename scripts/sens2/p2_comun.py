# -*- coding: utf-8 -*-
"""Sens2 P2 - modulo comun.

Carga el dataset de P1, lo DEDUPLICA (mismas 10 entradas y centro, conservando la
primera aparicion), anade `m_b` (leido del cargador de Sensibilidad 1) y el W_net
especifico `wnet_mb = Wnet / m_b`, y guarda `p2_dataset_dedup.csv`.

Utilidades: resumenes de percentiles, bootstrap de la diferencia de medianas (semilla
fija 20261017, 1000 remuestreos, IC 95 %), delta de Cliff por rangos, KS de scipy y
normalizacion de las 10 entradas al rango [0, 1] observado.
"""
import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp, rankdata

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))

P1 = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P1", "p1_dataset.csv")
SALIDA = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P2")
DEDUP = os.path.join(SALIDA, "p2_dataset_dedup.csv")

SEMILLA = 20261017
N_BOOT = 1000

ENTRADAS = ["T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "eta_t", "eta_p",
            "eps_hrvg", "eps_reg", "eps_cond"]
VIOLS = ["viol_O1", "viol_O2", "viol_O3", "viol_O5"]
VARIABLES = ["eta_pct", "wnet_mb", "rp", "qreg_qi", "dh_turb", "q4"]
SIN_CENTRO = "Sin centro (muestreo o malla)"
REF_TOTAL = "KALINA (total)"
REF_RANGO = "KALINA en rango experimental"
ATIPICOS = ["C1-B6-0236", "N1-T090-10", "N7A-C3-P_alta-001", "N7A-C4-P_alta-001",
            "N7A-C4-eps_hrvg-003", "N9-C4-B6-0004", "N8-C4-0141"]


def cargar_dedup():
    """Dataset de P1 deduplicado con m_b y wnet_mb; crea el CSV si no existe."""
    if os.path.exists(DEDUP):
        return pd.read_csv(DEDUP)
    import x1_cargar as x  # noqa: E402  (import perezoso, solo si hay que crear el CSV)
    d = pd.read_csv(P1)
    mb = x.cargar_todo()[["estudio", "id_punto", "m_b"]]
    d = d.merge(mb, on=["estudio", "id_punto"], how="left")
    d["centro"] = d["centro"].fillna(SIN_CENTRO)
    n0 = len(d)
    d = d.drop_duplicates(ENTRADAS + ["centro"], keep="first").reset_index(drop=True)
    d["wnet_mb"] = d["Wnet"] / d["m_b"]
    os.makedirs(SALIDA, exist_ok=True)
    d.to_csv(DEDUP, index=False)
    print("dataset P1:", n0, "filas; deduplicado:", len(d),
          "(quitadas", n0 - len(d), ")")
    return d


def grupos_centro(df):
    """Centros presentes, en el orden C1..C4 y luego el grupo sin centro."""
    conocidos = ["C1 Husavik", "C2 ancla A*", "C3 caliente 150 C", "C4 frio 110 C"]
    presentes = list(df["centro"].unique())
    orden = [c for c in conocidos if c in presentes]
    resto = [c for c in presentes if c not in conocidos]
    return orden + sorted(resto)


def etiqueta_centro(c):
    return SIN_CENTRO if (not isinstance(c, str) or c == "") else c


def resumen(x):
    """(n, mediana, P10, P90) ignorando NaN."""
    x = np.asarray(pd.to_numeric(pd.Series(x), errors="coerce"), float)
    x = x[np.isfinite(x)]
    if len(x) == 0:
        return (0, np.nan, np.nan, np.nan)
    return (int(len(x)), float(np.median(x)),
            float(np.percentile(x, 10)), float(np.percentile(x, 90)))


def ks(a, b):
    """Estadistico KS y p-valor (scipy.stats.ks_2samp)."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) == 0 or len(b) == 0:
        return (np.nan, np.nan)
    r = ks_2samp(a, b)
    return (float(r.statistic), float(r.pvalue))


def cliff_delta(a, b):
    """Delta de Cliff por rangos (con empates a media); sin bucles O(n^2)."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) == 0 or len(b) == 0:
        return np.nan
    r = rankdata(np.concatenate([a, b]))
    na = len(a)
    u = r[:na].sum() - na * (na + 1) / 2.0
    return float(2.0 * u / (na * len(b)) - 1.0)


def bootstrap_dif_medianas(a, b, n_boot=N_BOOT):
    """IC 95 % de mediana(a) - mediana(b) por remuestreo con semilla fija."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) == 0 or len(b) == 0:
        return (np.nan, np.nan)
    rng = np.random.default_rng(SEMILLA)
    da = rng.choice(a, size=(n_boot, len(a)), replace=True)
    db = rng.choice(b, size=(n_boot, len(b)), replace=True)
    dif = np.median(da, axis=1) - np.median(db, axis=1)
    return (float(np.percentile(dif, 2.5)), float(np.percentile(dif, 97.5)))


def m_b_por_estudio():
    """{estudio: [valores de m_b]} en el dataset completo de P1 (antes de deduplicar)."""
    import x1_cargar as x  # noqa: E402
    d = x.cargar_todo()
    g = {}
    for e, s in d.groupby("estudio"):
        g[int(e)] = sorted(float(v) for v in s["m_b"].dropna().unique())
    return g


def limites_normalizacion(df):
    """(min, max) observados de cada entrada en el dataset deduplicado."""
    return {v: (float(df[v].min()), float(df[v].max())) for v in ENTRADAS}


def matriz_norm(df, lim):
    """Matriz (n, 10) con cada entrada llevada a [0, 1] con su min/max observado."""
    m = np.empty((len(df), len(ENTRADAS)), float)
    for j, v in enumerate(ENTRADAS):
        lo, hi = lim[v]
        rango = hi - lo
        col = df[v].to_numpy(float)
        m[:, j] = (col - lo) / rango if rango > 0 else 0.0
    return m


def mas_cercano_l1(c_norm, k_norm, bloque=200):
    """Indice y distancia L1 del KALINA mas cercano para cada fila de `c_norm`."""
    n = len(c_norm)
    idx = np.empty(n, dtype=np.int64)
    dist = np.empty(n, float)
    for i in range(0, n, bloque):
        c = c_norm[i:i + bloque]
        d = np.abs(c[:, None, :] - k_norm[None, :, :]).sum(axis=2)
        idx[i:i + bloque] = d.argmin(axis=1)
        dist[i:i + bloque] = d.min(axis=1)
    return idx, dist


def violacion_dominante(fila):
    """Nombre(s) de la mayor de viol_O1/O2/O3/O5; empates se unen con '+'."""
    vals = {v: fila.get(v, np.nan) for v in VIOLS}
    fin = [v for v in VIOLS if np.isfinite(vals[v])]
    if not fin:
        return "sin dato"
    mx = max(vals[v] for v in fin)
    if mx <= 0:
        return "sin violacion"
    return "+".join(v for v in VIOLS if vals[v] == mx)
