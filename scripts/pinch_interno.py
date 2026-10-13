"""Sonda de pinch interno (corrección 4): perfiles Q–T de regenerador, HRVG y
condensador de los puntos de `pinch_interno_muestra.seleccionar()`.

POST-PROCESO: resuelve cada punto con `resolver_ciclo` (sin tocar `src/`) y
discretiza los perfiles desde fuera. Sin caudales de gases ni fuente finita
(HRVG y condensador contra reservorios isotermos, H8).

Regenerador, en contracorriente, con f = fracción de Q desde el extremo
caliente (donde entra 5 y sale 1): T_c(f) = T(P_alta, h5 − f·(h5−h6), x5) y
T_f(f) = T(P_alta, h1 − f·(h1−h10), x_b). ΔT(f) = T_c − T_f; cruce si ΔT ≤ 0.

Modos de entorno: `PINCH_HUMO=1` (3 puntos teqp, salida en `humo/`),
`PINCH_N_WORKERS` (por defecto 6). Salida en `OUT`: `pinch_puntos.csv` y
`perfiles_todos.csv`, escritos con flush por punto.
"""
from __future__ import annotations

import csv, os, sys, time  # noqa: E401,E402
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parent
sys.path[:0] = [str(_RAIZ), str(_DIR), str(_DIR / "barrido_final")]

from comun import PRESUPUESTO_S  # noqa: E402
from pinch_interno_muestra import VARS, seleccionar  # noqa: E402

HUMO = os.environ.get("PINCH_HUMO") == "1"
N_WORKERS = int(os.environ.get("PINCH_N_WORKERS", "6"))
OUT = _RAIZ / "resultados" / "2026-10-13_pinch_interno" / ("humo" if HUMO else "")
N_REG, N_PERF = 100, 40          # tramos del regenerador / de HRVG y condensador
PINCH_ESTRECHO = 5.0             # K
PRESUPUESTO_REAL_S = 3000        # el motor real necesita ~1500 s por punto
CAMPOS = (["tag", "grupo", "motor"] + VARS +
          ["convergio", "eta", "Qreg_kW", "T1", "T5", "T6", "T10",
           "reg_pinch_K", "reg_pos_f", "reg_dT_caliente", "reg_dT_frio",
           "reg_n_fallos", "T2", "T9", "hrvg_acerc_K", "hrvg_min_K", "T_bub_alta",
           "T_dew_alta", "hrvg_T1_menos_Tbub", "hrvg_T2_menos_Tbub", "hrvg_hierve",
           "cond_acerc_K", "cond_min_K", "clase_pinch", "t_s", "mensaje"])
CAM_PERF = ["tag", "motor", "equipo", "f", "h", "T_caliente", "T_frio"]


def _T(backend, P, h, x):
    """T(P, h, x) o `None` si el motor no la evalúa (no inventa valores)."""
    try:
        return float(backend.T_from_Ph(P, h, x=x))
    except Exception:                                   # noqa: BLE001
        return None


def _perfiles(b, e, c):
    """Devuelve (filas de perfil, dict de resumen) para un ciclo resuelto."""
    h1, h5, h6, h10 = e["e1"].h, e["e5"].h, e["e6"].h, e["e10"].h
    h2, h8, h9 = e["e2"].h, e["e8"].h, e["e9"].h
    perf, dts, fallos = [], [], 0
    for i in range(N_REG + 1):
        f = i / N_REG
        hc, hf = h5 - f * (h5 - h6), h1 - f * (h1 - h10)
        tc = _T(b, c["P_alta"], hc, e["e5"].x)
        tf = _T(b, c["P_alta"], hf, c["x_b"])
        perf.append(("regenerador", f, hc, tc, tf))
        if tc is None or tf is None:
            fallos += 1
        else:
            dts.append((tc - tf, f))
    hr, co = [], []
    for i in range(N_PERF + 1):
        f = i / N_PERF
        t = _T(b, c["P_alta"], h1 + f * (h2 - h1), c["x_b"])
        hr.append(None if t is None else c["T_fuente"] - t)
        perf.append(("hrvg", f, h1 + f * (h2 - h1), c["T_fuente"], t))
        t = _T(b, c["P_baja"], h8 + f * (h9 - h8), c["x_b"])
        co.append(None if t is None else t - c["T_sumidero"])
        perf.append(("condensador", f, h8 + f * (h9 - h8), t, c["T_sumidero"]))
    mn = min(dts) if dts else (None, None)
    return perf, dict(
        reg_pinch_K=mn[0], reg_pos_f=mn[1], reg_n_fallos=fallos,
        reg_dT_caliente=e["e5"].T - e["e1"].T, reg_dT_frio=e["e6"].T - e["e10"].T,
        hrvg_min_K=min((v for v in hr if v is not None), default=None),
        cond_min_K=min((v for v in co if v is not None), default=None))


