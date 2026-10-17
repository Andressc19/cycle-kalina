# -*- coding: utf-8 -*-
"""Sens2 - s2_f1: hojas `F1 Existencia` y `F1 Reglas y zonas grises` (fase A, de P1)."""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from x1_cargar import VARIABLES_ORDEN  # noqa: E402
from x2_formato import condiciones, descripcion, nota, subtitulo, tabla, titulo  # noqa: E402
from x5_graficos import bloque  # noqa: E402
from s2_comun import centro_txt, numero, nivel_lo, barras_con_signo, prob_lhs  # noqa: E402

BASE_F1 = "Base: 3921 puntos de Sensibilidad 1, con los duplicados exactos (n mayores que en F2 a F4)."
BLOQUES = ["C1 Husavik", "C2 ancla A*", "C3 caliente 150 C", "C4 frio 110 C"]
EXACTAS = ["eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond"]


def hoja_f1_existencia(wb, datos):
    ws = wb.create_sheet("F1 Existencia")
    r = datos["existencia_rangos"]
    fr = datos["fronteras"]
    f = 1
    f = titulo(ws, f, "F1 Existencia - donde hay KALINA (total)", ancho=10)

    f = subtitulo(ws, f, "1. Rango con KALINA (total) por bloque")
    f = condiciones(ws, f, [BASE_F1, "Que se barrio: los puntos calculados de Sensibilidad 1 (3921 puntos).",
                            "Que quedo fijo: el resto de entradas en el centro de cada bloque.",
                            "Fuente: p1_existencia_rangos.csv."])
    filas = []
    for b in BLOQUES:
        for v in VARIABLES_ORDEN:
            s = r[(r["centro"] == b) & (r["variable"] == v)]
            if len(s):
                x = s.iloc[0]
                filas.append([b, v, int(x["n_puntos"]), int(x["n_kalina"]),
                              numero(x["min_kalina"]), numero(x["max_kalina"]),
                              numero(x["min_todos"]), numero(x["max_todos"])])
    _, f, _ = tabla(ws, f, ["Bloque", "Variable", "n puntos", "n KALINA (total)",
                            "min KALINA (total)", "max KALINA (total)", "min todos", "max todos"],
                    filas, anchos=[20, 12, 9, 9, 12, 12, 11, 11])
    f += 1

    f = subtitulo(ws, f, "2. eps_cond minima con KALINA (total) por bloque")
    filas = []
    for b in BLOQUES:
        s = r[(r["centro"] == b) & (r["variable"] == "eps_cond")]
        filas.append([b, numero(s.iloc[0]["min_kalina"])])
    f = bloque(ws, f, titulo="eps_cond minima con KALINA (total) por bloque",
               encabezados=["Bloque", "eps_cond minima (-)"], filas=filas, x="Bloque",
               y="eps_cond minima (-)", nota_txt="Fuente: p1_existencia_rangos.csv (minimo de "
               "eps_cond entre los KALINA de cada bloque).")

    f = subtitulo(ws, f, "3. Fronteras de los barridos de una variable")
    f = condiciones(ws, f, [BASE_F1, "Que se barrio: una sola variable por bloque (barridos OFAT).",
                            "Que quedo fijo: las demas entradas en el centro del bloque.",
                            "Fuente: p1_fronteras.csv."])
    o = {"C1 Husavik": 0, "C2 ancla A*": 1, "C3 caliente 150 C": 2, "C4 frio 110 C": 3}
    ff = fr.copy()
    ff["_o"] = ff["centro"].map(o).fillna(9)
    ff = ff.sort_values(["_o", "variable"])
    filas = [[x["centro"], x["variable"], x["forma"], x["direccion"],
              numero(x["valor_frontera"]), numero(x["valor_anterior"]), numero(x["valor_siguiente"])]
             for _, x in ff.iterrows()]
    _, f, _ = tabla(ws, f, ["Bloque", "Variable", "Forma", "Direccion", "Valor de la frontera",
                            "Valor anterior", "Valor siguiente"], filas,
                    anchos=[20, 12, 10, 14, 13, 12, 12])
    f += 1
    filas = []
    for b in BLOQUES:
        pb = fr[(fr["centro"] == b) & (fr["variable"] == "P_baja")]
        tf = fr[(fr["centro"] == b) & (fr["variable"] == "T_fuente")]
        inf = tf[tf["direccion"] == "a KALINA"]
        sup = tf[tf["direccion"] == "a no-KALINA"]
        filas.append([b, numero(pb.iloc[0]["valor_frontera"]) if len(pb) else None,
                      numero(inf.iloc[0]["valor_frontera"]) if len(inf) else None,
                      numero(sup.iloc[0]["valor_frontera"]) if len(sup) else None])
    f = bloque(ws, f, titulo="Fronteras de P_baja y de T_fuente (inferior y superior) por bloque",
               encabezados=["Bloque", "P_baja (kPa)", "T_fuente inferior (K)", "T_fuente superior (K)"],
               filas=filas, x="Bloque", y="Valor de la frontera", nota_txt="Fuente: "
               "p1_fronteras.csv. P_baja y T_fuente estan en kPa y K (unidades distintas).")

    f = subtitulo(ws, f, "4. P(KALINA) por nivel de las variables con 14 niveles o menos")
    f = condiciones(ws, f, [BASE_F1, "Que se barrio: el muestreo LHS de 9 variables (estudios 3 y 14).",
                            "Que quedo fijo: nada; en el LHS se mueven 9 variables a la vez.",
                            "Fuente: p1_existencia_prob.csv (muestra = lhs)."])
    f = nota(ws, f, "Advertencia de diseno: la P(KALINA) por nivel depende del diseno. En un barrido "
                    "OFAT el resto de variables esta fijo y el nivel aisla su efecto; en el LHS todas "
                    "se mueven a la vez y el nivel es un promedio sobre las demas. Esta tabla usa el "
                    "LHS (965 puntos, >= 9 variables a la vez en cada punto).")
    p = datos["existencia_prob"]
    sel = p[(p["muestra"] == "lhs") & (p["centro"] == "todos") &
            (p["variable"].isin(EXACTAS) & ~p["nivel"].astype(str).str.startswith("["))].copy()
    sel["_o"] = sel["variable"].map({v: i for i, v in enumerate(EXACTAS)})
    sel["_lo"] = sel["nivel"].map(nivel_lo)
    sel = sel.sort_values(["_o", "_lo"])
    filas = [[x["variable"], x["nivel"], int(x["n"]), numero(x["p_kalina"])] for _, x in sel.iterrows()]
    _, f, _ = tabla(ws, f, ["Variable", "Nivel", "n", "P(KALINA)"], filas, anchos=[12, 14, 9, 11])
    f += 1

    for var in ("x_b", "P_baja"):
        d = prob_lhs(datos, var, BLOQUES)
        n = max(len(d[b]) for b in BLOQUES)
        filas = [[i + 1] + [(d[b][i] if i < len(d[b]) else None) for b in BLOQUES]
                 for i in range(n)]
        filas = [[fila[0]] + [numero(x, 4) for x in fila[1:]] for fila in filas]
        f = bloque(ws, f, titulo="P(KALINA) por banda de %s, por bloque (muestra LHS)" % var,
                   encabezados=["Banda (cuantil 1 a %d)" % n] + BLOQUES, filas=filas,
                   x="Banda (cuantil)", y="P(KALINA)", tipo="linea", x_vals=list(range(1, n + 1)),
                   nota_txt="Fuente: p1_existencia_prob.csv (muestra lhs). Cada bloque tiene sus "
                            "propios 8 cuantiles; la banda 1 es el cuantil mas bajo de cada bloque.")

    f = descripcion(ws, f, ["Rango con KALINA (total), fronteras de los barridos y P(KALINA) por "
                            "nivel. Los numeros salen de p1_existencia_rangos.csv, "
                            "p1_fronteras.csv y p1_existencia_prob.csv."])
    return ws


