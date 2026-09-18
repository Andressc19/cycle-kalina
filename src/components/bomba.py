"""Componente bomba de solución del ciclo Kalina KSC-11.

Eficiencia isentrópica estándar (CONTEXT.md, "Turbina y bomba"):
    h10s = h(P_alta, s9, x9)         (compresión isoentrópica)
    h10  = h9 + (h10s − h9) / η_p

`entrada` es la corriente 9 (salida del condensador). Consume únicamente la
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
    P_salida: float,
    eta_p: float,
    m: float,
) -> tuple[EstadoTermo, dict]:
    """Comprime la corriente 9 hasta la corriente 10 a ``P_salida``.

    Devuelve ``(estado 10, {"Wp": m·(h10 − h9)})`` con ``Wp`` en kW.
    """
    x9 = entrada.x
    h9 = entrada.h
    s9 = entrada.s

    h10s = backend.h(P_salida, s=s9, x=x9)
    h10 = h9 + (h10s - h9) / eta_p

    T10 = backend.T_from_Ph(P_salida, h10, x=x9)
    s10 = backend.s(P_salida, T=T10, x=x9)

    estado10 = EstadoTermo(
        T=T10, P=P_salida, h=h10, s=s10, x=x9, m=m, etiqueta="10"
    )
    return estado10, {"Wp": m * (h10 - h9)}
