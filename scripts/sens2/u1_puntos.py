# -*- coding: utf-8 -*-
"""Sens2 U1 - diseno de la propagacion de incertidumbre alrededor de los 4 centros KALINA.

Por centro y escenario: LHS de 10 variables con distribucion uniforme en [centro - tol, centro + tol]
(recortada a los limites del proyecto). Escenario A = tolerancias nominales; B = el doble.
Las tolerancias son SUPUESTOS DE ESCENARIO (variabilidad de operacion y de rendimiento de equipos), no
mediciones: se declaran en `TOL` y en el informe.
"""
from __future__ import annotations

import sys
from pathlib import Path

from scipy.stats import qmc

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_DIR.parents[0] / "sens1"), str(_DIR.parents[0] / "barrido_final")]
import x1_cargar as X  # noqa: E402

VARIABLES = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b",
             "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")
# tolerancia absoluta (escenario A); para P_alta y P_baja es relativa (fraccion del centro)
TOL = {"T_fuente": 5.0, "T_sumidero": 3.0, "P_alta": 0.05, "P_baja": 0.05, "x_b": 0.02,
       "eta_t": 0.05, "eta_p": 0.05, "eps_hrvg": 0.05, "eps_reg": 0.05, "eps_cond": 0.05}
ESCENARIOS = {"U1A": 1.0, "U1B": 2.0}
# Bloques de la ampliacion (revision de evaluador): segundo lote independiente de A (estabilidad), A sin perturbar
# eps_cond (aisla el sesgo del tope 0.95) y barrido solo de eps_cond (10 niveles por centro).
AMPLIACION = {"U1A2": dict(factor=1.0, semilla=1000, fijas=()), "U1C": dict(factor=1.0, semilla=2000, fijas=("eps_cond",))}
N_SCAN = 10
LIMITES = {"T_sumidero": (278.15, 303.15), "x_b": (0.30, 0.95), "eta_t": (0.40, 0.95),
           "eta_p": (0.40, 0.95), "eps_hrvg": (0.40, 0.95), "eps_reg": (0.40, 0.95),
           "eps_cond": (0.40, 0.95)}
N = 48
SEMILLA = 20261017
CODIGO = {"C1 Husavik": "C1", "C2 ancla A*": "C2", "C3 caliente 150 C": "C3", "C4 frio 110 C": "C4"}
BARRIDOS_CLI = ("U1A", "U1B", "U1A2", "U1C", "U1D", "all", "ampliacion")


def intervalo(var, centro, factor):
    c = float(centro[var])
    tol = TOL[var] * factor * (c if var in ("P_alta", "P_baja") else 1.0)
    lo, hi = c - tol, c + tol
    if var in LIMITES:
        lo, hi = max(lo, LIMITES[var][0]), min(hi, LIMITES[var][1])
    return lo, hi


def _lhs(e, k, nombre, factor, semilla, fijas):
    c = X.CENTROS[nombre]
    centro = dict(c, m_b=1.0)
    iv = {v: intervalo(v, centro, factor) for v in VARIABLES}
    for v in fijas:
        iv[v] = (float(centro[v]), float(centro[v]))
    u = qmc.LatinHypercube(d=len(VARIABLES), seed=SEMILLA + semilla + 10 * k + int(factor)).random(N)
    out, n = [], 0
    for fila in u:
        combo = dict(centro)
        for j, v in enumerate(VARIABLES):
            combo[v] = round(iv[v][0] + float(fila[j]) * (iv[v][1] - iv[v][0]), 4)
        if combo["P_alta"] < 1.3 * combo["P_baja"]:
            continue
        n += 1
        out.append(dict(id_punto="%s-%s-%03d" % (e, CODIGO[nombre], n), barrido=e, centro=CODIGO[nombre], par="",
                        var1="", val1=None, var2="", val2=None, combo=combo))
    return out


def _scan(nombre):
    c = dict(X.CENTROS[nombre], m_b=1.0)
    out = []
    for i in range(N_SCAN):
        combo = dict(c)
        combo["eps_cond"] = round(0.90 + 0.05 * i / (N_SCAN - 1), 4)
        out.append(dict(id_punto="U1D-%s-%03d" % (CODIGO[nombre], i + 1), barrido="U1D", centro=CODIGO[nombre],
                        par="", var1="eps_cond", val1=combo["eps_cond"], var2="", val2=None, combo=combo))
    return out


def tareas(barrido):
    quiero = {"all": ["U1A", "U1B"], "ampliacion": ["U1A2", "U1C", "U1D"]}.get(barrido, [barrido])
    out = []
    for e in quiero:
        for k, nombre in enumerate(X.CENTROS):
            if e in ESCENARIOS:
                out += _lhs(e, k, nombre, ESCENARIOS[e], 0, ())
            elif e in AMPLIACION:
                s = AMPLIACION[e]
                out += _lhs(e, k, nombre, s["factor"], s["semilla"], s["fijas"])
            elif e == "U1D":
                out += _scan(nombre)
    return out


if __name__ == "__main__":
    t = tareas("all")
    print(len(t), "puntos")
    for e in ESCENARIOS:
        for c in CODIGO.values():
            print(e, c, sum(1 for x in t if x["barrido"] == e and x["centro"] == c))
    c1 = X.CENTROS["C1 Husavik"]
    print({v: tuple(round(a, 3) for a in intervalo(v, c1, 1.0)) for v in VARIABLES})
