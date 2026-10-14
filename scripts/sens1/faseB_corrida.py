"""Sensibilidad 1, Fase B — mallas 2D (barridos de DOS variables) alrededor de
los 2 centros de la Fase A.

Seis pares de variables (B1..B6) por centro; cada par es una malla 7x7 con el
resto de variables fijas en el valor del centro. El `t_amb_diseno` de cada punto
es su propio `T_sumidero` (piso de O2). `m_b=1.0` fijo. Motor `teqp`,
`extra=True`; 5 procesos; escritura incremental con flush. Las combinaciones
repetidas (el punto base aparece en las seis mallas, y también las líneas
coordenadas donde una variable queda en el centro) se eliminan por (centro,
combinación): se evalúan UNA vez y el punto base queda con `par="base"` y
`var1=var2="base"`. Salida en `resultados/2026-10-14_sens1_faseB/`
(`faseB_filas.csv`, `faseB_log.txt`). Se ejecuta como script, no como módulo.

Este módulo también expone `CENTROS`, `PARES`, `PARES_D`, `VARIABLES`,
`valores_brutos` y `valores` para que el reporte reconstruya las mallas.
"""
from __future__ import annotations

import csv
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
_DIR_COMUN = _DIR.parents[0] / "barrido_final"
sys.path[:0] = [str(_RAIZ), str(_DIR_COMUN)]

from comun import COLS, COLS_EXTRA, evaluar_punto  # noqa: E402

OUT = _RAIZ / "resultados" / "2026-10-14_sens1_faseB"
N_WORKERS = 5

VARIABLES = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b",
             "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")
CENTROS = (
    ("C1", dict(T_fuente=394.15, T_sumidero=278.15, P_alta=3300.0, P_baja=690.0,
                x_b=0.82, m_b=1.0, eta_t=0.85, eta_p=0.80, eps_hrvg=0.85,
                eps_reg=0.75, eps_cond=0.95)),
    ("C2", dict(T_fuente=403.0, T_sumidero=300.15, P_alta=3000.0,
                P_baja=563.64, x_b=0.50, m_b=1.0, eta_t=0.85, eta_p=0.75,
                eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.95)))
CENTROS_D = dict(CENTROS)
PARES = (
    ("B1", "T_fuente", "P_baja"), ("B2", "P_baja", "x_b"),
    ("B3", "P_alta", "P_baja"), ("B4", "eps_cond", "T_sumidero"),
    ("B5", "eps_reg", "eta_t"), ("B6", "eps_hrvg", "T_fuente"))
PARES_D = {p: (a, b) for p, a, b in PARES}

# Rejillas 7x7 en unidades de la especificación (T_fuente en °C).
GRID = {
    "T_fuente": {"C1": [90, 100, 110, 121, 135, 150, 165],
                 "C2": [110, 120, 129.85, 140, 155, 170, 190]},
    "T_sumidero": {"C1": [278.15, 280.65, 283.15, 285.65, 288.15, 293.15,
                          298.15],
                   "C2": [278.15, 285.15, 290.15, 295.15, 300.15, 302.15,
                          303.15]},
    "P_alta": {"C1": [2000, 2500, 3000, 3300, 3800, 4400, 5000],
               "C2": [2000, 2500, 3000, 3250, 3500, 3750, 4000]},
    "P_baja": {"C1": [500, 600, 690, 800, 950, 1100, 1300],
               "C2": [400, 450, 500, 563.64, 700, 900, 1200]},
    "x_b": {"C1": [0.55, 0.60, 0.70, 0.75, 0.82, 0.90, 0.95],
            "C2": [0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70]},
    "eps_cond": {"C1": [0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95],
                 "C2": [0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]},
    "eta_t": {"C1": [0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95],
              "C2": [0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95]},
    "eps_hrvg": {"C1": [0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95],
                 "C2": [0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95]},
    "eps_reg": {"C1": [0.50, 0.60, 0.70, 0.75, 0.80, 0.90, 0.95],
                "C2": [0.50, 0.60, 0.70, 0.75, 0.80, 0.90, 0.95]},
}
CM = (["id_punto", "centro", "par", "var1", "val1", "var2", "val2"]
      + list(COLS) + list(COLS_EXTRA))


def valores_brutos(var: str, centro: str) -> list:
    """Valores de la rejilla en las unidades de la especificación (°C si T_fuente)."""
    return list(GRID[var][centro])


def valores(var: str, centro: str) -> list:
    """Valores de la rejilla en unidades de diseño (K si T_fuente)."""
    if var == "T_fuente":
        return [round(c + 273.15, 2) for c in GRID[var][centro]]
    return list(GRID[var][centro])


def _clave(combo: dict) -> tuple:
    return tuple(round(combo[k], 6) for k in VARIABLES)


def tareas() -> list:
    """El punto base + las seis mallas de cada centro, sin repetidos."""
    out = []
    for centro, base in CENTROS:
        vistos, idx = set(), [0]

        def add(par, var1, v1, var2, v2, combo):
            k = _clave(combo)
            if k in vistos:            # base y líneas-coordenada compartidas
                return
            vistos.add(k)
            out.append(dict(id_punto=f"{centro}-{par}-{idx[0]:04d}",
                            centro=centro, par=par, var1=var1, val1=v1,
                            var2=var2, val2=v2, combo=dict(combo)))
            idx[0] += 1

        add("base", "base", None, "base", None, base)
        for par, a, b in PARES:
            for va in valores(a, centro):
                for vb in valores(b, centro):
                    add(par, a, va, b, vb, dict(base, **{a: float(va),
                                                         b: float(vb)}))
    return out


def _eval(t: dict) -> dict:
    """UNA corrida; corre en un hijo del pool (patrón de faseA_corrida.py)."""
    f = evaluar_punto(t["combo"], motor="teqp", tag=t["id_punto"],
                      t_amb_diseno=t["combo"]["T_sumidero"], extra=True)
    f.update({k: t[k] for k in ("id_punto", "centro", "par", "var1", "val1",
                                "var2", "val2")})
    return f


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ts = tareas()
    total = len(ts)
    por_c = {c: sum(1 for t in ts if t["centro"] == c) for c, _ in CENTROS}
    print(f"Fase B sensibilidad 1 | {total} puntos {por_c} | {N_WORKERS} "
          f"workers -> {OUT}", flush=True)
    t0, n = time.perf_counter(), 0
    with open(OUT / "faseB_filas.csv", "w", encoding="utf-8",
              newline="") as fh:
        esc = csv.DictWriter(fh, fieldnames=CM)
        esc.writeheader()
        fh.flush()
        with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
            futs = [ex.submit(_eval, t) for t in ts]
            for fu in as_completed(futs):
                f = fu.result()
                esc.writerow({c: f.get(c) for c in CM})
                fh.flush()
                n += 1
                print(f'[{n}/{total}] {f["id_punto"]} {f["clasificacion"]} '
                      f'{f["t_s"]:.1f}s', flush=True)
    print(f"fin: {total} puntos en {time.perf_counter() - t0:.0f} s -> {OUT}",
          flush=True)


if __name__ == "__main__":
    main()
