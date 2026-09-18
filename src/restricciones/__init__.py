"""Validaciones termodinámicas y clasificación del ciclo Kalina KSC-11.

Punto de entrada público: `evaluar_ciclo`. Ver `clasificacion.py` para el
catálogo de criterios implementados y los que quedan fuera de alcance.
"""

from __future__ import annotations

from .clasificacion import NO_APLICA, evaluar_ciclo
from .modelos import Clasificacion, Falla, ResultadoValidacion, Severidad

__all__ = ["evaluar_ciclo", "NO_APLICA", "Clasificacion", "Falla",
          "ResultadoValidacion", "Severidad"]
