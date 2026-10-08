"""M6 — Parte A (teqp vs motor real) y B1 (piso 303.55 K) en UNA corrida.

`TASK_CONTEXT_final_M6.md` §Parte A y §B1. Los 12 puntos se evalúan dos veces
(`motor="teqp"` y `motor="real"`) con su piso de O2 de la Parte A, y una vez
más con `motor="teqp"` y `t_amb_diseno=303.55` (B1). Todo al mismo
`ProcessPoolExecutor(max_workers=7)` vía `comun.evaluar_punto`.

Salida: `resultados/2026-10-08_final_M6/m6_verificacion.csv` (24 filas,
una por punto y motor, columnas `comun.COLS` más `id` y `origen`) y
`m6_piso_30_4C.csv` (12 filas de B1). Con `M6_HUMO=1`: los primeros 2 puntos
(P01 y P02) con los dos motores más B1, y la salida va a `humo/`.
"""
from __future__ import annotations

import csv
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

from comun import COLS, evaluar_punto  # noqa: E402
from m6_puntos import AVISOS, PISO_B1, puntos  # noqa: E402

N_WORKERS = 7
HUMO = os.environ.get("M6_HUMO") == "1"
OUT = _RAIZ / "resultados" / ("2026-10-08_final_M6" + ("/humo" if HUMO else ""))
CM6 = ["id", "origen"] + list(COLS)
MOTORES = ("teqp", "real")
CSV_A, CSV_B1 = "m6_verificacion.csv", "m6_piso_30_4C.csv"


def tareas() -> list:
    """Las evaluaciones de la Parte A (2 por punto) y de B1 (1 por punto)."""
    pts = puntos()[:2] if HUMO else puntos()
    t = [dict(parte="A", id=p["id"], origen=p["origen"], combo=p["combo"],
              piso=p["piso"], motor=m) for p in pts for m in MOTORES]
    t += [dict(parte="B1", id=p["id"], origen=p["origen"], combo=p["combo"],
               piso=PISO_B1, motor="teqp") for p in pts]
    return t


def _eval(t: dict) -> dict:
    """UNA evaluación; corre en un hijo del pool (patrón de `m5c_m4c_corrida`)."""
    f = evaluar_punto(t["combo"], motor=t["motor"],
                      tag=f'm6:{t["parte"]}:{t["id"]}', t_amb_diseno=t["piso"])
    f.update(id=t["id"], origen=t["origen"], parte=t["parte"])
    return f


def main() -> None:
    for a in AVISOS:
        print("AVISO:", a, flush=True)
    ts = tareas()
    if not ts:
        raise SystemExit("sin tareas: revise los AVISOS de m6_puntos")
    OUT.mkdir(parents=True, exist_ok=True)
    rutas = {"A": OUT / CSV_A, "B1": OUT / CSV_B1}
    print(f"M6 A+B1 | {len(ts)} evaluaciones ({len(ts) // 3} puntos) | "
          f"{N_WORKERS} workers | {OUT}", flush=True)
    t0, n = time.perf_counter(), 0
    abiertos = {k: open(p, "w", encoding="utf-8", newline="")
                for k, p in rutas.items()}
    try:
        esc = {}
        for k, fh in abiertos.items():
            w = csv.DictWriter(fh, fieldnames=CM6)
            w.writeheader()
            fh.flush()
            esc[k] = (w, fh)
        with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
            futs = [ex.submit(_eval, t) for t in ts]
            for fu in as_completed(futs):
                fila = fu.result()
                w, fh = esc[fila["parte"]]
                w.writerow({c: fila.get(c) for c in CM6})
                fh.flush()
                n += 1
                clase = fila.get("clasificacion") or fila.get(
                    "error_inesperado") or "sin_clase"
                print(f'[{n}/{len(ts)}] {fila["parte"]} {fila["id"]} '
                      f'{fila["motor"]} {clase} {fila["t_s"]:.1f}s', flush=True)
    finally:
        for fh in abiertos.values():
            fh.close()
    print(f"fin: {n} corridas en {time.perf_counter() - t0:.0f} s", flush=True)
    print(f"salidas: {rutas['A'].name} y {rutas['B1'].name}", flush=True)


if __name__ == "__main__":
    main()
