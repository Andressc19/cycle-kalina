"""M5c + M4c — malla de 165 y LHS de 150 en UNA corrida (TASK_CONTEXT final_M5c_M4c).

**M5c:** malla completa `T_fuente = linspace(385, 410, 11)` ×
`eps_cond ∈ {0.85, 0.875, 0.90, 0.925, 0.95}` × `T_sumidero ∈ {278.15, 290.65,
300.032917}` = 165 celdas, con todo lo demás igual a `comun.PROFESOR` (P_alta
3000, P_baja 400, x_b 0.50, η_t 0.85, η_p 0.75, ε_HRVG 0.85, ε_reg 0.75).

**M4c:** LHS `LatinHypercube(d=10, seed=20261008)` sobre la caja de
`m4_datos.CAJA` con **P_baja ∈ [1500, 2500] kPa** (150 puntos, `id_muestra`
500–649). Si `P_baja >= P_alta − 300` el punto se omite sin evaluarlo
(`omitido=True`, con el motivo en `mensaje`).

Las DOS partes van al mismo `ProcessPoolExecutor(max_workers=7)` con
`evaluar_punto(..., motor="teqp", t_amb_diseno=combo["T_sumidero"])` (piso de O2
= T_sumidero en todo punto). `m4c_muestra.csv` se escribe ANTES de correr;
`m5c_malla.csv` y `m4c_lhs.csv` se escriben con flush y se imprime
`[n/N] parte clase t_s`. Con `M5C_HUMO=1`: 3 puntos por parte (los índices
0, 82 y 164 de la malla) y la salida va a `humo/`.
"""
from __future__ import annotations

import csv, os, sys, time  # noqa: E401,E402
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

import numpy as np  # noqa: E402
from scipy.stats import qmc  # noqa: E402

from comun import COLS, PROFESOR, evaluar_punto  # noqa: E402
from m4_datos import CAJA, VARS10  # noqa: E402

N_WORKERS = 7
HUMO = os.environ.get("M5C_HUMO") == "1"
SUF = "/humo" if HUMO else ""
OUT_M5C = _RAIZ / "resultados" / f"2026-10-07_final_M5c{SUF}"
OUT_M4C = _RAIZ / "resultados" / f"2026-10-07_final_M4c{SUF}"
SEED_C = 20261008            # semilla del LHS de M4c (TASK_CONTEXT §Parte 2)
ID0_C = 500                  # `id_muestra` de 500 a 649 (sigue a los 499 de M4b)
PB_C = (1500.0, 2500.0)      # caja de P_baja de M4c (TASK_CONTEXT §Parte 2)
DP_MIN = 300.0               # P_baja >= P_alta - 300 -> no se evalúa
MOTIVO = "P_baja demasiado cerca de P_alta"
TFUENTE = tuple(float(t) for t in np.linspace(385, 410, 11))   # 11 valores
EPS_COND = (0.85, 0.875, 0.90, 0.925, 0.95)                    # 5 valores
T_SUM = (278.15, 290.65, 300.032917)                           # 3 valores
IDS_HUMO = (0, 82, 164)      # 3 celdas repartidas por la malla de 165
N_M5C = len(IDS_HUMO) if HUMO else 165
N_M4C = 3 if HUMO else 150
CM5C = ["parte", "id"] + list(COLS)
CM4C = ["parte", "id", "omitido"] + list(COLS)
CMUESTRA = ["id_muestra"] + list(VARS10)


def puntos_m5c() -> list:
    """Las 165 celdas de la malla (con `M5C_HUMO=1`, las 3 de `IDS_HUMO`)."""
    out, n = [], 0
    for ts in T_SUM:
        for ec in EPS_COND:
            for tf in TFUENTE:
                out.append(dict(parte="M5c", id=n,
                                combo=dict(PROFESOR, T_fuente=tf, eps_cond=ec,
                                           T_sumidero=ts)))
                n += 1
    return [out[k] for k in IDS_HUMO] if HUMO else out


