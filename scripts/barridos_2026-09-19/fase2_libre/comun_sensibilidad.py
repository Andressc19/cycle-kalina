"""Helpers compartidos del barrido de sensibilidad FINAL de Fase 2.

Cada punto del barrido (tarea 2026-09-20-fase2-sensibilidad-final) se resuelve
con un backend dado (``TeqpAdapter`` para el grueso — instruccion del
director —, ``AmmoniaWaterAdapter`` solo para los spot-checks selectivos con
motor real), se clasifica y se le adjuntan:

- los margenes de los criterios que deciden la clasificacion en el entorno del
  candidato (O1: q4-0.90, O2: T_sat_L-T9_amb, S5: T_fuente-T2, O5: margen de
  q2), con la convencion margen>0 = cumple con ese excedente;
- el criterio "ligante" (el que decide la clasificacion: la falla principal
  para puntos no-KALINA, o la frontera mas cercana de O1/O2/S5 para KALINA)
  y su margen;
- ``motor_confirmado`` (= None aqui; lo rellena spot_check_sensibilidad.py con
  el motor real cuando el punto esta a menos de ~1-2 K/0.02 del borde).

``T_amb_diseno=303.55`` (caso del profesor, ver BASE_LIBRE_v2.md): la logica
de ``evaluar_ciclo``/O2 evalua el condensador contra max(T_sumidero, 303.55).

La carpeta tiene guiones y no es importable por nombre desde un script en otra
ruta; los scripts de esta carpeta la cargan con importlib por ruta. Unica
dependencia: src/ (interfaces publicas) — no modifica nada de produccion.
"""

from __future__ import annotations

import sys
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[3]
if str(_RAIZ) not in sys.path:
    sys.path.insert(0, str(_RAIZ))

from src.cycle_solver import CicloNoConvergeError, resolver_ciclo  # noqa: E402
from src.properties.adapter import PropertyRangeError  # noqa: E402
from src.restricciones import Clasificacion, evaluar_ciclo  # noqa: E402

__all__ = ["T_AMB_DISENO", "DQ", "UMBRALES_SPOT", "importar_teqp",
           "importar_real", "margenes", "ligante", "spot_necesario",
           "resolver_punto", "COLUMNAS_DIAG"]

T_AMB_DISENO = 303.55           # piso de diseno del criterio O2 (K)
DQ = 1e-3                       # margen del criterio O5 (mismo valor del motor)
# Umbrales de spot-check con motor real (~1-2 K, o 0.02 en q2/q4; TASK).
UMBRALES_SPOT = {"O1": 0.02, "O5": 0.02, "O2": 2.0, "S5": 2.0}

# Columnas de diagnostico que se anexan a la tabla base del barrido.
COLUMNAS_DIAG = ("q2", "q4", "T2", "T_sat_L", "T9_amb",
                 "margen_O1", "margen_O2", "margen_S5", "margen_O5",
                 "criterio_ligante", "margen_ligante", "motor_confirmado")


def importar_teqp():
    """Factory del motor rapido (el grueso del barrido)."""
    from src.properties.teqp_adapter import TeqpAdapter
    return TeqpAdapter(x=0.5)


def importar_real():
    """Factory del motor real (solo spot-checks selectivos)."""
    from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter
    return AmmoniaWaterAdapter(x=0.5)


def margenes(backend, res, combo: dict) -> dict:
    """Margenes O1/O2/S5/O5 de un punto ya resuelto (+ q2/q4/T2/TSat/T9amb).

    Convencion: margen > 0 = el criterio se cumple con ese excedente;
    margen < 0 = el criterio ya se viola por esa cantidad. Misma mecanica
    que busqueda_libre_v2.py (O2 re-resuelto contra max(T_sumidero, 303.55)).
    """
    from src.components.condensador import resolver as resolver_cond
    e = res["estados"]
    _, q4 = backend.fase_de(combo["P_baja"], e["e4"].T, e["e4"].x)
    _, q2 = backend.fase_de(combo["P_alta"], e["e2"].T, combo["x_b"])
    T_sat_L = backend.bubble_point(combo["P_baja"], combo["x_b"])
    T_amb_eval = max(combo["T_sumidero"], T_AMB_DISENO)
    est9_amb, _ = resolver_cond(e["e8"], backend, T_sumidero=T_amb_eval,
                                eps=combo["eps_cond"], m=combo["m_b"])
    return dict(q2=q2, q4=q4, T2=e["e2"].T, T_sat_L=T_sat_L,
                T9_amb=est9_amb.T,
                margen_O1=q4 - 0.90,                 # O1: q4 >= 0.90
                margen_O2=T_sat_L - est9_amb.T,      # O2: T9_amb <= T_sat_L
                margen_S5=combo["T_fuente"] - e["e2"].T,   # S5: T2 <= T_fuente
                margen_O5=min(q2 - DQ, (1.0 - DQ) - q2))   # O5: q2 en (DQ,1-DQ)


