"""Gráficos interactivos (Altair) para la UI Streamlit del ciclo Kalina.

Separado de `plots.py` (matplotlib estático, sin interacción) porque Altair
produce figuras con hover/zoom/etiquetas y viene incluido con Streamlit (sin
dependencia extra). Por ahora: el diagrama T-s del ciclo, que une los 10
estados en los dos tramos del lazo (principal 1→2→3→4→8→9→10→1 y la rama
líquida 2→5→6→7→8 del separador).
"""

from __future__ import annotations

import altair as alt
import pandas as pd

__all__ = ["grafico_ts"]

# Cada tramo es la secuencia de estados unidos por una línea (el ciclo se
# cierra repitiendo e1 al final del tramo principal).
_TRAMOS = (
    ("principal", ("e1", "e2", "e3", "e4", "e8", "e9", "e10", "e1")),
    ("rama líquida", ("e2", "e5", "e6", "e7", "e8")),
)


def grafico_ts(resultado_ciclo: dict, resultado_exergia: dict) -> alt.Chart:
    """Diagrama T-s interactivo: T [K] vs s [kJ/kg·K] de los 10 estados.

    Usa los estados de ``resultado_exergia`` si están (mismos T y s que el
    ciclo). Hover con el número de estado, T y s; zoom/pan con el mouse.
    """
    estados = resultado_exergia.get("estados", resultado_ciclo["estados"])
    filas = []
    for tramo, claves in _TRAMOS:
        for orden, clave in enumerate(claves):
            e = estados[clave]
            filas.append({"Tramo": tramo, "orden": orden, "Estado": clave[1:],
                          "s [kJ/kg·K]": round(e.s, 4), "T [K]": round(e.T, 2)})
    df = pd.DataFrame(filas)
    base = alt.Chart(df).encode(
        x=alt.X("s [kJ/kg·K]:Q", title="Entropía s [kJ/kg·K]"),
        y=alt.Y("T [K]:Q", title="Temperatura T [K]"),
        color=alt.Color("Tramo:N", title="Tramo"),
        tooltip=["Estado:N", "T [K]:Q", "s [kJ/kg·K]:Q"],
    )
    lineas = base.mark_line(
        point=alt.OverlayMarkDef(size=70), strokeWidth=2).encode(
        detail="Tramo:N", order="orden:Q")
    etiquetas = base.mark_text(dx=8, dy=-8, fontSize=12).encode(text="Estado:N")
    return (lineas + etiquetas).properties(
        height=440, title="Diagrama T-s del ciclo").interactive()
