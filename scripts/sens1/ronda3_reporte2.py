"""Sensibilidad 1, Ronda 3 - capa de DATOS del reporte (`ronda3_filas.csv`).

KALINA (total) = clasificacion KALINA; dentro = KALINA sin `fuera_rango` y con
eta/eps en [0.40, 0.95]; fuera = KALINA con `fuera_rango` (liquido > 420 K).
N9: mallas 7x7 por centro y par (la celda central es el punto base). N10:
malla 5x7 por centro (P_alta x P_baja), sin punto base.
"""
from __future__ import annotations

import csv
from collections import Counter

import numpy as np

from ronda3_puntos import CENTROS, P_ALTA_N10, P_BAJA_N10, PARES, valores

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
    xs = [num(f.get(k)) for k in ETAS_EPS]
    return es_kalina(f) and not fuera_rango(f) and all(
        x is not None and 0.40 - 1e-9 <= x <= 0.95 + 1e-9 for x in xs)


def percentiles(vals):
    """min, p10, mediana, p90, max (y n); None si no hay datos."""
    if not vals:
        return dict(n=0, **{k: None for k in STATS})
    q = np.percentile(np.asarray(vals, float), [0, 10, 50, 90, 100])
    return dict(n=len(vals), **dict(zip(STATS, map(float, q))))


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
        q = percentiles([v for v in (num(f.get("eta")) for f in g) if v is not None])
        for k, s in (("min", "minimo"), ("med", "mediana"), ("max", "maximo")):
            row[f"eta_{k}_{pre}_pct"] = None if q[s] is None else 100 * q[s]
    return row


def celda(f):
    if f is None:
        return "?"
    letra = LETRA.get(clase(f), "?")
    return letra.lower() if clase(f) != "NO_CONVERGIO" and fuera_rango(f) else letra


def _eta(f):
    e = None if f is None else num(f.get("eta"))
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
                    if f is not None and es_kalina(f):
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


def n10_idx(filas):
    """(centro, P_alta, P_baja) -> fila de N10 (columnas del combo)."""
    return {(f.get("centro"), _k(num(f.get("P_alta"))),
             _k(num(f.get("P_baja")))): f for f in filas
            if f.get("barrido") == "N10"}


def n10_tabla(filas, centro, modo):
    """(cabecera, filas) de la malla 5x7 de N10; modo='clase' | 'eta'."""
    idx, pb = n10_idx(filas), P_BAJA_N10[centro]
    cab = ["P_alta \\ P_baja"] + [fmt(x) for x in pb]
    lineas = [[fmt(a)] + [
        (celda(idx.get((centro, _k(a), _k(b)))) if modo == "clase"
         else _eta(idx.get((centro, _k(a), _k(b))))) for b in pb]
        for a in P_ALTA_N10]
    return cab, lineas


def agotados_por(filas):
    """Lineas de puntos sin tiempo: tope duro 600 s y presupuesto 300 s."""
    c = Counter((f.get("barrido"), f.get("centro"),
                 "600s" if str(f.get("mensaje") or "").startswith("tiempo_agotado")
                 else "300s") for f in filas if "agotado" in str(f.get("mensaje") or ""))
    return [f"- {b} / {ce} ({k}): {n} punto(s)" for (b, ce, k), n in sorted(c.items())]


def planificados(path):
    """{barrido: n} del `ronda3_diseno.csv` (vacio si no existe)."""
    if not path.exists():
        return {}
    return dict(Counter(r.get("barrido") for r in leer_filas(path)))
