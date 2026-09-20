"""Fase 3 (Husavik) — confirmacion selectiva con motor REAL.

Tarea 2026-09-20-fase3-sensibilidad-final. Para cada punto de los barridos
(OFAT + malla 2D) marcado en el CSV como `spot_check` (margen del criterio
ligante a menos de ~1-2 K del borde, o 0.02 en q4), se re-resuelve el punto
con AmmoniaWaterAdapter (iapws G4-01) y se escribe la columna
`motor_confirmado` (True si el motor real da la misma clasificacion, False si
discrepa, vacio si no se reviso).

Reglas:
- Se deduplica por combinacion de las 11 variables (el mismo punto aparece en
  varios barridos; no se gasta presupuesto del motor real dos veces con el
  mismo combo).
- Tope duro MAX_MOTOR_REAL=10 puntos (presupuesto del TASK_CONTEXT); si hay
  mas candidatos, se quedan los mas cerca de su borde (|margen_ligante| menor)
  y el resto queda sin confirmar (se reporta el descarte).
- El ancla YA esta confirmada (eta=0.12730, citada) y no se re-corre.

Salida: columnas motor_* escritas de vuelta en los CSVs + resumen_fase3.json.
NO modifica codigo de produccion. NO toca fase2_libre/ (tarea paralela).
"""

from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

import pandas as pd

_RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_RAIZ))

from src.cycle_solver import CicloNoConvergeError, resolver_ciclo
from src.properties.adapter import PropertyRangeError
from src.restricciones import evaluar_ciclo

_RUTA_COMUN = Path(__file__).with_name("sensibilidad_fase3_comun.py")
_spec = importlib.util.spec_from_file_location("sensibilidad_fase3_comun",
                                               _RUTA_COMUN)
comun = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(comun)
sys.modules["sensibilidad_fase3_comun"] = comun

RESULTADOS = _RAIZ / "resultados" / "barridos_2026-09-19" / "fase3_real"
MAX_MOTOR_REAL = 10

RUTAS = ["P_baja", "eps_cond", "eps_reg", "x_b", "eta_t", "2d_pbaja_epsreg"]


def resolver_motor_real(combo: dict) -> dict:
    """Resuelve + clasifica un punto con AmmoniaWaterAdapter (~4 min)."""
    from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter
    backend = AmmoniaWaterAdapter(x=combo["x_b"])
    try:
        resultado = resolver_ciclo(backend, **combo)
    except (CicloNoConvergeError, PropertyRangeError) as exc:
        return dict(convergio=False, clasificacion="NO_CONVERGIO",
                    eta=None, mensaje=str(exc)[:200])
    try:
        val = evaluar_ciclo(backend, resultado, P_alta=combo["P_alta"],
                            P_baja=combo["P_baja"], T_fuente=combo["T_fuente"],
                            T_sumidero=combo["T_sumidero"], x_b=combo["x_b"],
                            m_b=combo["m_b"], eps_hrvg=combo["eps_hrvg"],
                            eps_reg=combo["eps_reg"],
                            eps_cond=combo["eps_cond"],
                            T_amb_diseno=comun.T_AMB_DISENO)
    except PropertyRangeError as exc:
        return dict(convergio=False, clasificacion="NO_CONVERGIO",
                    eta=None, mensaje=f"evaluador O2 fuera de dominio: {exc}")
    return dict(convergio=True, clasificacion=val.clasificacion.value,
                eta=resultado["eta"], mensaje=val.mensaje_reporte()[:200])


