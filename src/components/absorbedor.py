"""Componente absorbedor del ciclo Kalina KSC-11.

Mezcla adiabática de las corrientes 4 (salida turbina) y 7 (salida válvula), sin
caída de presión ni modelo cinético (CONTEXT.md, "Absorbedor"):

    ṁ8 = ṁ4 + ṁ7
    x8 = (ṁ4·x4 + ṁ7·x7) / ṁ8          (balance de especie; en régimen
                                        estacionario reconstruye x_b)
    ṁ8·h8 = ṁ4·h4 + ṁ7·h7              (balance de energía)
"""

from __future__ import annotations

from ..properties.adapter import PropertyBackend
from ..state import EstadoTermo

__all__ = ["resolver"]


def resolver(
    entrada_turbina: EstadoTermo,
    entrada_valvula: EstadoTermo,
    backend: PropertyBackend,
    *,
    m_turbina: float,
    m_valvula: float,
) -> tuple[EstadoTermo, dict]:
    """Mezcla las corrientes 4 y 7 en la corriente 8.

    ``P8`` se toma de ``entrada_turbina.P`` (sin caída de presión; ambas
    entradas están a ``P_baja``). Devuelve ``(estado 8, {})``: la mezcla es
    adiabática, así que no reporta Q ni W externos.
    """
    m4 = m_turbina
    m7 = m_valvula
    m8 = m4 + m7

    h8 = (m4 * entrada_turbina.h + m7 * entrada_valvula.h) / m8
    x8 = (m4 * entrada_turbina.x + m7 * entrada_valvula.x) / m8
    P8 = entrada_turbina.P

    T8 = backend.T_from_Ph(P8, h8, x=x8)
    s8 = backend.s(P8, T=T8, x=x8)

    estado8 = EstadoTermo(T=T8, P=P8, h=h8, s=s8, x=x8, m=m8, etiqueta="8")
    return estado8, {}
