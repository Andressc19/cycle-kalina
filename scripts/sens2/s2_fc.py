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


HOJAS_FC = [hoja_caudales]
