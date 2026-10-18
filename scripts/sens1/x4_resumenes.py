# -*- coding: utf-8 -*-
"""Sensibilidad 1 - x4: tablas para las hojas de resumen por estudio.

Cada hoja de resumen cuenta SOLO los puntos de su estudio (no el total del libro) y el punto
base de un centro se cuenta dentro del barrido de cada variable (es un punto de todos sus
barridos), sin mostrarlo como fila aparte.
"""

import math

from x1_cargar import (CENTROS, VAR_TXT, VARIABLES_ORDEN, bases_por_centro,
                       etiqueta_centro)
from x2_formato import tabla
from x5b_graficos_a import dibujar_estudio


def _es_num(v):
    return isinstance(v, (int, float)) and not math.isnan(v)


def condicion_texto(est, df_e):
    """Linea de condiciones fijas y barrido para el bloque de condiciones."""
    if est["n"] == 0:
        return "Condiciones: C1 Husavik (T_fuente 394.15 K, T_sumidero 278.15 K, P_alta 3300 kPa, P_baja 690 kPa, x_b 0.82, eta_t 0.85, eta_p 0.80, eps_HRVG 0.85, eps_reg 0.75, eps_cond 0.95); m_b 1.0 kg/s; se vario m_b 1.0 y 20.0 kg/s."
    if est["barrido"] == "N1":
        return "Barrido N1 (T_fuente 70 a 300 °C) en 13 niveles; con variables de los centros C1/C2 segun el punto."
    if est["barrido"] == "N3":
        return "Barrido N3 (eps_cond x T_sumidero) en C1; malla 7x7."
    if est["barrido"] == "N4":
        return "Barrido N4 (P_alta x x_b) en C1 y C2; malla 7x7 por centro."
    if est["barrido"] == "N2":
        return "Barrido N2 (muestreo LHS con P_alta/P_baja bajas y fuente 70–130 °C)."
    if est["barrido"] == "N5":
        return "Barrido N5 (mapa T_fuente x T_sumidero x P_baja), P_alta 3000 kPa, x_b 0.70; malla 5x5x5."
    if est["barrido"] == "N6":
        return "Barrido N6 (equipos baratos): combinaciones de eta_t, eps_HRVG, eps_reg en {0.40, 0.55, 0.70}, eps_cond 0.95; C1 y C2."
    if est["barrido"] == "N7A":
        return "Barrido N7A (una variable) en C3 y C4."
    if est["barrido"] == "N7B":
        return "Barrido N7B (pares) en C3 y C4."
    if est["barrido"] == "N8":
        return ("Barrido N8 (muestreo LHS de 9 variables, semilla 20261017) en C3 y C4; 250 "
                "candidatas por centro redondeadas (0.5 K / 10 kPa / 0.01 / 0.05), eta_p 0.80 y "
                "m_b 1.0 kg/s fijos.")
    if est["barrido"] == "N9":
        return ("Barrido N9 (pares B5 eps_reg × eta_t y B6 eps_HRVG × T_fuente) en C3 y C4; "
                "malla 7 × 7 por par y centro con el punto base.")
    if est["barrido"] == "N10":
        return ("Barrido N10 (P_alta de 4000 a 8000 kPa × P_baja) en C1, C3 y C4; malla 5 × 7 "
                "por centro.")
    if est["n"] == 1:
        return "Barrido univariado (una variable): C1 y C2; se vario una variable a la vez en el rango 0.40–0.95 para eficiencias/efectividades."
    if est["n"] == 2:
        return "Barrido de pares: C1 y C2; malla 7x7 por par y centro."
    if est["n"] == 3:
        return "Muestreo LHS de 9 variables: C1 y C2; 500 puntos totales."
    return "Condiciones segun barrido del estudio."


def filas_ventanas(df):
    """[Variable, Unidad, Centro, min, medio, max, n KALINA] del barrido de cada variable + base.

    Cada variable usa solo los puntos de su propio barrido (mas el punto base del centro, que
    es un punto de todos los barridos). `df` debe contener ya los estudios y centros deseados.
    """
    bases = bases_por_centro(df)
    filas = []
    for var in VARIABLES_ORDEN:
        for cen in sorted(set(df["centro"])):
            s = df[(df["centro"] == cen) & (df["variable"] == var) & df["kalina"]]
            vv = [float(x) for x in s["valor"] if _es_num(x)]
            base = bases.get(cen)
            if base is not None and base["kalina"]:
                bv = CENTROS.get(cen, {}).get(var)
                if _es_num(bv):
                    vv.append(float(bv))
            if not vv:
                continue
            filas.append([VAR_TXT.get(var, var), "", etiqueta_centro(cen), round(min(vv), 4),
                          round(sum(vv) / len(vv), 4), round(max(vv), 4), len(vv)])
    return filas


def _tabla_conteos(ws, f, df_e):
    """Tabla de clases por centro del estudio; el Total es la suma de las 4 clases."""
    g = df_e.groupby(["centro", "clasificacion"]).size().unstack(fill_value=0)
    g = g.reindex(columns=["KALINA", "CORREGIBLE", "NO_CONVERGIO", "INVIABLE"], fill_value=0)
    g["KALINA_conf"] = df_e[df_e["confiable"]].groupby("centro").size()
    g["KALINA_fuera"] = df_e[df_e["fuera_motor"]].groupby("centro").size()
    g = g.fillna(0).astype(int)
    g["Total"] = g[["KALINA", "CORREGIBLE", "NO_CONVERGIO", "INVIABLE"]].sum(axis=1)
    filas = []
    for c, row in g.iterrows():
        filas.append([etiqueta_centro(c), row["KALINA"], row["KALINA_conf"], row["KALINA_fuera"],
                      row["CORREGIBLE"], row["NO_CONVERGIO"], row["INVIABLE"], row["Total"]])
    tabla(ws, f, ["Centro", "KALINA (total)", "de ellos dentro del rango experimental",
                  "de ellos fuera del rango experimental", "CORREGIBLE", "NO_CONVERGIO",
                  "INVIABLE", "Total"], filas, anchos=[20, 12, 22, 22, 14, 14, 12, 10],
          clases=None, clave_fila=None)
    return f + 2 + len(filas)


def resumen(ws, est, df):
    f = 1
    from x2_formato import titulo, condiciones, nota
    from conclusiones import apendice_a
    df_e = df[df["estudio"] == est["n"]]
    f = titulo(ws, f, est["hoja"])
    lineas = [condicion_texto(est, df_e)]
    if est["n"] == 1:
        lineas.append("Todos los valores salen de los CSV; no hay cifras copiadas de resumenes .md.")
    f = condiciones(ws, f, lineas)
    if est["n"] in (14, 15, 16):
        from x4b_resumenes_c import secciones_extra
        f = secciones_extra(ws, est["n"], df, f)
    else:
        f = _tabla_conteos(ws, f, df_e)
        if est["n"] in (1, 10):
            filas = filas_ventanas(df_e)
            if filas:
                tabla(ws, f, ["Variable", "Unidad", "Centro", "Valor minimo", "Valor medio",
                              "Valor maximo", "n KALINA (total)"], filas,
                      anchos=[16, 8, 20, 12, 12, 12, 14], clases=None, clave_fila=None)
                f += 2 + len(filas)
        f = dibujar_estudio(ws, est["n"], df, f)
    f = nota(ws, f, apendice_a(est["n"], df_e))
    return f


def hoja_resumen(wb, est, df):
    ws = wb.create_sheet(est["hoja"])
    resumen(ws, est, df)
    return ws.title
