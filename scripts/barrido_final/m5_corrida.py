"""M5 — 5 escenarios × 120 puntos LHS y la corrida (TASK_CONTEXT final_M5).

Cada escenario fija un subconjunto de los datos del profesor (`comun.PROFESOR`)
y deja libres las demás variables dentro de la caja de M5. Las 5 muestras se
generan con `scipy.stats.qmc.LatinHypercube(d=n_libres, seed=20261007 + k)`
(k = número del escenario, 1…5) y se guardan en `m5_muestra.csv` ANTES de
correr. Las 600 corridas (con `M5_HUMO=1`, 2 por escenario, y la salida va a
`.../2026-10-07_final_M5/humo/`) van todas al mismo
`ProcessPoolExecutor(max_workers=7)` con `evaluar_punto(..., motor="teqp",
t_amb_diseno=combo["T_sumidero"])`. Cada fila se escribe con flush en
`m5_lhs.csv` (columnas `escenario, id, omitido` más las de `COLS`) y se imprime
`[n/600] Sk clase t_s`. Si `P_baja >= P_alta − 300` el punto NO se evalúa:
queda `omitido=True` con el motivo en `mensaje` (sus variables sí se escriben).
"""
from __future__ import annotations

import csv, os, sys, time  # noqa: E401,E402
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

from scipy.stats import qmc  # noqa: E402

from comun import COLS, PROFESOR, evaluar_punto  # noqa: E402

N_WORKERS = 7
HUMO = os.environ.get("M5_HUMO") == "1"
N_POR_ESC = 2 if HUMO else 120
OUT = _RAIZ / "resultados" / ("2026-10-07_final_M5/humo" if HUMO
                              else "2026-10-07_final_M5")
SEED0 = 20261007            # semilla del LHS: 20261007 + k (§Diseño)
DP_MIN = 300.0              # P_baja >= P_alta - 300 kPa -> no se evalúa
MOTIVO = "P_baja demasiado cerca de P_alta"
# Rangos de las variables libres, fijados por el director (TASK_CONTEXT §tabla).
RANGOS = {"P_alta": (2000.0, 5000.0), "P_baja": (200.0, 2000.0),
          "T_fuente": (380.0, 623.15), "T_sumidero": (278.15, 303.55),
          "x_b": (0.50, 0.85), "eta_t": (0.40, 0.95), "eta_p": (0.40, 0.95),
          "eps_hrvg": (0.40, 0.95), "eps_reg": (0.40, 0.95),
          "eps_cond": (0.40, 0.95)}
# Qué conserva cada escenario del profesor (TASK_CONTEXT §Escenarios).
FIJOS = {1: ("T_fuente", "T_sumidero"), 2: ("P_alta", "P_baja"),
         3: ("P_alta", "P_baja", "T_sumidero"),
         4: ("P_alta", "T_fuente", "T_sumidero"), 5: ("T_fuente", "x_b")}
LIBRES = {k: [v for v in RANGOS if v not in FIJOS[k]] for k in FIJOS}
CMUESTRA = ["escenario", "id"] + list(RANGOS)
CAM5 = ["escenario", "id", "omitido"] + list(COLS)


def muestra_esc(k: int) -> list:
    """Las `N_POR_ESC` filas del escenario `k`: LHS sobre sus variables libres."""
    lib = LIBRES[k]
    X = qmc.scale(qmc.LatinHypercube(d=len(lib), seed=SEED0 + k).random(N_POR_ESC),
                  [RANGOS[v][0] for v in lib], [RANGOS[v][1] for v in lib])
    out = []
    for n in range(len(X)):
        punto = {v: PROFESOR[v] for v in FIJOS[k]}     # lo que se conserva
        punto.update({v: float(X[n][i]) for i, v in enumerate(lib)})
        out.append(dict(escenario=k, id=n, **punto))
    return out


def muestra() -> list:
    """Los 5 escenarios seguidos: 600 filas (10 con `M5_HUMO=1`)."""
    return [f for k in sorted(FIJOS) for f in muestra_esc(k)]


def guardar(mue: list) -> None:
    """Escribe `m5_muestra.csv` ANTES de lanzar ninguna corrida."""
    with open(OUT / "m5_muestra.csv", "w", encoding="utf-8", newline="") as fh:
        esc = csv.DictWriter(fh, fieldnames=CMUESTRA)
        esc.writeheader()
        esc.writerows(mue)
        fh.flush()
    print(f"m5_muestra.csv: {len(mue)} filas guardadas ANTES de correr", flush=True)


def combo(m: dict) -> dict:
    """El combo del punto: las 10 variables más `m_b = 1.0`."""
    return dict({v: m[v] for v in RANGOS}, m_b=1.0)


def _eval(m: dict) -> dict:
    """UNA corrida; corre en un hijo del pool (patrón de `m4b_corrida.py`)."""
    c = combo(m)
    omit = c["P_baja"] >= c["P_alta"] - DP_MIN
    tag = f'm5:S{m["escenario"]}:{m["id"]}'
    if omit:
        f = dict.fromkeys(COLS)
        f.update(tag=tag, mensaje=MOTIVO, **{v: c[v] for v in RANGOS})
    else:
        f = evaluar_punto(c, motor="teqp", tag=tag,
                          t_amb_diseno=c["T_sumidero"])
    f.update(escenario=m["escenario"], id=m["id"], omitido=omit)
    return f


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    mue = muestra()
    guardar(mue)
    total = len(mue)
    print(f"M5 LHS | N={total} ({N_POR_ESC} x 5) | {N_WORKERS} workers -> {OUT}",
          flush=True)
    t0, n = time.perf_counter(), 0
    with open(OUT / "m5_lhs.csv", "w", encoding="utf-8", newline="") as fh:
        esc = csv.DictWriter(fh, fieldnames=CAM5)
        esc.writeheader()
        fh.flush()
        with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
            futs = [ex.submit(_eval, m) for m in mue]
            for fu in as_completed(futs):
                f = fu.result()
                esc.writerow({c: f.get(c) for c in CAM5})
                fh.flush()
                n += 1
                clase = "omitido" if f["omitido"] else f["clasificacion"]
                ts = "-" if f["omitido"] else (
                    "n/d" if f["t_s"] is None else f'{f["t_s"]:.1f}s')
                print(f'[{n}/{total}] S{f["escenario"]} {clase} {ts}', flush=True)
    print(f"fin: {total} corridas en {time.perf_counter() - t0:.0f} s -> {OUT}",
          flush=True)


if __name__ == "__main__":
    main()
