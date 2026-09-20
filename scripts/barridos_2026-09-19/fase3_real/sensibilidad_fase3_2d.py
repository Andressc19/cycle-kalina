"""Fase 3 (Husavik) — malla 2D P_baja x eps_reg, sensibilidad FINAL.

Tarea 2026-09-20-fase3-sensibilidad-final. El par critico de O2 en este caso:
P_baja manda en la frontera KALINA/CORREGIBLE y eps_reg tambien la mueve en
algunos puntos. Malla 6x6 = 36 puntos (TeqpAdapter, resto en el ancla):

  P_baja : 600, 640, 680, 720, 760, 800 kPa
  eps_reg: 0.75, 0.79, 0.83, 0.87, 0.91, 0.95

Salida: resultados/barridos_2026-09-19/fase3_real/mapa_2d_pbaja_epsreg.csv
(columnas P_baja, eps_reg + esquema tabla_barrido + margenes + spot_check).
NO modifica codigo de produccion. NO toca fase2_libre/ (tarea paralela).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd

_RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_RAIZ))

_RUTA_COMUN = Path(__file__).with_name("sensibilidad_fase3_comun.py")
_spec = importlib.util.spec_from_file_location("sensibilidad_fase3_comun",
                                               _RUTA_COMUN)
comun = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(comun)
sys.modules["sensibilidad_fase3_comun"] = comun

from src.sensitivity import Barrido, Fijo, generar_combinaciones  # noqa: E402

RESULTADOS = _RAIZ / "resultados" / "barridos_2026-09-19" / "fase3_real"

# Columnas pedidas por la tarea primero; el resto del esquema comun despues.
COLUMNAS_MAPA = ["P_baja", "eps_reg"] + [
    c for c in comun.COLUMNAS if c not in ("P_baja", "eps_reg")]


def main() -> None:
    variables = {k: Fijo(v) for k, v in comun.CENTRO.items()}
    variables["P_baja"] = Barrido(600.0, 800.0, 40.0)   # 6 puntos
    variables["eps_reg"] = Barrido(0.75, 0.95, 0.04)    # 6 puntos
    combos = generar_combinaciones(variables)
    print(f"Malla 2D P_baja x eps_reg: {len(combos)} puntos "
          f"(6x6, TeqpAdapter, T_amb_diseno={comun.T_AMB_DISENO} K)",
          flush=True)
    filas = []
    for n, combo in enumerate(combos, 1):
        fila = comun.resolver_punto(combo)
        filas.append(fila)
        print(f"  {n:02d}/{len(combos)} P_baja={combo['P_baja']:.0f} "
              f"eps_reg={combo['eps_reg']:.2f} -> {fila['clasificacion']:<16} "
              f"eta={fila['eta']:.5f} O2_margen={fila['margen_O2']:.3f} "
              f"spot={fila['spot_check']}", flush=True)
    df = pd.DataFrame(filas)[COLUMNAS_MAPA]
    ruta = RESULTADOS / "mapa_2d_pbaja_epsreg.csv"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False, encoding="utf-8")
    conteo = df["clasificacion"].value_counts().to_dict()
    print(f"  guardado {ruta} ({len(df)} filas): {conteo}", flush=True)


if __name__ == "__main__":
    main()