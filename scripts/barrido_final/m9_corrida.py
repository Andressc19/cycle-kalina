"""M9 — paso 0 (Húsavík) y paso 3 (motor real) en UN solo pool (final_M9 §0 y §3).

Paso 0: el punto base de Húsavík (3300/690/0.82/394.15/278.15) con P_baja de 500 a
1000 kPa en pasos de 50 y dos pisos de O2 (283.15 y 278.15): 22 corridas. Paso 3:
tres puntos con `motor="real"` y presupuesto 1500 s —A*, el óptimo A4 de M7 y la
base de Húsavík— que arrancan primero en el mismo pool de 7. Salidas
`m9_husavik.csv` y `m9_motor_real.csv`. Reanudable: las filas reales crudas viven
en `m9_motor_real_raw.csv` y se saltan los `id`/`(piso, P_baja)` ya hechos. Con
`M9_HUMO=1`: 2 P_baja × 2 pisos + los 3 reales. El envoltorio de nivel de módulo
fija `comun.PRESUPUESTO_S` (1500 real, 300 teqp) antes de `evaluar_punto`.
"""
from __future__ import annotations

import csv, sys, time  # noqa: E401,E402
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

from comun import COLS, PROFESOR, evaluar_punto  # noqa: E402
import m9_datos as m9  # noqa: E402

N_WORKERS = 7
M7 = _RAIZ / "resultados" / "2026-10-07_final_M7"
M6 = _RAIZ / "resultados" / "2026-10-08_final_M6"
PB_MALLA = [500.0, 550.0, 690.0] if m9.HUMO else sorted(
    set(range(500, 1001, 50)) | {690})  # 690 = base del caso, fuera de la malla
PISOS = (283.15, 278.15)
PISO_HUS = 283.15
HUSAVIK = dict(P_alta=3300.0, P_baja=690.0, x_b=0.82, T_fuente=394.15,
               T_sumidero=278.15, eta_t=0.90, eta_p=0.80, eps_hrvg=0.85,
               eps_reg=0.75, eps_cond=0.95, m_b=1.0)
ID_REAL = ("A*", "A4", "HUS")
CHUS = ["piso_tamb", "P_baja_test"] + list(COLS)
CRAW = ["id", "origen"] + list(COLS)
CMP = ["id", "origen", "clase_teqp", "eta_teqp", "clase_real", "eta_real",
       "d_eta_pp", "coincide_clase", "T_amb_diseno", "T_fuente", "T_sumidero",
       "P_alta", "P_baja", "x_b", "eta_t", "eta_p", "eps_hrvg", "eps_reg",
       "eps_cond", "fuera_rango", "B_verificado", "t_s", "mensaje"]


def a4() -> dict:
    """El combo del óptimo A4 de M7 (las 11 variables con `m_b`=1.0)."""
    with open(M7 / "m7_optimos.csv", encoding="utf-8", newline="") as fh:
        r = next(x for x in csv.DictReader(fh) if x["arranque"] == "A4")
    return {**{v: float(r[v]) for v in ("T_fuente", "T_sumidero", "P_alta",
              "P_baja", "x_b", "eta_t", "eta_p", "eps_hrvg", "eps_reg",
              "eps_cond")}, "m_b": 1.0}


def a_estrella() -> dict:
    """El ancla A* de M6 (`dict(PROFESOR, T_fuente=403.0, P_baja=563.636…)`)."""
    return dict(PROFESOR, T_fuente=403.0, P_baja=563.6363636363637)


def tareas() -> list:
    """Paso 3 (3 reales, primero) y paso 0 (22 de Húsavík)."""
    a = a4()
    t = [dict(parte="motor_real", id="A*", origen="Ancla A*", motor="real",
              combo=a_estrella(), piso=PROFESOR["T_sumidero"], tag="m9:R:A*"),
         dict(parte="motor_real", id="A4", origen="Óptimo A4 de M7",
              motor="real", combo=a, piso=a["T_sumidero"], tag="m9:R:A4"),
         dict(parte="motor_real", id="HUS", origen="Base de Húsavík",
              motor="real", combo=dict(HUSAVIK), piso=PISO_HUS, tag="m9:R:HUS")]
    for pb in PB_MALLA:
        for piso in PISOS:
            t.append(dict(parte="husavik", id=None, motor="teqp", piso=piso,
                          combo=dict(HUSAVIK, P_baja=float(pb)),
                          tag=f"m9:H:{pb}:{piso}", pb=float(pb)))
    return t


def _eval(t: dict) -> dict:
    """UNA corrida en un hijo; fija el presupuesto según el motor."""
    import comun
    comun.PRESUPUESTO_S = 1500 if t["motor"] == "real" else 300
    f = evaluar_punto(t["combo"], motor=t["motor"], tag=t["tag"],
                      t_amb_diseno=t["piso"])
    f.update(parte=t["parte"], id=t.get("id"), origen=t.get("origen"),
             pb=t.get("pb"), piso_tamb=t["piso"], P_baja_test=t.get("pb"))
    return f


