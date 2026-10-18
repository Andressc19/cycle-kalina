"""Sensibilidad 1, Ronda 3 - seccion N8 del reporte (LHS de 9 variables).

Ventanas p10-p90 entre los KALINA (total), KS de cada variable (KALINA frente
al resto de genuinos), PRCC con eta entre los KALINA (rangos y residuos con
numpy), top 10 de eta y rangos de equipos. Lo importa `ronda3_reporte.py`.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import ks_2samp

from ronda3_puntos import VARS_N8
from ronda3_reporte2 import centros_de, clase, fmt, grupo, num

GENUINAS = ("KALINA", "CORREGIBLE", "INVIABLE")
EQ_UNI = dict(dh_turb="kJ/kg", Wnet="kW por kg/s", Qreg_Qi="(adim)", r_P="(adim)")
CAB_TOP = ["puesto", "id", "eta [%]", "Wnet [kW]", "T_fuente [K]", "P_alta [kPa]",
           "P_baja [kPa]", "x_b", "eta_t"]


def _tabla(cab, cel):
    return ["| " + " | ".join(str(c) for c in cab) + " |",
            "|" + "---|" * len(cab)] + [
        "| " + " | ".join(str(x) for x in f) + " |" for f in cel]


def _c(x, n=6):
    return "?" if x is None else f"{x:.{n}g}"


def _kal(filas, centro):
    return [f for f in grupo(filas, "N8", centro) if clase(f) == "KALINA"]


def _arr(fs, var):
    return np.asarray([x for f in fs if (x := num(f.get(var))) is not None], float)


def n8_ventanas(filas, centro):
    """[(variable, p10, p50, p90, n)] entre los KALINA (total) del centro."""
    kal = _kal(filas, centro)
    out = []
    for v in VARS_N8:
        x = _arr(kal, v)
        q = np.percentile(x, [10, 50, 90]) if len(x) else [None] * 3
        out.append((v, *[None if t is None else float(t) for t in q], len(x)))
    return out


def n8_ks(filas, centro):
    """[(variable, D, pvalor, n_kal, n_resto)]; KS: KALINA vs CORR+INV."""
    rs = grupo(filas, "N8", centro)
    kal = [f for f in rs if clase(f) == "KALINA"]
    res = [f for f in rs if clase(f) in ("CORREGIBLE", "INVIABLE")]
    out = []
    for v in VARS_N8:
        a, b = _arr(kal, v), _arr(res, v)
        if len(a) < 2 or len(b) < 2:
            out.append((v, None, None, len(a), len(b)))
            continue
        st = ks_2samp(a, b)
        out.append((v, float(st.statistic), float(st.pvalue), len(a), len(b)))
    return out


def _rank(x):
    """Rangos 1..n con promedio en empates (solo numpy)."""
    order = np.argsort(x, kind="mergesort")
    r = np.empty(len(x), float)
    s, i, n = x[order], 0, len(x)
    while i < n:
        j = i
        while j + 1 < n and s[j + 1] == s[i]:
            j += 1
        r[order[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    return r


def _resid(A, y):
    return y - A @ np.linalg.lstsq(A, y, rcond=None)[0]


def n8_prcc(filas, centro):
    """[(variable, prcc)] PRCC con eta entre los KALINA (solo numpy)."""
    fs = [f for f in _kal(filas, centro) if num(f.get("eta")) is not None]
    n = len(fs)
    if n < len(VARS_N8) + 2:
        return [(v, None) for v in VARS_N8]
    Y = _rank(np.asarray([num(f.get("eta")) for f in fs], float))
    X = np.column_stack([_rank(_arr(fs, v)) for v in VARS_N8])
    out = []
    for i, v in enumerate(VARS_N8):
        otros = [j for j in range(len(VARS_N8)) if j != i]
        A = np.column_stack([np.ones(n), X[:, otros]])
        rx, ry = _resid(A, X[:, i]), _resid(A, Y)
        prcc = (None if np.std(rx) < 1e-12 or np.std(ry) < 1e-12
                else float(np.corrcoef(rx, ry)[0, 1]))
        out.append((v, prcc))
    return out


def n8_top(filas, centro, k=10):
    """Filas del top-k de eta entre los KALINA (total) del centro."""
    kal = sorted(_kal(filas, centro),
                 key=lambda f: num(f.get("eta")) or -1.0, reverse=True)[:k]
    filas_top = []
    for i, f in enumerate(kal, 1):
        e = num(f.get("eta"))
        filas_top.append([i, f.get("id_punto"), "?" if e is None else
                          f"{100 * e:.2f}", fmt(num(f.get("Wnet")), 5),
                          fmt(num(f.get("T_fuente")), 6),
                          fmt(num(f.get("P_alta")), 6),
                          fmt(num(f.get("P_baja")), 6),
                          fmt(num(f.get("x_b")), 4),
                          fmt(num(f.get("eta_t")), 4)])
    return filas_top


def _eq(f):
    qi, qr = num(f.get("Qi")), num(f.get("Qreg"))
    pa, pb = num(f.get("P_alta")), num(f.get("P_baja"))
    return {"dh_turb": num(f.get("dh_turb")), "Wnet": num(f.get("Wnet")),
            "Qreg_Qi": None if not qi or qr is None else qr / qi,
            "r_P": None if not pb or pa is None else pa / pb}


def n8_equipos(filas, centro):
    """[(variable, min, p10, p50, p90, max, n)] entre los KALINA del centro."""
    vals = {k: [] for k in EQ_UNI}
    for f in _kal(filas, centro):
        for k, x in _eq(f).items():
            if x is not None:
                vals[k].append(x)
    out = []
    for k in EQ_UNI:
        x = np.asarray(vals[k], float)
        if not len(x):
            out.append((k, None, None, None, None, None, 0))
            continue
        q = np.percentile(x, [0, 10, 50, 90, 100])
        out.append((k, *map(float, q), len(x)))
    return out


def n8_bloque(filas):
    """Lineas markdown de la seccion 4 (N8) del ronda3_resumen.md."""
    out = ["## 4. N8 - muestreo LHS de 9 variables (C3 y C4)", "",
           "Por centro: 250 candidatas LHS (semilla 20261017) redondeadas; las "
           "con P_alta < 1.3*P_baja se descartaron sin re-muestrear (ver "
           "ronda3_descartes.csv) y los duplicados tras redondear se quitaron "
           "una sola vez. eta_p = 0.80 y m_b = 1.0 fijos.", ""]
    for centro in centros_de(filas, "N8"):
        rs = grupo(filas, "N8", centro)
        cnt = {c: sum(1 for f in rs if clase(f) == c)
               for c in GENUINAS + ("NO_CONVERGIO",)}
        out += [f"### {centro} ({len(rs)} puntos)", "",
                f"Clases: {cnt['KALINA']} KALINA (total), {cnt['CORREGIBLE']} "
                f"CORREGIBLE, {cnt['INVIABLE']} INVIABLE y "
                f"{cnt['NO_CONVERGIO']} NO_CONVERGIO.", ""]
        ven = n8_ventanas(filas, centro)
        out += ["Ventanas p10-p90 de las 9 variables entre los KALINA "
                "(total); el redondeo (0.5 K, 10 kPa, 0.01 y 0.05) marca la "
                "resolucion de estas cifras:", "",
                *_tabla(["variable", "p10", "mediana", "p90", "n"],
                        [[v, _c(a), _c(b), _c(c), n] for v, a, b, c, n in ven]),
                ""]
        ks = n8_ks(filas, centro)
        out += ["KS de cada variable: KALINA (total) frente al resto de "
                "puntos genuinos (CORREGIBLE + INVIABLE). D va de 0 (mismo "
                "muestreo) a 1; p-valor bajo (< 0.05) se lee como "
                "distribucion distinta (con valores redondeados, "
                "indicativo):", "",
                *_tabla(["variable", "D", "p-valor", "n KALINA", "n resto"],
                        [[v, _c(d, 3), _c(p, 3), na, nb]
                         for v, d, p, na, nb in ks]), ""]
        pr = n8_prcc(filas, centro)
        out += ["PRCC con eta entre los KALINA (total): rangos con promedio "
                "en empates y residuos de minimos cuadrados con intercepta "
                "(solo numpy). +1 sube eta, -1 la baja, ~0 no aporta "
                "linealmente:", "",
                *_tabla(["variable", "PRCC"], [[v, _c(p, 3)] for v, p in pr]),
                ""]
        prs = [(v, p) for v, p in pr if p is not None]
        if prs:
            hi, lo = max(prs, key=lambda t: t[1]), min(prs, key=lambda t: t[1])
            out += [f"Lectura: la mayor influencia positiva lineal es "
                    f"**{hi[0]}** (PRCC {_c(hi[1], 3)}) y la mayor negativa "
                    f"**{lo[0]}** (PRCC {_c(lo[1], 3)}).", ""]
        out += ["Top 10 de eta entre los KALINA (total):", "",
                *_tabla(CAB_TOP, n8_top(filas, centro)), ""]
        eq = n8_equipos(filas, centro)
        out += ["Rangos de equipos entre los KALINA (total): dh_turb en "
                "kJ/kg, Wnet en kW con m_b = 1.0 kg/s (kW por kg/s), Qreg/Qi "
                "y r_P = P_alta/P_baja sin unidades:", "",
                *_tabla(["variable", "unidad", "min", "p10", "mediana",
                         "p90", "max", "n"],
                        [[k, EQ_UNI[k], _c(a), _c(b), _c(c), _c(d), _c(e), n]
                         for k, a, b, c, d, e, n in eq]), ""]
    return out
