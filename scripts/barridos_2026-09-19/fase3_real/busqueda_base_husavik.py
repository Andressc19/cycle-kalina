"""Fase 3 (tarea 2026-09-19-fase3-caso-real): búsqueda de la base KALINA
anclada al caso real de la planta geotérmica de Húsavík (Islandia, 2 MW).

Caso real citado por el director (no re-buscado):
- T_fuente = 394.15 K (salmuera geotérmica a 121 °C)
- T_sumidero = 278.15 K (agua de refrigeración a 5 °C)
- x_b ≈ 0.82, P_alta ≈ 3300 kPa (32-34 bar), eta_t ≈ 0.90, eta_p ≈ 0.80

P_baja NO está publicado: se calibra con la regla ya usada en la Fase B0
(aprobada por el director): bubble_point(P_baja, x_b) = T_sumidero + 3 K.

Estrategia adaptativa con TeqpAdapter (rápido), todas las fases dentro de
CAMPOS_CICLO y cerca de los valores reales citados:
- Fase A: el punto base exacto del TASK_CONTEXT (1 punto).
- Fase B: palancas de T8 (salida absorbedor, la que decide O2): eta_t ×
  eps_reg × eps_cond en el eje real (P_alta=3300, x_b=0.82).
- Fase C (solo si hace falta): expandir P_alta/x_b alrededor de lo real
  con las mejores palancas de la Fase B.
- Fase D (solo si hace falta): refinamiento 1D de la palanca más sensible.

Cada punto probado se registra, converja o no, en
resultados/barridos_2026-09-19/fase3_real/busqueda_husavik.csv con el mismo
esquema que `tabla_barrido` (11 variables + convergio/clasificacion/eta/
Wnet/mensaje). Se detiene en cuanto encuentra un punto KALINA.

NO modifica código de producción (solo consume src/ como librería).
"""

from __future__ import annotations

import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
from scipy.optimize import brentq

_RAIZ = Path(__file__).resolve().parents[3]  # script en scripts/barridos_2026-09-19/fase3_real/
sys.path.insert(0, str(_RAIZ))

from src.cycle_solver import CicloNoConvergeError, resolver_ciclo
from src.properties.adapter import PropertyRangeError
from src.restricciones import evaluar_ciclo

# -- constantes del caso real (TASK_CONTEXT_fase3_real.md) -------------------
T_FUENTE = 394.15          # salmuera geotérmica, 121 °C
T_SUMIDERO = 278.15        # agua de refrigeración, 5 °C
DT_COND = 3.0              # supuesto ya usado en Fase B0 (no inventado)
T_OBJ_COND = T_SUMIDERO + DT_COND
MB = 1.0
ETA_P = 0.80               # valor citado en la literatura del caso
P_BAJA_MIN, P_BAJA_MAX = 50.0, 5000.0   # CAMPOS_CICLO
N_WORKERS = 4
CSV = (_RAIZ / "resultados" / "barridos_2026-09-19" / "fase3_real"
       / "busqueda_husavik.csv")
COLUMNAS = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "m_b",
            "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond",
            "convergio", "clasificacion", "eta", "Wnet", "mensaje")

# -- rejillas por fase --------------------------------------------------------
# Fase A: punto base literal del TASK_CONTEXT.
FASE_A = dict(P_alta=3300.0, x_b=0.82, eta_t=0.90, eps_hrvg=0.85,
              eps_reg=0.75, eps_cond=0.80)
# Fase B: palancas de T8 en el eje real (P_alta/x_b fijos).
FASE_B_ETA_T = (0.90, 0.95, 0.98)
FASE_B_EPS_REG = (0.90, 0.95)
FASE_B_EPS_COND = (0.90, 0.98)
# Fase C (condicional): extensión alrededor de lo real.
FASE_C_P_ALTA = (3000.0, 3200.0, 3400.0, 3500.0)
FASE_C_X_B = (0.78, 0.80, 0.84, 0.86)


def calibrar_p_baja(backend, xb: float) -> float:
    """P_baja tal que bubble_point(P_baja, x_b) = T_sumidero + 3 K."""
    f = lambda P: backend.bubble_point(P, xb) - T_OBJ_COND
    return float(brentq(f, P_BAJA_MIN, P_BAJA_MAX, xtol=1e-4))


def importar_backend():
    from src.properties.teqp_adapter import TeqpAdapter
    return TeqpAdapter(x=0.82)


def resolver_punto(pa: float, xb: float, eta_t: float, eps_h: float,
                   eps_r: float, eps_c: float) -> dict:
    """Resuelve un punto con TeqpAdapter y lo clasifica (worker de módulo)."""
    backend = importar_backend()
    pb = calibrar_p_baja(backend, xb)
    combo = dict(P_alta=pa, P_baja=pb, T_fuente=T_FUENTE,
                 T_sumidero=T_SUMIDERO, x_b=xb, m_b=MB, eta_t=eta_t,
                 eta_p=ETA_P, eps_hrvg=eps_h, eps_reg=eps_r, eps_cond=eps_c)
    fila = dict(T_fuente=T_FUENTE, T_sumidero=T_SUMIDERO, P_alta=pa,
                P_baja=pb, x_b=xb, m_b=MB, eta_t=eta_t, eta_p=ETA_P,
                eps_hrvg=eps_h, eps_reg=eps_r, eps_cond=eps_c)
    try:
        res = resolver_ciclo(backend, **combo)
    except (CicloNoConvergeError, PropertyRangeError) as exc:
        fila.update(convergio=False, clasificacion="NO_CONVERGIO",
                    eta=None, Wnet=None, mensaje=str(exc))
        return fila
    val = evaluar_ciclo(backend, res, P_alta=pa, P_baja=pb,
                        T_fuente=T_FUENTE, T_sumidero=T_SUMIDERO,
                        x_b=xb, m_b=MB, eps_hrvg=eps_h, eps_reg=eps_r,
                        eps_cond=eps_c)
    t8 = res["estados"]["e8"].T
    fila.update(convergio=True, clasificacion=val.clasificacion.value,
                eta=res["eta"], Wnet=res["Wnet"],
                mensaje=f"T8={t8:.2f} K || {val.mensaje_reporte()}")
    return fila


