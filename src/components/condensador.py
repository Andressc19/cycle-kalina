"""Componente condensador del ciclo Kalina KSC-11.

Método de efectividad (CONTEXT.md, "Fórmulas de efectividad"):
    ε_cond = (h8 − h9) / (h8 − h9,min),  h9,min = h(P_baja, T_sumidero, x_b)
    h9 = h8 − ε_cond · (h8 − h9,min)

`entrada` es la corriente 8 (salida del absorbedor). Consume únicamente la
interfaz `PropertyBackend`.
"""

from __future__ import annotations

from ..properties.adapter import PropertyBackend
from ..state import EstadoTermo

__all__ = ["resolver"]


def resolver(
    entrada: EstadoTermo,
    backend: PropertyBackend,
    *,
    T_sumidero: float,
    eps: float,
    m: float,
) -> tuple[EstadoTermo, dict]:
    """Enfría la corriente 8 hasta la corriente 9 a ``P_baja``.

    Devuelve ``(estado 9, {"Qout": m·(h8 − h9)})`` con ``Qout`` en kW.
    """
    P_baja = entrada.P
    x_b = entrada.x
    h8 = entrada.h

    h9_min = backend.h(P_baja, T=T_sumidero, x=x_b)
    h9 = h8 - eps * (h8 - h9_min)

    T9 = backend.T_from_Ph(P_baja, h9, x=x_b)
    s9 = backend.s(P_baja, T=T9, x=x_b)

    estado9 = EstadoTermo(
        T=T9, P=P_baja, h=h9, s=s9, x=x_b, m=m, etiqueta="9"
    )
    return estado9, {"Qout": m * (h8 - h9)}
