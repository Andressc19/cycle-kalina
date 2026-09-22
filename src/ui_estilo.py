"""Estilo visual (CSS + encabezados) de la UI Streamlit del ciclo Kalina.

`aplicar_estilo` inyecta un CSS acotado y moderno que el tema de
`.streamlit/config.toml` no cubre: tarjetas para las métricas, botones
redondeados, sidebar con separador y tabs prolijos. `encabezado` pinta los
títulos de sección con un icono, para que todas las secciones se vean igual.

Los selectores `data-testid` son los de Streamlit (estables dentro de la
versión pinneada 1.56.0); si alguna vez cambian, el CSS simplemente no aplica
y la app sigue funcionando igual.
"""

from __future__ import annotations

import streamlit as st

__all__ = ["aplicar_estilo", "encabezado"]

_CSS = """
<style>
:root {
    --kalina-borde: #E2E8F0;
    --kalina-sombra: 0 1px 2px rgba(15, 23, 42, .06);
    --kalina-radio: 12px;
}

/* Métricas como tarjetas */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid var(--kalina-borde);
    border-radius: var(--kalina-radio);
    padding: 14px 16px;
    box-shadow: var(--kalina-sombra);
}
[data-testid="stMetricLabel"] p { font-weight: 600; color: #475569; }

/* Botones y descargas */
.stButton > button, .stDownloadButton > button {
    border-radius: 10px;
    font-weight: 600;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #F8FAFC;
    border-right: 1px solid var(--kalina-borde);
}

/* Tabs */
[data-testid="stTabs"] button { font-weight: 600; }

/* Contenedores bordeados (cards de inputs/secciones) */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: var(--kalina-radio);
}

/* Encabezado de sección reutilizable */
.kalina-seccion {
    display: flex; align-items: center; gap: .5rem;
    margin: 1.1rem 0 .35rem 0;
    font-size: 1.02rem; font-weight: 700; color: #0F172A;
    letter-spacing: -.01em;
}
</style>
"""


def aplicar_estilo() -> None:
    """Inyecta el CSS del rediseño (idempotente: se re-aplica en cada rerun)."""
    st.markdown(_CSS, unsafe_allow_html=True)


def encabezado(icono: str, texto: str) -> None:
    """Título de sección con icono, consistente en toda la app."""
    st.markdown(f'<div class="kalina-seccion">{icono} {texto}</div>',
                unsafe_allow_html=True)
