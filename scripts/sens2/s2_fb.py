# -*- coding: utf-8 -*-
"""Sens2 etapa B - hoja `F3 Pisos 25 kPa y reintento` (todo leido de p6_pisos25.csv y p6_reintento_nc.csv)."""
import os
import sys

import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))
sys.path.insert(0, AQUI)
from x2_formato import condiciones, descripcion, nota, subtitulo, tabla, titulo  # noqa: E402
from x5_graficos import bloque  # noqa: E402

F1 = os.path.join(RAIZ, "resultados", "2026-10-18_sens2_F1")


def hoja_pisos_reintento(wb, datos):
    p = pd.read_csv(os.path.join(F1, "p6_pisos25.csv"))
    r = pd.read_csv(os.path.join(F1, "p6_reintento_nc.csv"))
    ws = wb.create_sheet("F3 Pisos 25 kPa y reintento")
    f = titulo(ws, 1, "F3 Pisos de P_baja con paso de 25 kPa y reintento de NO_CONVERGIO (corridas nuevas del motor)", ancho=10)
    f = condiciones(ws, f, [
        "Base: centro de cada bloque con x_b y P_baja cambiados; T_fuente, T_sumidero, P_alta y las eficiencias en el centro.",
        "Pisos: P_baja entre el ultimo nivel sin KALINA y el primero con KALINA de la malla P_baja x x_b (resolucion 100 a 150 kPa), con paso de 25 kPa (49 puntos).",
        "Reintento: 90 NO_CONVERGIO originales (75 que agotaron el presupuesto de 300 s y 15 rapidos de control) con presupuesto 900 s y tope 1100 s.",
        "Fuente: resultados/2026-10-18_sens2_B (s2b_filas.csv) y resultados/2026-10-18_sens2_F1 (p6_pisos25.csv, p6_reintento_nc.csv)."])
    f = subtitulo(ws, f, "1. Piso de P_baja: malla de 100 a 150 kPa frente a paso de 25 kPa")
    p["etiqueta"] = p["centro"] + " x_b " + p["x_b"].map(lambda v: "%.2f" % v)
    fl = [[a.etiqueta, float(a.piso_malla), float(a.piso_refinado)] for a in p.itertuples()]
    f = bloque(ws, f, titulo="Piso de P_baja (kPa) por centro y x_b", encabezados=["Centro y x_b", "Piso de la malla (kPa)", "Piso con paso de 25 kPa (kPa)"], filas=fl,
               x="Centro y x_b", y="P_baja del piso (kPa)", horizontal=False,
               nota_txt="Fuente: p6_pisos25.csv. El piso refinado es el menor P_baja desde el cual todos los puntos corridos hasta el piso de la malla son KALINA; "
                        "los NO_CONVERGIO cortan la secuencia. No es un NPSH: es el margen cero de cavitacion (O2).")
    cab = ["Centro", "x_b", "Nivel inferior de la malla", "Piso de la malla", "Puntos", "KALINA", "CORREGIBLE", "NO_CONVERGIO", "Piso con 25 kPa", "Mejora (kPa)"]
    fl = [[a.centro, float(a.x_b), "-" if pd.isna(a.nivel_inferior_malla) else float(a.nivel_inferior_malla), float(a.piso_malla), int(a.n_puntos), int(a.n_kalina),
           int(a.n_corregible), int(a.n_no_convergio), float(a.piso_refinado), float(a.mejora_kpa)] for a in p.itertuples()]
    _, f, _ = tabla(ws, f, cab, fl, anchos=[10, 8, 16, 14, 9, 9, 12, 14, 14, 12])
    f += 1
    f = subtitulo(ws, f + 1, "2. Reintento de NO_CONVERGIO con mayor presupuesto")
    tab = r.groupby(["grupo", "clase_nueva"]).size().unstack(fill_value=0)
    cols = [c for c in ("NO_CONVERGIO", "KALINA", "CORREGIBLE", "INVIABLE", "ERROR_MOTOR") if c in tab.columns]
    fl = [[g, int(tab.loc[g].sum())] + [int(tab.loc[g].get(c, 0)) for c in cols] for g in tab.index]
    _, f, _ = tabla(ws, f, ["Grupo", "Puntos"] + ["Ahora " + c for c in cols], fl, anchos=[14, 10] + [16] * len(cols))
    f += 1
    f = nota(ws, f, "Grupo 'lento': NO_CONVERGIO originales que agotaron el presupuesto (250 s o mas). Grupo 'control': NO_CONVERGIO originales rapidos (menos de 100 s); "
                    "sirve para comprobar que el motor es determinista.")
    c = r[r["clase_nueva"] == "NO_CONVERGIO"]["causa_nueva"].fillna("")
    causas = [("Sin dos extremos evaluables en el bracket de T1", int(c.str.startswith("sin dos extremos").sum())),
              ("Balance global de energia que no cierra (N2)", int(c.str.startswith("N2").sum())),
              ("Lazo interior frio sin convergencia", int(c.str.startswith("lazo interior").sum()))]
    causas.append(("Otras (sin cambio de signo, punto interior no evaluable)", int(len(c)) - sum(v for _, v in causas)))
    f += 1
    f = bloque(ws, f, titulo="Causa de los NO_CONVERGIO que siguen sin converger", encabezados=["Causa", "Puntos"], filas=[[a, b] for a, b in causas],
               x="Causa", y="Puntos (n)", horizontal=True, nota_txt="Fuente: p6_reintento_nc.csv (columna causa_nueva). Los 2 puntos con error de rango de propiedades del motor no se cuentan aqui.")
    descripcion(ws, f + 1, ["Pisos de P_baja con resolucion de 25 kPa y reintento de los NO_CONVERGIO con mayor presupuesto.",
                            "Sirve para afinar el piso de cavitacion y comprobar si los NO_CONVERGIO eran solo falta de tiempo."])
    return ws


