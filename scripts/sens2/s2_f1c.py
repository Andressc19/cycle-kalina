# -*- coding: utf-8 -*-
"""Sens2 - s2_f1c: hoja `F1 Margenes de operacion` (cuanto puede moverse cada variable desde el centro)."""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))
sys.path.insert(0, AQUI)
from x2_formato import condiciones, descripcion, nota, subtitulo, tabla, titulo  # noqa: E402
from x5_graficos import bloque  # noqa: E402
from s2_calc import BLOQUES, UNI, k_variables, margenes_ofat, num, pares_vecindad  # noqa: E402
from s2_comun import barras_con_signo  # noqa: E402

CORTO = {"C1 Husavik": "C1", "C2 ancla A*": "C2", "C3 caliente 150 C": "C3", "C4 frio 110 C": "C4"}
PARES_TXT = {"B1": "T_fuente x P_baja", "B2": "P_baja x x_b", "B3": "P_alta x P_baja",
             "B4": "eps_cond x T_sumidero", "B5": "eps_reg x eta_t", "B6": "eps_hrvg x T_fuente"}


def _lectura(m):
    """Frases por bloque con las variables que no dejan margen en alguno de los dos sentidos."""
    out = []
    for b in BLOQUES:
        s = m[m["bloque"] == b]
        abajo = [v for v, x in zip(s["variable"], s["marg_abajo"]) if x == 0]
        arriba = [v for v, x in zip(s["variable"], s["marg_arriba"]) if x == 0]
        out.append("%s: sin margen hacia abajo en %s; sin margen hacia arriba en %s."
                   % (CORTO[b], ", ".join(abajo) or "ninguna variable", ", ".join(arriba) or "ninguna variable"))
    return out


