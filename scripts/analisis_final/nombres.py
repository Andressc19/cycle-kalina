# -*- coding: utf-8 -*-
"""A1 · Nombres de presentacion, etiquetas de clase y glosario (seccion 4).

Diccionario unico: todos los productos (figuras, tablas, tableros) leen aqui.
Textos literales del TASK_CONTEXT af-A1 §4 y de METODOLOGIA_ANALISIS_RESULTADOS §3A.6.
"""

NOMBRE = {
    "T_fuente": "Temperatura de la fuente, T_fuente [K]",
    "T_sumidero": "Temperatura del sumidero, T_sumidero [K]",
    "P_alta": "Presión de alta, P_alta [kPa]",
    "P_baja": "Presión de baja, P_baja [kPa]",
    "x_b": "Fracción de amoníaco de la mezcla base, x_b [–]",
    "m_b": "Flujo másico base, m_b [kg/s]",
    "eta_t": "Eficiencia isentrópica de la turbina, η_t [–]",
    "eta_p": "Eficiencia isentrópica de la bomba, η_p [–]",
    "eps_hrvg": "Efectividad del generador de vapor, ε_HRVG [–]",
    "eps_reg": "Efectividad del regenerador, ε_reg [–]",
    "eps_cond": "Efectividad del condensador, ε_cond [–]",
    "T_amb_diseno": "Piso de O2 (T de diseño de la bomba) [K]",
    "eta_pct": "Eficiencia térmica del ciclo, η [%]",
    "Wnet": "Trabajo neto, W_net [kW] (m_b = 1 kg/s)",
    "dP": "Diferencia de presiones, ΔP [kPa]",
    "rP": "Razón de presiones, r_P [–]",
    "dT_fs": "Diferencia de temperatura fuente–sumidero [K]",
    "clasificacion": "Clase del ciclo",
    "D": "Índice de cercanía D [–]",
}

ETIQUETA_CLASE = {
    "KALINA": "KALINA",
    "CORREGIBLE": "Corregible",
    "INVIABLE": "Inviable",
    "NO_CONVERGIO": "No convergió",
    "N2": "Falso convergido (N2)",
    "OMITIDO": "Omitido (no evaluado)",
}

GLOSARIO = {
    "PP (punto del profesor)": (
        "Los datos del enunciado: P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50, "
        "T_fuente 623.15 K, T_sumidero 300.03 K, η_t 0.85, η_p 0.75, ε_HRVG 0.85, "
        "ε_reg 0.75, ε_cond 0.80. Con ellos el ciclo no converge."),
    "A* (punto ancla)": (
        "El punto del profesor con solo dos cambios: T_fuente = 403 K y "
        "P_baja = 563.64 kPa. Es KALINA con η = 8.48 %. Se eligió en M2 como el "
        "cambio intermedio que vuelve funcional el ciclo, y M3 estudia la "
        "sensibilidad a su alrededor."),
    "Punto genuino": (
        "Punto cuya clase es KALINA, CORREGIBLE o INVIABLE: el modelo lo resolvió "
        "de verdad."),
    "N2 (falso convergido)": (
        "El solver dice que convergió, pero el clasificador lo marca NO_CONVERGIO: "
        "es una solución espuria y no cuenta como convergido."),
    "KALINA confiable": (
        "Punto KALINA dentro del rango validado del modelo de propiedades "
        "(IAPWS G4-01) y con todas sus η y ε en [0.40, 0.95]."),
    "Fuera de rango": (
        "Punto con estados fuera del rango validado del modelo de propiedades "
        "(por ejemplo, líquido por encima de 420 K); su η se toma con cautela."),
    "O1": "Criterio de título (calidad del vapor) a la salida de la turbina.",
    "O2": "Criterio de cavitación: el líquido debe llegar subenfriado a la bomba.",
    "O3": "Criterio de trabajo neto: el ciclo debe producir trabajo (W_net > 0).",
    "O5": "Criterio del separador: debe recibir una mezcla de dos fases.",
    "Piso de O2": (
        "Temperatura con la que se evalúa la cavitación. 300.03 K fija en M1–M3; "
        "desde M2S es igual a la T_sumidero de cada punto."),
    "Banda de η": (
        "Incertidumbre del modelo de propiedades: ±0.4–0.7 puntos porcentuales; "
        "diferencias menores no son concluyentes."),
    "Bloque": (
        "Conjunto de puntos con las mismas variables fijas y los mismos valores; "
        "solo se comparan puntos de un mismo bloque."),
}
