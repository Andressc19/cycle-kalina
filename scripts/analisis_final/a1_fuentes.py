# -*- coding: utf-8 -*-
"""A1 · Fuentes de la tabla canónica (TASK_CONTEXT af-A1, secciones 1 y 2).

Cada entrada de FUENTES describe un CSV de la campaña final (M1-M10b):
  archivo    ruta relativa al directorio de trabajo (raiz: RAIZ)
  id_caso    identificador del caso
  tipo_punto literal, o {"columna": "<nombre>"} si sale de una columna de la fila
  subcaso    plantilla del id_subcaso; {col} se sustituye por el valor de la fila
  bloque     plantilla del bloque_director

El valor de una columna se sanea SOLO dentro de los identificadores (espacios y
'+' -> '_') y se conserva crudo en su propia columna.
"""
import os

import pandas as pd

RAIZ = "resultados"

ENTRADAS = ["T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "m_b", "eta_t",
            "eta_p", "eps_hrvg", "eps_reg", "eps_cond", "T_amb_diseno", "motor"]

SALIDAS = ["convergio", "clasificacion", "codigos_falla", "eta", "Wnet", "m_O1",
           "m_O2", "m_O3", "m_O5", "D", "viol_O1", "viol_O2", "viol_O3", "viol_O5",
           "fuera_rango", "B_verificado", "t_s", "mensaje"]

PROPIAS = ["grupo", "ruta", "var1", "val1", "var2", "val2", "parte", "base",
           "escenario", "conservados", "ronda", "arranque", "iteracion", "variable",
           "valor", "id", "id_muestra", "realista", "familia", "piso", "origen"]

CALCULADAS = ["genuino", "es_N2", "kalina_confiable", "omitido", "wnet_pos",
              "eta_pct", "dP", "rP", "dT_fs", "clase_trazo"]

COL_ID = ["id_punto", "estudio", "parte_estudio", "parte_nombre",   # nomenclatura nueva (codigos.py)
          "id_caso", "id_subcaso", "bloque_director", "tipo_punto",
          "origen_csv", "fila_origen"]

COLUMNAS_TABLA = COL_ID + ENTRADAS + SALIDAS + PROPIAS + CALCULADAS

# Punto del profesor (PP): solo estas 12 variables tienen valor de referencia.
PROFESOR = {"T_fuente": 623.15, "T_sumidero": 300.032917, "P_alta": 3000.0,
            "P_baja": 400.0, "x_b": 0.50, "m_b": 1.0, "eta_t": 0.85, "eta_p": 0.75,
            "eps_hrvg": 0.85, "eps_reg": 0.75, "eps_cond": 0.80,
            "T_amb_diseno": 300.032917}

UNIDAD = {"T_fuente": "K", "T_sumidero": "K", "P_alta": "kPa", "P_baja": "kPa",
          "x_b": "–", "m_b": "kg/s", "eta_t": "–", "eta_p": "–", "eps_hrvg": "–",
          "eps_reg": "–", "eps_cond": "–", "T_amb_diseno": "K", "motor": "–"}

CLASES_GENUINAS = ("KALINA", "CORREGIBLE", "INVIABLE")

