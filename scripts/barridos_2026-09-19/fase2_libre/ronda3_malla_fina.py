"""Fase 2, ronda 3 (tarea 2026-09-21-fase2-ronda3-malla-fina) — malla fina P_alta x P_baja.

Tercera ronda de la Fase 2: cerrar la frontera KALINA/CORREGIBLE que la ronda 2
dejo abierta en la franja (P_alta=3000, P_baja=650) CORREGIBLE O2=-0.15 K vs
(P_alta=3200, P_baja=650) KALINA O2=+0.75 K (misma x_b=0.50, eps_cond=0.95).

Malla fina: P_alta {3100..3300, paso 50} x P_baja {630..670, paso 10} = 25
candidatas; se excluye la ya probada (3200/650 viene de la ronda 2). Ancla FIJA
T_fuente=470.0 / T_sumidero=300.032917, x_b=0.50, eps_cond=0.95; resto en la
base de siempre (eta_t=0.85, eta_p=0.75, eps_hrvg=0.85, eps_reg=0.75, m_b=1.0);
T_amb_diseno=303.55. Motor SOLO TeqpAdapter.

Anti-duplicado: se reutiliza ronda2_pbaja.py (carpeta con guiones -> importlib
por ruta, mismo patron que test_fase2_libre.py).leer_probadas(): 8-tuplo
(P_alta, P_baja, x_b, eta_t, eta_p, eps_hrvg, eps_reg, eps_cond) redondeado a 3
decimales, leido de TODOS los CSV de fase2_libre. Salida: APPEND a
busqueda_libre_v2.csv, misma cabecera real (leida del archivo, 19 columnas).
NO crea CSVs nuevos. NO toca src/.
"""

from __future__ import annotations

import importlib.util
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

_RAIZ = Path(__file__).resolve().parents[3]
if str(_RAIZ) not in sys.path:
    sys.path.insert(0, str(_RAIZ))

T_AMB_DISENO = 303.55
X_B = 0.50
EPS_COND = 0.95
P_ALTA_GRID = (3100.0, 3150.0, 3200.0, 3250.0, 3300.0)
P_BAJA_GRID = (630.0, 640.0, 650.0, 660.0, 670.0)
CARPETA = _RAIZ / "resultados" / "barridos_2026-09-19" / "fase2_libre"
CSV = CARPETA / "busqueda_libre_v2.csv"
N_WORKERS = 4