def muestra_m4c() -> list:
    """Las `N_M4C` filas del LHS de M4c: la caja de M4 con P_baja en [1500, 2500]."""
    lo = [CAJA[v][0] for v in VARS10]
    hi = [CAJA[v][1] for v in VARS10]
    lo[VARS10.index("P_baja")], hi[VARS10.index("P_baja")] = PB_C
    X = qmc.scale(qmc.LatinHypercube(d=len(VARS10), seed=SEED_C).random(N_M4C),
                  lo, hi)
    return [dict(id_muestra=ID0_C + n,
                 **{v: float(X[n][i]) for i, v in enumerate(VARS10)})
            for n in range(len(X))]


def guardar(mue: list) -> None:
    """Escribe `m4c_muestra.csv` ANTES de lanzar ninguna corrida."""
    with open(OUT_M4C / "m4c_muestra.csv", "w", encoding="utf-8",
              newline="") as fh:
        esc = csv.DictWriter(fh, fieldnames=CMUESTRA)
        esc.writeheader()
        esc.writerows(mue)
        fh.flush()
    print(f"m4c_muestra.csv: {len(mue)} filas guardadas ANTES de correr",
          flush=True)


def puntos_m4c(mue: list) -> list:
    """Los puntos de M4c: el combo de la caja más `m_b = 1.0`."""
    return [dict(parte="M4c", id=m["id_muestra"],
                 combo=dict({v: m[v] for v in VARS10}, m_b=1.0)) for m in mue]


def _eval(p: dict) -> dict:
    """UNA corrida; corre en un hijo del pool (patrón de `m4b_corrida.py`)."""
    c = p["combo"]
    if p["parte"] == "M5c":
        f = evaluar_punto(c, motor="teqp", tag=f'm5c:{p["id"]}',
                          t_amb_diseno=c["T_sumidero"])
        f.update(parte="M5c", id=p["id"])
        return f
    omit = c["P_baja"] >= c["P_alta"] - DP_MIN
    if omit:
        f = dict.fromkeys(COLS)
        f.update(tag=f'm4c:{p["id"]}', mensaje=MOTIVO,
                 **{v: c[v] for v in VARS10})
    else:
        f = evaluar_punto(c, motor="teqp", tag=f'm4c:{p["id"]}',
                          t_amb_diseno=c["T_sumidero"])
    f.update(parte="M4c", id=p["id"], omitido=omit)
    return f


def main() -> None:
    OUT_M5C.mkdir(parents=True, exist_ok=True)
    OUT_M4C.mkdir(parents=True, exist_ok=True)
    mue = muestra_m4c()
    guardar(mue)
    pts = puntos_m5c() + puntos_m4c(mue)
    total = len(pts)
    print(f"M5c+M4c | M5c={total - len(mue)} M4c={len(mue)} | "
          f"{N_WORKERS} workers | {OUT_M5C} · {OUT_M4C}", flush=True)
    t0, n = time.perf_counter(), 0
    with open(OUT_M5C / "m5c_malla.csv", "w", encoding="utf-8",
              newline="") as f5, \
         open(OUT_M4C / "m4c_lhs.csv", "w", encoding="utf-8",
              newline="") as f4:
        e5 = csv.DictWriter(f5, fieldnames=CM5C)
        e4 = csv.DictWriter(f4, fieldnames=CM4C)
        e5.writeheader()
        e4.writeheader()
        f5.flush()
        f4.flush()
        with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
            futs = [ex.submit(_eval, p) for p in pts]
            for fu in as_completed(futs):
                fila = fu.result()
                esc, cols, fh = ((e5, CM5C, f5) if fila["parte"] == "M5c"
                                 else (e4, CM4C, f4))
                esc.writerow({c: fila.get(c) for c in cols})
                fh.flush()
                n += 1
                omit = fila.get("omitido") is True
                clase = "omitido" if omit else fila["clasificacion"]
                ts = "-" if omit else ("n/d" if fila["t_s"] is None
                                       else f'{fila["t_s"]:.1f}s')
                print(f'[{n}/{total}] {fila["parte"]} {clase} {ts}', flush=True)
    print(f"fin: {total} corridas en {time.perf_counter() - t0:.0f} s",
          flush=True)


if __name__ == "__main__":
    main()
