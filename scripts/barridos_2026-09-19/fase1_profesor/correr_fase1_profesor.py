"""Fase 1 (tarea 2026-09-19-fase1-profesor): correr y documentar el fallo con
los datos EXACTOS del enunciado del profesor (Word "5 CICLO KALINA"),
transcritos en TASK_CONTEXT_fase1_profesor.md.

Corre, SIN ajustar ninguna variable (no es optimización; la Fase 2 es una
tarea distinta que busca arreglos):
  1) el punto base con el motor real `AmmoniaWaterAdapter` (1 punto, ~1-2 min),
  2) los 3 barridos de sensibilidad que pide el enunciado con `TeqpAdapter`
     (rápido, 40 puntos en total):
       - P_alta 2000-4000 kPa (paso 250 kPa, 9 puntos), resto base,
       - x_b 0.40-0.70 (paso 0.05, 7 puntos), resto base,
       - T_ambiente: las 24 horas de tamb_profesor.csv usadas como T_sumidero
         (la tabla es el sumidero/ambiente; T_fuente queda fijo en 623.15 K).
Cada punto, converja o no, se registra con `Fijo`/`Barrido` +
`ejecutar_barrido`/`tabla_barrido` (src/sensitivity.py, herramienta validada)
en 3 CSV en resultados/barridos_2026-09-19/fase1_profesor/. El punto base se
documenta en CONSTANCIA_PROFESOR.md (se redacta con los números que imprime
este script).

Se espera que los puntos NO clasifiquen KALINA (síntoma conocido con
T_fuente alto: el estado 2 del HRVG queda sobrecalentado fuera de la campana
bifásica y el separador no puede flashear — ver CONTEXT.md nota 2026-09-17 y
b0_scan_cementera.csv). Si algún punto clasifica KALINA se reporta igual, sin
sesgo. El escaneo se paraleliza con ProcessPoolExecutor (Windows usa spawn):
el worker es de nivel de módulo y crea su propio backend, por lo que el
resultado es idéntico al secuencial.

NO modifica código de producción (solo consume src/ como librería) y NO toca
las carpetas fase2_libre/ ni fase3_real/ (tareas corriendo en paralelo).
"""

from __future__ import annotations

import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

_RAIZ = Path(__file__).resolve().parents[3]  # script vive 3 niveles bajo la raíz
sys.path.insert(0, str(_RAIZ))

from src.cycle_solver import CicloNoConvergeError, resolver_ciclo
from src.properties.adapter import PropertyRangeError
from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter
from src.restricciones import evaluar_ciclo
from src.sensitivity import (Barrido, Fijo, VARIABLES_BARRIBLES,
                             ejecutar_barrido, generar_valores, tabla_barrido)

# -- constantes del enunciado (TASK_CONTEXT_fase1_profesor.md) ---------------
T_FUENTE = 623.15             # 350 °C (fuente térmica, fija en todo el ejercicio)
T_SUMIDERO_BASE = 300.032917  # promedio de tamb_profesor.csv (= default CONTEXT.md)
MB = 1.0                      # m9 = m10 (base de cálculo)
X_B = 0.50                    # composición global de NH3
P_ALTA = 3000.0               # kPa — puntos 1,2,3,5,6,10
P_BAJA = 400.0                # kPa — puntos 4,7,8,9
ETA_T, ETA_P = 0.85, 0.75
EPS_HRVG, EPS_REG, EPS_COND = 0.85, 0.75, 0.80
N_WORKERS = 4

TAMB_CSV = Path(__file__).resolve().parent / "tamb_profesor.csv"
SALIDA_DIR = _RAIZ / "resultados" / "barridos_2026-09-19" / "fase1_profesor"

BASE = dict(T_fuente=T_FUENTE, T_sumidero=T_SUMIDERO_BASE, P_alta=P_ALTA,
            P_baja=P_BAJA, x_b=X_B, m_b=MB, eta_t=ETA_T, eta_p=ETA_P,
            eps_hrvg=EPS_HRVG, eps_reg=EPS_REG, eps_cond=EPS_COND)


def leer_tamb() -> pd.DataFrame:
    """La tabla horaria real del enunciado (24 valores, columnas hora,T_amb_K)."""
    df = pd.read_csv(TAMB_CSV)
    if list(df.columns) != ["hora", "T_amb_K"]:
        raise ValueError(
            f"columnas inesperadas en {TAMB_CSV}: {list(df.columns)}")
    return df


def correr_punto_base() -> dict:
    """1 punto base con el motor real (AmmoniaWaterAdapter, ~1-2 min)."""
    backend = AmmoniaWaterAdapter(x=X_B)
    t0 = time.perf_counter()
    try:
        res = resolver_ciclo(backend, **BASE)
    except (CicloNoConvergeError, PropertyRangeError) as exc:
        return dict(convergio=False, clasificacion="NO_CONVERGIO", eta=None,
                    Wnet=None, mensaje=str(exc),
                    tiempo_s=round(time.perf_counter() - t0, 1))
    val = evaluar_ciclo(backend, res, **BASE)
    return dict(convergio=True, clasificacion=val.clasificacion.value,
                eta=res["eta"], Wnet=res["Wnet"], mensaje=val.mensaje_reporte(),
                tiempo_s=round(time.perf_counter() - t0, 1))


