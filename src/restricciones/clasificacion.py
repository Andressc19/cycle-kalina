"""Orquestador: `evaluar_ciclo` corre los 17 criterios implementados
(N2,N3,S1-S8,O1-O3,O5,C1-C3) sobre un punto ya resuelto y clasifica el punto.

N1 NO se evalúa aquí: es la ausencia de `CicloNoConvergeError` del solver, y
eso solo lo sabe quien llama a `resolver_ciclo` (ver `sensitivity.py`) — un
punto que lanzó esa excepción nunca llega a tener un `resultado` que validar.

Criterios documentados como no aplicables a esta arquitectura (repo
"ciclo_kalina_tercero": único método de cierre por efectividad, fuente/sumidero
de capacidad infinita):
    F1  — solo aplica al método A (pinch); este repo no lo tiene.
    S9  — no-cruce interno con C_g finito; no implementado.
    O6  — rocío ácido con C_g finito; no implementado.
    CD  — cierre declarado alcanzable con C_g finito; no implementado.
    O4  — eliminado deliberadamente por el propio catálogo del vault.
    C1b — nunca definido formalmente en el vault (su "Nota de recuperación"
          lo admite explícitamente).
    N4  — dominio de validez del motor de propiedades; sin rango de T
          declarado en este repo. UNRESOLVED (decisión del usuario: omitir).
"""

from __future__ import annotations

from .composicion import verificar_composicion
from .modelos import Clasificacion, Falla, ResultadoValidacion, Severidad
from .numericos import verificar_n2, verificar_n3
from .operativos import verificar_operativos
from .segunda_ley import verificar_segunda_ley

__all__ = ["evaluar_ciclo", "NO_APLICA"]

NO_APLICA = ("F1", "S9", "O6", "CD", "O4", "C1b", "N4")

# Prioridad de clasificación para elegir la peor entre varias fallas.
_PRIORIDAD = {
    Clasificacion.NO_CONVERGIO: 0,
    Clasificacion.INVIABLE: 1,
    Clasificacion.DEGENERADO: 2,
    Clasificacion.CORREGIBLE: 3,
    Clasificacion.VALIDO_ADVERTENCIA: 4,
    Clasificacion.KALINA: 5,
}


def evaluar_ciclo(backend, resultado: dict, *, P_alta: float, P_baja: float,
                  T_fuente: float, T_sumidero: float, x_b: float, m_b: float,
                  eps_hrvg: float, eps_reg: float, eps_cond: float,
                  T_amb_diseno: float = 303.55) -> ResultadoValidacion:
    """Corre los 17 criterios implementados sobre un punto ya resuelto.

    ``resultado`` es el dict que devuelve `resolver_ciclo` (estados + energías).
    No lanza excepciones: un punto que no convergió nunca llega aquí (ver
    docstring del módulo). Devuelve un `ResultadoValidacion` con la
    clasificación final (la más severa entre todas las fallas encontradas, o
    KALINA si no hay ninguna) y la lista completa de fallas, para no perder
    trazabilidad.

    ``T_amb_diseno`` es el piso de diseño del criterio O2 (cavitación) en K:
    se propaga a `verificar_operativos`, que evalúa el condensador contra
    `max(T_sumidero, T_amb_diseno)`. Default 303.55 K (decisión del vault);
    configurable y retrocompatible para quien no lo pase.
    """
    fallas: list[Falla] = []

    f_n2 = verificar_n2(resultado)
    if f_n2 is not None:
        fallas.append(f_n2)
    fallas.extend(verificar_n3(resultado, x_b))
    fallas.extend(verificar_segunda_ley(
        resultado, T_fuente=T_fuente, T_sumidero=T_sumidero,
        eps_hrvg=eps_hrvg, eps_reg=eps_reg, eps_cond=eps_cond))
    fallas.extend(verificar_operativos(
        resultado, backend, P_alta=P_alta, P_baja=P_baja,
        T_sumidero=T_sumidero, x_b=x_b, m_b=m_b, eps_cond=eps_cond,
        T_amb_diseno=T_amb_diseno))
    fallas.extend(verificar_composicion(resultado, x_b))

    if not fallas:
        clasificacion = Clasificacion.KALINA
    else:
        clasificacion = min(
            (f.clasificacion for f in fallas), key=lambda c: _PRIORIDAD[c])

    return ResultadoValidacion(
        clasificacion=clasificacion, fallas=fallas, no_aplica=NO_APLICA)
