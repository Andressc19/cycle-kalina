"""Columnas de rango confiable en las filas de `sensitivity.ejecutar_barrido`.

La tabla del barrido no tiene columnas por estado, así que cuando un estado
interno sale de rango se señalan `eta` y `Wnet` (los números a tomar con pinzas);
si lo que sale de rango es una entrada (`P_alta`, ...), se señala esa celda. La
clasificación de la fila NO se toca.
"""

from __future__ import annotations

from .rangos_motor import evaluar_rango, evaluar_rango_entradas

__all__ = ["COLUMNAS_RANGO", "anotar_rango"]

COLUMNAS_RANGO = ("fuera_rango", "detalle_rango", "columnas_rango")
_RESULTADOS = ("eta", "Wnet")


def anotar_rango(fila: dict, combo: dict, resultado, motor, backend,
                 modo: str) -> dict:
    """Añade `COLUMNAS_RANGO` a `fila`; con `motor=None` la devuelve intacta."""
    if motor is None:
        return fila
    if resultado is None:
        viol = evaluar_rango_entradas(motor, combo, modo=modo)
    else:
        viol = evaluar_rango(motor, resultado, backend=backend, modo=modo)
    cols = []
    for v in viol:
        destino = (v.columna,) if v.columna in fila else _RESULTADOS
        cols.extend(c for c in destino if c not in cols)
    fila.update(fuera_rango=bool(viol),
                detalle_rango="; ".join(v.texto() for v in viol) or None,
                columnas_rango=";".join(cols) or None)
    return fila
