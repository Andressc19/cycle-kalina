"""Verificacion LENTA del reintento tolerante con el motor real (fuera de la suite).

Tarea `2026-10-01-tests-primero-reintento-tolerante`: no toca `src/` ni los tests.
Toma de `resultados/2026-09-30_arranque_solver/sonda_filas.csv`:
  * las 10 filas de control (`ctl_*`), que hoy ya resuelven sin reintento;
  * 5 filas RESCATADAS por el prototipo de la sonda (2 `f2_T_from_Ph`, 2
    `lit_T_from_Ph`, 1 `lit_bifasico`): filas donde el intento original falla
    (`V0_eta` vacio) y el prototipo V2 si converge (`V2_clas` != NO_CONVERGIO),
    tomadas en orden de CSV.
Para cada fila llama a `resolver_ciclo(..., reintento_tolerante=True)` con
`TeqpVerificado` y compara `eta` (|Δη| < 1e-4) y la clasificacion contra el CSV.
Referencia: controles -> `eta_original`/`clasificacion_original`; rescatadas ->
`V2_eta`/`V2_clas` (su `eta_original` esta vacio: antes no convergian).
Escribe una linea de progreso por fila en
`resultados/2026-10-01_tests_reintento/progreso.log`.

Hoy debe FALLAR: `resolver_ciclo` todavia no acepta `reintento_tolerante`.

Uso:  .venv\\Scripts\\python scripts\\verificar_controles_reintento.py
"""
from __future__ import annotations

import csv
import re
import sys
import time
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_RAIZ))

from src.cycle_solver import resolver_ciclo                      # noqa: E402
from src.properties.teqp_verificado import TeqpVerificado        # noqa: E402
from src.restricciones import evaluar_ciclo                       # noqa: E402

CSV_IN = _RAIZ / "resultados" / "2026-09-30_arranque_solver" / "sonda_filas.csv"
LOG_OUT = _RAIZ / "resultados" / "2026-10-01_tests_reintento" / "progreso.log"
COLS_SOLVER = ("x_b", "P_alta", "P_baja", "T_fuente", "T_sumidero", "m_b",
               "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond",
               "tol_T10", "max_iter_frio")
COLS_CLASIF = ("x_b", "P_alta", "P_baja", "T_fuente", "T_sumidero", "m_b",
               "eps_hrvg", "eps_reg", "eps_cond")
T_AMB, DETA_ETA = 303.55, 1e-4          # piso O2 de la sonda; tolerancia de eta
RESCATADAS = (("f2_T_from_Ph", 2), ("lit_T_from_Ph", 2), ("lit_bifasico", 1))


def _x_backend(fila: dict) -> float:
    """x del engine: la columna `backend` lo deja escrito ('TeqpVerificado(x=0.5)')."""
    return float(re.search(r"x=([0-9.]+)", fila["backend"]).group(1))


def _kw(fila: dict) -> dict:
    kw = {c: float(fila[c]) for c in COLS_SOLVER}
    kw["max_iter_frio"] = int(kw["max_iter_frio"])      # `range()` exige entero
    return kw


def _muestra() -> list[dict]:
    """10 controles + 5 rescatadas (2/2/1), con su referencia de eta y clase."""
    filas = list(csv.DictReader(CSV_IN.open(encoding="utf-8-sig")))
    out = []
    for f in filas:
        if f["grupo"].startswith("ctl_"):
            out.append(dict(f, eta_ref=float(f["eta_original"]),
                            clas_ref=f["clasificacion_original"], tipo="control"))
    for grupo, k in RESCATADAS:
        cand = [f for f in filas if f["grupo"] == grupo
                and not f["V0_eta"].strip()                 # el intento original falla
                and f["V2_clas"].strip() not in ("", "NO_CONVERGIO")]   # V2 lo rescata
        if len(cand) < k:
            raise SystemExit(f"faltan filas rescatadas en {grupo}: {len(cand)} < {k}")
        for f in cand[:k]:
            out.append(dict(f, eta_ref=float(f["V2_eta"]),
                            clas_ref=f["V2_clas"], tipo="rescatada"))
    return out


def main() -> None:
    muestra, t0 = _muestra(), time.perf_counter()
    LOG_OUT.parent.mkdir(parents=True, exist_ok=True)
    print(f"{len(muestra)} filas (10 controles + 5 rescatadas) desde {CSV_IN.name}")
    fallos, api, lineas = 0, 0, []
    with LOG_OUT.open("w", encoding="utf-8") as log:
        for n, f in enumerate(muestra, 1):
            ini, kw, xb = time.perf_counter(), _kw(f), _x_backend(f)
            prefijo = (f"{n}/{len(muestra)} {f['tipo']:9s} grupo={f['grupo']:14s} "
                       f"fila_csv={f['fila_csv']:>4s}")
            try:
                real = TeqpVerificado(x=xb)
                res = resolver_ciclo(real, **kw, reintento_tolerante=True)
                val = evaluar_ciclo(real, res, T_amb_diseno=T_AMB,
                                    **{c: kw[c] for c in COLS_CLASIF})
                de, dcl = res["eta"] - f["eta_ref"], val.clasificacion.value
                dcl = f"{dcl} (ref {f['clas_ref']})"
                ok = abs(de) < DETA_ETA and val.clasificacion.value == f["clas_ref"]
                if not ok:
                    fallos += 1
                linea = (f"{prefijo} {'OK  ' if ok else 'MAL '} "
                         f"eta={res['eta']:.6f} d_eta={de:+.2e} clas={dcl} "
                         f"reintento_usado={res.get('reintento_usado')} "
                         f"[{time.perf_counter() - ini:.1f} s]")
            except Exception as exc:                      # incluye la API inexistente
                msg = str(exc).splitlines()[0][:150]
                if isinstance(exc, TypeError) and "reintento_tolerante" in msg:
                    api += 1
                fallos += 1
                linea = f"{prefijo} ERROR {type(exc).__name__}: {msg}"
            log.write(linea + "\n")
            log.flush()
            lineas.append(linea)
            print(linea, flush=True)
    print(f"\n{len(muestra)} filas en {time.perf_counter() - t0:.0f} s "
          f"-> {LOG_OUT.relative_to(_RAIZ)}")
    if api:
        raise SystemExit(
            f"FALLO DE API: {api}/{len(muestra)} filas con TypeError; "
            f"`resolver_ciclo` todavia no acepta `reintento_tolerante=True` "
            f"(tests primero: implementacion pendiente).")
    if fallos:
        raise SystemExit(f"{fallos}/{len(muestra)} filas no reproduced el CSV.")
    print("OK: las 15 filas reproducen eta y clasificacion del CSV "
          f"(|Δη| < {DETA_ETA:g}).")


if __name__ == "__main__":
    main()