"""M3 — sensibilidad local OAT alrededor del ancla A* (TASK_CONTEXT final_M3).

Ancla A* = `dict(PROFESOR, T_fuente=403.0, P_baja=563.6363636363637)`. Para cada
una de las 10 variables se corren los 15 valores de malla
`v_j = a + (j-1)(b-a)/14` (j = 1..15) y los dos vecinos `A* ± h` con
`h = 0.01*(b-a)`, dejando las otras nueve variables en A*. Total
1 + 10 x 17 = 171 corridas con `ProcessPoolExecutor(max_workers=5)` y
`motor="teqp"`. Cada fila se escribe con flush en `m3_ofat.csv` y se imprime
`[n/total] var=valor clase t_s`. Con `M3_HUMO=1`: A* + 1 variable x 3 valores
(4 corridas) y la salida va a `.../2026-10-06_final_M3/humo/`.
"""
from __future__ import annotations

import csv, os, sys, time  # noqa: E401,E402
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

from comun import COLS, PROFESOR, evaluar_punto  # noqa: E402

HUMO = os.environ.get("M3_HUMO") == "1"
OUT = _RAIZ / "resultados" / ("2026-10-06_final_M3/humo" if HUMO else "2026-10-06_final_M3")
N_WORKERS = 5
N_MALLA = 15
ANCHOR = dict(PROFESOR, T_fuente=403.0, P_baja=563.6363636363637)
# (variable, a, b) — rangos fijados por el director, actualizados 2026-10-06.
RANGOS = (("T_fuente", 340.0, 623.15), ("T_sumidero", 283.15, 303.55),
          ("P_alta", 1000.0, 10000.0), ("P_baja", 150.0, 1500.0),
          ("x_b", 0.30, 0.90), ("eta_t", 0.40, 0.95), ("eta_p", 0.40, 0.95),
          ("eps_hrvg", 0.40, 0.95), ("eps_reg", 0.40, 0.95),
          ("eps_cond", 0.40, 0.95))
CM3 = ["tipo_punto", "variable", "valor"] + list(COLS)


def malla(a: float, b: float) -> list:
    """Los 15 valores `v_j = a + (j-1)(b-a)/14`, j = 1..15."""
    return [a + j * (b - a) / (N_MALLA - 1) for j in range(N_MALLA)]


def tareas() -> list:
    """El ancla + (15 de malla + 2 vecinos) por variable; en humo, 1 x 3."""
    ts = [dict(tipo_punto="ancla", variable="", valor=None, combo=dict(ANCHOR))]
    for nom, a, b in (RANGOS[:1] if HUMO else RANGOS):
        vals = [a, (a + b) / 2, b] if HUMO else malla(a, b)
        for v in vals:
            ts.append(dict(tipo_punto="malla", variable=nom, valor=float(v),
                           combo=dict(ANCHOR, **{nom: float(v)})))
        if not HUMO:
            h = 0.01 * (b - a)
            for v in (ANCHOR[nom] - h, ANCHOR[nom] + h):
                ts.append(dict(tipo_punto="vecino", variable=nom, valor=v,
                               combo=dict(ANCHOR, **{nom: v})))
    return ts


def _tag(t: dict) -> str:
    if t["tipo_punto"] == "ancla":
        return "ancla"
    return f'{t["tipo_punto"]}:{t["variable"]}={t["valor"]:g}'


def _eval(t: dict) -> dict:
    """UNA corrida; corre en un hijo del pool (patrón de m2_nivel2.py)."""
    f = evaluar_punto(t["combo"], motor="teqp", tag=_tag(t))
    f.update({k: t[k] for k in ("tipo_punto", "variable", "valor")})
    return f


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ts = tareas()
    total = len(ts)
    print(f"M3 OAT | humo={HUMO} | {total} corridas | {N_WORKERS} workers -> {OUT}",
          flush=True)
    t0, n = time.perf_counter(), 0
    with open(OUT / "m3_ofat.csv", "w", encoding="utf-8", newline="") as fh:
        esc = csv.DictWriter(fh, fieldnames=CM3)
        esc.writeheader()
        fh.flush()
        with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
            futs = [ex.submit(_eval, t) for t in ts]
            for fu in as_completed(futs):
                f = fu.result()
                esc.writerow({c: f.get(c) for c in CM3})
                fh.flush()
                n += 1
                lbl = ("ancla" if f["tipo_punto"] == "ancla"
                       else f'{f["variable"]}={f["valor"]:g}')
                print(f'[{n}/{total}] {lbl} {f["clasificacion"]} '
                      f'{f["t_s"]:.1f}s', flush=True)
    print(f"fin: {total} corridas en {time.perf_counter() - t0:.0f} s -> {OUT}",
          flush=True)


if __name__ == "__main__":
    main()
