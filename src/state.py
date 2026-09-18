"""Tipo compartido `EstadoTermo`: un punto del ciclo Kalina KSC-11.

Es un **contenedor de datos puro**, sin lógica de propiedades: los componentes
(`src/components/`) son los que consultan el `PropertyBackend` y construyen o
transforman estos estados. Unidades canónicas de la interfaz de propiedades:
T [K], P [kPa], h [kJ/kg], s [kJ/kg·K], x = fracción másica de NH3 [-], m [kg/s].

`q`, `fase` y `exergia_fisica` pueden quedar en `None`: la interfaz
`PropertyBackend` no expone el título/fase (solo lo hace el motor real como
salida interna), así que los componentes los dejan sin calcular salvo donde el
propio componente los conoce (p.ej. las fases saturadas del separador). La
exergía física se llena en la tarea de exergía, no aquí.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["EstadoTermo"]


@dataclass
class EstadoTermo:
    T: float
    P: float
    h: float
    s: float
    x: float                          # fracción másica de NH3 en esta corriente
    m: float | None = None            # kg/s, caudal de esta corriente
    q: float | None = None            # título: 0 = líq. sat., 1 = vap. sat.
    fase: str | None = None           # 'liquido' | 'vapor' | 'bifasico' | None
    exergia_fisica: float | None = None  # kJ/kg (tarea de exergía, no aquí)
    etiqueta: str | None = None       # "1", "2", ... del mapa de estados
