"""Helpers de presentación para la UI Streamlit del ciclo Kalina KSC-11.

Construye los DataFrames que muestra `app.py` (tabla de los 10 estados y
tabla de Sgen/Ed por componente), el snapshot de parámetros de entrada para
el Excel y los bytes PNG de una figura. También vive aquí el esquema de
campos de la UI: la namedtuple `Campo` reúne la etiqueta corta en español,
el símbolo LaTeX con su unidad (solo pantalla; `st.number_input` no
renderiza `$...$` en labels), el tooltip y los límites de CONTEXT.md.
`dict_parametros` conserva etiquetas planas, sin LaTeX, para el Excel.
"""

from __future__ import annotations

from collections import namedtuple
from io import BytesIO

import pandas as pd

__all__ = ["ORDEN_COMPONENTES", "NOMBRES_COMPONENTES", "Campo",
           "tabla_estados", "tabla_sgen_ed", "advertencias_segunda_ley",
           "dict_parametros", "fig_png", "CAMPOS_CICLO", "CAMPOS_ESTADO",
           "CLAVES_RESULTADO", "agrupar_campos"]

ORDEN_COMPONENTES = ("hrvg", "separador", "turbina", "regenerador",
                     "valvula", "absorbedor", "condensador", "bomba")

NOMBRES_COMPONENTES = {"hrvg": "HRVG", "separador": "Separador",
                       "turbina": "Turbina", "regenerador": "Regenerador",
                       "valvula": "Válvula", "absorbedor": "Absorbedor",
                       "condensador": "Condensador", "bomba": "Bomba"}


def _num(valor, cifras):
    """``valor`` redondeado o "—" si es None (m, q y exergía pueden faltar)."""
    return "—" if valor is None else round(valor, cifras)


def tabla_estados(resultado_ciclo, resultado_exergia) -> pd.DataFrame:
    """DataFrame de los 10 estados: T, P, h, s, x, m, q, fase y exergía física.

    Prefiere los estados de ``resultado_exergia`` (copias con
    ``exergia_fisica`` ya rellenada) y cae a los del ciclo si faltaran.
    """
    estados = resultado_exergia.get("estados", resultado_ciclo["estados"])
    filas = []
    for clave in sorted(estados, key=lambda k: int(k[1:])):
        e = estados[clave]
        filas.append({
            "Estado": e.etiqueta or clave,
            "T [K]": round(e.T, 2),
            "P [kPa]": round(e.P, 2),
            "h [kJ/kg]": round(e.h, 2),
            "s [kJ/kg·K]": round(e.s, 4),
            "x (NH3) [-]": round(e.x, 4),
            "m [kg/s]": _num(e.m, 4),
            "q [-]": _num(e.q, 4),
            "Fase": e.fase or "—",
            "ex_física [kJ/kg]": _num(e.exergia_fisica, 3),
        })
    return pd.DataFrame(filas)


def tabla_sgen_ed(resultado_exergia) -> pd.DataFrame:
    """DataFrame de Sgen [kW/K] y Ed [kW] por componente, más el total."""
    sgen, ed = resultado_exergia["sgen"], resultado_exergia["ed"]
    filas = [
        {"Componente": NOMBRES_COMPONENTES[c],
         "Sgen [kW/K]": round(sgen[c], 5),
         "Ed [kW]": round(ed[c], 3)}
        for c in ORDEN_COMPONENTES
    ]
    filas.append({
        "Componente": "Total",
        "Sgen [kW/K]": round(sum(sgen[c] for c in ORDEN_COMPONENTES), 5),
        "Ed [kW]": round(resultado_exergia["ed_total"], 3),
    })
    return pd.DataFrame(filas)


# Sgen [kW/K] bajo este límite es ruido numérico del solver, no violación
# real (-1e-6 es ~100-10000x más chico que un Sgen real, ~0.01-1 kW/K).
_TOL_SGEN = 1e-4


def advertencias_segunda_ley(resultado_exergia) -> list:
    """Mensajes por componente con Sgen claramente < 0 (más allá de
    `_TOL_SGEN`; la tabla de Sgen/Ed sigue mostrando el valor exacto)."""
    sgen = resultado_exergia["sgen"]
    mensajes = []
    for comp in ORDEN_COMPONENTES:
        if sgen[comp] < -_TOL_SGEN:
            mensajes.append(
                f"{NOMBRES_COMPONENTES[comp]} reporta Sgen = {sgen[comp]:.5f} "
                "kW/K < 0, lo que violaría la segunda ley en el modelo. Revise "
                "los datos de entrada (temperaturas, efectividades, composición) "
                "o el modelo de ese componente."
            )
    return mensajes


def dict_parametros(valores: dict) -> dict:
    """Snapshot {nombre: (valor, unidad)} de las entradas, para el Excel."""
    return {
        "P_alta (presión alta)": (round(valores["P_alta"], 3), "kPa"),
        "P_baja (presión baja)": (round(valores["P_baja"], 3), "kPa"),
        "x_NH3 (x_b, composición global)": (round(valores["x_b"], 4), "-"),
        "T_fuente": (round(valores["T_fuente"], 3), "K"),
        "T_sumidero (agua de enfriamiento)": (round(valores["T_sumidero"], 3), "K"),
        "m_b (base de cálculo)": (round(valores["m_b"], 4), "kg/s"),
        "eta_turbina (isentrópica)": (round(valores["eta_t"], 4), "-"),
        "eta_bomba (isentrópica)": (round(valores["eta_p"], 4), "-"),
        "eps_hrvg": (round(valores["eps_hrvg"], 4), "-"),
        "eps_reg (regenerador)": (round(valores["eps_reg"], 4), "-"),
        "eps_cond (condensador)": (round(valores["eps_cond"], 4), "-"),
        "T0 (estado muerto)": (round(valores["T0"], 6), "K"),
        "P0 (estado muerto)": (round(valores["P0"], 4), "kPa"),
    }


def fig_png(fig) -> bytes:
    """Figura matplotlib → bytes PNG (para ``st.download_button``)."""
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    return buf.getvalue()


# -- Esquema de la UI (datos de presentación, sin Streamlit) -----------------

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
CLAVES_RESULTADO = ("resultado_ciclo", "resultado_exergia",
                    "resultado_validacion", "parametros", "backend_nombre")


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