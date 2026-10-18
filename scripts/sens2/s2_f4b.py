# -*- coding: utf-8 -*-
"""Sens2 - s2_f4b: hojas `F4 Regenerador y condensador` y `F4 Preseleccion` (de P4 y Etapa 0)."""
import os
import sys
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from x2_formato import condiciones, descripcion, nota, subtitulo, tabla, titulo  # noqa: E402
from x5_graficos import bloque  # noqa: E402
from s2_comun import numero  # noqa: E402
import pandas as pd  # noqa: E402
from p4_comun import CANT_DEP as DEP  # noqa: E402
from s2_f4 import (BLQ, TOP, TOT, UNIDAD, grafico_rango, nan, tabla_dependencias,  # noqa: E402
                   tabla_rangos)

REGEN = ["pinch_reg", "LMTD_reg", "UA_reg", "qreg_qi"]
COND = ["Qout_mb", "aprox_cond_sal", "aprox_cond_ent"]
HRVG = ["Qi_mb", "aprox_fuente"]
BOMBA = ["Wp_mb", "Wp_Wt"]
P4_RES = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P4", "p4_resumen.md")
EQUIPOS = [("Turbina", ["rp", "dh_turb", "Wt_mb", "q4"], "q4 >= 0.90 (O1)",
            "Radial-inflow para EPR < 10; EPR tipico 1.997 a 7.95; titulo de salida >= 0.90 [54][33][57]"),
           ("Regenerador", ["pinch_reg", "UA_reg", "qreg_qi"], "Sin cruce de temperaturas (pinch > 0)",
            "Pinch de 4 a 5 K en la literatura; metodo de efectividad o LMTD [30][33][35]"),
           ("Condensador", ["Qout_mb", "aprox_cond_sal"], "Cavitacion en la bomba (O2)",
            "Acercamiento de 4.5 K y 5 K de subenfriamiento; LMTD o e-NTU [30][59][58]"),
           ("HRVG", ["Qi_mb", "aprox_fuente"], "Temperatura de la fuente",
            "El pinch del HRVG se ubica en la evaporacion [30]"),
           ("Bomba", ["Wp_mb", "Wp_Wt"], "Margen de cavitacion (O2)",
            "NPSHA/NPSHR de 1.1 a 2.5 [62][63]")]


def hoja_f4_regen(wb, datos):
    ws = wb.create_sheet("F4 Regenerador y condensador")
    n = len(datos["dataset_dedup"])
    f = titulo(ws, 1, "F4 Regenerador, condensador, HRVG y bomba", ancho=10)
    f = condiciones(ws, f, ["Base: %d puntos sin duplicados; KALINA (total) con eta valida." % n,
                            "Regenerador en contraflujo: lado caliente 5 a 6 y lado frio 10 a 1. Cantidades por kg/s de m_b.",
                            "Los acercamientos del condensador y de la fuente son diferencias de temperatura, no un pinch de diseno.",
                            "Fuente: p4_envolventes.csv, p4_restricciones.csv, p4_dependencias.csv."])
    for nombre, qs in (("1. Regenerador", REGEN), ("2. Condensador", COND), ("3. HRVG", HRVG), ("4. Bomba", BOMBA)):
        f = subtitulo(ws, f, nombre + " (todos los bloques)")
        f, _ = tabla_rangos(ws, f, datos, qs)
    f = grafico_rango(ws, f, datos, "pinch_reg", "Fuente: p4_envolventes.csv. Sin cruces en ningun KALINA.")
    f = grafico_rango(ws, f, datos, "UA_reg", "Fuente: p4_envolventes.csv. UA = Q_reg/LMTD, contraflujo puro.")
    f = grafico_rango(ws, f, datos, "Qout_mb", "Fuente: p4_envolventes.csv.")
    f = subtitulo(ws, f, "5. Restricciones activas: KALINA frente a CORREGIBLE")
    r = datos["restricciones"]
    filas = []
    for _, x in r.iterrows():
        filas.append([x["centro"], x["grupo"], int(x["n"]), numero(x["frac_q4_lt_090"]), numero(x["frac_pinch_le0"]),
                      numero(x["pinch_p5"]), numero(x["pinch_p50"]), numero(x["pinch_p95"]),
                      "referencia" if nan(x["frac_T9_sub_med"]) else numero(x["frac_T9_sub_med"])])
    _, f, _ = tabla(ws, f, ["Bloque", "Grupo", "n", "Fraccion q4 < 0.90", "Fraccion con cruce", "Pinch P5 (K)",
                            "Pinch mediana (K)", "Pinch P95 (K)", "Fraccion con T9 - T_sumidero bajo la mediana KALINA"],
                    filas, anchos=[28, 16, 8, 12, 12, 12, 12, 12, 22])
    f += 1
    for col, y in (("frac_q4_lt_090", "Fraccion con q4 < 0.90"), ("pinch_p50", "Pinch mediana (K)")):
        fl = []
        for b in BLQ + ["todos"]:
            a = r[(r["centro"] == b) & (r["grupo"] == "KALINA (total)")].iloc[0]
            c = r[(r["centro"] == b) & (r["grupo"] == "CORREGIBLE")].iloc[0]
            fl.append([b, numero(a[col]), numero(c[col])])
        f = bloque(ws, f, titulo="%s: KALINA frente a CORREGIBLE" % y,
                   encabezados=["Bloque", "KALINA (total)", "CORREGIBLE"], filas=fl, x="Bloque", y=y,
                   nota_txt="Fuente: p4_restricciones.csv.")
    f = subtitulo(ws, f, "6. Variable de entrada mas asociada con cada cantidad")
    f = tabla_dependencias(ws, f, datos, ["UA_reg", "pinch_reg", "qreg_qi", "Qout_mb", "aprox_cond_sal",
                                          "Qi_mb", "Wp_Wt"])
    descripcion(ws, f, ["Requisitos del regenerador, el condensador, el HRVG y la bomba.",
                        "LMTD y UA se reconstruyen de los estados del ciclo; el modelo usa efectividad."])
    return ws


