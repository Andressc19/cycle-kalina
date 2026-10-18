"""Sensibilidad 1, Ronda 2 — puntos de los barridos N2, N5 y N6.

Genera las tres mallas de la ronda 2 y deja los puntos planeados en
`ronda2_diseno.csv` (para verificar el conteo) y el resumen de descartes del
LHS de N2 en `ronda2_descartes.csv`:

- N2: LHS(d=5, seed=20261016) de 150 puntos sobre T_fuente, P_alta, P_baja,
  x_b, T_sumidero (resto nominal, eta_p=0.80). Se descartan (sin resamplear)
  los puntos con `P_alta < 1.3 * P_baja`.
- N5: malla completa 6x6x10 (T_fuente C, T_sumidero C, P_baja kPa) = 360 puntos.
- N6: por centro (C1, C2) malla 3x3x3 (eta_t, eps_hrvg, eps_reg) = 54 puntos.

Elimina duplicados por combinacion dentro de cada barrido. Se ejecuta como
modulo (lo importa `ronda2_corrida.py`) y como script (escribe el diseno).
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

from scipy.stats.qmc import LatinHypercube

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
OUT = _RAIZ / "resultados" / "2026-10-15_sens1_ronda2"

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

N2_N = 150
N2_SEED = 20261016
N2_VARS = ("T_fuente", "P_alta", "P_baja", "x_b", "T_sumidero")
N2_RANGOS = ((343.15, 403.15),   # 70-130 C
             (800.0, 3000.0),
             (100.0, 900.0),
             (0.30, 0.80),
             (278.15, 303.15))

N5_TF_C = (90, 110, 130, 150, 170, 200)      # se suma 273.15
N5_TS_C = (5, 10, 15, 20, 25, 30)            # se suma 273.15
N5_PBAJA = (300.0, 400.0, 500.0, 600.0, 700.0, 800.0, 900.0, 1000.0,
            1250.0, 1500.0)

N6_EFECTOS = (0.40, 0.55, 0.70)              # eta_t x eps_hrvg x eps_reg

BARRIDOS = ("N2", "N5", "N6")
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
        if cl not in vistos:
            vistos.add(cl)
            out.append(it)
    return out


def n2_puntos() -> tuple:
    """(tareas N2, descartes). LHS d=5; descarta P_alta < 1.3*P_baja."""
    u = LatinHypercube(d=5, seed=N2_SEED).random(N2_N)
    cand, nd = [], 0
    for fila in u:
        vals = [redondear(v, lo + float(fila[k]) * (hi - lo))
                for k, (v, (lo, hi)) in enumerate(zip(N2_VARS, N2_RANGOS))]
        tf, pa, pb, xb, ts = vals
        if pa < 1.3 * pb:
            nd += 1
            continue
        cand.append(dict(T_fuente=tf, P_alta=pa, P_baja=pb, x_b=xb,
                         T_sumidero=ts))
    vistos, uniq = set(), []
    for vals in cand:
        cl = tuple(vals[v] for v in N2_VARS)
        if cl not in vistos:
            vistos.add(cl)
            uniq.append(vals)
    tareas = [dict(id_punto=f"N2-{nn:03d}", barrido="N2", centro="NA",
                   combo=combo_base(**vals))
              for nn, vals in enumerate(uniq, 1)]
    desc = dict(barrido="N2", nivel="todos", n_lhs=N2_N, n_descartados=nd,
                n_duplicados=len(cand) - len(uniq), n_final=len(uniq))
    return tareas, [desc]


def n5_puntos() -> list:
    """Malla 6x6x10 = 360 puntos. id_punto N5-T{°C:03d}-S{°C:02d}-{nn:02d}."""
    tareas = []
    for tf_c in N5_TF_C:
        for ts_c in N5_TS_C:
            for nn, pb in enumerate(N5_PBAJA, 1):
                combo = combo_base(T_fuente=tf_c + 273.15,
                                   T_sumidero=ts_c + 273.15, P_baja=pb,
                                   P_alta=3000.0, x_b=0.70, eta_p=0.80)
                tareas.append(dict(
                    id_punto=f"N5-T{tf_c:03d}-S{ts_c:02d}-{nn:02d}",
                    barrido="N5", centro="NA", combo=combo))
    return _dedup(tareas)


def n6_puntos() -> list:
    """2 centros x 3x3x3 = 54. id_punto N6-{centro}-{nn:02d} (nn global)."""
    tareas, seq = [], 0
    for centro in ("C1", "C2"):
        base = dict(CENTROS[centro])
        base["eps_cond"] = 0.95
        for et in N6_EFECTOS:
            for eh in N6_EFECTOS:
                for er in N6_EFECTOS:
                    seq += 1
                    tareas.append(dict(
                        id_punto=f"N6-{centro}-{seq:02d}", barrido="N6",
                        centro=centro,
                        combo=combo_base(**base, eta_t=et, eps_hrvg=eh,
                                         eps_reg=er)))
    return _dedup(tareas)


def tareas(barrido: str) -> list:
    """Lista de tareas para el barrido solicitado (o vacio)."""
    return {"N2": lambda: n2_puntos()[0], "N5": n5_puntos,
            "N6": n6_puntos}.get(barrido, lambda: [])()


def diseno_completo() -> tuple:
    """Todo el diseño y todos los descartes (N2)."""
    t2, d2 = n2_puntos()
    return t2 + n5_puntos() + n6_puntos(), d2


def _escribir_diseno(dirs: Path) -> tuple:
    dirs.mkdir(parents=True, exist_ok=True)
    todos, d2 = diseno_completo()
    with open(dirs / "ronda2_diseno.csv", "w", encoding="utf-8",
              newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS_DISENO)
        w.writeheader()
        for t in todos:
            w.writerow({**{k: t[k] for k in ("id_punto", "barrido",
                                             "centro")}, **t["combo"]})
    with open(dirs / "ronda2_descartes.csv", "w", encoding="utf-8",
              newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS_DESC)
        w.writeheader()
        w.writerows(d2)
    print(f"diseno escrito: {dirs / 'ronda2_diseno.csv'} ({len(todos)}) | "
          f"{dirs / 'ronda2_descartes.csv'} ({len(d2)})", flush=True)
    return todos, d2


if __name__ == "__main__":
    _escribir_diseno(OUT)
