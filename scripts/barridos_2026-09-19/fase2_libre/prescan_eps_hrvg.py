"""Fase 2 (tarea 2026-09-20-fase2-prescan-eps-hrvg) — pre-escaneo de eps_hrvg.

Cierra el vacío detectado en BASE_LIBRE_v2.md §3: la variable `eps_hrvg` del
candidato v2 (400/0.40/0.95) nunca se barrió, ni siquiera en exploración
gruesa, así que el rango propuesto 0.80-0.90 para el barrido de sensibilidad
era una suposición sin evidencia. Este pre-escaneo decide si ese rango es
adecuado o hay que corregirlo.

Escanea `eps_hrvg` en {0.70, 0.75, 0.80, 0.85, 0.90, 0.95} (6 puntos, paso
0.05) con TeqpAdapter, resto de variables fijas en el candidato v2 confirmado
con el motor real (confirmacion_motor_real_v2.json): P_alta=3000, P_baja=400,
x_b=0.40, T_fuente=470.0, T_sumidero=300.032917, m_b=1.0, eta_t=0.85,
eta_p=0.75, eps_reg=0.75, eps_cond=0.95, T_amb_diseno=303.55.

Cada punto registra (converja o no) el esquema `tabla_barrido` de
src/sensitivity.py + los diagnósticos de las dos fronteras que eps_hrvg
gobierna —q2 y T2, criterios O5 y S5— + el trío O2 (T_sat_L, T9_amb,
O2_margen), mismo patrón que busqueda_libre_v2.csv, para dejar constancia de
que O2 no es el criterio limitante en esta variable.

Salida: resultados/barridos_2026-09-19/fase2_libre/prescan_eps_hrvg.csv
+ el resumen de interpretación lo escribe el ejecutor (PRESCAN_EPS_HRVG.md).

NO modifica código de producción (solo consume src/ como librería).
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd

_RAIZ = Path(__file__).resolve().parents[3]  # ruta: scripts/.../fase2_libre/
sys.path.insert(0, str(_RAIZ))

from src.cycle_solver import CicloNoConvergeError, resolver_ciclo  # noqa: E402
from src.properties.adapter import PropertyRangeError  # noqa: E402
from src.restricciones import evaluar_ciclo  # noqa: E402

T_AMB_DISENO = 303.55          # caso del profesor: su tabla real llega a 30.4 C
CANDIDATO = dict(P_alta=3000.0, T_fuente=470.0, T_sumidero=300.032917, m_b=1.0,
                 eta_t=0.85, eta_p=0.75, eps_hrvg=0.85, eps_reg=0.75,
                 P_baja=400.0, x_b=0.40, eps_cond=0.95)
EPS_HRVG_GRID = (0.70, 0.75, 0.80, 0.85, 0.90, 0.95)
CSV = (_RAIZ / "resultados" / "barridos_2026-09-19" / "fase2_libre"
       / "prescan_eps_hrvg.csv")
VARIABLES = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "m_b",
             "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")
COLUMNAS = (list(VARIABLES) + ["q2", "T2", "T_sat_L", "T9_amb", "O2_margen",
                               "convergio", "clasificacion", "eta", "Wnet",
                               "mensaje"])


def importar_backend():
    from src.properties.teqp_adapter import TeqpAdapter
    return TeqpAdapter(x=0.5)


def combos_eps_hrvg() -> list[dict]:
    """Los 6 puntos del pre-escaneo: candidato v2 con solo eps_hrvg variado."""
    return [{**CANDIDATO, "eps_hrvg": eps} for eps in EPS_HRVG_GRID]


def resolver_punto(combo: dict) -> dict:
    """Resuelve + clasifica un punto y adjunta diagnósticos q2/T2/O2."""
    from src.components.condensador import resolver as resolver_cond
    backend = importar_backend()
    fila = dict(combo, q2=None, T2=None, T_sat_L=None, T9_amb=None,
                O2_margen=None)
    try:
        res = resolver_ciclo(backend, **combo)
    except (CicloNoConvergeError, PropertyRangeError) as exc:
        fila.update(convergio=False, clasificacion="NO_CONVERGIO", eta=None,
                    Wnet=None, mensaje=str(exc)[:400])
        return fila
    e2 = res["estados"]["e2"]
    _, q2 = backend.fase_de(combo["P_alta"], e2.T, combo["x_b"])
    T_amb_evaluar = max(combo["T_sumidero"], T_AMB_DISENO)
    est9_amb, _ = resolver_cond(res["estados"]["e8"], backend,
                                T_sumidero=T_amb_evaluar,
                                eps=combo["eps_cond"], m=combo["m_b"])
    T_sat_L = backend.bubble_point(combo["P_baja"], combo["x_b"])
    val = evaluar_ciclo(backend, res, P_alta=combo["P_alta"],
                        P_baja=combo["P_baja"], T_fuente=combo["T_fuente"],
                        T_sumidero=combo["T_sumidero"], x_b=combo["x_b"],
                        m_b=combo["m_b"], eps_hrvg=combo["eps_hrvg"],
                        eps_reg=combo["eps_reg"], eps_cond=combo["eps_cond"],
                        T_amb_diseno=T_AMB_DISENO)
    fila.update(q2=q2, T2=e2.T, T_sat_L=T_sat_L, T9_amb=est9_amb.T,
                O2_margen=T_sat_L - est9_amb.T)
    fila.update(convergio=True, clasificacion=val.clasificacion.value,
                eta=res["eta"], Wnet=res["Wnet"],
                mensaje=val.mensaje_reporte()[:400])
    return fila


def main() -> None:
    puntos = combos_eps_hrvg()
    print(f"Pre-escaneo eps_hrvg: {len(puntos)} puntos "
          f"(eps_hrvg={EPS_HRVG_GRID}) con TeqpAdapter, resto = candidato v2, "
          f"T_amb_diseno={T_AMB_DISENO} K...", flush=True)
    filas = []
    t0 = time.perf_counter()
    for n, combo in enumerate(puntos, 1):
        fila = resolver_punto(combo)
        filas.append(fila)
        print(f"  [{n}/{len(puntos)}] eps_hrvg={combo['eps_hrvg']:.2f} -> "
              f"{fila['clasificacion']} eta={fila['eta']} "
              f"q2={fila['q2']} T2={fila['T2']}", flush=True)
    dt = time.perf_counter() - t0

    df = pd.DataFrame(filas)[COLUMNAS]
    CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CSV, index=False, encoding="utf-8")

    print(f"\nPuntos evaluados: {len(filas)} en {dt:.1f} s "
          f"({dt / len(filas):.2f} s/punto)", flush=True)
    print(df[["eps_hrvg", "clasificacion", "eta"]].to_string(index=False))
    print(f"\nCSV guardado en {CSV}")


if __name__ == "__main__":
    main()