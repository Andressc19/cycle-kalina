"""M6 — Parte B2: P_baja mínima para un margen de subenfriamiento ΔT_sub.

Bisección SOLO sobre `P_baja` de los puntos P01, P02, P03 y P05–P09 (cada uno
con su piso de la Parte A), para los objetivos ΔT_sub ∈ {2.0, 5.0} K, con el
predicado `clasificacion == "KALINA" and m_O2 >= ΔT_sub` y `motor="teqp"`.

`lo` = la P_baja del punto; `hi = min(0.6·P_alta, 2500)` kPa. Primero se
evalúa `lo` (si ya cumple, `P_baja_req = lo`), después `hi` (si allí no cumple,
se registra "no alcanzable con P_baja") y después se biseca hasta
`hi − lo ≤ 5 kPa` o 12 iteraciones, tomando el último `hi` que cumple. Las 16
bisecciones son independientes y se paralelizan entre ellas (7 workers).

Salida: `m6_subenfriamiento_evals.csv` (todas las evaluaciones) y
`m6_subenfriamiento.csv` (un resumen por caso). Con `M6_HUMO=1`: las 2
primeras bisecciones, en `humo/`.
"""
from __future__ import annotations

import csv
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

from comun import evaluar_punto  # noqa: E402
from m6_puntos import AVISOS, por_id  # noqa: E402

N_WORKERS = 7
HUMO = os.environ.get("M6_HUMO") == "1"
OUT = _RAIZ / "resultados" / ("2026-10-08_final_M6" + ("/humo" if HUMO else ""))
IDS = ("P01", "P02", "P03", "P05", "P06", "P07", "P08", "P09")
OBJETIVOS = (2.0, 5.0)
TOL_KPA, MAX_IT = 5.0, 12
CM6 = ["id", "origen", "ΔT_sub", "alcanzable", "P_baja_orig", "P_baja_req",
       "ΔP_baja", "eta_orig", "eta_req", "d_eta_pp", "rP_req", "m_O1_req",
       "iteraciones", "nota"]
CEV = ["id", "ΔT_sub", "paso", "P_baja", "convergio", "clasificacion", "eta",
       "m_O1", "m_O2", "cumple", "t_s"]


def _cumple(f: dict, obj: float) -> bool:
    m2 = f.get("m_O2")
    return f.get("clasificacion") == "KALINA" and m2 is not None and m2 >= obj


def _una(p: dict, obj: float, pb: float, paso: str) -> tuple:
    """Evalúa UN P_baja del punto; devuelve (fila, evaluación registrable)."""
    f = evaluar_punto(dict(p["combo"], P_baja=float(pb)), motor="teqp",
                      tag=f'm6b:{p["id"]}:{obj}:{paso}',
                      t_amb_diseno=p["piso"])
    e = {"id": p["id"], "ΔT_sub": obj, "paso": paso, "P_baja": float(pb),
         "convergio": f.get("convergio"), "clasificacion": f.get("clasificacion"),
         "eta": f.get("eta"), "m_O1": f.get("m_O1"), "m_O2": f.get("m_O2"),
         "cumple": _cumple(f, obj), "t_s": f.get("t_s")}
    print(f'  {p["id"]} ΔT={obj:g} {paso} P={float(pb):.1f} '
          f'{e["clasificacion"]} m_O2={e["m_O2"]} cumple={e["cumple"]} '
          f'{e["t_s"]:.1f}s', flush=True)
    return f, e


def _notas(evs: list) -> str:
    """No monótono (pasa abajo y falla arriba) y huecos NO_CONVERGIO."""
    out, ord_ = [], sorted(evs, key=lambda e: e["P_baja"])
    for a, b in zip(ord_, ord_[1:]):
        if a["cumple"] and not b["cumple"]:
            out.append(f"no monótono: cumple en {a['P_baja']:.1f} kPa y falla "
                       f"en {b['P_baja']:.1f} kPa")
            break
    mal = [e["P_baja"] for e in ord_ if e["clasificacion"] == "NO_CONVERGIO"]
    if mal:
        out.append("hueco NO_CONVERGIO en " +
                   ", ".join(f"{p:.1f} kPa" for p in mal))
    return "; ".join(out)


