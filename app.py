"""UI Streamlit de la app del ciclo Kalina KSC-11 (punto de entrada).

Tarea 2026-09-17-ui-streamlit. Interfaz en español para público poco
familiarizado con software académico: los parámetros se definen en el área
principal (grilla 2×2 con símbolos LaTeX y unidades) y la barra lateral es el
panel de ejecución (motor de propiedades, aviso de tiempo y botón). UNA
simulación por clic (el motor NH3-H2O real tarda ~8-9 min por corrida);
resultados (estados, energías, exergía), descarga de Excel y gráficas, y la
sección de sensibilidad reservada como "próximamente". El cálculo se lanza
SOLO al pulsar el botón y queda guardado en `st.session_state` — Streamlit
re-ejecuta el script en cada interacción. Ejecutar: `streamlit run app.py`.
Los valores por defecto y el esquema de campos viven en `src/ui_helpers.py`;
el renderizado de los inputs y del panel de ejecución en `src/ui_inputs.py`.
"""

from __future__ import annotations

import streamlit as st

from src import ui_backend, ui_barrido, ui_clasificacion, ui_helpers, ui_inputs
from src.cycle_solver import CicloNoConvergeError, resolver_ciclo
from src.exergy import calcular_exergia
from src.export_excel import generar_excel
from src.plots import grafico_balance_energia, grafico_exergia_destruida
from src.properties.adapter import PropertyRangeError
from src.restricciones import evaluar_ciclo


def _limpiar_resultados():
    """Borra resultados de una corrida anterior (falló la actual)."""
    for clave in ui_helpers.CLAVES_RESULTADO:
        if clave in st.session_state:
            del st.session_state[clave]


def _ejecutar(vals, backend_sel):
    """Corre UNA simulación real y guarda el resultado en session_state."""
    backend, nombre_backend, aviso = ui_backend.construir_backend(
        backend_sel, vals["x_b"])
    if aviso:
        st.warning(aviso)
    mensaje_espera = (
        "⏳ Resolviendo el ciclo con TeqpAdapter (NIST teqp)... unas "
        "decenas de segundos."
        if nombre_backend == ui_backend.BACKEND_TEQP else
        "⏳ Resolviendo el ciclo con el motor NH3-H2O riguroso... esto puede "
        "tardar varios minutos. No cierres esta pestaña."
    )
    # Margen de peor caso (2026-09-20-ui-tamb-diseno-visible): desmarcado → el
    # valor efectivo de T_amb_diseno es T_sumidero (criterio O2 sin margen).
    # Vale para el Excel (dict_parametros) y para evaluar_ciclo (más abajo).
    if not vals.get("aplica_margen_o2", True):
        vals["T_amb_diseno"] = vals["T_sumidero"]
    parametros = ui_helpers.dict_parametros(vals)
    try:
        with st.spinner(mensaje_espera):
            resultado = resolver_ciclo(
                backend, P_alta=vals["P_alta"], P_baja=vals["P_baja"],
                T_fuente=vals["T_fuente"], T_sumidero=vals["T_sumidero"],
                x_b=vals["x_b"], m_b=vals["m_b"], eta_t=vals["eta_t"],
                eta_p=vals["eta_p"], eps_hrvg=vals["eps_hrvg"],
                eps_reg=vals["eps_reg"], eps_cond=vals["eps_cond"])
            exergia = calcular_exergia(resultado, backend,
                                       T_fuente=vals["T_fuente"],
                                       T_sumidero=vals["T_sumidero"],
                                       T0=vals["T0"], P0=vals["P0"])
            validacion = evaluar_ciclo(
                backend, resultado, P_alta=vals["P_alta"], P_baja=vals["P_baja"],
                T_fuente=vals["T_fuente"], T_sumidero=vals["T_sumidero"],
                x_b=vals["x_b"], m_b=vals["m_b"], eps_hrvg=vals["eps_hrvg"],
                eps_reg=vals["eps_reg"], eps_cond=vals["eps_cond"],
                T_amb_diseno=vals["T_amb_diseno"])
    except CicloNoConvergeError as exc:
        _limpiar_resultados()
        st.warning(
            "⚠️ El ciclo **no convergió** con estos parámetros: "
            f"{exc}. Pruebe con otros valores, por ejemplo T_fuente más alta "
            "u otras efectividades."
        )
        return
    except PropertyRangeError as exc:
        _limpiar_resultados()
        st.warning(
            "⚠️ Algún estado quedó **fuera del rango válido** del motor de "
            f"propiedades: {exc}. Revise presiones, temperaturas y composición."
        )
        return
    st.session_state["resultado_ciclo"] = resultado
    st.session_state["resultado_exergia"] = exergia
    st.session_state["resultado_validacion"] = validacion
    st.session_state["parametros"] = parametros
    st.session_state["backend_nombre"] = nombre_backend
    st.success("✅ Simulación completada. Resultados abajo.")


