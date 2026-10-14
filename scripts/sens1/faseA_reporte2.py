"""Sensibilidad 1, Fase A — utilidades del reporte (`faseA_reporte.py`).

Lectura de `faseA_filas.csv`, predicados de clase (KALINA y KALINA confiable),
agrupación por (centro, variable), el barrido ordenado con sus escalones y el
`faseA_resumen_variables.csv`. Cada número sale del CSV; no se inventa nada.
Se ejecuta como script, no como módulo.
"""
from __future__ import annotations

import csv
from pathlib import Path

VARIABLES = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b",
             "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")
CENTROS = ("C1", "C2")
CLASES = ("KALINA", "CORREGIBLE", "INVIABLE", "NO_CONVERGIO")
ETAS_EPS = ("eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")
_CAMPOS_VAR = ["centro", "variable", "n_puntos", "n_kalina", "n_corregible",
               "n_inviable", "n_no_convergio", "n_kalina_confiable",
               "valor_min", "valor_max", "eta_min_pct", "eta_max_pct",
               "eta_amplitud_pp", "contiguo"]


def num(v):
    """float o None (tolera '', 'None')."""
    if v in (None, "", "None"):
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def fmt(v, n=6):
    x = num(v)
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
    """KALINA confiable: clase KALINA, sin `fuera_rango` y todas las eta_*/eps_*
    dentro de [0.40, 0.95]."""
    if not es_kalina(f) or fuera_rango(f):
        return False
    for k in ETAS_EPS:
        v = num(f.get(k))
        if v is None or not (0.40 - 1e-9 <= v <= 0.95 + 1e-9):
            return False
    return True


def es_genuino(f) -> bool:
    """convergio=True y clase distinta de NO_CONVERGIO (los N2 espurios —falso
    convergido— no cuentan)."""
    return str(f.get("convergio")) == "True" and clase(f) != "NO_CONVERGIO"


def agrupar(filas: list) -> dict:
    """(centro, variable) -> lista de filas, tal como vienen del CSV."""
    g = {}
    for f in filas:
        g.setdefault((f.get("centro"), f.get("variable")), []).append(f)
    return g


def por_centro(filas: list) -> dict:
    g = {c: [] for c in CENTROS}
    for f in filas:
        g.setdefault(f.get("centro"), []).append(f)
    return g


def barrido_ordenado(rows: list) -> list:
    """Filas de una variable ordenadas por `valor` ascendente."""
    return sorted(rows, key=lambda r: num(r.get("valor")) or 0.0)


def escalones(rows: list) -> dict:
    """Bloque KALINA de un barrido: extremos, vecinos no-KALINA y contigüidad.

    `abajo`/`arriba` son las filas inmediatamente fuera del bloque KALINA (o
    None si el bloque toca el borde del barrido). `contiguo` es True si las
    filas KALINA ocupan posiciones consecutivas en la rejilla ordenada.
    """
    rs = barrido_ordenado(rows)
    idxk = [i for i, r in enumerate(rs) if es_kalina(r)]
    if not idxk:
        return dict(min=None, max=None, abajo=None, arriba=None, contiguo=False,
                    n_k=0)
    lo, hi = idxk[0], idxk[-1]
    return dict(min=num(rs[lo]["valor"]), max=num(rs[hi]["valor"]),
                abajo=(rs[lo - 1] if lo > 0 else None),
                arriba=(rs[hi + 1] if hi + 1 < len(rs) else None),
                contiguo=(hi - lo + 1) == len(idxk), n_k=len(idxk))


def amplitudes_eta(rows: list):
    """(n KALINA, η_min, η_max, amplitud) entre los KALINA con η numérica."""
    etas = [num(r.get("eta")) for r in rows if es_kalina(r)]
    etas = [e for e in etas if e is not None]
    if not etas:
        return 0, None, None, None
    return len(etas), min(etas), max(etas), max(etas) - min(etas)


def fila_resumen(centro: str, var: str, rows: list) -> dict:
    conteo = {c: sum(1 for r in rows if clase(r) == c) for c in CLASES}
    _, emin, emax, amp = amplitudes_eta(rows)
    esc = escalones(rows) if var != "base" else dict(
        min=None, max=None, contiguo=None)
    pct = (lambda x: None if x is None else 100.0 * x)
    return dict(centro=centro, variable=var, n_puntos=len(rows),
                n_kalina=conteo["KALINA"], n_corregible=conteo["CORREGIBLE"],
                n_inviable=conteo["INVIABLE"],
                n_no_convergio=conteo["NO_CONVERGIO"],
                n_kalina_confiable=sum(1 for r in rows if confiable(r)),
                valor_min=esc["min"], valor_max=esc["max"],
                eta_min_pct=pct(emin), eta_max_pct=pct(emax),
                eta_amplitud_pp=pct(amp),
                contiguo=esc["contiguo"])


def escribir_resumen_variables(g: dict, destino) -> int:
    n = 0
    with open(destino, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=_CAMPOS_VAR)
        w.writeheader()
        for centro in CENTROS:
            for var in ["base"] + list(VARIABLES):
                rows = g.get((centro, var))
                if not rows:
                    continue
                w.writerow(fila_resumen(centro, var, rows))
                n += 1
    return n


def estadisticas_equipos(rows: list) -> dict:
    """min/máx entre los KALINA de dh_turb, Wnet, Qreg/Qi y m_O2."""
    kal = [r for r in rows if es_kalina(r)]
    out = {}
    for clave, campo in (("dh_turb", "dh_turb"), ("Wnet", "Wnet"),
                         ("m_O2", "m_O2")):
        vals = [num(r.get(campo)) for r in kal]
        vals = [v for v in vals if v is not None]
        out[clave] = (min(vals), max(vals)) if vals else (None, None)
    rat = []
    for r in kal:
        qi, qr = num(r.get("Qi")), num(r.get("Qreg"))
        if qi not in (None, 0) and qr is not None:
            rat.append(qr / qi)
    out["Qreg_Qi"] = (min(rat), max(rat)) if rat else (None, None)
    out["n_kalina"] = len(kal)
    return out
