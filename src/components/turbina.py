"""Componente turbina del ciclo Kalina KSC-11.

Eficiencia isentrópica estándar (CONTEXT.md, "Turbina y bomba"):
    h4s = h(P_baja, s3, x3)          (expansión isoentrópica)
    h4  = h3 − η_t · (h3 − h4s)

Consume únicamente la interfaz `PropertyBackend`.
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
    eta_t: float,
) -> tuple[EstadoTermo, dict]:
    """Expande la corriente 3 (entrada) hasta la corriente 4 a ``P_salida``.

    Devuelve ``(estado 4, {"Wt": ...})``. Si ``entrada.m`` está fijado, ``Wt``
    es potencia en kW (``m·(h3 − h4)``); si no, ``Wt`` queda normalizado por
    unidad de masa en kJ/kg (``h3 − h4``) y ``estado4.m`` es ``None``.
    """
    x3 = entrada.x
    h3 = entrada.h
    s3 = entrada.s

    h4s = backend.h(P_salida, s=s3, x=x3)
    h4 = h3 - eta_t * (h3 - h4s)

    T4 = backend.T_from_Ph(P_salida, h4, x=x3)
    s4 = backend.s(P_salida, T=T4, x=x3)

    estado4 = EstadoTermo(
        T=T4, P=P_salida, h=h4, s=s4, x=x3, m=entrada.m, etiqueta="4"
    )
    # kW = (kg/s)·(kJ/kg); si no hay caudal, kJ/kg (valor normalizado).
    Wt = (h3 - h4) if entrada.m is None else entrada.m * (h3 - h4)
    return estado4, {"Wt": Wt}
