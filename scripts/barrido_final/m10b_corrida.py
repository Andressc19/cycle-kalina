"""M10b — correr el OFAT de x_b (0.30–0.70) y la malla x_b × P_baja bajas.

Un solo `ProcessPoolExecutor(7)`: 17 + 54 = 71 corridas con `evaluar_punto(motor=
"teqp")` sobre el ancla de Húsavík (la misma de M10), piso de O2 283.15 K. Las
muestras se escriben ANTES de correr. Reanudable: salta las claves ya presentes
en cada CSV. Con `M10B_HUMO=1` corre 1 punto de cada parte (2 en total) y la
salida va en `.../humo/`.
"""
from __future__ import annotations

import sys, time  # noqa: E401,E402
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

from comun import evaluar_punto  # noqa: E402

import m10_datos as d10  # noqa: E402
import m10b_datos as d  # noqa: E402

N_WORKERS = 7


def _eval(t: dict) -> dict:
    """UNA corrida en un hijo del pool; añade las columnas de su parte."""
    f = evaluar_punto(t["combo"], motor="teqp", tag=t["tag"],
                      t_amb_diseno=t["piso"])
    f["parte"] = t["parte"]
    if t["parte"] == "ofat":
        f.update(variable=t["variable"], valor=t["valor"])
    return f


def main() -> None:
    d.OUT.mkdir(parents=True, exist_ok=True)
    tas = d.tareas()
    d.escribir_muestras(tas)
    fho, esco, vo = d10.reanudar(d.OUT / "m10b_ofat_xb.csv", d.COF)
    fhm, escm, vm = d10.reanudar(d.OUT / "m10b_malla_xb_pbaja.csv", d.CM)
    vistas = vo | vm
    pend = [t for t in tas if d.clave(t) not in vistas]
    print(f"M10b | {len(pend)} por correr ({len(vistas)} ya hechas de {len(tas)}) "
          f"| {N_WORKERS} workers -> {d.OUT}", flush=True)
    salida = {"ofat": (esco, fho), "malla": (escm, fhm)}
    cols = {"ofat": d.COF, "malla": d.CM}
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
                etiq = (f'x_b={f["x_b"]:.3f}' if parte == "ofat"
                        else f'xb={f["x_b"]:.2f},pb={f["P_baja"]:.0f}')
                print(f"[{n}/{len(pend)}] {parte}:{etiq} {clase} {ts}", flush=True)
    finally:
        for fh in (fho, fhm):
            fh.close()
    print(f"fin: {n} corridas en {time.perf_counter() - t0:.0f} s -> {d.OUT}",
          flush=True)


if __name__ == "__main__":
    main()
