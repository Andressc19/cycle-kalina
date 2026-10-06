"""M4 — RSA: KS, valor p, IC95 % por bootstrap y rango favorable (MATEMATICA §6.2).

Cuatro separaciones — `KALINA` (vs el resto), `converge` (genuino vs no
genuino), `cumple_O2` y `cumple_O1` (ambas entre genuinos) — cruzadas con las
13 variables (las 10 de la caja más `dP`, `rP`, `dT_fs`). Para cada cruce:
`KS = máx_u |F_B(u) − F_B̄(u)|`, valor p con `scipy.stats.ks_2samp`, IC95 % por
bootstrap de 1000 remuestreos con semilla fija (cada grupo se remuestrea por
separado, con su mismo tamaño) y rango favorable = percentiles 5–95 de la
variable dentro de B.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import ks_2samp

from m4_datos import SEED, VARS13, genu

SEPS = ("KALINA", "converge", "cumple_O2", "cumple_O1")
N_BOOT = 1000
CRSA = ["separacion", "variable", "n_B", "n_Bbar", "n_excluidos", "KS",
        "p_valor", "ic_lo", "ic_hi", "fav_p05", "fav_p95"]


def marcador(f: dict, sep: str):
    """`True` = está en B, `False` = en B̄, `None` = excluido (no aplica)."""
    if sep == "KALINA":
        return f["clasificacion"] == "KALINA"
    if sep == "converge":
        return genu(f)
    if not genu(f):
        return None
    m = f.get("m_O2" if sep == "cumple_O2" else "m_O1")
    return None if m is None else m >= 0


def ks_ic(b: list, bb: list):
    """`(KS, p, ic_lo, ic_hi)`; sin datos suficientes, `None` en lo que falte."""
    if not b or not bb:
        return None, None, None, None
    st, p = ks_2samp(b, bb)
    if min(len(b), len(bb)) < 2:
        return float(st), float(p), None, None
    rng = np.random.default_rng(SEED)
    boot = np.empty(N_BOOT)
    for k in range(N_BOOT):
        boot[k] = ks_2samp(rng.choice(b, len(b), replace=True),
                           rng.choice(bb, len(bb), replace=True)).statistic
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return float(st), float(p), float(lo), float(hi)


def valores(filas: list, sep: str, v: str) -> tuple:
    """`(B, B̄)` con los valores de la variable `v` para la separación `sep`."""
    mar = [marcador(f, sep) for f in filas]
    b = [f[v] for f, m in zip(filas, mar) if m is True and f[v] is not None]
    bb = [f[v] for f, m in zip(filas, mar) if m is False and f[v] is not None]
    return b, bb, mar


def filas_rsa(filas: list) -> list:
    """Una fila por (separación, variable) con KS, p, IC95 % y rango favorable."""
    out = []
    for sep in SEPS:
        for v in VARS13:
            b, bb, mar = valores(filas, sep, v)
            ks, p, lo, hi = ks_ic(b, bb)
            out.append(dict(separacion=sep, variable=v, n_B=len(b),
                            n_Bbar=len(bb),
                            n_excluidos=sum(1 for m in mar if m is None),
                            KS=ks, p_valor=p, ic_lo=lo, ic_hi=hi,
                            fav_p05=float(np.percentile(b, 5)) if b else None,
                            fav_p95=float(np.percentile(b, 95)) if b else None))
    return out


def ks_de(filas: list, sep: str, v: str):
    """Solo el KS de una (separación, variable); lo usa la convergencia."""
    b, bb, _ = valores(filas, sep, v)
    return ks_ic(b, bb)[0]
