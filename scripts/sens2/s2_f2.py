# -*- coding: utf-8 -*-
"""Sens2 - s2_f2: hojas `F2 CORREGIBLE vs KALINA` y `F2 Distancia y rescate` (fase C, de P2)."""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from x2_formato import condiciones, descripcion, nota, subtitulo, tabla, titulo  # noqa: E402
from x5_graficos import bloque  # noqa: E402
from s2_comun import numero  # noqa: E402

BASE_F2 = "Base: 3663 puntos sin duplicados exactos; eta y potencias solo donde el punto convergio."
BLOQUES = ["C1 Husavik", "C2 ancla A*", "C3 caliente 150 C", "C4 frio 110 C",
           "Sin centro (muestreo o malla)", "todos"]
VAR_TXT = {"eta_pct": "eta (%)", "wnet_mb": "W_net/m_b (kW/kg/s)", "rp": "r_P (-)",
           "qreg_qi": "Q_reg/Q_i (-)", "dh_turb": "dh_turb (kJ/kg)", "q4": "q4 (-)"}


def _extra(txt):
    d = {}
    for kv in str(txt).split(";"):
        if "=" in kv:
            k, v = kv.split("=", 1)
            d[k.strip()] = v.strip()
    return d


def hoja_f2_comparacion(wb, datos):
    ws = wb.create_sheet("F2 CORREGIBLE vs KALINA")
    c = datos["comparacion"]
    c = c[(c["ambito"] == "todos los puntos") & (c["ref"] == "KALINA (total)")]
    f = 1
    f = titulo(ws, f, "F2 CORREGIBLE vs KALINA (total)", ancho=10)

    f = subtitulo(ws, f, "1. Comparacion CORREGIBLE frente a KALINA (total)")
    f = condiciones(ws, f, [BASE_F2, "Que se compara: los 968 CORREGIBLE frente a los 2047 KALINA (total).",
                            "Que quedo fijo: el conjunto de puntos de Sensibilidad 1 sin duplicados.",
                            "Fuente: p2_comparacion.csv (ambito todos los puntos)."])
    o = {b: i for i, b in enumerate(BLOQUES)}
    cc = c.assign(_o=c["centro"].map(o)).sort_values(["_o", "variable"])
    filas = [[x["centro"], x["variable"], int(x["n_cor"]), int(x["n_kal"]),
              numero(x["med_cor"]), numero(x["p10_cor"]), numero(x["p90_cor"]),
              numero(x["med_kal"]), numero(x["p10_kal"]), numero(x["p90_kal"]),
              numero(x["dif_mediana"]), numero(x["ic_lo"]), numero(x["ic_hi"]),
              numero(x["ks"]), numero(x["ks_p"], 8)] for _, x in cc.iterrows()]
    _, f, _ = tabla(ws, f, ["Bloque", "Variable", "n CORREGIBLE", "n KALINA", "mediana CORREGIBLE",
                            "P10 CORREGIBLE", "P90 CORREGIBLE", "mediana KALINA", "P10 KALINA",
                            "P90 KALINA", "diferencia", "IC 95% bajo", "IC 95% alto", "KS", "p"],
                    filas, anchos=[22, 10, 11, 9, 12, 11, 11, 11, 10, 10, 10, 10, 10, 9, 10])
    cl = datos["comparacion"]
    cl = cl[(cl["ambito"] == "LHS (estudios 3 y 14)") & (cl["ref"] == "KALINA (total)")
            & (cl["centro"] == "todos")]
    txt = "; ".join("%s: %+.2f, IC 95 %% [%+.2f, %+.2f]" % (VAR_TXT[r["variable"]], r["dif_mediana"],
                                                         r["ic_lo"], r["ic_hi"])
                    for _, r in cl.iterrows() if r["variable"] in ("eta_pct", "wnet_mb"))
    f = nota(ws, f, "Los p-valores y los IC de esta tabla suponen puntos independientes; los barridos y mallas no lo "
                    "son. Version mas defendible, solo muestreo LHS (diferencia de medianas CORREGIBLE - KALINA): "
                    + txt + ". Fuente: p2_comparacion.csv (ambito LHS).")
    f += 1

    for var in ("eta_pct", "wnet_mb"):
        filas = []
        for b in BLOQUES:
            s = c[(c["centro"] == b) & (c["variable"] == var)]
            filas.append([b, numero(s.iloc[0]["med_cor"]), numero(s.iloc[0]["med_kal"])])
        f = bloque(ws, f, titulo="Mediana de %s: CORREGIBLE frente a KALINA (total)" % VAR_TXT[var],
                   encabezados=["Bloque", "CORREGIBLE", "KALINA (total)"], filas=filas, x="Bloque",
                   y=VAR_TXT[var], nota_txt="Fuente: p2_comparacion.csv (medianas por bloque).")

    f = subtitulo(ws, f, "2. Violacion dominante por bloque")
    f = condiciones(ws, f, [BASE_F2, "Que se barrio: los CORREGIBLE de cada bloque.",
                            "Fuente: p2_violaciones.csv (seccion dominante)."])
    v = datos["violaciones"]
    vd = v[v["seccion"] == "dominante"]
    filas = []
    for b in BLOQUES:
        s = vd[vd["centro"] == b]
        filas.append([b, numero(s[s["clave"] == "viol_O1"].iloc[0]["fraccion"]),
                      numero(s[s["clave"] == "viol_O2"].iloc[0]["fraccion"])])
    f = bloque(ws, f, titulo="Fraccion de CORREGIBLE por violacion dominante y bloque",
               encabezados=["Bloque", "viol_O1", "viol_O2"], filas=filas, x="Bloque",
               y="Fraccion de CORREGIBLE", tipo="barras", apiladas=True,
               nota_txt="Fuente: p2_violaciones.csv. Cada barra suma 1 (la violacion dominante de "
                        "cada CORREGIBLE).")

    f = subtitulo(ws, f, "3. D por cuartil")
    f = condiciones(ws, f, [BASE_F2, "Que se barrio: los CORREGIBLE ordenados por D en 4 cuartiles.",
                            "Fuente: p2_violaciones.csv (seccion cruce)."])
    cr = v[(v["seccion"] == "cruce") & (v["clave"] == "viol_O2")]
    filas = []
    for q in ("Q1", "Q2", "Q3", "Q4"):
        fila = [q]
        for b in BLOQUES:
            s = cr[(cr["centro"] == b) & (cr["subclave"] == q)]
            fila.append(numero(s.iloc[0]["fraccion"]) if len(s) else None)
        filas.append(fila)
    _, f, _ = tabla(ws, f, ["Cuartil de D"] + BLOQUES, filas, anchos=[12] + [16] * len(BLOQUES))
    f = nota(ws, f, "Se muestra la fraccion de viol_O2 (dominante en los 4 cuartiles) dentro de cada "
                    "cuartil de D; Q1 reune los CORREGIBLE con D mas bajo.")
    f = descripcion(ws, f, ["Comparacion CORREGIBLE frente a KALINA (total), violacion dominante y D "
                            "por cuartil. Los numeros salen de p2_comparacion.csv y "
                            "p2_violaciones.csv."])
    return ws


