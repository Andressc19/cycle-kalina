"""Renderizado de inputs del ciclo Kalina KSC-11.

Tarea 2026-09-17-ui-streamlit (apartado visual de inputs). Los grupos de
parámetros se dibujan en el ÁREA PRINCIPAL en una grilla de 2 columnas
(`st.columns(2)`): a la izquierda, apilados de arriba a abajo, "Condiciones de
borde", "Presiones del ciclo" y "Composición y flujo"; a la derecha, en un
contenedor que ocupa todo el alto, "Rendimiento de equipos" y, justo debajo,
VISIBLE sin plegar, "Criterio de diseño (cavitación)" con el piso
`T_amb_diseno` (criterio O2) y el checkbox "Aplicar margen de peor caso":
marcado (default) → campo editable y se usa tal cual; desmarcado → campo
deshabilitado y el valor efectivo es `T_sumidero` de la corrida, sin margen.
Debajo, a ancho completo, va el expander plegado "Estado muerto (exergía)"
(T0/P0). La barra lateral queda reservada para el panel de ejecución (motor de
propiedades, aviso de tiempo y botón). Anatomía de cada campo: un
`st.markdown` con el símbolo LaTeX y su unidad arriba del widget (los labels
de `st.number_input` NO renderizan `$...$`) y, debajo, la etiqueta corta con
tooltip (los help SÍ renderizan `$...$`). Cada widget usa la key explícita
`input_<clave>` para que el orden de renderizado quede estable entre reruns.
"""

from __future__ import annotations

import streamlit as st

from src import ui_backend, ui_estilo, ui_helpers

__all__ = ["renderizar_inputs", "renderizar_panel_ejecucion"]


def _campo_num(campo, disabled=False):
    """Símbolo LaTeX (markdown) + number_input; devuelve el valor actual.
    ``disabled=True`` pinta el widget gris y no editable (se usa cuando el
    checkbox de margen de peor caso está desmarcado)."""
    st.markdown(f"**{campo.simbolo}**")
    return st.number_input(
        campo.etiqueta, min_value=campo.vmin, max_value=campo.vmax,
        value=campo.default, step=campo.paso, format=campo.formato,
        help=campo.ayuda, key=f"input_{campo.clave}", disabled=disabled)


def _render_filas(campos, destino):
    """Campos en filas de 2 columnas (la última puede quedar con uno solo)."""
    for i in range(0, len(campos), 2):
        cols = st.columns(2)
        for campo, col in zip(campos[i:i + 2], cols):
            with col:
                destino[campo.clave] = _campo_num(campo)


def _seccion(nombre, campos, destino):
    """Una sección bordeada con el encabezado del grupo y sus campos."""
    with st.container(border=True):
        ui_estilo.encabezado("", nombre)
        _render_filas(campos, destino)


def _render_expander(titulo, campos, destino):
    """Bloque a ancho completo, plegado, con los ``campos`` del grupo."""
    with st.expander(titulo, expanded=False):
        with st.container(border=True):
            _render_filas(campos, destino)


def _seccion_tamb_diseno(campos, destino):
    """`T_amb_diseno` VISIBLE (sin plegar), justo debajo de "Rendimiento de
    equipos" en la columna derecha. El checkbox "Aplicar margen de peor caso"
    (True por defecto, preserva el comportamiento actual) controla el campo:
    marcado → editable y se usa tal cual; desmarcado → el widget se
    deshabilita y el valor efectivo que usa `app._ejecutar` es `T_sumidero`
    de la corrida (sin margen; el `max(T_sumidero, T_amb_diseno)` del
    criterio O2 colapsa a `T_sumidero`). El estado del checkbox viaja en
    `destino["aplica_margen_o2"]` para que `app.py` lo lea."""
    with st.container(border=True):
        ui_estilo.encabezado("", "Criterio de diseño (cavitación)")
        aplica = st.checkbox(
            "Aplicar margen de peor caso", value=True,
            key="input_aplica_margen_o2",
            help="Marcado (por defecto): se usa T_amb_diseno tal cual, con el "
                 "margen de peor caso sobre T_sumidero. Desmarcado: el "
                 "criterio O2 se evalúa solo contra T_sumidero de esta "
                 "corrida, sin margen adicional.")
        for campo in campos:
            destino[campo.clave] = _campo_num(campo, disabled=not aplica)
        if not aplica:
            st.caption(f"Margen desactivado: esta corrida usará "
                       f"T_sumidero = {destino['T_sumidero']:.3f} K como "
                       "T_amb_diseno efectiva (sin margen de peor caso).")
        destino["aplica_margen_o2"] = aplica


def renderizar_inputs():
    """Izquierda: 3 grupos apilados; derecha: Rendimiento de equipos y, justo
    debajo, visible sin plegar, el criterio de diseño (T_amb_diseno + checkbox
    de margen); estado muerto (T0/P0) a ancho completo. Devuelve los valores."""
    destino = {}
    grupos = ui_helpers.agrupar_campos(ui_helpers.CAMPOS_CICLO)
    col_izq, col_der = st.columns(2)
    with col_izq:
        for nombre, campos in grupos[:-1]:
            _seccion(nombre, campos, destino)
    with col_der:
        for nombre, campos in grupos[-1:]:
            _seccion(nombre, campos, destino)
        _seccion_tamb_diseno(ui_helpers.CAMPOS_DISENO, destino)
    _render_expander("Estado muerto (exergía)",
                     ui_helpers.CAMPOS_ESTADO, destino)
    return destino


def _seccion_backend():
    """Selector de motor de propiedades + nota al pie (texto plano)."""
    with st.container(border=True):
        ui_estilo.encabezado("", "Motor de propiedades")
        backend = st.selectbox(
            "Backend de propiedades", ui_backend.BACKENDS, index=0,
            key="select_backend",
            help="AmmoniaWaterAdapter (motor riguroso) y TeqpAdapter (NIST "
                 "teqp, más rápido) soportan la mezcla NH3-H2O en este "
                 "entorno.")
        st.caption("IAPWSAdapter (agua pura) y PyfluidsAdapter (CoolProp) no "
                   "cubren la mezcla NH3-H2O; se listan solo como referencia.")
    return backend


def renderizar_panel_ejecucion():
    """Panel lateral de ejecución; devuelve (backend, botón_pulsado)."""
    ui_estilo.encabezado("⚙️", "Ejecución")
    st.caption("Defina los parámetros en el área principal y ejecute la "
               "simulación desde aquí.")
    backend = _seccion_backend()
    if backend == ui_backend.BACKENDS[1]:
        st.markdown(
            "⏱️ **TeqpAdapter resuelve el ciclo en decenas de segundos** "
            "(~10-20x más rápido que el motor riguroso). No cierres esta "
            "pestaña mientras corre."
        )
    else:
        st.markdown(
            "⏱️ **El cálculo con el motor de propiedades real puede tardar "
            "varios minutos (~8-9 min). No cierres esta pestaña ni pulses el "
            "botón de nuevo mientras corre.**"
        )
    ejecutar = st.button("Ejecutar simulación", type="primary",
                         width="stretch")
    return backend, ejecutar