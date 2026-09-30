"""Fase 3 (tarea 2026-09-20-actualizar-rangos-fase2-fase3) — confirmación v2.

Re-resuelve el candidato KALINA de Húsavík hallado con TeqpAdapter en
busqueda_husavik_v2.py con el motor REAL AmmoniaWaterAdapter (iapws G4-01):

  P_alta=3300, P_baja=670, x_b=0.82, T_fuente=394.15, T_sumidero=278.15,
  eta_t=0.90, eta_p=0.80, eps_hrvg=0.85, eps_reg=0.95, eps_cond=0.95,
  T_amb_diseno=283.15 (piso realista de Islandia, decisión del director).

Evalúa además el mismo punto con el piso heredado 303.55 K para tener la
comparación like-for-like dentro del motor real — se espera CORREGIBLE (O2),
igual que en Teqp.

Guarda resultados/barridos_2026-09-19/fase3_real/confirmacion_motor_real_v2.json.
NO modifica código de producción.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_RAIZ))

from src.cycle_solver import CicloNoConvergeError, resolver_ciclo
from src.properties.adapter import PropertyRangeError
from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter
from src.restricciones import evaluar_ciclo

CASO = dict(P_alta=3300.0, P_baja=670.0, T_fuente=394.15, T_sumidero=278.15,
            x_b=0.82, m_b=1.0, eta_t=0.90, eta_p=0.80, eps_hrvg=0.85,
            eps_reg=0.95, eps_cond=0.95)
T_AMBS = (283.15, 303.55)
SALIDA = (_RAIZ / "resultados" / "barridos_2026-09-19" / "fase3_real"
          / "confirmacion_motor_real_v2.json")


def correr_punto(backend, tamb: float) -> dict:
    t0 = time.perf_counter()
    try:
        res = resolver_ciclo(backend, **CASO)
    except (CicloNoConvergeError, PropertyRangeError) as exc:
        return dict(T_amb_diseno=tamb, convergio=False,
                    clasificacion="NO_CONVERGIO", mensaje=str(exc),
                    tiempo_s=round(time.perf_counter() - t0, 1))
    val = evaluar_ciclo(backend, res, P_alta=CASO["P_alta"],
                        P_baja=CASO["P_baja"], T_fuente=CASO["T_fuente"],
                        T_sumidero=CASO["T_sumidero"], x_b=CASO["x_b"],
                        m_b=CASO["m_b"], eps_hrvg=CASO["eps_hrvg"],
                        eps_reg=CASO["eps_reg"], eps_cond=CASO["eps_cond"],
                        T_amb_diseno=tamb)
    est = res["estados"]
    return dict(T_amb_diseno=tamb, convergio=True,
                clasificacion=val.clasificacion.value, eta=res["eta"],
                Wnet=res["Wnet"], mensaje=val.mensaje_reporte(),
                T1=est["e1"].T, T2=est["e2"].T, T8=est["e8"].T,
                T9=est["e9"].T, x3=est["e3"].x, x5=est["e5"].x,
                m_v=est["e3"].m, m_l=est["e5"].m, Qi=res["Qi"],
                Qout=res["Qout"], tiempo_s=round(time.perf_counter() - t0, 1))


def main() -> None:
    print("Confirmación v2 con motor real (AmmoniaWaterAdapter, iapws "
          "G4-01)...", flush=True)
    backend = AmmoniaWaterAdapter(x=0.82)
    puntos = []
    for tamb in T_AMBS:
        print(f"\n-- T_amb_diseno={tamb} --", flush=True)
        r = correr_punto(backend, tamb)
        print(f"  {r['clasificacion']} ({(r.get('tiempo_s') or 0):.0f} s)",
              flush=True)
        print(f"  mensaje: {r['mensaje'][:220]}", flush=True)
        if r["convergio"]:
            print(f"  eta={r['eta']:.5f}  Wnet={r['Wnet']:.3f} kW "
                  f"T8={r['T8']:.2f} T9={r['T9']:.2f}", flush=True)
        puntos.append(r)

    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump(dict(caso=CASO, motor="AmmoniaWaterAdapter (iapws G4-01)",
                       puntos=puntos), f, indent=2, ensure_ascii=False)
    print(f"\nGuardado {SALIDA}")


if __name__ == "__main__":
    main()