def resolver_punto(combo: dict) -> dict:
    """Worker (nivel de módulo, necesario por spawn en Windows): 1 punto."""
    from src.properties.teqp_adapter import TeqpAdapter

    backend = TeqpAdapter(x=combo["x_b"])
    variables = {k: Fijo(v) for k, v in combo.items()}
    return ejecutar_barrido(backend, variables)[0]


def main() -> None:
    tamb = leer_tamb()
    print(f"Tabla horaria: {len(tamb)} filas, promedio T_amb = "
          f"{tamb['T_amb_K'].mean():.6f} K (la base usa {T_SUMIDERO_BASE} K)",
          flush=True)

    print("\n[1/2] Punto base con motor real (AmmoniaWaterAdapter)...",
          flush=True)
    base = correr_punto_base()
    print(f"  convergio={base['convergio']} "
          f"clasificacion={base['clasificacion']} "
          f"({base['tiempo_s']} s)", flush=True)
    print(f"  mensaje: {base['mensaje'][:400]}", flush=True)
    if base["convergio"]:
        print(f"  eta={base['eta']:.5f}  Wnet={base['Wnet']:.3f} kW",
              flush=True)

    # -- combos de los 3 barridos (enumeración explícita del TASK_CONTEXT) ----
    grupos: dict[str, list[dict]] = {"P_alta": [], "x_b": [], "T_ambiente": []}
    for pa in generar_valores(Barrido(2000.0, 4000.0, 250.0)):
        grupos["P_alta"].append(dict(BASE, P_alta=pa))
    for xb in generar_valores(Barrido(0.40, 0.70, 0.05)):
        grupos["x_b"].append(dict(BASE, x_b=xb))
    horas_tamb: list[int] = []
    for _, fila in tamb.iterrows():
        horas_tamb.append(int(fila["hora"]))
        grupos["T_ambiente"].append(
            dict(BASE, T_sumidero=float(fila["T_amb_K"])))

    tareas = [(grupo, i, combo) for grupo, combos in grupos.items()
              for i, combo in enumerate(combos)]
    print(f"\n[2/2] Barridos con TeqpAdapter: {len(tareas)} puntos "
          f"(P_alta 9 + x_b 7 + T_ambiente 24) con {N_WORKERS} workers...",
          flush=True)

    filas: dict[tuple[str, int], dict] = {}
    t0 = time.perf_counter()
    n_hechos = 0
    with ProcessPoolExecutor(max_workers=N_WORKERS) as pool:
        futuros = {pool.submit(resolver_punto, combo): (grupo, i)
                   for grupo, i, combo in tareas}
        for fut in as_completed(futuros):
            grupo, i = futuros[fut]
            filas[(grupo, i)] = fut.result()
            n_hechos += 1
            if n_hechos % 10 == 0:
                print(f"  {n_hechos}/{len(tareas)} puntos "
                      f"({time.perf_counter() - t0:.0f} s)", flush=True)
    dt = time.perf_counter() - t0
    print(f"  {len(tareas)} puntos en {dt:.0f} s "
          f"({dt / len(tareas):.2f} s/punto promedio)", flush=True)

    d_pa = tabla_barrido([filas[("P_alta", i)]
                          for i in range(len(grupos["P_alta"]))])
    d_xb = tabla_barrido([filas[("x_b", i)]
                          for i in range(len(grupos["x_b"]))])
    d_ta = tabla_barrido([filas[("T_ambiente", i)]
                          for i in range(len(grupos["T_ambiente"]))])
    d_ta.insert(0, "hora", horas_tamb)  # trazabilidad con la tabla del profesor
    d_ta = d_ta.sort_values("T_sumidero").reset_index(drop=True)

    SALIDA_DIR.mkdir(parents=True, exist_ok=True)
    for df, nombre in ((d_pa, "eta_vs_Palta_profesor.csv"),
                       (d_xb, "eta_vs_xb_profesor.csv"),
                       (d_ta, "eta_vs_Tambiente_profesor.csv")):
        ruta = SALIDA_DIR / nombre
        df.to_csv(ruta, index=False, encoding="utf-8")
        print(f"  {nombre}: {len(df)} puntos -> {ruta}", flush=True)

    print("\nResumen por clasificacion (alimenta CONSTANCIA_PROFESOR.md):",
          flush=True)
    for nombre, df in (("P_alta", d_pa), ("x_b", d_xb),
                       ("T_ambiente", d_ta)):
        print(f"  {nombre} ({len(df)} puntos):", flush=True)
        print(df["clasificacion"].value_counts().sort_index().to_string(),
              flush=True)
        print(f"    convergencias: {int(df['convergio'].sum())}", flush=True)
    print(f"\nPunto base: {base['clasificacion']} "
          f"(convergio={base['convergio']})", flush=True)
    print("LISTO — los números de arriba alimentan CONSTANCIA_PROFESOR.md")


if __name__ == "__main__":
    main()