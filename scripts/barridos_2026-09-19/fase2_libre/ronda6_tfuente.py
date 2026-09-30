"""Fase 2, ronda 6 (tarea 2026-09-29-fase2-ronda6-tfuente-libre-xb-alto) — runner
de T_fuente libre (380-500 K) x x_b alto (0.70-0.85) x P_alta libre (2800-4500).
Motor: TeqpAdapter para el grueso (TASK constraint 4); el spot-check con motor
real va en `ronda6_spotcheck.py` (AmmoniaWaterAdapter / IAPWS G4-01).
Registra en DOS archivos, igual que la ronda 5: (1) APPEND a
`busqueda_libre_v2.csv` con el ESQUEMA REAL de 19 columnas (se lee la cabecera,
nunca se asume; no se crea ningun CSV nuevo para el barrido) y (2) APPEND a
`ronda6_diagnostico.csv` (companion NUEVO) con los margenes de los cuatro
criterios con margen medible (O1, O2, S5, O5), el `criterio_ligante`, la bandera
`al_filo_O1` y — nuevo de esta ronda — el FILTRO DE CAMPANA (T_bub, T_dew,
estado_filtro). Por que dos archivos: inyectar columnas en el historico
obligaria a reescribir las 945 filas de las rondas 1-5 para ponerles NaN, y el
TASK pide "append" con las 19 columnas reales.
Subcomandos: filtro (campana, sin motor) | nivel1 (escalera de rho) | nivel2
(refina el bracket O2) | nivel3 (palanecas en la frontera O2). CHECKPOINTING
por lotes (leccion de la ronda 4): cada LOTE sale por append a los dos CSV, de
modo que una interrupcion no pierde lo ya calculado. Todo punto se registra,
converja o no (TASK constraint 3).
Uso: python ronda6_tfuente.py {filtro|nivel1|nivel2|nivel3} [--presupuesto SEG]
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
import time
from collections import Counter
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
col = _cargar("ronda6_columnas")
DIAG, DIAG_COLS = col.DIAG, col.DIAG_COLS


def _worker(combo: dict) -> dict:
    """Un punto con TeqpAdapter. try/except ABIERTO: todo punto se registra.
    Como en las rondas 4 y 5, el diagnostico posterior a `resolver_ciclo`
    (`evaluar_ciclo`, `fase_de`, `bubble_point`, condensador con T_amb) tambien
    puede lanzar `PropertyRangeError`; sin el try/except tumba la tanda entera.
    Las 3 claves del FILTRO (T_bub, T_dew, estado_filtro) van al companion pero
    NO son entradas del ciclo (el solver es de kwargs y las rechaza): se extraen."""
    filtro = {k: combo.pop(k) for k in ("T_bub", "T_dew", "estado_filtro")
              if k in combo}          # no son entradas del ciclo
    try:
        r = comun.resolver_punto(combo, comun.importar_teqp)
    except Exception as exc:                                   # noqa: BLE001
        r = dict(combo, convergio=False, clasificacion="NO_CONVERGIO", eta=None,
                 Wnet=None, mensaje=f"{type(exc).__name__}: {exc}"[:300])
    return dict(r, **filtro)


def _fila_csv(r: dict) -> dict:
    """Mapea el dict del diagnostico al esquema de 19 columnas del historico."""
    return {**{k: r.get(k) for k in col.ESQUEMA_CSV},
            "O2_margen": r.get("margen_O2")}


def _fila_diag(r: dict) -> dict:
    """Fila del companion: margenes de los 4 criterios + filtro de campana."""
    m1 = r.get("margen_O1")
    return {**{k: r.get(k) for k in DIAG_COLS},
            "al_filo_O1": None if m1 is None else bool(0.0 <= float(m1) < 0.05)}


def _descartadas(fuera: list) -> None:
    """Registra en el companion las celdas FUERA_BUB que el filtro no corrio.
    Van SOLO al companion (nunca al historico): no son puntos de ciclo sino
    celdas descartadas, y se anotan para que ninguna de las 160 celdas del TASK
    quede sin registro (TASK constraint 3)."""
    if not fuera:
        return
    base, filas = col.base_centro(), []
    for c in fuera:
        filas.append(_fila_diag(dict(
            base, **{k: c[k] for k in DIAG_COLS if k in c}, convergio=False,
            clasificacion="NO_APLICA_FILTRO", eta=None,
            mensaje="descartado por filtro de campana: T_fuente <= T_bub")))
    pd.DataFrame(filas).reindex(columns=DIAG_COLS).to_csv(
        DIAG, mode="a", header=not DIAG.exists(), index=False, encoding="utf-8")

def _nuevas(cand: list) -> tuple:
    """Duplicados contra TODOS los CSV de fase2_libre + los de la propia tanda."""
    probadas, unicas = col.leer_probadas_r6(), {col.tupla(c): c for c in cand}
    return ([c for t, c in unicas.items() if t not in probadas],
            len(cand), len(unicas))


def correr(nuevas: list, etiqueta: str, presupuesto: float) -> None:
    """Ejecuta `nuevas` con TeqpAdapter, 4 workers y checkpoint cada LOTE."""
    if not nuevas:
        print(f"[{etiqueta}] nada nuevo que correr.", flush=True)
        return
    cab = list(pd.read_csv(col.CSV, nrows=0).columns)
    tope = int(presupuesto / col.S_PT)          # tope por presupuesto de pared
    if tope < len(nuevas):
        print(f"[{etiqueta}] presupuesto {presupuesto:.0f} s -> entran {tope} de "
              f"{len(nuevas)}; se recortan {len(nuevas) - tope}.", flush=True)
        nuevas = nuevas[:tope]
    print(f"[{etiqueta}] {len(nuevas)} puntos TeqpAdapter, T_amb_diseno="
          f"{col.T_AMB_DISENO} K, {col.N_WORKERS} workers, checkpoint cada "
          f"{col.LOTE}; append a {col.CSV.name} ({len(cab)} col) + "
          f"{DIAG.name} ({len(DIAG_COLS)} col)", flush=True)
    t0, filas, diag = time.perf_counter(), [], []

    def guardar() -> None:
        """Vuelca ambos buffers (cada checkpoint y en el `finally`)."""
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
          f"({dt / max(len(nuevas), 1):.1f} s/punto) | {col.CSV.name} "
          f"{len(pd.read_csv(col.CSV))} filas | {DIAG.name} "
          f"{len(pd.read_csv(DIAG))} filas", flush=True)


def filtro() -> None:
    """Imprime la campana de las 160 celdas (no resuelve ningun ciclo)."""
    est = col.filtrar_campana()
    print(f"Campana NH3-H2O, {len(est)} celdas "
          f"(T_fuente x x_b x P_alta) del TASK.\n")
    print(f"{'T_fuente':>8} | {'x_b':>5} | " + " | ".join(
        f"{pa:>13.0f}" for pa in col.P_ALTA_GRID))
    for tf in col.T_FUENTE_GRID:
        for xb in col.X_B_GRID:
            print(f"{tf:8.0f} | {xb:5.2f} | " + " | ".join(
                f"{est[(tf, xb, pa)]['T_bub']:5.1f}-"
                f"{est[(tf, xb, pa)]['T_dew']:5.1f}"
                f"{'*' if est[(tf, xb, pa)]['estado_filtro'] == 'CUBIERTO' else ' '}"
                for pa in col.P_ALTA_GRID))
    c = Counter(v["estado_filtro"] for v in est.values())
    print(f"\n* = CUBIERTO (la campana cubre T_fuente). Recuento: {dict(c)}")
    print("Sin * = PARCIAL (T_fuente >= T_dew; el HRVG aun da T2 < T_dew porque "
          "eps_hrvg < 1, regimen en el que la ronda 5 SI convergio a 470 K).")
    cand, fuera = col.nivel1(est)
    nuevas, n_cand, n_uni = _nuevas(cand)
    print(f"\nNivel 1: candidatas {n_cand} | repetidas en la tanda {n_cand - n_uni} "
          f"| ya probadas {n_uni - len(nuevas)} | NUEVAS {len(nuevas)} "
          f"| celdas FUERA_BUB descartadas {len(fuera)}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Barrido T_fuente libre x x_b alto")
    ap.add_argument("nivel", choices=("filtro", "nivel1", "nivel2", "nivel3"))
    ap.add_argument("--presupuesto", type=float, default=7200.0, help="segundos")
    args = ap.parse_args()
    if args.nivel == "filtro":
        return filtro()
    if args.nivel == "nivel1":
        est = col.filtrar_campana()
        cand, fuera = col.nivel1(est)
        _descartadas(fuera)          # celdas FUERA_BUB -> companion
    else:
        cand = {"nivel2": col.nivel2, "nivel3": col.nivel3}[args.nivel]()
    nuevas, n_cand, n_uni = _nuevas(cand)
    print(f"[{args.nivel}] candidatas: {n_cand} | repetidas en la tanda: "
          f"{n_cand - n_uni} | ya probadas (rondas 1-6): {n_uni - len(nuevas)} | "
          f"nuevas: {len(nuevas)}", flush=True)
    correr(nuevas, args.nivel, args.presupuesto)


if __name__ == "__main__":
    main()