def _mostrar_clasificacion():
    """Caja con la etiqueta de clasificación termodinámica del punto
    (`restricciones.evaluar_ciclo`: KALINA/VALIDO_ADVERTENCIA/CORREGIBLE/
    DEGENERADO/INVIABLE) y el detalle de qué criterios la produjeron."""
    validacion = st.session_state.get("resultado_validacion")
    if validacion is None:
        return
    etiqueta, tipo = ui_clasificacion.CLASIFICACION_INFO.get(
        validacion.clasificacion.value, (validacion.clasificacion.value, "info"))
    with st.container(border=True):
        st.markdown("**Clasificación del ciclo**")
        getattr(st, tipo)(f"**{etiqueta}**")
        st.caption(validacion.mensaje_reporte().replace("\n", "  \n"))


def _mostrar_resultados():
    """Renderiza clasificación, métricas, estados, gráficas, advertencias y
    descargas."""
    r = st.session_state["resultado_ciclo"]
    x = st.session_state["resultado_exergia"]
    eta_ex = r["Wnet"] / x["ex_qi"] if x["ex_qi"] else float("nan")

    _mostrar_clasificacion()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("η energético", f"{r['eta']:.1%}", border=True)
    c2.metric("η exergético (Wnet/Ex_Qi)", f"{eta_ex:.1%}", border=True)
    c3.metric("Wnet [kW]", f"{r['Wnet']:.2f}", border=True)
    c4.metric("Qi [kW]", f"{r['Qi']:.2f}", border=True)
    c5.metric("Qout [kW]", f"{r['Qout']:.2f}", border=True)

    st.markdown("**Estados del ciclo (T, P, h, s, x, m, q, fase, exergía física)**")
    st.dataframe(ui_helpers.tabla_estados(r, x), hide_index=True)

    cA, cB = st.columns(2)
    fig_bal = grafico_balance_energia(r)
    fig_exg = grafico_exergia_destruida(x)
    with cA:
        st.pyplot(fig_bal)
        st.download_button("⬇ Balance de energía (PNG)",
                           ui_helpers.fig_png(fig_bal),
                           file_name="balance_energia.png", mime="image/png")
    with cB:
        st.pyplot(fig_exg)
        st.download_button("⬇ Exergía destruida (PNG)",
                           ui_helpers.fig_png(fig_exg),
                           file_name="exergia_destruida.png", mime="image/png")

    st.markdown("**Entropía generada y exergía destruida por componente**")
    st.dataframe(ui_helpers.tabla_sgen_ed(x), hide_index=True)

    st.markdown("**Panel de advertencias**")
    avisos = ui_helpers.advertencias_segunda_ley(x)
    if avisos:
        for aviso in avisos:
            st.warning(aviso)
    else:
        st.success("Sin advertencias de segunda ley en los resultados.")

    st.markdown("**Descargas**")
    st.download_button(
        "⬇ Excel con todos los resultados (.xlsx)",
        generar_excel(r, x, st.session_state["parametros"],
                      st.session_state["backend_nombre"]),
        file_name="kalina_ksc11_resultados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


def main() -> None:
    st.set_page_config(page_title="Ciclo Kalina KSC-11", page_icon="♻️",
                       layout="wide")
    st.title("Ciclo Kalina KSC-11")
    st.markdown(
        "Análisis **energético y exergético** (exergía física, sin química) de un "
        "ciclo Kalina KSC-11 con mezcla NH₃-H₂O: el calor de la fuente se convierte "
        "en potencia neta en la turbina y el resto se rechaza al sumidero. UNA "
        "simulación por clic — configure los parámetros arriba y ejecútela desde "
        "la barra lateral."
    )

    with st.sidebar:
        backend_sel, ejecutar = ui_inputs.renderizar_panel_ejecucion()

    tab_puntual, tab_barrido = st.tabs(
        ["Análisis puntual", "Sensibilidad paramétrica"])

    with tab_puntual:
        vals = ui_inputs.renderizar_inputs()

        if ejecutar:
            _ejecutar(vals, backend_sel)

        if "resultado_ciclo" in st.session_state:
            _mostrar_resultados()
        else:
            st.info("Configure los parámetros y pulse **Ejecutar simulación** "
                    "para ver aquí los resultados, las gráficas y las descargas.")

    with tab_barrido:
        ui_barrido.renderizar_panel_barrido(vals, backend_sel)


if __name__ == "__main__":
    main()