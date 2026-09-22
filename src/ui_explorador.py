"""Explorador interactivo (PyGWalker) de los DataFrames de resultados.

Envuelve `pygwalker.api.streamlit.StreamlitRenderer` con el renderer cacheado
(la doc de PyGWalker avisa que sin cache la memoria puede explotar) y la
telemetría apagada (`GlobalVarManager.set_privacy("offline")` — PyGWalker
manda eventos anónimos por defecto vía kanaries_track/segment). Si pygwalker
no estuviera disponible, cae a un `st.dataframe` plano para no romper la app.

OJO: PyGWalker exige Streamlit <= 1.56.0 (usa la API interna
`streamlit.web.server.server_util.make_url_path_regex`, eliminada en 1.57.0)
— ver el pin y su comentario en requirements.txt.
"""

from __future__ import annotations

import streamlit as st

__all__ = ["explorar"]

_telemetria_apagada = False


def _apagar_telemetria() -> None:
    """Desactiva el envío de eventos anónimos de PyGWalker (una sola vez)."""
    global _telemetria_apagada
    if _telemetria_apagada:
        return
    try:
        from pygwalker.services.global_var import GlobalVarManager
        GlobalVarManager.set_privacy("offline")
    except Exception:
        pass
    _telemetria_apagada = True


@st.cache_resource(show_spinner=False, max_entries=3)
def _renderer(df, gid: str):
    """Renderer de PyGWalker cacheado por (contenido del DataFrame, gid)."""
    from pygwalker.api.streamlit import StreamlitRenderer
    return StreamlitRenderer(df, gid=gid)


def explorar(df, gid: str) -> None:
    """Explorador drag-and-drop del DataFrame (o tabla plana si no hay pygwalker).

    ``gid`` identifica al explorador dentro de la página (permite varios en la
    misma app sin que choquen las claves de los componentes).
    """
    _apagar_telemetria()
    try:
        renderer = _renderer(df, gid)
    except Exception as exc:  # pygwalker ausente o incompatible
        st.caption(f"Explorador interactivo no disponible ({exc}). Tabla plana:")
        st.dataframe(df, hide_index=True)
        return
    st.caption("Arrastre campos a los ejes para explorar; el resultado es "
               "interactivo (zoom, filtros, tipos de gráfico).")
    renderer.explorer(key=f"explorer_{gid}")
