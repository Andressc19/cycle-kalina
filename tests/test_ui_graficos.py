"""Test del diagrama T-s interactivo (Altair) de `src/ui_graficos.py`.

No verifica estilo, solo que la figura se construye a partir de los 10 estados
y devuelve una capa válida de Altair (el render real lo hace Streamlit).
"""

from __future__ import annotations

from src import ui_graficos
from src.state import EstadoTermo


def _estados_fake() -> dict:
    return {f"e{i}": EstadoTermo(T=300.0 + 10.0 * i, P=1000.0, h=100.0 + i,
                                 s=1.0 + 0.1 * i, x=0.5)
            for i in range(1, 11)}


def test_grafico_ts_construye_una_capa_altair():
    estados = _estados_fake()
    chart = ui_graficos.grafico_ts({"estados": estados}, {"estados": estados})
    spec = chart.to_dict()
    assert "layer" in spec
    assert len(spec["layer"]) == 2  # líneas + etiquetas de estado
