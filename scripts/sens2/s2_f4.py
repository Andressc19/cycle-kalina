# -*- coding: utf-8 -*-
"""Sens2 - s2_f4: hoja `F4 Turbina` (de P4) y utilidades comunes de la fase de equipos."""
import math
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from x2_formato import condiciones, descripcion, nota, subtitulo, tabla, titulo  # noqa: E402
from x5_graficos import bloque, grafico_sobre_tabla  # noqa: E402
from s2_comun import numero  # noqa: E402

TOT = "KALINA (total)"
TOP = "10 % de KALINA (total) con mayor eta"
BLQ = ["C1 Husavik", "C2 ancla A*", "C3 caliente 150 C", "C4 frio 110 C"]
UNIDAD = {"rp": "r_P (-)", "dh_turb": "dh_turb (kJ/kg)", "Wt_mb": "W_t (kW por kg/s)", "q4": "q4 (-)",
          "T3": "T3 (K)", "T4": "T4 (K)", "m_v_mb": "m_v (kg/s por kg/s)",
          "pinch_reg": "pinch regenerador (K)", "LMTD_reg": "LMTD regenerador (K)",
          "UA_reg": "UA regenerador (kW/K por kg/s)", "qreg_qi": "Q_reg/Q_i (-)",
          "Qout_mb": "Q_out (kW por kg/s)", "aprox_cond_sal": "T9 - T_sumidero (K)",
          "aprox_cond_ent": "T8 - T_sumidero (K)", "Qi_mb": "Q_i (kW por kg/s)",
          "aprox_fuente": "T_fuente - T3 (K)", "Wp_mb": "W_p (kW por kg/s)", "Wp_Wt": "W_p/W_t (-)"}
TURBINA = ["rp", "dh_turb", "Wt_mb", "q4", "T3", "T4", "m_v_mb"]


def nan(x):
    return x is None or (isinstance(x, float) and math.isnan(x))


def tabla_rangos(ws, f, datos, cantidades, centro="todos"):
    """Tabla P5/mediana/P95 de KALINA (total) y del 10 % de mayor eta. Devuelve (fila_sig, tabla)."""
    e = datos["envolventes"]
    e = e[e["centro"] == centro]
    filas = []
    for q in cantidades:
        a = e[(e["cantidad"] == q) & (e["conjunto"] == TOT)].iloc[0]
        b = e[(e["cantidad"] == q) & (e["conjunto"] == TOP)].iloc[0]
        filas.append([UNIDAD[q], int(a["n"]), numero(a["p5"]), numero(a["p50"]), numero(a["p95"]),
                      int(b["n"]), numero(b["p5"]), numero(b["p50"]), numero(b["p95"])])
    _, f, _ = tabla(ws, f, ["Cantidad", "n (total)", "P5", "Mediana", "P95", "n (10 % superior)",
                            "P5", "Mediana", "P95"], filas, anchos=[30, 10, 10, 10, 10, 14, 10, 10, 10])
    return f + 1, filas


def grafico_rango(ws, f, datos, q, nota_txt):
    e = datos["envolventes"]
    e = e[(e["centro"] == "todos") & (e["cantidad"] == q)]
    filas = []
    for etq, col in (("P5", "p5"), ("Mediana", "p50"), ("P95", "p95")):
        filas.append([etq, numero(e[e["conjunto"] == TOT].iloc[0][col]),
                      numero(e[e["conjunto"] == TOP].iloc[0][col])])
    return bloque(ws, f, titulo="%s: todo KALINA frente al 10 %% de mayor eta" % UNIDAD[q],
                  encabezados=["Estadistico", "KALINA (total)", "10 % de mayor eta"], filas=filas,
                  x="Estadistico", y=UNIDAD[q], nota_txt=nota_txt)


def tabla_dependencias(ws, f, datos, cantidades):
    d = datos["dependencias"]
    d = d[(d["tipo"] == "spearman") & (d["centro"].isin(BLQ)) & (d["cantidad"].isin(cantidades))]
    d = d.assign(_a=d["estadistico"].abs()).dropna(subset=["_a"])
    filas = []
    for q in cantidades:
        for b in BLQ:
            s = d[(d["cantidad"] == q) & (d["centro"] == b)]
            if len(s):
                x = s.loc[s["_a"].idxmax()]
                filas.append([UNIDAD[q], b, x["variable"], numero(x["estadistico"], 3),
                              numero(x["p_valor"], 6), int(x["n"])])
    _, f, _ = tabla(ws, f, ["Cantidad", "Bloque", "Variable mas asociada", "Spearman", "p", "n"], filas,
                    anchos=[30, 20, 20, 10, 10, 8])
    return f + 1


