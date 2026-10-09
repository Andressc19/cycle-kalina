"""M10 — utilidades compartidas (TASK_CONTEXT final_M10_husavik).

Directorio de salida, ancla de Húsavík, familias de la Fase 3, muestras de B1/B2,
"punto genuino" / "KALINA confiable", tipado y reanudación.
"""
from __future__ import annotations

import csv, os, sys  # noqa: E401,E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

import numpy as np  # noqa: E402

HUMO = os.environ.get("M10_HUMO") == "1"
OUT = _RAIZ / "resultados" / (
    "2026-10-09_final_M10_husavik/humo" if HUMO else "2026-10-09_final_M10_husavik")
F3 = _RAIZ / "resultados" / "barridos_2026-09-19" / "fase3_real"
VARS11 = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "m_b",
          "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")
ANCLA = dict(P_alta=3300.0, P_baja=690.0, x_b=0.82, T_fuente=394.15,
             T_sumidero=278.15, eta_t=0.90, eta_p=0.80, eps_hrvg=0.85,
             eps_reg=0.75, eps_cond=0.95, m_b=1.0)
PISO_B = 283.15
GENU = frozenset({"KALINA", "CORREGIBLE", "INVIABLE"})
# familia -> (archivos, piso de O2 original, variables movidas)
FAMILIAS = (
    ("F3-A", ("busqueda_husavik.csv",), 303.55, "P_alta, P_baja, x_b, eta_t, eps_reg, eps_cond"),
    ("F3-B", ("busqueda_husavik_v2.csv",), 283.15, "P_baja, eps_reg, eps_cond"),
    ("F3-C", ("mapa_2d_pbaja_epsreg.csv",), 283.15, "P_baja x eps_reg"),
    ("F3-D", ("sensibilidad_P_baja.csv", "sensibilidad_eps_cond.csv", "sensibilidad_eps_reg.csv", "sensibilidad_eta_t.csv", "sensibilidad_x_b.csv"), 283.15, "una variable por archivo (P_baja, eps_cond, eps_reg, eta_t, x_b)"),
    ("F3-E", ("sensibilidad_palta.csv", "sensibilidad_pbaja.csv", "sensibilidad_xb.csv"), 303.55, "una variable por archivo (P_alta, P_baja, x_b)"),
)
OFAT = (("T_fuente", 380.0, 430.0), ("T_sumidero", 273.15, 293.15), ("P_alta", 2500.0, 4000.0),
        ("P_baja", 500.0, 1200.0), ("x_b", 0.60, 0.95), ("eta_t", 0.75, 0.95),
        ("eta_p", 0.60, 0.90), ("eps_hrvg", 0.60, 0.95), ("eps_reg", 0.40, 0.95), ("eps_cond", 0.70, 0.95))
XB_MALLA = (0.70, 0.73, 0.76, 0.79, 0.82, 0.85, 0.88, 0.91)
PB_MALLA = (500.0, 600.0, 700.0, 800.0, 900.0, 1000.0, 1100.0, 1200.0)
N_OFAT = 2 if HUMO else 15
CFLOT = ("eta", "Wnet", "D", "m_O1", "m_O2", "m_O3", "m_O5", "q4", "q2",
         "T9_amb", "T_bub", "T_amb_diseno", "t_s", "eta_sept", "d_eta_pp",
         "valor", "min_kalina", "max_kalina", "eta_min", "eta_max", *VARS11)
CFLOT = CFLOT + ("piso_O2", "d_eta_pp_medio_abs", "d_eta_pp_max_abs")
CINT = ("fila_origen", "n", "KALINA_sept", "KALINA_ahora", "confiables_ahora",
        "coincide", "n_kalina")
CBOOL = ("convergio", "fuera_rango", "B_verificado", "coincide_clase",
         "A_verificacion_incompleta")


def num(s):
    """Cadena a `float`; vacío o inconvertible -> `None`."""
    if s in (None, ""):
        return None
    try:
        return float(s)
    except (TypeError, ValueError):
        return None

def _s(v) -> str:
    """Clave textual estable de un número (o de su cadena)."""
    try:
        return f"{float(v):.10g}"
    except (TypeError, ValueError):
        return "" if v is None else str(v)

def tipar(rows: list) -> list:
    """Tipa números y booleanos (incl. extras de M10)."""
    for f in rows:
        for k in CFLOT:
            if k in f:
                f[k] = num(f.get(k))
        for k in CINT:
            if k in f:
                v = num(f.get(k))
                f[k] = None if v is None else int(v)
        for k in CBOOL:
            if k in f:
                v = f.get(k)
                f[k] = None if v in (None, "") else str(v) == "True"
    return rows

def leer(path) -> list:
    """Filas tipadas de un CSV de M10."""
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return tipar(list(csv.DictReader(fh)))

