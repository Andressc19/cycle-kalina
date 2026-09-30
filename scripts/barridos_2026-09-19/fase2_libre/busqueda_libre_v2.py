"""Fase 2 (tarea 2026-09-20-actualizar-rangos-fase2-fase3) — búsqueda v2.

Nueva palanca: x_b bajo (0.35-0.50, nunca probado) cruzado con P_baja
400-600 kPa y eps_cond 0.80-0.95 (rango razonable, NO forzado al 0.99 del
candidato viejo). T_amb_diseno se mantiene en 303.55 K (default): es el caso
del profesor, cuya propia tabla horaria real SÍ llega a 30.4 °C en la hora 17
(decisión documentada en BASE_LIBRE_v2.md, ver TASK_CONTEXT §Contexto).

Base del profesor (la que converge, CONTEXT.md): P_alta=3000, T_fuente=470.0,
T_sumidero=300.032917, m_b=1.0, eta_t=0.85, eta_p=0.75, eps_hrvg=0.85,
eps_reg=0.75. Escaneo: 4 x_b x 5 P_baja x 4 eps_cond = 80 puntos TeqpAdapter
(paralelo, 4 workers). Cada punto registra además el diagnóstico O2 (T9
re-resuelta al piso T_amb=303.55 K vs bubble_point(P_baja, x_b)) para poder
comparar margenes con la iteracion vieja.

Salida:
resultados/barridos_2026-09-19/fase2_libre/busqueda_libre_v2.csv

NO modifica codigo de produccion (solo consume src/ como libreria).
"""

from __future__ import annotations

import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

_RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_RAIZ))

from src.cycle_solver import CicloNoConvergeError, resolver_ciclo
from src.properties.adapter import PropertyRangeError
from src.restricciones import evaluar_ciclo

T_AMB_DISENO = 303.55          # caso del profesor: su tabla real llega a 30.4 C
BASE = dict(P_alta=3000.0, T_fuente=470.0, T_sumidero=300.032917, m_b=1.0,
            eta_t=0.85, eta_p=0.75, eps_hrvg=0.85, eps_reg=0.75)
X_B_GRID = (0.35, 0.40, 0.45, 0.50)
P_BAJA_GRID = (400.0, 450.0, 500.0, 550.0, 600.0)
EPS_COND_GRID = (0.80, 0.85, 0.90, 0.95)
N_WORKERS = 4
CSV = (_RAIZ / "resultados" / "barridos_2026-09-19" / "fase2_libre"
       / "busqueda_libre_v2.csv")
COLUMNAS = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "m_b",
            "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond",
            "T_sat_L", "T9_amb", "O2_margen",
            "convergio", "clasificacion", "eta", "Wnet", "mensaje")


def importar_backend():
    from src.properties.teqp_adapter import TeqpAdapter
    return TeqpAdapter(x=0.5)


def resolver_punto(combo: dict) -> dict:
    """Resuelve + clasifica un punto y adjunta el diagnostico O2 (worker)."""
    from src.components.condensador import resolver as resolver_cond
    backend = importar_backend()
    fila = dict(combo, T_sat_L=None, T9_amb=None, O2_margen=None)
    try:
        res = resolver_ciclo(backend, **combo)
    except (CicloNoConvergeError, PropertyRangeError) as exc:
        fila.update(convergio=False, clasificacion="NO_CONVERGIO", eta=None,
                    Wnet=None, mensaje=str(exc)[:300])
        return fila
    val = evaluar_ciclo(backend, res, P_alta=combo["P_alta"],
                        P_baja=combo["P_baja"], T_fuente=combo["T_fuente"],
                        T_sumidero=combo["T_sumidero"], x_b=combo["x_b"],
                        m_b=combo["m_b"], eps_hrvg=combo["eps_hrvg"],
                        eps_reg=combo["eps_reg"], eps_cond=combo["eps_cond"],
                        T_amb_diseno=T_AMB_DISENO)
    # Diagnostico O2 explicitado: T9 re-resuelta al piso max(T_sumidero, 303.55)
    T_amb_evaluar = max(combo["T_sumidero"], T_AMB_DISENO)
    est9_amb, _ = resolver_cond(res["estados"]["e8"], backend,
                                T_sumidero=T_amb_evaluar,
                                eps=combo["eps_cond"], m=combo["m_b"])
    T_sat_L = backend.bubble_point(combo["P_baja"], combo["x_b"])
    fila.update(T_sat_L=T_sat_L, T9_amb=est9_amb.T,
                O2_margen=T_sat_L - est9_amb.T)
    fila.update(convergio=True, clasificacion=val.clasificacion.value,
                eta=res["eta"], Wnet=res["Wnet"],
                mensaje=val.mensaje_reporte()[:300])
    return fila


