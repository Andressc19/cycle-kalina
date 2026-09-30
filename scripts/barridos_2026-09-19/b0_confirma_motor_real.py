"""Fase B0 — confirmación de los mejores candidatos con el motor real
(`AmmoniaWaterAdapter`, iapws G4-01; lento, ~1-2 min/punto).

Tarea 2026-09-19-b0-scan-base-cementera, paso 6 del approach: si ningún punto
del escaneo grueso (TeqpAdapter) clasifica KALINA, confirmar los 1-3 mejores
candidatos con el motor real y reportar la discrepancia tal cual (si la hay).

Los "mejores" candidatos cuando nada converge son los de máximo rocío a
P_alta <= 7000 kPa (más cerca de tener el estado 2 dentro de la campana):
(7000 kPa, x_b=0.35) y (6500 kPa, x_b=0.35), con el eps_hrvg más bajo de la
rejilla (0.50) y el siguiente (0.65) — el eps más bajo es la palanca que más
aleja el estado 2 real del borde de la campana.

Guarda el resultado en resultados/barridos_2026-09-19/
b0_confirmacion_motor_real.json (cada punto: convergio, clasificacion,
mensaje y, si convergió, eta/Wnet).

NO modifica código de producción.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from scipy.optimize import brentq

_RAIZ = Path(__file__).resolve().parents[2]  # script vive en scripts/barridos_2026-09-19/
sys.path.insert(0, str(_RAIZ))

from src.cycle_solver import CicloNoConvergeError, resolver_ciclo
from src.properties.adapter import PropertyRangeError
from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter
from src.restricciones import evaluar_ciclo

T_FUENTE = 583.15
T_SUMIDERO = 300.032917
DT_COND = 3.0
T_OBJ_COND = T_SUMIDERO + DT_COND
MB = 1.0
ETA_T, ETA_P = 0.85, 0.75
EPS_REG, EPS_COND = 0.75, 0.80
P_BAJA_MIN, P_BAJA_MAX = 50.0, 5000.0
SALIDA = (_RAIZ / "resultados" / "barridos_2026-09-19"
          / "b0_confirmacion_motor_real.json")

# (P_alta kPa, x_b, eps_hrvg) — máximos rocío del escaneo grueso
PUNTOS = ((7000.0, 0.35, 0.50), (7000.0, 0.35, 0.65), (6500.0, 0.35, 0.50))


def calibrar_p_baja(backend, x_b: float) -> float:
    f = lambda P: backend.bubble_point(P, x_b) - T_OBJ_COND
    return brentq(f, P_BAJA_MIN, P_BAJA_MAX, xtol=1e-4)


def resolver_punto(backend, pa: float, pb: float, xb: float,
                   eps_h: float) -> dict:
    combo = dict(P_alta=pa, P_baja=pb, T_fuente=T_FUENTE,
                 T_sumidero=T_SUMIDERO, x_b=xb, m_b=MB, eta_t=ETA_T,
                 eta_p=ETA_P, eps_hrvg=eps_h, eps_reg=EPS_REG,
                 eps_cond=EPS_COND)
    t0 = time.perf_counter()
    try:
        res = resolver_ciclo(backend, **combo)
    except (CicloNoConvergeError, PropertyRangeError) as exc:
        return dict(convergio=False, clasificacion="NO_CONVERGIO",
                    mensaje=str(exc), tiempo_s=round(time.perf_counter() - t0, 1))
    val = evaluar_ciclo(backend, res, P_alta=pa, P_baja=pb,
                        T_fuente=T_FUENTE, T_sumidero=T_SUMIDERO,
                        x_b=xb, m_b=MB, eps_hrvg=eps_h, eps_reg=EPS_REG,
                        eps_cond=EPS_COND)
    return dict(convergio=True, clasificacion=val.clasificacion.value,
                eta=res["eta"], Wnet=res["Wnet"],
                mensaje=val.mensaje_reporte(),
                tiempo_s=round(time.perf_counter() - t0, 1))


def main() -> None:
    print("Confirmación con motor real (AmmoniaWaterAdapter, iapws G4-01)...",
          flush=True)
    backend = AmmoniaWaterAdapter(x=0.35)
    registros = []
    for pa, xb, eps_h in PUNTOS:
        pb = calibrar_p_baja(backend, xb)
        print(f"\n-- P_alta={pa:.0f} kPa, x_b={xb:.2f}, eps_hrvg={eps_h:.2f}, "
              f"P_baja={pb:.1f} kPa --", flush=True)
        r = resolver_punto(backend, pa, pb, xb, eps_h)
        print(f"  convergio={r['convergio']} "
              f"clasificacion={r['clasificacion']} ({r['tiempo_s']} s)",
              flush=True)
        print(f"  mensaje: {r['mensaje'][:300]}", flush=True)
        if r["convergio"]:
            print(f"  eta={r['eta']:.5f}  Wnet={r['Wnet']:.3f} kW", flush=True)
        registros.append(dict(P_alta=pa, P_baja=pb, x_b=xb, eps_hrvg=eps_h,
                              **r))

    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump(dict(caso=dict(T_fuente=T_FUENTE, T_sumidero=T_SUMIDERO,
                                 DT_COND=DT_COND, eta_t=ETA_T, eta_p=ETA_P,
                                 eps_reg=EPS_REG, eps_cond=EPS_COND,
                                 m_b=MB), puntos=registros), f, indent=2,
                  ensure_ascii=False)
    print(f"\nGuardado {SALIDA}")
    print("LISTO")


if __name__ == "__main__":
    main()