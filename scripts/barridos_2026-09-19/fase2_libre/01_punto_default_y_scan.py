"""Fase 2 (tarea 2026-09-19-fase2-busqueda-libre) — etapa 1.

Búsqueda LIBRE de una base que clasifique KALINA (sin anclaje a caso real;
exploración del modelo, no realismo industrial — ver TASK_CONTEXT):

- Punto 0: la base por defecto EXACTA de CAMPOS_CICLO (T_fuente=470.0 K,
  P_alta=3000, P_baja=400, x_b=0.50, T_sumidero=300.032917, m_b=1.0,
  eta_t=0.85, eta_p=0.75, eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.80).
- Escaneo focalizado: la única falla del punto 0 es O2 (cavitación de bomba:
  salida del condensador re-resuelta al sumidero de diseño 303.55 K queda sobre
  el bubble point de P_baja). Palancas directas según el propio criterio O2:
  aumentar eps_cond (más subenfriamiento) y/o subir P_baja (sube T_sat_L).

Todo punto probado se registra en
resultados/barridos_2026-09-19/fase2_libre/busqueda_libre.csv con el mismo
esquema de columnas que `tabla_barrido` (sensitivity.py). Paralelizado con
ProcessPoolExecutor igual que la Fase B0 (workers con su propio TeqpAdapter).

NO modifica código de producción (solo consume src/ como librería).
"""

from __future__ import annotations

import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

_RAIZ = Path(__file__).resolve().parents[3]  # ruta: scripts/barridos_2026-09-19/fase2_libre/
sys.path.insert(0, str(_RAIZ))

from src.cycle_solver import CicloNoConvergeError, resolver_ciclo
from src.properties.adapter import PropertyRangeError
from src.restricciones import evaluar_ciclo

DEFAULTS = dict(T_fuente=470.0, T_sumidero=300.032917, P_alta=3000.0,
                P_baja=400.0, x_b=0.50, m_b=1.0, eta_t=0.85, eta_p=0.75,
                eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.80)

VARIABLES = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "m_b",
             "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")
COLUMNAS = list(VARIABLES) + ["convergio", "clasificacion", "eta", "Wnet",
                              "mensaje"]
N_WORKERS = 4
CSV = (_RAIZ / "resultados" / "barridos_2026-09-19" / "fase2_libre"
       / "busqueda_libre.csv")


def importar_backend():
    from src.properties.teqp_adapter import TeqpAdapter
    return TeqpAdapter(x=0.5)


def resolver_punto(combo: dict) -> dict:
    """Resuelve + clasifica un punto; devuelve la fila para el CSV."""
    backend = importar_backend()
    fila = dict(combo)
    try:
        res = resolver_ciclo(backend, **combo)
    except (CicloNoConvergeError, PropertyRangeError) as exc:
        fila.update(convergio=False, clasificacion="NO_CONVERGIO", eta=None,
                    Wnet=None, mensaje=str(exc)[:400])
        return fila
    val = evaluar_ciclo(backend, res, P_alta=combo["P_alta"],
                        P_baja=combo["P_baja"], T_fuente=combo["T_fuente"],
                        T_sumidero=combo["T_sumidero"], x_b=combo["x_b"],
                        m_b=combo["m_b"], eps_hrvg=combo["eps_hrvg"],
                        eps_reg=combo["eps_reg"], eps_cond=combo["eps_cond"])
    fila.update(convergio=True, clasificacion=val.clasificacion.value,
                eta=res["eta"], Wnet=res["Wnet"],
                mensaje=val.mensaje_reporte()[:400])
    return fila


def combos_etapa1() -> list[dict]:
    """Punto 0 (default) + escaneo eps_cond x P_baja (todo lo demás default)."""
    puntos = [dict(DEFAULTS)]
    for pb in (400.0, 450.0, 500.0):
        for ec in (0.95, 0.98, 0.99):
            c = dict(DEFAULTS)
            c["P_baja"] = pb
            c["eps_cond"] = ec
            puntos.append(c)
    return puntos


def main() -> None:
    puntos = combos_etapa1()
    print(f"Etapa 1: {len(puntos)} puntos (default + eps_cond x P_baja) con "
          f"{N_WORKERS} workers...", flush=True)
    filas = []
    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=N_WORKERS) as pool:
        futuros = [pool.submit(resolver_punto, p) for p in puntos]
        for n, fut in enumerate(as_completed(futuros), 1):
            filas.append(fut.result())
            if n % 4 == 0:
                print(f"  {n}/{len(puntos)} puntos "
                      f"({time.perf_counter() - t0:.0f} s)", flush=True)
    dt = time.perf_counter() - t0

    df = pd.DataFrame(filas)[COLUMNAS]
    CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CSV, index=False, encoding="utf-8")

    print(f"\nPuntos evaluados: {len(filas)} en {dt:.1f} s "
          f"({dt / len(filas):.2f} s/punto)", flush=True)
    print(df["clasificacion"].value_counts().to_string())
    print(f"Convergencias: {int(df['convergio'].sum())}")
    lin = df[df["clasificacion"] == "KALINA"]
    if not lin.empty:
        print("\nCANDIDATOS KALINA encontrados:")
        for _, r in lin.iterrows():
            print(f"  P_baja={r['P_baja']:.1f} eps_cond={r['eps_cond']:.2f} "
                  f"eta={r['eta']:.5f} Wnet={r['Wnet']:.2f} kW")
    else:
        print("\nSin KALINA en esta etapa. Mejores (CORREGIBLE/otros):")
        for _, r in df.sort_values("convergio", ascending=False).head(6).iterrows():
            print(f"  P_baja={r['P_baja']:.1f} eps_cond={r['eps_cond']:.2f} "
                  f"-> {r['clasificacion']} | {r['mensaje'][:120]}")
    print(f"\nCSV guardado en {CSV}")


if __name__ == "__main__":
    main()