"""Renderizado de los resultados del análisis puntual (extraído de `app.py`).

Estructura visual (rediseño): clasificación + fila de métricas como tarjetas +
panel de advertencias arriba (siempre visible), y debajo tres pestañas
internas — Estados, Gráficos y Descargas — para no obligar a scrollear una
columna larguísima. El diagrama T-s es interactivo (Altair) y la tabla de
estados se puede explorar con PyGWalker.
"""

from __future__ import annotations

import streamlit as st

from src import ui_clasificacion, ui_estilo, ui_explorador, ui_graficos, ui_helpers
from src.export_excel import generar_excel
from src.plots import grafico_balance_energia, grafico_exergia_destruida

__all__ = ["mostrar_resultados"]


def _mostrar_clasificacion() -> None:
    """Caja con la etiqueta de clasificación termodinámica del punto
    (`restricciones.evaluar_ciclo`: KALINA/VALIDO_ADVERTENCIA/CORREGIBLE/
    DEGENERADO/INVIABLE) y el detalle de qué criterios la produjeron."""
    validacion = st.session_state.get("resultado_validacion")
    if validacion is None:
        return
    etiqueta, tipo = ui_clasificacion.CLASIFICACION_INFO.get(
        validacion.clasificacion.value, (validacion.clasificacion.value, "info"))
    with st.container(border=True):
        ui_estilo.encabezado("🧪", "Clasificación del ciclo")
        getattr(st, tipo)(f"**{etiqueta}**")
        st.caption(validacion.mensaje_reporte().replace("\n", "  \n"))


def _mostrar_advertencias(resultado_exergia) -> None:
    """Panel de segunda ley: avisos por Sgen < 0 o mensaje de que no hay."""
    avisos = ui_helpers.advertencias_segunda_ley(resultado_exergia)
    if avisos:
        ui_estilo.encabezado("⚠️", "Advertencias de segunda ley")
        for aviso in avisos:
            st.warning(aviso)


def mostrar_resultados() -> None:
    """Clasificación, métricas y pestañas de estados, gráficos y descargas."""
    r = st.session_state["resultado_ciclo"]
    x = st.session_state["resultado_exergia"]
    eta_ex = r["Wnet"] / x["ex_qi"] if x["ex_qi"] else float("nan")

    _mostrar_clasificacion()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("η energético", f"{r['eta']:.1%}")
    c2.metric("η exergético", f"{eta_ex:.1%}")
    c3.metric("Wnet [kW]", f"{r['Wnet']:.2f}")
    c4.metric("Qi [kW]", f"{r['Qi']:.2f}")
    c5.metric("Qout [kW]", f"{r['Qout']:.2f}")

    _mostrar_advertencias(x)

    tab_estados, tab_graficos, tab_descargas = st.tabs(
        ["📋 Estados", "📈 Gráficos", "⬇ Descargas"])

    with tab_estados:
        ui_estilo.encabezado("📋", "Estados del ciclo")
        st.caption("T, P, h, s, x, m, q, fase y exergía física de los 10 estados.")
        tabla = ui_helpers.tabla_estados(r, x)
        st.dataframe(tabla, hide_index=True)
        ui_estilo.encabezado("🔥", "Entropía generada y exergía destruida")
        st.dataframe(ui_helpers.tabla_sgen_ed(x), hide_index=True)
        with st.expander("🔎 Explorar los estados (PyGWalker)"):
            ui_explorador.explorar(tabla, gid="estados_puntual")

    with tab_graficos:
        ui_estilo.encabezado("📈", "Diagrama T-s del ciclo")
        st.altair_chart(ui_graficos.grafico_ts(r, x), use_container_width=True)
        cA, cB = st.columns(2)
        with cA:
            st.pyplot(grafico_balance_energia(r))
        with cB:
            st.pyplot(grafico_exergia_destruida(x))

    with tab_descargas:
        ui_estilo.encabezado("⬇", "Descargas")
        st.download_button(
            "⬇ Excel con todos los resultados (.xlsx)",
            generar_excel(r, x, st.session_state["parametros"],
                          st.session_state["backend_nombre"]),
            file_name="kalina_ksc11_resultados.xlsx",
            mime=("application/vnd.openxmlformats-officedocument"
                  ".spreadsheetml.sheet"))
        cA, cB = st.columns(2)
        fig_bal = grafico_balance_energia(r)
        fig_exg = grafico_exergia_destruida(x)
        with cA:
            st.download_button("⬇ Balance de energía (PNG)",
                               ui_helpers.fig_png(fig_bal),
                               file_name="balance_energia.png", mime="image/png")
        with cB:
            st.download_button("⬇ Exergía destruida (PNG)",
                               ui_helpers.fig_png(fig_exg),
                               file_name="exergia_destruida.png", mime="image/png")
