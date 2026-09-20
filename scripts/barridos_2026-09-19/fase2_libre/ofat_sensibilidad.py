"""Fase 2 (tarea 2026-09-20-fase2-sensibilidad-final) — 5 barridos OFAT.

Parte B del entregable: 5 barridos de una variable a la vez (~7 puntos cada
uno, 33 en total) alrededor del candidato base confirmado con motor real
(P_alta=3000, P_baja=400, x_b=0.40, T_fuente=470.0, T_sumidero=300.032917,
eta_t=0.85, eta_p=0.75, eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.95,
T_amb_diseno=303.55; eta=0.124296 motor real, confirmacion_motor_real_v2.json).

El grueso del barrido usa EXCLUSIVAMENTE TeqpAdapter (instruccion del
director); el motor real queda reservado para los spot-checks selectivos del
script aparte. Las combinaciones se generan con `Fijo`/`Barrido` +
`generar_combinaciones` y la tabla base con `tabla_barrido` de src.sensitivity
(API validada, no modificada). No se llama a `ejecutar_barrido` tal cual
porque descarta el resultado/estados que se necesitan para los margenes
(misma razon por la que busqueda_libre_v2.py implementa su propio
resolver_punto). A cada fila se anexan los margenes O1/O2/S5/O5, el criterio
ligante con su margen y motor_confirmado=None (lo rellena el spot-check).

Salida (una por variable): resultados/barridos_2026-09-19/fase2_libre/
sensibilidad_<var>.csv — esquema tabla_barrido + COLUMNAS_DIAG.

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

from src.sensitivity import (Barrido, Fijo, generar_combinaciones,  # noqa: E402
                             tabla_barrido)

CENTRO = dict(P_alta=3000.0, T_fuente=470.0, T_sumidero=300.032917, m_b=1.0,
              eta_t=0.85, eta_p=0.75, eps_hrvg=0.85, eps_reg=0.75,
              P_baja=400.0, x_b=0.40, eps_cond=0.95)

# Variables del OFAT con sus rangos (FIN = centro; tope 0.99 de eps_hrvg es
# el bracket de la frontera S5, ver PRESCAN_EPS_HRVG.md).
BARRIDOS = {
    "x_b": Barrido(0.35, 0.45, 0.02),
    "P_baja": Barrido(400.0, 500.0, 20.0),
    "eps_cond": Barrido(0.85, 0.95, 0.02),
    "eta_t": Barrido(0.80, 0.90, 0.02),
    "eps_hrvg": Barrido(0.80, 0.99, 0.025),
}
SALIDAS = (_RAIZ / "resultados" / "barridos_2026-09-19" / "fase2_libre")


def especificacion(var: str) -> dict:
    """Especificacion Fijo/Barrido de las 11 variables para un barrido."""
    spec = {k: Fijo(v) for k, v in CENTRO.items()}
    spec[var] = BARRIDOS[var]
    return spec


def guardar(csv: Path, filas: list[dict]) -> None:
    base = tabla_barrido(filas)
    extra = pd.DataFrame(
        [{c: f.get(c) for c in comun.COLUMNAS_DIAG} for f in filas])
    pd.concat([base, extra], axis=1).to_csv(
        csv, index=False, encoding="utf-8")


def main() -> None:
    csvs, totex = {}, 0
    for var in BARRIDOS:
        csv = SALIDAS / f"sensibilidad_{var}.csv"
        csvs[var] = csv
        totex += len(generar_combinaciones(especificacion(var)))
    print(f"OFAT: {len(BARRIDOS)} barridos, {totex} puntos TeqpAdapter, "
          f"{csvs[list(BARRIDOS)[0]].parent}", flush=True)
    for var in BARRIDOS:
        csv = csvs[var]
        n = len(generar_combinaciones(especificacion(var)))
        if csv.exists():
            df = pd.read_csv(csv)
            print(f"  {var}: ya existe {csv.name} ({len(df)} filas), "
                  f"se reutiliza", flush=True)
            print(f"    {df['clasificacion'].value_counts().to_dict()}")
            continue
        t0 = time.perf_counter()
        combos = generar_combinaciones(especificacion(var))
        with ProcessPoolExecutor(max_workers=4) as pool:
            filas = list(pool.map(comun.resolver_punto, combos))
        guardar(csv, filas)
        df = pd.read_csv(csv)
        dt = time.perf_counter() - t0
        print(f"  {var} ({n} pts): "
              f"{df['clasificacion'].value_counts().to_dict()} | "
              f"KALINA eta medio={df.loc[df['clasificacion']=='KALINA','eta'].mean():.5f}"
              f" | {dt:.0f} s ({dt/n:.1f} s/pt) | {csv.name}", flush=True)
    print("OFAT terminado.", flush=True)


if __name__ == "__main__":
    main()