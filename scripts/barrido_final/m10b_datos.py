"""M10b — utilidades compartidas (TASK_CONTEXT final_M10b_xb_bajo).

Directorio de salida, ancla de Húsavík (la misma de M10), el OFAT de x_b bajo
(0.30–0.70) y la malla x_b × P_baja bajas. Reutiliza la infraestructura de
`m10_datos` (reanudar / leer / es_kalina / confiable) y solo añade lo propio:
las tareas, su clave de reanudación y las muestras.

La etiqueta "x_b bajo" (< 0.55) es de reporte, no un filtro.
"""
from __future__ import annotations

import csv, os, sys  # noqa: E401,E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

import numpy as np  # noqa: E402

from comun import COLS  # noqa: E402
import m10_datos as d10  # noqa: E402

HUMO = os.environ.get("M10B_HUMO") == "1"
OUT = _RAIZ / "resultados" / (
    "2026-10-09_final_M10b_xb_bajo/humo" if HUMO
    else "2026-10-09_final_M10b_xb_bajo")
M10_OUT = _RAIZ / "resultados" / "2026-10-09_final_M10_husavik"
VARS11 = d10.VARS11
ANCLA = dict(P_alta=3300.0, P_baja=690.0, x_b=0.82, T_fuente=394.15,
             T_sumidero=278.15, eta_t=0.90, eta_p=0.80, eps_hrvg=0.85,
             eps_reg=0.75, eps_cond=0.95, m_b=1.0)
PISO_B = 283.15
XB_OFAT = np.linspace(0.30, 0.70, 17)
XB_MALLA = (0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70)
PB_MALLA = (200.0, 300.0, 400.0, 500.0, 600.0, 700.0)
XB_BAJO = 0.55
COF = list(COLS) + ["variable", "valor"]
CM = list(COLS)


def tareas_ofat() -> list:
    """OFAT de x_b (17 puntos) sobre el ancla, P_baja 690."""
    return [dict(parte="ofat", variable="x_b", valor=float(v), piso=PISO_B,
                 combo=dict(ANCLA, x_b=float(v)),
                 tag=f"m10b:x_b={float(v):.10g}") for v in XB_OFAT]


def tareas_malla() -> list:
    """Malla x_b × P_baja (9 × 6) sobre el ancla."""
    out = []
    for xb in XB_MALLA:
        for pb in PB_MALLA:
            out.append(dict(parte="malla", x_b=float(xb), p_baja=float(pb),
                            piso=PISO_B,
                            combo=dict(ANCLA, x_b=float(xb), P_baja=float(pb)),
                            tag=f"m10b:xb{xb}:pb{pb:g}"))
    return out


def tareas() -> list:
    """Todas (OFAT + malla); con `M10B_HUMO=1`, 1 por parte (2 en total)."""
    tas = tareas_ofat() + tareas_malla()
    if not HUMO:
        return tas
    return [t for parte in ("ofat", "malla")
            for t in [u for u in tas if u["parte"] == parte][:1]]


def clave(t: dict) -> tuple:
    """Clave de reanudación (misma forma que `m10_datos.clave_fila`)."""
    if t["parte"] == "ofat":
        return ("ofat", t["variable"], d10._s(t["valor"]))
    return ("malla", d10._s(t["x_b"]), d10._s(t["p_baja"]))


def escribir_muestras(tas: list) -> None:
    """`m10b_muestra.csv`: todas las muestras ANTES de correr nada."""
    cols = (["parte"] + list(VARS11) + ["piso", "variable", "valor", "tag"])
    with open(OUT / "m10b_muestra.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for t in tas:
            f = dict(t.get("combo", {}))
            f.update(parte=t["parte"], piso=t["piso"], variable=t.get("variable"),
                     valor=t.get("valor"), tag=t["tag"])
            w.writerow({c: f.get(c) for c in cols})
        fh.flush()
    print(f"m10b_muestra.csv: {len(tas)} filas guardadas ANTES de correr",
          flush=True)
