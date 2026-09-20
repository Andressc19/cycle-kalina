"""Fase 3 (tarea 2026-09-19-fase3-caso-real): sensibilidad alrededor de la
base KALINA de Husavik confirmada (motor real, iapws G4-01).

Base: T_fuente=394.15, T_sumidero=278.15, P_alta=3300, P_baja=1200,
      x_b=0.82, m_b=1.0, eta_t=0.90, eta_p=0.80, eps_hrvg=0.85,
      eps_reg=0.95, eps_cond=0.95  ->  KALINA, eta=0.0882, Wnet=78.9 kW

3 barridos pequenos (4 puntos c/u) con TeqpAdapter (rapido):
  1. sensibilidad_palta.csv : P_alta en {3000, 3200, 3400, 3500}
  2. sensibilidad_xb.csv    : x_b en {0.78, 0.80, 0.84, 0.86} (P_baja fija)
  3. sensibilidad_pbaja.csv : P_baja en {1100, 1150, 1250, 1300}

Mismas columnas que busqueda_husavik.csv (esquema tabla_barrido). NO toca
codigo de produccion ni las carpetas de las tareas paralelas.
"""

from __future__ import annotations

import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

_RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_RAIZ))

from src.cycle_solver import CicloNoConvergeError, resolver_ciclo
from src.properties.adapter import PropertyRangeError
from src.restricciones import evaluar_ciclo

T_FUENTE = 394.15
T_SUMIDERO = 278.15
MB = 1.0
ETA_T = 0.90
ETA_P = 0.80
EPS_HRVG = 0.85
EPS_REG = 0.95
EPS_COND = 0.95
P_ALTA = 3300.0
P_BAJA = 1200.0
X_B = 0.82

RESULTADOS = _RAIZ / "resultados" / "barridos_2026-09-19" / "fase3_real"

# (nombre salida, variar campo, valores)
BARRIDOS = [
    ("sensibilidad_palta.csv", "P_alta", [3000.0, 3200.0, 3400.0, 3500.0]),
    ("sensibilidad_xb.csv", "x_b", [0.78, 0.80, 0.84, 0.86]),
    ("sensibilidad_pbaja.csv", "P_baja", [1100.0, 1150.0, 1250.0, 1300.0]),
]

COLUMNAS = ["T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "m_b",
            "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond",
            "convergio", "clasificacion", "eta", "Wnet", "mensaje"]

COLUMNA_BOOL = {"P_alta", "P_baja", "x_b"}


def resolver_punto(pa: float, pb: float, xb: float) -> dict:
    from src.properties.teqp_adapter import TeqpAdapter
    backend = TeqpAdapter()
    combo = dict(P_alta=pa, P_baja=pb, T_fuente=T_FUENTE,
                 T_sumidero=T_SUMIDERO, x_b=xb, m_b=MB, eta_t=ETA_T,
                 eta_p=ETA_P, eps_hrvg=EPS_HRVG, eps_reg=EPS_REG,
                 eps_cond=EPS_COND)
    try:
        res = resolver_ciclo(backend, **combo)
    except (CicloNoConvergeError, PropertyRangeError) as exc:
        return dict(T_fuente=T_FUENTE, T_sumidero=T_SUMIDERO, P_alta=pa,
                    P_baja=pb, x_b=xb, m_b=MB, eta_t=ETA_T, eta_p=ETA_P,
                    eps_hrvg=EPS_HRVG, eps_reg=EPS_REG, eps_cond=EPS_COND,
                    convergio=False, clasificacion="NO_CONVERGIO", eta=None,
                    Wnet=None, mensaje=str(exc))
    val = evaluar_ciclo(backend, res, P_alta=pa, P_baja=pb,
                        T_fuente=T_FUENTE, T_sumidero=T_SUMIDERO,
                        x_b=xb, m_b=MB, eps_hrvg=EPS_HRVG, eps_reg=EPS_REG,
                        eps_cond=EPS_COND)
    return dict(T_fuente=T_FUENTE, T_sumidero=T_SUMIDERO, P_alta=pa,
                P_baja=pb, x_b=xb, m_b=MB, eta_t=ETA_T, eta_p=ETA_P,
                eps_hrvg=EPS_HRVG, eps_reg=EPS_REG, eps_cond=EPS_COND,
                convergio=True, clasificacion=val.clasificacion.value,
                eta=res["eta"], Wnet=res["Wnet"],
                mensaje=val.mensaje_reporte())


def main() -> None:
    for nombre, campo, valores in BARRIDOS:
        filas = []
        with ProcessPoolExecutor(max_workers=4) as pool:
            if campo == "P_alta":
                futuros = [pool.submit(resolver_punto, v, P_BAJA, X_B)
                           for v in valores]
            elif campo == "P_baja":
                futuros = [pool.submit(resolver_punto, P_ALTA, v, X_B)
                           for v in valores]
            else:
                futuros = [pool.submit(resolver_punto, P_ALTA, P_BAJA, v)
                           for v in valores]
            for fut in as_completed(futuros):
                r = fut.result()
                filas.append(r)
                print(f"[{nombre}] {campo}={r[campo]:.2f} -> "
                      f"{r['clasificacion']} eta={r['eta']}", flush=True)
        df = pd.DataFrame(filas)
        df = df[COLUMNAS]  # orden estable
        for c in COLUMNA_BOOL:
            pass  # (se dejan como float para consistencia numerica)
        ruta = RESULTADOS / nombre
        df.to_csv(ruta, index=False, encoding="utf-8-sig")
        print(f"  guardado {ruta} ({len(df)} filas)", flush=True)


if __name__ == "__main__":
    main()