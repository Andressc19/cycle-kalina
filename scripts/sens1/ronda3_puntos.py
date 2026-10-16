"""Sensibilidad 1, Ronda 3 - puntos de los barridos N9, N10 y N8.

N9: dos mallas 7x7 por centro en C3 y C4 (B5 y B6) con el punto base PRIMERO;
N10: malla 5x7 (P_alta x P_baja) en C1, C3 y C4, sin base; N8: LHS de 9
variables en C3 y C4 (250 por centro, semilla 20261017), redondeado, con
P_alta < 1.3*P_baja descartado SIN re-muestreo; eta_p = 0.80 y m_b = 1.0 fijos.
Salidas en `resultados/2026-10-16_sens1_ronda3/`; se usa como modulo o script.
"""
from __future__ import annotations

import csv
from pathlib import Path

from scipy.stats.qmc import LatinHypercube

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
OUT = _RAIZ / "resultados" / "2026-10-16_sens1_ronda3"

VARIABLES = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b",
             "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")
COMBO = tuple(VARIABLES) + ("m_b",)
M_B = 1.0
CENTROS = (
    ("C3", dict(T_fuente=423.15, T_sumidero=280.5, P_alta=3150.0, P_baja=950.0,
                x_b=0.75, m_b=M_B, eta_t=0.85, eta_p=0.80, eps_hrvg=0.85,
                eps_reg=0.75, eps_cond=0.95)),
    ("C4", dict(T_fuente=383.15, T_sumidero=282.5, P_alta=3880.0, P_baja=910.0,
                x_b=0.88, m_b=M_B, eta_t=0.85, eta_p=0.80, eps_hrvg=0.85,
                eps_reg=0.75, eps_cond=0.95)))
CENTRO_C1 = ("C1", dict(T_fuente=394.15, T_sumidero=278.15, P_alta=3300.0,
                        P_baja=690.0, x_b=0.82, m_b=M_B, eta_t=0.85, eta_p=0.80,
                        eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.95))
CENTROS_N10 = (CENTRO_C1,) + CENTROS
P_ALTA_N10 = [4000.0, 5000.0, 6000.0, 7000.0, 8000.0]
P_BAJA_N10 = {"C1": [500.0, 600.0, 690.0, 800.0, 950.0, 1100.0, 1300.0],
              "C3": [500.0, 650.0, 800.0, 950.0, 1100.0, 1300.0, 1600.0],
              "C4": [500.0, 650.0, 800.0, 910.0, 1050.0, 1250.0, 1500.0]}
PARES = (("B5", "eps_reg", "eta_t"), ("B6", "eps_hrvg", "T_fuente"))
GRID = {
    "eps_reg": [0.50, 0.60, 0.70, 0.75, 0.80, 0.90, 0.95],
    "eta_t": [0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95],
    "eps_hrvg": [0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95],
    "T_fuente_C": {"C3": [110, 130, 140, 150, 160, 180, 200],
                   "C4": [80, 90, 100, 110, 120, 135, 150]},
}
VARS_N8 = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "eta_t",
           "eps_hrvg", "eps_reg", "eps_cond")
RANGOS_N8 = {
    "C3": [(363.15, 463.15), (278.15, 295.65), (1500.0, 5000.0),
           (500.0, 1800.0), (0.40, 0.95), (0.50, 0.95), (0.50, 0.95),
           (0.50, 0.95), (0.85, 0.95)],
    "C4": [(353.15, 423.15), (278.15, 290.65), (1500.0, 5000.0),
           (700.0, 1800.0), (0.55, 0.95), (0.50, 0.95), (0.50, 0.95),
           (0.50, 0.95), (0.85, 0.95)]}
N8_SEED, N8_N = 20261017, 250
DEFINIDOS = ("N9", "N10", "N8")
BARRIDOS_CLI = ("N9", "N10", "N8", "all")
META = ("id_punto", "barrido", "centro", "par", "var1", "val1", "var2", "val2")
CM_DESC = ["barrido", "centro", "n_candidatas", "n_descartados", "n_duplicados",
           "n_final"]

def redondear(var, v):
    """T a 0.5 K, P a 10 kPa, x_b a 0.01 y eta/eps al 0.05 mas cercano."""
    p = {"T_fuente": 0.5, "T_sumidero": 0.5, "P_alta": 10.0,
         "P_baja": 10.0, "x_b": 0.01}.get(var, 0.05)
    return round(round(v / p) * p, 2)


def valores(var, centro):
    """Rejilla de N9 en unidades de diseno (K si T_fuente)."""
    if var == "T_fuente":
        return [round(c + 273.15, 2) for c in GRID["T_fuente_C"][centro]]
    return [float(v) for v in GRID[var]]


def clave(combo):
    return tuple(round(float(combo[k]), 6) for k in VARIABLES)


