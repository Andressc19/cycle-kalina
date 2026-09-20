"""Fase 2 (tarea 2026-09-19-fase2-busqueda-libre) — confirmación con motor real.

Los 3 candidatos KALINA hallados con TeqpAdapter (etapa 1) se re-resuelven con
el motor real `AmmoniaWaterAdapter` (iapws G4-01, lento ~1-2 min/punto) para
verificar que la clasificación KALINA no es artefacto del motor rápido
(misma mecánica que la Fase B0: la discrepancia Teqp vs real ya se confirmó
antes en el bracket de T1 alto).

Candidatos (todo lo demás = defaults de CAMPOS_CICLO, T_fuente=470.0 K,
P_alta=3000 kPa, x_b=0.50, T_sumidero=300.032917, eta_t=0.85, eta_p=0.75,
eps_hrvg=0.85, eps_reg=0.75):
  (P_baja=450, eps_cond=0.99)  eta_teqp=0.12275
  (P_baja=500, eps_cond=0.98)  eta_teqp=0.11739
  (P_baja=500, eps_cond=0.99)  eta_teqp=0.11651

Guarda resultados/barridos_2026-09-19/fase2_libre/confirmacion_motor_real.json
(cada punto: convergio, clasificacion, mensaje y, si convergió, eta/Wnet).

NO modifica código de producción.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[3]  # ruta: scripts/barridos_2026-09-19/fase2_libre/
sys.path.insert(0, str(_RAIZ))

from src.cycle_solver import CicloNoConvergeError, resolver_ciclo
from src.properties.adapter import PropertyRangeError
from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter
from src.restricciones import evaluar_ciclo

CASO = dict(T_fuente=470.0, T_sumidero=300.032917, P_alta=3000.0, x_b=0.50,
            m_b=1.0, eta_t=0.85, eta_p=0.75, eps_hrvg=0.85, eps_reg=0.75)
PUNTOS = ((450.0, 0.99), (500.0, 0.98), (500.0, 0.99))  # (P_baja, eps_cond)
SALIDA = (_RAIZ / "resultados" / "barridos_2026-09-19" / "fase2_libre"
          / "confirmacion_motor_real.json")


def resolver_punto(backend, pb: float, eps_c: float) -> dict:
    combo = dict(CASO, P_baja=pb, eps_cond=eps_c)
    t0 = time.perf_counter()
    try:
        res = resolver_ciclo(backend, **combo)
    except (CicloNoConvergeError, PropertyRangeError) as exc:
        return dict(P_baja=pb, eps_cond=eps_c, convergio=False,
                    clasificacion="NO_CONVERGIO", mensaje=str(exc),
                    tiempo_s=round(time.perf_counter() - t0, 1))
    val = evaluar_ciclo(backend, res, P_alta=CASO["P_alta"], P_baja=pb,
                        T_fuente=CASO["T_fuente"], T_sumidero=CASO["T_sumidero"],
                        x_b=CASO["x_b"], m_b=CASO["m_b"],
                        eps_hrvg=CASO["eps_hrvg"], eps_reg=CASO["eps_reg"],
                        eps_cond=eps_c)
    return dict(P_baja=pb, eps_cond=eps_c, convergio=True,
                clasificacion=val.clasificacion.value, eta=res["eta"],
                Wnet=res["Wnet"], mensaje=val.mensaje_reporte(),
                tiempo_s=round(time.perf_counter() - t0, 1))


def main() -> None:
    print("Confirmación con motor real (AmmoniaWaterAdapter, iapws G4-01)...",
          flush=True)
    backend = AmmoniaWaterAdapter(x=0.50)
    registros = []
    for pb, eps_c in PUNTOS:
        print(f"\n-- P_baja={pb:.0f} kPa, eps_cond={eps_c:.2f} --", flush=True)
        r = resolver_punto(backend, pb, eps_c)
        print(f"  convergio={r['convergio']} "
              f"clasificacion={r['clasificacion']} ({r['tiempo_s']} s)",
              flush=True)
        print(f"  mensaje: {r['mensaje'][:300]}", flush=True)
        if r["convergio"]:
            print(f"  eta={r['eta']:.5f}  Wnet={r['Wnet']:.3f} kW", flush=True)
        registros.append(r)

    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump(dict(caso=CASO, puntos=registros), f, indent=2,
                  ensure_ascii=False)
    print(f"\nGuardado {SALIDA}")
    print("LISTO")


if __name__ == "__main__":
    main()