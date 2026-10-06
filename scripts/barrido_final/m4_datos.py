"""M4 — caja de muestreo, lectura de `m4_lhs.csv` y utilidades del análisis.

La caja de 10 variables viene de `TASK_CONTEXT final_M4` (rangos fijados por el
director, con su respaldo); `m_b = 1.0` y el piso de O2 de cada punto es su
propia `T_sumidero`. `leer()` devuelve las filas de `m4_lhs.csv` tipadas, con
las tres variables derivadas (`dP`, `rP`, `dT_fs`) y el marcador de punto
genuino. Todo el análisis se re-ejecuta sobre el CSV sin recalcular el ciclo.
"""
from __future__ import annotations

import csv, os, sys  # noqa: E401,E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

# Rangos de la caja, fijados por el director en TASK_CONTEXT final_M4 (§caja).
CAJA = {"T_fuente": (380.0, 500.0), "T_sumidero": (278.15, 303.55),
        "P_alta": (2000.0, 5000.0), "P_baja": (300.0, 1500.0),
        "x_b": (0.50, 0.85), "eta_t": (0.75, 0.92), "eta_p": (0.65, 0.90),
        "eps_hrvg": (0.60, 0.95), "eps_reg": (0.60, 0.95),
        "eps_cond": (0.70, 0.95)}
VARS10 = tuple(CAJA)                       # mismo orden de la caja (d = 10)
DERIV = ("dP", "rP", "dT_fs")              # se añaden en el análisis
VARS13 = VARS10 + DERIV
GENU = frozenset({"KALINA", "CORREGIBLE", "INVIABLE"})
SEED = 20261006
HUMO = os.environ.get("M4_HUMO") == "1"
OUT = _RAIZ / "resultados" / ("2026-10-06_final_M4/humo" if HUMO
                              else "2026-10-06_final_M4")
FLOT = ("id_muestra", "eta", "Wnet", "D", "m_O1", "m_O2", "m_O3", "m_O5",
        "t_s", "m_b", *VARS10, *DERIV)
BOOL = ("convergio", "fuera_rango")


def num(s):
    """Cadena del CSV a `float`; vacío o inconvertible → `None`."""
    if s in (None, ""):
        return None
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def genu(f: dict) -> bool:
    """Punto genuino: `clasificacion` ∈ {KALINA, CORREGIBLE, INVIABLE}.

    Una fila con `convergio=True` y `NO_CONVERGIO` es espuria (N2): como su
    clase no está en el conjunto, es NO genuina en todo (TASK_CONTEXT §caja).
    """
    return f["clasificacion"] in GENU


def u_de(f: dict, v: str) -> float:
    """Posición de la variable dentro de su rango, normalizada a [0, 1]."""
    a, b = CAJA[v]
    return (f[v] - a) / (b - a)


def derivar(f: dict) -> dict:
    """Las tres variables derivadas de TASK_CONTEXT final_M4 §3."""
    f["dP"] = f["P_alta"] - f["P_baja"]
    f["rP"] = f["P_alta"] / f["P_baja"]
    f["dT_fs"] = f["T_fuente"] - f["T_sumidero"]
    return f


def leer(nombre: str = "m4_lhs.csv") -> list:
    """Filas de `OUT/nombre` con números, booleanos y derivadas ya tipados."""
    with open(OUT / nombre, encoding="utf-8", newline="") as fh:
        filas = list(csv.DictReader(fh))
    for f in filas:
        for k in FLOT:
            f[k] = num(f.get(k))
        for k in BOOL:
            v = f.get(k)
            f[k] = None if v in (None, "") else v == "True"
        f["clasificacion"] = f.get("clasificacion") or None
        derivar(f)
    return filas


def escribir(nombre: str, cab: list, filas: list) -> None:
    """CSV de salida del análisis (una fila por dict de `filas`)."""
    with open(OUT / nombre, "w", encoding="utf-8", newline="") as fh:
        esc = csv.DictWriter(fh, fieldnames=cab)
        esc.writeheader()
        for f in filas:
            esc.writerow({c: f.get(c) for c in cab})
    print(f"{nombre}: {len(filas)} filas", flush=True)
