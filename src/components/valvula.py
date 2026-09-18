"""Componente válvula de expansión del ciclo Kalina KSC-11.

Válvula isoentálpica (CONTEXT.md, "Válvula"): h7 = h6. La composición no cambia
y T/s se recalculan a ``P_salida`` vía el backend.
"""

from __future__ import annotations

from ..properties.adapter import PropertyBackend
from ..state import EstadoTermo

__all__ = ["resolver"]


def resolver(
    entrada: EstadoTermo,
    backend: PropertyBackend,
    *,
    P_salida: float,
) -> tuple[EstadoTermo, dict]:
    """Estrangula la corriente 6 (entrada) hasta la corriente 7 a ``P_salida``.

    Devuelve ``(estado 7, {})``: una válvula isoentálpica no intercambia
    energía, así que no reporta Q ni W.
    """
    x6 = entrada.x
    h7 = entrada.h                                  # isoentálpica: h7 = h6

    T7 = backend.T_from_Ph(P_salida, h7, x=x6)
    s7 = backend.s(P_salida, T=T7, x=x6)

    estado7 = EstadoTermo(
        T=T7, P=P_salida, h=h7, s=s7, x=x6, m=entrada.m, etiqueta="7"
    )
    return estado7, {}