def hoja_f2_distancia(wb, datos):
    ws = wb.create_sheet("F2 Distancia y rescate")
    d = datos["distancia_resumen"]
    f = 1
    f = titulo(ws, f, "F2 Distancia y rescate", ancho=10)

    f = subtitulo(ws, f, "1. Que variable rescata a un CORREGIBLE (rescate univariado)")
    f = condiciones(ws, f, [BASE_F2, "Que se barrio: corregir una sola variable de cada CORREGIBLE.",
                            "Fuente: p2_distancia_resumen.csv (seccion univariado, centro todos)."])
    u = d[(d["seccion"] == "univariado") & (d["centro"] == "todos")]
    filas = [[x["clave"], x["subclave"], int(x["n"]), numero(x["valor"])] for _, x in u.iterrows()]
    _, f, _ = tabla(ws, f, ["Variable", "Direccion", "n", "Fraccion de CORREGIBLE"], filas,
                    anchos=[12, 10, 8, 20])
    f += 1
    filas = [[x["clave"] + " " + x["subclave"], numero(x["valor"])] for _, x in u.iterrows()]
    f = bloque(ws, f, titulo="Fraccion de CORREGIBLE rescatada por una sola variable",
               encabezados=["Variable y direccion", "Fraccion de CORREGIBLE"], filas=filas,
               x="Variable y direccion", y="Fraccion de CORREGIBLE",
               nota_txt="Fuente: p2_distancia_resumen.csv. Fraccion de los 968 CORREGIBLE que "
                        "quedan a una sola variable de un KALINA.")

    f = subtitulo(ws, f, "2. Distribucion de la distancia L1 y del numero de variables distintas")
    f = condiciones(ws, f, [BASE_F2, "Que se barrio: los CORREGIBLE de cada bloque.",
                            "Fuente: p2_distancia_resumen.csv (seccion distribucion)."])
    dd = d[d["seccion"] == "distribucion"]
    filas = []
    for b in BLOQUES[:-1]:
        l1 = dd[(dd["centro"] == b) & (dd["clave"] == "l1")].iloc[0]
        nv = dd[(dd["centro"] == b) & (dd["clave"] == "nvars")].iloc[0]
        filas.append([b, numero(l1["p10"]), numero(l1["mediana"]), numero(l1["p90"]),
                      numero(nv["p10"]), numero(nv["mediana"]), numero(nv["p90"])])
    _, f, _ = tabla(ws, f, ["Bloque", "L1 P10", "L1 mediana", "L1 P90", "nvars P10", "nvars mediana",
                            "nvars P90"], filas, anchos=[22] + [11] * 6)
    f += 1
    filas = [[ff[0], ff[1], ff[2], ff[3]] for ff in filas]
    f = bloque(ws, f, titulo="Distancia L1 al KALINA mas cercano, por bloque",
               encabezados=["Bloque", "L1 P10", "L1 mediana", "L1 P90"], filas=filas, x="Bloque",
               y="Distancia L1 (normalizada)", nota_txt="Fuente: p2_distancia_resumen.csv.")

    f = subtitulo(ws, f, "3. Cambio de eta al rescatar")
    f = condiciones(ws, f, [BASE_F2, "Que se barrio: llevar cada CORREGIBLE a su KALINA vecino.",
                            "Fuente: p2_distancia_resumen.csv (seccion eta)."])
    e = d[(d["seccion"] == "eta") & (d["clave"] == "eta_vecino_minus_cor")]
    filas = []
    for b in BLOQUES[:-1]:
        s = e[e["centro"] == b].iloc[0]
        x = _extra(s["extra"])
        filas.append([b, int(s["n"]), numero(s["mediana"]), numero(s["valor"]),
                      numero(x.get("ic_lo"), 4), numero(x.get("ic_hi"), 4)])
    _, f, _ = tabla(ws, f, ["Bloque", "n", "mediana (eta vecino - eta CORREGIBLE)", "valor",
                            "IC 95% bajo", "IC 95% alto"], filas, anchos=[22, 8, 30, 10, 11, 11])
    f += 1

    f = subtitulo(ws, f, "4. Robustez: el 10 % de mayor eta frente al resto")
    f = condiciones(ws, f, [BASE_F2, "Que se barrio: el 10 % de mayor eta de cada bloque frente al resto.",
                            "Fuente: p2_robustez.csv (seccion comparacion)."])
    rb = datos["robustez"]
    cmp_ = rb[rb["seccion"] == "comparacion"]
    filas = []
    for b in BLOQUES:
        s = cmp_[cmp_["centro"] == b]
        if not len(s):
            continue
        x = _extra(s.iloc[0]["txt"])
        filas.append([b, numero(x.get("med_top"), 4), numero(x.get("med_resto"), 4),
                      numero(s.iloc[0]["valor"], 4), numero(x.get("ks_p"), 8),
                      int(float(x.get("n_top", 0))), int(float(x.get("n_resto", 0)))])
    _, f, _ = tabla(ws, f, ["Bloque", "dist mediana Top 10%", "dist mediana resto", "KS", "p",
                            "n Top 10%", "n resto"], filas, anchos=[22] + [13] * 5 + [9])
    f += 1
    filas = [[x[0], x[1], x[2]] for x in filas]
    f = bloque(ws, f, titulo="Distancia a la frontera: el 10 % de mayor eta frente al resto",
               encabezados=["Bloque", "Top 10% de eta", "Resto"], filas=filas, x="Bloque",
               y="Distancia a la frontera (mediana)",
               nota_txt="Fuente: p2_robustez.csv. KS y p comparan las dos distribuciones de "
                        "distancia.")
    f += 1

    f = subtitulo(ws, f, "5. Top-10 de eta por bloque")
    f = condiciones(ws, f, [BASE_F2, "Que se lista: los 10 puntos de mayor eta de cada bloque y del total.",
                            "Fuente: p2_robustez.csv (seccion top10_eta)."])
    t10 = rb[rb["seccion"] == "top10_eta"]
    filas = []
    for b in BLOQUES:
        s = t10[t10["centro"] == b].sort_values("valor", ascending=False)
        for _, x in s.iterrows():
            d2 = _extra(x["txt"])
            filas.append([b, int(float(x["subclave"])), d2.get("id"), numero(x["valor"], 4),
                          numero(d2.get("dist"), 4), d2.get("rango")])
    _, f, _ = tabla(ws, f, ["Bloque", "Lugar", "Punto", "eta (%)", "Distancia a la frontera",
                            "Rango experimental"], filas, anchos=[22, 7, 18, 10, 16, 30])
    f = descripcion(ws, f, ["Rescate univariado, distribucion de la distancia, cambio de eta al "
                            "rescatar, robustez del optimo y top-10 de eta. Los numeros salen de "
                            "p2_distancia_resumen.csv y p2_robustez.csv."])
    return ws
