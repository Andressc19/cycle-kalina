"""Sensibilidad 1, Fase C — muestreo LHS de 9 variables alrededor de 2 centros.

Con las fases A (OFAT) y B (mallas 2D) ya se conocen las ventanas univariadas y
por pares. Aquí se mueven NUEVE variables a la vez dentro de una caja alrededor
de cada centro, con un muestreo de hipercubo latino (`scipy.stats.qmc`): 250
puntos por centro (500 en total) para el rango conjunto con KALINA.

Variables muestreadas (9): T_fuente, T_sumidero, P_alta, P_baja, x_b, eta_t,
eps_hrvg, eps_reg, eps_cond. Fijos por centro: eta_p (C1=0.80, C2=0.75) y
m_b=1.0. `t_amb_diseno` de cada punto es su propio T_sumidero (piso de O2).
Motor `teqp`, `extra=True`; 5 procesos; escritura incremental con flush.

Tras escalar cada columna al rango de la tabla se REDONDEA: temperaturas a
0.5 K, presiones a 10 kPa, x_b a 0.01, eficiencias/efectividades al múltiplo de
0.05 más cercano; luego se eliminan duplicados exactos. Salida en
`resultados/2026-10-14_sens1_faseC/` (`faseC_filas.csv`, `faseC_log.txt`).
Se ejecuta como script, no como módulo.
"""
from __future__ import annotations

import csv
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from scipy.stats.qmc import LatinHypercube

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
_DIR_COMUN = _DIR.parents[0] / "barrido_final"
sys.path[:0] = [str(_RAIZ), str(_DIR_COMUN)]

from comun import COLS, COLS_EXTRA, evaluar_punto  # noqa: E402

OUT = _RAIZ / "resultados" / "2026-10-14_sens1_faseC"
N_WORKERS = 5
N_POR_CENTRO = 250
SEED = 20261014

VARIABLES = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b",
             "eta_t", "eps_hrvg", "eps_reg", "eps_cond")
CENTROS = (
    ("C1", dict(T_fuente=394.15, T_sumidero=278.15, P_alta=3300.0, P_baja=690.0,
                x_b=0.82, m_b=1.0, eta_t=0.85, eta_p=0.80, eps_hrvg=0.85,
                eps_reg=0.75, eps_cond=0.95)),
    ("C2", dict(T_fuente=403.0, T_sumidero=300.15, P_alta=3000.0,
                P_baja=563.64, x_b=0.50, m_b=1.0, eta_t=0.85, eta_p=0.75,
                eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.95)))
# Caja de muestreo [lo, hi] por centro, en el orden de VARIABLES.
RANGOS = {
    "C1": [(363.15, 443.15), (278.15, 288.15), (2000.0, 5000.0),
           (500.0, 1300.0), (0.55, 0.95), (0.50, 0.95),
           (0.50, 0.95), (0.50, 0.95), (0.80, 0.95)],
    "C2": [(393.15, 463.15), (278.15, 303.15), (2000.0, 4000.0),
           (400.0, 1200.0), (0.40, 0.65), (0.50, 0.95),
           (0.50, 0.95), (0.50, 0.95), (0.70, 0.95)],
}
CM = list(COLS) + list(COLS_EXTRA) + ["id_punto", "centro", "tipo"]


def redondear(var: str, v: float) -> float:
    """Redondeo de la especificación por tipo de variable."""
    if var in ("T_fuente", "T_sumidero"):
        return round(round(v / 0.5) * 0.5, 2)
    if var in ("P_alta", "P_baja"):
        return round(round(v / 10.0) * 10.0, 1)
    if var == "x_b":
        return round(round(v / 0.01) * 0.01, 2)
    return round(round(v / 0.05) * 0.05, 2)


def muestrear(centro: str) -> tuple:
    """(puntos únicos tras redondear, n_descartados) del LHS de `centro`."""
    rangos = RANGOS[centro]
    u = LatinHypercube(d=len(VARIABLES), seed=SEED).random(N_POR_CENTRO)
    vistos, out = set(), []
    for fila in u:
        combo = {}
        for k, var in enumerate(VARIABLES):
            lo, hi = rangos[k]
            combo[var] = redondear(var, lo + float(fila[k]) * (hi - lo))
        clave = tuple(combo[v] for v in VARIABLES)
        if clave in vistos:
            continue
        vistos.add(clave)
        out.append(combo)
    return out, N_POR_CENTRO - len(out)


def tareas() -> list:
    """Los 2x250 puntos LHS con su etiqueta `id_punto`, `centro` y `tipo`."""
    out = []
    for centro, base in CENTROS:
        pts, _ = muestrear(centro)
        for i, combo in enumerate(pts, 1):
            full = dict(base)
            full.update(combo)
            out.append(dict(id_punto=f"{centro}-LHS-{i:04d}", centro=centro,
                            tipo="lhs", combo=full))
    return out


def _eval(t: dict) -> dict:
    """UNA corrida; corre en un hijo del pool (patrón de faseB_corrida.py)."""
    f = evaluar_punto(t["combo"], motor="teqp", tag=t["id_punto"],
                      t_amb_diseno=t["combo"]["T_sumidero"], extra=True)
    f.update(id_punto=t["id_punto"], centro=t["centro"], tipo="lhs")
    return f


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ts = tareas()
    total = len(ts)
    for centro, _ in CENTROS:
        _, desc = muestrear(centro)
        if desc:
            print(f"AVISO {centro}: {desc} puntos descartados por redondeo "
                  f"({N_POR_CENTRO - desc}/{N_POR_CENTRO} unicos)", flush=True)
    por_c = {c: sum(1 for t in ts if t["centro"] == c) for c, _ in CENTROS}
    print(f"Fase C sensibilidad 1 | {total} puntos {por_c} | {N_WORKERS} "
          f"workers -> {OUT}", flush=True)
    t0, n = time.perf_counter(), 0
    with open(OUT / "faseC_filas.csv", "w", encoding="utf-8",
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