def n9_puntos():
    """(tareas N9, descartes); base primero y dedup por combinacion."""
    tareas, desc = [], []
    for centro, base in CENTROS:
        vistos, por_par, cand = set(), {}, [0, 0]

        def add(par, a, va, b, vb, combo):
            cand[0] += 1
            k = clave(combo)
            if k in vistos:
                cand[1] += 1
                return
            vistos.add(k)
            por_par[par] = por_par.get(par, 0) + 1
            tareas.append(dict(id_punto=f"N9-{centro}-{par}-{por_par[par]:04d}",
                               barrido="N9", centro=centro, par=par, var1=a,
                               val1=va, var2=b, val2=vb, combo=dict(combo)))
        ini = len(tareas)
        add("base", "", None, "", None, dict(base))
        for par, a, b in PARES:
            for va in valores(a, centro):
                for vb in valores(b, centro):
                    add(par, a, float(va), b, float(vb),
                        dict(base, **{a: float(va), b: float(vb)}))
        desc.append(dict(barrido="N9", centro=centro, n_candidatas=cand[0],
                         n_descartados=0, n_duplicados=cand[1],
                         n_final=len(tareas) - ini))
    return tareas, desc


def n10_puntos():
    """(tareas N10, descartes); malla 5x7 por centro, SIN punto base."""
    tareas, desc = [], []
    for centro, base in CENTROS_N10:
        vistos, cand, n = set(), [0, 0], 0
        for pa in P_ALTA_N10:
            for pb in P_BAJA_N10[centro]:
                cand[0] += 1
                combo = dict(base, P_alta=float(pa), P_baja=float(pb))
                k = clave(combo)
                if k in vistos:
                    cand[1] += 1
                    continue
                vistos.add(k)
                n += 1
                tareas.append(dict(id_punto=f"N10-{centro}-{n:04d}", barrido="N10",
                                   centro=centro, par="", var1="P_alta",
                                   val1=float(pa), var2="P_baja", val2=float(pb),
                                   combo=combo))
        desc.append(dict(barrido="N10", centro=centro, n_candidatas=cand[0],
                         n_descartados=0, n_duplicados=cand[1], n_final=n))
    return tareas, desc


def n8_puntos():
    """(tareas N8, descartes); LHS de 9 variables, descarta sin re-muestrear."""
    tareas, desc = [], []
    for centro, base in CENTROS:
        rangos = RANGOS_N8[centro]
        u = LatinHypercube(d=len(VARS_N8), seed=N8_SEED).random(N8_N)
        vistos, n, dsc, dup = set(), 0, 0, 0
        for fila in u:
            combo = {v: redondear(v, rangos[k][0] + float(fila[k]) *
                                  (rangos[k][1] - rangos[k][0]))
                     for k, v in enumerate(VARS_N8)}
            if combo["P_alta"] < 1.3 * combo["P_baja"]:
                dsc += 1
                continue
            full = dict(base, **combo)
            k = clave(full)
            if k in vistos:
                dup += 1
                continue
            vistos.add(k)
            n += 1
            tareas.append(dict(id_punto=f"N8-{centro}-{n:04d}", barrido="N8",
                               centro=centro, par="", var1="", val1=None,
                               var2="", val2=None, combo=full))
        desc.append(dict(barrido="N8", centro=centro, n_candidatas=N8_N,
                         n_descartados=dsc, n_duplicados=dup, n_final=n))
    return tareas, desc

_FABRICAS = {"N9": n9_puntos, "N10": n10_puntos, "N8": n8_puntos}


def tareas(barrido):
    """Tareas del barrido pedido; [] si todavia no esta definido."""
    if barrido == "all":
        return sum((tareas(b) for b in DEFINIDOS), [])
    fn = _FABRICAS.get(barrido)
    return [] if fn is None else fn()[0]

def diseno_completo():
    """Tareas y descartes de los barridos definidos + fila TOTAL por barrido."""
    ts, ds = [], []
    for b in DEFINIDOS:
        tb, db = _FABRICAS[b]()
        ts += tb
        tot = {k: sum(r[k] for r in db) for k in CM_DESC[2:]}
        ds += db + [dict(barrido=b, centro="TOTAL", **tot)]
    return ts, ds


def _escribir_diseno(dirs):
    dirs.mkdir(parents=True, exist_ok=True)
    todos, desc = diseno_completo()
    plano = ({**{k: t[k] for k in META}, **t["combo"]} for t in todos)
    for nom, cols, filas in (("ronda3_diseno.csv", list(META) + list(COMBO),
                              plano), ("ronda3_descartes.csv", CM_DESC, desc)):
        with open(dirs / nom, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(filas)
    print(f"diseno: {len(todos)} filas | descartes: {len(desc)} filas", flush=True)
    for r in desc:
        print(f"  {r['barrido']} / {r['centro']}: {r['n_final']} planeados", flush=True)
    return todos, desc

if __name__ == "__main__":
    _escribir_diseno(OUT)
