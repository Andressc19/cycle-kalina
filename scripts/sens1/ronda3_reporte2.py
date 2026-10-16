"""Sensibilidad 1, Ronda 3 - capa de DATOS del reporte (`ronda3_filas.csv`).

**KALINA (total)**: fila con clasificacion KALINA. **Dentro del rango
experimental**: KALINA sin la marca `fuera_rango` y con eta_*/eps_* en
[0.40, 0.95]. **Fuera del rango experimental (liquido > 420 K)**: KALINA con
la marca `fuera_rango`. N9: mallas 7x7 por centro y par; la celda central de
cada malla es el punto base (`par="base"`), que dedup dejo una sola vez.
"""
from __future__ import annotations

import csv
from collections import Counter

import numpy as np

from ronda3_puntos import CENTROS, PARES, valores

BARRIDOS = ("N9", "N10", "N8")
ETAS_EPS = ("eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")
STATS = ("minimo", "p10", "mediana", "p90", "maximo")
LETRA = dict(KALINA="K", CORREGIBLE="c", INVIABLE="i", NO_CONVERGIO="n")
CENTROS_D = dict(CENTROS)


def num(v):
    """float o None (tolera '', 'None')."""
    try:
        return None if v in (None, "", "None") else float(v)
    except (TypeError, ValueError):
        return None


def fmt(v, n=6):
    x = v if isinstance(v, (int, float)) else num(v)
    return "?" if x is None else f"{x:.{n}g}"


def leer_filas(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def clase(f):
    return f.get("clasificacion") or "NO_CONVERGIO"


def es_kalina(f):
    return clase(f) == "KALINA"


def fuera_rango(f):
    return str(f.get("fuera_rango") or "").strip().lower() in ("true", "1")


def dentro(f):
    """Dentro del rango experimental: KALINA, sin fuera_rango, eta/eps 0.40-0.95."""
    if not es_kalina(f) or fuera_rango(f):
        return False
    return all(num(f.get(k)) is not None and 0.40 - 1e-9 <= num(f.get(k))
               <= 0.95 + 1e-9 for k in ETAS_EPS)


def percentiles(vals):
    """min, p10, mediana, p90, max (y n); None si no hay datos."""
    if not vals:
        return dict(n=0, minimo=None, p10=None, mediana=None, p90=None,
                    maximo=None)
    q = np.percentile(np.asarray(vals, float), [0, 10, 50, 90, 100])
    return dict(n=len(vals), minimo=float(q[0]), p10=float(q[1]),
                mediana=float(q[2]), p90=float(q[3]), maximo=float(q[4]))


def centros_de(filas, barrido):
    return sorted({f.get("centro") for f in filas if f.get("barrido") == barrido})


def grupo(filas, barrido, centro):
    return [f for f in filas if f.get("barrido") == barrido
            and (centro == "TOTAL" or f.get("centro") == centro)]


def resumen_por(filas, barrido, centro):
    """Puntos, clases, dentro/fuera y eta min/mediana/max (KALINA y dentro)."""
    rs = grupo(filas, barrido, centro)
    cnt = Counter(clase(f) for f in rs)
    kal = [f for f in rs if es_kalina(f)]
    den = [f for f in rs if dentro(f)]
    row = dict(barrido=barrido, centro=centro, n_puntos=len(rs),
               n_kalina_total=cnt["KALINA"], n_corregible=cnt["CORREGIBLE"],
               n_inviable=cnt["INVIABLE"], n_no_convergio=cnt["NO_CONVERGIO"],
               n_dentro=len(den),
               n_fuera=sum(1 for f in rs if es_kalina(f) and fuera_rango(f)))
    for pre, g in (("kal", kal), ("dentro", den)):
        q = percentiles([v for v in (num(f.get("eta")) for f in g)
                         if v is not None])
        for k, s in (("min", "minimo"), ("med", "mediana"), ("max", "maximo")):
            row[f"eta_{k}_{pre}_pct"] = None if q[s] is None else 100 * q[s]
    return row


def celda(f):
    if f is None:
        return "?"
    c = clase(f)
    letra = LETRA.get(c, "?")
    if c != "NO_CONVERGIO" and fuera_rango(f):
        return letra.lower()
    return letra


def _eta(f):
    if f is None:
        return "?"
    e = num(f.get("eta"))
    return "?" if e is None else f"{100 * e:.2f}"


def _k(x):
    return round(float(x), 6)


def n9_idx(filas):
    """(centro, par, val1, val2) -> fila; la celda central es el punto base."""
    idx = {}
    for f in filas:
        if f.get("barrido") != "N9":
            continue
        if f.get("par") == "base":
            c = f.get("centro")
            for par, a, b in PARES:
                idx[(c, par, _k(CENTROS_D[c][a]), _k(CENTROS_D[c][b]))] = f
        else:
            idx[(f.get("centro"), f.get("par"), _k(num(f.get("val1"))),
                 _k(num(f.get("val2"))))] = f
    return idx


def n9_tabla(filas, centro, par, modo):
    """(cabecera, filas) de la malla 7x7; modo='clase' | 'eta'."""
    idx = n9_idx(filas)
    _, a, b = next(p for p in PARES if p[0] == par)
    ea, eb = valores(a, centro), valores(b, centro)
    cab = [f"{a} \\ {b}"] + [fmt(x) for x in eb]
    lineas = []
    for va in ea:
        celdas = [fmt(va)]
        for vb in eb:
            f = idx.get((centro, par, _k(va), _k(vb)))
            celdas.append(celda(f) if modo == "clase" else _eta(f))
        lineas.append(celdas)
    return cab, lineas


def n9_par_resumen(filas):
    """Por (centro, par): KALINA contando el base y el KALINA de mayor eta."""
    idx, out = n9_idx(filas), []
    for centro in centros_de(filas, "N9"):
        for par, a, b in PARES:
            mejor, n_kal, n_cel = None, 0, 0
            for va in valores(a, centro):
                for vb in valores(b, centro):
                    f = idx.get((centro, par, _k(va), _k(vb)))
                    n_cel += 1
                    if f is None or not es_kalina(f):
                        continue
                    n_kal += 1
                    e = num(f.get("eta")) or -1
                    if mejor is None or e > (num(mejor[0].get("eta")) or -1):
                        mejor = (f, va, vb)
            e = None if mejor is None else num(mejor[0].get("eta"))
            out.append(dict(centro=centro, par=par, var1=a, var2=b,
                            n_celdas=n_cel, n_kalina=n_kal,
                            id_mejor=mejor[0].get("id_punto") if mejor else "",
                            eta_mejor_pct=None if e is None else 100 * e,
                            val1_mejor=mejor[1] if mejor else None,
                            val2_mejor=mejor[2] if mejor else None))
    return out


def agotados_por(filas):
    """Lineas `- {barrido} / {centro}: n punto(s)` con tiempo agotado."""
    por = {}
    for f in filas:
        if str(f.get("mensaje") or "").startswith("tiempo_agotado"):
            k = (f.get("barrido"), f.get("centro"))
            por[k] = por.get(k, 0) + 1
    return [f"- {b} / {c}: {n} punto(s)" for (b, c), n in sorted(por.items())]


def planificados(path):
    """{barrido: n} del `ronda3_diseno.csv` (vacio si no existe)."""
    try:
        filas = leer_filas(path)
    except FileNotFoundError:
        return {}
    return dict(Counter(r.get("barrido") for r in filas))
