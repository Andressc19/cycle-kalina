"""Fase 3 (tarea 2026-09-20-actualizar-rangos-fase2-fase3) — búsqueda v2.

Repite la calibración de P_baja (regla B0: bubble_point(P_baja, x_b=0.82) =
T_sumidero + 3 K = 281.15 K, NO cambia) pero evalúa O2 con el piso REALISTA
de Islandia: T_amb_diseno=283.15 K (10 C, margen conservador sobre los 5 C
reales de Húsavík — decisión del director, TASK_CONTEXT §Contexto) en vez del
piso tropical heredado 303.55 K.

Con TeqpAdapter se barre P_baja fino (paso 20 kPa) entre el mínimo calibrado
(~468 kPa) y el valor viejo (1200 kPa) buscando el P_baja MÍNIMO que ya pase
O2/KALINA — candidato de menor pinch. Base del caso real ya usada:
P_alta=3300, x_b=0.82, T_fuente=394.15, T_sumidero=278.15, m_b=1.0,
eta_t=0.90, eta_p=0.80, eps_hrvg=0.85. Dos líneas de efectividades:
- A (valores ya usados): eps_reg=0.95, eps_cond=0.95.
- B (defaults, mejora adicional a reportar): eps_reg=0.75, eps_cond=0.80 —
  solo en P_baja alrededor del mínimo hallado en A y hasta el primer KALINA.

Salida:
resultados/barridos_2026-09-19/fase3_real/busqueda_husavik_v2.csv
(NO toca los CSVs/historial v1: son comparables, no se sobrescriben.)

NO modifica codigo de produccion.
"""

from __future__ import annotations

import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
from scipy.optimize import brentq

_RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_RAIZ))

from src.cycle_solver import CicloNoConvergeError, resolver_ciclo
from src.properties.adapter import PropertyRangeError
from src.restricciones import evaluar_ciclo

T_AMB_DISENO = 283.15          # piso realista de diseno para Islandia (10 C)
T_FUENTE = 394.15
T_SUMIDERO = 278.15
DT_COND = 3.0
T_OBJ_COND = T_SUMIDERO + DT_COND
MB = 1.0
ETA_P = 0.80
N_WORKERS = 4
P_BAJA_MIN, P_BAJA_MAX = 50.0, 5000.0          # CAMPOS_CICLO
P_BAJA_BARRIDO = (470.0, 1200.0, 20.0)         # (desde, hasta, paso)
CSV = (_RAIZ / "resultados" / "barridos_2026-09-19" / "fase3_real"
       / "busqueda_husavik_v2.csv")
COLUMNAS = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "m_b",
            "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond",
            "T_sat_L", "T9_amb", "O2_margen", "pinch_K",
            "convergio", "clasificacion", "eta", "Wnet", "mensaje")
PALANCAS_A = dict(eta_t=0.90, eps_hrvg=0.85, eps_reg=0.95, eps_cond=0.95)
PALANCAS_B = dict(eta_t=0.90, eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.80)


def calibrar_p_baja(backend, xb: float) -> float:
    """P_baja tal que bubble_point(P_baja, x_b) = T_sumidero + 3 K (regla B0)."""
    f = lambda P: backend.bubble_point(P, xb) - T_OBJ_COND
    return float(brentq(f, P_BAJA_MIN, P_BAJA_MAX, xtol=1e-4))


def importar_backend():
    from src.properties.teqp_adapter import TeqpAdapter
    return TeqpAdapter(x=0.82)


