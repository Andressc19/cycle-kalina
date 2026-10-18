# -*- coding: utf-8 -*-
"""Sens2 P3 - metodos given-data de sensibilidad (numpy/scipy, sin scikit-learn).

PRCC, SRC, KS/RSA, PAWN, delta de Borgonovo, HSIC normalizado (CKA), eta^2 y
regresion logistica estandarizada (IRLS con ridge 1e-6). Constantes y utilidades
compartidas viven en `p3_comun.py`.
"""
import numpy as np
from scipy.stats import rankdata, ks_2samp

from p3_comun import BINS, SEMILLA, N_PERM


def _ranks(Mx):
    Mx = np.asarray(Mx, float)
    if Mx.ndim == 1:
        return rankdata(Mx)
    return np.column_stack([rankdata(Mx[:, j]) for j in range(Mx.shape[1])])


def prcc(X, y):
    """Correlacion parcial de rangos (residuos por minimos cuadrados)."""
    X, y = np.asarray(X, float), np.asarray(y, float)
    Rx, Ry = _ranks(X), rankdata(y)
    n, p = Rx.shape
    out = np.full(p, np.nan)
    if n <= p + 1:
        return out
    for j in range(p):
        A = np.column_stack([np.ones(n), Rx[:, [k for k in range(p) if k != j]]])
        ey = Ry - A @ np.linalg.lstsq(A, Ry, rcond=None)[0]
        ex = Rx[:, j] - A @ np.linalg.lstsq(A, Rx[:, j], rcond=None)[0]
        if np.std(ex) > 0 and np.std(ey) > 0:
            out[j] = float(np.corrcoef(ex, ey)[0, 1])
    return out


def src(X, y):
    """Coeficientes de regresion estandarizados y R^2 del modelo lineal."""
    X, y = np.asarray(X, float), np.asarray(y, float)
    sx, sy = X.std(axis=0), y.std()
    if sy <= 0 or np.any(sx <= 0):
        return np.full(X.shape[1], np.nan), np.nan
    Xs, ys = (X - X.mean(axis=0)) / sx, (y - y.mean()) / sy
    A = np.column_stack([np.ones(len(y)), Xs])
    b = np.linalg.lstsq(A, ys, rcond=None)[0]
    r = ys - A @ b
    tot = ((ys - ys.mean()) ** 2).sum()
    return b[1:], (1.0 - (r @ r) / tot if tot > 0 else np.nan)


def ks_stat(a, b):
    """Estadistico KS de dos muestras (ECDF por searchsorted; sin p-valor)."""
    a, b = np.sort(np.asarray(a, float)), np.sort(np.asarray(b, float))
    if len(a) == 0 or len(b) == 0:
        return np.nan
    d = np.concatenate([a, b])
    ca = np.searchsorted(a, d, side="right") / len(a)
    cb = np.searchsorted(b, d, side="right") / len(b)
    return float(np.max(np.abs(ca - cb)))


def ks_pvalor(a, b):
    if len(a) == 0 or len(b) == 0:
        return np.nan
    return float(ks_2samp(np.asarray(a, float), np.asarray(b, float)).pvalue)


def _clases(x, bins=BINS):
    x = np.asarray(x, float)
    lab = np.empty(len(x), int)
    o = np.argsort(x, kind="mergesort")
    lab[o] = (np.arange(len(x)) * bins) // len(x)
    return lab


def pawn(x, y, bins=BINS):
    """KS entre la CDF global de y y la de cada rebanada de x: (mediana, maximo)."""
    lab, y = _clases(x, bins), np.asarray(y, float)
    ks = [ks_stat(y, y[lab == i]) for i in range(bins) if (lab == i).sum() >= 2]
    return (np.nan, np.nan) if not ks else (float(np.median(ks)), float(np.max(ks)))


def eta2(x, y, bins=BINS):
    """Razon de correlacion: varianza entre rebanadas / varianza total."""
    lab, y = _clases(x, bins), np.asarray(y, float)
    gm = y.mean()
    bt = sum(len(yi) * (yi.mean() - gm) ** 2 for yi in (y[lab == i] for i in range(bins)) if len(yi))
    tot = ((y - gm) ** 2).sum()
    return float(bt / tot) if tot > 0 else np.nan


