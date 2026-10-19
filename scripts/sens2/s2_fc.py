# -*- coding: utf-8 -*-
"""Sens2 etapa B - hoja `F4 Caudales y bomba` (todo leido de p6_dens.csv): caudal volumetrico de turbina y altura de bomba por kW neto."""
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
AMB = ["todos", "C1", "C2", "C3", "C4", "resto de estudios"]


def hoja_caudales(wb, datos):
    t = pd.read_csv(os.path.join(F1, "p6_dens.csv"))
    ws = wb.create_sheet("F4 Caudales y bomba")
    f = titulo(ws, 1, "F4 Caudales volumetricos de turbina y bomba por kW neto (corrida nueva del motor)", ancho=10)
    f = condiciones(ws, f, [
        "Base: 150 KALINA dentro del rango experimental (30 por ambito: LHS de C1 a C4 y resto de estudios), elegidos en posiciones equiespaciadas del orden por eta.",
        "Cada punto se volvio a resolver con el motor (m_b = 1 kg/s) y reprodujo su eta original; las densidades salen del modelo teqp en los estados 3, 4 y 9.",
        "Salida de turbina bifasica: volumen especifico = q/rho_vapor + (1 - q)/rho_liquido con las fases del flash a (P_baja, T4).",
        "Fuente: resultados/2026-10-18_sens2_F1 (p6_dens.csv) y resultados/2026-10-18_sens2_B (s2b_dens_filas.csv)."])
    f = subtitulo(ws, f, "1. Envolventes por kW neto (ambito todos)")
    a = t[t["ambito"] == "todos"]
    fl = [[r.descripcion, r.unidad, int(r.n), float(r.p5), float(r.p50), float(r.p95)] for r in a.itertuples()]
    _, f, _ = tabla(ws, f, ["Magnitud", "Unidad", "n", "P5", "P50", "P95"], fl, anchos=[48, 18, 8, 12, 12, 12])
    f += 1
    f = nota(ws, f, "Son envolventes de un muestreo numerico por kW neto, no especificaciones de compra. P5 a P95 de los puntos elegidos, no de toda la campana.")
    g = t[t["magnitud"].isin(["V3_kW", "V4_kW"])]
    fl = [[amb] + [float(g[(g["ambito"] == amb) & (g["magnitud"] == m)]["p50"].iloc[0]) for m in ("V3_kW", "V4_kW")] for amb in AMB if amb in set(g["ambito"])]
    f = bloque(ws, f + 1, titulo="Caudal volumetrico de la turbina por kW neto (mediana por ambito)", encabezados=["Ambito", "Entrada de turbina (L/s por kW)", "Salida de turbina (L/s por kW)"],
               filas=fl, x="Ambito", y="Caudal (L/s por kW neto)", nota_txt="Fuente: p6_dens.csv (P50). La salida es bifasica en todos los puntos; el caudal de salida es mayor que el de entrada.")
    h = t[t["magnitud"] == "H_bomba_m"]
    fl = [[amb, float(h[h["ambito"] == amb]["p50"].iloc[0])] for amb in AMB if amb in set(h["ambito"])]
    f = bloque(ws, f, titulo="Altura de la bomba (mediana por ambito)", encabezados=["Ambito", "Altura de la bomba (m)"], filas=fl,
               x="Ambito", y="Altura (m)", nota_txt="Fuente: p6_dens.csv (P50). Altura = (P_alta - P_baja)/(rho g) con la densidad del liquido a la entrada de la bomba.")
    f = subtitulo(ws, f, "2. Caudal volumetrico de la bomba por kW neto, por ambito")
    v = t[t["magnitud"] == "V9_kW"]
    fl = [[r.ambito, int(r.n), float(r.p5), float(r.p50), float(r.p95)] for r in v.itertuples()]
    _, f, _ = tabla(ws, f, ["Ambito", "n", "P5 (L/s por kW)", "P50 (L/s por kW)", "P95 (L/s por kW)"], fl, anchos=[24, 8, 16, 16, 16])
    descripcion(ws, f + 2, ["Caudales volumetricos de turbina y bomba y altura de bomba por kW neto.",
                            "Sirve para preseleccionar turbina y bomba (pregunta 4 del profesor)."])
    return ws


