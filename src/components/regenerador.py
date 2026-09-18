"""Componente regenerador del ciclo Kalina KSC-11.

Método de efectividad (CONTEXT.md, "Fórmulas de efectividad"):
    ε_reg = (h5 − h6) / (h5 − h6,min),  h6,min = h(P_alta, T10, x5)
    h6 = h5 − ε_reg · (h5 − h6,min)

`entrada_caliente` es la corriente 5 (líquido saturado del separador) y
`entrada_fria` la corriente 10 (salida de la bomba), cuyo T alimenta ``h6,min``.
Consume únicamente la interfaz `PropertyBackend`.
"""

from __future__ import annotations

from dataclasses import replace

from ..properties.adapter import PropertyBackend
from ..state import EstadoTermo

__all__ = ["resolver"]


def resolver(
    entrada_caliente: EstadoTermo,
    entrada_fria: EstadoTermo,
    backend: PropertyBackend,
    *,
    eps: float,
) -> tuple[EstadoTermo, EstadoTermo, dict]:
    """Enfría la corriente 5 hasta la 6 y devuelve también el lado frío.

    La efectividad dada define **solo** el lado caliente (estado 6). CONTEXT.md
    no da ninguna fórmula para el estado 1 (salida fría), así que este
    componente devuelve el lado frío sin cambiar (pass-through) y lo reporta en
    ``UNRESOLVED``: el estado 1 queda a cargo de una tarea/definición posterior.

    Devuelve ``(estado 6, salida_fría, {"Qreg": ...})``. ``Qreg`` es la carga
    interna en kW (``m5·(h5 − h6)``) si ``entrada_caliente.m`` está fijado; si
    no, queda en ``None``.
    """
    P_caliente = entrada_caliente.P
    x_caliente = entrada_caliente.x
    h5 = entrada_caliente.h

    h6_min = backend.h(P_caliente, T=entrada_fria.T, x=x_caliente)
    h6 = h5 - eps * (h5 - h6_min)

    T6 = backend.T_from_Ph(P_caliente, h6, x=x_caliente)
    s6 = backend.s(P_caliente, T=T6, x=x_caliente)

    estado6 = EstadoTermo(
        T=T6, P=P_caliente, h=h6, s=s6, x=x_caliente,
        m=entrada_caliente.m, etiqueta="6",
    )
    # Lado frío: pass-through (ver docstring), copia para no compartir objeto.
    salida_fria = replace(entrada_fria)

    Qreg = None
    if entrada_caliente.m is not None:
        Qreg = entrada_caliente.m * (h5 - h6)       # kW
    return estado6, salida_fria, {"Qreg": Qreg}