def cargar_ronda2():
    """Ronda 2 por ruta; la carpeta lleva guiones en su nombre -> no importable."""
    ruta = Path(__file__).resolve().parent / "ronda2_pbaja.py"
    spec = importlib.util.spec_from_file_location("ronda2_pbaja", ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rejilla_fina() -> list:
    r2 = cargar_ronda2()
    return [dict(r2.BASE, P_alta=pa, P_baja=pb, x_b=X_B, eps_cond=EPS_COND)
            for pa in P_ALTA_GRID for pb in P_BAJA_GRID]


def resolver_punto(combo: dict) -> dict:
    """Worker: delega en ronda2_pbaja.resolver_punto (TeqpAdapter + diagnostico O2)."""
    return cargar_ronda2().resolver_punto(combo)


def _celda(r) -> str:
    if not r["convergio"]:
        return "NC/ --  "
    return f"{r['clasificacion'][:4]}/{r['O2_margen']:+.2f}"


def _cruces(filas: list) -> None:
    """Localiza el cruce CORREGIBLE->KALINA (O2=0) por fila y por columna."""
    df = pd.DataFrame(filas)
    flip = []
    for pb in P_BAJA_GRID:
        fila = [(round(r["P_alta"], 1),
                 0.0 if not r["convergio"] else r["O2_margen"])
                for r in df[df["P_baja"] == pb].sort_values("P_alta").to_dict("records")]
        for (p1, m1), (p2, m2) in zip(fila, fila[1:]):
            if m1 * m2 < 0:
                p0 = p1 + (0 - m1) * (p2 - p1) / (m2 - m1)
                flip.append(f"P_baja={pb:.0f}: cruce en P_alta~{p0:.0f} kPa ({p1:.0f}->{p2:.0f})")
    for pa in P_ALTA_GRID:
        col = [(round(r["P_baja"], 1),
                0.0 if not r["convergio"] else r["O2_margen"])
               for r in df[df["P_alta"] == pa].sort_values("P_baja").to_dict("records")]
        for (p1, m1), (p2, m2) in zip(col, col[1:]):
            if m1 * m2 < 0:
                p0 = p1 + (0 - m1) * (p2 - p1) / (m2 - m1)
                flip.append(f"P_alta={pa:.0f}: cruce en P_baja~{p0:.0f} kPa ({p1:.0f}->{p2:.0f})")
    print("Cruce de frontera (O2=0, interpolacion lineal):", flush=True)
    for linea in flip:
        print(f"  {linea}", flush=True)
    if not flip:
        print("  sin cruce en esta malla", flush=True)


def main() -> None:
    r2 = cargar_ronda2()
    print("Anti-duplicado: leyendo TODOS los CSV de fase2_libre...", flush=True)
    probadas = r2.leer_probadas()
    candidatas = rejilla_fina()
    nuevas = [c for c in candidatas if r2.tupla(c) not in probadas]
    n_desc = len(candidatas) - len(nuevas)
    print(f"  candidatas: {len(candidatas)} | descartadas por duplicado: "
          f"{n_desc} | nuevas: {len(nuevas)}", flush=True)
    if not nuevas:
        print("Nada nuevo que correr.")
        return
    cabecera = list(pd.read_csv(CSV, nrows=0).columns)
    print(f"  Ronda 3: {len(nuevas)} puntos TeqpAdapter, malla fina P_alta x "
          f"P_baja, T_amb_diseno={T_AMB_DISENO} K, {N_WORKERS} workers; append "
          f"a {CSV.name} (columnas: {len(cabecera)}).", flush=True)
    t0 = time.perf_counter()
    filas: list = []
    primera = not CSV.exists()
    with ProcessPoolExecutor(max_workers=N_WORKERS) as pool:
        futuros = [pool.submit(resolver_punto, p) for p in nuevas]
        for n, fut in enumerate(as_completed(futuros), 1):
            filas.append(fut.result())
            if n % 10 == 0 or n == len(nuevas):
                tabla = pd.DataFrame(filas).reindex(columns=cabecera)
                tabla.to_csv(CSV, mode="a" if not primera else "w",
                             header=primera, index=False, encoding="utf-8")
                primera = False
                filas = []
                print(f"  {n}/{len(nuevas)} guardados "
                      f"({time.perf_counter() - t0:.0f} s)", flush=True)
    df = pd.read_csv(CSV)
    print(df["clasificacion"].value_counts().to_string(), flush=True)
    nuevas_df = df.tail(len(nuevas)).copy()
    print("\nPuntos de esta ronda (clasificacion y margen O2):", flush=True)
    for _, r in nuevas_df.sort_values(["P_alta", "P_baja"]).iterrows():
        margen = "--" if pd.isna(r["O2_margen"]) else f"{r['O2_margen']:+.2f} K"
        print(f"  P_alta={r['P_alta']:.0f} P_baja={r['P_baja']:.0f} "
              f"-> {r['clasificacion']:<13s} O2_margen={margen}", flush=True)
    _cruces(list(nuevas_df.to_dict("records")))
    dups = nuevas_df.duplicated(subset=["P_alta", "P_baja", "x_b", "eta_t",
                                        "eta_p", "eps_hrvg", "eps_reg", "eps_cond"])
    assert not dups.any(), "duplicados dentro de la tanda nueva"
    print(f"CSV completo: {CSV} ({len(df)} filas, "
          f"{int(df['convergio'].sum())} convergen).", flush=True)


if __name__ == "__main__":
    main()