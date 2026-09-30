"""Fase 3 (tarea 2026-09-19-fase3-caso-real): confirmación de la base KALINA
de Húsavík con el motor REAL de propiedades (AmmoniaWaterAdapter, iapws
G4-01; lento, ~1-2 min/punto).

La base fue encontrada con TeqpAdapter (busqueda_base_husavik.py +
ajuste_p_baja_husavik.py) anclada al caso real:
  T_fuente=394.15 K, T_sumidero=278.15 K, x_b=0.82, P_alta=3300 kPa,
  eta_t=0.90, eta_p=0.80 (valores citados en la literatura del caso),
  eps_hrvg=0.85, eps_reg=0.95, eps_cond=0.95, P_baja=1200 kPa (calibrada:
  no publicada; margen de diseno frente al criterio O2).

Confirma 2 puntos (la base + el vecino mas eficiente) y guarda el resultado
en resultados/barridos_2026-09-19/fase3_real/confirmacion_motor_real.json.

NO modifica codigo de produccion.
"""

from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[3]  # script en scripts/.../fase3_real/
sys.path.insert(0, str(_RAIZ))

from src.cycle_solver import CicloNoConvergeError, resolver_ciclo
from src.properties.adapter import PropertyRangeError
from src.restricciones import evaluar_ciclo

T_FUENTE = 394.15
T_SUMIDERO = 278.15
MB = 1.0
ETA_P = 0.80
N_WORKERS = 2          # el motor real es lento; 2 workers evita saturar RAM
SALIDA = (_RAIZ / "resultados" / "barridos_2026-09-19" / "fase3_real"
          / "confirmacion_motor_real.json")

# (P_alta, P_baja, x_b, eta_t, eps_hrvg, eps_reg, eps_cond)
# Punto 1: la base definitiva. Punto 2: el vecino de mayor eficiencia.
PUNTOS = [
    (3300.0, 1200.0, 0.82, 0.90, 0.85, 0.95, 0.95),
    (3300.0, 1150.0, 0.82, 0.90, 0.85, 0.95, 0.98),
]


def importar_backend_real():
    from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter
    return AmmoniaWaterAdapter(x=0.82)


def resolver_punto(pa: float, pb: float, xb: float, eta_t: float, eps_h: float,
                   eps_r: float, eps_c: float) -> dict:
    backend = importar_backend_real()
    combo = dict(P_alta=pa, P_baja=pb, T_fuente=T_FUENTE,
                 T_sumidero=T_SUMIDERO, x_b=xb, m_b=MB, eta_t=eta_t,
                 eta_p=ETA_P, eps_hrvg=eps_h, eps_reg=eps_r, eps_cond=eps_c)
    t0 = time.perf_counter()
    try:
        res = resolver_ciclo(backend, **combo)
    except (CicloNoConvergeError, PropertyRangeError) as exc:
        return dict(P_alta=pa, P_baja=pb, x_b=xb, eta_t=eta_t,
                    eps_hrvg=eps_h, eps_reg=eps_r, eps_cond=eps_c,
                    convergio=False, clasificacion="NO_CONVERGIO",
                    eta=None, Wnet=None, mensaje=str(exc),
                    tiempo_s=round(time.perf_counter() - t0, 1))
    val = evaluar_ciclo(backend, res, P_alta=pa, P_baja=pb,
                        T_fuente=T_FUENTE, T_sumidero=T_SUMIDERO,
                        x_b=xb, m_b=MB, eps_hrvg=eps_h, eps_reg=eps_r,
                        eps_cond=eps_c)
    est = res["estados"]
    return dict(P_alta=pa, P_baja=pb, x_b=xb, eta_t=eta_t,
                eps_hrvg=eps_h, eps_reg=eps_r, eps_cond=eps_c,
                convergio=True, clasificacion=val.clasificacion.value,
                eta=res["eta"], Wnet=res["Wnet"],
                mensaje=val.mensaje_reporte(),
                T1=est["e1"].T, T2=est["e2"].T, T4=est["e4"].T,
                T8=est["e8"].T, T9=est["e9"].T, T10=est["e10"].T,
                x3=est["e3"].x, x5=est["e5"].x, m_v=est["e3"].m,
                m_l=est["e5"].m, Qi=res["Qi"], Qout=res["Qout"],
                tiempo_s=round(time.perf_counter() - t0, 1))


def main() -> None:
    print("Confirmacion con motor real (AmmoniaWaterAdapter, iapws G4-01)...",
          flush=True)
    registros = []
    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=N_WORKERS) as pool:
        futuros = [pool.submit(resolver_punto, *p) for p in PUNTOS]
        for fut in as_completed(futuros):
            r = fut.result()
            registros.append(r)
            print(f"  P_alta={r['P_alta']:.0f} P_baja={r['P_baja']:.0f} "
                  f"x_b={r['x_b']:.2f} eps_c={r['eps_cond']:.2f} -> "
                  f"{r['clasificacion']} ({r['tiempo_s']} s)", flush=True)
            if r["convergio"]:
                print(f"    eta={r['eta']:.5f} Wnet={r['Wnet']:.2f} kW", flush=True)

    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump(dict(
            motor="AmmoniaWaterAdapter (iapws G4-01)",
            caso=dict(T_fuente=T_FUENTE, T_sumidero=T_SUMIDERO, m_b=MB,
                      eta_p=ETA_P, fuente_caso="Husavik 121C / 5C, Mlcak et al."),
            puntos=sorted(registros, key=lambda r: -r["tiempo_s"]),
        ), f, indent=2, ensure_ascii=False)
    print(f"\nGuardado {SALIDA}")
    print(f"Tiempo total: {time.perf_counter()-t0:.0f} s")


if __name__ == "__main__":
    main()