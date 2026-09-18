"""Helpers de presentación para la UI Streamlit del ciclo Kalina KSC-11.

Tarea 2026-09-17-ui-streamlit. Construye los DataFrames que muestra
`app.py` (tabla de los 10 estados y tabla de Sgen/Ed por componente), el
snapshot de parámetros de entrada para el Excel y los bytes PNG de una
figura. Solo pandas y las estructuras que devuelven
`resolver_ciclo`/`calcular_exergia`: no toca Streamlit ni el solver. Los
campos m, q, fase y exergia_fisica pueden quedar en None (ver
`src/state.py`) y se muestran como "—".
"""

from __future__ import annotations

from io import BytesIO

import pandas as pd

__all__ = ["ORDEN_COMPONENTES", "NOMBRES_COMPONENTES", "tabla_estados",
           "tabla_sgen_ed", "advertencias_segunda_ley", "dict_parametros",
           "fig_png", "CAMPOS_CICLO", "CAMPOS_ESTADO", "BACKENDS",
           "BACKEND_REAL", "CLAVES_RESULTADO"]

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


def advertencias_segunda_ley(resultado_exergia) -> list:
    """Mensajes en español para cada componente con Sgen < 0 (violaría la 2ª ley)."""
    sgen = resultado_exergia["sgen"]
    mensajes = []
    for comp in ORDEN_COMPONENTES:
        if sgen[comp] < 0:
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

# Valores por defecto de CONTEXT.md ("Valores por defecto sugeridos para la
# UI", con T_fuente ya actualizado a 470.0 K). Cada campo:
# (clave, etiqueta, unidad, ayuda, por defecto, mínimo, máximo, paso, formato).
# T0 = 300.032917 K (estado muerto, media del perfil horario ambiente);
# P0 = 101.325 kPa (supuesto atmosférico de CONTEXT.md).
CAMPOS_CICLO = (
    ("P_alta", "Presión alta", "kPa",
     "Presión de alta del ciclo (descarga de la bomba, entrada al HRVG).",
     3000.0, 500.0, 20000.0, 50.0, "%.1f"),
    ("P_baja", "Presión baja", "kPa",
     "Presión de baja del ciclo (descarga de la turbina y condensador).",
     400.0, 50.0, 5000.0, 50.0, "%.1f"),
    ("x_b", "Composición global de NH3", "-",
     "Fracción másica de amoníaco de la mezcla NH3-H2O que circula; define el "
     "equilibrio del separador (0 < x < 1).", 0.50, 0.05, 0.95, 0.01, "%.2f"),
    ("T_fuente", "Temperatura de la fuente", "K",
     "Temperatura del reservorio que entrega calor al HRVG.",
     470.0, 350.0, 800.0, 10.0, "%.1f"),
    ("T_sumidero", "Temperatura del sumidero", "K",
     "Temperatura del agua de enfriamiento que recibe el calor rechazado.",
     300.032917, 250.0, 600.0, 1.0, "%.3f"),
    ("m_b", "Flujo másico de trabajo", "kg/s",
     "Base de cálculo del ciclo: caudal de mezcla circulante.",
     1.0, 0.01, 100.0, 0.1, "%.2f"),
    ("eta_t", "Eficiencia isentrópica de la turbina", "-",
     "Relación entre el trabajo real y el isentrópico de la turbina.",
     0.85, 0.05, 0.99, 0.01, "%.2f"),
    ("eta_p", "Eficiencia isentrópica de la bomba", "-",
     "Relación entre el trabajo isentrópico y el real de la bomba.",
     0.75, 0.05, 0.99, 0.01, "%.2f"),
    ("eps_hrvg", "Efectividad del HRVG", "-",
     "ε_HRVG = (h2 − h1)/(h2,máx − h1): qué tan cerca del máximo opera el HRVG.",
     0.85, 0.05, 0.99, 0.01, "%.2f"),
    ("eps_reg", "Efectividad del regenerador", "-",
     "ε_reg = (h5 − h6)/(h5 − h6,mín): recuperación interna de calor.",
     0.75, 0.05, 0.99, 0.01, "%.2f"),
    ("eps_cond", "Efectividad del condensador", "-",
     "ε_cond = (h8 − h9)/(h8 − h9,mín) frente al sumidero.",
     0.80, 0.05, 0.99, 0.01, "%.2f"),
)
CAMPOS_ESTADO = (
    ("T0", "Temperatura ambiente (estado muerto)", "K",
     "T0 = 300.032917 K: media del perfil horario ambiente (CONTEXT.md).",
     300.032917, 250.0, 400.0, 0.001, "%.6f"),
    ("P0", "Presión ambiente (estado muerto)", "kPa",
     "P0 = 101.325 kPa (atmosférica estándar; supuesto de CONTEXT.md).",
     101.325, 50.0, 500.0, 0.1, "%.3f"),
)
BACKENDS = (
    "AmmoniaWaterAdapter — mezcla NH3-H2O (recomendado)",
    "IAPWSAdapter (agua pura) — no aplica a la mezcla NH3-H2O en este entorno",
    "PyfluidsAdapter (CoolProp) — no soporta el par NH3-H2O en este entorno",
)
BACKEND_REAL = "AmmoniaWaterAdapter"
CLAVES_RESULTADO = ("resultado_ciclo", "resultado_exergia", "parametros",
                    "backend_nombre")