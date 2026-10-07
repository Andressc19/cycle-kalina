"""M4b — 200 puntos nuevos con LHS y corrida (TASK_CONTEXT final_M4b, paso 1).

Muestra `scipy.stats.qmc.LatinHypercube(d=10, seed=20261007)` escalada con
`qmc.scale` a la **misma caja** `m4_datos.CAJA` (`m_b = 1.0`), con `id_muestra`
de 300 a 499, guardada en `m4b_muestra.csv` ANTES de correr. Las corridas (200;
con `M4B_HUMO=1`, 4 y la salida va a `.../2026-10-07_final_M4b/humo/`) van en
`ProcessPoolExecutor(max_workers=7)` con el mismo motor y la misma evaluación
que M4: `evaluar_punto(..., motor="teqp", t_amb_diseno=T_sumidero)`. Cada fila
se escribe con flush en `m4b_lhs.csv` y se imprime `[n/200] clase t_s`.
"""
from __future__ import annotations

import csv, sys, time  # noqa: E401,E402
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

from scipy.stats import qmc  # noqa: E402

from comun import COLS, evaluar_punto  # noqa: E402
from m4_datos import CAJA, VARS10  # noqa: E402
from m4b_datos import ID0, N_M4B, OUT, SEED_B  # noqa: E402

N_WORKERS = 7
CM4 = ["id_muestra"] + list(COLS)
CMUESTRA = ["id_muestra"] + list(VARS10)


def muestra() -> list:
    """Las N filas de la caja: LHS con un punto por franja de cada variable."""
    lo = [CAJA[v][0] for v in VARS10]
    hi = [CAJA[v][1] for v in VARS10]
    X = qmc.scale(qmc.LatinHypercube(d=len(VARS10), seed=SEED_B).random(N_M4B),
                  lo, hi)
    return [dict(id_muestra=ID0 + n,
                 **{v: float(X[n][i]) for i, v in enumerate(VARS10)})
            for n in range(len(X))]


def guardar(mue: list) -> None:
    """Escribe `m4b_muestra.csv` ANTES de lanzar ninguna corrida."""
    with open(OUT / "m4b_muestra.csv", "w", encoding="utf-8", newline="") as fh:
        esc = csv.DictWriter(fh, fieldnames=CMUESTRA)
        esc.writeheader()
        esc.writerows(mue)
        fh.flush()
    print(f"m4b_muestra.csv: {len(mue)} filas guardadas ANTES de correr",
          flush=True)


def combo(m: dict) -> dict:
    """El combo del punto: las 10 variables de la caja más `m_b = 1.0`."""
    return dict({v: m[v] for v in VARS10}, m_b=1.0)


def _eval(m: dict) -> dict:
    """UNA corrida; corre en un hijo del pool (patrón de `m4_corrida.py`)."""
    c = combo(m)
    f = evaluar_punto(c, motor="teqp", tag=f'm4b:{m["id_muestra"]}',
                      t_amb_diseno=c["T_sumidero"])
    f["id_muestra"] = m["id_muestra"]
    return f


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    mue = muestra()
    guardar(mue)
    total = len(mue)
    print(f"M4b LHS | N={total} | {N_WORKERS} workers -> {OUT}", flush=True)
    t0, n = time.perf_counter(), 0
    with open(OUT / "m4b_lhs.csv", "w", encoding="utf-8", newline="") as fh:
        esc = csv.DictWriter(fh, fieldnames=CM4)
        esc.writeheader()
        fh.flush()
        with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
            futs = [ex.submit(_eval, m) for m in mue]
            for fu in as_completed(futs):
                f = fu.result()
                esc.writerow({c: f.get(c) for c in CM4})
                fh.flush()
                n += 1
                ts = "n/d" if f["t_s"] is None else f'{f["t_s"]:.1f}s'
                print(f'[{n}/{total}] {f["clasificacion"]} {ts}', flush=True)
    print(f"fin: {total} corridas en {time.perf_counter() - t0:.0f} s -> {OUT}",
          flush=True)


if __name__ == "__main__":
    main()
