"""M9 — paso 1: conservar UN grupo del profesor (final_M9 §1).

Seis escenarios `C_TF`, `C_EF`, `C_PA`, `C_PB`, `C_TS` y `C_XB`: en cada uno se
fija ese grupo (`comun.PROFESOR`) y el resto queda libre en la caja de M9. LHS de
100 puntos por escenario con `seed = 20261008 + k` (k = 1…6, en ese orden); la
muestra se guarda en `m9_paso1_muestra.csv` ANTES de correr. Las 600 corridas van
a un solo `ProcessPoolExecutor(max_workers=7)` con `evaluar_punto(..., motor=
"teqp", t_amb_diseno=combo["T_sumidero"])`; cada fila con flush en
`m9_paso1.csv`. Reanudable: se saltan los `(escenario, id)` ya presentes. Si
`P_baja >= P_alta − 300` el punto no se evalúa (`omitido=True`). Con `M9_HUMO=1`:
2 puntos por escenario en `resultados/2026-10-08_final_M9/humo/`.
"""
from __future__ import annotations

import csv, sys, time  # noqa: E401,E402
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

from comun import COLS, evaluar_punto  # noqa: E402
import m9_datos as m9  # noqa: E402

N_WORKERS = 7
TODOS = ("TF", "EF", "PA", "PB", "TS", "XB")
SEED0 = 20261008
N = 2 if m9.HUMO else 100
CMU = ["escenario", "conservados", "id", "seed"] + list(m9.VARS10) + ["m_b"]
CAM = ["escenario", "conservados", "id", "omitido"] + list(COLS)


def clave(escenario, i) -> tuple:
    return (escenario, str(i))


def muestra() -> list:
    """600 filas (12 con M9_HUMO=1): LHS de cada escenario, en orden."""
    out = []
    for k, g in enumerate(TODOS, 1):
        for i, p in enumerate(m9.muestra([g], N, SEED0 + k)):
            row = dict(escenario=f"C_{g}", conservados=g, id=i, seed=SEED0 + k)
            row.update(p)
            out.append(row)
    return out


def combo(m: dict) -> dict:
    return {v: m[v] for v in (*m9.VARS10, "m_b")}


def _eval(m: dict) -> dict:
    """UNA corrida; corre en un hijo del pool (patrón de `m5_corrida.py`)."""
    c = combo(m)
    tag = f'm9:S{m["escenario"]}:{m["id"]}'
    omit = c["P_baja"] >= c["P_alta"] - m9.DP_MIN
    f = (m9.omitido(c, tag=tag) if omit else
         evaluar_punto(c, motor="teqp", tag=tag,
                       t_amb_diseno=c["T_sumidero"]))
    f.update(escenario=m["escenario"], conservados=m["conservados"],
             id=m["id"], omitido=omit)
    return f


def main() -> None:
    m9.OUT.mkdir(parents=True, exist_ok=True)
    mue = muestra()
    with open(m9.OUT / "m9_paso1_muestra.csv", "w", encoding="utf-8",
              newline="") as fh:
        esc = csv.DictWriter(fh, fieldnames=CMU)
        esc.writeheader()
        esc.writerows({c: r.get(c) for c in CMU} for r in mue)
        fh.flush()
    print(f"m9_paso1_muestra.csv: {len(mue)} filas ANTES de correr", flush=True)
    fh, esc, vistos = m9.reanudar(
        m9.OUT / "m9_paso1.csv", CAM,
        lambda f: (f.get("escenario"), str(f.get("id"))))
    pend = [m for m in mue if clave(m["escenario"], m["id"]) not in vistos]
    total, n = len(mue), 0
    print(f"M9 paso 1 | {len(pend)} por correr de {total} (6 x {N}) | "
          f"{N_WORKERS} workers -> {m9.OUT}", flush=True)
    t0 = time.perf_counter()
    try:
        with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
            futs = [ex.submit(_eval, m) for m in pend]
            for fu in as_completed(futs):
                f = fu.result()
                esc.writerow({c: f.get(c) for c in CAM})
                fh.flush()
                n += 1
                clase = "omitido" if f["omitido"] else (
                    f.get("clasificacion") or f.get("error_inesperado") or "s/e")
                print(f'[{n}/{len(pend)}] {f["escenario"]}:{f["id"]} {clase}',
                      flush=True)
    finally:
        fh.close()
    print(f"fin: {n} corridas en {time.perf_counter() - t0:.0f} s -> {m9.OUT}",
          flush=True)


if __name__ == "__main__":
    main()
