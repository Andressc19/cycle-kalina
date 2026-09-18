"""Componente separador ideal (flash) del ciclo Kalina KSC-11.

Separador IDEAL (CONTEXT.md, "Separador"): reparte la corriente 2 en vapor
saturado (3, hacia la turbina) y líquido saturado (5, hacia el regenerador) a la
misma P y T de equilibrio, con las composiciones L-V de la mezcla NH3-H2O y las
fracciones de la regla de la palanca.

Las composiciones de equilibrio a la P,T de la corriente de entrada se obtienen
con el flash directo ``equilibrio_liquido_vapor(P, T)`` del backend
(``PropertyBackend``): (T,P) → (x_liquido, x_vapor) másicos, sin invertir
bubble/dew point por bisección (el motor real no cubre composiciones extremas
y la inversión era lenta; ver TASK_CONTEXT 2026-09-17-fix-separador-flash-
directo). Las excepciones del backend se propagan sin envolver.
"""

from __future__ import annotations

from ..properties.adapter import PropertyBackend
from ..state import EstadoTermo

__all__ = ["resolver"]


def resolver(entrada: EstadoTermo, backend: PropertyBackend) -> tuple[
    EstadoTermo, EstadoTermo, dict
]:
    """Separa la corriente 2 en vapor saturado (3) y líquido saturado (5).

    Devuelve ``(vapor, liquido, {})``. Las fracciones de vapor/líquido siguen la
    regla de la palanca y se aplican a ``entrada.m`` si está fijado (si no, los
    caudales de salida quedan en ``None``).
    """
    P = entrada.P
    T_eq = entrada.T
    z = entrada.x

    x_l, y_v = backend.equilibrio_liquido_vapor(P, T_eq)

    f_vapor = (z - x_l) / (y_v - x_l)              # regla de la palanca
    m_vapor = None if entrada.m is None else f_vapor * entrada.m
    m_liquido = None if entrada.m is None else (1.0 - f_vapor) * entrada.m

    vapor = EstadoTermo(
        T=T_eq, P=P, h=backend.h(P, T=T_eq, x=y_v), s=backend.s(P, T=T_eq, x=y_v),
        x=y_v, m=m_vapor, q=1.0, fase="vapor", etiqueta="3",
    )
    liquido = EstadoTermo(
        T=T_eq, P=P, h=backend.h(P, T=T_eq, x=x_l), s=backend.s(P, T=T_eq, x=x_l),
        x=x_l, m=m_liquido, q=0.0, fase="liquido", etiqueta="5",
    )
    return vapor, liquido, {}