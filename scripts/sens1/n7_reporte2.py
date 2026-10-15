"""Sensibilidad 1, N7 — capa de DATOS del reporte (`n7_filas.csv`).
KALINA confiable: clase KALINA, sin `fuera_rango` y `eta_*`/`eps_*` en
[0.40, 0.95]. El base se incluye DENTRO del barrido de cada variable.
"""
import csv
from collections import Counter

import numpy as np

from n7_puntos import CENTROS_D, VARIABLES

CENTROS = ("C3", "C4")
BARRIDOS = ("N7A", "N7B")
ETAS_EPS = ("eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")
CODIGO = {"KALINA": "K", "CORREGIBLE": "c", "INVIABLE": "i",
          "NO_CONVERGIO": "n"}
MAGS = (("dh_turb", "dh_turb [kJ/kg]"),
        ("Wnet_m_b", "Wnet/m_b [kW por kg/s]"),
        ("Qin_m_b", "Qi/m_b [kW por kg/s]"),
        ("Qreg_Qi", "Qreg/Qi"),
        ("Qout_m_b", "Qout/m_b [kW por kg/s]"),
        ("ratio_P", "P_alta/P_baja"))
CAMPOS_VAR = ["centro", "variable", "n_puntos", "n_kalina", "n_corregible",
              "n_inviable", "n_no_convergio", "n_kalina_confiable",
              "n_kalina_fuera_rango", "valor_min", "valor_max", "eta_min_pct",
              "eta_max_pct", "eta_amplitud_pp", "eta_min_kalina_pct",
              "eta_max_kalina_pct", "eta_amplitud_kalina_pp", "contiguo"]
CAMPOS_PAR = ["centro", "par", "var1", "var2", "n_celdas", "n_puntos",
              "n_descartado", "n_kalina", "n_corregible", "n_inviable",
              "n_no_convergio", "n_kalina_confiable", "pct_area_kalina",
              "eta_min_pct", "eta_max_pct", "mejor_var1", "mejor_var2",
              "mejor_eta_pct"]
CAMPOS_EQ = ["centro", "magnitud", "n", "minimo", "mediana", "maximo"]


def num(v):
    """float o None (tolera '', 'None')."""
    try:
        return None if v in (None, "", "None") else float(v)
    except (TypeError, ValueError):
        return None


def fmt(v, n=6):
    x = v if isinstance(v, (int, float)) else num(v)
    return "—" if x is None else f"{x:.{n}g}"

