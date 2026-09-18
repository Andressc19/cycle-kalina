"""Componente HRVG (Heat Recovery Vapor Generator) del ciclo Kalina KSC-11.

Método de efectividad (CONTEXT.md, "Fórmulas de efectividad"):
    ε_HRVG = (h2 − h1) / (h2,max − h1),  h2,max = h(P_alta, T_fuente, x_b)
    h2 = h1 + ε_HRVG · (h2,max − h1)

Consume únicamente la interfaz `PropertyBackend` (patrón adapter): nunca importa
un backend concreto.
"""

from __future__ import annotations

from ..properties.adapter import PropertyBackend
from ..state import EstadoTermo

__all__ = ["resolver"]


def resolver(
    entrada: EstadoTermo,
    backend: PropertyBackend,
    *,
    T_fuente: float,
    eps: float,
    m_b: float,
) -> tuple[EstadoTermo, dict]:
    """Calienta la corriente 1 (entrada) hasta la corriente 2 (salida HRVG).

    Parámetros: ``T_fuente`` [K] temperatura de la fuente térmica, ``eps`` = ε_HRVG
    [-], ``m_b`` [kg/s] caudal base (el que circula por el HRVG).

    Devuelve ``(estado 2, {"Qi": m_b·(h2 − h1)})`` con ``Qi`` en kW (kg/s ·
    kJ/kg = kJ/s = kW). El título/fase de la salida quedan en ``None``: la
    interfaz no los expone.
    """
    P_alta = entrada.P
    x_b = entrada.x
    h1 = entrada.h

    h2_max = backend.h(P_alta, T=T_fuente, x=x_b)
    h2 = h1 + eps * (h2_max - h1)

    T2 = backend.T_from_Ph(P_alta, h2, x=x_b)
    s2 = backend.s(P_alta, T=T2, x=x_b)

    estado2 = EstadoTermo(
        T=T2, P=P_alta, h=h2, s=s2, x=x_b, m=m_b, etiqueta="2"
    )
    return estado2, {"Qi": m_b * (h2 - h1)}
