"""Fase 3 (tarea 2026-09-20-fase3-confirma-690) — confirmación del ANCLA final.

El director eligió como candidato ANCLA 690/0.75/0.95 (robustez: margen O2
+1.19 K en vez de +0.30 K del 670; realismo: eps_reg=0.75 default en vez del
forzado 0.95). Ese punto SOLO se probó con TeqpAdapter (eta~0.12732, tabla de
diagnostico de CASO_HUSAVIK_v2.md §2) y este script lo confirma con el motor
REAL AmmoniaWaterAdapter (iapws G4-01):

  P_alta=3300, P_baja=690, x_b=0.82, T_fuente=394.15, T_sumidero=278.15,
  m_b=1.0, eta_t=0.90, eta_p=0.80, eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.95,
  T_amb_diseno=283.15 (piso realista de Islandia).

Ademas re-resuelve el mismo punto con TeqpAdapter para la comparacion
like-for-like (motor real vs Teqp, misma regla que v2) y reporta la diferencia
relativa de eta/Wnet.

Guarda resultados/barridos_2026-09-19/fase3_real/confirmacion_motor_real_690.json
(mismo esquema que confirmacion_motor_real_v2.json: caso/motor/puntos).
NO modifica codigo de produccion. NO toca fase2_libre/ (tarea paralela).
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
from src.restricciones import evaluar_ciclo

CASO = dict(P_alta=3300.0, P_baja=690.0, T_fuente=394.15, T_sumidero=278.15,
            x_b=0.82, m_b=1.0, eta_t=0.90, eta_p=0.80, eps_hrvg=0.85,
            eps_reg=0.75, eps_cond=0.95)
T_AMB_DISENO = 283.15
SALIDA = (_RAIZ / "resultados" / "barridos_2026-09-19" / "fase3_real"
          / "confirmacion_motor_real_690.json")


def correr_punto(nombre: str, backend) -> dict:
    t0 = time.perf_counter()
    try:
        res = resolver_ciclo(backend, **CASO)
    except (CicloNoConvergeError, PropertyRangeError) as exc:
        print(f"  [{nombre}] NO_CONVERGIO: {exc}", flush=True)
        return dict(motor=nombre, convergio=False,
                    clasificacion="NO_CONVERGIO", mensaje=str(exc),
                    tiempo_s=round(time.perf_counter() - t0, 1))
    val = evaluar_ciclo(backend, res, P_alta=CASO["P_alta"],
                        P_baja=CASO["P_baja"], T_fuente=CASO["T_fuente"],
                        T_sumidero=CASO["T_sumidero"], x_b=CASO["x_b"],
                        m_b=CASO["m_b"], eps_hrvg=CASO["eps_hrvg"],
                        eps_reg=CASO["eps_reg"], eps_cond=CASO["eps_cond"],
                        T_amb_diseno=T_AMB_DISENO)
    est = res["estados"]
    punto = dict(motor=nombre, convergio=True,
                 clasificacion=val.clasificacion.value, eta=res["eta"],
                 Wnet=res["Wnet"], mensaje=val.mensaje_reporte(),
                 T1=est["e1"].T, T2=est["e2"].T, T8=est["e8"].T,
                 T9=est["e9"].T, x3=est["e3"].x, x5=est["e5"].x,
                 m_v=est["e3"].m, m_l=est["e5"].m, Qi=res["Qi"],
                 Qout=res["Qout"], tiempo_s=round(time.perf_counter() - t0, 1))
    print(f"  [{nombre}] {punto['clasificacion']} "
          f"eta={punto['eta']:.5f} Wnet={punto['Wnet']:.3f} kW "
          f"({punto['tiempo_s']:.0f} s)", flush=True)
    print(f"    mensaje: {punto['mensaje'][:200]}", flush=True)
    return punto


def main() -> None:
    print("Confirmacion ANCLA 690/0.75/0.95 - T_amb_diseno=283.15 K",
          flush=True)

    # 1) Motor REAL (referencia oficial del informe).
    from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter
    print("\n-- Motor real (AmmoniaWaterAdapter, iapws G4-01) --", flush=True)
    real = correr_punto("AmmoniaWaterAdapter", AmmoniaWaterAdapter(x=0.82))

    # 2) Mismo punto con TeqpAdapter (comparacion like-for-like, ~segundos).
    from src.properties.teqp_adapter import TeqpAdapter
    print("\n-- Referencia TeqpAdapter --", flush=True)
    teqp = correr_punto("TeqpAdapter", TeqpAdapter(x=0.82))

    # 3) Comparacion relativa.
    if real["convergio"] and teqp["convergio"]:
        d_eta = (real["eta"] - teqp["eta"]) / teqp["eta"] * 100.0
        d_wnet = (real["Wnet"] - teqp["Wnet"]) / teqp["Wnet"] * 100.0
        print(f"\nDif. relativa motor real vs Teqp: "
              f"eta {d_eta:+.4f} %   Wnet {d_wnet:+.4f} %", flush=True)
    else:
        d_eta = d_wnet = None

    # 4) Guardar JSON con el esquema de confirmacion_motor_real_v2.json
    #    (caso/motor/puntos; solo el punto real de T_amb_diseno de la tarea).
    puntos = []
    if real["convergio"]:
        puntos.append(dict(T_amb_diseno=T_AMB_DISENO, **{
            k: real[k] for k in ("convergio", "clasificacion", "eta", "Wnet",
                                 "mensaje", "T1", "T2", "T8", "T9", "x3",
                                 "x5", "m_v", "m_l", "Qi", "Qout", "tiempo_s")}))
    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump(dict(caso={k: CASO[k] for k in
                             ("P_alta", "P_baja", "T_fuente", "T_sumidero",
                              "x_b", "m_b", "eta_t", "eta_p", "eps_hrvg",
                              "eps_reg", "eps_cond")},
                       motor="AmmoniaWaterAdapter (iapws G4-01)",
                       puntos=puntos), f, indent=2, ensure_ascii=False)
    print(f"\nGuardado {SALIDA}", flush=True)


if __name__ == "__main__":
    main()