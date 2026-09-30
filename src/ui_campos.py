"""Esquema de campos de la UI del ciclo Kalina KSC-11.

Extraído de `ui_helpers` en la tarea 2026-09-20-t-amb-diseno-configurable por
el límite de 200 líneas por archivo. La namedtuple `Campo` reúne la etiqueta
corta en español, el símbolo LaTeX con su unidad (solo pantalla;
`st.number_input` no renderiza `$...$` en labels), el tooltip y los límites de
CONTEXT.md. `agrupar_campos` separa un esquema en secciones por `campo.grupo`
respetando el orden de definición: lo usan `ui_inputs` y `ui_barrido` para que
ambas pestañas agrupen las mismas variables de la misma forma.

Grupos: `CAMPOS_CICLO` (las 11 variables del ciclo), `CAMPOS_ESTADO` (T0/P0 del
estado muerto de exergía) y `CAMPOS_DISENO` (piso de T_ambiente del criterio
O2, semánticamente un criterio de diseño, no un estado del ciclo). `ui_helpers`
re-exporta el esquema completo para no romper sus consumidores existentes.
"""

from __future__ import annotations

from collections import namedtuple

__all__ = ["Campo", "CAMPOS_CICLO", "CAMPOS_ESTADO", "CAMPOS_DISENO",
           "agrupar_campos"]

# Un campo de entrada: clave, etiqueta corta (plana, sin LaTeX), símbolo LaTeX
# con unidad (se muestra con st.markdown sobre el widget; los labels de
# st.number_input NO renderizan $...$), tooltip (estos sí admiten $...$),
# default/mínimo/máximo/paso/formato de CONTEXT.md y grupo de la barra lateral.
Campo = namedtuple("Campo", (
    "clave", "etiqueta", "simbolo", "ayuda",
    "default", "vmin", "vmax", "paso", "formato", "grupo",
))

