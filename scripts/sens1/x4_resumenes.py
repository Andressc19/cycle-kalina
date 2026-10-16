# -*- coding: utf-8 -*-
"""Sensibilidad 1 - x4: tablas para las hojas de resumen por estudio."""

import math

import pandas as pd

from x1_cargar import CENTROS, VAR_TXT, VARIABLES_ORDEN
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
    if est["n"] == 1:
        return "Barrido univariado (una variable): C1 y C2; se vario una variable a la vez en el rango 0.40–0.95 para eficiencias/efectividades."
    if est["n"] == 2:
        return "Barrido de pares: C1 y C2; malla 7x7 por par y centro."
    if est["n"] == 3:
        return "Muestreo LHS de 9 variables: C1 y C2; 500 puntos totales."
    return "Condiciones segun barrido del estudio."


def resumen_e1(ws, est, df_e):
    f = 1
    from x2_formato import titulo, condiciones, nota
    from conclusiones import apendice_a
    f = titulo(ws, f, est["hoja"])
    f = condiciones(ws, f, [condicion_texto(est, df_e), "Todos los valores salen de los CSV; no hay cifras copiadas de resumenes .md."])
    # Tabla de conteos por centro y clase
    g = df_e.groupby(["centro", "clasificacion"]).size().unstack(fill_value=0)
    g = g.reindex(columns=["KALINA", "CORREGIBLE", "NO_CONVERGIO", "INVIABLE"], fill_value=0)
    g["KALINA_conf"] = df_e[df_e["confiable"]].groupby("centro").size()
    g["KALINA_fuera"] = df_e[df_e["fuera_motor"]].groupby("centro").size()
    g = g.fillna(0).astype(int)
    g["Total"] = g.sum(axis=1)
    filas = []
    for c, row in g.iterrows():
        filas.append([c, row["KALINA"], row["KALINA_conf"], row["KALINA_fuera"], row["CORREGIBLE"], row["NO_CONVERGIO"], row["INVIABLE"], row["Total"]])
    tabla(ws, f, ["Centro", "KALINA (total)", "de ellos dentro del rango experimental", "de ellos fuera del rango experimental", "CORREGIBLE", "NO_CONVERGIO", "INVIABLE", "Total"], filas, anchos=[20, 12, 22, 22, 14, 14, 12, 10], clases=None, clave_fila=None)
    f += 2 + len(filas)
    # Tabla por variable (valores KALINA dentro del rango experimental)
    encabezados = ["Variable", "Unidad", "Centro", "Valor minimo", "Valor medio", "Valor maximo", "n KALINA dentro del rango experimental"]
    filas_v = []
    for var in VARIABLES_ORDEN:
        for cen in sorted(set(df_e["centro"])):
            sub = df_e[(df_e["confiable"]) & (df_e["centro"] == cen)]
            if sub.empty:
                continue
            vv = sub.apply(lambda r: r.get("valor") if r.get("variable") == var else (r.get("val1") if r.get("var1") == var else (r.get("val2") if r.get("var2") == var else None)), axis=1)
            vv = vv[vv.apply(_es_num)]
            if vv.empty:
                continue
            filas_v.append([VAR_TXT.get(var, var), "", cen, round(vv.min(), 4), round(vv.mean(), 4), round(vv.max(), 4), int(len(vv))])
    if filas_v:
        tabla(ws, f, encabezados, filas_v, anchos=[16, 8, 20, 12, 12, 12, 20], clases=None, clave_fila=None)
        f += 2 + len(filas_v)
    # Graficos del estudio (tabla de datos + grafico nativo junto a ella)
    f = dibujar_estudio(ws, est["n"], df_e, f)
    # Conclusion
    f = nota(ws, f, apendice_a(est["n"], df_e))
    return f


def resumen_generico(ws, est, df_e):
    f = 1
    from x2_formato import titulo, condiciones, nota
    from conclusiones import apendice_a
    f = titulo(ws, f, est["hoja"])
    f = condiciones(ws, f, [condicion_texto(est, df_e)])
    # Conteos
    g = df_e.groupby(["centro", "clasificacion"]).size().unstack(fill_value=0)
    g = g.reindex(columns=["KALINA", "CORREGIBLE", "NO_CONVERGIO", "INVIABLE"], fill_value=0)
    g["KALINA_conf"] = df_e[df_e["confiable"]].groupby("centro").size()
    g["KALINA_fuera"] = df_e[df_e["fuera_motor"]].groupby("centro").size()
    g = g.fillna(0).astype(int)
    g["Total"] = g.sum(axis=1)
    filas = []
    for c, row in g.iterrows():
        filas.append([c, row["KALINA"], row["KALINA_conf"], row["KALINA_fuera"], row["CORREGIBLE"], row["NO_CONVERGIO"], row["INVIABLE"], row["Total"]])
    tabla(ws, f, ["Centro", "KALINA (total)", "de ellos dentro del rango experimental", "de ellos fuera del rango experimental", "CORREGIBLE", "NO_CONVERGIO", "INVIABLE", "Total"], filas, anchos=[20, 12, 22, 22, 14, 14, 12, 10], clases=None, clave_fila=None)
    f += 2 + len(filas)
    # Graficos del estudio (tabla de datos + grafico nativo junto a ella)
    f = dibujar_estudio(ws, est["n"], df_e, f)
    f = nota(ws, f, apendice_a(est["n"], df_e))
    return f


def hoja_resumen(wb, est, df_e):
    ws = wb.create_sheet(est["hoja"])
    if est["n"] == 1:
        resumen_e1(ws, est, df_e)
    else:
        resumen_generico(ws, est, df_e)
    return ws.title
