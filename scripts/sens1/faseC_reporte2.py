"""Sensibilidad 1, Fase C — utilidades del reporte LHS (`faseC_filas.csv`).

Predicados de clase (KALINA y KALINA confiable, con el mismo criterio de la
Fase B), percentiles de ventana, Kolmogorov-Smirnov entre KALINA confiables y
los demas puntos genuinos, PRCC (correlacion parcial por rangos) de cada
variable con eta, tabla top10 y magnitudes de equipos. Cada numero sale de un
archivo; no se inventa nada. Se ejecuta como modulo, no como script.
"""
from __future__ import annotations

import csv

import numpy as np
from scipy.stats import ks_2samp, rankdata

VARIABLES = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b",
             "eta_t", "eps_hrvg", "eps_reg", "eps_cond")
ETAS_EPS = ("eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")
CLASES = ("KALINA", "CORREGIBLE", "INVIABLE", "NO_CONVERGIO")
MAGS = (("dh_turb", "dh_turb [kJ/kg]"), ("Wnet_m_b", "Wnet/m_b [kW por kg/s]"),
        ("Qin", "Qin = Qi/m_b [kW por kg/s]"),
        ("Qreg_Qi", "Qreg/Qi"),
        ("Qout_m_b", "Qout/m_b [kW por kg/s]"),
        ("ratio_P", "P_alta/P_baja"), ("m_O2", "m_O2"))


def num(v):
    """float o None (tolera '', 'None', 'True')."""
    if v in (None, "", "None"):
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def bool_col(v) -> bool:
    return str(v).strip().lower() in ("true", "1")


def fmt(v, n=6) -> str:
    x = num(v) if not isinstance(v, (int, float)) else float(v)
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


def genuino(f) -> bool:
    """convergio=True y clase != NO_CONVERGIO."""
    return bool_col(f.get("convergio")) and clase(f) != "NO_CONVERGIO"


def _vals(filas: list, var: str) -> list:
    return [num(f.get(var)) for f in filas if num(f.get(var)) is not None]


def percentiles(vals: list) -> dict:
    """min, p10, mediana, p90, max (y n). `None` si no hay datos."""
    if not vals:
        return dict(n=0, minimo=None, p10=None, mediana=None, p90=None,
                    maximo=None)
    q = np.percentile(np.asarray(vals, float), [0, 10, 50, 90, 100])
    return dict(n=len(vals), minimo=float(q[0]), p10=float(q[1]),
                mediana=float(q[2]), p90=float(q[3]), maximo=float(q[4]))


def ventanas(filas: list, centro: str) -> list:
    """Percentiles por variable entre KALINA confiables y entre los no KALINA."""
    kal = [f for f in filas if f.get("centro") == centro and confiable(f)]
    no = [f for f in filas if f.get("centro") == centro and not es_kalina(f)]
    out = []
    for var in VARIABLES:
        out.append(dict(centro=centro, variable=var, grupo="KALINA_confiable",
                        **percentiles(_vals(kal, var))))
    for var in VARIABLES:
        out.append(dict(centro=centro, variable=var, grupo="no_KALINA",
                        **percentiles(_vals(no, var))))
    return out


def ks_filas(filas: list, centro: str) -> list:
    """KS de cada variable: KALINA confiables vs los demas puntos genuinos."""
    kal = [f for f in filas if f.get("centro") == centro and confiable(f)]
    otros = [f for f in filas
             if f.get("centro") == centro and genuino(f) and not confiable(f)]
    out = []
    for var in VARIABLES:
        a, b = _vals(kal, var), _vals(otros, var)
        if not a or not b:
            out.append(dict(centro=centro, variable=var, ks=None,
                            p_valor=None, n_kalina=len(a), n_otros=len(b)))
            continue
        r = ks_2samp(a, b)
        out.append(dict(centro=centro, variable=var, ks=float(r.statistic),
                        p_valor=float(r.pvalue), n_kalina=len(a),
                        n_otros=len(b)))
    out.sort(key=lambda d: (d["ks"] is None, -(d["ks"] or 0.0)))
    return out


def prcc_filas(filas: list, centro: str) -> list:
    """PRCC de cada variable con eta, solo sobre los KALINA confiables.

    Transforma las 9 variables y eta a rangos; para cada variable regresa su
    rango y el de eta contra los rangos de las otras 8 (minimos cuadrados) y
    correlaciona los residuos (Pearson)."""
    kal = [f for f in filas if f.get("centro") == centro and confiable(f)]
    n = len(kal)
    if n < 10:
        return []
    X = np.array([[num(f.get(v)) for v in VARIABLES] for f in kal], float)
    y = np.array([num(f.get("eta")) for f in kal], float)
    R = np.column_stack([rankdata(X[:, j]) for j in range(X.shape[1])])
    ry = rankdata(y)
    out = []
    for j, var in enumerate(VARIABLES):
        Z = np.column_stack([np.ones(n), np.delete(R, j, axis=1)])
        rx = R[:, j]
        bx, *_ = np.linalg.lstsq(Z, rx, rcond=None)
        by, *_ = np.linalg.lstsq(Z, ry, rcond=None)
        ex, ey = rx - Z @ bx, ry - Z @ by
        prcc = float(np.corrcoef(ex, ey)[0, 1])
        out.append(dict(centro=centro, variable=var, prcc=prcc,
                        abs_prcc=abs(prcc), n=n))
    out.sort(key=lambda d: -d["abs_prcc"])
    return out


def top10(filas: list, centro: str) -> list:
    """10 KALINA confiables de mayor eta con sus 9 variables."""
    kal = [f for f in filas if f.get("centro") == centro and confiable(f)]
    kal.sort(key=lambda f: num(f.get("eta")) or -1.0, reverse=True)
    out = []
    for i, f in enumerate(kal[:10], 1):
        d = dict(centro=centro, rank=i, id_punto=f.get("id_punto"),
                 eta=num(f.get("eta")))
        d.update({v: num(f.get(v)) for v in VARIABLES})
        out.append(d)
    return out


def _mag(nombre: str, f: dict):
    def d(a, b):
        a, b = num(a), num(b)
        return None if a is None or not b else a / b
    return {"dh_turb": lambda: num(f.get("dh_turb")),
            "Wnet_m_b": lambda: d(f.get("Wnet"), f.get("m_b")),
            "Qin": lambda: d(f.get("Qi"), f.get("m_b")),
            "Qreg_Qi": lambda: d(f.get("Qreg"), f.get("Qi")),
            "Qout_m_b": lambda: d(f.get("Qout"), f.get("m_b")),
            "ratio_P": lambda: d(f.get("P_alta"), f.get("P_baja")),
            "m_O2": lambda: num(f.get("m_O2"))}[nombre]()


def equipos_filas(filas: list, centro: str) -> list:
    """min / mediana / max de cada magnitud entre KALINA confiables."""
    kal = [f for f in filas if f.get("centro") == centro and confiable(f)]
    out = []
    for nombre, etiqueta in MAGS:
        vals = [_mag(nombre, f) for f in kal]
        vals = [v for v in vals if v is not None]
        q = percentiles(vals)
        out.append(dict(centro=centro, magnitud=etiqueta, n=q["n"],
                        minimo=q["minimo"], mediana=q["mediana"],
                        maximo=q["maximo"]))
    return out