def main() -> None:
    # Recolectar candidatos spot_check por combinacion unica de variables.
    por_combo: dict[tuple, list[tuple[Path, int]]] = {}
    for nombre in RUTAS:
        nombre_csv = ("mapa_2d_pbaja_epsreg.csv" if nombre.startswith("2d")
                      else f"sensibilidad_{nombre}.csv")
        ruta = RESULTADOS / nombre_csv
        if not ruta.exists():
            raise SystemExit(f"falta {ruta}; correr primero el barrido")
        df = pd.read_csv(ruta)
        for idx, fila in df.iterrows():
            if not bool(fila["spot_check"]):
                continue
            key = tuple(float(fila[v]) for v in comun.VARIABLES)
            por_combo.setdefault(key, []).append((ruta, idx))

    # Tope duro: a igualdad de regla, quedan los mas cerca del borde.
    def _margen(kv):
        ruta_0, idx_0 = kv[1][0]
        df_0 = pd.read_csv(ruta_0)
        return abs(df_0.at[idx_0, "margen_ligante"])

    orden = sorted(por_combo.items(), key=_margen)
    seleccion, descartados = orden[:MAX_MOTOR_REAL], orden[MAX_MOTOR_REAL:]
    print(f"Candidatos spot_check: {len(orden)} combos unicos; se confirman "
          f"{len(seleccion)} con motor real "
          f"(tope {MAX_MOTOR_REAL}); {len(descartados)} descartados por "
          f"presupuesto", flush=True)

    with open(RESULTADOS / "confirmacion_motor_real_690.json",
              encoding="utf-8") as f:
        eta_ancla = round(json.load(f)["puntos"][0]["eta"], 5)

    # Leer una vez cada CSV y acumular actualizaciones por (ruta, idx).
    rutas_a_editar = {rut for _, destinos in seleccion for rut, _ in destinos}
    dfs = {ruta: pd.read_csv(ruta) for ruta in rutas_a_editar}
    # Columnas aun sin confirmar leen como float64 (todo NaN) en pandas;
    # pasarlas a object para poder escribir string/bool/None sin cast fallido.
    for df in dfs.values():
        for col in ("motor_confirmado", "motor_real_clasificacion",
                    "motor_real_eta"):
            df[col] = df[col].astype(object)
    actualizados: dict[tuple[Path, int], tuple[str, str | None, float | None]] \
        = {}

    confirmados = 0
    for key, destinos in seleccion:
        combo = dict(zip(comun.VARIABLES, key))
        t0 = time.perf_counter()
        res = resolver_motor_real(combo)
        dt = time.perf_counter() - t0
        # La clasificacion de referencia (Teqp): unica por combo en todos
        # los CSVs (mismo punto, mismos numeros).
        ruta_ref, idx_ref = destinos[0]
        clas_teqp = dfs[ruta_ref].at[idx_ref, "clasificacion"]
        coincide = res["clasificacion"] == clas_teqp
        for ruta, idx in destinos:
            actualizados[(ruta, idx)] = (res["clasificacion"], res["eta"],
                                         bool(coincide))
        print(f"  P_baja={combo['P_baja']:.1f} eps_reg={combo['eps_reg']:.2f} "
              f"eps_cond={combo['eps_cond']:.3f} x_b={combo['x_b']:.4f} "
              f"-> Teqp={clas_teqp} / real={res['clasificacion']} "
              f"(eta={res['eta']:.5f}, {dt:.0f} s) "
              f"confirmado={coincide}", flush=True)
        confirmados += int(coincide)

    for (ruta, idx), (clas_real, eta_real, ok) in actualizados.items():
        df = dfs[ruta]
        df.at[idx, "motor_real_clasificacion"] = clas_real
        df.at[idx, "motor_real_eta"] = eta_real
        df.at[idx, "motor_confirmado"] = ok
    for ruta, df in dfs.items():
        df.to_csv(ruta, index=False, encoding="utf-8")
    print(f"Confirmaciones con motor real: {confirmados}/{len(seleccion)} "
          f"coinciden con Teqp", flush=True)

    leccion = (f"P_baja y eps_cond gobiernan el margen O2; del ancla 690 kPa "
               f"hacia abajo la frontera KALINA/CORREGIBLE se cruza "
               f"rapidamente y {confirmados}/{len(seleccion)} puntos de borde "
               f"se confirmaron igual con motor real (eta_ancla={eta_ancla}).")
    resumen = {"fase": "3_husavik", "clasificacion_ancla": "KALINA",
               "eta_ancla": eta_ancla, "leccion_aprendida": leccion}
    with open(RESULTADOS / "resumen_fase3.json", "w", encoding="utf-8") as f:
        json.dump(resumen, f, indent=2, ensure_ascii=False)
    print(f"guardado {RESULTADOS / 'resumen_fase3.json'}", flush=True)


if __name__ == "__main__":
    main()