FUENTES = [
    {"archivo": "2026-10-06_final_M1/m1_filas.csv", "id_caso": "KF-M01",
     "tipo_punto": "malla", "subcaso": "KF-M01-{grupo}", "bloque": "B01"},
    {"archivo": "2026-10-06_final_M2/m2n1_malla.csv", "id_caso": "KF-M02-N1",
     "tipo_punto": "malla", "subcaso": "KF-M02-N1", "bloque": "B02"},
    {"archivo": "2026-10-06_final_M2/m2n1_biseccion.csv", "id_caso": "KF-M02-N1",
     "tipo_punto": "biseccion", "subcaso": "KF-M02-N1", "bloque": "B02"},
    {"archivo": "2026-10-06_final_M2/m2n2_malla.csv", "id_caso": "KF-M02-N2",
     "tipo_punto": "malla", "subcaso": "KF-M02-N2-{ruta}", "bloque": "B03-{ruta}"},
    {"archivo": "2026-10-06_final_M2/m2n2_biseccion.csv", "id_caso": "KF-M02-N2",
     "tipo_punto": "biseccion", "subcaso": "KF-M02-N2-{ruta}", "bloque": "B03-{ruta}"},
    {"archivo": "2026-10-06_final_M2R/m2r_n1_malla.csv", "id_caso": "KF-M02R",
     "tipo_punto": "malla", "subcaso": "KF-M02R-{parte}", "bloque": "B04-{parte}"},
    {"archivo": "2026-10-06_final_M2R/m2r_n1_biseccion.csv", "id_caso": "KF-M02R",
     "tipo_punto": "biseccion", "subcaso": "KF-M02R-{parte}", "bloque": "B04-{parte}"},
    {"archivo": "2026-10-06_final_M2R/m2r_n2a_malla.csv", "id_caso": "KF-M02R",
     "tipo_punto": "malla", "subcaso": "KF-M02R-{parte}", "bloque": "B04-{parte}"},
    {"archivo": "2026-10-06_final_M2R/m2r_n2a_biseccion.csv", "id_caso": "KF-M02R",
     "tipo_punto": "biseccion", "subcaso": "KF-M02R-{parte}", "bloque": "B04-{parte}"},
    {"archivo": "2026-10-06_final_M2R/m2r_n2b_malla.csv", "id_caso": "KF-M02R",
     "tipo_punto": "malla", "subcaso": "KF-M02R-{parte}", "bloque": "B04-{parte}"},
    {"archivo": "2026-10-06_final_M2R/m2r_n2b_biseccion.csv", "id_caso": "KF-M02R",
     "tipo_punto": "biseccion", "subcaso": "KF-M02R-{parte}", "bloque": "B04-{parte}"},
    {"archivo": "2026-10-06_final_M2R/m2r_n3_malla.csv", "id_caso": "KF-M02R",
     "tipo_punto": "malla", "subcaso": "KF-M02R-{parte}", "bloque": "B04-{parte}"},
    {"archivo": "2026-10-06_final_M2S/m2s_malla.csv", "id_caso": "KF-M02S",
     "tipo_punto": "malla", "subcaso": "KF-M02S-{base}", "bloque": "B05-{base}"},
    {"archivo": "2026-10-06_final_M2S/m2s_biseccion.csv", "id_caso": "KF-M02S",
     "tipo_punto": "biseccion", "subcaso": "KF-M02S-{base}", "bloque": "B05-{base}"},
    {"archivo": "2026-10-06_final_M3/m3_ofat.csv", "id_caso": "KF-M03",
     "tipo_punto": {"columna": "tipo_punto"}, "subcaso": "KF-M03", "bloque": "B06"},
    {"archivo": "2026-10-06_final_M4/m4_lhs.csv", "id_caso": "KF-M04",
     "tipo_punto": "lhs", "subcaso": "KF-M04", "bloque": "B07"},
    {"archivo": "2026-10-07_final_M4b/m4b_lhs.csv", "id_caso": "KF-M04b",
     "tipo_punto": "lhs", "subcaso": "KF-M04b", "bloque": "B07"},
    {"archivo": "2026-10-07_final_M4c/m4c_lhs.csv", "id_caso": "KF-M04c",
     "tipo_punto": "lhs", "subcaso": "KF-M04c", "bloque": "B08"},
    {"archivo": "2026-10-07_final_M5/m5_lhs.csv", "id_caso": "KF-M05",
     "tipo_punto": "lhs", "subcaso": "KF-M05-{escenario}", "bloque": "B09-{escenario}"},
    {"archivo": "2026-10-07_final_M5c/m5c_malla.csv", "id_caso": "KF-M05c",
     "tipo_punto": "malla", "subcaso": "KF-M05c", "bloque": "B10"},
    {"archivo": "2026-10-07_final_M7/m7_evaluaciones.csv", "id_caso": "KF-M07",
     "tipo_punto": "busqueda", "subcaso": "KF-M07-{arranque}", "bloque": "B11-{arranque}"},
    {"archivo": "2026-10-07_final_M8_anecdotico/m8_oat.csv", "id_caso": "KF-M08",
     "tipo_punto": "oat", "subcaso": "KF-M08", "bloque": "BX"},
    {"archivo": "2026-10-08_final_M6/m6_verificacion.csv", "id_caso": "KF-M06",
     "tipo_punto": "control", "subcaso": "KF-M06-VER", "bloque": "B12"},
    {"archivo": "2026-10-08_final_M6/m6_piso_30_4C.csv", "id_caso": "KF-M06",
     "tipo_punto": "control", "subcaso": "KF-M06-PISO", "bloque": "B12"},
    {"archivo": "2026-10-08_final_M6/m6_subenfriamiento_evals.csv", "id_caso": "KF-M06",
     "tipo_punto": "busqueda", "subcaso": "KF-M06-SUB", "bloque": "B12"},
    {"archivo": "2026-10-08_final_M9/m9_paso1.csv", "id_caso": "KF-M09",
     "tipo_punto": "lhs", "subcaso": "KF-M09-R0-{conservados}",
     "bloque": "B13-{conservados}"},
    {"archivo": "2026-10-08_final_M9/m9_paso2.csv", "id_caso": "KF-M09",
     "tipo_punto": "lhs", "subcaso": "KF-M09-R{ronda}-{conservados}",
     "bloque": "B13-{conservados}"},
    {"archivo": "2026-10-08_final_M9/m9_husavik.csv", "id_caso": "KF-M09",
     "tipo_punto": "control", "subcaso": "KF-M09-HUS", "bloque": "B13-HUS"},
    {"archivo": "2026-10-08_final_M9/m9_motor_real_raw.csv", "id_caso": "KF-M09",
     "tipo_punto": "control", "subcaso": "KF-M09-REAL", "bloque": "B12"},
    {"archivo": "2026-10-09_final_M10_husavik/m10_recorrida_fase3.csv", "id_caso": "KF-M10",
     "tipo_punto": "control", "subcaso": "KF-M10-F3", "bloque": "B14-F3"},
    {"archivo": "2026-10-09_final_M10_husavik/m10_ofat.csv", "id_caso": "KF-M10",
     "tipo_punto": "oat", "subcaso": "KF-M10-OFAT", "bloque": "B14-OFAT"},
    {"archivo": "2026-10-09_final_M10_husavik/m10_malla_xb_pbaja.csv", "id_caso": "KF-M10",
     "tipo_punto": "malla", "subcaso": "KF-M10-MALLA", "bloque": "B14-MALLA"},
    {"archivo": "2026-10-09_final_M10b_xb_bajo/m10b_ofat_xb.csv", "id_caso": "KF-M10b",
     "tipo_punto": "oat", "subcaso": "KF-M10b-OFAT", "bloque": "B14-OFATb"},
    {"archivo": "2026-10-09_final_M10b_xb_bajo/m10b_malla_xb_pbaja.csv", "id_caso": "KF-M10b",
     "tipo_punto": "malla", "subcaso": "KF-M10b-MALLA", "bloque": "B14-MALLA"},
]


