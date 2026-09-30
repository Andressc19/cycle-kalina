"""Fase B0 (tarea 2026-09-19-b0-scan-base-cementera): escaneo grueso de la
base realista del caso cementera.

T_fuente=583.15 K y T_sumidero=300.032917 K fijos (caso cementera,
precalentador a 310 °C). Barre (P_alta, x_b, eps_hrvg) dentro del rango
realista de la literatura P_alta in [2000, 7000] kPa (NO se sube de 7000:
ver TASK_CONTEXT punto 2 — decisión ya tomada), fija P_baja por combinación
con bubble_point(P_baja, x_b) = T_sumidero + 3 K (único supuesto físico nuevo,
autorizado por el director) y registra CADA punto probado, converja o no, en
resultados/barridos_2026-09-19/b0_scan_cementera.csv.

eta_t=0.85, eta_p=0.75, eps_reg=0.75, eps_cond=0.80 (defaults de CONTEXT.md):
solo se abrirán a barrido si la evidencia lo pide (TASK_CONTEXT paso 4).

Cada punto corre el `resolver_ciclo` REAL (con TeqpAdapter). El escaneo se
paraleliza con ProcessPoolExecutor (Windows usa spawn): la función de trabajo
es de nivel de módulo y los workers crean su propio backend, por lo que el
resultado es idéntico al secuencial.

NO modifica código de producción (solo consume src/ como librería).
"""

from __future__ import annotations

import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
from scipy.optimize import brentq

_RAIZ = Path(__file__).resolve().parents[2]  # script vive en scripts/barridos_2026-09-19/
sys.path.insert(0, str(_RAIZ))

from src.cycle_solver import CicloNoConvergeError, resolver_ciclo
from src.properties.adapter import PropertyRangeError
from src.restricciones import evaluar_ciclo

# -- constantes del caso (TASK_CONTEXT / CONTEXT.md) --------------------------
T_FUENTE = 583.15
T_SUMIDERO = 300.032917
DT_COND = 3.0                      # supuesto autorizado (TASK_CONTEXT paso 3)
T_OBJ_COND = T_SUMIDERO + DT_COND
MB = 1.0
ETA_T, ETA_P = 0.85, 0.75          # defaults CONTEXT.md
EPS_REG, EPS_COND = 0.75, 0.80     # defaults CONTEXT.md
P_ALTA_MIN, P_ALTA_MAX, PASO_P = 2000.0, 7000.0, 500.0
X_MIN, X_MAX, PASO_X = 0.35, 0.70, 0.05
EPS_GRID = (0.50, 0.65, 0.80, 0.90)
P_BAJA_MIN, P_BAJA_MAX = 50.0, 5000.0   # límites CAMPOS_CICLO
N_WORKERS = 4
CSV = (_RAIZ / "resultados" / "barridos_2026-09-19"
       / "b0_scan_cementera.csv")
COLUMNAS = ("P_alta", "P_baja", "x_b", "eta_t", "eta_p", "eps_hrvg",
            "eps_reg", "eps_cond", "convergio", "clasificacion", "eta",
            "Wnet", "mensaje")


def rejilla_p_alta() -> list[float]:
    return [float(v) for v in range(int(P_ALTA_MIN), int(P_ALTA_MAX) + 1,
                                    int(PASO_P))]


def rejilla_x_b() -> list[float]:
    n = int(round((X_MAX - X_MIN) / PASO_X)) + 1
    return [round(X_MIN + i * PASO_X, 6) for i in range(n)]


def calibrar_p_baja(backend, xb: float) -> tuple[float, str]:
    """P_baja tal que bubble_point(P_baja, x_b) = T_sumidero + 3 K
    (ΔT_app,cond≈3 K, único supuesto físico nuevo — autorizado)."""
    f = lambda P: backend.bubble_point(P, xb) - T_OBJ_COND
    pb = brentq(f, P_BAJA_MIN, P_BAJA_MAX, xtol=1e-4)
    return float(pb), "raiz"


# -- trabajo por worker --------------------------------------------------------
def importar_backend():
    from src.properties.teqp_adapter import TeqpAdapter
    return TeqpAdapter(x=0.5)


def anotar_sonda(bub: float, dew: float, t2: float) -> str:
    """Clasifica la sonda del bracket contra la campana (P_alta, x_b)."""
    if t2 < bub:
        return (f"T2_sonda={t2:.1f} K < bubble={bub:.1f} K (liquido: sonda "
                f"T1 del arranque del bracket cae fuera de campana)")
    if t2 > dew:
        return (f"T2_sonda={t2:.1f} K > dew={dew:.1f} K (sobrecalentado: "
                f"sonda T1 del arranque del bracket pega el estado 2 fuera "
                f"de campana)")
    return (f"T2_sonda={t2:.1f} K DENTRO de campana [{bub:.1f},{dew:.1f}] K — "
            "SOSPECHOSO de limitacion numerica del motor rapido (no estructural)")


