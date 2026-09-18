"""Renderizado de inputs del ciclo Kalina KSC-11.

Tarea 2026-09-17-ui-streamlit (apartado visual de inputs). Los grupos de
parámetros se dibujan en el ÁREA PRINCIPAL en una grilla de 2 columnas
(`st.columns(2)`): a la izquierda, apilados de arriba a abajo, "Condiciones de
borde", "Presiones del ciclo" y "Composición y flujo"; a la derecha, en un
contenedor que ocupa todo el alto, "Rendimiento de equipos". Debajo, a ancho
completo, va el expander plegado "Estado muerto (exergía)".
La barra lateral queda reservada para el panel de ejecución (motor de
propiedades, aviso de tiempo y botón). Anatomía de cada campo: un
`st.markdown` con el símbolo LaTeX y su unidad arriba del widget (los labels
de `st.number_input` NO renderizan `$...$`) y, debajo, la etiqueta corta con
tooltip (los help SÍ renderizan `$...$`). Cada widget usa la key explícita
`input_<clave>` para que el orden de renderizado quede estable entre reruns.
"""

from __future__ import annotations

import streamlit as st

from src import ui_helpers

__all__ = ["renderizar_inputs", "renderizar_panel_ejecucion"]


def _campo_num(campo):
    """Símbolo LaTeX (markdown) + number_input; devuelve el valor actual."""
    st.markdown(f"**{campo.simbolo}**")
    return st.number_input(
        campo.etiqueta, min_value=campo.vmin, max_value=campo.vmax,
        value=campo.default, step=campo.paso, format=campo.formato,
        help=campo.ayuda, key=f"input_{campo.clave}")


def _render_filas(campos, destino):
    """Campos en filas de 2 columnas (la última puede quedar con uno solo)."""
    for i in range(0, len(campos), 2):
        cols = st.columns(2)
        for campo, col in zip(campos[i:i + 2], cols):
            with col:
                destino[campo.clave] = _campo_num(campo)


def _agrupar(campos):
    """Separa el esquema en secciones respetando el orden de definición."""
    grupos = []
    for campo in campos:
        if grupos and grupos[-1][0] == campo.grupo:
            grupos[-1][1].append(campo)
        else:
            grupos.append([campo.grupo, [campo]])
    return grupos


def _seccion(nombre, campos, destino):
    """Una sección bordeada con el encabezado del grupo y sus campos."""
    with st.container(border=True):
        st.markdown(f"**{nombre}**")
        _render_filas(campos, destino)


def _render_estado_muerto(destino):
    """Bloque a ancho completo, plegado, con T0/P0 (exergía)."""
    with st.expander("Estado muerto (exergía)", expanded=False):
        with st.container(border=True):
            _render_filas(ui_helpers.CAMPOS_ESTADO, destino)


def renderizar_inputs():
    """Izquierda: 3 grupos apilados; derecha: Rendimiento de equipos; +
    estado muerto a ancho completo. Devuelve los valores."""
    destino = {}
    grupos = _agrupar(ui_helpers.CAMPOS_CICLO)
    col_izq, col_der = st.columns(2)
    with col_izq:
        for nombre, campos in grupos[:-1]:
            _seccion(nombre, campos, destino)
    with col_der:
        for nombre, campos in grupos[-1:]:
            _seccion(nombre, campos, destino)
    _render_estado_muerto(destino)
    return destino


def _seccion_backend():
    """Selector de motor de propiedades + nota al pie (texto plano)."""
    with st.container(border=True):
        st.markdown("**Motor de propiedades**")
        backend = st.selectbox(
            "Backend de propiedades", ui_helpers.BACKENDS, index=0,
            key="select_backend",
            help="AmmoniaWaterAdapter es el único motor que soporta la mezcla "
                 "NH3-H2O en este entorno.")
        st.caption("IAPWSAdapter (agua pura) y PyfluidsAdapter (CoolProp) no "
                   "cubren la mezcla NH3-H2O; se listan solo como referencia.")
    return backend


def renderizar_panel_ejecucion():
    """Panel lateral de ejecución; devuelve (backend, botón_pulsado)."""
    st.header("Ejecución")
    st.caption("Defina los parámetros en el área principal y ejecute la "
               "simulación desde aquí.")
    backend = _seccion_backend()
    st.markdown(
        "⏱️ **El cálculo con el motor de propiedades real puede tardar varios "
        "minutos (~8-9 min). No cierres esta pestaña ni pulses el botón de "
        "nuevo mientras corre.**"
    )
    ejecutar = st.button("Ejecutar simulación", type="primary",
                         width="stretch")
    return backend, ejecutar