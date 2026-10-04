"""Verificacion LENTA de MA (bracket tolerante, V2 desde el primer intento) con el
motor real `TeqpVerificado`, FUERA de la suite normal.

Tarea `2026-10-02-tests-primero-ma`: NO toca `src/`. Llama a
`resolver_ciclo(..., bracket_tolerante=True)` y compara contra las columnas V2 de
`resultados/2026-10-01_ablacion_tiempos/ablacion_filas.csv` (`V2_eta`, `V2_clas`) para:
  * las 10 filas de control (`ctl_*`);
  * 8 filas RESCATADAS por V2 (2 de cada grupo `f2_T_from_Ph`, `lit_T_from_Ph`,
    `lit_bifasico`, `f2_h_Ps`; si un grupo no tiene 2 recuperadas, completa con la
    siguiente del mismo orden de grupos). "Rescatada" = el intento original V0 falla
    (`V0_eta` vacio) y V2 si converge (`V2_clas` != NO_CONVERGIO).
Criterio: `|Δη| < 1e-4` y misma clasificacion. Una linea de progreso por fila en
`resultados/2026-10-02_tests_ma/progreso.log` (con `flush`); un fallo en una fila NO
aborta las demas. La carga de parametros por fila se IMPORTA del script MB retirado
(`OBSOLETO_verificar_controles_reintento_MB.py`), no se reescribe.

Hoy debe FALLAR: `resolver_ciclo` todavia no acepta `bracket_tolerante`.

Uso:  .venv\\Scripts\\python scripts\\verificar_controles_ma.py
"""
from __future__ import annotations

import csv
import importlib.util
import sys
import time
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_RAIZ))

from src.cycle_solver import resolver_ciclo                      # noqa: E402
from src.properties.teqp_verificado import TeqpVerificado        # noqa: E402
from src.restricciones import evaluar_ciclo                       # noqa: E402

CSV_IN = _RAIZ / "resultados" / "2026-10-01_ablacion_tiempos" / "ablacion_filas.csv"
LOG_OUT = _RAIZ / "resultados" / "2026-10-02_tests_ma" / "progreso.log"
MB = _RAIZ / "resultados" / "2026-10-02_tests_ma" / "OBSOLETO_verificar_controles_reintento_MB.py"
DETA_ETA = 1e-4                        # tolerancia de eta contra la columna V2
GRUPOS = ("f2_T_from_Ph", "lit_T_from_Ph", "lit_bifasico", "f2_h_Ps")
POR_GRUPO, N_RESC = 2, 8               # 2 por grupo; 8 rescatadas en total


def _carga_MB():
    """Carga de parametros por fila del script MB (OBSOLETO): `_kw`, `_x_backend`,
    `COLS_CLASIF`. Se importa tal cual para no reescribirla ni divergir de ella."""
    spec = importlib.util.spec_from_file_location("verif_controles_reintento_MB", MB)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_MB = _carga_MB()
_kw, _x_backend, COLS_CLASIF = _MB._kw, _MB._x_backend, _MB.COLS_CLASIF


def _rescatadas(filas: list[dict]) -> list[dict]:
    """2 por grupo en orden; las que falten se toman de las sobrantes, tambien en
    orden de grupo (`f2_h_Ps` solo aporta 1: la 8a sale de `f2_T_from_Ph`)."""
    rec = [f for f in filas if not f["V0_eta"].strip()                # V0 falla
           and f["V2_clas"].strip() not in ("", "NO_CONVERGIO")]      # V2 lo rescata
    por = {g: [f for f in rec if f["grupo"] == g] for g in GRUPOS}
    sel = [f for g in GRUPOS for f in por[g][:POR_GRUPO]]              # 2 por grupo
    for g in GRUPOS:                                                  # completa N_RESC
        sel += [f for f in por[g][POR_GRUPO:] if len(sel) < N_RESC][:N_RESC - len(sel)]
    return sel[:N_RESC]


def _muestra() -> list[dict]:
    """10 controles + 8 rescatadas, con su referencia: SIEMPRE las columnas V2."""
    filas = list(csv.DictReader(CSV_IN.open(encoding="utf-8-sig")))
    out = [dict(f, tipo="control") for f in filas if f["grupo"].startswith("ctl_")]
    out += [dict(f, tipo="rescatada") for f in _rescatadas(filas)]
    faltan = [f["fila_csv"] for f in out if not f["V2_eta"].strip()]
    if faltan:
        raise SystemExit(f"filas sin V2_eta de referencia: {faltan}")
    return out


def main() -> None:
    muestra, t0 = _muestra(), time.perf_counter()
    LOG_OUT.parent.mkdir(parents=True, exist_ok=True)
    print(f"{len(muestra)} filas (10 controles + {N_RESC} rescatadas) desde {CSV_IN.name}")
    fallos, api = 0, 0
    with LOG_OUT.open("w", encoding="utf-8") as log:
        for n, f in enumerate(muestra, 1):
            ini, kw, xb = time.perf_counter(), _kw(f), _x_backend(f)
            prefijo = (f"{n}/{len(muestra)} {f['tipo']:9s} grupo={f['grupo']:14s} "
                       f"fila_csv={f['fila_csv']:>4s}")
            try:
                real = TeqpVerificado(x=xb)
                res = resolver_ciclo(real, **kw, bracket_tolerante=True)
                val = evaluar_ciclo(real, res, T_amb_diseno=float(f["T_amb_diseno"]),
                                    **{c: kw[c] for c in COLS_CLASIF})
                de, dcl = res["eta"] - float(f["V2_eta"]), val.clasificacion.value
                ok = abs(de) < DETA_ETA and dcl == f["V2_clas"]
                if not ok:
                    fallos += 1
                linea = (f"{prefijo} {'OK  ' if ok else 'MAL '} eta={res['eta']:.6f} "
                         f"d_eta={de:+.2e} clas={dcl} (ref {f['V2_clas']}) "
                         f"bracket={res.get('bracket')} [{time.perf_counter() - ini:.1f} s]")
            except Exception as exc:                      # incluye la API inexistente
                msg = str(exc).splitlines()[0][:150]
                if isinstance(exc, TypeError) and "bracket_tolerante" in msg:
                    api += 1
                fallos += 1
                linea = f"{prefijo} ERROR {type(exc).__name__}: {msg}"
            log.write(linea + "\n")
            log.flush()
            print(linea, flush=True)
    print(f"\n{len(muestra)} filas en {time.perf_counter() - t0:.0f} s "
          f"-> {LOG_OUT.relative_to(_RAIZ)}")
    if api:
        raise SystemExit(
            f"FALLO DE API: {api}/{len(muestra)} filas con TypeError; "
            f"`resolver_ciclo` todavia no acepta `bracket_tolerante=True` "
            f"(tests primero: implementacion pendiente).")
    if fallos:
        raise SystemExit(f"{fallos}/{len(muestra)} filas no reproducen las columnas V2.")
    print(f"OK: las {len(muestra)} filas reproducen `V2_eta` y `V2_clas` "
          f"(|Δη| < {DETA_ETA:g}).")


if __name__ == "__main__":
    main()