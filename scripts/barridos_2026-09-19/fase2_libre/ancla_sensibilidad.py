"""Fase 2 (tarea 2026-09-20-fase2-sensibilidad-final) — entregable A: tablas
del punto ancla.

El ancla (P_alta=3000, P_baja=400, x_b=0.40, T_fuente=470.0,
T_sumidero=300.032917, m_b=1.0, eta_t=0.85, eta_p=0.75, eps_hrvg=0.85,
eps_reg=0.75, eps_cond=0.95, T_amb_diseno=303.55) YA fue confirmado con el
motor real (eta=0.124296, KALINA — confirmacion_motor_real_v2.json): se cita,
NO se vuelve a correr el motor real. Las tablas de estados se generan con el
motor rapido TeqpAdapter (el que usa todo el barrido) resolviendo el ancla
una sola vez:

- ancla_estados.csv: los 10 estados (T, P, h, s, x, m, q, fase), con
  fase/titulo evaluados por `fase_de` (P,T,x) — misma mecanica que la
  clasificacion O1/O5.
- ancla_balance.csv: Qi, Qout, Wt, Wp, Wnet, eta + verificacion de cierre N2
  (|Qi-Qout-Wnet| <= 1e-3·Qi) y la referencia del motor real (citada).

NO toca codigo de produccion; NO toca fase3_real/ ni fase1_profesor/.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

_RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_RAIZ))

from src.cycle_solver import resolver_ciclo  # noqa: E402
from src.properties.teqp_adapter import TeqpAdapter  # noqa: E402
from src.restricciones import evaluar_ciclo  # noqa: E402
from src.restricciones.numericos import _TOL  # noqa: E402  (1e-3 relativo de N2)

T_AMB_DISENO = 303.55
ANCLA = dict(P_alta=3000.0, P_baja=400.0, x_b=0.40, T_fuente=470.0,
             T_sumidero=300.032917, m_b=1.0, eta_t=0.85, eta_p=0.75,
             eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.95)
FASE2 = _RAIZ / "resultados" / "barridos_2026-09-19" / "fase2_libre"
NUEVE = ("e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8", "e9", "e10")


def tabla_estados(backend, res) -> pd.DataFrame:
    filas = []
    for clave in NUEVE:
        e = res["estados"][clave]
        fase, q = backend.fase_de(e.P, e.T, e.x)
        filas.append({
            "Estado": clave, "T [K]": round(e.T, 2),
            "P [kPa]": round(e.P, 2), "h [kJ/kg]": round(e.h, 2),
            "s [kJ/kg·K]": round(e.s, 4), "x (NH3) [-]": round(e.x, 4),
            "m [kg/s]": (round(e.m, 4) if e.m is not None else None),
            "q [-]": round(q, 4), "Fase": fase,
        })
    return pd.DataFrame(filas)


def main() -> None:
    FASE2.mkdir(parents=True, exist_ok=True)
    backend = TeqpAdapter(x=ANCLA["x_b"])
    res = resolver_ciclo(backend, **ANCLA)
    val = evaluar_ciclo(backend, res, P_alta=ANCLA["P_alta"],
                        P_baja=ANCLA["P_baja"], T_fuente=ANCLA["T_fuente"],
                        T_sumidero=ANCLA["T_sumidero"], x_b=ANCLA["x_b"],
                        m_b=ANCLA["m_b"], eps_hrvg=ANCLA["eps_hrvg"],
                        eps_reg=ANCLA["eps_reg"], eps_cond=ANCLA["eps_cond"],
                        T_amb_diseno=T_AMB_DISENO)

    tabla_estados(backend, res).to_csv(
        FASE2 / "ancla_estados.csv", index=False, encoding="utf-8")

    Qi, Qout, Wt, Wp = res["Qi"], res["Qout"], res["Wt"], res["Wp"]
    Wnet, eta = res["Wnet"], res["eta"]
    residuo = abs(Qi - Qout - Wnet)
    limite = _TOL * abs(Qi)
    linea = dict(Qi=round(Qi, 3), Qout=round(Qout, 3), Wt=round(Wt, 3),
                 Wp=round(Wp, 3), Wnet=round(Wnet, 3), eta=round(eta, 6),
                 residuo_N2=round(residuo, 6), limite_N2=round(limite, 6),
                 cumple_N2=bool(residuo <= limite),
                 clasificacion_teqp=val.clasificacion.value,
                 nota=("Tablas con TeqpAdapter; motor real citado de "
                       "confirmacion_motor_real_v2.json: eta=0.124296, "
                       "KALINA, Wnet=166.62 kW"))
    pd.DataFrame([linea]).to_csv(FASE2 / "ancla_balance.csv", index=False,
                                 encoding="utf-8")

    # Referencia directa del JSON de confirmacion con motor real (citado).
    ref = FASE2 / "confirmacion_motor_real_v2.json"
    if ref.exists():
        dato = json.loads(ref.read_text(encoding="utf-8"))
        p = dato["puntos"][0]
        print(f"Ancla (motor real, citado): {p['clasificacion']} "
              f"eta={p['eta']:.6f} Wnet={p['Wnet']:.2f} kW "
              f"({p.get('tiempo_s')} s)")
    print(f"Ancla (TeqpAdapter): {val.clasificacion.value} "
          f"eta={eta:.6f} Wnet={Wnet:.2f} kW; N2 residuo={residuo:.3e} "
          f"<= limite={limite:.3e} -> {residuo <= limite}")
    print(f"Guardados ancla_estados.csv y ancla_balance.csv en {FASE2}")


if __name__ == "__main__":
    main()