def correr_fase(specs: list[tuple], etiqueta: str) -> list[dict]:
    """Corre una fase en paralelo y devuelve las filas en orden de llegada."""
    print(f"\n=== {etiqueta}: {len(specs)} puntos ===", flush=True)
    filas = []
    t0 = time.perf_counter()
    n = 0
    with ProcessPoolExecutor(max_workers=N_WORKERS) as pool:
        futuros = [pool.submit(resolver_punto, *sp) for sp in specs]
        for fut in as_completed(futuros):
            filas.append(fut.result())
            n += 1
            if n % 4 == 0:
                print(f"  {n}/{len(specs)} ({time.perf_counter()-t0:.0f} s)",
                      flush=True)
    return filas


def guardar(filas: list[dict], primera: bool) -> None:
    df = pd.DataFrame(filas)[list(COLUMNAS)]
    df.to_csv(CSV, mode="a" if not primera else "w",
              header=primera, index=False, encoding="utf-8")


def resumen(filas: list[dict]) -> None:
    for f in filas:
        estado = (f"eta={f['eta']:.4f} Wnet={f['Wnet']:.1f} kW"
                  if f["convergio"] else "sin converger")
        print(f"  P_alta={f['P_alta']:.0f} x_b={f['x_b']:.2f} "
              f"eta_t={f['eta_t']:.2f} eps_r={f['eps_reg']:.2f} "
              f"eps_c={f['eps_cond']:.2f} -> {f['clasificacion']} ({estado})",
              flush=True)


def main() -> None:
    primera = True
    if CSV.exists():
        CSV.unlink()  # re-corrida: CSV viejo se reemplaza (solo est. de fase3)

    # Fase A: punto base.
    a = FASE_A
    filas_a = correr_fase([(a["P_alta"], a["x_b"], a["eta_t"], a["eps_hrvg"],
                            a["eps_reg"], a["eps_cond"])], "Fase A: base")
    guardar(filas_a, primera)
    primera = False
    resumen(filas_a)
    if any(f["clasificacion"] == "KALINA" for f in filas_a):
        print(f"\nBASE KALINA encontrada en Fase A. CSV en {CSV}")
        return

    # Fase B: palancas de T8 en el eje real.
    specs_b = [(3300.0, 0.82, et, 0.85, er, ec)
               for et in FASE_B_ETA_T for er in FASE_B_EPS_REG
               for ec in FASE_B_EPS_COND]
    filas_b = correr_fase(specs_b, "Fase B: palancas T8 (P_alta=3300, x_b=0.82)")
    guardar(filas_b, primera)
    primera = False
    resumen(filas_b)
    if any(f["clasificacion"] == "KALINA" for f in filas_b):
        print(f"\nBASE KALINA encontrada en Fase B. CSV en {CSV}")
        return

    # Fase C: expandir P_alta/x_b alrededor de lo real con las 2 mejores
    # combinaciones de palancas de la Fase B (las de clasificación menos severa).
    conv = [f for f in filas_b if f["convergio"]]
    peso = {"KALINA": 0, "VALIDO_ADVERTENCIA": 1, "CORREGIBLE": 2,
            "DEGENERADO": 3, "INVIABLE": 4, "NO_CONVERGIO": 5}
    mejores = sorted(conv, key=lambda f: (peso.get(f["clasificacion"], 9),
                                          -(f["eta"] or 0.0)))[:2]
    if not mejores:
        print("  (sin puntos convergentes en Fase B: uso palancas máximas "
              "para la Fase C)", flush=True)
        mejores = [dict(eta_t=0.95, eps_hrvg=0.85, eps_reg=0.95, eps_cond=0.98),
                   dict(eta_t=0.98, eps_hrvg=0.85, eps_reg=0.90, eps_cond=0.98)]
    specs_c = [(pa, xb, m["eta_t"], m["eps_hrvg"], m["eps_reg"], m["eps_cond"])
               for pa in FASE_C_P_ALTA for xb in FASE_C_X_B for m in mejores]
    filas_c = correr_fase(specs_c, "Fase C: extension P_alta/x_b")
    guardar(filas_c, primera)
    primera = False
    resumen(filas_c)
    if any(f["clasificacion"] == "KALINA" for f in filas_c):
        print(f"\nBASE KALINA encontrada en Fase C. CSV en {CSV}")
        return

    print("\nSin punto KALINA en A+B+C. Mejor candidato para refinamiento:")
    todas = filas_a + filas_b + filas_c
    best = min((f for f in todas if f["convergio"]),
               key=lambda f: peso.get(f["clasificacion"], 9))
    print(f"  {best['clasificacion']} P_alta={best['P_alta']:.0f} "
          f"x_b={best['x_b']:.2f} eta_t={best['eta_t']:.2f} "
          f"eps_r={best['eps_reg']:.2f} eps_c={best['eps_cond']:.2f} "
          f"eta={best['eta']:.4f}")
    print(f"\nCSV parcial en {CSV}")


if __name__ == "__main__":
    main()