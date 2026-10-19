# -*- coding: utf-8 -*-
"""Sens2 - s2_f7c: hoja `F7 Nulo y correccion FDR` (permutaciones y Benjamini-Hochberg de los indices globales)."""
import os
import sys

import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))
sys.path.insert(0, AQUI)
from x2_formato import condiciones, descripcion, nota, subtitulo, tabla, titulo  # noqa: E402
from x5_graficos import bloque  # noqa: E402
from s2_comun import numero  # noqa: E402
import p6_comun as K  # noqa: E402

F1 = os.path.join(RAIZ, "resultados", "2026-10-18_sens2_F1")
CORTO = {"E3 C1 Husavik": "C1", "E3 C2 ancla A*": "C2", "E14 C3 caliente 150 C": "C3", "E14 C4 frio 110 C": "C4"}


def hoja_f7_fdr(wb, datos):
    ws = wb.create_sheet("F7 Nulo y correccion FDR")
    s = pd.read_csv(os.path.join(F1, "p6_indices_fdr.csv"))
    n = pd.read_csv(os.path.join(F1, "p6_nulo_perm.csv"))
    dum = n[n["tipo"] == "dummy"]
    f = titulo(ws, 1, "F7 Nulo por permutacion y correccion de Benjamini-Hochberg de los indices globales", ancho=10)
    f = condiciones(ws, f, [
        "Base: los LHS de los 4 bloques (estudios 3 y 14), respuestas Y1 (KALINA total), Y2 (eta) y Y3 (W_net por kg/s de m_b).",
        "Cada indice (PRCC, SRC, PAWN, delta, HSIC, eta2 y KS en Y1) se compara con 2 000 permutaciones de la respuesta; p-valor = (1 + #nulo >= observado)/(2 001).",
        "Benjamini-Hochberg por bloque y respuesta (q < 0.05). Una variable es 'distinguible' si pasa en al menos 2 metodos. Los metodos no son independientes.",
        "Calibracion: en las 3 variables dummy el %.1f %% de las pruebas da p < 0.05 (esperable: 5 %%)." % (100 * float((dum["p_perm"] < 0.05).mean())),
        "Fuente: resultados/2026-10-18_sens2_F1 (p6_nulo_perm.csv, p6_indices_fdr.csv)."])
    f = subtitulo(ws, f, "1. Variables distinguibles: criterio anterior y correccion")
    ys = sorted(s["respuesta"].unique())
    fl = [[y.split(" ")[0], int(s[s["respuesta"] == y]["distinguible_p3"].fillna(False).astype(bool).sum()),
           int(s[s["respuesta"] == y]["distinguible_fdr"].astype(bool).sum())] for y in ys]
    f = bloque(ws, f, titulo="Variables distinguibles (suma de los 4 bloques) segun el criterio",
               encabezados=["Respuesta", "Criterio anterior (3 dummy)", "Con permutacion y Benjamini-Hochberg"], filas=fl,
               x="Respuesta", y="Variables distinguibles (n)",
               nota_txt="Fuente: p6_indices_fdr.csv. La correccion por multiplicidad reduce las variables marcadas en las tres respuestas.")
    r = n[n["tipo"] == "real"].copy()
    r["q"] = float("nan")
    for _, ix in r.groupby(["bloque", "respuesta"]).groups.items():
        r.loc[ix, "q"] = K.bh(r.loc[ix, "p_perm"])
    cm = r[r["q"] < K.Q].groupby(["bloque", "respuesta", "variable"]).size()
    fl = [[y.split(" ")[0]] + [int((cm[cm.index.get_level_values("respuesta") == y] >= k).sum()) for k in (1, 2, 3)] for y in ys]
    f = bloque(ws, f, titulo="Variables distinguibles segun el numero minimo de metodos que exigimos (suma de los 4 bloques)",
               encabezados=["Respuesta", "Al menos 1 metodo", "Al menos 2 metodos (regla usada)", "Al menos 3 metodos"], filas=fl,
               x="Respuesta", y="Variables distinguibles (n)",
               nota_txt="Fuente: p6_nulo_perm.csv. La exigencia de 2 metodos es una regla propia (los metodos no son independientes y la correccion "
                        "controla cada metodo por separado); el grafico muestra cuanto cambia el resultado si se exige 1 o 3.")
    f = subtitulo(ws, f, "2. Variables que pasan la correccion, por bloque y respuesta")
    filas = []
    for (b, r), g in s.groupby(["bloque", "respuesta"], sort=False):
        v = g[g["distinguible_fdr"].astype(bool)].sort_values("q_min")
        filas.append([CORTO[b], r, int(g["n"].iloc[0]), len(v), ", ".join(v["variable"]) or "ninguna",
                      ", ".join(g[g["distinguible_p3"].fillna(False).astype(bool) & ~g["distinguible_fdr"].astype(bool)]["variable"]) or "-"])
    _, f, _ = tabla(ws, f, ["Bloque", "Respuesta", "n", "Variables (BH)", "Cuales", "Marcadas antes y que ya no pasan"], filas,
                    anchos=[8, 24, 8, 14, 58, 58])
    cal = pd.read_csv(os.path.join(F1, "p6_calibra_regla.csv"))
    f = subtitulo(ws, f + 1, "3. Calibracion de la regla 'distinguible' con las variables dummy")
    a = cal[cal["tabla"] == "A_por_respuesta"]
    fl = [[g, int(x["n_unidades"]), int(x["marcadas"]), "%.1f %%" % (100 * x["fraccion"]), "%.1f a %.1f %%" % (100 * x["ic_lo"], 100 * x["ic_hi"])]
          for g, x in zip(a["grupo"], a.to_dict("records"))]
    _, f, _ = tabla(ws, f, ["Respuesta", "Dummy evaluadas", "Marcadas por la regla", "Fraccion", "IC 95 % (Wilson)"], fl, anchos=[24, 16, 20, 12, 22])
    f += 1
    b = cal[cal["tabla"] == "B_curva_k"]
    fl = [[int(k), "%.1f %%" % (100 * float(b[(b["k"] == k) & (b["grupo"] == "dummy")]["fraccion"].iloc[0])),
           "%.1f %%" % (100 * float(b[(b["k"] == k) & (b["grupo"] == "real")]["fraccion"].iloc[0]))] for k in (1, 2, 3, 4)]
    _, f, _ = tabla(ws, f, ["Metodos exigidos (k)", "Dummy marcadas", "Reales marcadas"], fl, anchos=[24, 16, 20])
    g = cal[cal["tabla"] == "C_global"].iloc[-1]
    f += 1
    f = nota(ws, f, "Familia global: al juntar las pruebas de los 4 bloques y las 3 respuestas, las variables reales distinguibles pasan de %d (correccion por bloque) a %d (una sola familia, "
                    "metodos mezclados) de %d. Solo hay 36 evaluaciones de dummy, asi que la tasa de falsos positivos de la regla es una estimacion gruesa (Fuente: p6_calibra_regla.csv)."
             % (g["reales_bloque"], g["reales_global_mezcla"], g["n_unidades"]))
    f += 1
    f = nota(ws, f, "Caja comun de rangos (comparar magnitudes entre bloques): los 4 LHS tienen 1 a 9 puntos dentro del rango comun de las 9 variables, asi que "
                    "los indices no se comparan en magnitud entre bloques; solo se usan los rangos y las pruebas dentro de cada bloque.")
    descripcion(ws, f + 1, ["Prueba de permutacion y correccion de Benjamini-Hochberg de los indices de sensibilidad global.",
                            "Sirve para decidir que variables se distinguen del ruido sin inflar los falsos positivos."])
    return ws


HOJAS_F7C = [hoja_f7_fdr]