def hoja_f1_reglas(wb, datos):
    ws = wb.create_sheet("F1 Reglas y zonas grises")
    reg = datos["reglas"]
    f = 1
    f = titulo(ws, f, "F1 Reglas y zonas grises - que separa KALINA de no-KALINA", ancho=10)
    grupos = BLOQUES + ["todos"]

    f = subtitulo(ws, f, "1. Mejores cortes unicos (stump) por bloque")
    f = condiciones(ws, f, [BASE_F1, "Que se barrio: solo los puntos LHS de 9 variables (estudios 3 y 14).",
                            "Que quedo fijo: nada (LHS).", "Fuente: p1_reglas.csv (seccion stump)."])
    st = reg[reg["seccion"] == "stump"]
    st = st[st["centro"].isin(grupos) & (st["orden"] <= 5)]
    o = {g: i for i, g in enumerate(grupos)}
    st = st.assign(_o=st["centro"].map(o)).sort_values(["_o", "orden"])
    filas = [[x["centro"], x["variable"], numero(x["umbral"]), x["direccion"],
              numero(x["ganancia"], 6)] for _, x in st.iterrows()]
    _, f, _ = tabla(ws, f, ["Bloque", "Variable", "Umbral", "Lado KALINA", "Ganancia (Gini)"],
                    filas, anchos=[20, 12, 11, 12, 13])
    f += 1
    filas = []
    for v in VARIABLES_ORDEN:
        s = st[st["variable"] == v]
        filas.append([v] + [(numero(s[s["centro"] == g].sort_values("orden").iloc[0]["ganancia"], 6)
                             if len(s[s["centro"] == g]) else 0.0) for g in grupos])
    f = bloque(ws, f, titulo="Ganancia del mejor corte por variable y bloque",
               encabezados=["Variable"] + grupos, filas=filas, x="Variable", y="Ganancia (Gini)",
               nota_txt="Fuente: p1_reglas.csv (seccion stump). 0 = esa variable no aparece entre "
                        "los 5 mejores cortes del bloque.", ancho=20.0)

    f = subtitulo(ws, f, "2. Coeficientes de la regresion logistica (con signo)")
    f = condiciones(ws, f, [BASE_F1, "Que se barrio: puntos LHS.", "Que quedo fijo: nada (LHS).",
                            "Fuente: p1_reglas.csv (seccion logistica)."])
    lg = reg[reg["seccion"] == "logistica"]
    filas = [[x["centro"], x["termino"], numero(x["coef"]), int(x["signo"]), bool(x["convergio"])]
             for _, x in lg[lg["centro"].isin(grupos)].iterrows()]
    _, f, _ = tabla(ws, f, ["Bloque", "Termino", "Coeficiente", "Signo", "Convergio"], filas,
                    anchos=[20, 14, 12, 8, 10])
    f += 1
    terminos = ["(intercepto)"] + VARIABLES_ORDEN
    filas = []
    for t in terminos:
        fila = [t]
        for g in grupos:
            s = lg[(lg["centro"] == g) & (lg["termino"] == t)]
            fila.append(numero(s.iloc[0]["coef"]) if len(s) else 0.0)
        filas.append(fila)
    f = barras_con_signo(ws, f, ["Termino"] + grupos, filas, titulo="Coeficientes de la logistica "
                          "por bloque (signo incluido)", x="Termino", y="Coeficiente")

    f = subtitulo(ws, f, "3. Reglas del arbol")
    arb = reg[reg["seccion"] == "arbol"]
    filas = [[x["centro"], x["variable"], x["regla"], int(x["n"]), int(x["n_kalina"]),
              numero(x["p_kalina"]), numero(x["pureza"])] for _, x in arb.iterrows()]
    _, f, _ = tabla(ws, f, ["Bloque", "Lado", "Regla", "n", "KALINA en la regla", "p KALINA",
                            "Pureza"], filas, anchos=[18, 12, 38, 7, 13, 10, 9])
    f = nota(ws, f, "p1_reglas.csv solo trae dos reglas de arbol con pureza >= 0.9 y n >= 30, ambas "
                    "del lado no-KALINA (C1 y C4); ningun lado KALINA cumple ese criterio.")
    f += 1

    f = subtitulo(ws, f, "4. Conteo de zonas grises por bloque y violacion dominante")
    f = condiciones(ws, f, [BASE_F1, "Que se barrio: los CORREGIBLE con D en el cuantil 25 % mas bajo.",
                            "Que quedo fijo: el cuartil de D que define la zona gris.",
                            "Fuente: p1_zonas_grises.csv."])
    z = datos["zonas_grises"]
    zz = z.copy()
    zz["_c"] = zz["centro"].map(centro_txt)
    filas = []
    for g in BLOQUES + ["Sin centro (muestreo o malla)"]:
        s = zz[zz["_c"] == g]
        filas.append([g, int((s["dominante"] == "viol_O1").sum()),
                      int((s["dominante"] == "viol_O2").sum())])
    f = bloque(ws, f, titulo="Zonas grises por bloque y violacion dominante",
               encabezados=["Bloque", "viol_O1", "viol_O2"], filas=filas, x="Bloque",
               y="Zonas grises", tipo="barras", apiladas=True,
               nota_txt="Fuente: p1_zonas_grises.csv. Zona gris = CORREGIBLE con D <= cuantil 25 % "
                        "de D entre los CORREGIBLE.")
    f = descripcion(ws, f, ["Cortes unicos, regresion logistica, reglas del arbol y zonas grises. "
                            "Los numeros salen de p1_reglas.csv y p1_zonas_grises.csv."])
    return ws
