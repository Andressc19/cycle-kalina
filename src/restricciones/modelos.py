"""Tipos compartidos del módulo de restricciones: `Falla`, `Severidad`, `Clasificacion`.

Catálogo de 19 criterios de admisibilidad del ciclo Kalina KSC-11 (N2-N4, S1-S8,
O1-O3/O5, C1-C3 — ver `restricciones/clasificacion.py` para la fuente de cada
criterio y qué queda fuera de alcance en esta arquitectura).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

__all__ = ["Severidad", "Clasificacion", "Falla", "ResultadoValidacion"]


class Severidad(str, Enum):
    """Severidad de un criterio (catálogo del vault, ver clasificacion.py)."""
    NUMERICO = "numerico"
    CRITICO = "critico"
    TOPOLOGICO = "topologico"
    TECNOLOGICO = "tecnologico"


class Clasificacion(str, Enum):
    """Etiqueta resultante de un punto del ciclo, de más a menos severa."""
    NO_CONVERGIO = "NO_CONVERGIO"
    INVIABLE = "INVIABLE"
    DEGENERADO = "DEGENERADO"          # topológico: ya no es Kalina (Rankine)
    CORREGIBLE = "CORREGIBLE"          # O2: cavitación, ajustable en diseño
    VALIDO_ADVERTENCIA = "VALIDO_ADVERTENCIA"
    KALINA = "KALINA"


# Orden de severidad (índice bajo = más severo). Determina la falla "principal"
# cuando varios criterios fallan a la vez en el mismo punto.
_ORDEN_CLASIFICACION = {
    Clasificacion.NO_CONVERGIO: 0,
    Clasificacion.INVIABLE: 1,
    Clasificacion.DEGENERADO: 2,
    Clasificacion.CORREGIBLE: 3,
    Clasificacion.VALIDO_ADVERTENCIA: 4,
    Clasificacion.KALINA: 5,
}


@dataclass
class Falla:
    """Una violación de un criterio de admisibilidad, con contexto reportable."""
    codigo: str                    # p.ej. "O5", "S6", "C1"
    severidad: Severidad
    clasificacion: Clasificacion   # etiqueta que produce ESTA falla específica
    mensaje: str                   # mensaje breve y legible
    variable: str                  # variable/estado involucrado (p.ej. "T9", "x")
    valor_medido: float
    valor_esperado: str            # rango o valor esperado, como texto
    causa_probable: str
    sugerencia: str


@dataclass
class ResultadoValidacion:
    """Resultado de validar un punto ya resuelto del ciclo."""
    clasificacion: Clasificacion
    fallas: list[Falla] = field(default_factory=list)
    no_aplica: tuple[str, ...] = ()

    @property
    def principal(self) -> Falla | None:
        """La falla de mayor severidad (o None si `clasificacion` es KALINA)."""
        if not self.fallas:
            return None
        return min(self.fallas, key=lambda f: _ORDEN_CLASIFICACION[f.clasificacion])

    @property
    def secundarias(self) -> list[Falla]:
        """Todas las demás fallas, salvo la principal."""
        principal = self.principal
        return [f for f in self.fallas if f is not principal]

    def mensaje_reporte(self) -> str:
        """Mensaje jerárquico: principal en detalle, secundarias en una línea c/u."""
        if self.clasificacion == Clasificacion.KALINA:
            return "KALINA: régimen Kalina genuino y admisible, sin fallas."
        principal = self.principal
        lineas = [
            f"[{self.clasificacion.value}] {principal.codigo}: {principal.mensaje} "
            f"(medido={principal.valor_medido!r}, esperado={principal.valor_esperado}). "
            f"Causa probable: {principal.causa_probable}. Sugerencia: {principal.sugerencia}"
        ]
        for f in self.secundarias:
            lineas.append(
                f"  - [{f.clasificacion.value}] {f.codigo}: {f.mensaje} "
                f"(medido={f.valor_medido!r}, esperado={f.valor_esperado}). "
                f"Sugerencia: {f.sugerencia}"
            )
        return "\n".join(lineas)
