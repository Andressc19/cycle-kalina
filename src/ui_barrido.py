"""Panel de barrido para la pestaña "Sensibilidad paramétrica" de la UI.

Es el contenido de una pestaña de nivel superior (ver `app.py::main`,
hermana de "Análisis puntual" — la página principal de una sola corrida).
No lleva encabezado ni acordeón propios: la pestaña ya lo identifica.

Envuelve `src/sensitivity.py` (barrido cartesiano `Fijo`/`Barrido` +
`restricciones.evaluar_ciclo`): una fila por variable de
`sensitivity.VARIABLES_BARRIBLES`, con un radio Fijo/Barrido y sus campos
numéricos (`inicio→fin→paso` si está en Barrido), reutilizando los límites
y valores por defecto de `ui_helpers.CAMPOS_CICLO`. Con más de una
variable en Barrido, el resultado es el producto cartesiano de todas.

Misma distribución que "Análisis puntual" (`ui_inputs.renderizar_inputs`):
las 11 variables agrupadas con `ui_helpers.agrupar_campos` en secciones
bordeadas ("Condiciones de borde", "Presiones del ciclo", "Composición y
flujo" a la izquierda; "Rendimiento de equipos" a la derecha) — así cada
fila (más ancha aquí por el radio y, en Barrido, sus 3 columnas
inicio/fin/paso) queda organizada por tema en vez de una lista plana de
11 filas apiladas.

El backend se construye con `ui_backend.construir_backend` (misma
selección que la pestaña de análisis puntual), así que TeqpAdapter también
sirve para explorar rangos. Un tope de puntos evita lanzar una rejilla que
tardaría horas con el motor riguroso desde la UI.

El barrido corre en lotes de un punto entre reruns de Streamlit: mientras
está activo se muestra progreso y resultado parcial, con un botón
**Cancelar** que detiene la corrida y conserva los puntos ya resueltos.
"""

from __future__ import annotations

import streamlit as st

from src import sensitivity, ui_backend, ui_helpers

__all__ = ["renderizar_panel_barrido"]

_TOPE_PUNTOS = 300

_BARRILLO_ESTADO = "barrido_en_curso"
_PUNTOS_POR_LOTE = 1
_ULTIMOS_PREVIEW = 10


def _fila_barrido(campo, valor_actual):
    """Fila de una variable: símbolo + radio Fijo/Barrido + sus widgets."""
    c1, c2 = st.columns([2, 3])
    with c1:
        st.markdown(f"**{campo.simbolo}**")
        modo = st.radio(
            campo.etiqueta, ("Fijo", "Barrido"), horizontal=False,
            key=f"barrido_modo_{campo.clave}", label_visibility="collapsed")
    with c2:
        if modo == "Fijo":
            valor = st.number_input(
                "Valor", min_value=campo.vmin, max_value=campo.vmax,
                value=valor_actual, step=campo.paso, format=campo.formato,
                key=f"barrido_fijo_{campo.clave}")
            return campo.clave, sensitivity.Fijo(valor)
        bc1, bc2, bc3 = st.columns(3)
        inicio = bc1.number_input(
            "Inicio", min_value=campo.vmin, max_value=campo.vmax,
            value=campo.vmin, step=campo.paso, format=campo.formato,
            key=f"barrido_ini_{campo.clave}")
        fin = bc2.number_input(
            "Fin", min_value=campo.vmin, max_value=campo.vmax,
            value=campo.vmax, step=campo.paso, format=campo.formato,
            key=f"barrido_fin_{campo.clave}")
        paso = bc3.number_input(
            "Paso", min_value=campo.paso, max_value=max(campo.vmax - campo.vmin, campo.paso),
            value=campo.paso, step=campo.paso, format=campo.formato,
            key=f"barrido_paso_{campo.clave}")
        return campo.clave, sensitivity.Barrido(min(inicio, fin), max(inicio, fin), paso)


def _seccion_barrido(nombre: str, campos, vals: dict, destino: dict) -> None:
    """Una sección bordeada (mismo estilo que `ui_inputs._seccion`) con la
    fila Fijo/Barrido de cada variable del grupo, apiladas verticalmente."""
    with st.container(border=True):
        st.markdown(f"**{nombre}**")
        for campo in campos:
            clave, spec = _fila_barrido(campo, vals.get(campo.clave, campo.default))
            destino[clave] = spec