def _clase(r: dict) -> str:
    p = r["reg_pinch_K"]
    if p is None:
        return "NO_EVALUADO"
    neg = [r[k] for k in ("hrvg_min_K", "cond_min_K") if r[k] is not None and r[k] < 0]
    if p <= 0 or neg:
        return "CRUCE"
    return "SIN_CRUCE_ESTRECHO" if p < PINCH_ESTRECHO else "SIN_CRUCE_AMPLIO"


def _eval(p: dict):
    """UNA corrida (hijo del pool). Devuelve (fila, perfiles); nunca lanza."""
    from src.cycle_solver import resolver_ciclo
    from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter
    from src.properties.teqp_verificado import TeqpVerificado

    c = {v: p[v] for v in VARS}
    fila = dict.fromkeys(CAMPOS)
    fila.update(tag=p["tag"], grupo=p["grupo"], motor=p["motor"], **c)
    t0, perf = time.perf_counter(), []
    try:
        real = p["motor"] == "real"
        b = (AmmoniaWaterAdapter(x=c["x_b"]) if real else TeqpVerificado(x=c["x_b"]))
        res = resolver_ciclo(b, **c, bracket_tolerante=True,
                             presupuesto_s=PRESUPUESTO_REAL_S if real else PRESUPUESTO_S)
        e = res["estados"]
        perf, resumen = _perfiles(b, e, c)
        fila.update(resumen, convergio=True, eta=res["eta"], Qreg_kW=res["Qreg"],
                    T1=e["e1"].T, T2=e["e2"].T, T5=e["e5"].T, T6=e["e6"].T,
                    T9=e["e9"].T, T10=e["e10"].T,
                    hrvg_acerc_K=c["T_fuente"] - e["e2"].T,
                    cond_acerc_K=e["e9"].T - c["T_sumidero"])
        try:
            tb = b.bubble_point(c["P_alta"], c["x_b"])
            fila.update(T_bub_alta=tb, T_dew_alta=b.dew_point(c["P_alta"], c["x_b"]),
                        hrvg_T1_menos_Tbub=e["e1"].T - tb,
                        hrvg_T2_menos_Tbub=e["e2"].T - tb,
                        hrvg_hierve=bool(e["e2"].T > tb))
        except Exception as exc:                        # noqa: BLE001
            fila["mensaje"] = f"bub/dew: {type(exc).__name__}: {exc}"[:200]
    except Exception as exc:                            # noqa: BLE001
        fila.update(convergio=False, mensaje=f"{type(exc).__name__}: {exc}"[:300])
    fila["clase_pinch"] = _clase(fila) if fila["convergio"] else "NO_CONVERGIO"
    fila["t_s"] = time.perf_counter() - t0
    return fila, [dict(tag=p["tag"], motor=p["motor"], equipo=q[0], f=q[1], h=q[2],
                       T_caliente=q[3], T_frio=q[4]) for q in perf]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pts = sorted(seleccionar(), key=lambda p: p["motor"] != "real")  # real primero
    if HUMO:
        pts = [next(p for p in pts if p["grupo"] == g) for g in
               ("A_estrella", "elsayed", "estratificada")]
    total, n, t0 = len(pts), 0, time.perf_counter()
    print(f"pinch interno | N={total} | {N_WORKERS} workers -> {OUT}", flush=True)
    with open(OUT / "pinch_puntos.csv", "w", encoding="utf-8", newline="") as fh, \
         open(OUT / "perfiles_todos.csv", "w", encoding="utf-8", newline="") as fp:
        esc = csv.DictWriter(fh, fieldnames=CAMPOS)
        per = csv.DictWriter(fp, fieldnames=CAM_PERF)
        esc.writeheader(), per.writeheader()
        with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
            for fu in as_completed([ex.submit(_eval, p) for p in pts]):
                fila, perf = fu.result()
                esc.writerow(fila), per.writerows(perf)
                fh.flush(), fp.flush()
                n += 1
                print(f'[{n}/{total}] {fila["grupo"]} {fila["motor"]} '
                      f'{fila["clase_pinch"]} pinch={fila["reg_pinch_K"]} '
                      f'{fila["t_s"]:.0f}s', flush=True)
    print(f"fin: {total} puntos en {time.perf_counter() - t0:.0f} s -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
