"""Fase 2 (tarea 2026-09-20-actualizar-rangos-fase2-fase3) — confirmación v2.

Re-resuelve el candidato KALINA hallado con TeqpAdapter en
busqueda_libre_v2.py con el motor REAL AmmoniaWaterAdapter (iapws G4-01,
lento) para verificar que la clasificación KALINA no es artefacto del motor
rápido (misma mecánica que la iteración v1).

Candidato v2 (1 punto): P_baja=400, x_b=0.40, eps_cond=0.95, todo lo demás
en la base del profesor (P_alta=3000, T_fuente=470.0, T_sumidero=300.032917,
eta_t=0.85, eta_p=0.75, eps_hrvg=0.85, eps_reg=0.75), T_amb_diseno=303.55
(caso del profesor: su tabla real llega a 30.4 C; no se baja, ver v1).

Guarda resultados/barridos_2026-09-19/fase2_libre/confirmacion_motor_real_v2.json.
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

T_AMB_DISENO = 303.55
CASO = dict(P_alta=3000.0, T_fuente=470.0, T_sumidero=300.032917, m_b=1.0,
            eta_t=0.85, eta_p=0.75, eps_hrvg=0.85, eps_reg=0.75,
            P_baja=400.0, x_b=0.40, eps_cond=0.95)
SALIDA = (_RAIZ / "resultados" / "barridos_2026-09-19" / "fase2_libre"
          / "confirmacion_motor_real_v2.json")


def main() -> None:
    print("Confirmación v2 con motor real (AmmoniaWaterAdapter, iapws "
          "G4-01)...", flush=True)
    backend = AmmoniaWaterAdapter(x=0.40)
    t0 = time.perf_counter()
    try:
        res = resolver_ciclo(backend, **CASO)
        convergio = True
    except (CicloNoConvergeError, PropertyRangeError) as exc:
        r = dict(convergio=False, clasificacion="NO_CONVERGIO",
                 mensaje=str(exc), tiempo_s=round(time.perf_counter()-t0, 1))
    else:
        val = evaluar_ciclo(backend, res, P_alta=CASO["P_alta"],
                            P_baja=CASO["P_baja"], T_fuente=CASO["T_fuente"],
                            T_sumidero=CASO["T_sumidero"], x_b=CASO["x_b"],
                            m_b=CASO["m_b"], eps_hrvg=CASO["eps_hrvg"],
                            eps_reg=CASO["eps_reg"],
                            eps_cond=CASO["eps_cond"],
                            T_amb_diseno=T_AMB_DISENO)
        r = dict(convergio=True, clasificacion=val.clasificacion.value,
                 eta=res["eta"], Wnet=res["Wnet"],
                 mensaje=val.mensaje_reporte(),
                 tiempo_s=round(time.perf_counter()-t0, 1))
    print(f"  convergio={r['convergio']} "
          f"clasificacion={r['clasificacion']} ({r['tiempo_s']} s)",
          flush=True)
    print(f"  mensaje: {r['mensaje'][:300]}", flush=True)
    if r["convergio"]:
        print(f"  eta={r['eta']:.6f}  Wnet={r['Wnet']:.4f} kW", flush=True)

    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump(dict(caso=CASO, T_amb_diseno=T_AMB_DISENO, puntos=[r]),
                  f, indent=2, ensure_ascii=False)
    print(f"Guardado {SALIDA}")


if __name__ == "__main__":
    main()