def hoja_sim(wb, datos):
    t = pd.read_csv(os.path.join(F1, "p6_sim.csv"))
    ws = wb.create_sheet("F5 Incertidumbre simetrica")
    f = titulo(ws, 1, "F5 Incertidumbre con eps_cond simetrico (corrida nueva del motor)", ancho=10)
    f = condiciones(ws, f, [
        "Base: LHS de 48 puntos por centro; las nueve variables distintas de eps_cond se perturban como en el escenario A de U1 (tolerancias supuestas, uniformes).",
        "SIM: eps_cond centrado en 0.90 y perturbado +-0.05 (intervalo simetrico 0.85 a 0.95). U1A: eps_cond centrado en el tope 0.95, solo puede bajar.",
        "Los NO_CONVERGIO cuentan como no KALINA. Intervalos de Wilson de 95 %.",
        "Fuente: resultados/2026-10-18_sens2_B (s2b_sim_filas.csv) y resultados/2026-10-17_sens2_U1 (u1_filas.csv); tabla en p6_sim.csv."])
    f = subtitulo(ws, f, "1. P(KALINA) segun el centro de eps_cond")
    sim, u = t[t["escenario"].str.startswith("SIM")], t[t["escenario"].str.startswith("U1A")]
    fl = [[c, float(sim[sim["centro"] == c]["p_kalina"].iloc[0]), float(u[u["centro"] == c]["p_kalina"].iloc[0])] for c in ("C1", "C2", "C3", "C4")]
    f = bloque(ws, f, titulo="P(KALINA) con eps_cond centrado en 0.90 (simetrico) y en 0.95 (solo hacia abajo)",
               encabezados=["Bloque", "SIM: centro 0.90 +-0.05", "U1A: centro 0.95 hacia abajo"], filas=fl, x="Bloque", y="P(KALINA)",
               nota_txt="Fuente: p6_sim.csv. La probabilidad cambia con el centro de eps_cond: es el resultado de un escenario, no una propiedad del ciclo.")
    cab = ["Bloque", "Escenario", "n", "KALINA", "P(KALINA)", "IC 95 % inferior", "IC 95 % superior", "CORREGIBLE", "INVIABLE", "NO_CONVERGIO"]
    fl = [[r.centro, r.escenario, int(r.n), int(r.n_kalina), float(r.p_kalina), float(r.ic_lo), float(r.ic_hi), int(r.n_corregible), int(r.n_inviable),
           int(r.n_no_convergio)] for r in t.itertuples()]
    _, f, _ = tabla(ws, f, cab, fl, anchos=[8, 36, 6, 9, 11, 14, 14, 13, 10, 14])
    descripcion(ws, f + 2, ["P(KALINA) con eps_cond perturbado de forma simetrica frente a la perturbacion solo hacia abajo de U1.",
                            "Sirve para no leer la probabilidad de U1 como un riesgo del ciclo."])
    return ws


HOJAS_FB = [hoja_pisos_reintento]
HOJAS_FB_SIM = [hoja_sim]
