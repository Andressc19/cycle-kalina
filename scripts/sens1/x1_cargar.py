# -*- coding: utf-8 -*-
"""Sensibilidad 1 - x1: carga y normaliza los 12 conjuntos en un solo DataFrame.

Todos los numeros del libro salen de aqui (los CSV de `resultados/`); no se copia ninguna
cifra de los resumenes .md. Cada fila lleva su estudio, su centro, la variable o el par que
se movio, y las columnas derivadas: KALINA dentro del rango experimental, KALINA fuera del
rango experimental, eta en %, Qreg/Qi y P_alta/P_baja.
"""
import os

import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RES = os.path.join(RAIZ, "resultados")
SALIDA = os.path.join(RAIZ, "datos", "Kalina_anal_sensible_1.xlsx")

CENTRO_TXT = {"C1": "C1 Husavik", "C2": "C2 ancla A*", "C3": "C3 caliente 150 C",
              "C4": "C4 frio 110 C", "NA": "sin centro (muestreo)"}

# Valores de los 4 centros (los mismos que fijaron las tareas de barrido; eta_t/eta_p y las
# efectividades son iguales en C1/C3/C4, y C2 cambia eta_p). Se usan solo para rellenar el
# `valor` de la fila "base" de un barrido univariado (el CSV la deja vacia).
CENTROS = {
    "C1 Husavik": {"T_fuente": 394.15, "T_sumidero": 278.15, "P_alta": 3300.0, "P_baja": 690.0,
                   "x_b": 0.82, "eta_t": 0.85, "eta_p": 0.80, "eps_hrvg": 0.85, "eps_reg": 0.75,
                   "eps_cond": 0.95},
    "C2 ancla A*": {"T_fuente": 403.0, "T_sumidero": 300.15, "P_alta": 3000.0, "P_baja": 563.64,
                    "x_b": 0.50, "eta_t": 0.85, "eta_p": 0.75, "eps_hrvg": 0.85, "eps_reg": 0.75,
                    "eps_cond": 0.95},
    "C3 caliente 150 C": {"T_fuente": 423.15, "T_sumidero": 280.5, "P_alta": 3150.0,
                          "P_baja": 950.0, "x_b": 0.75, "eta_t": 0.85, "eta_p": 0.80,
                          "eps_hrvg": 0.85, "eps_reg": 0.75, "eps_cond": 0.95},
    "C4 frio 110 C": {"T_fuente": 383.15, "T_sumidero": 282.5, "P_alta": 3880.0, "P_baja": 910.0,
                      "x_b": 0.88, "eta_t": 0.85, "eta_p": 0.80, "eps_hrvg": 0.85,
                      "eps_reg": 0.75, "eps_cond": 0.95},
}

# Texto de presentacion de cada variable barrida (con su unidad).
VAR_TXT = {"T_fuente": "T_fuente (K)", "T_sumidero": "T_sumidero (K)", "P_alta": "P_alta (kPa)",
           "P_baja": "P_baja (kPa)", "x_b": "x_b (-)", "eta_t": "η_t (-)", "eta_p": "η_p (-)",
           "eps_hrvg": "ε_HRVG (-)", "eps_reg": "ε_reg (-)", "eps_cond": "ε_cond (-)"}
VARIABLES_ORDEN = ["T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "eta_t", "eta_p",
                   "eps_hrvg", "eps_reg", "eps_cond"]

PARS = {"B1": "B1 (T_fuente x P_baja)", "B2": "B2 (P_baja x x_b)",
        "B3": "B3 (P_alta x P_baja)", "B4": "B4 (eps_cond x T_sumidero)",
        "B5": "B5 (eps_reg x eta_t)", "B6": "B6 (eps_HRVG x T_fuente)"}

# Las 5 eficiencias/efectividades que deben quedar en [0.40, 0.95] para un KALINA dentro del
# rango experimental.
EFIC = ["eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond"]

