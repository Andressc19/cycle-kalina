# -*- coding: utf-8 -*-
"""Sens2 - s2_f5u: hoja `F5 Incertidumbre` (propagacion de incertidumbre alrededor de los 4 centros KALINA)."""
import os
import sys

import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))
sys.path.insert(0, AQUI)
from x2_formato import condiciones, descripcion, nota, subtitulo, tabla, titulo  # noqa: E402
from x5_graficos import bloque  # noqa: E402
from s2_comun import barras_con_signo, numero  # noqa: E402
from u1_puntos import ESCENARIOS, TOL, VARIABLES  # noqa: E402

U1 = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_U1")
CENTROS = ["C1", "C2", "C3", "C4"]


def _tol_txt():
    return ", ".join("%s %s" % (v, ("%.0f %%" % (TOL[v] * 100)) if v in ("P_alta", "P_baja") else "%g" % TOL[v])
                     for v in VARIABLES)


def hoja_f5_incertidumbre(wb, datos):
    ws = wb.create_sheet("F5 Incertidumbre")
    r = pd.read_csv(os.path.join(U1, "u1_resumen.csv"))
    s = pd.read_csv(os.path.join(U1, "u1_sensibilidad.csv"))
    n = int(r["n"].sum())
    f = titulo(ws, 1, "F5 Propagacion de incertidumbre alrededor de los 4 centros KALINA", ancho=10)
    f = condiciones(ws, f, [
        "Base: %d puntos nuevos del motor (teqp): %d por escenario y centro (LHS de 10 variables, uniforme alrededor del centro)." % (
            n, int(r["n"].max())),
        "Escenario A (tolerancias nominales): " + _tol_txt() + " (absolutas; P_alta y P_baja relativas).",
        "Escenario B: el doble de cada tolerancia. Limites: eficiencias y efectividades en 0.40 a 0.95; T_sumidero 5 a 30 °C; P_alta >= 1.3 P_baja.",
        "Las tolerancias son SUPUESTOS de escenario (variabilidad de operacion y de rendimiento de equipos), no mediciones.",
        "Banda del modelo de propiedades (G4-01): +-0.7 pp de eta, sumada de forma determinista a P5 y P95.",
        "Fuente: resultados/2026-10-17_sens2_U1 (u1_filas.csv, u1_resumen.csv, u1_sensibilidad.csv)."])
    f = subtitulo(ws, f, "1. Probabilidad de seguir siendo KALINA")
    filas = [[x["escenario"], x["centro"], int(x["n"]), int(x["n_kalina"]), numero(x["p_kalina"], 3), numero(x["p_lo"], 3),
              numero(x["p_hi"], 3), int(x["n_corregible"]), int(x["n_no_conv"]), int(x["n_inviable"])]
             for _, x in r.iterrows()]
    _, f, _ = tabla(ws, f, ["Escenario", "Bloque", "Puntos", "KALINA", "P(KALINA)", "IC 95 % bajo", "IC 95 % alto",
                            "CORREGIBLE", "NO_CONVERGIO", "INVIABLE"], filas, anchos=[10, 8, 8, 9, 10, 12, 12, 12, 14, 10])
    f += 1
    piv = [[c] + [numero(float(r[(r["escenario"] == e) & (r["centro"] == c)]["p_kalina"].iloc[0]), 3) for e in ESCENARIOS]
           for c in CENTROS]
    f = bloque(ws, f, titulo="P(KALINA) tras perturbar todas las variables, por bloque y escenario",
               encabezados=["Bloque"] + list(ESCENARIOS), filas=piv, x="Bloque", y="P(KALINA)",
               nota_txt="Fuente: u1_resumen.csv. A = tolerancias nominales; B = el doble. Intervalos de Wilson en la tabla.")
    f = subtitulo(ws, f, "2. Eficiencia de los puntos que siguen siendo KALINA")
    filas = [[x["escenario"], x["centro"], numero(x["eta_nominal"], 2), numero(x["eta_p5"], 2), numero(x["eta_p50"], 2),
              numero(x["eta_p95"], 2), numero(x["eta_p5_modelo"], 2), numero(x["eta_p95_modelo"], 2),
              numero(x["p_eta_1pp"], 2), numero(x["p_fuera_rango"], 2)] for _, x in r.iterrows()]
    _, f, _ = tabla(ws, f, ["Escenario", "Bloque", "eta del centro (%)", "eta P5 (%)", "eta mediana (%)", "eta P95 (%)",
                            "P5 con banda del modelo (%)", "P95 con banda del modelo (%)", "P(|eta - centro| <= 1 pp)",
                            "Fraccion fuera del rango experimental"], filas,
                    anchos=[10, 8, 12, 10, 12, 10, 16, 16, 16, 18])
    f += 1
    for e in ESCENARIOS:
        fl = [[c, numero(x["eta_nominal"], 2), numero(x["eta_p5"], 2), numero(x["eta_p50"], 2), numero(x["eta_p95"], 2)]
              for c in CENTROS for _, x in [(0, r[(r["escenario"] == e) & (r["centro"] == c)].iloc[0])]]
        f = bloque(ws, f, titulo="eta de los KALINA tras perturbar (%s): centro, P5, mediana y P95" % e,
                   encabezados=["Bloque", "Centro", "P5", "Mediana", "P95"], filas=fl, x="Bloque", y="eta (%)",
                   nota_txt="Fuente: u1_resumen.csv; solo los puntos que siguen siendo KALINA.")
    f = subtitulo(ws, f, "3. Por que dejan de ser KALINA")
    fl = [["%s %s" % (x["escenario"][-1], x["centro"]), int(x["corr_o2"]), int(x["corr_o1"]),
           int(x["n_corregible"] - x["corr_o2"] - x["corr_o1"]), int(x["n_no_conv"]), int(x["n_inviable"])]
          for _, x in r.iterrows()]
    f = bloque(ws, f, titulo="Puntos que dejan de ser KALINA, por causa (escenario y bloque)",
               encabezados=["Escenario y bloque", "CORREGIBLE por O2", "CORREGIBLE por O1", "CORREGIBLE por otra causa",
                            "NO_CONVERGIO", "INVIABLE"], filas=fl, x="Escenario y bloque", y="Puntos", apiladas=True,
               nota_txt="Fuente: u1_resumen.csv. O2 = subenfriamiento en la bomba (cavitacion); O1 = titulo de salida de turbina.",
               ancho=20.0)
    f = subtitulo(ws, f, "4. Que variables explican que se pierda la clase KALINA (PRCC sobre el indicador KALINA)")
    for e in ESCENARIOS:
        fl = []
        for v in VARIABLES:
            fila = [v]
            for c in CENTROS:
                x = s[(s["escenario"] == e) & (s["centro"] == c) & (s["variable"] == v)]["prcc_kalina"]
                fila.append(numero(float(x.iloc[0]), 3) if len(x) and x.iloc[0] == x.iloc[0] else 0.0)
            fl.append(fila)
        f = barras_con_signo(ws, f, ["Variable"] + CENTROS, fl, titulo="PRCC de cada variable con P(KALINA) (%s)" % e,
                             x="Variable", y="PRCC (-)")
    f = nota(ws, f, "PRCC positivo: subir la variable favorece seguir en KALINA. 0.0 = indice no calculable (variable sin variacion util).")
    descripcion(ws, f + 1, ["Propagacion de incertidumbre: cuantos puntos siguen siendo KALINA al perturbar las 10 variables a la vez.",
                            "Escenario A con tolerancias nominales y escenario B con el doble; resultados por bloque."])
    return ws


HOJAS_F5U = [hoja_f5_incertidumbre]
