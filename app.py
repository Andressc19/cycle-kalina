"""UI Streamlit de la app del ciclo Kalina KSC-11 (punto de entrada).

Interfaz en español para público poco familiarizado con software académico:
los parámetros se definen en el área principal (grilla 2×2 con símbolos LaTeX
y unidades) y la barra lateral es el panel de ejecución (motor de propiedades,
aviso de tiempo y botón). UNA simulación por clic (el motor NH3-H2O real tarda
~8-9 min por corrida) que corre en un hilo de fondo con tiempo transcurrido,
estimado, log de iteraciones del solver y botón Cancelar (ver
`src/ui_ejecucion.py`). Los resultados (estados, energías, exergía, diagrama
T-s interactivo, descargas Excel/PNG y explorador PyGWalker) viven en
`src/ui_resultados.py`; el barrido, en `src/ui_barrido.py`. Ejecutar:
`streamlit run app.py`.
"""

from __future__ import annotations

import streamlit as st

from src import (ui_barrido, ui_ejecucion, ui_estilo, ui_inputs,
                 ui_resultados)


def main() -> None:
    st.set_page_config(page_title="Ciclo Kalina KSC-11", page_icon="♻️",
                       layout="wide")
    ui_estilo.aplicar_estilo()
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

        if ejecutar and not ui_ejecucion.hay_ejecucion():
            ui_ejecucion.iniciar(backend_sel, vals)

        if not ui_ejecucion.renderizar_ejecucion():
            if "resultado_ciclo" in st.session_state:
                ui_resultados.mostrar_resultados()
            else:
                st.info("Configure los parámetros y pulse **Ejecutar simulación** "
                        "para ver aquí los resultados, las gráficas y las descargas.")

    with tab_barrido:
        ui_barrido.renderizar_panel_barrido(vals, backend_sel)


if __name__ == "__main__":
    main()
