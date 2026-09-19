"""Etiqueta de UI para la `Clasificacion` de `src/restricciones`.

Separado de `ui_helpers.py` (por espacio, no por tema) para que la caja de
clasificación de `app.py` no tenga que ir a buscar el texto de presentación
mezclado entre las demás utilidades de tablas/figuras.
"""

from __future__ import annotations

__all__ = ["CLASIFICACION_INFO"]

# Etiqueta legible + método st.<tipo> por `Clasificacion` de `restricciones`
# (ver ese módulo para el significado de cada una), de más a menos severa.
CLASIFICACION_INFO = {
    "NO_CONVERGIO": ("NO CONVERGIÓ", "error"),
    "INVIABLE": ("INVIABLE", "error"),
    "DEGENERADO": ("DEGENERADO — ya no opera como ciclo Kalina", "warning"),
    "CORREGIBLE": ("CORREGIBLE — ajustable en el diseño", "warning"),
    "VALIDO_ADVERTENCIA": ("VÁLIDO CON ADVERTENCIA", "info"),
    "KALINA": ("KALINA — régimen genuino y admisible", "success"),
}
