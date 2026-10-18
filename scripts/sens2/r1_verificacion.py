# -*- coding: utf-8 -*-
"""Sens2 R1 - Paso 3: verificacion independiente de r1_filtro / r1_contraste.

Una linea OK/FALLA por control, con calculo independiente (no reutiliza las formulas
de los scripts). Devuelve codigo de salida 1 si hay alguna FALLA.
"""
import os
import sys

import numpy as np
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens2"))
SALIDA = os.path.join(RAIZ, "resultados", "2026-10-18_sens2_R1")
LIBRO = os.path.join(RAIZ, "datos", "Excel_kalina_final_final_final.xlsx")

V10 = ["T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "eta_t", "eta_p",
       "eps_hrvg", "eps_reg", "eps_cond"]
VARS5 = ["T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b"]
CENT = {"C1 Husavik": [394.15, 278.15, 3300.0, 690.0, 0.82],
        "C2 ancla A*": [403.0, 300.15, 3000.0, 563.64, 0.50],
        "C3 caliente 150 C": [423.15, 280.5, 3150.0, 950.0, 0.75],
        "C4 frio 110 C": [383.15, 282.5, 3880.0, 910.0, 0.88]}
ESC = {"T_fuente": 230.0, "T_sumidero": 25.15, "P_alta": 7180.0, "P_baja": 1900.0,
       "x_b": 0.65}
LIM = {"T_fuente": (343.15, 573.15), "T_sumidero": (278.0, 303.15), "P_alta": (820.0, 8000.0),
       "P_baja": (100.0, 2000.0), "x_b": (0.30, 0.95), "eta_t": (0.40, 0.95),
       "eta_p": (0.40, 0.95), "eps_hrvg": (0.40, 0.95), "eps_reg": (0.40, 0.95),
       "eps_cond": (0.40, 0.95)}
MALAS = ["confiable", "no citable", "fuera de rango del motor", "indicio", "extrapol"]
c = os.path.join


def _clave(df):
    return df[V10].round(4).astype("float64").apply(
        lambda r: "|".join("%.4f" % x for x in r), axis=1)


def ctrl_cascada(puntos):
    cas = pd.read_csv(c(SALIDA, "r1_cascada.csv"))
    mono = all((cas[k].diff().dropna() <= 0).all() for k in ["n_filas", "n_unicos", "n_kalina"])
    fin = cas["n_filas"].iloc[-1] == len(puntos) == cas["n_unicos"].iloc[-1]
    return mono and fin, "monotona=%s; ultimo paso=%d; r1_puntos=%d" % (
        mono, cas["n_filas"].iloc[-1], len(puntos))


def ctrl_libro(puntos):
    lib = pd.read_excel(LIBRO, sheet_name="Datos").set_index("id_punto")
    f1 = f2 = 0
    for t in puntos.itertuples():
        r = lib.loc[t.id_punto]
        tamb = r["T_amb_diseno"]
        if pd.isna(tamb) or tamb <= r["T_sumidero"] + 1e-6:
            f1 += 1
        if all(LIM[v][0] <= r[v] <= LIM[v][1] for v in V10):
            f2 += 1
    return f1 == len(puntos) and f2 == len(puntos), "piso O2 ok=%d; dominio ok=%d de %d" % (
        f1, f2, len(puntos))


def ctrl_dedup(puntos):
    from s2_cargar import dataset_dedup
    claves = set(_clave(puntos))
    dd = set(_clave(dataset_dedup()))
    return len(claves & dd) == 0, "claves comunes=%d" % len(claves & dd)


def ctrl_centro(puntos):
    mal = 0
    for t in puntos.itertuples():
        d = {k: max(abs(getattr(t, v) - CENT[k][i]) / ESC[v] for i, v in enumerate(VARS5))
             for k in CENT}
        b = min(d, key=d.get)
        if b != t.centro or abs(d[b] - t.dist) > 1e-9:
            mal += 1
    return mal == 0, "filas con centro/dist distinto=%d" % mal


def ctrl_resumen(puntos):
    res = pd.read_csv(c(SALIDA, "r1_resumen.csv"))
    return int(res["n"].sum()) == int(puntos["cerca"].sum()), "suma resumen=%d; cerca=%d" % (
        int(res["n"].sum()), int(puntos["cerca"].sum()))


def _dist_sin(puntos, centro, v):
    vs = VARS5 if v not in VARS5 else [x for x in VARS5 if x != v]
    sub = puntos[puntos["centro"] == centro]
    d = np.max(np.array([np.abs(sub[x] - CENT[centro][VARS5.index(x)]) / ESC[x]
                         for x in vs]).T, axis=1)
    return sub[d <= 0.15]


def _pred(sel, centro, v, forma, direccion, f, fron):
    val = sel[v].to_numpy(float)
    if forma == "ventana":
        pares = sorted(set(fron[(fron["centro"] == centro) & (fron["variable"] == v) &
                                (fron["forma"] == "ventana")]["valor_frontera"]))
        if len(pares) >= 2:
            return (val >= pares[0]) & (val <= pares[-1])
    return val >= f if direccion == "a KALINA" else val < f


def ctrl_fronteras(puntos):
    cont = pd.read_csv(c(SALIDA, "r1_fronteras_contraste.csv"))
    fron = pd.read_csv(c(RAIZ, "resultados", "2026-10-17_sens2_P1", "p1_fronteras.csv"))
    rng = np.random.default_rng(20261018)
    idx = rng.choice(len(cont), size=3, replace=False)
    ok = True
    detalle = []
    for i in idx:
        t = cont.iloc[i]
        sel = _dist_sin(puntos, t["centro"], t["variable"])
        pr = _pred(sel, t["centro"], t["variable"], t["forma"], t["direccion"],
                   t["valor_frontera"], fron)
        real = (sel["clasificacion"] == "KALINA").to_numpy(bool)
        n, ac = len(sel), int((pr == real).sum())
        ok &= (n == t["n"]) and (ac == t["aciertos"])
        detalle.append("%s/%s n=%d/%d ac=%d/%d" % (t["centro"], t["variable"], n, t["n"], ac, t["aciertos"]))
    return ok, "; ".join(detalle)


def ctrl_palabras():
    mal = []
    for f in sorted(os.listdir(SALIDA)):
        if f.endswith(".md") or f.endswith(".csv"):
            txt = open(c(SALIDA, f), encoding="utf-8").read().lower()
            for w in MALAS:
                if w in txt:
                    mal.append("%s:%s" % (f, w))
    return len(mal) == 0, "hallazgos=%s" % (mal if mal else "ninguno")


def main():
    puntos = pd.read_csv(c(SALIDA, "r1_puntos.csv"))
    controles = [("1 cascada", ctrl_cascada(puntos)), ("2 libro viejo", ctrl_libro(puntos)),
                 ("3 sin claves de dedup", ctrl_dedup(puntos)), ("4 centro y dist", ctrl_centro(puntos)),
                 ("5 resumen", ctrl_resumen(puntos)), ("6 fronteras al azar", ctrl_fronteras(puntos)),
                 ("7 palabras prohibidas", ctrl_palabras())]
    fallas = 0
    for nombre, (ok, det) in controles:
        print("%s %s: %s" % ("OK" if ok else "FALLA", nombre, det))
        fallas += 0 if ok else 1
    print("TOTAL: %d controles, %d FALLA" % (len(controles), fallas))
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