CAMPOS_CICLO = (
    Campo("T_fuente", "Temperatura de la fuente", r"$T_{\mathrm{fuente}}\ [\mathrm{K}]$",
          "Temperatura del reservorio que entrega calor al HRVG.",
          470.0, 350.0, 800.0, 10.0, "%.1f", "Condiciones de borde"),
    Campo("T_sumidero", "Temperatura del sumidero", r"$T_{\mathrm{sumidero}}\ [\mathrm{K}]$",
          "Temperatura del agua de enfriamiento que recibe el calor rechazado.",
          300.032917, 250.0, 600.0, 1.0, "%.3f", "Condiciones de borde"),
    Campo("P_alta", "Presión alta", r"$P_{\mathrm{alta}}\ [\mathrm{kPa}]$",
          "Presión de alta del ciclo (descarga de la bomba, entrada al HRVG).",
          3000.0, 500.0, 20000.0, 50.0, "%.1f", "Presiones del ciclo"),
    Campo("P_baja", "Presión baja", r"$P_{\mathrm{baja}}\ [\mathrm{kPa}]$",
          "Presión de baja del ciclo (descarga de la turbina y condensador).",
          400.0, 50.0, 5000.0, 50.0, "%.1f", "Presiones del ciclo"),
    Campo("x_b", "Composición global de NH3", r"$x_{\mathrm{NH_3}}$",
          "Fracción másica de amoníaco de la mezcla NH3-H2O que circula; define "
          "el equilibrio del separador ($0 < x < 1$).",
          0.50, 0.05, 0.95, 0.01, "%.2f", "Composición y flujo"),
    Campo("m_b", "Flujo másico de trabajo", r"$\dot{m}_{b}\ [\mathrm{kg/s}]$",
          "Base de cálculo del ciclo: caudal de mezcla circulante.",
          1.0, 0.01, 100.0, 0.1, "%.2f", "Composición y flujo"),
    Campo("eta_t", "Eficiencia isentrópica de la turbina", r"$\eta_{t}$",
          "Relación entre el trabajo real y el isentrópico de la turbina.",
          0.85, 0.05, 0.99, 0.01, "%.2f", "Rendimiento de equipos"),
    Campo("eta_p", "Eficiencia isentrópica de la bomba", r"$\eta_{p}$",
          "Relación entre el trabajo isentrópico y el real de la bomba.",
          0.75, 0.05, 0.99, 0.01, "%.2f", "Rendimiento de equipos"),
    Campo("eps_hrvg", "Efectividad del HRVG", r"$\varepsilon_{\mathrm{HRVG}}$",
          r"Efectividad del HRVG: $\varepsilon_{\mathrm{HRVG}} = (h_2 - h_1)/"
          r"(h_{2,\mathrm{max}} - h_1)$ — qué tan cerca del máximo opera.",
          0.85, 0.05, 0.99, 0.01, "%.2f", "Rendimiento de equipos"),
    Campo("eps_reg", "Efectividad del regenerador", r"$\varepsilon_{\mathrm{reg}}$",
          r"Efectividad del regenerador: $\varepsilon_{\mathrm{reg}} = (h_5 - h_6)/"
          r"(h_5 - h_{6,\mathrm{min}})$ — recuperación interna de calor.",
          0.75, 0.05, 0.99, 0.01, "%.2f", "Rendimiento de equipos"),
    Campo("eps_cond", "Efectividad del condensador", r"$\varepsilon_{\mathrm{cond}}$",
          r"Efectividad del condensador: $\varepsilon_{\mathrm{cond}} = (h_8 - h_9)/"
          r"(h_8 - h_{9,\mathrm{min}})$ — rechazo de calor al sumidero.",
          0.80, 0.05, 0.99, 0.01, "%.2f", "Rendimiento de equipos"),
)
CAMPOS_ESTADO = (
    Campo("T0", "Temperatura ambiente (estado muerto)", r"$T_{0}\ [\mathrm{K}]$",
          "Media del perfil horario de temperatura ambiente (CONTEXT.md): "
          r"$T_0 = 300.032917\ \mathrm{K}$.",
          300.032917, 250.0, 400.0, 0.001, "%.6f", "Estado muerto (exergía)"),
    Campo("P0", "Presión ambiente (estado muerto)", r"$P_{0}\ [\mathrm{kPa}]$",
          "Presión atmosférica estándar (supuesto de CONTEXT.md): "
          r"$P_0 = 101.325\ \mathrm{kPa}$.",
          101.325, 50.0, 500.0, 0.1, "%.3f", "Estado muerto (exergía)"),
)
CAMPOS_DISENO = (
    Campo("T_amb_diseno", "Piso de T ambiente (criterio O2)",
          r"$T_{\mathrm{amb,diseno}}\ [\mathrm{K}]$",
          "Piso de diseño del criterio O2 (cavitación): el condensador se "
          "evalúa siempre contra al menos esta T ambiente, aunque T_sumidero "
          "sea menor. Comparte el perfil horario de T_ambiente con T0 (estado "
          "muerto) pero son variables independientes: T0 = 300.032917 K es el "
          "PROMEDIO, referencia contable de exergía que NO afecta la "
          "clasificación; T_amb_diseno = 303.55 K es el MÁXIMO/peor caso y SÍ "
          "decide si el punto clasifica KALINA (criterio O2). No las fusione. "
          "Subirlo es un criterio de diseño más conservador; bajarlo, uno "
          "más permisivo.",
          303.55, 250.0, 400.0, 0.001, "%.3f", "Criterio de diseño (cavitación)"),
)


def agrupar_campos(campos: tuple) -> list:
    """Separa un esquema de `Campo` en secciones (`campo.grupo`), respetando
    el orden de definición. Usado por `ui_inputs` y `ui_barrido` para que
    ambas pestañas agrupen las mismas 11 variables de la misma forma."""
    grupos = []
    for campo in campos:
        if grupos and grupos[-1][0] == campo.grupo:
            grupos[-1][1].append(campo)
        else:
            grupos.append([campo.grupo, [campo]])
    return grupos