def _resumen(p: dict, obj: float, alcanzable: bool, pb_req, f_orig: dict,
             f_req: dict | None, it: int, evs: list, extra: str = "") -> dict:
    eta_o, eta_r = f_orig.get("eta"), (f_req or {}).get("eta")
    req = None if pb_req is None else float(pb_req)
    d_eta = None if (eta_o is None or eta_r is None) else 100.0 * (eta_r - eta_o)
    nota = "; ".join(x for x in (_notas(evs), extra) if x)
    return {"id": p["id"], "origen": p["origen"], "ΔT_sub": obj,
            "alcanzable": alcanzable, "P_baja_orig": float(p["combo"]["P_baja"]),
            "P_baja_req": req,
            "ΔP_baja": None if req is None else req - float(p["combo"]["P_baja"]),
            "eta_orig": eta_o, "eta_req": eta_r, "d_eta_pp": d_eta,
            "rP_req": None if req is None else p["combo"]["P_alta"] / req,
            "m_O1_req": None if f_req is None else f_req.get("m_O1"),
            "iteraciones": it, "nota": nota}


def bisecar(p: dict, obj: float) -> tuple:
    """`(resumen, evaluaciones)` de UN caso (corre dentro de un hijo del pool)."""
    lo, hi = float(p["combo"]["P_baja"]), min(0.6 * p["combo"]["P_alta"], 2500.0)
    evs: list = []
    print(f'{p["id"]} ΔT={obj:g}: lo={lo:.1f} hi={hi:.1f}', flush=True)
    f_lo, e_lo = _una(p, obj, lo, "lo")
    evs.append(e_lo)
    if e_lo["cumple"]:
        return _resumen(p, obj, True, lo, f_lo, f_lo, 0, evs), evs
    if hi <= lo:
        return _resumen(p, obj, False, None, f_lo, None, 0, evs,
                        f"hi ({hi:.1f}) <= lo ({lo:.1f})"), evs
    f_hi, e_hi = _una(p, obj, hi, "hi")
    evs.append(e_hi)
    if not e_hi["cumple"]:
        print(f'{p["id"]} ΔT={obj:g}: NO alcanzable en hi', flush=True)
        return _resumen(p, obj, False, None, f_lo, None, 0, evs,
                        f"no alcanzable con P_baja: no cumple en hi={hi:.1f} kPa"), evs
    it, f_req = 0, f_hi
    while hi - lo > TOL_KPA and it < MAX_IT:
        it += 1
        mid = 0.5 * (lo + hi)
        f_mid, e_mid = _una(p, obj, mid, f"it{it}")
        evs.append(e_mid)
        if e_mid["cumple"]:
            hi, f_req = mid, f_mid
        else:
            lo = mid
    return _resumen(p, obj, True, hi, f_lo, f_req, it, evs), evs


def tareas() -> list:
    pts = por_id()
    t = [(pts[i], o) for i in IDS for o in OBJETIVOS if i in pts]
    return t[:2] if HUMO else t


def main() -> None:
    for a in AVISOS:
        print("AVISO:", a, flush=True)
    ts = tareas()
    if not ts:
        raise SystemExit("sin tareas: revise los AVISOS de m6_puntos")
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"M6 B2 | {len(ts)} bisecciones | {N_WORKERS} workers | {OUT}",
          flush=True)
    t0, n = time.perf_counter(), 0
    p_res, p_evs = OUT / "m6_subenfriamiento.csv", OUT / "m6_subenfriamiento_evals.csv"
    with open(p_res, "w", encoding="utf-8", newline="") as fh_r, \
         open(p_evs, "w", encoding="utf-8", newline="") as fh_e:
        w_r, w_e = csv.DictWriter(fh_r, fieldnames=CM6), csv.DictWriter(fh_e, fieldnames=CEV)
        w_r.writeheader()
        w_e.writeheader()
        fh_r.flush()
        fh_e.flush()
        with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
            futs = [ex.submit(bisecar, p, o) for p, o in ts]
            for fu in as_completed(futs):
                res, evs = fu.result()
                w_e.writerows(evs)
                w_r.writerow(res)
                fh_e.flush()
                fh_r.flush()
                n += 1
                print(f'[{n}/{len(ts)}] {res["id"]} ΔT={res["ΔT_sub"]:g} '
                      f'alcanzable={res["alcanzable"]} '
                      f'P_req={res["P_baja_req"]} iter={res["iteraciones"]} '
                      f'nota={res["nota"] or "-"}', flush=True)
    print(f"fin: {n} bisecciones en {time.perf_counter() - t0:.0f} s",
          flush=True)


if __name__ == "__main__":
    main()
