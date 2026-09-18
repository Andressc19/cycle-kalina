"""Tests de las gráficas matplotlib del ciclo Kalina KSC-11.

Usa los mismos datos de ejemplo construidos a mano (`tests/_datos_ejemplo.py`,
sin backend real ni `resolver_ciclo`). Verifica la ESTRUCTURA de las figuras
— tipo `matplotlib.figure.Figure`, número de barras y datos que alimentan
cada barra (`ax.patches`) — no pixel-perfect.
"""

from __future__ import annotations

import pytest
from matplotlib.figure import Figure

from src.plots import grafico_balance_energia, grafico_exergia_destruida
from tests._datos_ejemplo import (resultado_ciclo_ejemplo,
                                  resultado_exergia_ejemplo)


def test_balance_energia_devuelve_figure_con_5_barras():
    fig = grafico_balance_energia(resultado_ciclo_ejemplo())
    assert isinstance(fig, Figure)
    ax = fig.axes[0]
    assert len(ax.patches) == 5
    alturas = [round(p.get_height(), 2) for p in ax.patches]
    assert alturas == [50.0, 44.0, 11.3, 12.6, -1.3]
    assert [t.get_text() for t in ax.get_xticklabels()] == \
        ["Qi", "Qout", "Wt", "Wp", "Wnet"]
    assert ax.get_ylabel() == "Energía [kW]"
    assert ax.get_title() == "Balance de energía del ciclo"


def test_exergia_destruida_8_barras_ordenadas_de_mayor_a_menor():
    fig = grafico_exergia_destruida(resultado_exergia_ejemplo())
    assert isinstance(fig, Figure)
    ax = fig.axes[0]
    assert len(ax.patches) == 8
    alturas = [round(p.get_height(), 1) for p in ax.patches]
    assert alturas == sorted(alturas, reverse=True)
    assert alturas == [112.5, 30.0, 15.0, 4.5, -7.5, -30.0, -30.0, -88.0]
    # etiquetas en español, alineadas con el orden de las barras
    # (sort estable con reverse=True: los empates conservan el orden original
    # del dict — turbina antes que regenerador, ambas con Ed = −30 kW).
    assert [t.get_text() for t in ax.get_xticklabels()] == \
        ["HRVG", "Bomba", "Separador", "Absorbedor", "Válvula",
         "Turbina", "Regenerador", "Condensador"]
    assert ax.get_ylabel() == "Exergía destruida [kW]"