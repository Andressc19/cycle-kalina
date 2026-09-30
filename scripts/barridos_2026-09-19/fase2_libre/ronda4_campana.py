"""Fase 2, ronda 4 (tarea 2026-09-28-fase2-ronda4-campana-3h) — runner de la
campana extendida (~3 h de computo).

Ejecuta los niveles de la campana de `ronda4_columnas.py` con TeqpAdapter
(unico motor permitido en esta ronda) y 4 workers, con CHECKPOINTING OBLIGATORIO:
cada LOTE puntos se hace append a busqueda_libre_v2.csv, de modo que si el
proceso se interrumpe no se pierde el trabajo ya hecho (leccion de la ronda de
sensibilidad final de Fase 2, donde un bug costo 18 min de motor real).

    nivel1  escalera gruesa de P_baja sobre las 59 columnas
    nivel2  refinamiento adaptativo dentro del bracket O2=0 mas ancho
    nivel3  segunda pasada de refinamiento (estrecha el bracket)
    informe  reporte final (`ronda4_informe.py`), sin correr motor

Anti-duplicado: reutiliza ronda2_pbaja.leer_probadas() (8-tuplo redondeado a 3
decimales, leido de TODOS los CSV de fase2_libre, incluidas las 184 filas de
las rondas 1-3) y descarta candidatas ya probadas o repetidas dentro de la
tanda, informando el conteo de cada descarte.

Salida: APPEND a resultados/barridos_2026-09-19/fase2_libre/busqueda_libre_v2.csv
con la cabecera REAL leida del archivo. NO crea CSVs nuevos. NO toca src/.

Uso:  python ronda4_campana.py {nivel1|nivel2|nivel3|informe}
      [--presupuesto SEG]   (segundos de pared disponibles para ese nivel)
"""

from __future__ import annotations

import argparse
import importlib.util
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

from ronda4_columnas import (CSV, LOTE, N_WORKERS, S_PT, T_AMB_DISENO,
                              cargar_r2, columnas, nivel1, refinado)


def cargar_informe():
    """ronda4_informe por ruta (la carpeta lleva guiones -> no importable)."""
    ruta = Path(__file__).resolve().parent / "ronda4_informe.py"
    spec = importlib.util.spec_from_file_location("ronda4_informe", ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _worker(combo: dict) -> dict:
    """Worker de proceso: TeqpAdapter + diagnostico O2.

    El worker tiene que ser una funcion de nivel de modulo (igual que
    `ronda3_malla_fina.resolver_punto`): con `spawn` de Windows no se puede
    pasar por el pipe una funcion creada con `importlib`, porque el hijo la
    des-picklea resolviendo `ronda2_pbaja.resolver_punto` y el objeto no es el
    mismo. Aqui se carga el modulo DENTRO del worker.

    Envuelve TODA la llamada en un try/except abierto. `resolver_punto` de la
    ronda 2 solo protege el `resolver_ciclo`; el diagnostico de O2 que viene
    despues (`evaluar_ciclo`, el condensador con T_amb y `bubble_point`) puede
    tambien lanzar `PropertyRangeError` en puntos extremos de la campana, y una
    excepcion ahi SUBE por el pipe y tumba la tanda entera. En la ronda 4 eso
    costo una tanda de 78 puntos: se registro el punto como NO_CONVERGIO con la
    excepcion real en `mensaje` en vez de perder la tanda (regla 3 de la ronda:
    todo punto se registra, converja o no).
    """
    try:
        return cargar_r2().resolver_punto(combo)
    except Exception as exc:                          # noqa: BLE001
        return dict(combo, T_sat_L=None, T9_amb=None, O2_margen=None,
                    convergio=False, clasificacion="NO_CONVERGIO", eta=None,
                    Wnet=None,
                    mensaje=f"{type(exc).__name__}: {exc}"[:300])


def correr(nuevas: list, etiqueta: str, presupuesto: float) -> None:
    """Ejecuta `nuevas` con TeqpAdapter, 4 workers, append por lotes de LOTE."""
    if not nuevas:
        print(f"[{etiqueta}] nada nuevo que correr.")
        return
    cab = list(pd.read_csv(CSV, nrows=0).columns)
    tope = int(presupuesto / S_PT)
    if tope < len(nuevas):
        print(f"[{etiqueta}] presupuesto {presupuesto:.0f} s -> entran {tope} de "
              f"{len(nuevas)} puntos; se recortan los ultimos "
              f"{len(nuevas) - tope}.", flush=True)
        nuevas = nuevas[:tope]
    if not nuevas:
        print(f"[{etiqueta}] nada nuevo que correr.")
        return
    print(f"[{etiqueta}] {len(nuevas)} puntos TeqpAdapter, "
          f"T_amb_diseno={T_AMB_DISENO} K, {N_WORKERS} workers, checkpoint "
          f"cada {LOTE}; append a {CSV.name} ({len(cab)} columnas).", flush=True)
    t0, filas = time.perf_counter(), []

    def guardar() -> None:
        """Vuelca el buffer al CSV. Se llama en cada checkpoint y en el
        `finally`, para que una excepcion a media tanda no tire por tierra los
        puntos ya calculados que todavia no habian salido del buffer."""
        if filas:
            pd.DataFrame(filas).reindex(columns=cab).to_csv(
                CSV, mode="a", header=False, index=False, encoding="utf-8")
            filas.clear()

    try:
        with ProcessPoolExecutor(max_workers=N_WORKERS) as pool:
            futs = [pool.submit(_worker, p) for p in nuevas]
            for n, fut in enumerate(as_completed(futs), 1):
                filas.append(fut.result())
                if n % LOTE == 0 or n == len(nuevas):
                    guardar()
                    print(f"  [{etiqueta}] {n}/{len(nuevas)} guardados "
                          f"({time.perf_counter() - t0:.0f} s)", flush=True)
    finally:
        guardar()
    dt = time.perf_counter() - t0
    print(f"[{etiqueta}] fin: {len(nuevas)} puntos en {dt:.0f} s de pared "
          f"({dt / len(nuevas):.1f} s/punto, 4 workers en paralelo).", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="Campana extendida Fase 2, ronda 4")
    ap.add_argument("nivel", choices=("nivel1", "nivel2", "nivel3", "informe"))
    ap.add_argument("--presupuesto", type=float, default=3600.0,
                    help="segundos de pared disponibles para este nivel")
    args = ap.parse_args()
    if args.nivel == "informe":
        cargar_informe().informe()
        return
    r2 = cargar_r2()
    cand = nivel1() if args.nivel == "nivel1" else refinado()
    probadas = r2.leer_probadas()
    unicas = {r2.tupla(c): c for c in cand}
    nuevas = [c for t, c in unicas.items() if t not in probadas]
    print(f"[{args.nivel}] candidatas: {len(cand)} | repetidas dentro de la "
          f"tanda: {len(cand) - len(unicas)} | ya probadas (rondas 1-4): "
          f"{len(unicas) - len(nuevas)} | nuevas: {len(nuevas)}", flush=True)
    correr(nuevas, args.nivel, args.presupuesto)


if __name__ == "__main__":
    main()