def combos() -> list[dict]:
    puntos = []
    for xb in X_B_GRID:
        for pb in P_BAJA_GRID:
            for ec in EPS_COND_GRID:
                c = dict(BASE)
                c["P_baja"] = pb
                c["x_b"] = xb
                c["eps_cond"] = ec
                puntos.append(c)
    return puntos


def main() -> None:
    todos = combos()
    hechos: set = set()
    CSV.parent.mkdir(parents=True, exist_ok=True)
    if CSV.exists():
        prev = pd.read_csv(CSV)
        hechos = {(r.x_b, r.P_baja, r.eps_cond) for r in prev.itertuples()}
        print(f"Checkpoint: {len(hechos)} puntos ya en {CSV.name}, "
              f"continua desde ahi", flush=True)
    puntos = [p for p in todos if (p["x_b"], p["P_baja"], p["eps_cond"])
              not in hechos]
    print(f"Escaneo v2: {len(todos)} puntos totales, {len(puntos)} pendientes "
          f"(x_b x P_baja x eps_cond) con T_amb_diseno={T_AMB_DISENO} K, "
          f"{N_WORKERS} workers...", flush=True)
    if not puntos:
        filas_acum = pd.read_csv(CSV).to_dict("records")
    else:
        t0 = time.perf_counter()
        filas: list[dict] = []
        primera = CSV.exists() is False
        with ProcessPoolExecutor(max_workers=N_WORKERS) as pool:
            futuros = [pool.submit(resolver_punto, p) for p in puntos]
            for n, fut in enumerate(as_completed(futuros), 1):
                filas.append(fut.result())
                if n % 10 == 0 or n == len(puntos):
                    df_chunk = pd.DataFrame(filas)[list(COLUMNAS)]
                    df_chunk.to_csv(CSV, mode="a" if not primera else "w",
                                    header=primera, index=False,
                                    encoding="utf-8")
                    primera = False
                    filas = []
                    print(f"  {n}/{len(puntos)} puntos guardados "
                          f"({time.perf_counter() - t0:.0f} s)", flush=True)
        dt = time.perf_counter() - t0
        print(f"Puntos evaluados ahora: {len(puntos)} en {dt:.1f} s "
              f"({dt / len(puntos):.2f} s/punto)", flush=True)
        filas_acum = pd.read_csv(CSV).to_dict("records")

    df = pd.DataFrame(filas_acum)[list(COLUMNAS)]
    print(df["clasificacion"].value_counts().to_string())
    print(f"Convergencias: {int(df['convergio'].sum())}", flush=True)

    kalina = df[df["clasificacion"] == "KALINA"]
    if not kalina.empty:
        kalina_sorted = kalina.sort_values(
            ["eta", "eps_cond", "P_baja", "x_b"], ascending=[False] * 4)
        print(f"\nKALINA: {len(kalina)} punto(s). Mejores por eta:", flush=True)
        for _, r in kalina_sorted.head(8).iterrows():
            print(f"  P_baja={r['P_baja']:.0f} x_b={r['x_b']:.2f} "
                  f"eps_cond={r['eps_cond']:.2f} eta={r['eta']:.5f} "
                  f"Wnet={r['Wnet']:.2f} O2_margen={r['O2_margen']:+.2f} K",
                  flush=True)
    else:
        print("\nSin KALINA. Mejores por clasificacion:", flush=True)
        peso = {"VALIDO_ADVERTENCIA": 4, "CORREGIBLE": 3, "DEGENERADO": 2,
                "INVIABLE": 1, "NO_CONVERGIO": 0}
        orden = df.assign(_p=lambda d: d["clasificacion"].map(peso))
        for _, r in orden.sort_values("_p", ascending=False).head(8).iterrows():
            print(f"  P_baja={r['P_baja']:.0f} x_b={r['x_b']:.2f} "
                  f"eps_cond={r['eps_cond']:.2f} -> {r['clasificacion']} "
                  f"eta={r['eta']:.5f}", flush=True)
    print(f"\nCSV guardado en {CSV}")


if __name__ == "__main__":
    main()