def ligante(clasificacion: str, codigo_principal, m: dict) -> tuple:
    """(criterio, margen) que decide la clasificacion del punto.

    KALINA no tiene fallas: se reporta la frontera mas cercana de las tres
    que gobiernan el entorno (O1/O2/S5), la que primero voltearia el punto.
    Para el resto, la falla principal (si es medible O1/O2/S5/O5; los demas
    criterios no tienen un margen de temperatura/titulo comparable -> None).
    """
    if clasificacion == "KALINA":
        candidatos = [("O1", m["margen_O1"]), ("O2", m["margen_O2"]),
                      ("S5", m["margen_S5"])]
        return min(candidatos, key=lambda t: t[1])
    if codigo_principal in ("O1", "O2", "S5", "O5"):
        clave = {"O1": "margen_O1", "O2": "margen_O2", "S5": "margen_S5",
                 "O5": "margen_O5"}[codigo_principal]
        return codigo_principal, m[clave]
    return codigo_principal, None


def spot_necesario(clasificacion: str, codigo_principal, m: dict) -> bool:
    """¿Está el punto a <umbral (1-2 K / 0.02 en q) de la frontera decisiva?

    Solo para O1/O2/S5/O5 (los que tienen margen medible); el resto de
    criterios no gatilla spot-check con el motor real.
    """
    if clasificacion == "KALINA":
        return (m["margen_O1"] < UMBRALES_SPOT["O1"]
                or m["margen_O2"] < UMBRALES_SPOT["O2"]
                or m["margen_S5"] < UMBRALES_SPOT["S5"])
    if codigo_principal in ("O1", "O2", "S5", "O5"):
        return abs(m[f"margen_{codigo_principal}"]) < UMBRALES_SPOT[codigo_principal]
    return False


def resolver_punto(combo: dict, factory=importar_teqp) -> dict:
    """Resuelve + clasifica un punto del barrido y adjunta margenes (worker).

    ``factory`` es la funcion que crea el backend (por defecto TeqpAdapter
    para el grueso del barrido; el motor real se pasa explicitamente en el
    spot-check). Todo punto se registra igual, converja o no (TASK Constraint 4).
    """
    backend = factory()
    fila = dict(combo, convergio=False,
                clasificacion=Clasificacion.NO_CONVERGIO.value, eta=None,
                Wnet=None, mensaje="", q2=None, q4=None, T2=None,
                T_sat_L=None, T9_amb=None, margen_O1=None, margen_O2=None,
                margen_S5=None, margen_O5=None, criterio_ligante=None,
                margen_ligante=None, motor_confirmado=None)
    try:
        res = resolver_ciclo(backend, **combo)
    except (CicloNoConvergeError, PropertyRangeError) as exc:
        fila["mensaje"] = str(exc)[:300]
        return fila
    val = evaluar_ciclo(backend, res, P_alta=combo["P_alta"],
                        P_baja=combo["P_baja"], T_fuente=combo["T_fuente"],
                        T_sumidero=combo["T_sumidero"], x_b=combo["x_b"],
                        m_b=combo["m_b"], eps_hrvg=combo["eps_hrvg"],
                        eps_reg=combo["eps_reg"], eps_cond=combo["eps_cond"],
                        T_amb_diseno=T_AMB_DISENO)
    m = margenes(backend, res, combo)
    principal = val.principal
    codigo = principal.codigo if principal is not None else None
    cod_lig, marg_lig = ligante(val.clasificacion.value, codigo, m)
    fila.update(**m, criterio_ligante=cod_lig, margen_ligante=marg_lig,
                convergio=True, clasificacion=val.clasificacion.value,
                eta=res["eta"], Wnet=res["Wnet"],
                mensaje=val.mensaje_reporte()[:300])
    return fila