def _refs(hus: list) -> dict:
    """Clase y η teqp de los 3 puntos (Húsavík del paso 0; A*/A4 de M6)."""
    h = next((f for f in hus if m9.num(f.get("P_baja_test")) == 690.0
              and m9.num(f.get("piso_tamb")) == 283.15), None)
    ref = {"HUS": (h["clasificacion"], h["eta"]) if h else (None, None)}
    with open(M6 / "m6_verificacion.csv", encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["motor"] == "teqp" and r["id"] in ("P01", "P08"):
                ref["A*" if r["id"] == "P01" else "A4"] = (
                    r["clasificacion"] or None, m9.num(r["eta"]))
    return ref


def _comparacion(hus: list, reales: list) -> list:
    """Una fila por punto: clase/η de los dos motores y `d_eta_pp`."""
    ref, out = _refs(hus), []
    for f in reales:
        ct, et = ref.get(f["id"], (None, None))
        er = f["eta"]
        out.append(dict(id=f["id"], origen=f["origen"], clase_teqp=ct,
                        eta_teqp=et, clase_real=f["clasificacion"], eta_real=er,
                        d_eta_pp=None if et is None or er is None else 100.0 * (er - et),
                        coincide_clase=(ct == f["clasificacion"]),
                        T_amb_diseno=f["T_amb_diseno"],
                        **{v: f.get(v) for v in ("T_fuente", "T_sumidero",
                           "P_alta", "P_baja", "x_b", "eta_t", "eta_p",
                           "eps_hrvg", "eps_reg", "eps_cond")},
                        fuera_rango=f.get("fuera_rango"),
                        B_verificado=f.get("B_verificado"), t_s=f.get("t_s"),
                        mensaje=f.get("mensaje")))
    return out


def main() -> None:
    m9.OUT.mkdir(parents=True, exist_ok=True)
    m9.marca_inicio()
    fhH, escH, vH = m9.reanudar(m9.OUT / "m9_husavik.csv", CHUS,
                                lambda f: (str(f.get("piso_tamb")),
                                           str(f.get("P_baja_test"))))
    fhR, escR, vR = m9.reanudar(m9.OUT / "m9_motor_real_raw.csv", CRAW,
                                lambda f: str(f.get("id")))
    ts = [t for t in tareas()
          if not (t["parte"] == "motor_real" and str(t["id"]) in vR)
          and not (t["parte"] == "husavik"
                   and (str(t["piso"]), str(t["pb"])) in vH)]
    print(f"M9 paso 0+3 | {len(ts)} por correr ({len(vH)} Húsavík y {len(vR)} "
          f"reales ya hechos) | {N_WORKERS} workers -> {m9.OUT}", flush=True)
    t0, n = time.perf_counter(), 0
    try:
        if ts:
            with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
                for fu in as_completed([ex.submit(_eval, t) for t in ts]):
                    f = fu.result()
                    n += 1
                    clase = f.get("clasificacion") or f.get("error_inesperado") or "s/e"
                    ts_ = "-" if f.get("t_s") is None else f'{f["t_s"]:.1f}s'
                    if f["parte"] == "motor_real":
                        escR.writerow({c: f.get(c) for c in CRAW}); fhR.flush()
                        print(f'[{n}/{len(ts)}] REAL {f["id"]} {clase} {ts_}',
                              flush=True)
                    else:
                        escH.writerow({c: f.get(c) for c in CHUS}); fhH.flush()
                        print(f'[{n}/{len(ts)}] HUS P_baja={f["pb"]:g} '
                              f'piso={f["piso_tamb"]:g} {clase} {ts_}', flush=True)
    finally:
        fhH.close(); fhR.close()
    comp = _comparacion(m9.leer(m9.OUT / "m9_husavik.csv"),
                        m9.leer(m9.OUT / "m9_motor_real_raw.csv"))
    with open(m9.OUT / "m9_motor_real.csv", "w", encoding="utf-8",
              newline="") as fh2:
        w = csv.DictWriter(fh2, fieldnames=CMP)
        w.writeheader()
        w.writerows({c: r.get(c) for c in CMP}
                    for r in sorted(comp, key=lambda r: r["id"]))
        fh2.flush()
    print(f"fin: {n} corridas en {time.perf_counter() - t0:.0f} s -> {m9.OUT}",
          flush=True)
    for r in sorted(comp, key=lambda r: r["id"]):
        print(f'real vs teqp {r["id"]}: {r["clase_real"]}/{r["clase_teqp"]} '
              f'eta_real={r["eta_real"]} eta_teqp={r["eta_teqp"]} '
              f'd_eta_pp={r["d_eta_pp"]}', flush=True)


if __name__ == "__main__":
    main()
