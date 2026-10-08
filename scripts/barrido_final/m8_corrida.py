"""M8 (ANECDÓTICO) — OAT de eficiencias y efectividades de 0.20 a 0.99.

Cinco variables (eta_t, eta_p, eps_hrvg, eps_reg, eps_cond) sobre dos bases —
B1 = ancla A* `dict(PROFESOR, T_fuente=403.0, P_baja=563.6363636363637)` con
piso de O2 = 300.032917; B2 = óptimo sin restricciones de M7 (arranque A1 de
`resultados/2026-10-07_final_M7/m7_optimos.csv`, piso de O2 = su T_sumidero) —
con los 16 valores de `VALORES` y el resto de las variables en la base:
2 x 5 x 16 = 160 corridas con `ProcessPoolExecutor(max_workers=7)` y SOLO
motor teqp. Cada fila se marca `realista = (0.40 <= valor <= 0.95)`.

VALORES FUERA DE [0.40, 0.95] NO SON REALISTAS para este proyecto: esta
campaña es ANECDÓTICA (curiosidad), no son recomendaciones ni resultados de
diseño. Con `M8_HUMO=1`: 3 puntos (B1, eta_t en 0.20/0.60/0.99) y la salida
va a `.../2026-10-07_final_M8_anecdotico/humo/`.
"""
from __future__ import annotations

import csv, os, sys, time  # noqa: E401,E402
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

from comun import COLS, PROFESOR, evaluar_punto  # noqa: E402

HUMO = os.environ.get("M8_HUMO") == "1"
OUT = _RAIZ / "resultados" / ("2026-10-07_final_M8_anecdotico/humo" if HUMO
                              else "2026-10-07_final_M8_anecdotico")
N_WORKERS = 7
VARIABLES = ("eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")
VALORES = (0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.60, 0.70, 0.80, 0.85,
           0.90, 0.93, 0.95, 0.97, 0.98, 0.99)
HUMO_VAL = (0.20, 0.60, 0.99)
PISO_B1 = 300.032917
M7 = "2026-10-07_final_M7"
CM8 = ["base", "variable", "valor", "realista"] + list(COLS)


def bases() -> dict:
    """B1 = ancla A*; B2 = óptimo A1 de M7 (piso de O2 = su T_sumidero)."""
    b1 = dict(PROFESOR, T_fuente=403.0, P_baja=563.6363636363637)
    with open(_RAIZ / "resultados" / M7 / "m7_optimos.csv", encoding="utf-8",
              newline="") as fh:
        a1 = next(r for r in csv.DictReader(fh) if r["arranque"] == "A1")
    b2 = {v: float(a1[v]) for v in ("T_fuente", "T_sumidero", "P_alta",
                                    "P_baja", "x_b", *VARIABLES)}
    b2["m_b"] = 1.0                       # m7_optimizar: c0 con m_b = 1.0
    return {"B1": dict(combo=b1, piso=PISO_B1),
            "B2": dict(combo=b2, piso=float(a1["T_sumidero"]))}


def tareas() -> list:
    """El OAT completo; en humo solo B1 x eta_t x 3 valores (3 puntos)."""
    out = []
    items = list(bases().items())[:1] if HUMO else list(bases().items())
    for bn, b in items:
        for v in (VARIABLES[:1] if HUMO else VARIABLES):
            for x in (HUMO_VAL if HUMO else VALORES):
                out.append(dict(base=bn, variable=v, valor=float(x),
                                piso=b["piso"],
                                combo=dict(b["combo"], **{v: float(x)})))
    return out


def _eval(t: dict) -> dict:
    """UNA corrida; corre en un hijo del pool (patrón de m3_ofat.py)."""
    f = evaluar_punto(t["combo"], motor="teqp",
                      tag=f'{t["base"]}:{t["variable"]}={t["valor"]:g}',
                      t_amb_diseno=t["piso"])
    f.update(base=t["base"], variable=t["variable"], valor=t["valor"],
             realista=0.40 <= t["valor"] <= 0.95)
    return f


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ts = tareas()
    total = len(ts)
    print(f"M8 ANECDÓTICO (no realista) | humo={HUMO} | {total} corridas | "
          f"{N_WORKERS} workers | solo teqp -> {OUT}", flush=True)
    t0, n = time.perf_counter(), 0
    with open(OUT / "m8_oat.csv", "w", encoding="utf-8", newline="") as fh:
        esc = csv.DictWriter(fh, fieldnames=CM8)
        esc.writeheader()
        fh.flush()
        with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
            futs = [ex.submit(_eval, t) for t in ts]
            for fu in as_completed(futs):
                f = fu.result()
                esc.writerow({c: f.get(c) for c in CM8})
                fh.flush()
                n += 1
                print(f'[{n}/{total}] {f["base"]} {f["variable"]}='
                      f'{f["valor"]:g} {f["clasificacion"]} eta={f["eta"]} '
                      f'{f["t_s"]:.1f}s', flush=True)
    print(f"fin: {total} corridas en {time.perf_counter() - t0:.0f} s -> {OUT}",
          flush=True)


if __name__ == "__main__":
    main()