def hoja_opt(wb, datos):
    t = pd.read_csv(os.path.join(F1, "p6_opt_T.csv"))
    ws = wb.create_sheet("F4 Optimo vs T_fuente")
    f = titulo(ws, 1, "F4 Eta maxima frente a T_fuente con busqueda local (corrida nueva del motor)", ancho=10)
    f = condiciones(ws, f, [
        "Base: 12 bandas de T_fuente (80 a 300 C, cada 20 C); P_alta, P_baja y x_b libres; eta_t 0.85, eta_p 0.80, eps_hrvg 0.85, eps_reg 0.75, eps_cond 0.95 y T_sumidero 280.5 K fijos.",
        "Busqueda coordenada a coordenada con paso inicial 600 kPa, 100 kPa y 0.03; hasta 30 evaluaciones por banda; solo cuentan los puntos KALINA. Es un maximo local, no un optimo global.",
        "Comparacion orientativa: eta maxima del conjunto muestreado (todos los KALINA) en la ventana [T-10, T+10) K, que mezcla eta_t hasta 0.95 y otras T_sumidero. Desde 160 C el punto optimo cae fuera del rango experimental (liquido > 420 K).",
        "Fuente: resultados/2026-10-18_sens2_B (s2b_opt_*.csv) y resultados/2026-10-18_sens2_F1 (p6_opt_T.csv)."])
    f = subtitulo(ws, f, "1. Eta maxima por banda de T_fuente")
    fl = [[float(r.T_fuente_C), float(r.eta_max_pct), float(r.eta_max_muestreo_pct) if pd.notna(r.eta_max_muestreo_pct) else 0.0] for r in t.itertuples()]
    f = bloque(ws, f, titulo="Eta maxima (%) por banda de T_fuente (desde 160 C, fuera del rango experimental)", encabezados=["T_fuente (C)", "Busqueda local (%)", "Maximo muestreado (%)"], filas=fl,
               x="T_fuente (C)", y="Eta maxima (%)", tipo="linea", nota_txt="Fuente: p6_opt_T.csv. Un cero en 'Maximo muestreado' significa que no hay puntos KALINA muestreados en esa banda. "
                                                                          "Desde 160 C el optimo esta fuera del rango experimental.")
    cab = ["T_fuente (C)", "Evaluaciones", "KALINA", "Eta max (%)", "P_alta (kPa)", "P_baja (kPa)", "x_b", "Fuera de rango", "Eta max dentro del rango (%)", "Maximo muestreado (%)", "Mejora (pp)"]
    fl = [[float(r.T_fuente_C), int(r.n_eval), int(r.n_kalina), float(r.eta_max_pct), float(r.P_alta), float(r.P_baja), float(r.x_b), "si" if r.fuera_rango else "no",
           "-" if pd.isna(r.eta_max_dentro_pct) else float(r.eta_max_dentro_pct), "-" if pd.isna(r.eta_max_muestreo_pct) else float(r.eta_max_muestreo_pct),
           "-" if pd.isna(r.mejora_pp) else float(r.mejora_pp)] for r in t.itertuples()]
    _, f, _ = tabla(ws, f, cab, fl, anchos=[12, 12, 8, 11, 12, 12, 8, 13, 18, 17, 11])
    f += 1
    f = nota(ws, f, "A 80 C la busqueda no alcanza el maximo muestreado, que viene de puntos a otra temperatura (ventana de 20 K) y otra configuracion; no se lee como una falla de la busqueda.")
    descripcion(ws, f + 1, ["Eta maxima por banda de T_fuente con busqueda local de P_alta, P_baja y x_b.", "Responde la pregunta 3 del profesor (ciclo frente a temperatura) con datos del motor."])
    return ws


HOJAS_FC = [hoja_caudales, hoja_opt]