def mensaje_fallo(exc, pa: float, pb: float, bub: float, dew: float) -> str:
    """Clasifica el fallo contra (a) la campana de la sonda del bracket (P_alta)
    o (b) el lado frio (P_baja, cobertura del motor teqp) según la presion que
    aparece en el mensaje de la excepcion."""
    m = str(exc)
    if "lazo interior (frio) no convergio" in m:
        prefijo = ("lazo_frio_no_conv (sin P/T): el lazo interior frio no "
                   "convergio en la 1a evaluacion del bracket — no es un "
                   "estado de campana")
        return f"{prefijo} || {m}"[:400]
    mm_p = re.search(r"P=([0-9.eE+\-]+)\s*(kPa|Pa)", m)
    mm_t = re.search(r"T=([0-9.]+)", m)
    if mm_p:
        p = float(mm_p.group(1))
        if mm_p.group(2) == "Pa":
            p = p / 1000.0  # normaliza a kPa
        if abs(p - pb) < 0.02 * pb + 0.5:   # estado del lado frio (P_baja)
            t = (f"T={float(mm_t.group(1)):.1f} K, ") if mm_t else ""
            prefijo = (f"lado_frio(P_baja={pb:.1f} kPa, {t}estado fuera del "
                       f"dominio/cobertura del motor teqp — sin relacion "
                       f"con la campana de la sonda")
        elif abs(p - pa) < 0.02 * pa + 0.5:  # estado de la sonda (P_alta)
            if mm_t:
                prefijo = ("bracket_sonda: "
                           + anotar_sonda(bub, dew, float(mm_t.group(1))))
            else:
                prefijo = "sonda T1 no identificada en el mensaje"
        else:
            prefijo = f"otra_ubicacion(P={p:.5g} kPa)"
    else:
        prefijo = "sonda T1 no identificada en el mensaje"
    return f"{prefijo} || {m}"[:400]


def resolver_punto(pa: float, pb: float, xb: float, eps_h: float,
                   bub: float, dew: float) -> dict:
    backend = importar_backend()
    combo = dict(P_alta=pa, P_baja=pb, T_fuente=T_FUENTE,
                 T_sumidero=T_SUMIDERO, x_b=xb, m_b=MB, eta_t=ETA_T,
                 eta_p=ETA_P, eps_hrvg=eps_h, eps_reg=EPS_REG,
                 eps_cond=EPS_COND)
    fila = dict(P_alta=pa, P_baja=pb, x_b=xb, eta_t=ETA_T, eta_p=ETA_P,
                eps_hrvg=eps_h, eps_reg=EPS_REG, eps_cond=EPS_COND)
    try:
        res = resolver_ciclo(backend, **combo)
    except (CicloNoConvergeError, PropertyRangeError) as exc:
        fila.update(convergio=False, clasificacion="NO_CONVERGIO",
                    eta=None, Wnet=None,
                    mensaje=mensaje_fallo(exc, pa, pb, bub, dew))
        return fila
    val = evaluar_ciclo(backend, res, P_alta=pa, P_baja=pb,
                        T_fuente=T_FUENTE, T_sumidero=T_SUMIDERO,
                        x_b=xb, m_b=MB, eps_hrvg=eps_h, eps_reg=EPS_REG,
                        eps_cond=EPS_COND)
    fila.update(convergio=True, clasificacion=val.clasificacion.value,
                eta=res["eta"], Wnet=res["Wnet"], mensaje=val.mensaje_reporte())
    return fila


# -- orquestador ---------------------------------------------------------------
def main() -> None:
    backend = importar_backend()

    # Precomputo (una sola vez) de dews/bubbles y P_baja por (P_alta, x_b).
    campana: dict[tuple, tuple] = {}
    p_bajas: dict[float, float] = {}
    for xb in rejilla_x_b():
        p_bajas[xb], _ = calibrar_p_baja(backend, xb)
        for pa in rejilla_p_alta():
            campana[(pa, xb)] = (backend.bubble_point(pa, xb),
                                 backend.dew_point(pa, xb))
    print(f"Precomputo de campana/P_baja listo "
          f"({len(campana)} pares (P,x)).", flush=True)

    specs = []
    for pa in rejilla_p_alta():
        for xb in rejilla_x_b():
            bub, dew = campana[(pa, xb)]
            for eps_h in EPS_GRID:
                specs.append((pa, p_bajas[xb], xb, eps_h, bub, dew))
    print(f"Puntos a evaluar: {len(specs)} (rejilla 11 x 8 x 4 = 352) con "
          f"{N_WORKERS} workers...", flush=True)

    filas = []
    t0 = time.perf_counter()
    n_hechos = 0
    with ProcessPoolExecutor(max_workers=N_WORKERS) as pool:
        futuros = [pool.submit(resolver_punto, *sp) for sp in specs]
        for fut in as_completed(futuros):
            filas.append(fut.result())
            n_hechos += 1
            if n_hechos % 25 == 0:
                print(f"  {n_hechos}/{len(specs)} puntos "
                      f"({time.perf_counter() - t0:.0f} s)", flush=True)
    dt = time.perf_counter() - t0

    df = pd.DataFrame(filas)[list(COLUMNAS)]
    df = df.sort_values(["P_alta", "x_b", "eps_hrvg"])
    df.to_csv(CSV, index=False, encoding="utf-8")

    print(f"\nPuntos evaluados: {len(filas)} en {dt:.1f} s "
          f"({dt / len(filas):.2f} s/punto)", flush=True)
    print("Distribución por clasificación:")
    print(df["clasificacion"].value_counts().to_string())
    print(f"Convergencias: {int(df['convergio'].sum())}")

    print("\nMejores candidatos (máximo rocío = más cerca de ser válidos):")
    pares = sorted(set(campana), key=lambda t: -campana[t][1])
    for pa, xb in pares[:6]:
        bub, dew = campana[(pa, xb)]
        print(f"  P_alta={pa:5.0f} kPa x_b={xb:.2f}: bubble={bub:.1f} K, "
              f"dew={dew:.1f} K  (T_fuente={T_FUENTE:.2f} K, sonda_hi="
              f"{T_FUENTE - 1:.2f} K)")
    print(f"\nCSV guardado en {CSV}")


if __name__ == "__main__":
    main()