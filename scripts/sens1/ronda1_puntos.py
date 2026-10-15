"""Sensibilidad 1, Ronda 1 — puntos de los barridos N1, N3 y N4.

Genera las tres mallas de la ronda 1 y deja los puntos planeados en
`ronda1_diseno.csv` (para verificar el conteo) y el resumen de descartes del
LHS de N1 en `ronda1_descartes.csv`:

- N1: 13 niveles de T_fuente (70..300 C; +273.15 a K), 30 puntos LHS(d=4) por
  nivel (`seed=20261015+i`) sobre P_alta/P_baja/x_b/T_sumidero; se descartan
  (sin resamplear) los de `P_alta < 1.3 * P_baja`.
- N4: malla 7x7 de P_alta x x_b en los centros C1 y C2 (98 puntos).
- N3: malla 8x8x3 de eps_cond x P_baja x T_sumidero en C1 (192 puntos).

Elimina duplicados por combinacion dentro de cada barrido. Se ejecuta como
modulo (lo importa `ronda1_corrida.py`) y como script (escribe el diseno).
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

from scipy.stats.qmc import LatinHypercube

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
OUT = _RAIZ / "resultados" / "2026-10-14_sens1_ronda1"

VARIABLES = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "m_b",
             "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")
NOMINAL = dict(eta_t=0.85, eta_p=0.80, eps_hrvg=0.85, eps_reg=0.75,
               eps_cond=0.95, m_b=1.0)
CENTROS = {
    "C1": dict(T_fuente=394.15, T_sumidero=278.15, P_alta=3300.0,
               P_baja=690.0, x_b=0.82, eta_p=0.80),
    "C2": dict(T_fuente=403.0, T_sumidero=300.15, P_alta=3000.0,
               P_baja=563.64, x_b=0.50, eta_p=0.75),
}
N1_TC = (70, 90, 110, 130, 150, 170, 190, 210, 230, 250, 270, 290, 300)
N1_N, N1_SEED0 = 30, 20261015
N1_VARS = ("P_alta", "P_baja", "x_b", "T_sumidero")
N1_RANGOS = ((1000.0, 5000.0), (150.0, 2000.0), (0.30, 0.95),
             (278.15, 303.15))
N4_PALTA = (1000.0, 1250.0, 1500.0, 1750.0, 2000.0, 2500.0, 3000.0)
N4_XB = (0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.95)
N3_EPS = (0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95)
N3_PBAJA = (400.0, 500.0, 600.0, 700.0, 800.0, 1000.0, 1250.0, 1500.0)
N3_TSUM = (283.15, 293.15, 303.15)
N3_BASE = dict(T_fuente=394.15, P_alta=3300.0, x_b=0.82, eta_t=0.85,
               eta_p=0.80, eps_hrvg=0.85, eps_reg=0.75, m_b=1.0)
BARRIDOS = ("N1", "N4", "N3")
COLS_DISENO = ["id_punto", "barrido", "centro"] + list(VARIABLES)
COLS_DESC = ["barrido", "nivel", "n_lhs", "n_descartados", "n_duplicados",
             "n_final"]


def redondear(var: str, v: float) -> float:
    """Redondeo por tipo de variable (0.5 K, 10 kPa, 0.01, 0.05)."""
    if var in ("T_fuente", "T_sumidero"):
        return round(round(v / 0.5) * 0.5, 2)
    if var in ("P_alta", "P_baja"):
        return round(round(v / 10.0) * 10.0, 1)
    if var == "x_b":
        return round(round(v / 0.01) * 0.01, 2)
    return round(round(v / 0.05) * 0.05, 2)


def combo_base(**over) -> dict:
    """Configuracion nominal con las variables de `over` por encima."""
    c = dict(NOMINAL)
    c.update(over)
    return c


def _clave(combo: dict) -> tuple:
    return tuple(combo[v] for v in VARIABLES)


def _dedup(items: list) -> list:
    """Primer item de cada combinacion unica (dentro de un barrido)."""
    vistos, out = set(), []
    for it in items:
        cl = _clave(it["combo"])
        if cl in vistos:
            continue
        vistos.add(cl)
        out.append(it)
    return out


def n1_puntos() -> tuple:
    """(tareas N1, descartes por nivel). LHS de 4 variables por nivel."""
    tareas, descartes = [], []
    for i, tc in enumerate(N1_TC):
        u = LatinHypercube(d=4, seed=N1_SEED0 + i).random(N1_N)
        cand, nd = [], 0
        for fila in u:
            vals = [redondear(v, lo + float(fila[k]) * (hi - lo))
                    for k, (v, (lo, hi)) in enumerate(zip(N1_VARS, N1_RANGOS))]
            pa, pb, xb, ts = vals
            if pa < 1.3 * pb:
                nd += 1
                continue
            cand.append(dict(T_fuente=tc + 273.15, P_alta=pa, P_baja=pb,
                             x_b=xb, T_sumidero=ts))
        vistos, uniq = set(), []
        for vals in cand:
            cl = tuple(vals[v] for v in N1_VARS)
            if cl not in vistos:
                vistos.add(cl)
                uniq.append(vals)
        for nn, vals in enumerate(uniq, 1):
            tareas.append(dict(id_punto=f"N1-T{tc:03d}-{nn:02d}", barrido="N1",
                               centro="NA", combo=combo_base(**vals)))
        descartes.append(dict(barrido="N1", nivel=tc, n_lhs=N1_N,
                              n_descartados=nd,
                              n_duplicados=len(cand) - len(uniq),
                              n_final=len(uniq)))
    return tareas, descartes


def n4_puntos() -> list:
    """Malla 7x7 de P_alta x x_b en C1 y C2 (resto al valor del centro)."""
    out = []
    for centro, base in CENTROS.items():
        pts = [dict(combo=combo_base(**{**base, "P_alta": pa, "x_b": xb}),
                    centro=centro)
               for pa in N4_PALTA for xb in N4_XB]
        pts = _dedup(pts)
        for i, it in enumerate(pts, 1):
            out.append(dict(id_punto=f"N4-{centro}-{i:04d}", barrido="N4",
                            centro=centro, combo=it["combo"]))
    return out


def n3_puntos() -> list:
    """Malla 8 (eps_cond) x 8 (P_baja) x 3 (T_sumidero) en C1."""
    pts = []
    for ts in N3_TSUM:
        for eps in N3_EPS:
            for pb in N3_PBAJA:
                combo = combo_base(**dict(N3_BASE, T_sumidero=ts,
                                          eps_cond=eps, P_baja=pb))
                pts.append(dict(combo=combo, centro="C1"))
    pts = _dedup(pts)
    return [dict(id_punto=f"N3-{i:04d}", barrido="N3", centro="C1",
                 combo=it["combo"]) for i, it in enumerate(pts, 1)]


def tareas(barrido: str = "all") -> list:
    """Puntos del barrido pedido (`N1`, `N3`, `N4` o `all`)."""
    if barrido == "N1":
        return n1_puntos()[0]
    if barrido == "N4":
        return n4_puntos()
    if barrido == "N3":
        return n3_puntos()
    if barrido == "all":
        return n1_puntos()[0] + n4_puntos() + n3_puntos()
    raise ValueError(f"barrido desconocido: {barrido}")


def _escribir(path, cols: list, filas: list) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for f in filas:
            w.writerow(f)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    todos = tareas("all")
    _, desc = n1_puntos()
    _escribir(OUT / "ronda1_diseno.csv", COLS_DISENO,
              [dict(id_punto=t["id_punto"], barrido=t["barrido"],
                    centro=t["centro"], **t["combo"]) for t in todos])
    _escribir(OUT / "ronda1_descartes.csv", COLS_DESC, desc)
    por = {b: sum(1 for t in todos if t["barrido"] == b) for b in BARRIDOS}
    print(f"diseno: {len(todos)} puntos {por}", flush=True)
    print("N1 descartados por P_alta<1.3*P_baja: "
          f"{sum(d['n_descartados'] for d in desc)}; por nivel: "
          + ", ".join(f"T{d['nivel']:03d}={d['n_descartados']}" for d in desc),
          flush=True)
    print("N1 duplicados por redondeo: "
          f"{sum(d['n_duplicados'] for d in desc)}", flush=True)


if __name__ == "__main__":
    main()
