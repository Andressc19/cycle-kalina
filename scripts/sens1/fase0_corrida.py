"""Sensibilidad 1, Fase 0 — 11 puntos H* (Húsavík con el nuevo tope eps_cond).

Corre un punto de referencia H* (Húsavík, eps_cond de 0.95 -> 0.90) con el nuevo
`extra=True` de `comun.evaluar_punto` (que guarda las energías y estados que el
motor ya calculaba), un control de no-regresión (`H0_noextra`, `extra=False`),
un barrido de caudal (M5..M20) y de eps_cond/P_baja alrededor de H* — todos con
`t_amb_diseno=283.15`. Motor `teqp`, patrón de `scripts/barrido_final/m3_ofat.py`.
Se ejecuta como script, no como módulo; salida en
`resultados/2026-10-14_sens1_fase0/`.
"""
from __future__ import annotations

import csv, sys, time  # noqa: E401,E402
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
_DIR_COMUN = _DIR.parents[0] / "barrido_final"
sys.path[:0] = [str(_RAIZ), str(_DIR_COMUN)]

from comun import COLS, COLS_EXTRA, evaluar_punto  # noqa: E402

OUT = _RAIZ / "resultados" / "2026-10-14_sens1_fase0"
N_WORKERS = 5
T_AMB = 283.15
# H* = Fase 3 de Húsavík (estudio 6.2), solo eps_cond cambia 0.95 -> 0.90.
BASE = dict(T_fuente=394.15, T_sumidero=278.15, P_alta=3300.0, P_baja=690.0,
            x_b=0.82, m_b=1.0, eta_t=0.85, eta_p=0.80, eps_hrvg=0.85,
            eps_reg=0.75, eps_cond=0.90)
# (id, cambio respecto a H*, extra) — H0_noextra es el control de no-regresión.
PUNTOS = (("H0", {}, True),
          ("H0_noextra", {}, False),
          ("M5", {"m_b": 5.0}, True),
          ("M10", {"m_b": 10.0}, True),
          ("M15", {"m_b": 15.0}, True),
          ("M20", {"m_b": 20.0}, True),
          ("E95", {"eps_cond": 0.95}, True),
          ("E85", {"eps_cond": 0.85}, True),
          ("E80", {"eps_cond": 0.80}, True),
          ("P600", {"P_baja": 600.0}, True),
          ("P800", {"P_baja": 800.0}, True))
CM = ["id_punto"] + list(COLS) + list(COLS_EXTRA)


def _eval(t: tuple) -> dict:
    """UNA corrida; corre en un hijo del pool (patrón de m3_ofat.py)."""
    pid, cambio, extra = t
    f = evaluar_punto(dict(BASE, **cambio), motor="teqp", tag=pid,
                      t_amb_diseno=T_AMB, extra=extra)
    f["id_punto"] = pid
    return f


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    total = len(PUNTOS)
    print(f"Fase 0 sensibilidad 1 | {total} puntos | {N_WORKERS} workers -> {OUT}",
          flush=True)
    t0, n = time.perf_counter(), 0
    with open(OUT / "fase0_filas.csv", "w", encoding="utf-8", newline="") as fh:
        esc = csv.DictWriter(fh, fieldnames=CM)
        esc.writeheader()
        fh.flush()
        with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
            futs = [ex.submit(_eval, t) for t in PUNTOS]
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
