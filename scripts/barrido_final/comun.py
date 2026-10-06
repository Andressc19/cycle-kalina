"""Utilidades comunes de la campaña final (docs/METODOLOGIA_BARRIDOS_FINAL.md §1).

Configuración congelada de M0, los márgenes O1/O2/O3/O5 en forma NUMÉRICA (no
fallas), el índice de cercanía D de docs/MATEMATICA_ITERACIONES_SENSIBILIDAD.md §2
y la evaluación de UN punto.

`evaluar_punto` es de nivel de módulo a propósito: las fases la usan con
`ProcessPoolExecutor`, que en Windows arranca por `spawn` y reimporta el script
principal en cada proceso hijo.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[2]
if str(_RAIZ) not in sys.path:
    sys.path.insert(0, str(_RAIZ))

from src import sensitivity  # noqa: E402
from src._rango_barrido import COLUMNAS_RANGO, anotar_rango  # noqa: E402
from src.cycle_solver import CicloNoConvergeError, resolver_ciclo  # noqa: E402
from src.components import condensador  # noqa: E402
from src.properties.adapter import PropertyRangeError  # noqa: E402
from src.sensitivity import VARIABLES_BARRIBLES  # noqa: E402

__all__ = ["PROFESOR", "T_AMB_DISENO", "TAU", "PRESUPUESTO_S", "VARS", "COLS",
           "margenes", "indice_D", "evaluar_punto"]

# -- Configuración congelada (METODOLOGIA_BARRIDOS_FINAL.md §1 y §0) ---------
PROFESOR = dict(T_fuente=623.15, T_sumidero=300.032917, P_alta=3000.0,
                P_baja=400.0, x_b=0.50, m_b=1.0, eta_t=0.85, eta_p=0.75,
                eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.80)
T_AMB_DISENO = 300.032917      # piso de diseño de O2 aprobado el 2026-10-05
TAU = dict(O1=0.01, O2=1.0, O3=1.0, O5=0.01)
PRESUPUESTO_S = 300
VARS = VARIABLES_BARRIBLES
MARGENES = ("m_O1", "m_O2", "m_O3", "m_O5")
VIOL = ("viol_O1", "viol_O2", "viol_O3", "viol_O5")

COLS = (["tag", "motor", "pid", "convergio", "clasificacion", "eta", "Wnet",
         "mensaje"] + list(VARS)
        + ["q4", "q2", "T9_amb", "T_bub"] + list(MARGENES) + ["D"] + list(VIOL)
        + ["err_margenes"] + list(sensitivity.COLUMNAS_A)
        + list(sensitivity.COLUMNAS_B) + list(COLUMNAS_RANGO)
        + ["bracket_lo", "bracket_hi", "repliegues_lo", "repliegues_hi", "nF",
           "t_s", "error_inesperado"])


def _intenta(m: dict, clave: str, fn) -> None:
    """Ejecuta `fn` y guarda el número en `m[clave]`; si lanza, `None` + nota."""
    try:
        m[clave] = fn()
    except Exception as exc:                       # noqa: BLE001 - se registra
        m[clave] = None
        msg = f"{clave}: {type(exc).__name__}: {exc}"[:200]
        m["err_margenes"] = (f"{m['err_margenes']} | {msg}"
                             if m["err_margenes"] else msg)


def margenes(backend, resultado: dict, combo: dict) -> dict:
    """Márgenes O1/O2/O3/O5 como NÚMEROS (no `Falla`s).

    Réplica exacta de `src/restricciones/operativos.py::verificar_operativos`:
    `m_O1 = q4 − 0.90`, `m_O2 = T_bub − T9(max(T_sumidero, T_AMB_DISENO))`,
    `m_O3 = Wnet` y `m_O5 = min(q2 − 0.001, 0.999 − q2)`. Un cálculo que lance
    deja su valor en `None` y anota el motivo en `err_margenes`.
    """
    e = resultado["estados"]
    m = dict.fromkeys(MARGENES + ("q4", "q2", "T9_amb", "T_bub"))
    m["err_margenes"] = None
    _intenta(m, "q4", lambda: backend.fase_de(
        combo["P_baja"], e["e4"].T, e["e4"].x)[1])
    _intenta(m, "q2", lambda: backend.fase_de(
        combo["P_alta"], e["e2"].T, combo["x_b"])[1])

    def _t9() -> float:
        T_amb = max(combo["T_sumidero"], T_AMB_DISENO)
        return condensador.resolver(e["e8"], backend, T_sumidero=T_amb,
                                    eps=combo["eps_cond"],
                                    m=combo["m_b"])[0].T

    _intenta(m, "T9_amb", _t9)
    _intenta(m, "T_bub", lambda: backend.bubble_point(
        combo["P_baja"], combo["x_b"]))
    if m["q4"] is not None:
        m["m_O1"] = m["q4"] - 0.90
    if m["T9_amb"] is not None and m["T_bub"] is not None:
        m["m_O2"] = m["T_bub"] - m["T9_amb"]
    m["m_O3"] = resultado["Wnet"]
    if m["q2"] is not None:
        m["m_O5"] = min(m["q2"] - 0.001, 0.999 - m["q2"])
    return m


def indice_D(m: dict) -> tuple:
    """`(D, viol)` de docs/MATEMATICA_ITERACIONES_SENSIBILIDAD.md §2.

    `viol_k = max(0, −m_k)` y `D = Σ viol_k / TAU[k]`. Si algún margen es `None`
    (no se pudo calcular) `D` es `None`.
    """
    viol, D, falta = {}, 0.0, False
    for k in ("O1", "O2", "O3", "O5"):
        val = m.get(f"m_{k}")
        if val is None:
            falta, viol[f"viol_{k}"] = True, None
            continue
        viol[f"viol_{k}"] = max(0.0, -val)
        D += viol[f"viol_{k}"] / TAU[k]
    return (None if falta else D), viol


def evaluar_punto(combo: dict, *, motor: str = "teqp", tag=None) -> dict:
    """Resuelve, clasifica y mide UN punto; devuelve su fila. Nunca lanza.

    `motor="teqp"` usa `TeqpVerificado` (protección A) más un `AmmoniaWaterAdapter`
    para la verificación B; `motor="real"` usa el motor riguroso como backend y
    sin B. Siempre con `bracket_tolerante=True` y `presupuesto_s=PRESUPUESTO_S`.
    """
    from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter
    from src.properties.teqp_verificado import TeqpVerificado
    from src.restricciones import evaluar_ciclo

    x_b = combo["x_b"]
    if motor == "teqp":
        backend, motor_real = TeqpVerificado(x=x_b), AmmoniaWaterAdapter(x=x_b)
    else:
        backend, motor_real = AmmoniaWaterAdapter(x=x_b), None
    antes = (getattr(backend, "n_recurrencias", None),
             getattr(backend, "n_fallos", None))

    fila = dict.fromkeys(COLS)
    fila.update(tag=tag, motor=motor, pid=os.getpid(), **combo)
    t0 = time.perf_counter()
    try:
        res = resolver_ciclo(backend, **combo, bracket_tolerante=True,
                             presupuesto_s=PRESUPUESTO_S)
    except (CicloNoConvergeError, PropertyRangeError) as exc:
        fila.update(convergio=False, clasificacion="NO_CONVERGIO", eta=None,
                    Wnet=None, mensaje=str(exc)[:300])
        if motor == "teqp":
            fila = sensitivity._anotar_ab(fila, combo, None, backend,
                                          motor_real, antes)
        fila = anotar_rango(fila, combo, None, motor, backend,
                            "extrapolar_marcar")
    except Exception as exc:                       # noqa: BLE001 - se registra
        fila["error_inesperado"] = f"{type(exc).__name__}: {exc}"[:300]
    else:
        crit = {k: combo[k] for k in sensitivity._CRIT}
        crit["T_amb_diseno"] = T_AMB_DISENO
        val = evaluar_ciclo(backend, res, **crit)
        fila.update(convergio=True, clasificacion=val.clasificacion.value,
                    eta=res["eta"], Wnet=res["Wnet"],
                    mensaje=val.mensaje_reporte()[:300])
        if motor == "teqp":
            fila = sensitivity._anotar_ab(fila, combo, res, backend,
                                          motor_real, antes)
        fila = anotar_rango(fila, combo, res, motor, backend,
                            "extrapolar_marcar")
        m = margenes(backend, res, combo)
        D, viol = indice_D(m)
        fila.update(m, D=D, **viol)
        br = res.get("bracket") or {}
        fila.update(bracket_lo=br.get("lo"), bracket_hi=br.get("hi"),
                    repliegues_lo=br.get("repliegues_lo"),
                    repliegues_hi=br.get("repliegues_hi"), nF=br.get("nF"))
    fila["t_s"] = time.perf_counter() - t0
    return fila