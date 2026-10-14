"""Sensibilidad 1, Fase A — barridos OFAT (una variable) alrededor de 2 centros.

Para cada centro (C1 «frío» Húsavík, C2 «cálido» ancla A*) se corre el punto
base (todas las variables en el centro, `m_b=1.0`) y, para cada una de las 10
variables de diseño, un barrido univariado con el resto fijo en el centro. El
`t_amb_diseno` de cada punto es su propio `T_sumidero` (piso de O2). Como los
barridos solo cambian UNA variable, la única combinación repetida es el punto
base; se elimina por clave y se marca `variable="base"` (una vez por centro).
Motor `teqp`, `extra=True`; 5 procesos; escritura incremental con flush. Salida
en `resultados/2026-10-14_sens1_faseA/` (`faseA_filas.csv`, `faseA_log.txt`).
Se ejecuta como script, no como módulo.
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

OUT = _RAIZ / "resultados" / "2026-10-14_sens1_faseA"
N_WORKERS = 5

VARIABLES = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b",
             "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")
CENTROS = (("C1", dict(T_fuente=394.15, T_sumidero=278.15, P_alta=3300.0,
                       P_baja=690.0, x_b=0.82, m_b=1.0, eta_t=0.85,
                       eta_p=0.80, eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.95)),
           ("C2", dict(T_fuente=403.0, T_sumidero=300.15, P_alta=3000.0,
                       P_baja=563.64, x_b=0.50, m_b=1.0, eta_t=0.85,
                       eta_p=0.75, eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.95)))
# Grado en °C de los barridos de T_fuente del profesor: 70..300 paso 10 más los
# finos 105..165 paso 10.
_TF_C = [70 + 10 * i for i in range(24)] + [105, 115, 125, 135, 145, 155, 165]
_ETAS = [round(0.40 + 0.05 * i, 2) for i in range(12)]     # 0.40..0.95
_XB = [round(0.30 + 0.05 * i, 2) for i in range(14)]       # 0.30..0.95
_TS = [round(278.15 + 2.5 * i, 2) for i in range(11)]      # 278.15..303.15
_PALTA = [2000.0 + 250 * i for i in range(13)]             # 2000..5000
_PBAJA = [300.0 + 100 * i for i in range(13)]              # 300..1500
CM = ["id_punto", "centro", "variable", "valor"] + list(COLS) + list(COLS_EXTRA)


def _valores(nom: str, base: float) -> list:
    """Valores del barrido de `nom`. Para T_fuente, T_sumidero y P_baja se añade
    el del centro si no está en la rejilla (lo pide la especificación); en los
    demás la rejilla es la del profesor tal cual."""
    if nom == "T_fuente":
        vals = [round(c + 273.15, 2) for c in _TF_C]
    elif nom == "T_sumidero":
        vals = list(_TS)
    elif nom == "P_baja":
        vals = list(_PBAJA)
    elif nom == "P_alta":
        return list(_PALTA)
    elif nom == "x_b":
        return list(_XB)
    else:
        return list(_ETAS)
    if not any(abs(v - base) <= 1e-9 for v in vals):
        vals.append(round(base, 2))
    return sorted(vals)


def _clave(combo: dict) -> tuple:
    return tuple(round(combo[k], 6) for k in VARIABLES)


def tareas() -> list:
    """El punto base + los barridos de cada centro, sin combinaciones repetidas."""
    out = []
    for centro, base in CENTROS:
        vistos, idx = set(), [0]

        def add(var: str, valor, combo: dict) -> None:
            k = _clave(combo)
            if k in vistos:            # p. ej. el punto base repetido en un barrido
                return
            vistos.add(k)
            out.append(dict(id_punto=f"{centro}-{var}-{idx[0]:04d}",
                            centro=centro, variable=var, valor=valor,
                            combo=dict(combo)))
            idx[0] += 1

        add("base", None, base)
        for nom in VARIABLES:
            for v in _valores(nom, base[nom]):
                add(nom, float(v), dict(base, **{nom: float(v)}))
    return out


def _eval(t: dict) -> dict:
    """UNA corrida; corre en un hijo del pool (patrón de fase0_corrida.py)."""
    f = evaluar_punto(t["combo"], motor="teqp", tag=t["id_punto"],
                      t_amb_diseno=t["combo"]["T_sumidero"], extra=True)
    f.update({k: t[k] for k in ("id_punto", "centro", "variable", "valor")})
    return f


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ts = tareas()
    total = len(ts)
    por_c = {c: sum(1 for t in ts if t["centro"] == c) for c, _ in CENTROS}
    print(f"Fase A sensibilidad 1 | {total} puntos {por_c} | {N_WORKERS} workers"
          f" -> {OUT}", flush=True)
    t0, n = time.perf_counter(), 0
    with open(OUT / "faseA_filas.csv", "w", encoding="utf-8", newline="") as fh:
        esc = csv.DictWriter(fh, fieldnames=CM)
        esc.writeheader()
        fh.flush()
        with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
            futs = [ex.submit(_eval, t) for t in ts]
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