# Variables comunes a todos los conjuntos (se copian tal cual del CSV).
COMUNES = ["T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "eta_t", "eta_p",
           "eps_hrvg", "eps_reg", "eps_cond", "m_b", "T_amb_diseno", "eta", "Wnet", "Qi",
           "Qout", "Wt", "Wp", "Qreg", "dh_turb", "m_O1", "m_O2", "m_O3", "m_O5", "t_s"]


def _ruta(*partes):
    return os.path.join(RES, *partes)


ESTUDIOS = [
    {"n": 0, "nombre": "Referencia de Husavik", "hoja": "E0 Referencia Husavik",
     "datos": "E0 Datos Referencia", "grupo": "", "barrido": None, "centro": "C1",
     "archivo": _ruta("2026-10-14_sens1_fase0", "fase0_filas.csv")},
    {"n": 1, "nombre": "Una variable", "hoja": "E1 Una variable",
     "datos": "E1 Datos Una variable", "grupo": "C1 y C2", "barrido": None, "centro": "",
     "archivo": _ruta("2026-10-14_sens1_faseA", "faseA_filas.csv")},
    {"n": 2, "nombre": "Pares de variables", "hoja": "E2 Pares",
     "datos": "E2 Datos Pares", "grupo": "C1 y C2", "barrido": None, "centro": "",
     "archivo": _ruta("2026-10-14_sens1_faseB", "faseB_filas.csv")},
    {"n": 3, "nombre": "Muestreo LHS de 9 variables", "hoja": "E3 LHS 9 variables",
     "datos": "E3 Datos LHS", "grupo": "C1 y C2", "barrido": None, "centro": "",
     "archivo": _ruta("2026-10-14_sens1_faseC", "faseC_filas.csv")},
    {"n": 4, "nombre": "Fuente de 70 a 300 C", "hoja": "E4 Fuente 70-300 C",
     "datos": "E4 Datos Fuente", "grupo": "13 niveles de T_fuente", "barrido": "N1",
     "centro": "", "archivo": _ruta("2026-10-14_sens1_ronda1", "ronda1_filas.csv")},
    {"n": 5, "nombre": "Condensador y clima", "hoja": "E5 Condensador y clima",
     "datos": "E5 Datos Condensador", "grupo": "C1", "barrido": "N3", "centro": "",
     "archivo": _ruta("2026-10-14_sens1_ronda1", "ronda1_filas.csv")},
    {"n": 6, "nombre": "P_alta baja y composicion", "hoja": "E6 P_alta baja y x_b",
     "datos": "E6 Datos P_alta x_b", "grupo": "C1 y C2", "barrido": "N4", "centro": "",
     "archivo": _ruta("2026-10-14_sens1_ronda1", "ronda1_filas.csv")},
    {"n": 7, "nombre": "Fuente fria, presiones bajas", "hoja": "E7 Fuente fria",
     "datos": "E7 Datos Fuente fria", "grupo": "muestreo", "barrido": "N2", "centro": "",
     "archivo": _ruta("2026-10-15_sens1_ronda2", "ronda2_filas.csv")},
    {"n": 8, "nombre": "Mapa fuente x clima x P_baja", "hoja": "E8 Mapa fuente y clima",
     "datos": "E8 Datos Mapa fuente", "grupo": "malla", "barrido": "N5", "centro": "",
     "archivo": _ruta("2026-10-15_sens1_ronda2", "ronda2_filas.csv")},
    {"n": 9, "nombre": "Equipos baratos", "hoja": "E9 Equipos baratos",
     "datos": "E9 Datos Equipos", "grupo": "C1 y C2", "barrido": "N6", "centro": "",
     "archivo": _ruta("2026-10-15_sens1_ronda2", "ronda2_filas.csv")},
    {"n": 10, "nombre": "Centros nuevos, una variable", "hoja": "E10 Centros nuevos 1 variable",
     "datos": "E10 Datos Centros nuevos", "grupo": "C3 y C4", "barrido": "N7A", "centro": "",
     "archivo": _ruta("2026-10-15_sens1_N7", "n7_filas.csv")},
    {"n": 11, "nombre": "Centros nuevos, pares", "hoja": "E11 Centros nuevos pares",
     "datos": "E11 Datos Centros pares", "grupo": "C3 y C4", "barrido": "N7B", "centro": "",
     "archivo": _ruta("2026-10-15_sens1_N7", "n7_filas.csv")},
]