def columnas_de(plantilla):
    """Nombres {col} de una plantilla de identificador."""
    import re
    return re.findall(r"\{(\w+)\}", plantilla)


def sanea(valor):
    """Valor de columna apto para un identificador (espacios y '+' -> '_')."""
    return str(valor).strip().replace(" ", "_").replace("+", "_")


def es_verdadero(valor):
    """True solo para valores verdaderos; NaN/None/''/NA cuentan como falso."""
    if valor is None:
        return False
    if isinstance(valor, str):
        texto = valor.strip().lower()
        if texto in ("", "nan", "none", "<na>"):
            return False
        return texto in ("true", "1", "verdadero", "si", "sí")
    try:
        if pd.isna(valor):
            return False
    except (TypeError, ValueError):
        return False
    return bool(valor)


def vacio(valor):
    """True si el valor no aporta dato (vacío o NaN)."""
    if valor is None:
        return True
    if isinstance(valor, str):
        return valor.strip() == ""
    try:
        return bool(pd.isna(valor))
    except (TypeError, ValueError):
        return False


def fmtg(valor):
    """Representación corta de un valor (6 cifras significativas para números)."""
    if isinstance(valor, str):
        return valor
    return f"{float(valor):g}"


def sig6(valor):
    """Redondeo a 6 cifras significativas (clave para contar valores distintos)."""
    return float(f"{float(valor):.6g}")


def ruta_origen(archivo):
    """Ruta de origen normalizada con '/' (raíz RAIZ)."""
    return (RAIZ + "/" + archivo).replace(os.sep, "/")


def conteos(grupo):
    """[n, genuinos, KALINA, KALINA confiables, CORREGIBLE, INVIABLE,
    NO_CONVERGIO sin N2, N2, omitidos, fuera de rango] para un grupo de filas."""
    clase = grupo["clasificacion"]
    n2 = grupo["es_N2"].map(es_verdadero)
    return [len(grupo), int(grupo["genuino"].map(es_verdadero).sum()),
            int(clase.eq("KALINA").sum()),
            int(grupo["kalina_confiable"].map(es_verdadero).sum()),
            int(clase.eq("CORREGIBLE").sum()), int(clase.eq("INVIABLE").sum()),
            int((clase.eq("NO_CONVERGIO") & ~n2).sum()), int(n2.sum()),
            int(grupo["omitido"].map(es_verdadero).sum()),
            int(grupo["fuera_rango"].map(es_verdadero).sum())]


NOMBRES_CONTEO = ["n_puntos", "genuinos", "kalina", "kalina_confiables",
                  "corregible", "invariable", "no_convergio", "n2", "omitidos",
                  "fuera_rango"]