def resolver_punto(pb: float, pal: dict) -> dict:
    """Resuelve + clasifica un punto (workers con su propio TeqpAdapter)."""
    from src.components.condensador import resolver as resolver_cond
    backend = importar_backend()
    combo = dict(P_alta=3300.0, P_baja=pb, T_fuente=T_FUENTE,
                 T_sumidero=T_SUMIDERO, x_b=0.82, m_b=MB, eta_p=ETA_P,
                 **pal)
    fila = dict(combo, T_sat_L=None, T9_amb=None, O2_margen=None, pinch_K=None)
    try:
        res = resolver_ciclo(backend, **combo)
    except (CicloNoConvergeError, PropertyRangeError) as exc:
        fila.update(convergio=False, clasificacion="NO_CONVERGIO", eta=None,
                    Wnet=None, mensaje=str(exc)[:300])
        return fila
    try:
        val = evaluar_ciclo(backend, res, P_alta=combo["P_alta"],
                            P_baja=combo["P_baja"], T_fuente=combo["T_fuente"],
                            T_sumidero=combo["T_sumidero"], x_b=combo["x_b"],
                            m_b=combo["m_b"], eps_hrvg=combo["eps_hrvg"],
                            eps_reg=combo["eps_reg"],
                            eps_cond=combo["eps_cond"],
                            T_amb_diseno=T_AMB_DISENO)
    except PropertyRangeError as exc:
        # Borde de dominio del motor al re-resolver el condensador en O2
        # (T9_amb pegado a la campana): se registra sin clasificar.
        fila.update(convergio=False, clasificacion="NO_CONVERGIO", eta=None,
                    Wnet=None, mensaje=f"evaluador O2 fuera de dominio: {exc}"[:300])
        return fila
    T_amb_evaluar = max(combo["T_sumidero"], T_AMB_DISENO)
    try:
        est9_amb, _ = resolver_cond(res["estados"]["e8"], backend,
                                    T_sumidero=T_amb_evaluar,
                                    eps=combo["eps_cond"], m=combo["m_b"])
        T_sat_L = backend.bubble_point(combo["P_baja"], combo["x_b"])
    except PropertyRangeError as exc:
        fila.update(convergio=True, clasificacion=val.clasificacion.value,
                    eta=res["eta"], Wnet=res["Wnet"],
                    mensaje=f"O2 diag fuera de dominio: {exc}"[:300])
        return fila
    fila.update(T_sat_L=T_sat_L, T9_amb=est9_amb.T,
                O2_margen=T_sat_L - est9_amb.T,
                pinch_K=T_sat_L - T_OBJ_COND)
    fila.update(convergio=True, clasificacion=val.clasificacion.value,
                eta=res["eta"], Wnet=res["Wnet"],
                mensaje=val.mensaje_reporte()[:300])
    return fila


def main() -> None:
    backend = importar_backend()
    pb_min_cal = calibrar_p_baja(backend, 0.82)
    print(f"P_baja minima calibrada (regla B0): {pb_min_cal:.1f} kPa",
          flush=True)

    desde, hasta, paso = P_BAJA_BARRIDO
    pbs_A = [p for p in range(int(desde), int(hasta) + 1, int(paso))]
    pbs_A = [max(p, pb_min_cal) for p in pbs_A if p >= pb_min_cal]
    specs_A = [(pb, PALANCAS_A) for pb in pbs_A]
    print(f"Linea A (eps_reg=0.95, eps_cond=0.95): {len(specs_A)} puntos "
          f"P_baja {min(pbs_A):.0f}-{max(pbs_A):.0f} kPa, "
          f"T_amb_diseno={T_AMB_DISENO} K", flush=True)

    t0 = time.perf_counter()
    filas = []
    with ProcessPoolExecutor(max_workers=N_WORKERS) as pool:
        futuros = [pool.submit(resolver_punto, *sp) for sp in specs_A]
        for n, fut in enumerate(as_completed(futuros), 1):
            filas.append(fut.result())
            if n % 6 == 0:
                print(f"  {n}/{len(specs_A)} ({time.perf_counter()-t0:.0f} s)",
                      flush=True)
    dt = time.perf_counter() - t0
    print(f"Linea A: {len(filas)} pts en {dt:.1f} s", flush=True)

    # Linea B (defaults) alrededor del minimo KALINA de A.
    kalina_A = sorted([f for f in filas if f["clasificacion"] == "KALINA"],
                      key=lambda f: f["P_baja"])
    if kalina_A:
        pb_nuevo = kalina_A[0]["P_baja"]
        pbs_B = [max(p, pb_min_cal) for p in
                 (pb_nuevo - 40.0, pb_nuevo - 20.0, pb_nuevo)]
        specs_B = [(pb, PALANCAS_B) for pb in pbs_B if pb >= pb_min_cal]
        print(f"Linea B (defaults eps_reg=0.75, eps_cond=0.80) en "
              f"P_baja={pbs_B}: {len(specs_B)} puntos", flush=True)
        with ProcessPoolExecutor(max_workers=N_WORKERS) as pool:
            futuros = [pool.submit(resolver_punto, *sp) for sp in specs_B]
            for fut in as_completed(futuros):
                filas.append(fut.result())

    df = pd.DataFrame(filas)[list(COLUMNAS)]
    CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CSV, index=False, encoding="utf-8")

    print(df["clasificacion"].value_counts().to_string(), flush=True)
    print("Ordenadas por P_baja (convergentes):", flush=True)
    for _, r in df.sort_values("P_baja").iterrows():
        if r["convergio"]:
            print(f"  P_baja={r['P_baja']:.0f} linea="
                  f"{'B' if r['eps_reg'] == 0.75 else 'A'} "
                  f"-> {r['clasificacion']} eta={r['eta']:.5f} "
                  f"pinch={r['pinch_K']:.2f} K O2={r['O2_margen']:+.2f} K",
                  flush=True)
    print(f"\nCSV guardado en {CSV}")


if __name__ == "__main__":
    main()