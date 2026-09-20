"""Fase 3 (Husavik) — tablas del punto ANCLA (entregable A).

Tarea 2026-09-20-fase3-sensibilidad-final. El ancla
(3300/690/0.82/394.15/278.15/1.0/0.90/0.80/0.85/0.75/0.95 con
T_amb_diseno=283.15) YA esta confirmada con el motor real: KALINA,
eta=0.12730 (confirmacion_motor_real_690.json) — se cita ese valor y NO se
re-corre el motor real.

Para las tablas de estados y balance se resuelve el ancla UNA vez con
TeqpAdapter (rapido, ~segundos; el mismo punto con Teqp da eta=0.12732,
-0.02 % vs motor real — ver CASO_HUSAVIK_v2.md §1.0) y se anota al lado el
valor oficial citado con motor real cuando existe en el JSON.

Salida: resultados/barridos_2026-09-19/fase3_real/ancla_estados.csv y
ancla_balance.csv. NO modifica codigo de produccion.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

_RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_RAIZ))

from src.cycle_solver import CicloNoConvergeError, resolver_ciclo  # noqa: E402
from src.properties.adapter import PropertyRangeError  # noqa: E402
from src.restricciones import evaluar_ciclo  # noqa: E402

RESULTADOS = _RAIZ / "resultados" / "barridos_2026-09-19" / "fase3_real"
CASO = dict(P_alta=3300.0, P_baja=690.0, x_b=0.82, T_fuente=394.15,
            T_sumidero=278.15, m_b=1.0, eta_t=0.90, eta_p=0.80,
            eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.95)
T_AMB_DISENO = 283.15
ETA_MOTOR_REAL = 0.12730          # citado, confirmacion_motor_real_690.json
ETIQUETAS = {"e1": "1", "e2": "2", "e3": "3", "e4": "4", "e5": "5",
             "e6": "6", "e7": "7", "e8": "8", "e9": "9", "e10": "10"}


def _num(valor, cifras):
    return "—" if valor is None else round(valor, cifras)


def main() -> None:
    # Citas oficiales con motor real (JSON de confirmacion ya generado).
    with open(RESULTADOS / "confirmacion_motor_real_690.json", encoding="utf-8") as f:
        confirm = json.load(f)
    oficial = confirm["puntos"][0]
    print(f"Ancla confirmada (motor real, citada): {oficial['clasificacion']} "
          f"eta={oficial['eta']:.5f}  (NO se re-corre)", flush=True)

    # Tabla de estados: una sola corrida con TeqpAdapter (~segundos).
    from src.properties.teqp_adapter import TeqpAdapter
    backend = TeqpAdapter(x=CASO["x_b"])
    try:
        resultado = resolver_ciclo(backend, **CASO)
    except (CicloNoConvergeError, PropertyRangeError) as exc:
        raise SystemExit(f"el ancla no converge con TeqpAdapter: {exc}")
    val = evaluar_ciclo(backend, resultado, P_alta=CASO["P_alta"],
                        P_baja=CASO["P_baja"], T_fuente=CASO["T_fuente"],
                        T_sumidero=CASO["T_sumidero"], x_b=CASO["x_b"],
                        m_b=CASO["m_b"], eps_hrvg=CASO["eps_hrvg"],
                        eps_reg=CASO["eps_reg"], eps_cond=CASO["eps_cond"],
                        T_amb_diseno=T_AMB_DISENO)
    print(f"Ancla con TeqpAdapter: {val.clasificacion.value} "
          f"eta={resultado['eta']:.5f}", flush=True)

    # ancla_estados.csv — los 10 estados (motor: TeqpAdapter; ancla oficial
    # citada arriba, no se vuelve a correr con el motor real).
    filas = []
    for clave, etiqueta in ETIQUETAS.items():
        e = resultado["estados"][clave]
        filas.append({"Estado": etiqueta, "T [K]": round(e.T, 3),
                      "P [kPa]": round(e.P, 3), "h [kJ/kg]": round(e.h, 3),
                      "s [kJ/kg·K]": round(e.s, 5),
                      "x (NH3) [-]": round(e.x, 5),
                      "m [kg/s]": _num(e.m, 5), "q [-]": _num(e.q, 5),
                      "Fase": e.fase or "—",
                      "motor": "TeqpAdapter"})
    pd.DataFrame(filas).to_csv(RESULTADOS / "ancla_estados.csv", index=False,
                               encoding="utf-8")

    # ancla_balance.csv — balance Teqp + valores oficiales citados del motor
    # real (Qi/Qout/Wnet/eta si estan publicados en el JSON; Wt y Wp no se
    # volcaron ahi).
    N2_abs = abs(resultado["Qi"] - resultado["Qout"] - resultado["Wnet"])
    N2_lim = 1e-3 * abs(resultado["Qi"])
    filas = [
        {"magnitud": "Qi [kW]", "valor_teqp": round(resultado["Qi"], 4),
         "motor_real_citado": round(oficial["Qi"], 4)},
        {"magnitud": "Qout [kW]", "valor_teqp": round(resultado["Qout"], 4),
         "motor_real_citado": round(oficial["Qout"], 4)},
        {"magnitud": "Wt [kW]", "valor_teqp": round(resultado["Wt"], 4),
         "motor_real_citado": None},
        {"magnitud": "Wp [kW]", "valor_teqp": round(resultado["Wp"], 4),
         "motor_real_citado": None},
        {"magnitud": "Wnet [kW]", "valor_teqp": round(resultado["Wnet"], 4),
         "motor_real_citado": round(oficial["Wnet"], 4)},
        {"magnitud": "eta [-]", "valor_teqp": round(resultado["eta"], 6),
         "motor_real_citado": round(oficial["eta"], 6)},
        {"magnitud": "N2 |Qi-Qout-Wnet| [kW]", "valor_teqp": round(N2_abs, 6),
         "motor_real_citado": None},
        {"magnitud": "N2 limite 1e-3*Qi [kW]", "valor_teqp": round(N2_lim, 6),
         "motor_real_citado": None},
        {"magnitud": "N2 cumple (<= limite)", "valor_teqp": N2_abs <= N2_lim,
         "motor_real_citado": None},
    ]
    pd.DataFrame(filas).to_csv(RESULTADOS / "ancla_balance.csv", index=False,
                               encoding="utf-8")
    print(f"N2 verificado: |Qi-Qout-Wnet|={N2_abs:.3g} kW <= "
          f"1e-3*Qi={N2_lim:.3g} kW -> {N2_abs <= N2_lim}", flush=True)
    print(f"guardados {RESULTADOS / 'ancla_estados.csv'} y "
          f"{RESULTADOS / 'ancla_balance.csv'} (eta oficial citada = "
          f"{ETA_MOTOR_REAL})", flush=True)


if __name__ == "__main__":
    main()