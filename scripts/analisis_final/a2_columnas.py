# -*- coding: utf-8 -*-
"""A2 · Nombres en español propuestos para las columnas que no trae nombres.NOMBRE.

Cada entrada: columna_original -> (nombre_propuesto, tipo).  Los tipos son:
pres [kPa] · temp [K] · pct (%, 2 dec) · pct1 (%, 1 dec) · dec3 (3 dec) ·
idx (índices, 3 dec) · int · txt · gen (general).
Todo lo que se propone aquí se anota también en 02_tablas/traducciones_columnas.csv.
"""

PROPIAS = {
    # --- identificación y textos -------------------------------------------------
    "id": ("Identificador", "txt"), "id_subcaso": ("Subcaso", "txt"),
    "origen": ("Origen", "txt"), "grupo": ("Grupo", "txt"), "ruta": ("Ruta", "txt"),
    "parte": ("Parte", "txt"), "base": ("Base", "txt"), "familia": ("Familia", "txt"),
    "arranque": ("Arranque", "txt"), "escenario": ("Escenario", "int"),
    "conservados": ("Datos conservados", "txt"), "ronda": ("Ronda", "int"),
    "fuente": ("Fuente", "txt"), "franja": ("Franja", "int"),
    "separacion": ("Separación", "txt"), "salida": ("Salida", "txt"),
    "criterio": ("Criterio", "txt"), "tipo": ("Tipo", "txt"),
    "variable": ("Variable", "txt"), "nota": ("Nota", "txt"),
    "mensaje": ("Mensaje", "txt"), "mensaje_antes": ("Mensaje (antes)", "txt"),
    "mensaje_ahora": ("Mensaje (ahora)", "txt"),
    "variables_movidas": ("Variables movidas", "txt"),
    "clase_teqp": ("Clase con teqp", "txt"), "clase_real": ("Clase con el motor real", "txt"),
    "rP_req": ("Razón de presiones requerida, r_P [–]", "dec3"),
    "var1": ("Variable 1", "txt"), "var2": ("Variable 2", "txt"),
    "clase_antes": ("Clase (antes)", "txt"), "clase_ahora": ("Clase (ahora)", "txt"),
    "misma_clase": ("Misma clase", "txt"), "factible": ("Factible", "txt"),
    "alcanzable": ("Alcanzable", "txt"), "elegido": ("Elegido", "txt"),
    "coincide": ("Coincide", "int"), "dentro_banda": ("Dentro de la banda", "txt"),
    "B_verificado": ("B verificado", "txt"), "B_verificado_min_kalina": ("B verificado en la mínima KALINA", "txt"),
    "fuera_rango": ("Fuera de rango", "txt"),
    "fuera_rango_min_kalina": ("Fuera de rango en la mínima KALINA", "txt"),
    "coincide_clase": ("Coincide la clase", "txt"),
    "kalina_por_busqueda": ("KALINA por búsqueda", "txt"),

    # --- códigos y criterios -----------------------------------------------------
    "criterios_bloqueantes_frecuentes": ("Criterios bloqueantes frecuentes", "txt"),
    "criterios_bloqueantes": ("Criterios que bloquean", "txt"),
    "criterio_mas_roto": ("Criterio más roto", "txt"),
    "bloqueantes": ("Bloqueantes", "txt"),
    "bloqueantes_genuinos": ("Bloqueantes (genuinos)", "txt"),
    "codigos_bloqueo": ("Códigos de bloqueo", "txt"),
    "bloqueante": ("Criterio bloqueante", "txt"),
    "bloqueante_n": ("Veces que bloquea", "int"),
    "criterio_bajo": ("Criterio que rompe al bajar la variable", "txt"),
    "criterio_alto": ("Criterio que rompe al subir la variable", "txt"),

    # --- conteos -----------------------------------------------------------------
    "n": ("N", "int"), "n_puntos": ("Corridas", "int"), "kalina": ("KALINA", "int"),
    "kalina_confiables": ("KALINA confiables", "int"), "corregible": ("Corregibles", "int"),
    "invariable": ("Inviables", "int"), "no_convergio": ("No convergidos", "int"),
    "n2": ("Falsos convergidos (N2)", "int"), "omitidos": ("Omitidas", "int"),
    "n_B": ("n en B (KALINA)", "int"),
    "n_Bbar": ("n en B̄ (no KALINA)", "int"), "n_excluidos": ("n excluidos", "int"),
    "n_converge": ("Convergen", "int"), "n_kalina": ("KALINA", "int"),
    "n_corregible": ("Corregibles", "int"), "n_inviable": ("Inviables", "int"),
    "n_no_convergio": ("No convergidos", "int"),
    "n_espurios_N2": ("Falsos convergidos (N2)", "int"), "n_genuinos": ("Genuinos", "int"),
    "n_N2": ("Falsos convergidos (N2)", "int"), "n_kalina_confiable": ("KALINA confiables", "int"),
    "n_conservadas": ("Datos del profesor conservados", "int"), "n_eval": ("Evaluadas", "int"),
    "evaluados": ("Evaluados", "int"), "omitidos": ("Omitidos", "int"),
    "genuinos": ("Genuinos", "int"), "KALINA": ("KALINA", "int"),
    "N2": ("Falsos convergidos (N2)", "int"), "fuera_rango": ("Fuera de rango", "int"),
    "confiables_ahora": ("Confiables ahora", "int"),
    "KALINA_sept": ("KALINA (septiembre)", "int"), "KALINA_ahora": ("KALINA (ahora)", "int"),
    "iteraciones": ("Iteraciones", "int"), "evaluaciones": ("Evaluaciones", "int"),
    "t_s": ("Tiempo [s]", "gen"), "suma_t_s": ("Tiempo total [s]", "gen"),

    # --- valores de variable (sin unidad fija: la da la columna Variable) ---------
    "valor": ("Valor", "gen"), "val1": ("Valor 1", "gen"), "val2": ("Valor 2", "gen"),
    "a": ("Límite inferior a", "gen"), "b": ("Límite superior b", "gen"),
    "lo": ("Límite inferior", "gen"), "hi": ("Límite superior", "gen"),
    "min": ("Mínimo", "gen"), "p05": ("Percentil 5", "gen"),
    "mediana": ("Mediana", "gen"), "p95": ("Percentil 95", "gen"),
    "max": ("Máximo", "gen"),
    "valor_ancla": ("Valor en A*", "gen"),
    "valor_conv_mas_cercano_prof": ("Valor convergido más cercano al PP", "gen"),
    "valor_kalina_mas_cercano_prof": ("Valor KALINA más cercano al PP", "gen"),
    "valor_D_minimo": ("Valor de D mínimo", "gen"),
    "menor_d_val1": ("Valor 1 del d menor", "gen"), "menor_d_val2": ("Valor 2 del d menor", "gen"),
    "mayor_eta_val1": ("Valor 1 de la η mayor", "gen"), "mayor_eta_val2": ("Valor 2 de la η mayor", "gen"),
    "valor_eta_max_kalina": ("Valor de la η máxima KALINA", "gen"),
    "fav_p05": ("Rango favorable, p05", "gen"), "fav_p95": ("Rango favorable, p95", "gen"),
    "kalina_desde": ("KALINA desde", "gen"), "kalina_hasta": ("KALINA hasta", "gen"),
    "v_j": ("Valor anterior", "gen"), "v_j1": ("Valor siguiente", "gen"),
    "v_cruce": ("Valor del cruce", "gen"), "clase_j": ("Clase en el valor anterior", "txt"),
    "clase_j1": ("Clase en el valor siguiente", "txt"),
    "min_kalina": ("Mínimo KALINA", "gen"), "max_kalina": ("Máximo KALINA", "gen"),

    # --- presiones y temperaturas -------------------------------------------------
    "P_baja_min": ("P_baja mínima [kPa]", "pres"), "P_baja_max": ("P_baja máxima [kPa]", "pres"),
    "dP_min": ("ΔP mínima [kPa]", "pres"), "dP_max": ("ΔP máxima [kPa]", "pres"),
    "rP_min": ("r_P mínima [–]", "dec3"), "rP_max": ("r_P máxima [–]", "dec3"),
    "P_baja_min_kalina": ("P_baja mínima KALINA [kPa]", "pres"),
    "P_baja_max_kalina": ("P_baja máxima KALINA [kPa]", "pres"),
    "P_baja_min_O2": ("P_baja mínima con O2 [kPa]", "pres"),
    "P_baja_mejor_D": ("P_baja del mejor D [kPa]", "pres"),
    "P_baja_eta_max_kalina": ("P_baja en la η máxima KALINA [kPa]", "pres"),
    "P_baja_orig": ("P_baja original [kPa]", "pres"),
    "P_baja_req": ("P_baja requerida [kPa]", "pres"),
    "ΔP_baja": ("ΔP_baja [kPa]", "pres"),
    "P_alta_min": ("P_alta mínima [kPa]", "pres"), "P_alta_max": ("P_alta máxima [kPa]", "pres"),
    "piso_O2": ("Piso de O2 [K]", "temp"),
    "T_fuente_min": ("T_fuente mínima [K]", "temp"), "T_fuente_max": ("T_fuente máxima [K]", "temp"),
    "ΔT_sub": ("Subenfriamiento, ΔT_sub [K]", "temp"),

    # --- eficiencias (fracción -> %) ---------------------------------------------
    "eta": ("Eficiencia térmica del ciclo, η [%]", "pct"),
    "eta_pct": ("Eficiencia térmica del ciclo, η [%]", "pct"),
    "eta_antes": ("η (antes) [%]", "pct"), "eta_ahora": ("η (ahora) [%]", "pct"),
    "eta_min": ("η mínima [%]", "pct"), "eta_max": ("η máxima [%]", "pct"),
    "eta_teqp": ("η con teqp [%]", "pct"), "eta_real": ("η con el motor real [%]", "pct"),
    "eta_min_kalina": ("η mínima KALINA [%]", "pct"),
    "eta_max_kalina": ("η máxima KALINA [%]", "pct"),
    "eta_en_Tmin": ("η en T_fuente mínima [%]", "pct"),
    "eta_en_Tmax": ("η en T_fuente máxima [%]", "pct"),
    "mejor_eta": ("η máxima [%]", "pct"), "cercano_eta": ("η del más cercano [%]", "pct"),
    "mayor_eta": ("η mayor [%]", "pct"), "menor_d_eta": ("η en el d menor [%]", "pct"),
    "eta_orig": ("η original [%]", "pct"), "eta_req": ("η requerida [%]", "pct"),
    "d_eta_pp": ("Δη [pp]", "gen"), "delta_eta": ("Δη [pp]", "gen"),
    "d_eta_pp_medio_abs": ("|Δη| medio [pp]", "gen"), "d_eta_pp_max_abs": ("|Δη| máximo [pp]", "gen"),

    # --- índices y magnitudes sin unidad fija ------------------------------------
    "KS": ("KS", "idx"), "p_valor": ("Valor p", "idx"), "prcc": ("PRCC", "idx"),
    "t": ("t de Student", "idx"), "ic_lo": ("IC inferior", "idx"), "ic_hi": ("IC superior", "idx"),
    "d_normalizada": ("d normalizado", "idx"), "D_minimo": ("D mínimo", "idx"),
    "menor_d": ("d menor", "idx"), "mejor_D": ("D mínimo", "idx"), "D_min": ("D mínimo", "idx"),
    "E_eta": ("Elasticidad E en A* [–]", "idx"), "mejor_D_id": ("Identificador del D mínimo", "txt"),
    "cercano_id": ("Identificador del más cercano", "txt"), "cercano_d": ("d del más cercano", "idx"),
    "mejor_eta_id": ("Identificador de la η máxima", "txt"),
    "pct_kalina": ("KALINA [%]", "pct1"), "piso": ("Piso de O2 [K]", "temp"),
    "m_O1_teqp": ("Margen O1 con teqp [–]", "dec3"), "m_O1_real": ("Margen O1 con el motor real [–]", "dec3"),
    "m_O2_teqp": ("Margen O2 con teqp [K]", "temp"), "m_O2_real": ("Margen O2 con el motor real [K]", "temp"),
    "m_O1_req": ("Margen O1 requerido [–]", "dec3"),
    "m_O1": ("Margen O1 [–]", "dec3"), "m_O2": ("Margen O2 [K]", "temp"),
    "m_O5": ("Margen O5 [–]", "dec3"),
}

# η guardadas como fracción en los CSV fuente: al presentar en % se multiplican por 100.
ETA_FRAC = {"eta", "eta_antes", "eta_ahora", "eta_min", "eta_max", "eta_teqp",
            "eta_real", "eta_min_kalina", "eta_max_kalina", "eta_en_Tmin",
            "eta_en_Tmax", "mejor_eta", "cercano_eta", "mayor_eta", "menor_d_eta",
            "eta_orig", "eta_req"}


def tipo_por_unidad(nombre):
    """Tipo de dato deducido de la unidad escrita entre corchetes del nombre."""
    if "[kPa]" in nombre:
        return "pres"
    if "[K]" in nombre:
        return "temp"
    if "[%]" in nombre:
        return "pct"
    if "[–]" in nombre:
        return "dec3"
    return "gen"