def genu(f: dict) -> bool:
    """Punto genuino: KALINA, CORREGIBLE o INVIABLE (N2 no cuenta)."""
    return f.get("clasificacion") in GENU

def es_kalina(f: dict) -> bool:
    return f.get("clasificacion") == "KALINA"

def confiable(f: dict) -> bool:
    """KALINA, fuera_rango == False y B_verificado == True."""
    return (es_kalina(f) and f.get("fuera_rango") is False
            and f.get("B_verificado") is True)

def tareas() -> list:
    """Todas las tareas (A + B); con `M10_HUMO=1`, 2 por parte."""
    tas = tareas_fase3() + tareas_ofat() + tareas_malla()
    if not HUMO:
        return tas
    return [t for parte in ("fase3", "ofat", "malla")
            for t in [u for u in tas if u["parte"] == parte][:2]]

def tareas_fase3() -> list:
    """Cada fila KALINA de las familias F3-A…F3-E, re-evaluada con teqp."""
    out = []
    for fam, archivos, piso, _mov in FAMILIAS:
        for arch in archivos:
            with open(F3 / arch, encoding="utf-8-sig", newline="") as fh:
                for i, r in enumerate(csv.DictReader(fh)):
                    if r.get("clasificacion") != "KALINA":
                        continue
                    out.append(dict(
                        parte="fase3", familia=fam, archivo=arch, fila=i,
                        piso=piso, clase_sept="KALINA",
                        eta_sept=num(r.get("eta")),
                        combo={v: float(r[v]) for v in VARS11},
                        tag=f"m10:F:{fam}:{arch}:{i}"))
    return out

def tareas_ofat() -> list:
    """B1: `numpy.linspace`, el resto en el ancla (15 puntos por variable)."""
    out = []
    for var, lo, hi in OFAT:
        for v in np.linspace(lo, hi, N_OFAT):
            out.append(dict(parte="ofat", variable=var, valor=float(v),
                            piso=PISO_B, combo=dict(ANCLA, **{var: float(v)}),
                            tag=f"m10:{var}={float(v):.10g}"))
    return out

def tareas_malla() -> list:
    """B2: malla 2D x_b × P_baja (8 × 8) sobre el ancla."""
    out = []
    for xb in XB_MALLA:
        for pb in PB_MALLA:
            out.append(dict(parte="malla", x_b=float(xb), p_baja=float(pb),
                            piso=PISO_B,
                            combo=dict(ANCLA, x_b=float(xb), P_baja=float(pb)),
                            tag=f"m10:xb{xb}:pb{pb:g}"))
    return out


def clave(t: dict) -> tuple:
    """Clave de reanudación de una tarea (parte + identidad)."""
    if t["parte"] == "fase3":
        return ("fase3", t["familia"], t["archivo"], _s(t["fila"]))
    if t["parte"] == "ofat":
        return ("ofat", t["variable"], _s(t["valor"]))
    return ("malla", _s(t["x_b"]), _s(t["p_baja"]))


def clave_fila(f: dict) -> tuple:
    """La misma clave de `clave`, pero leída de una fila de resultado."""
    if "familia" in f:
        return ("fase3", f.get("familia"), f.get("archivo_origen"),
                _s(f.get("fila_origen")))
    if "variable" in f:
        return ("ofat", f.get("variable"), _s(f.get("valor")))
    return ("malla", _s(f.get("x_b")), _s(f.get("P_baja")))


def reanudar(path, cols: list):
    """Abre `path` en append -> `(fh, escritor, claves ya presentes)`."""
    p = Path(path)
    existe = p.exists()
    vistas = set()
    if existe:
        with open(p, encoding="utf-8-sig", newline="") as fh:
            vistas = {clave_fila(f) for f in csv.DictReader(fh)}
    fh = open(p, "a" if existe else "w", encoding="utf-8", newline="")
    esc = csv.DictWriter(fh, fieldnames=cols)
    if not existe:
        esc.writeheader()
        fh.flush()
    return fh, esc, vistas


def escribir_muestras(tas: list) -> None:
    """`m10_muestra.csv`: todas las muestras ANTES de correr nada."""
    cols = (["parte"] + list(VARS11)
            + ["piso", "familia", "archivo_origen", "fila_origen", "variable",
               "valor", "tag"])
    with open(OUT / "m10_muestra.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for t in tas:
            f = dict(t.get("combo", {}))
            f.update(parte=t["parte"], piso=t["piso"], familia=t.get("familia"),
                     archivo_origen=t.get("archivo"), fila_origen=t.get("fila"),
                     variable=t.get("variable"), valor=t.get("valor"),
                     tag=t["tag"])
            w.writerow({c: f.get(c) for c in cols})
        fh.flush()
    print(f"m10_muestra.csv: {len(tas)} filas guardadas ANTES de correr",
          flush=True)
