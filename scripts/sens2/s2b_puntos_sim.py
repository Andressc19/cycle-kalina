# -*- coding: utf-8 -*-
"""Sens2 etapa B - puntos SIM: propagacion de incertidumbre con eps_cond perturbado de forma SIMETRICA.

En U1 el centro tiene eps_cond = 0.95 (el tope del proyecto), asi que la perturbacion solo podia ir hacia abajo y P(KALINA) quedaba
sesgada. Aqui eps_cond se centra en 0.90 y se perturba +-0.05 (uniforme, intervalo [0.85, 0.95], simetrico); las otras 9 variables se
perturban igual que en el escenario A de U1 (`u1_puntos.TOL`). LHS de 48 puntos por centro, semilla propia, P_alta >= 1.3 P_baja.
"""
from __future__ import annotations

import sys
from pathlib import Path

from scipy.stats import qmc

_DIR = Path(__file__).resolve().parent
sys.path[:0] = [str(_DIR), str(_DIR.parents[0] / "sens1"), str(_DIR.parents[0] / "barrido_final")]
import u1_puntos as U  # noqa: E402
import x1_cargar as X  # noqa: E402

BARRIDOS_CLI = ("SIM", "all")
EPS_CENTRO = 0.90
EPS_TOL = 0.05
N = 48
SEMILLA = 20261019


def tareas(barrido):
    out = []
    for k, nombre in enumerate(X.CENTROS):
        centro = dict(X.CENTROS[nombre], m_b=1.0)
        centro["eps_cond"] = EPS_CENTRO
        iv = {v: U.intervalo(v, centro, 1.0) for v in U.VARIABLES}
        iv["eps_cond"] = (EPS_CENTRO - EPS_TOL, EPS_CENTRO + EPS_TOL)
        u = qmc.LatinHypercube(d=len(U.VARIABLES), seed=SEMILLA + 10 * k).random(N)
        n = 0
        for fila in u:
            combo = dict(centro)
            for j, v in enumerate(U.VARIABLES):
                combo[v] = round(iv[v][0] + float(fila[j]) * (iv[v][1] - iv[v][0]), 4)
            if combo["P_alta"] < 1.3 * combo["P_baja"]:
                continue
            n += 1
            cod = U.CODIGO[nombre]
            out.append(dict(id_punto="SIM-%s-%03d" % (cod, n), barrido="SIM", centro=cod, par="", var1="eps_cond_centro", val1=EPS_CENTRO,
                            var2="", val2=None, combo=combo))
    return out


if __name__ == "__main__":
    t = tareas("SIM")
    print(len(t), "puntos")
    for c in ("C1", "C2", "C3", "C4"):
        print(c, sum(1 for x in t if x["centro"] == c))
