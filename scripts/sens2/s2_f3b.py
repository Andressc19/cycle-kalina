# -*- coding: utf-8 -*-
"""Sens2 - s2_f3b: hojas `F3 Interacciones` y `F3 Elasticidades` (fase B, de P3)."""
import math
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from x2_formato import condiciones, descripcion, nota, subtitulo, tabla, titulo  # noqa: E402
from x5_graficos import bloque as bloque_graf, grafico_sobre_tabla  # noqa: E402
from s2_comun import barras_con_signo, numero  # noqa: E402

BLQ = ["C1 Husavik", "C2 ancla A*", "C3 caliente 150 C", "C4 frio 110 C"]
CORTO = {"C1 Husavik": "C1", "C2 ancla A*": "C2", "C3 caliente 150 C": "C3", "C4 frio 110 C": "C4"}
PARES = {"B1": "T_fuente x P_baja", "B2": "P_baja x x_b", "B3": "P_alta x P_baja",
         "B4": "eps_cond x T_sumidero", "B5": "eps_reg x eta_t", "B6": "eps_HRVG x T_fuente"}


def _nan(x):
    return x is None or (isinstance(x, float) and math.isnan(x))


def hoja_f3_interacciones(wb, datos):
    ws = wb.create_sheet("F3 Interacciones")
    it = datos["interaccion"]
    o = {b: i for i, b in enumerate(BLQ)}
    it = it.assign(_o=it["centro"].map(o)).sort_values(["_o", "par"])
    f = titulo(ws, 1, "F3 Interacciones entre pares de variables", ancho=10)
    f = condiciones(ws, f, [
        "Base: mallas de pares 7 x 7 por bloque, contadas por pertenencia a la malla (no por etiqueta).",
        "No aditividad = 1 - R^2 del modelo aditivo (media de fila + media de columna - media global).",
        "Umbrales declarados: menor de 0.05 aditivo; 0.25 o mas, fuerte. Signo: sinergico / antagonico.",
        "C3 y C4 solo tienen los pares B1 a B4. Fuente: p3_interaccion.csv."])
    f = subtitulo(ws, f, "1. No aditividad por par y bloque")
    filas = [[x["par"], PARES[x["par"]], CORTO[x["centro"]], int(x["n_celdas_eta"]),
              numero(x["noadit_eta"]), str(x["clasificacion"]), int(x["n_celdas_ind"]),
              numero(x["noadit_ind"]), str(x["clasificacion_ind"])] for _, x in it.iterrows()]
    _, f, _ = tabla(ws, f, ["Par", "Variables", "Bloque", "Celdas con eta", "No aditividad de eta",
                            "Clase (eta)", "Celdas KALINA", "No aditividad (KALINA)", "Clase (KALINA)"],
                    filas, anchos=[6, 24, 8, 12, 14, 18, 12, 14, 20])
    f += 1
    for col, nom, enc in (("noadit_ind", "indicador KALINA", "No aditividad (KALINA)"),
                          ("noadit_eta", "eficiencia eta", "No aditividad de eta")):
        f = subtitulo(ws, f, "2. No aditividad sobre %s" % nom)
        fl = [["%s %s" % (x["par"], CORTO[x["centro"]]), numero(x[col])]
              for _, x in it.iterrows() if not _nan(x[col])]
        f = bloque_graf(ws, f, titulo="No aditividad (1 - R^2) sobre %s, por par y bloque" % nom,
                        encabezados=["Par y bloque", enc], filas=fl, x="Par y bloque",
                        y="1 - R^2 del modelo aditivo",
                        nota_txt="Fuente: p3_interaccion.csv. Solo los pares con valor definido "
                                 "(B4 en C1 no tiene eta definida).")
    f = nota(ws, f, "Las matrices 7 x 7 de eta y KALINA por par no se incluyen en este libro: "
                    "p3_interaccion.csv guarda solo los indices de cada malla.")
    descripcion(ws, f + 1, ["Interaccion entre pares: cuanto de la respuesta no se explica sumando "
                            "el efecto de cada variable por separado.",
                            "Sobre la existencia de KALINA los pares B2 y B4 interactuan en los cuatro bloques."])
    return ws


def hoja_f3_elasticidades(wb, datos):
    ws = wb.create_sheet("F3 Elasticidades")
    e = datos["elasticidad"]
    f = titulo(ws, 1, "F3 Elasticidades locales de eta en el punto base", ancho=10)
    f = condiciones(ws, f, [
        "Elasticidad = (d eta / eta0) / (d v / v0) con los dos niveles vecinos del punto base (centrada)",
        "si ambos son KALINA; si no, hacia adelante o hacia atras; 'sin KALINA vecino' si ninguno lo es.",
        "Base: barridos de una variable de los estudios 1 y 10; los demas no traen la columna variable.",
        "Fuente: p3_elasticidad.csv."])
    f = subtitulo(ws, f, "1. Elasticidad por variable y bloque")
    vars_ = list(dict.fromkeys(e["variable"]))
    filas, completas = [], []
    for v in vars_:
        fila = [v]
        vals = []
        for b in BLQ:
            s = e[(e["centro"] == b) & (e["variable"] == v)]
            x = s.iloc[0] if len(s) else None
            ok = x is not None and not _nan(x["elasticidad"])
            fila.append(numero(x["elasticidad"], 3) if ok else "sin KALINA vecino")
            vals.append(numero(x["elasticidad"], 3) if ok else None)
        filas.append(fila)
        if all(t is not None for t in vals):
            completas.append([v] + vals)
    _, f, _ = tabla(ws, f, ["Variable"] + [CORTO[b] for b in BLQ], filas, anchos=[14, 18, 18, 18, 18])
    f += 1
    f = subtitulo(ws, f, "2. Grafico (variables con elasticidad en los cuatro bloques)")
    f = barras_con_signo(ws, f, ["Variable"] + [CORTO[b] for b in BLQ], completas,
                         titulo="Elasticidad de eta en el punto base", x="Variable",
                         y="Elasticidad (-)")
    f = nota(ws, f - 2, "T_fuente en C2 da 13.2: el punto base esta sobre una rampa de la frontera "
                        "(un cambio de 5 K mueve eta 16 %). No es un valor de diseno. "
                        "Excluidas del grafico: variables sin KALINA vecino en algun bloque.")
    f = subtitulo(ws, f + 1, "3. Detalle del calculo")
    det = [[CORTO[x["centro"]], x["variable"], numero(x["v0"], 4), numero(x["eta0"], 4),
            numero(x["nivel_menos"], 4), numero(x["nivel_mas"], 4), str(x["tipo"]),
            numero(x["elasticidad"], 3)] for _, x in e.iterrows()]
    _, f, _ = tabla(ws, f, ["Bloque", "Variable", "v0", "eta0 (-)", "Nivel menos", "Nivel mas",
                            "Tipo de diferencia", "Elasticidad"], det,
                    anchos=[8, 14, 10, 10, 11, 11, 20, 12])
    descripcion(ws, f, ["Cuanto cambia eta, en proporcion, por un cambio proporcional de cada variable.",
                        "Valores cercanos a 1 indican respuesta casi proporcional (eta_t, T_fuente en C1)."])
    return ws


HOJAS_F3B = [hoja_f3_interacciones, hoja_f3_elasticidades]
