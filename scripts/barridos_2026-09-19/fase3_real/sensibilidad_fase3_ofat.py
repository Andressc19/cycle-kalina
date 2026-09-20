"""Fase 3 (Husavik) — 5 barridos OFAT de sensibilidad FINAL (TeqpAdapter).

Tarea 2026-09-20-fase3-sensibilidad-final. Un barrido a la vez, el resto de
variables fijas en el ancla confirmada (eta=0.12730, motor real):

  P_baja : 600 - 800 kPa      eps_cond: 0.90 - 0.99
  eps_reg: 0.75 - 0.95        x_b     : 0.78 - 0.86
  eta_t  : 0.85 - 0.95        (7 puntos c/u, cerrando el rango)

Se usa Fijo/Barrido + generar_combinaciones de src/sensitivity.py (API
validada; ver nota en sensibilidad_fase3_comun.py sobre por que no se llama a
ejecutar_barrido: T_amb_diseno=283.15 es obligatorio para Husavik).

Salida: resultados/barridos_2026-09-19/fase3_real/sensibilidad_<var>.csv
(esquema tabla_barrido + margenes O1/O2/S5 + criterio_ligante + spot_check).
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

BARRIDOS = [
    ("P_baja", Barrido(600.0, 800.0, 200.0 / 6)),
    ("eps_cond", Barrido(0.90, 0.99, 0.09 / 6)),
    ("eps_reg", Barrido(0.75, 0.95, 0.20 / 6)),
    ("x_b", Barrido(0.78, 0.86, 0.08 / 6)),
    ("eta_t", Barrido(0.85, 0.95, 0.10 / 6)),
]


def correr_barrido(var: str, spec: Barrido) -> pd.DataFrame:
    """Resuelve los ~7 puntos del barrido OFAT de `var` (resto en el ancla)."""
    variables = {k: Fijo(v) for k, v in comun.CENTRO.items()}
    variables[var] = spec
    combos = generar_combinaciones(variables)
    print(f"\nBarrido OFAT {var}: {len(combos)} puntos "
          f"[{combos[0][var]:.4g} .. {combos[-1][var]:.4g}] "
          f"(centro en el ancla)", flush=True)
    filas = []
    for n, combo in enumerate(combos, 1):
        fila = comun.resolver_punto(combo)
        filas.append(fila)
        print(f"  {n:02d}/{len(combos)} {var}={combo[var]:.4g} -> "
              f"{fila['clasificacion']:<16} eta={fila['eta']:.5f} "
              f"ligante={fila['criterio_ligante']} "
              f"margen={fila['margen_ligante']:.3f} "
              f"spot={fila['spot_check']}", flush=True)
    return pd.DataFrame(filas)


def main() -> None:
    print("Sensibilidad FINAL Fase 3 (Husavik) — 5 barridos OFAT, "
          "TeqpAdapter, T_amb_diseno=283.15 K", flush=True)
    total = 0
    for var, spec in BARRIDOS:
        df = correr_barrido(var, spec)
        comun.guardar(df, RESULTADOS / f"sensibilidad_{var}.csv")
        total += len(df)
    print(f"\nTotal puntos OFAT: {total}", flush=True)


if __name__ == "__main__":
    main()