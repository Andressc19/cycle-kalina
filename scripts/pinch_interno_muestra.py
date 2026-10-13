"""Selección de los puntos de la sonda de pinch interno (corrección 4).

Lee `analisis_final/01_datos/todos_los_puntos.csv` (solo lectura) y arma la lista
de combos a evaluar, cada uno con `tag`, `grupo` y `motor`. No calcula nada del
ciclo. Reproducible: la muestra estratificada usa `random.Random(SEMILLA)`.

Grupos: A_estrella, opt_5_1, franja_4_2, final_4_3, husavik, elsayed (control
positivo, 23 puntos calibrados), estratificada (3.2 y 5.1 por ε_reg × ε_HRVG),
extremos (ε_reg o ε_HRVG más altos) y real (control con el motor real).
"""
from __future__ import annotations

import csv
import random
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DATOS = RAIZ / "analisis_final" / "01_datos" / "todos_los_puntos.csv"
ELSAYED = (RAIZ / "resultados" / "2026-09-24_validacion_tendencias"
           / "validacion_tendencias.csv")
SEMILLA = 20261013
VARS = ["T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "m_b", "eta_t",
        "eta_p", "eps_hrvg", "eps_reg", "eps_cond"]
PROFESOR = dict(T_fuente=623.15, T_sumidero=300.032917, P_alta=3000.0,
                P_baja=400.0, x_b=0.50, m_b=1.0, eta_t=0.85, eta_p=0.75,
                eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.80)
BINS = [(0.40, 0.60), (0.60, 0.80), (0.80, 0.9501)]
POR_CELDA = 12          # puntos por celda ε_reg × ε_HRVG
N_EXTREMOS = 10         # los N con mayor ε_reg y los N con mayor ε_HRVG
N_REAL = 4              # controles con el motor real


def _combo(r: dict) -> dict:
    return {v: float(r[v]) for v in VARS}


def _llave(c: dict) -> tuple:
    return tuple(round(c[v], 6) for v in VARS)


def _confiables() -> list:
    with open(DATOS, encoding="utf-8", newline="") as fh:
        return [r for r in csv.DictReader(fh) if r["kalina_confiable"] == "True"]


def _pt(c: dict, tag: str, grupo: str, motor: str = "teqp") -> dict:
    return dict(c, tag=tag, grupo=grupo, motor=motor)


def _bin(v: float):
    return next((i for i, (a, b) in enumerate(BINS) if a <= v < b), None)


def seleccionar() -> list:
    ok = _confiables()
    pts, vistos = [], set()

    def sumar(c, tag, grupo):
        if _llave(c) not in vistos:
            vistos.add(_llave(c))
            pts.append(_pt(c, tag, grupo))

    sumar(dict(PROFESOR, T_fuente=403.0, P_baja=563.64), "A*", "A_estrella")
    for parte in sorted({r["parte_estudio"] for r in ok if r["estudio"] == "5.1"}):
        g = [r for r in ok if r["estudio"] == "5.1" and r["parte_estudio"] == parte]
        r = max(g, key=lambda r: float(r["eta"]))
        sumar(_combo(r), f"opt_{parte}", "opt_5_1")
    for tf in (390.0, 410.0):
        for ec in (0.875, 0.95):
            g = sorted((r for r in ok if r["estudio"] == "4.2"
                        and abs(float(r["T_fuente"]) - tf) < 1e-6
                        and abs(float(r["eps_cond"]) - ec) < 1e-6),
                       key=lambda r: float(r["T_sumidero"]))
            for r in (g[:1] + g[-1:]):
                sumar(_combo(r), f"4.2_{tf:.0f}_{ec}_{r['T_sumidero'][:6]}",
                      "franja_4_2")
    g43 = [r for r in ok if r["estudio"] == "4.3"]
    if g43:
        rmax = max(r["ronda"] for r in g43)
        for i, r in enumerate(x for x in g43 if x["ronda"] == rmax):
            sumar(_combo(r), f"4.3_r{rmax}_{i}", "final_4_3")
    hus = sorted((r for r in ok if r["estudio"] == "6.2"),
                 key=lambda r: float(r["P_baja"]))
    if hus:
        elegidos = [hus[0], hus[len(hus) // 2], max(hus, key=lambda r: float(r["eta"]))]
        for i, r in enumerate(elegidos):
            sumar(_combo(r), f"husavik_{i}", "husavik")
    n_obl = len(pts)
    rng = random.Random(SEMILLA)
    base = [r for r in ok if r["estudio"] in ("3.2", "5.1")]
    celdas = {}
    for r in base:
        k = (_bin(float(r["eps_reg"])), _bin(float(r["eps_hrvg"])))
        if None not in k:
            celdas.setdefault(k, []).append(r)
    for k in sorted(celdas):
        g = celdas[k]
        for i, r in enumerate(rng.sample(g, min(POR_CELDA, len(g)))):
            sumar(_combo(r), f"est_{k[0]}{k[1]}_{i}", "estratificada")
    for var in ("eps_reg", "eps_hrvg"):
        for i, r in enumerate(sorted(base, key=lambda r: -float(r[var]))[:N_EXTREMOS]):
            sumar(_combo(r), f"ext_{var}_{i}", "extremos")
    with open(ELSAYED, encoding="utf-8", newline="") as fh:
        for i, r in enumerate(x for x in csv.DictReader(fh) if x["convergio"] == "True"):
            c = dict(T_fuente=float(r["T_fuente_K"]), T_sumidero=283.0,
                     P_alta=float(r["P_alta_kPa"]), P_baja=float(r["P_baja_kPa"]),
                     x_b=float(r["x_b"]), m_b=1.0, eta_t=0.80, eta_p=0.80,
                     eps_hrvg=float(r["eps_hrvg"]), eps_reg=float(r["eps_reg"]),
                     eps_cond=float(r["eps_cond"]))
            pts.append(_pt(c, f"elsayed_{i:02d}_{r['serie']}", "elsayed"))
    reales = [p for p in pts if p["grupo"] in ("A_estrella", "opt_5_1", "husavik")]
    ext = max((p for p in pts if p["grupo"] == "estratificada"),
              key=lambda p: p["eps_reg"], default=None)
    for p in (reales[:1] + reales[1:2] + reales[-1:] + ([ext] if ext else []))[:N_REAL]:
        pts.append(dict(p, tag=p["tag"] + "_real", grupo="real", motor="real"))
    return pts


def main() -> None:
    pts = seleccionar()
    cuenta = {}
    for p in pts:
        cuenta[p["grupo"]] = cuenta.get(p["grupo"], 0) + 1
    print(f"puntos: {len(pts)}", flush=True)
    for g, n in cuenta.items():
        print(f"  {g}: {n}", flush=True)


if __name__ == "__main__":
    main()
