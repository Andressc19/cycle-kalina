"""M10 — correr la re-evaluación de la Fase 3 (A) y los barridos que faltaron (B).

Un solo `ProcessPoolExecutor(7)`: cada fila KALINA de las familias F3-A…F3-E se
vuelve a evaluar con `evaluar_punto(motor="teqp", t_amb_diseno=<piso original>)`;
B1 recorre 15 puntos por variable y B2 la malla x_b × P_baja, ambas sobre el ancla
de Húsavík con piso 283.15. Las muestras se escriben ANTES de correr. Reanudable:
salta las claves ya presentes en cada CSV. Con `M10_HUMO=1`, 2 puntos por parte y
salida en `.../humo/`.
"""
from __future__ import annotations

import sys, time  # noqa: E401,E402
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

from comun import COLS, evaluar_punto  # noqa: E402

import m10_datos as d  # noqa: E402

N_WORKERS = 7
CF3 = list(COLS) + ["familia", "archivo_origen", "fila_origen", "clase_sept",
                    "eta_sept", "coincide_clase", "d_eta_pp"]
COF = list(COLS) + ["variable", "valor"]
CM = list(COLS)


def _eval(t: dict) -> dict:
    """UNA corrida en un hijo del pool; añade las columnas de su parte."""
    f = evaluar_punto(t["combo"], motor="teqp", tag=t["tag"],
                      t_amb_diseno=t["piso"])
    f["parte"] = t["parte"]
    if t["parte"] == "fase3":
        et = f.get("eta")
        f.update(familia=t["familia"], archivo_origen=t["archivo"],
                 fila_origen=t["fila"], clase_sept=t["clase_sept"],
                 eta_sept=t["eta_sept"],
                 coincide_clase=(f.get("clasificacion") == t["clase_sept"]))
        f["d_eta_pp"] = (None if et is None or t["eta_sept"] is None
                         else 100.0 * (et - t["eta_sept"]))
    elif t["parte"] == "ofat":
        f.update(variable=t["variable"], valor=t["valor"])
    return f


def main() -> None:
    d.OUT.mkdir(parents=True, exist_ok=True)
    tas = d.tareas()
    d.escribir_muestras(tas)
    fh3, esc3, v3 = d.reanudar(d.OUT / "m10_recorrida_fase3.csv", CF3)
    fho, esco, vo = d.reanudar(d.OUT / "m10_ofat.csv", COF)
    fhm, escm, vm = d.reanudar(d.OUT / "m10_malla_xb_pbaja.csv", CM)
    vistas = v3 | vo | vm
    pend = [t for t in tas if d.clave(t) not in vistas]
    print(f"M10 | {len(pend)} por correr ({len(vistas)} ya hechas de {len(tas)}) "
          f"| {N_WORKERS} workers -> {d.OUT}", flush=True)
    salida = {"fase3": (esc3, fh3), "ofat": (esco, fho), "malla": (escm, fhm)}
    cols = {"fase3": CF3, "ofat": COF, "malla": CM}
    t0, n = time.perf_counter(), 0
    try:
        with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
            futs = {ex.submit(_eval, t): t for t in pend}
            for fu in as_completed(futs):
                f = fu.result()
                parte = f["parte"]
                esc, fh = salida[parte]
                esc.writerow({c: f.get(c) for c in cols[parte]})
                fh.flush()
                n += 1
                clase = f.get("clasificacion") or f.get("error_inesperado") or "s/e"
                ts = "-" if f.get("t_s") is None else f'{f["t_s"]:.1f}s'
                etiq = (f'{f["variable"]}={f["valor"]:.4g}' if parte == "ofat"
                        else (f'xb={f["x_b"]:.2f},pb={f["P_baja"]:.0f}'
                              if parte == "malla" else f'{f["familia"]}'))
                print(f"[{n}/{len(pend)}] {parte}:{etiq} {clase} {ts}", flush=True)
    finally:
        for fh in (fh3, fho, fhm):
            fh.close()
    print(f"fin: {n} corridas en {time.perf_counter() - t0:.0f} s -> {d.OUT}",
          flush=True)


if __name__ == "__main__":
    main()
