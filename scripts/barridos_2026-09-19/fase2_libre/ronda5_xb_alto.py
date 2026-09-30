"""Fase 2, ronda 5 (tarea 2026-09-29-fase2-ronda5-xb-alto) — runner del barrido
de x_b alto (0.70-0.85) con TeqpAdapter, checkpointing por lotes y registro en
DOS archivos:

  1. APPEND a `busqueda_libre_v2.csv` con el ESQUEMA REAL de 19 columnas (se lee
     la cabecera, nunca se asume). No se crea ningun CSV nuevo para el barrido.
  2. APPEND a `ronda5_diagnostico.csv` (companion NUEVO, solo de esta ronda) con
     los margenes de los CuATRO criterios con margen medible (O1, O2, S5, O5),
     el `criterio_ligante` y una bandera `al_filo_O1` (margen_O1 < 0.05).

Por que DOS archivos y no columnas nuevas en el historico: inyectar columnas
nuevas en `busqueda_libre_v2.csv` obligaria a reescribir las 797 filas de las
rondas 1-4 para ponerles NaN, y el TASK pide "append" y "mismo esquema de 19
columnas (lee la cabecera real)". El companion deja intacto el historico y
cumple igual el punto 7 (registrar margen_O1 de cada punto). Decision
documentada en el reporte.

Motor: TeqpAdapter para el grueso (TASK punto 8). El spot-check con motor real
va en `ronda5_spotcheck.py`.

Uso:  python ronda5_xb_alto.py {nivel1|nivel2|nivel3} [--presupuesto SEG]
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

_CARPETA = Path(__file__).resolve().parent
sys.path.insert(0, str(_CARPETA))


def _cargar(nombre: str):
    """Carga un modulo hermano por ruta (la carpeta lleva guiones)."""
    spec = importlib.util.spec_from_file_location(nombre, _CARPETA / f"{nombre}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sys.modules.setdefault(nombre, mod)
    return mod


comun = _cargar("comun_sensibilidad")
col = _cargar("ronda5_columnas")

DIAG = col.DIAG
DIAG_COLS = ("P_alta", "P_baja", "x_b", "eta_t", "eta_p", "eps_hrvg", "eps_reg",
             "eps_cond", "q4", "q2", "T_sat_L", "T9_amb", "margen_O1",
             "margen_O2", "margen_S5", "margen_O5", "criterio_ligante",
             "margen_ligante", "al_filo_O1", "convergio", "clasificacion",
             "eta", "mensaje")


def _worker(combo: dict) -> dict:
    """Un punto con TeqpAdapter. try/except ABIERTO: todo punto se registra.

    Igual que en la ronda 4, el diagnostico posterior a `resolver_ciclo`
    (`evaluar_ciclo`, `fase_de`, `bubble_point`, condensador con T_amb) tambien
    puede lanzar `PropertyRangeError`; sin el try/except abierto la excepcion
    sube por el pipe y tumba la tanda entera.
    """
    try:
        return comun.resolver_punto(combo, comun.importar_teqp)
    except Exception as exc:                                   # noqa: BLE001
        return dict(combo, convergio=False, clasificacion="NO_CONVERGIO",
                    eta=None, Wnet=None, mensaje=f"{type(exc).__name__}: {exc}"[:300])


def _fila_csv(r: dict) -> dict:
    """Mapea el dict del diagnostico al esquema de 19 columnas del historico."""
    f = {k: r.get(k) for k in col.ESQUEMA_CSV}
    f["O2_margen"] = r.get("margen_O2")
    return f


def _fila_diag(r: dict) -> dict:
    """Fila del companion: margenes de los 4 criterios + bandera de filo O1."""
    f = {k: r.get(k) for k in DIAG_COLS}
    m1 = r.get("margen_O1")
    f["al_filo_O1"] = (None if m1 is None
                       else bool(float(m1) >= 0.0 and float(m1) < 0.05))
    return f


def correr(nuevas: list, etiqueta: str, presupuesto: float) -> None:
    """Ejecuta `nuevas` con TeqpAdapter, 4 workers y checkpoint cada LOTE."""
    if not nuevas:
        print(f"[{etiqueta}] nada nuevo que correr.", flush=True)
        return
    cab = list(pd.read_csv(col.CSV, nrows=0).columns)
    tope = int(presupuesto / col.S_PT)
    if tope < len(nuevas):
        print(f"[{etiqueta}] presupuesto {presupuesto:.0f} s -> entran {tope} de "
              f"{len(nuevas)}; se recortan los ultimos {len(nuevas) - tope}.",
              flush=True)
        nuevas = nuevas[:tope]
    print(f"[{etiqueta}] {len(nuevas)} puntos TeqpAdapter, T_amb_diseno="
          f"{col.T_AMB_DISENO} K, {col.N_WORKERS} workers, checkpoint cada "
          f"{col.LOTE}; append a {col.CSV.name} ({len(cab)} col) + "
          f"{DIAG.name} ({len(DIAG_COLS)} col)", flush=True)
    t0, filas, diag = time.perf_counter(), [], []

    def guardar() -> None:
        if filas:
            pd.DataFrame(filas).reindex(columns=cab).to_csv(
                col.CSV, mode="a", header=False, index=False, encoding="utf-8")
            filas.clear()
        if diag:
            pd.DataFrame(diag).reindex(columns=DIAG_COLS).to_csv(
                DIAG, mode="a", header=not DIAG.exists(), index=False,
                encoding="utf-8")
            diag.clear()

    try:
        with ProcessPoolExecutor(max_workers=col.N_WORKERS) as pool:
            futs = [pool.submit(_worker, p) for p in nuevas]
            for n, fut in enumerate(as_completed(futs), 1):
                r = fut.result()
                filas.append(_fila_csv(r))
                diag.append(_fila_diag(r))
                if n % col.LOTE == 0 or n == len(nuevas):
                    guardar()
                    print(f"  [{etiqueta}] {n}/{len(nuevas)} guardados "
                          f"({time.perf_counter() - t0:.0f} s)", flush=True)
    finally:
        guardar()
    dt = time.perf_counter() - t0
    print(f"[{etiqueta}] fin: {len(nuevas)} puntos en {dt:.0f} s "
          f"({dt / max(len(nuevas), 1):.1f} s/punto).", flush=True)


def _nuevas(cand: list) -> list:
    """Filtra duplicados contra TODOS los CSV de fase2_libre + dentro de la tanda."""
    r2 = col.cargar_r2()
    probadas = r2.leer_probadas()
    unicas = {r2.tupla(c): c for c in cand}
    return [c for t, c in unicas.items() if t not in probadas], len(cand), len(unicas)


def main() -> None:
    ap = argparse.ArgumentParser(description="Barrido x_b alto, Fase 2 ronda 5")
    ap.add_argument("nivel", choices=("nivel1", "nivel2", "nivel3"))
    ap.add_argument("--presupuesto", type=float, default=5400.0,
                    help="segundos de pared disponibles para este nivel")
    args = ap.parse_args()
    cand = {"nivel1": col.nivel1, "nivel2": col.nivel2,
            "nivel3": col.nivel3}[args.nivel]()
    nuevas, n_cand, n_uni = _nuevas(cand)
    print(f"[{args.nivel}] candidatas: {n_cand} | repetidas dentro de la tanda: "
          f"{n_cand - n_uni} | ya probadas (rondas 1-5): {n_uni - len(nuevas)} | "
          f"nuevas: {len(nuevas)}", flush=True)
    correr(nuevas, args.nivel, args.presupuesto)


if __name__ == "__main__":
    main()
