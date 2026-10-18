# -*- coding: utf-8 -*-
"""Sens2 - s2_f3: hoja `F3 Indices globales` (fase B, de P3)."""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from x2_formato import condiciones, descripcion, nota, subtitulo, tabla, titulo  # noqa: E402
from x5_graficos import grafico_sobre_tabla  # noqa: E402
from s2_comun import numero  # noqa: E402

BLOQUES = [("E3 C1 Husavik", "C1 Husavik"), ("E3 C2 ancla A*", "C2 ancla A*"),
           ("E14 C3 caliente 150 C", "C3 caliente 150 C"), ("E14 C4 frio 110 C", "C4 frio 110 C")]
RESP = [("Y1 KALINA (total)", "Y1. Que decide que haya KALINA (total)"),
        ("Y2 eta (%)", "Y2. Que mueve la eficiencia eta (%)"),
        ("Y3 W_net/m_b", "Y3. Que mueve la potencia W_net/m_b"),
        ("Y4 D CORREGIBLE", "Y4. Que reduce D en los CORREGIBLE")]
TOPE = 13  # 9 variables reales + 3 dummy = 12 puestos; importancia = 13 - rango medio
EXPLICA = [
    "Indices calculados sobre el muestreo LHS de cada bloque (estudios 3 y 14), sin mezclar bloques.",
    "PRCC: correlacion parcial de rangos; KS: separa KALINA de no-KALINA; PAWN: distancia entre la CDF de",
    "la salida y la condicionada; delta de Borgonovo: cambio en toda la distribucion; HSIC: dependencia",
    "no lineal; eta^2: varianza entre rebanadas; logistica: coeficiente estandarizado.",
    "Piso de ruido: 3 variables dummy uniformes. Una variable es 'distinguible del ruido' si el limite",
    "inferior del IC 95 % de algun metodo supera el maximo de las dummy. Criterio mas estricto (permutacion y Benjamini-Hochberg): hoja F7 Rigor estadistico.",
    "Rango medio: puesto medio entre metodos (1 = mas importante). Importancia = %d - rango medio." % TOPE,
]


def _filas(rk, bloque, resp):
    s = rk[(rk["bloque"] == bloque) & (rk["respuesta"] == resp)]
    reales = s[s["tipo"] == "real"].sort_values("rango_medio")
    dum = s[s["tipo"] == "dummy"].sort_values("rango_medio").head(1)
    filas = []
    for _, x in reales.iterrows():
        imp = numero(TOPE - x["rango_medio"], 2)
        d = bool(x["distinguible"])
        filas.append([x["variable"], numero(x["rango_medio"], 2), str(x["signo"]),
                      "si" if d else "no", imp if d else 0, 0 if d else imp, 0])
    for _, x in dum.iterrows():
        filas.append(["mejor dummy (ruido)", numero(x["rango_medio"], 2), "-", "-", 0, 0,
                      numero(TOPE - x["rango_medio"], 2)])
    return filas


def hoja_f3_indices(wb, datos):
    ws = wb.create_sheet("F3 Indices globales")
    rk = datos["ranking"]
    n_blq = datos["dataset_dedup"].groupby("estudio").size()
    f = titulo(ws, 1, "F3 Indices globales de sensibilidad", ancho=10)
    f = condiciones(ws, f, ["Base: puntos de muestreo LHS sin duplicados (estudio 3: C1 y C2; estudio 14: C3 y C4)."]
                    + EXPLICA + ["Fuente: p3_ranking.csv y p3_indices.csv."])
    resumen = []
    for resp, texto in RESP:
        f = subtitulo(ws, f, texto)
        for bloque, nombre in BLOQUES:
            filas = _filas(rk, bloque, resp)
            f = subtitulo(ws, f, "%s - %s" % (nombre, resp))
            enc, ult, _ = tabla(ws, f, ["Variable", "Rango medio", "Signo del efecto",
                                        "Distinguible del ruido", "Importancia: distinguible del ruido",
                                        "Importancia: no distinguible del ruido", "Importancia: piso de ruido (dummy)"],
                                filas, anchos=[22, 12, 12, 14, 18, 18, 18])
            reales = [x for x in filas if not x[0].startswith("mejor dummy")]
            dum = [x for x in filas if x[0].startswith("mejor dummy")]
            resumen.append([nombre, resp, sum(1 for x in reales if x[3] == "si"), len(reales),
                            reales[0][0], reales[0][1], dum[0][1] if dum else None])
            if resp != "Y4 D CORREGIBLE":
                f = grafico_sobre_tabla(ws, enc, len(filas), [5, 6, 7], cat_col=1, apiladas=True,
                                        colores=["2E7D32", "B9770E", "7F8C8D"],
                                        titulo="%s: importancia por variable (%s)" % (resp, nombre),
                                        x="Variable", y="Importancia (%d - rango medio; 12 variables)" % TOPE,
                                        nota_txt="Fuente: p3_ranking.csv. Importancia = 13 - rango medio (hay 12 variables en el ranking: 9 reales y 3 dummy; "
                                                 "el rango 1 es el mejor). Barra mas alta = mas importante; verde = supera el piso "
                                                 "de ruido, ambar = no lo supera, gris = mejor dummy. 0 = no aplica a esa serie.")
            else:
                f = nota(ws, ult + 1, "Fuente: p3_ranking.csv (Y4: n pequeno en C4, indicativo).") + 1
    f = subtitulo(ws, f, "Coincidencias y discrepancias entre metodos")
    f = condiciones(ws, f, ["Cuantas de las 9 variables superan el ruido y cual es la primera, por bloque y respuesta.",
                            "Fuente: p3_ranking.csv."])
    _, f, _ = tabla(ws, f, ["Bloque", "Respuesta", "Distinguibles", "de", "Primera variable",
                            "Rango medio 1.a", "Rango mejor dummy"], resumen,
                    anchos=[22, 20, 12, 6, 18, 14, 16])
    descripcion(ws, f, ["Indices globales por bloque, calculados sobre el muestreo LHS ya existente.",
                        "Un indice vale como senal solo si supera el piso de las 3 variables dummy.",
                        "Los datos completos (metodo, valor, IC 95 %) estan en la hoja D5 Datos indices."])
    return ws


HOJAS_F3 = [hoja_f3_indices]
try:
    from s2_f3b import HOJAS_F3B  # noqa: E402
    HOJAS_F3 = HOJAS_F3 + list(HOJAS_F3B)
except ImportError:
    pass
