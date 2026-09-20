"""Fase 2 (tarea 2026-09-20-fase2-sensibilidad-final) — malla 2D parte C.

Malla 6×6 = 36 puntos en el plano P_baja × eps_cond (el par que gobierna
juntos el criterio O2/cavitacion), resto de variables fijas en el centro del
candidato base. Objetivo: mapear la frontera KALINA/CORREGIBLE como region
2D, no como dos lineas independientes.

Mismo trabajador que el OFAT: `comun.resolver_punto` con TeqpAdapter.
Salida: resultados/barridos_2026-09-19/fase2_libre/mapa_2d_pbaja_epscond.csv
con las columnas pedidas (P_baja, eps_cond, clasificacion, eta, O2_margen)
mas los margenes/diagnostico de los criterios ligantes y motor_confirmado
(None; lo rellena el spot-check con motor real). Checkpoint a nivel de
archivo: si el CSV ya existe, se reutiliza.

NO toca codigo de produccion; NO toca fase3_real/ ni fase1_profesor/.
"""

from __future__ import annotations

import importlib.util
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

from src.sensitivity import Barrido, Fijo, generar_combinaciones  # noqa: E402

CENTRO = dict(P_alta=3000.0, T_fuente=470.0, T_sumidero=300.032917, m_b=1.0,
              eta_t=0.85, eta_p=0.75, eps_hrvg=0.85, eps_reg=0.75,
              x_b=0.40)
P_BAJA_GRID = (400.0, 420.0, 440.0, 460.0, 480.0, 500.0)
EPS_COND_GRID = (0.85, 0.87, 0.89, 0.91, 0.93, 0.95)
CSV = (_RAIZ / "resultados" / "barridos_2026-09-19" / "fase2_libre"
       / "mapa_2d_pbaja_epscond.csv")
COLUMNAS = ("P_baja", "eps_cond", "clasificacion", "eta", "O2_margen",
            "T_sat_L", "T9_amb", "margen_O1", "margen_S5",
            "criterio_ligante", "margen_ligante", "motor_confirmado")
N_WORKERS = 4


def especificacion() -> dict:
    """Fijo/Barrido de las 11 variables: malla P_baja × eps_cond."""
    spec = {k: Fijo(v) for k, v in CENTRO.items()}
    spec["P_baja"] = Barrido(P_BAJA_GRID[0], P_BAJA_GRID[-1], 20.0)
    spec["eps_cond"] = Barrido(EPS_COND_GRID[0], EPS_COND_GRID[-1], 0.02)
    return spec


def main() -> None:
    combos = generar_combinaciones(especificacion())
    print(f"Malla 2D: {len(combos)} puntos TeqpAdapter "
          f"(P_baja {P_BAJA_GRID[0]:.0f}-{P_BAJA_GRID[-1]:.0f} × "
          f"eps_cond {EPS_COND_GRID[0]:.2f}-{EPS_COND_GRID[-1]:.2f}), "
          f"{N_WORKERS} workers...", flush=True)
    CSV.parent.mkdir(parents=True, exist_ok=True)
    if CSV.exists():
        df = pd.read_csv(CSV)
        if len(df) >= len(combos):
            print(f"  ya existe {CSV.name} ({len(df)} filas), se reutiliza")
            print(df["clasificacion"].value_counts().to_string())
            return
    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=N_WORKERS) as pool:
        filas = list(pool.map(comun.resolver_punto, combos))
    for f in filas:  # alias del CSV (spec): O2_margen = margen_O2 interno
        f["O2_margen"] = f["margen_O2"]
    tabla = pd.DataFrame({col: [f[col] for f in filas] for col in COLUMNAS})
    tabla = tabla.sort_values(["P_baja", "eps_cond"]).reset_index(drop=True)
    tabla.to_csv(CSV, index=False, encoding="utf-8")
    dt = time.perf_counter() - t0
    print(f"  {len(combos)} puntos en {dt:.0f} s "
          f"({dt / len(combos):.1f} s/pt)", flush=True)
    print(tabla["clasificacion"].value_counts().to_string())
    print(f"CSV guardado en {CSV}")


if __name__ == "__main__":
    main()