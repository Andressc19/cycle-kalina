"""Gráficas matplotlib de los resultados del ciclo Kalina KSC-11.

Dos figuras mínimas para la UI Streamlit (tarea siguiente): balance de
energía y exergía destruida por componente. Se construyen con
``matplotlib.figure.Figure`` directa — sin ``pyplot``, sin ``plt.close()``:
no hay figura global que cerrar y quien la use (p.ej. ``st.pyplot``) decide
cuándo liberarla. Etiquetas y títulos en español, ejes con unidades.
"""

from __future__ import annotations

from matplotlib.figure import Figure

__all__ = ["grafico_balance_energia", "grafico_exergia_destruida"]

_NOMBRES = {"hrvg": "HRVG", "separador": "Separador", "turbina": "Turbina",
            "regenerador": "Regenerador", "valvula": "Válvula",
            "absorbedor": "Absorbedor", "condensador": "Condensador",
            "bomba": "Bomba"}


def grafico_balance_energia(resultado_ciclo: dict) -> Figure:
    """Barras de Qi, Qout, Wt, Wp y Wnet [kW] del ciclo resultante."""
    magnitudes = ("Qi", "Qout", "Wt", "Wp", "Wnet")
    fig = Figure(figsize=(8, 5))
    ax = fig.subplots()
    ax.bar(magnitudes, [resultado_ciclo[n] for n in magnitudes],
           color="#1f77b4")
    ax.axhline(0.0, color="gray", linewidth=0.8)
    ax.set_title("Balance de energía del ciclo")
    ax.set_ylabel("Energía [kW]")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


def grafico_exergia_destruida(resultado_exergia: dict) -> Figure:
    """Barras de Ed por los 8 componentes, de mayor a menor destrucción.

    Lee ``resultado_exergia["ed"]`` (dict componente -> Ed [kW]); las barras
    salen ordenadas de mayor a menor para ver de un vistazo qué componente
    domina la destrucción de exergía.
    """
    pares = sorted(((_NOMBRES[k], v) for k, v in resultado_exergia["ed"].items()),
                   key=lambda p: p[1], reverse=True)
    fig = Figure(figsize=(8, 5))
    ax = fig.subplots()
    ax.bar([p[0] for p in pares], [p[1] for p in pares], color="#d62728")
    ax.set_title("Exergía destruida por componente")
    ax.set_ylabel("Exergía destruida [kW]")
    ax.tick_params(axis="x", rotation=30)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig