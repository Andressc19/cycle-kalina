"""Sensibilidad 1, Ronda 1 — capa de DATOS del reporte (`ronda1_filas.csv`).

KALINA confiable: clase KALINA, `fuera_rango` falso/vacio y todo
`eta_*`/`eps_*` en [0.40, 0.95]; KALINA fuera de rango: clase KALINA con
`fuera_rango` verdadero (se reporta aparte). Modulo, no script.
"""
from __future__ import annotations

import csv
from collections import Counter

import numpy as np

BARRIDOS = ("N1", "N3", "N4")
N1_VARS = ("P_alta", "P_baja", "x_b", "T_sumidero")
ETAS_EPS = ("eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")
STATS = ("minimo", "p10", "mediana", "p90", "maximo")
LETRA = dict(KALINA="K", CORREGIBLE="c", INVIABLE="i", NO_CONVERGIO="n")


def num(v):
    """float o None (tolera '', 'None')."""
    try:
        return None if v in (None, "", "None") else float(v)
    except (TypeError, ValueError):
        return None


def fmt(v, n=6) -> str:
    x = v if isinstance(v, (int, float)) else num(v)
    return "—" if x is None else f"{x:.{n}g}"


def leer_filas(path) -> list:
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def clase(f) -> str:
    return f.get("clasificacion") or "NO_CONVERGIO"


def es_kalina(f) -> bool:
    return clase(f) == "KALINA"


def fuera_rango(f) -> bool:
    return str(f.get("fuera_rango") or "").strip().lower() in ("true", "1")


def confiable(f) -> bool:
    """Clase KALINA, sin `fuera_rango` y todos los eta_*/eps_* en [0.40, 0.95]."""
    if not es_kalina(f) or fuera_rango(f):
        return False
    return all(num(f.get(k)) is not None and 0.40 - 1e-9 <= num(f.get(k))
               <= 0.95 + 1e-9 for k in ETAS_EPS)


def percentiles(vals: list) -> dict:
    """min, p10, mediana, p90, max (y n). `None` si no hay datos."""
    if not vals:
        return dict(n=0, minimo=None, p10=None, mediana=None, p90=None,
                    maximo=None)
    q = np.percentile(np.asarray(vals, float), [0, 10, 50, 90, 100])
    return dict(n=len(vals), minimo=float(q[0]), p10=float(q[1]),
                mediana=float(q[2]), p90=float(q[3]), maximo=float(q[4]))


def centros_de(filas: list, barrido: str) -> list:
    return sorted({f.get("centro") for f in filas if f.get("barrido") == barrido})


def grupo(filas: list, barrido: str, centro: str) -> list:
    return [f for f in filas if f.get("barrido") == barrido
            and (centro == "TOTAL" or f.get("centro") == centro)]


def resumen_por(filas: list, barrido: str, centro: str) -> dict:
    """Conteos por clase y eta (min/mediana/max) entre KALINA confiables."""
    rs = grupo(filas, barrido, centro)
    cnt = Counter(clase(f) for f in rs)
    conf = [f for f in rs if confiable(f)]
    q = percentiles([v for v in (num(f.get("eta")) for f in conf)
                     if v is not None])
    row = dict(barrido=barrido, centro=centro, n_puntos=len(rs),
               n_kalina=cnt["KALINA"], n_corregible=cnt["CORREGIBLE"],
               n_inviable=cnt["INVIABLE"], n_no_convergio=cnt["NO_CONVERGIO"],
               n_kalina_confiable=len(conf),
               n_kalina_fuera_rango=sum(1 for f in rs
                                        if es_kalina(f) and fuera_rango(f)))
    for k, s in (("min", "minimo"), ("mediana", "mediana"), ("max", "maximo")):
        row[f"eta_{k}_pct"] = None if q[s] is None else 100 * q[s]
    return row


def n1_por_temperatura(filas: list) -> list:
    """Por nivel de T_fuente: conteos, percentiles y eta maxima entre KALINA."""
    n1 = [f for f in filas if f.get("barrido") == "N1"]
    out = []
    for tf in sorted({num(f.get("T_fuente")) for f in n1}):
        g = [f for f in n1 if num(f.get("T_fuente")) == tf]
        kal = [f for f in g if es_kalina(f)]
        row = dict(t_fuente_C=tf - 273.15, t_fuente_K=tf, n_puntos=len(g),
                   n_kalina_confiable=sum(1 for f in g if confiable(f)),
                   n_kalina_fuera_rango=sum(1 for f in kal if fuera_rango(f)))
        for v in N1_VARS:
            vals = [num(f.get(v)) for f in kal if num(f.get(v)) is not None]
            row.update({f"{v}_{s}": x for s, x in percentiles(vals).items()
                        if s in STATS})
        gana = max(kal, key=lambda f: num(f.get("eta")) or -1, default=None)
        gana = gana if gana and num(gana.get("eta")) is not None else None
        row["eta_max"] = num(gana.get("eta")) if gana else None
        row["eta_max_id"] = gana.get("id_punto") if gana else None
        row.update({f"eta_max_{v}": (num(gana.get(v)) if gana else None)
                    for v in N1_VARS})
        out.append(row)
    return out