def hoja_f1_margenes(wb, datos):
    ws = wb.create_sheet("F1 Margenes de operacion")
    m = margenes_ofat()
    f = titulo(ws, 1, "F1 Margenes de operacion: cuanto se puede mover desde un KALINA", ancho=10)
    f = condiciones(ws, f, [
        "Base: barridos de una variable (estudios 1 y 10), mallas de pares (estudios 2 y 11) y todos los puntos sin duplicados.",
        "Centro de cada bloque = punto KALINA de partida (los cuatro centros son KALINA). Se mueve una variable cada vez.",
        "Margen = hasta el ultimo nivel KALINA contiguo al centro; la frontera real queda entre ese nivel y el primero que no es KALINA.",
        "Margen relativo = (nivel - centro) / (rango probado de esa variable), en %. 0 = el primer paso ya sale de KALINA.",
        "Una barra que llega al extremo del rango probado significa que no se encontro frontera en ese sentido ('extremo del barrido' en la tabla).",
        "Fuente: p1_dataset / CSV de Sensibilidad 1 (x1_cargar) y p2_dataset_dedup.csv."])
    f = subtitulo(ws, f, "1. Mover una variable (resto en el centro)")
    f = nota(ws, f, "Lectura: " + " ".join(_lectura(m)))
    filas = []
    for _, x in m.iterrows():
        filas.append([CORTO[x["bloque"]], x["variable"], x["unidad"], num(x["v0"]), num(x["ult_abajo"]),
                      num(x["prim_no_abajo"]) if x["prim_no_abajo"] is not None else "extremo del barrido",
                      num(x["ult_arriba"]),
                      num(x["prim_no_arriba"]) if x["prim_no_arriba"] is not None else "extremo del barrido",
                      num(x["marg_abajo"], 1), num(x["marg_arriba"], 1)])
    _, f, _ = tabla(ws, f, ["Bloque", "Variable", "Unidad", "Valor del centro", "Ultimo KALINA hacia abajo",
                            "Primer no-KALINA hacia abajo", "Ultimo KALINA hacia arriba",
                            "Primer no-KALINA hacia arriba", "Margen abajo (% del rango)",
                            "Margen arriba (% del rango)"], filas,
                    anchos=[8, 12, 8, 12, 14, 18, 14, 18, 14, 14])
    f += 1
    for b in BLOQUES:
        s = m[m["bloque"] == b]
        fl = [[x["variable"], num(x["marg_abajo"], 1), num(x["marg_arriba"], 1)] for _, x in s.iterrows()]
        f = barras_con_signo(ws, f, ["Variable", "Hacia abajo", "Hacia arriba"], fl,
                             titulo="Margen de operacion desde el centro (%s)" % b, x="Variable",
                             y="Margen (% del rango probado)")
    f = subtitulo(ws, f, "2. Mover dos variables a la vez (mallas de pares 7 x 7)")
    f = condiciones(ws, f, ["KALINA de la malla = celdas con clase KALINA / celdas con dato (NO_CONVERGIO cuenta como no KALINA).",
                            "Vecindad 3 x 3 = la celda del centro y sus ocho vecinas (un paso en cada variable del par)."])
    p = pares_vecindad()
    fl = [[x["par"], PARES_TXT[x["par"]], CORTO[x["bloque"]], int(x["celdas"]), int(x["n_kalina"]),
           num(100.0 * x["n_kalina"] / x["celdas"], 1), "si" if x["centro_kalina"] else "no",
           int(x["vec_celdas"]), int(x["vec_kalina"]), num(100.0 * x["vec_kalina"] / x["vec_celdas"], 1)]
          for _, x in p.iterrows()]
    _, f, _ = tabla(ws, f, ["Par", "Variables", "Bloque", "Celdas", "Celdas KALINA", "% KALINA de la malla",
                            "Centro KALINA", "Celdas vecindad 3 x 3", "KALINA en la vecindad",
                            "% KALINA de la vecindad"], fl, anchos=[6, 24, 8, 9, 10, 14, 10, 14, 14, 14])
    f += 1
    gr = [["%s %s" % (x["par"], CORTO[x["bloque"]]), num(100.0 * x["n_kalina"] / x["celdas"], 1),
           num(100.0 * x["vec_kalina"] / x["vec_celdas"], 1)] for _, x in p.iterrows()]
    f = bloque(ws, f, titulo="Pares de variables: % KALINA en toda la malla y en la vecindad del centro",
               encabezados=["Par y bloque", "% de la malla", "% de la vecindad 3 x 3"], filas=gr,
               x="Par y bloque", y="% de celdas KALINA", nota_txt="Fuente: mallas de pares (estudios 2 y 11). "
               "B4 (eps_cond x T_sumidero) deja pocas celdas KALINA: el condensador manda.", ancho=22.0)
    f = subtitulo(ws, f, "3. Mover varias variables (todos los puntos de cada bloque)")
    f = condiciones(ws, f, ["k = numero de variables (de 10) que difieren del centro. Los diseños no son comparables en tamaño de paso:",
                            "k = 1 son los barridos de una variable sobre todo su rango; k = 7 a 9 es el muestreo LHS. Lectura exploratoria."])
    k = k_variables(datos["dataset_dedup"])
    fl = [[CORTO[x["bloque"]], x["k"], int(x["n"]), int(x["n_kalina"]), num(100.0 * x["p_kalina"], 1)]
          for _, x in k.iterrows()]
    _, f, _ = tabla(ws, f, ["Bloque", "Variables movidas (k)", "Puntos", "KALINA", "% KALINA"], fl,
                    anchos=[8, 20, 9, 9, 10])
    f += 1
    ks = ["1", "2", "7 a 9"]
    piv = [[kk] + [num(100.0 * float(k[(k["bloque"] == b) & (k["k"] == kk)]["p_kalina"].iloc[0]), 1)
                   for b in BLOQUES] for kk in ks]
    f = bloque(ws, f, titulo="% KALINA segun cuantas variables se mueven desde el centro",
               encabezados=["Variables movidas (k)"] + [CORTO[b] for b in BLOQUES], filas=piv,
               x="Variables movidas (k)", y="% de puntos KALINA",
               nota_txt="Fuente: p2_dataset_dedup.csv. Se grafican k = 1, 2 y 7 a 9 (presentes en los 4 bloques); "
                        "k = 3 y 4 a 6 estan en la tabla.")
    descripcion(ws, f, ["Cuanto se puede mover cada variable, de a una y de a dos, desde el centro KALINA de cada bloque.",
                        "Sin margen hacia abajo en eps_cond (el primer paso ya sale de KALINA): %s."
                        % (", ".join(CORTO[x["bloque"]] for _, x in m[(m["variable"] == "eps_cond")
                                                                      & (m["marg_abajo"] == 0)].iterrows()) or "ningun bloque")])
    return ws


HOJAS_F1C = [hoja_f1_margenes]