def leer_filas(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def clase(f):
    return f.get("clasificacion") or "NO_CONVERGIO"


def es_kalina(f):
    return clase(f) == "KALINA"

def fuera_rango(f):
    return str(f.get("fuera_rango") or "").strip().lower() in ("true", "1")


def confiable(f):
    if not es_kalina(f) or fuera_rango(f):
        return False
    return all(num(f.get(k)) is not None and 0.40 - 1e-9 <= num(f.get(k))
               <= 0.95 + 1e-9 for k in ETAS_EPS)


def percentiles(vals):
    """min, mediana, max (y n); `None` si no hay datos."""
    if not vals:
        return dict(n=0, minimo=None, mediana=None, maximo=None)
    q = np.percentile(np.asarray(vals, float), [0, 50, 100])
    return dict(n=len(vals), minimo=float(q[0]), mediana=float(q[1]),
                maximo=float(q[2]))


def grupo(filas, centro):
    return [f for f in filas if f.get("centro") == centro]


def _valor(r):
    v = num(r.get("valor"))
    return -1e18 if v is None else v


def con_base(rows, base_fila, valor):
    """Copia de `rows` mas la fila base con `valor`, si ese valor no esta ya."""
    if any(abs(_valor(r) - float(valor)) < 1e-9 for r in rows):
        return list(rows)
    return list(rows) + [dict(base_fila, valor=valor)]


def escalones(rows):
    """Extremos del bloque KALINA y contiguedad sobre `valor` ordenado."""
    rs = sorted(rows, key=_valor)
    idxk = [i for i, r in enumerate(rs) if es_kalina(r)]
    if not idxk:
        return dict(min=None, max=None, contiguo=False)
    lo, hi = idxk[0], idxk[-1]
    return dict(min=num(rs[lo]["valor"]), max=num(rs[hi]["valor"]),
                contiguo=(hi - lo + 1) == len(idxk))


def _amp(rows):
    etas = [e for e in (num(r.get("eta")) for r in rows if es_kalina(r))
            if e is not None]
    return (len(etas), min(etas), max(etas)) if etas else (0, None, None)


def fila_resumen(centro, var, rows):
    cnt = Counter(clase(r) for r in rows)
    conf = [r for r in rows if confiable(r)]
    kal = [r for r in rows if es_kalina(r)]
    _, emin, emax = _amp(conf)
    _, kmin, kmax = _amp(kal)
    esc = (dict(min=None, max=None, contiguo=None) if var == "base"
           else escalones(rows))
    pct = lambda x: None if x is None else 100.0 * x
    return dict(centro=centro, variable=var, n_puntos=len(rows),
                n_kalina=cnt["KALINA"], n_corregible=cnt["CORREGIBLE"],
                n_inviable=cnt["INVIABLE"], n_no_convergio=cnt["NO_CONVERGIO"],
                n_kalina_confiable=len(conf),
                n_kalina_fuera_rango=sum(1 for r in kal if fuera_rango(r)),
                valor_min=esc["min"], valor_max=esc["max"],
                eta_min_pct=pct(emin), eta_max_pct=pct(emax),
                eta_amplitud_pp=pct(None if emin is None else emax - emin),
                eta_min_kalina_pct=pct(kmin), eta_max_kalina_pct=pct(kmax),
                eta_amplitud_kalina_pp=pct(None if kmin is None else kmax - kmin),
                contiguo=esc["contiguo"])


def resumenes_centro(filas, centro):
    """Resumen N7A del centro con la base incluida en cada barrido."""
    g = {}
    for f in grupo(filas, centro):
        if f.get("barrido") == "N7A":
            g.setdefault(f.get("variable"), []).append(f)
    out = [fila_resumen(centro, "base", g["base"])]
    for var in VARIABLES:
        out.append(fila_resumen(centro, var,
                                con_base(g.get(var, []), g["base"][0],
                                         CENTROS_D[centro][var])))
    return out


def _div(a, b):
    a, b = num(a), num(b)
    return None if a is None or not b else a / b


MAGF = {"dh_turb": lambda f: num(f.get("dh_turb")),
        "Wnet_m_b": lambda f: _div(f.get("Wnet"), f.get("m_b")),
        "Qin_m_b": lambda f: _div(f.get("Qi"), f.get("m_b")),
        "Qreg_Qi": lambda f: _div(f.get("Qreg"), f.get("Qi")),
        "Qout_m_b": lambda f: _div(f.get("Qout"), f.get("m_b")),
        "ratio_P": lambda f: _div(f.get("P_alta"), f.get("P_baja"))}


def equipos(filas, centro):
    conf = [f for f in grupo(filas, centro) if confiable(f)]
    out = []
    for nombre, etiqueta in MAGS:
        q = percentiles([v for v in (MAGF[nombre](f) for f in conf)
                         if v is not None])
        out.append(dict(centro=centro, magnitud=etiqueta, n=q["n"],
                        minimo=q["minimo"], mediana=q["mediana"],
                        maximo=q["maximo"]))
    return out


def conteos(filas):
    out = []
    for b in BARRIDOS:
        for c in CENTROS:
            g = [f for f in filas if f.get("barrido") == b
                 and f.get("centro") == c]
            cnt = Counter(clase(f) for f in g)
            out.append(dict(barrido=b, centro=c, n_puntos=len(g),
                            n_kalina=cnt["KALINA"],
                            n_corregible=cnt["CORREGIBLE"],
                            n_inviable=cnt["INVIABLE"],
                            n_no_convergio=cnt["NO_CONVERGIO"],
                            n_kalina_confiable=sum(1 for f in g
                                                   if confiable(f)),
                            n_kalina_fuera_rango=sum(
                                1 for f in g
                                if es_kalina(f) and fuera_rango(f))))
    return out


def tiempo_agotado(filas):
    por = {}
    for f in filas:
        if (f.get("mensaje") or "").startswith("tiempo_agotado"):
            k = (f.get("barrido"), f.get("centro"))
            por[k] = por.get(k, 0) + 1
    return [f"- {b} / {c}: {n} punto(s)" for (b, c), n in sorted(por.items())]
