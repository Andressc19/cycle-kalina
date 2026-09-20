"""Helpers de presentación para la UI Streamlit del ciclo Kalina KSC-11.

Construye los DataFrames que muestra `app.py` (tabla de los 10 estados y
tabla de Sgen/Ed por componente), el snapshot de parámetros de entrada para
el Excel y los bytes PNG de una figura. El esquema de campos (namedtuple
`Campo`, `CAMPOS_CICLO`, `CAMPOS_ESTADO`, `CAMPOS_DISENO`, `agrupar_campos`)
vive en `src/ui_campos.py` (extraído aquí por el límite de 200 líneas) y se
re-exporta para no romper a `ui_inputs`, `ui_barrido` y los scripts.
`dict_parametros` conserva etiquetas planas, sin LaTeX, para el Excel.
"""

from __future__ import annotations

from io import BytesIO

import pandas as pd

from .ui_campos import (CAMPOS_CICLO, CAMPOS_DISENO, CAMPOS_ESTADO,
                        Campo, agrupar_campos)

__all__ = ["ORDEN_COMPONENTES", "NOMBRES_COMPONENTES", "Campo",
           "tabla_estados", "tabla_sgen_ed", "advertencias_segunda_ley",
           "dict_parametros", "fig_png", "CAMPOS_CICLO", "CAMPOS_ESTADO",
           "CAMPOS_DISENO", "CLAVES_RESULTADO", "agrupar_campos"]

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
        "T_amb_diseno (piso criterio O2)": (round(valores["T_amb_diseno"], 3), "K"),
    }


def fig_png(fig) -> bytes:
    """Figura matplotlib → bytes PNG (para ``st.download_button``)."""
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    return buf.getvalue()


CLAVES_RESULTADO = ("resultado_ciclo", "resultado_exergia",
                    "resultado_validacion", "parametros", "backend_nombre")