def _procesar_barrido_en_curso(estado: dict) -> bool:
    """Siguiente lote del barrido activo, con progreso y cancelación.

    Mientras queden puntos, renderiza el botón **Cancelar**, la barra de
    progreso y el resultado parcial, y fuerza un rerun para continuar; al
    terminar o cancelar devuelve ``False`` para que la UI vuelva a pintar el
    esquema con el resultado final (o el parcial conservado).
    """
    if estado.get("aviso"):
        st.warning(estado["aviso"])
    if st.button("Cancelar barrido", key="btn_cancelar_barrido"):
        st.session_state["barrido_cancelado"] = True
        if estado["filas"]:
            st.session_state["resultado_barrido"] = \
                sensitivity.tabla_barrido(estado["filas"])
            st.session_state["backend_barrido"] = estado["nombre_backend"]
        del st.session_state[_BARRILLO_ESTADO]
        return False
    lote = estado["combinaciones"][:_PUNTOS_POR_LOTE]
    for combo in lote:
        estado["filas"].append(
            sensitivity.resolver_combinacion(estado["backend"], combo))
    estado["combinaciones"] = estado["combinaciones"][len(lote):]
    resueltos, total = len(estado["filas"]), estado["total"]
    if not estado["combinaciones"]:
        st.session_state["resultado_barrido"] = \
            sensitivity.tabla_barrido(estado["filas"])
        st.session_state["backend_barrido"] = estado["nombre_backend"]
        st.session_state.pop("barrido_cancelado", None)
        del st.session_state[_BARRILLO_ESTADO]
        return False
    st.progress(resueltos / total)
    st.caption(f"Puntos resueltos: **{resueltos} de {total}** — motor "
               f"{estado['nombre_backend']}.")
    st.dataframe(sensitivity.tabla_barrido(estado["filas"])
                 .tail(_ULTIMOS_PREVIEW), hide_index=True)
    st.rerun()


def renderizar_panel_barrido(vals: dict, backend_sel: str) -> None:
    """Contenido de la pestaña de barrido; guarda el resultado en session_state."""
    st.caption(
        "Declare cada variable como **Fijo** (un solo valor, el de arriba) o "
        "**Barrido** (rejilla `inicio→fin` con paso). Con más de una variable "
        "en Barrido, el resultado es el **producto cartesiano** de todas — "
        "puede crecer rápido; use **TeqpAdapter** en el panel de ejecución "
        "para explorar rangos más grandes."
    )
    if st.session_state.get(_BARRILLO_ESTADO) is not None:
        estado = st.session_state[_BARRILLO_ESTADO]
        if _procesar_barrido_en_curso(estado):
            return
    grupos = ui_helpers.agrupar_campos(ui_helpers.CAMPOS_CICLO)
    variables: dict = {}
    col_izq, col_der = st.columns(2)
    with col_izq:
        for nombre, campos in grupos[:-1]:
            _seccion_barrido(nombre, campos, vals, variables)
    with col_der:
        for nombre, campos in grupos[-1:]:
            _seccion_barrido(nombre, campos, vals, variables)

    n_puntos = 1
    for spec in variables.values():
        n_puntos *= len(sensitivity.generar_valores(spec))
    st.caption(f"Puntos en la rejilla: **{n_puntos}**"
               f" (tope de {_TOPE_PUNTOS} para correr desde la UI).")

    if st.button("Ejecutar barrido", key="btn_ejecutar_barrido"):
        if n_puntos > _TOPE_PUNTOS:
            st.error(
                f"{n_puntos} puntos supera el tope de {_TOPE_PUNTOS} para "
                "correr desde la UI (cada punto resuelve un ciclo completo). "
                "Reduzca el rango o el número de variables en Barrido."
            )
        else:
            x_b = variables["x_b"].valor if isinstance(
                variables["x_b"], sensitivity.Fijo) else vals["x_b"]
            backend, nombre_backend, aviso = ui_backend.construir_backend(
                backend_sel, x_b)
            st.session_state.pop("barrido_cancelado", None)
            st.session_state[_BARRILLO_ESTADO] = {
                "backend": backend,
                "combinaciones": sensitivity.generar_combinaciones(variables),
                "filas": [],
                "total": n_puntos,
                "nombre_backend": nombre_backend,
                "aviso": aviso,
            }
            st.rerun()

    if "resultado_barrido" in st.session_state:
        tabla = st.session_state["resultado_barrido"]
        if st.session_state.pop("barrido_cancelado", None):
            st.warning(f"Barrido **cancelado**: se listan los {len(tabla)} "
                       "puntos ya resueltos.")
        st.markdown(
            f"**Resultado del barrido** ({len(tabla)} puntos, motor "
            f"{st.session_state.get('backend_barrido', '—')})"
        )
        st.dataframe(tabla, hide_index=True)
        st.download_button(
            "⬇ Barrido (.csv)", tabla.to_csv(index=False).encode("utf-8"),
            file_name="kalina_barrido.csv", mime="text/csv")
