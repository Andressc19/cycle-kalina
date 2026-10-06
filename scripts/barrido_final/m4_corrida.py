"""M4 — muestreo LHS y corrida global (TASK_CONTEXT final_M4, pasos 1 y 3).

Muestra `scipy.stats.qmc.LatinHypercube(d=10, seed=20261006)` escalada con
`qmc.scale` a la caja de las 10 variables (`m_b = 1.0`), guardada en
`m4_muestra.csv` ANTES de correr. Las N corridas (300; con `M4_HUMO=1`, 6 y la
salida va a `.../2026-10-06_final_M4/humo/`) corren en
`ProcessPoolExecutor(max_workers=5)` con `motor="teqp"` y el piso de O2 de cada
punto en su propia `T_sumidero`. Cada fila se escribe con flush en `m4_lhs.csv`
con `id_muestra` más las columnas `COLS`, y se imprime `[n/N] clase eta t_s`.
"""
from __future__ import annotations

import csv, os, sys, time  # noqa: E401,E402
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

from scipy.stats import qmc  # noqa: E402

from comun import COLS, evaluar_punto  # noqa: E402
from m4_datos import CAJA, OUT, SEED, VARS10  # noqa: E402

N_HUMO = 6
N_REAL = 300
N_WORKERS = 5
CM4 = ["id_muestra"] + list(COLS)
CMUESTRA = ["id_muestra"] + list(VARS10)


def n_puntos() -> int:
    return N_HUMO if os.environ.get("M4_HUMO") == "1" else N_REAL


def muestra() -> list:
    """Las N filas de la caja: LHS con un punto por franja de cada variable."""
    lo = [CAJA[v][0] for v in VARS10]
    hi = [CAJA[v][1] for v in VARS10]
    X = qmc.scale(qmc.LatinHypercube(d=len(VARS10), seed=SEED).random(n_puntos()),
                  lo, hi)
    return [dict(id_muestra=n, **{v: float(X[n][i]) for i, v in enumerate(VARS10)})
            for n in range(len(X))]


def guardar(mue: list) -> None:
    """Escribe `m4_muestra.csv` ANTES de lanzar ninguna corrida."""
    with open(OUT / "m4_muestra.csv", "w", encoding="utf-8", newline="") as fh:
        esc = csv.DictWriter(fh, fieldnames=CMUESTRA)
        esc.writeheader()
        esc.writerows(mue)
        fh.flush()
    print(f"m4_muestra.csv: {len(mue)} filas guardadas ANTES de correr",
          flush=True)


def combo(m: dict) -> dict:
    """El combo del punto: las 10 variables de la caja más `m_b = 1.0`."""
    return dict({v: m[v] for v in VARS10}, m_b=1.0)


def _eval(m: dict) -> dict:
    """UNA corrida; corre en un hijo del pool (patrón de `m3_ofat.py`)."""
    c = combo(m)
    f = evaluar_punto(c, motor="teqp", tag=f'm4:{m["id_muestra"]}',
                      t_amb_diseno=c["T_sumidero"])
    f["id_muestra"] = m["id_muestra"]
    return f


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    mue = muestra()
    guardar(mue)
    total = len(mue)
    print(f"M4 LHS | N={total} | {N_WORKERS} workers -> {OUT}", flush=True)
    t0, n = time.perf_counter(), 0
    with open(OUT / "m4_lhs.csv", "w", encoding="utf-8", newline="") as fh:
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
                eta = "-" if f["eta"] is None else f'{f["eta"]:.4f}'
                print(f'[{n}/{total}] {f["clasificacion"]} {eta} '
                      f'{f["t_s"]:.1f}s', flush=True)
    print(f"fin: {total} corridas en {time.perf_counter() - t0:.0f} s -> {OUT}",
          flush=True)


if __name__ == "__main__":
    main()
