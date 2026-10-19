# -*- coding: utf-8 -*-
"""Sens2 etapa B - puntos del motor: reintento de NO_CONVERGIO y pisos de P_baja a 25 kPa.

REINT0: control de determinismo (15 NO_CONVERGIO rapidos, t_s < 100 s) mas los NO_CONVERGIO que agotaron el presupuesto
        (t_s >= 250 s). Se corren con presupuesto y tope mayores (variables de entorno S2B_PRESUPUESTO y S2B_LIMITE).
PISOS:  P_baja con paso de 25 kPa entre el ultimo nivel no KALINA y el primer nivel KALINA de la malla B2 (P_baja x x_b),
        en los 4 centros y 3 niveles de x_b por centro; el resto de variables en el centro.
Cada punto sale con m_b = 1.0 (igual que el conjunto original).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_DIR), str(_DIR.parents[0] / "sens1"), str(_DIR.parents[0] / "barrido_final")]
import x1_cargar as X  # noqa: E402

VARIABLES = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")
CODIGO = {"C1 Husavik": "C1", "C2 ancla A*": "C2", "C3 caliente 150 C": "C3", "C4 frio 110 C": "C4"}
XB_PISOS = {"C1 Husavik": (0.82, 0.90, 0.95), "C2 ancla A*": (0.50, 0.55, 0.60),
            "C3 caliente 150 C": (0.75, 0.88, 0.95), "C4 frio 110 C": (0.83, 0.88, 0.95)}
PASO = 25.0
SEMILLA = 20261018
N_CONTROL = 15
BARRIDOS_CLI = ("REINT0", "PISOS", "all")
DEDUP = _RAIZ / "resultados" / "2026-10-17_sens2_P2" / "p2_dataset_dedup.csv"


def _tarea(idp, barrido, centro, combo, var1="", val1=None):
    return dict(id_punto=idp, barrido=barrido, centro=centro, par="", var1=var1, val1=val1, var2="", val2=None, combo=combo)


def _reint0():
    d = pd.read_csv(DEDUP)
    nc = d[d["clasificacion"] == "NO_CONVERGIO"].copy()
    lentos = nc[nc["t_s"] >= 250.0]
    rap = nc[nc["t_s"] < 100.0]
    rng = np.random.default_rng(SEMILLA)
    ctrl = rap.iloc[np.sort(rng.choice(len(rap), size=min(N_CONTROL, len(rap)), replace=False))]
    out = []
    for etiqueta, g in (("lento", lentos), ("control", ctrl)):
        for r in g.itertuples():
            combo = {v: float(getattr(r, v)) for v in VARIABLES}
            combo["m_b"] = 1.0
            out.append(_tarea("RN-%s-%s" % (etiqueta, r.id_punto), "REINT0", str(r.centro), combo, var1="t_s_original", val1=float(r.t_s)))
    return out


def _pisos():
    import s2_calc as C
    out = []
    for nombre, xbs in XB_PISOS.items():
        _, cls, av, bv = C.malla_clases(nombre, "B2")
        av, bv = [float(a) for a in av], [float(b) for b in bv]
        c = dict(X.CENTROS[nombre], m_b=1.0)
        for xb in xbs:
            j = int(np.argmin([abs(b - xb) for b in bv]))
            col = [i for i in range(len(av)) if cls[i, j] == "K"]
            jmin = min(col) if col else len(av) - 1
            hi = av[jmin]
            lo = av[jmin - 1] if jmin > 0 else hi - 100.0
            for k, p in enumerate(np.arange(lo, hi + 1e-9, PASO)):
                if min(abs(p - lo), abs(p - hi)) < 1e-9:
                    continue                        # extremos ya conocidos de la malla
                combo = dict(c)
                combo["x_b"], combo["P_baja"] = float(xb), float(round(p, 4))
                if combo["P_alta"] < 1.3 * combo["P_baja"]:
                    continue
                out.append(_tarea("PS-%s-x%03d-p%04d" % (CODIGO[nombre], round(xb * 100), round(p)), "PISOS", CODIGO[nombre],
                                  combo, var1="P_baja", val1=float(round(p, 4))))
    return out


def tareas(barrido):
    quiero = {"all": ["REINT0", "PISOS"]}.get(barrido, [barrido])
    out = []
    for b in quiero:
        out += _reint0() if b == "REINT0" else _pisos() if b == "PISOS" else []
    return out


if __name__ == "__main__":
    for b in ("REINT0", "PISOS"):
        t = tareas(b)
        print(b, len(t), "puntos")
        for c in sorted({x["centro"] for x in t}):
            print("  ", c, sum(1 for x in t if x["centro"] == c))