def n3_frontera(filas: list) -> list:
    """Por (T_sumidero, eps_cond): P_baja minima con KALINA y su eta."""
    n3 = [f for f in filas if f.get("barrido") == "N3"]
    out = []
    for ts in sorted({num(f.get("T_sumidero")) for f in n3}):
        for eps in sorted({num(f.get("eps_cond")) for f in n3}):
            g = [f for f in n3 if num(f.get("T_sumidero")) == ts
                 and num(f.get("eps_cond")) == eps and es_kalina(f)]
            base = dict(T_sumidero=ts, T_sumidero_C=ts - 273.15, eps_cond=eps)
            if not g:
                out.append(dict(base, P_baja_min=None, eta=None,
                                estado="ninguna"))
                continue
            b = min(g, key=lambda f: num(f.get("P_baja")) or 1e18)
            out.append(dict(base, P_baja_min=num(b.get("P_baja")),
                            eta=num(b.get("eta")), estado="kalina"))
    return out


def celda(f) -> str:
    """Letra de clase (K/c/n/i); minuscula si el punto esta fuera de rango."""
    if f is None:
        return "?"
    c = clase(f)
    letra = LETRA.get(c, "?")
    return letra.lower() if (c != "NO_CONVERGIO" and fuera_rango(f)) else letra


def n3_mallas(filas: list) -> list:
    """Matriz 8x8 de clases (K/c/n/i) por cada T_sumidero (markdown)."""
    n3 = [f for f in filas if f.get("barrido") == "N3"]
    idx = {(num(f.get("T_sumidero")), num(f.get("eps_cond")),
            num(f.get("P_baja"))): f for f in n3}
    ts_all = sorted({num(f.get("T_sumidero")) for f in n3})
    ep_all = sorted({num(f.get("eps_cond")) for f in n3}, reverse=True)
    pb_all = sorted({num(f.get("P_baja")) for f in n3})
    cab = "| eps_cond | " + " | ".join(f"{p:.0f}" for p in pb_all) + " |"
    out = []
    for ts in ts_all:
        out += [f"### T_sumidero = {ts:.2f} K ({ts - 273.15:.0f} C)", "",
                cab, "|" + "---|" * (len(pb_all) + 1)]
        out += [f"| {e:.2f} | " + " | ".join(celda(idx.get((ts, e, p)))
                                             for p in pb_all) + " |"
                for e in ep_all]
        out.append("")
    return out


def n4_mallas(filas: list) -> list:
    """Matriz 7x7 de clase y de eta [%] por centro (markdown)."""
    n4 = [f for f in filas if f.get("barrido") == "N4"]
    idx = {(f.get("centro"), num(f.get("P_alta")), num(f.get("x_b"))): f
           for f in n4}
    out = []
    for c in sorted({f.get("centro") for f in n4}):
        pa = sorted({num(f.get("P_alta")) for f in n4 if f.get("centro") == c})
        xb = sorted({num(f.get("x_b")) for f in n4 if f.get("centro") == c})
        cab = "| P_alta \\ x_b | " + " | ".join(f"{x:.2f}" for x in xb) + " |"
        cl, et = [], []
        for p in pa:
            cel = [(idx.get((c, p, x))) for x in xb]
            cl.append(f"| {p:.0f} | " + " | ".join(celda(f) for f in cel) + " |")
            et.append(f"| {p:.0f} | " + " | ".join(
                "—" if (not f or num(f.get("eta")) is None)
                else f"{100 * num(f.get('eta')):.2f}" for f in cel) + " |")
        for rot, cuerpo in (("clase (K/c/n/i; minuscula si fuera de rango)", cl),
                            ("eta [%]", et)):
            out += [f"### {c} — {rot}", "", cab,
                    "|" + "---|" * (len(xb) + 1), *cuerpo, ""]
    return out


def tiempo_agotado(filas: list) -> list:
    """Lineas markdown con el reparto de puntos que agotaron los 600 s."""
    por = {}
    for f in filas:
        if (f.get("mensaje") or "").startswith("tiempo_agotado"):
            k = (f.get("barrido"), f.get("centro"))
            por[k] = por.get(k, 0) + 1
    return [f"- {b} / {c}: {n} punto(s)" for (b, c), n in sorted(por.items())]
