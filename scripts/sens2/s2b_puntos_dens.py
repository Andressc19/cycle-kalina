# -*- coding: utf-8 -*-
"""Sens2 etapa B - puntos DENS: ~150 KALINA representativos para obtener flujo volumetrico de turbina y altura de bomba.

Cinco grupos de 30 puntos KALINA dentro del rango experimental: el LHS de cada centro (estudios 3 y 14: C1..C4) y el resto de estudios
(sin centro). En cada grupo, 30 puntos en posiciones equiespaciadas del orden por eta (cuantiles 0 a 1). Mismos valores de las 10
variables que el conjunto original; se vuelven a resolver para guardar los estados y calcular densidades. m_b = 1.0.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_DIR)]
from s2b_puntos import DEDUP, VARIABLES  # noqa: E402

BARRIDOS_CLI = ("DENS", "all")
N_GRUPO = 30
GRUPOS = (("C1", "C1 Husavik"), ("C2", "C2 ancla A*"), ("C3", "C3 caliente 150 C"), ("C4", "C4 frio 110 C"), ("SC", "Sin centro (muestreo o malla)"))


def tareas(barrido):
    d = pd.read_csv(DEDUP)
    k = d[(d["clasificacion"] == "KALINA") & ~d["fuera_rango"].astype(bool)]
    out = []
    for cod, centro in GRUPOS:
        g = k[k["centro"] == centro]
        g = g[g["estudio"].isin([3, 14])] if cod != "SC" else g
        g = g.sort_values(["eta_pct", "id_punto"]).reset_index(drop=True)
        pos = sorted(set(int(round(p)) for p in np.linspace(0, len(g) - 1, min(N_GRUPO, len(g)))))
        for i in pos:
            r = g.iloc[i]
            combo = {v: float(r[v]) for v in VARIABLES}
            combo["m_b"] = 1.0
            out.append(dict(id_punto="DN-%s-%s" % (cod, r["id_punto"]), barrido="DENS", centro=cod, par="", var1="eta_pct_original",
                            val1=float(r["eta_pct"]), var2="", val2=None, combo=combo))
    return out


if __name__ == "__main__":
    t = tareas("DENS")
    print(len(t), "puntos")
    for cod, _ in GRUPOS:
        print(cod, sum(1 for x in t if x["centro"] == cod))