def _fijan(datos, qs):
    d = datos["dependencias"]
    d = d[(d["tipo"] == "spearman") & (d["centro"].isin(BLQ)) & (d["cantidad"].isin(qs))]
    d = d.assign(_a=d["estadistico"].abs()).dropna(subset=["_a"])
    top = [d[(d["cantidad"] == q) & (d["centro"] == b)].sort_values("_a").iloc[-1]["variable"]
           for q in qs for b in BLQ if len(d[(d["cantidad"] == q) & (d["centro"] == b)])]
    return ", ".join(v for v, _ in Counter(top).most_common(2))


def hoja_f4_presel(wb, datos):
    ws = wb.create_sheet("F4 Preseleccion")
    e = datos["envolventes"]
    e = e[e["centro"] == "todos"]
    f = titulo(ws, 1, "F4 Preseleccion de equipos", ancho=10)
    f = condiciones(ws, f, ["Rango a cubrir = P5 a P95 de KALINA (total) y del 10 % de mayor eta (todos los bloques).",
                            "Variable que lo fija = la de mayor |Spearman| mas frecuente entre los 4 bloques.",
                            "Referencia: docs/ETAPA0_INVESTIGACION_SENSIBILIDAD_KALINA.md, seccion 5 (numeros de fuente entre corchetes).",
                            "Fuente: p4_envolventes.csv y p4_dependencias.csv."])
    filas = []
    for equipo, qs, restr, ref in EQUIPOS:
        for q in qs:
            a = e[(e["cantidad"] == q) & (e["conjunto"] == TOT)].iloc[0]
            b = e[(e["cantidad"] == q) & (e["conjunto"] == TOP)].iloc[0]
            filas.append([equipo, UNIDAD[q], "%s a %s" % (numero(a["p5"], 3), numero(a["p95"], 3)),
                          "%s a %s" % (numero(b["p5"], 3), numero(b["p95"], 3)), _fijan(datos, [q]), restr, ref])
    f = subtitulo(ws, f, "1. Lo que debe cubrir cada equipo")
    _, f, _ = tabla(ws, f, ["Equipo", "Cantidad", "Rango P5 a P95 (KALINA total)", "Rango P5 a P95 (10 % superior)",
                            "Variable que lo fija", "Restriccion activa", "Referencia de la literatura"],
                    filas, anchos=[14, 30, 20, 20, 24, 30, 60])
    f += 1
    eq = pd.read_csv(os.path.join(RAIZ, "resultados", "2026-10-18_sens2_F1", "p6_equipos_diseno.csv"))
    eq = eq[(eq["ambito"] == "todos") & eq["conjunto"].isin(["b_solo_LHS", "c_peso_igual"]) & eq["cantidad"].isin(DEP)]
    cants = [q for q in DEP if q in set(eq["cantidad"])]
    des = {c: {x["conjunto"]: x["desplazamiento"] for _, x in g.iterrows()} for c, g in eq.groupby("cantidad")}
    f = bloque(ws, f, titulo="Cuanto se corre la mediana de cada requisito si cambia el diseno de muestreo (fraccion del ancho P5-P95)",
               encabezados=["Cantidad", "Solo muestreo LHS", "Peso igual por centro y estudio"],
               filas=[[q, numero(des[q].get("b_solo_LHS"), 3), numero(des[q].get("c_peso_igual"), 3)] for q in cants],
               x="Cantidad de equipo", y="Desplazamiento de la mediana (-)",
               nota_txt="Fuente: p6_equipos_diseno.csv, KALINA (total) de todos los bloques. Un valor mayor que 0.15 en valor absoluto indica que la "
                        "envolvente depende del diseno de muestreo y debe citarse con esa precision.")
    f = subtitulo(ws, f, "2. Limites de la preseleccion")
    with open(P4_RES, encoding="utf-8") as fh:
        txt = fh.read().split("## Limites de este analisis", 1)[1]
    for linea in [l[2:].replace("`", "") for l in txt.splitlines() if l.startswith("- ")]:
        ws.cell(f, 1, linea)
        f += 1
    descripcion(ws, f + 1, ["Requisitos de turbina, regenerador, condensador, HRVG y bomba para preseleccionar.",
                            "Son envolventes de un muestreo numerico, no especificaciones de compra."])
    return ws


HOJAS_F4B = [hoja_f4_regen, hoja_f4_presel]