def hoja_f4_turbina(wb, datos):
    ws = wb.create_sheet("F4 Turbina")
    n = len(datos["dataset_dedup"])
    f = titulo(ws, 1, "F4 Turbina: relacion de presiones, caida de entalpia y titulo de salida", ancho=10)
    f = condiciones(ws, f, ["Base: %d puntos sin duplicados; KALINA (total) con eta valida." % n,
                            "Cantidades por kg/s de m_b. Rango = P5 a P95 de KALINA (total) y del 10 % de mayor eta.",
                            "Fuente: p4_envolventes.csv, p4_bandas.csv, p4_dependencias.csv."])
    f = subtitulo(ws, f, "1. Lo que debe cubrir la turbina (todos los bloques)")
    f, _ = tabla_rangos(ws, f, datos, TURBINA)
    f = grafico_rango(ws, f, datos, "rp", "Fuente: p4_envolventes.csv. Los disenos de mayor eta piden mayor r_P.")
    f = grafico_rango(ws, f, datos, "dh_turb", "Fuente: p4_envolventes.csv.")
    f = subtitulo(ws, f, "2. Mediana por bloque (KALINA total)")
    e = datos["envolventes"]
    filas = []
    for b in BLQ:
        fila = [b]
        for q in TURBINA:
            fila.append(numero(e[(e["centro"] == b) & (e["conjunto"] == TOT) & (e["cantidad"] == q)].iloc[0]["p50"]))
        filas.append(fila)
    _, f, _ = tabla(ws, f, ["Bloque"] + [UNIDAD[q] for q in TURBINA], filas, anchos=[20] + [14] * 7)
    f += 1
    f = subtitulo(ws, f, "3. Bandas de relacion de presiones r_P (todos los bloques)")
    b = datos["bandas"]
    b = b[b["centro"] == "todos"]
    filas = [[x["banda"], int(x["n"]), numero(x["eta_p50"]), numero(x["eta_p10"]), numero(x["eta_p90"]),
              numero(x["dh_p50"]), numero(x["q4_p50"]), numero(x["wt_p50"])] for _, x in b.iterrows()]
    _, f, _ = tabla(ws, f, ["Banda de r_P", "n", "eta mediana (%)", "eta P10 (%)", "eta P90 (%)",
                            "dh_turb mediana (kJ/kg)", "q4 mediana (-)", "W_t mediana (kW por kg/s)"],
                    filas, anchos=[14, 8, 12, 12, 12, 16, 12, 16])
    f += 1
    for col, y in (("eta_p50", "eta mediana (%)"), ("dh_p50", "dh_turb mediana (kJ/kg)")):
        fl = [[x["banda"], numero(x[col])] for _, x in b.iterrows()]
        f = bloque(ws, f, titulo="%s por banda de r_P" % y, encabezados=["Banda de r_P", y], filas=fl,
                   x="Banda de r_P", y=y, nota_txt="Fuente: p4_bandas.csv (todos los bloques).")
    f = subtitulo(ws, f, "4. Regresion dh_turb sobre r_P")
    r = datos["dependencias"]
    r = r[r["tipo"] == "regresion"]
    filas = [[x["centro"], int(x["n"]), numero(x["pendiente"], 3), numero(x["intercepto"], 3), numero(x["r2"], 3)]
             for _, x in r.iterrows()]
    enc, _, _ = tabla(ws, f, ["Bloque", "n", "Pendiente (kJ/kg por unidad de r_P)", "Intercepto (kJ/kg)", "R^2"],
                      filas, anchos=[22, 8, 22, 16, 8])
    f = grafico_sobre_tabla(ws, enc, len(filas), [3], titulo="Pendiente de dh_turb frente a r_P",
                            x="Bloque", y="kJ/kg por unidad de r_P",
                            nota_txt="Fuente: p4_dependencias.csv (muestreo LHS, KALINA total).")
    f = subtitulo(ws, f, "5. Variable de entrada mas asociada con cada cantidad de la turbina")
    f = tabla_dependencias(ws, f, datos, ["rp", "dh_turb", "Wt_mb", "q4"])
    descripcion(ws, f, ["Requisitos de la turbina: relacion de presiones, caida de entalpia y titulo de salida.",
                        "El titulo q4 se mantiene por encima de 0.90 (criterio O1) en todos los KALINA."])
    return ws


HOJAS_F4 = [hoja_f4_turbina]
try:
    from s2_f4b import HOJAS_F4B  # noqa: E402
    HOJAS_F4 = HOJAS_F4 + list(HOJAS_F4B)
except ImportError:
    pass
