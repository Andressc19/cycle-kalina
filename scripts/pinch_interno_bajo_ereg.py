"""Ronda corta de la sonda de pinch interno con ε_reg < 0.60 (corrección 4).

La muestra principal no tiene KALINA confiable con ε_reg < 0.60. Aquí se toman
5 puntos base ya medidos (A*, óptimos 5.1a y 5.1b, la franja 4.2 a 410 K con
ε_cond 0.95 y 300 K de sumidero, y Húsavík `husavik_2`) y se les cambia SOLO ε_reg a 0.40 y 0.55. No son puntos KALINA
confiables por construcción: es una comprobación del pinch, con las mismas
funciones de `pinch_interno.py`. Salida: `OUT/bajo_ereg/`.
"""
from __future__ import annotations

import csv, sys, time  # noqa: E401,E402
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_DIR = Path(__file__).resolve().parent
sys.path[:0] = [str(_DIR.parent), str(_DIR), str(_DIR / "barrido_final")]

import pinch_interno as pi  # noqa: E402
from pinch_interno_muestra import seleccionar  # noqa: E402

BASES = ("A*", "opt_5.1a", "opt_5.1b", "husavik_2")
EPS = (0.40, 0.55)
OUT = pi.OUT / "bajo_ereg"


def puntos() -> list:
    todos = seleccionar()
    bases = [p for p in todos if p["tag"] in BASES and p["motor"] == "teqp"]
    bases += [p for p in todos if p["grupo"] == "franja_4_2"
              and abs(p["T_fuente"] - 410.0) < 1e-6 and abs(p["eps_cond"] - 0.95) < 1e-6
              and abs(p["T_sumidero"] - 300.032917) < 1e-3][:1]
    out = []
    for b in bases:
        for e in EPS:
            out.append(dict(b, eps_reg=e, tag=f'{b["tag"]}_ereg{e:.2f}',
                            grupo="bajo_ereg", motor="teqp"))
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pts = puntos()
    print(f"bajo_ereg | N={len(pts)} -> {OUT}", flush=True)
    t0 = time.perf_counter()
    with open(OUT / "pinch_puntos.csv", "w", encoding="utf-8", newline="") as fh, \
         open(OUT / "perfiles_todos.csv", "w", encoding="utf-8", newline="") as fp:
        esc = csv.DictWriter(fh, fieldnames=pi.CAMPOS)
        per = csv.DictWriter(fp, fieldnames=pi.CAM_PERF)
        esc.writeheader(), per.writeheader()
        with ProcessPoolExecutor(max_workers=min(6, len(pts))) as ex:
            for n, fu in enumerate(as_completed([ex.submit(pi._eval, p) for p in pts]), 1):
                fila, perf = fu.result()
                esc.writerow(fila), per.writerows(perf)
                fh.flush(), fp.flush()
                print(f'[{n}/{len(pts)}] {fila["tag"]} eps_reg={fila["eps_reg"]} '
                      f'{fila["clase_pinch"]} pinch={fila["reg_pinch_K"]} '
                      f'pos_f={fila["reg_pos_f"]} T1={fila["T1"]} '
                      f'T_bub={fila["T_bub_alta"]} {fila["t_s"]:.0f}s', flush=True)
    print(f"fin: {len(pts)} puntos en {time.perf_counter() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
