"""M4 — tablas y formato de números del `REPORTE_M4.md`.

Los formatos son fijos a propósito: la verificación (`m4_verificar.py`)
recalcula cada cifra desde los CSV con estos mismos decimales y exige que el
reporte coincida. `nf` = decimal fijo, `gf` = general (6 cifras), `pf` = valor
p con 4 cifras, `icf` = intervalo de confianza entre corchetes.
"""
from __future__ import annotations

from m4_datos import VARS10

CAB_RSA = ("| variable | KS | IC95 % | valor p | rango favorable (p5–p95) | "
           "n_B | n_B̄ |")
CAB_PWN = ("| variable | PAWN η (mediana) | PAWN η (máx) | PAWN D (mediana) | "
           "PAWN D (máx) |")
CAB_PRCC = ("| variable | PRCC η | IC95 % (η) | valor p (η) | PRCC m_O1 | "
            "PRCC m_O2 | PRCC m_O5 |")


def nf(x, d=3):
    """Número con `d` decimales fijos; `None` → `n/d`."""
    return "n/d" if x is None else f"{x:.{d}f}"


def gf(x, d=6):
    """Número en notación general (hasta `d` cifras); `None` → `n/d`."""
    return "n/d" if x is None else f"{x:.{d}g}"


def pf(x):
    """Valor p con 4 cifras (notación exponencial si hace falta)."""
    return "n/d" if x is None else f"{x:.4g}"


def icf(lo, hi, d=3):
    """Intervalo `[lo, hi]` con `d` decimales."""
    return "n/d" if lo is None else f"[{nf(lo, d)}, {nf(hi, d)}]"


def tabla_rsa(rows):
    """Filas del RSA ordenadas por KS descendente (los `None` al final)."""
    o = sorted(rows, key=lambda r: (r["KS"] is None, -(r["KS"] or 0.0)))
    out = [CAB_RSA, "|---|---|---|---|---|---|---|"]
    for r in o:
        out.append(f'| {r["variable"]} | {nf(r["KS"])} | '
                   f'{icf(r["ic_lo"], r["ic_hi"])} | {pf(r["p_valor"])} | '
                   f'[{gf(r["fav_p05"])}, {gf(r["fav_p95"])}] | '
                   f'{r["n_B"]} | {r["n_Bbar"]} |')
    return "\n".join(out)


def tabla_pawn(pawn):
    """PAWN de η y de D, variables ordenadas por el índice de η."""
    eta = {r["variable"]: r for r in pawn if r["salida"] == "eta"}
    dd = {r["variable"]: r for r in pawn if r["salida"] == "D"}
    out = [CAB_PWN, "|---|---|---|---|---|"]
    for v in sorted(eta, key=lambda v: -(eta[v]["T_mediana"] or 0.0)):
        out.append(f'| {v} | {nf(eta[v]["T_mediana"])} | {nf(eta[v]["T_max"])} | '
                   f'{nf(dd[v]["T_mediana"])} | {nf(dd[v]["T_max"])} |')
    return "\n".join(out)


def tabla_prcc(prcc):
    """PRCC de η (con IC y p) y de los tres márgenes, ordenado por |PRCC| de η."""
    g = {(r["salida"], r["variable"]): r for r in prcc}
    out = [CAB_PRCC, "|---|---|---|---|---|---|---|"]
    for v in sorted(VARS10, key=lambda v: -abs(g[("eta", v)]["prcc"] or 0.0)):
        e = g[("eta", v)]
        out.append(f'| {v} | {nf(e["prcc"])} | {icf(e["ic_lo"], e["ic_hi"])} | '
                   f'{pf(e["p_valor"])} | {nf(g[("m_O1", v)]["prcc"])} | '
                   f'{nf(g[("m_O2", v)]["prcc"])} | {nf(g[("m_O5", v)]["prcc"])} |')
    return "\n".join(out)


def tabla_top(top):
    """Los 10 mejores KALINA con sus 10 variables."""
    out = ["| # | id | η | W_net (kW) | D | " + " | ".join(VARS10) + " |",
           "|---|---|" + "---|" * (3 + len(VARS10))]
    for r in top:
        out.append(f'| {r["puesto"]} | {r["id_muestra"]} | {nf(r["eta"], 4)} | '
                   f'{nf(r["Wnet"], 2)} | {nf(r["D"], 2)} | '
                   + " | ".join(gf(r[v]) for v in VARS10) + " |")
    return "\n".join(out)