def _cajas_y(y, bins=BINS):
    y = np.asarray(y, float)
    uy = np.unique(y)
    if len(uy) <= bins:
        return np.searchsorted(uy, y), len(uy)
    e = np.unique(np.quantile(y, np.linspace(0, 1, bins + 1)))
    return np.clip(np.searchsorted(e, y, side="right") - 1, 0, len(e) - 2), len(e) - 1


def borgonovo(x, y, bins=BINS):
    """delta de Borgonovo given-data: 10 rebanadas de x y cajas de y."""
    lab, y = _clases(x, bins), np.asarray(y, float)
    ly, k = _cajas_y(y, bins)
    if k < 2:
        return np.nan
    n = len(y)
    fy = np.bincount(ly, minlength=k) / n
    delta = 0.0
    for i in range(bins):
        m = lab == i
        if m.sum() == 0:
            continue
        fi = np.bincount(ly[m], minlength=k) / m.sum()
        delta += (m.sum() / n) * np.abs(fy - fi).sum()
    return float(0.5 * delta)


def _kernel(x):
    x = np.asarray(x, float)
    n = len(x)
    d = np.abs(x[:, None] - x[None, :])
    s = np.median(d[np.triu_indices(n, 1)])
    if not np.isfinite(s) or s <= 0:
        s = 1.0
    return np.exp(-(d * d) / (2.0 * s * s))


def _centrar(K):
    return K - K.mean(axis=0, keepdims=True) - K.mean(axis=1, keepdims=True) + K.mean()


def _cka(Kc, Lc):
    den = np.sqrt((Kc * Kc).sum() * (Lc * Lc).sum())
    return float((Kc * Lc).sum() / den) if den > 0 else 0.0


def hsic(x, y):
    """HSIC normalizado (CKA), kernel gaussiano con ancho por la mediana."""
    return _cka(_centrar(_kernel(x)), _centrar(_kernel(y)))


def hsic_pval(x, y, B=N_PERM, seed=SEMILLA):
    """p-valor de HSIC por B permutaciones de y (kernel de y reordenado)."""
    y = np.asarray(y, float)
    n = len(y)
    Kc, L = _centrar(_kernel(x)), _kernel(y)
    obs = _cka(Kc, _centrar(L))
    rng = np.random.default_rng(seed)
    ge = 0
    for _ in range(B):
        p = rng.permutation(n)
        if _cka(Kc, _centrar(L[np.ix_(p, p)])) >= obs:
            ge += 1
    return (1.0 + ge) / (1.0 + B)


def logistica(X, y, ridge=1e-6, itmax=100):
    """Regresion logistica estandarizada por IRLS con ridge; (coef, error est.)."""
    X, y = np.asarray(X, float), np.asarray(y, float)
    sx = X.std(axis=0)
    if np.any(sx <= 0) or len(np.unique(y)) < 2:
        return np.full(X.shape[1], np.nan), np.full(X.shape[1], np.nan)
    A = np.column_stack([np.ones(len(y)), (X - X.mean(axis=0)) / sx])
    beta = np.zeros(A.shape[1])
    for _ in range(itmax):
        mu = 1.0 / (1.0 + np.exp(-A @ beta))
        w = np.clip(mu * (1.0 - mu), 1e-9, None)
        H = A.T @ (w[:, None] * A) + ridge * np.eye(A.shape[1])
        b2 = np.linalg.solve(H, A.T @ (w * (A @ beta + (y - mu) / w)))
        if np.max(np.abs(b2 - beta)) < 1e-8:
            beta = b2
            break
        beta = b2
    mu = 1.0 / (1.0 + np.exp(-A @ beta))
    w = np.clip(mu * (1.0 - mu), 1e-9, None)
    H = A.T @ (w[:, None] * A) + ridge * np.eye(A.shape[1])
    se = np.sqrt(np.clip(np.diag(np.linalg.inv(H)), 0, None))
    return beta[1:], se[1:]