# Columnas de estado del motor que van a la hoja de datos completa, en su orden final.
ESTADOS = [f"T_e{i}" for i in range(1, 11)] + [f"h_e{i}" for i in range(1, 11)]


def _num(df, col):
    if col in df.columns:
        return pd.to_numeric(df[col], errors="coerce")
    return pd.Series([float("nan")] * len(df), index=df.index)


def _txt(df, col, defecto=""):
    if col in df.columns:
        return df[col].fillna(defecto).astype(str)
    return pd.Series([defecto] * len(df), index=df.index)


def cargar_estudio(est):
    """Lee el CSV de un estudio, se queda con su barrido y normaliza las columnas."""
    df = pd.read_csv(est["archivo"])
    if est["barrido"]:
        df = df[df["barrido"] == est["barrido"]].copy()
    df = df.reset_index(drop=True)
    o = pd.DataFrame(index=df.index)
    o["estudio"] = est["n"]
    o["id_punto"] = _txt(df, "id_punto")
    cen = _txt(df, "centro") if "centro" in df.columns else pd.Series([est["centro"]] * len(df))
    o["centro"] = [CENTRO_TXT.get(c, c) for c in cen]
    o["variable"] = _txt(df, "variable")
    o["par"] = _txt(df, "par")
    o["var1"] = _txt(df, "var1")
    o["var2"] = _txt(df, "var2")
    for c in COMUNES + ["valor", "val1", "val2"]:
        o[c] = _num(df, c)
    # Una fila sin clase (error del worker) no convergio: se cuenta como NO_CONVERGIO.
    o["clasificacion"] = _txt(df, "clasificacion").replace("", "NO_CONVERGIO")
    o["mensaje"] = _txt(df, "mensaje")
    o["convergio"] = _txt(df, "convergio").str.lower().isin(["true", "1"]).values
    o["fuera_rango"] = _txt(df, "fuera_rango").str.lower().isin(["true", "1"]).values
    for c in ESTADOS:
        o[c] = _num(df, c)
    return o


def derivar(df):
    """Columnas derivadas: clases, eta en %, y las razones Qreg/Qi y P_alta/P_baja."""
    d = df.copy()
    d["kalina"] = d["clasificacion"] == "KALINA"
    d["en_rango"] = True
    for c in EFIC:
        d["en_rango"] &= d[c].between(0.40, 0.95)
    d["confiable"] = d["kalina"] & (~d["fuera_rango"]) & d["en_rango"]
    d["fuera_motor"] = d["kalina"] & d["fuera_rango"]
    d["eta_pct"] = d["eta"] * 100.0
    d["qreg_qi"] = d["Qreg"] / d["Qi"]
    d["rp"] = d["P_alta"] / d["P_baja"]
    d["genuino"] = d["convergio"] & (d["clasificacion"] != "NO_CONVERGIO")
    return d


def valor_de(fila, variable):
    """Valor de `variable` en una fila; para la fila base de un barrido univariado, el del centro."""
    if fila.get("variable") == "base":
        return CENTROS.get(fila["centro"], {}).get(variable)
    return fila.get("valor")


def cargar_todo():
    """Los 12 estudios en un solo DataFrame derivado (3157 filas)."""
    partes = [cargar_estudio(e) for e in ESTUDIOS]
    d = derivar(pd.concat(partes, ignore_index=True))
    return d


def de_estudio(df, n):
    return df[df["estudio"] == n]


def de_centro(df, centro_txt):
    return df[df["centro"] == centro_txt]


NOMBRE_CENTRO = {e["n"]: e["grupo"] for e in ESTUDIOS}
