"""Sensibilidad 1, Fase B — utilidades del reporte de las mallas 2D.

Lectura de `faseB_filas.csv`, predicados de clase (KALINA y KALINA confiable),
reconstrucción de las seis mallas 7x7 por centro (las combinaciones repetidas
entre pares se recuperan por combinación, no por su etiqueta `par`), agregados
por (centro, par), y las líneas KALINA de la Fase A (con el punto base ya
incluido) para medir la interacción. Cada número sale de un archivo; no se
inventa nada. Se ejecuta como script, no como módulo.
"""
from __future__ import annotations

import csv

from faseB_corrida import (CENTROS_D, PARES_D, VARIABLES, valores,
                           valores_brutos)

CLASES = ("KALINA", "CORREGIBLE", "INVIABLE", "NO_CONVERGIO")
ETAS_EPS = ("eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")
CODIGO = {"CORREGIBLE": "c", "INVIABLE": "i", "NO_CONVERGIO": "n"}
MAGS = ("dh_turb", "Wnet", "Qreg_Qi", "Qout", "ratio_P")


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


def clave(combo: dict) -> tuple:
    return tuple(round(combo[k], 6) for k in VARIABLES)


def indice(filas: list) -> dict:
    """combinación (10 variables) -> fila, para recuperar cada celda de malla."""
    d = {}
    for f in filas:
        try:
            d[tuple(round(num(f.get(k)), 6) for k in VARIABLES)] = f
        except TypeError:            # fila sin todas las variables: se ignora
            continue
    return d


def celdas(centro: str, par: str, idx: dict):
    """Celdas de una malla: etiquetas (unidades de espec.) y fila por celda."""
    a, b = PARES_D[par]
    base = CENTROS_D[centro]
    ra, da = valores_brutos(a, centro), valores(a, centro)
    rb, db = valores_brutos(b, centro), valores(b, centro)
    out = []
    for i, (xa, va) in enumerate(zip(ra, da)):
        for j, (xb, vb) in enumerate(zip(rb, db)):
            combo = dict(base, **{a: float(va), b: float(vb)})
            out.append(dict(i=i, j=j, ra=xa, rb=xb, da=va, db=vb,
                            row=idx.get(clave(combo))))
    return out, ra, rb, a, b


def _div(a, b):
    return None if a is None or not b else a / b


def _in(v, s) -> bool:
    return v is not None and any(abs(v - x) < 1e-6 for x in s)


def lineas_kalina_faseA(path_a) -> dict:
    """(centro, variable) -> valores (unidades de diseño) KALINA en la Fase A,
    incluido el punto base. Fuente: `faseA_filas.csv`."""
    filas = leer_filas(path_a)
    sets, base = {}, {}
    for f in filas:
        c = f.get("centro")
        if f.get("variable") == "base":
            base[c] = f
        elif es_kalina(f):
            sets.setdefault((c, f.get("variable")), set()).add(
                num(f.get("valor")))
    for c, bf in base.items():
        if es_kalina(bf):
            for var in VARIABLES:
                sets.setdefault((c, var), set()).add(num(bf.get(var)))
    return sets


def equipos(conf: list) -> dict:
    """min/máx de las magnitudes de preselección entre KALINA confiables
    (`m_b=1.0`: Wnet/m_b = Wnet, Qout/m_b = Qout)."""
    def valor(nombre, r):
        if nombre == "dh_turb":
            return num(r.get("dh_turb"))
        if nombre == "Wnet":
            return _div(num(r.get("Wnet")), num(r.get("m_b")))
        if nombre == "Qout":
            return _div(num(r.get("Qout")), num(r.get("m_b")))
        if nombre == "Qreg_Qi":
            return _div(num(r.get("Qreg")), num(r.get("Qi")))
        return _div(num(r.get("P_alta")), num(r.get("P_baja")))

    out = {}
    for nombre in MAGS:
        vals = [valor(nombre, c["row"]) for c in conf]
        vals = [v for v in vals if v is not None]
        out[nombre] = (min(vals), max(vals)) if vals else (None, None)
    return out


def agrega(centro: str, par: str, idx: dict, lineas: dict) -> dict:
    celdas_l, ra, rb, a, b = celdas(centro, par, idx)
    n = len(celdas_l)
    cnt = {k: sum(1 for c in celdas_l
                  if c["row"] is not None and clase(c["row"]) == k)
           for k in CLASES}
    kal = [c for c in celdas_l if c["row"] is not None and es_kalina(c["row"])]
    conf = [c for c in kal if confiable(c["row"])]
    etas = [num(c["row"].get("eta")) for c in kal]
    etas = [e for e in etas if e is not None]
    mejor = None
    if conf:
        cm = max(conf, key=lambda c: num(c["row"].get("eta")) or -1.0)
        mejor = (cm["ra"], cm["rb"], 100 * (num(cm["row"].get("eta")) or 0.0))
    esp = sum(1 for c in celdas_l
              if _in(c["da"], lineas.get((centro, a), set()))
              and _in(c["db"], lineas.get((centro, b), set())))
    rango = None
    if kal:
        rango = (min(c["ra"] for c in kal), max(c["ra"] for c in kal),
                 min(c["rb"] for c in kal), max(c["rb"] for c in kal))
    return dict(centro=centro, par=par, var1=a, var2=b, n_puntos=n,
                n_kalina=cnt["KALINA"], n_corregible=cnt["CORREGIBLE"],
                n_inviable=cnt["INVIABLE"], n_no_convergio=cnt["NO_CONVERGIO"],
                n_kalina_confiable=len(conf),
                pct_area_kalina=(100 * len(kal) / n if n else None),
                eta_min_pct=(100 * min(etas) if etas else None),
                eta_max_pct=(100 * max(etas) if etas else None),
                mejor=mejor, kalina_real=len(kal), kalina_esperado=esp,
                hay_interaccion=len(kal) < esp, rango=rango,
                equipos=equipos(conf), celdas=celdas_l,
                raw_a=ra, raw_b=rb, code=CODIGO)
