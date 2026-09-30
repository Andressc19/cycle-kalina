"""Fase 2 (tarea 2026-09-20-fase2-sensibilidad-final) — spot-checks selectivos
con el motor REAL (AmmoniaWaterAdapter).

Regla (TASK §3): solo se re-resuelven con el motor real los puntos (de los 5
OFAT o de la malla) cuyo margen del criterio que decide la clasificacion
(O1: q4-0.90, O2: T_sat_L-T9_amb, S5: T_fuente-T2, O5: margen de q2) este a
menos del umbral (~1-2 K, o 0.02 en q2/q4). Presupuesto: <=10 puntos motor
real. Si hay mas candidatos que el tope, se revisan primero los mas cercanos
al borde y el exceso queda documentado en el JSON.

Salidas:
- columna `motor_confirmado` (True si el motor real da la misma clasificacion,
  False si difiere, None si no aplicaba) escrita en cada CSV correspondiente;
- detalle en resultados/barridos_2026-09-19/fase2_libre/
  spotcheck_motor_real_fase2.json.

NO toca codigo de produccion; NO toca fase3_real/ ni fase1_profesor/.
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pandas as pd

_RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_RAIZ))

_CARPETA = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location(
    "comun_sensibilidad", _CARPETA / "comun_sensibilidad.py")
comun = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(comun)
sys.modules.setdefault("comun_sensibilidad", comun)  # pickling en pool (spawn)

from src.sensitivity import VARIABLES_BARRIBLES  # noqa: E402

VARS_OFAT = ("x_b", "P_baja", "eps_cond", "eta_t", "eps_hrvg")
FASE2 = _RAIZ / "resultados" / "barridos_2026-09-19" / "fase2_libre"
MALLA_CSV = FASE2 / "mapa_2d_pbaja_epscond.csv"
JSON_OUT = FASE2 / "spotcheck_motor_real_fase2.json"
CENTRO_MALLA = dict(P_alta=3000.0, T_fuente=470.0, T_sumidero=300.032917,
                    m_b=1.0, eta_t=0.85, eta_p=0.75, eps_hrvg=0.85,
                    eps_reg=0.75, x_b=0.40, eps_cond=0.95)
MAX_SPOT = 10
N_WORKERS = 4


def combo_de_fila(csv_nombre: str, fila: dict) -> dict:
    """Reconstruye el combo de las 11 variables de una fila (OFAT o malla)."""
    if csv_nombre.startswith("sensibilidad_"):
        return {k: float(fila[k]) for k in VARIABLES_BARRIBLES}
    combo = dict(CENTRO_MALLA)
    combo["P_baja"] = float(fila["P_baja"])
    combo["eps_cond"] = float(fila["eps_cond"])
    return combo


def _num(v) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return float("nan")


def margenes_de_fila(fila: dict) -> dict:
    """Margenes desde las columnas del CSV (sin re-resolver el punto)."""
    return dict(margen_O1=_num(fila.get("margen_O1")),
                margen_O2=_num(fila.get("margen_O2",
                                        fila.get("O2_margen"))),
                margen_S5=_num(fila.get("margen_S5")),
                margen_O5=_num(fila.get("margen_O5")))


def _necesita(fila: dict) -> bool:
    """¿En el umbral de la frontera decisiva y aun sin confirmar?"""
    mc = fila.get("motor_confirmado")
    if mc is not None and not pd.isna(mc):
        return False  # ya confirmado
    return bool(comun.spot_necesario(fila["clasificacion"],
                                     fila["criterio_ligante"],
                                     margenes_de_fila(fila)))


def candidatos() -> list[dict]:
    """Filas de todos los CSVs cuyo margen ligante esta dentro del umbral."""
    out = []
    for var in VARS_OFAT:
        csv = FASE2 / f"sensibilidad_{var}.csv"
        if not csv.exists():
            continue
        for i, fila in pd.read_csv(csv).iterrows():
            f = fila.to_dict()
            if _necesita(f):
                f["_csv"], f["_idx"] = csv.name, i
                out.append(f)
    if MALLA_CSV.exists():
        for i, fila in pd.read_csv(MALLA_CSV).iterrows():
            f = fila.to_dict()
            if _necesita(f):
                f["_csv"], f["_idx"] = MALLA_CSV.name, i
                out.append(f)
    return out


def main() -> None:
    c = candidatos()
    con_margen = [f for f in c
                  if not (f.get("margen_ligante") is None
                          or (isinstance(f.get("margen_ligante"), float)
                              and math.isnan(f["margen_ligante"])))]
    print(f"Spot-check: {len(con_margen)} candidatos de {len(c)} en el "
          f"umbral con margen medible; tope motor real {MAX_SPOT}",
          flush=True)
    con_margen.sort(key=lambda f: abs(float(f["margen_ligante"])))
    for f in con_margen:
        print(f"  {f['_csv']} fila {f['_idx']}: {f['clasificacion']} via "
              f"{f['criterio_ligante']} margen {f['margen_ligante']:+.3f}",
              flush=True)
    elegidos = con_margen[:MAX_SPOT]
    if len(con_margen) > MAX_SPOT:
        print(f"  AVISO: {len(con_margen)} candidatos > tope; se revisan los "
              f"{MAX_SPOT} mas cercanos al borde.", flush=True)

    detalles = []
    if elegidos:
        t0 = time.perf_counter()
        with ProcessPoolExecutor(max_workers=N_WORKERS) as pool:
            futuros = [(f, pool.submit(comun.resolver_punto,
                                       combo_de_fila(f["_csv"], f),
                                       comun.importar_real))
                       for f in elegidos]
        for f, fut in futuros:
            t1 = time.perf_counter()
            real = fut.result()
            mismo = (f["clasificacion"] == real["clasificacion"])
            detalle = dict(
                csv=f["_csv"], fila_idx=f["_idx"],
                combo=combo_de_fila(f["_csv"], f),
                clasificacion_teqp=f["clasificacion"],
                clasificacion_real=real["clasificacion"],
                motor_confirmado=bool(mismo),
                eta_real=real["eta"],
                margen_ligante=f["margen_ligante"],
                tiempo_s=round(time.perf_counter() - t1, 1))
            detalles.append(detalle)
            # Checkpoint incremental: cada punto se persiste al terminar,
            # para que un corte no pierda el trabajo ya hecho.
            _checkpoint_json(detalle, con_margen, MAX_SPOT)
            for var in VARS_OFAT:
                csv = FASE2 / f"sensibilidad_{var}.csv"
                if csv.exists():
                    _escribir_motor(csv, [detalle])
            if MALLA_CSV.exists():
                _escribir_motor(MALLA_CSV, [detalle])
            print(f"  {f['_csv']} fila {f['_idx']}: teqp="
                  f"{f['clasificacion']} -> real={real['clasificacion']} "
                  f"confirmado={mismo} ({detalle['tiempo_s']:.0f} s)",
                  flush=True)
        print(f"  {len(elegidos)} puntos motor real en "
              f"{time.perf_counter() - t0:.0f} s", flush=True)

    # Reescritura final (idempotente): consolida en los CSVs y el JSON.
    for var in VARS_OFAT:
        csv = FASE2 / f"sensibilidad_{var}.csv"
        if csv.exists():
            _escribir_motor(csv, detalles)
    if MALLA_CSV.exists():
        _escribir_motor(MALLA_CSV, detalles)
    resumen = dict(T_amb_diseno=comun.T_AMB_DISENO, tope_motor_real=MAX_SPOT,
                   puntos=detalles,
                   exceso=[dict(csv=f["_csv"], fila_idx=f["_idx"],
                                clasificacion=f["clasificacion"],
                                criterio=f["criterio_ligante"],
                                margen=f["margen_ligante"])
                           for f in con_margen[MAX_SPOT:]])
    with open(JSON_OUT, "w", encoding="utf-8") as fh:
        json.dump(resumen, fh, indent=2, ensure_ascii=False)
    print(f"Guardado {JSON_OUT}")


def _checkpoint_json(detalle: dict, con_margen: list, tope: int) -> None:
    """Append de un punto al JSON (idempotente por csv+fila_idx)."""
    prev = {"puntos": [], "exceso": []}
    if JSON_OUT.exists():
        try:
            prev = json.loads(JSON_OUT.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            prev = {"puntos": [], "exceso": []}
    prev["T_amb_diseno"] = comun.T_AMB_DISENO
    prev["tope_motor_real"] = tope
    prev["puntos"] = [p for p in prev["puntos"]
                      if not (p["csv"] == detalle["csv"]
                              and p["fila_idx"] == detalle["fila_idx"])]
    prev["puntos"].append(detalle)
    prev["exceso"] = [dict(csv=f["_csv"], fila_idx=f["_idx"],
                           clasificacion=f["clasificacion"],
                           criterio=f["criterio_ligante"],
                           margen=f["margen_ligante"])
                      for f in con_margen[tope:]]
    with open(JSON_OUT, "w", encoding="utf-8") as fh:
        json.dump(prev, fh, indent=2, ensure_ascii=False)


def _escribir_motor(csv: Path, detalles: list[dict]) -> None:
    df = pd.read_csv(csv)
    if "motor_confirmado" not in df:
        df["motor_confirmado"] = None
    df["motor_confirmado"] = df["motor_confirmado"].astype(object)
    idx = [d["fila_idx"] for d in detalles if d["csv"] == csv.name]
    val = [d["motor_confirmado"] for d in detalles if d["csv"] == csv.name]
    for i, v in zip(idx, val):
        if 0 <= i < len(df):
            df.loc[i, "motor_confirmado"] = v
    df.to_csv(csv, index=False, encoding="utf-8")
    print(f"  motor_confirmado actualizado en {csv.name}")


if __name__ == "__main__":
    main()