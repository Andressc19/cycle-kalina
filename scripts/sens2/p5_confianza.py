# -*- coding: utf-8 -*-
"""Sens2 - p5_confianza: regla de confianza de las conclusiones, aplicada por codigo.

Cada conclusion tiene una fila en `p5_evidencia.csv` (criterios escritos a mano y versionados, con una nota que los
justifica). La confianza NO se escribe en el texto: se calcula aqui. Columnas de `p5_evidencia.csv`:

- tipo: `recuento` (un conteo directo de los datos), `inferencia` (estimacion, comparacion o ranking),
  `determinista` (cifra de una evaluacion directa del modelo en pocos puntos, como una derivada local, una frontera
  de un barrido o un margen: el tamaño de muestra no aplica, pero la cifra vale solo en esa rebanada) y `limite`
  (declaracion de un limite del analisis).
- lineas: lineas de evidencia independientes (metodos de familias distintas, campañas o muestreos distintos).
- n_min: tamaño de la muestra mas pequeña que sostiene la afirmacion principal.
- robusto_nc: `si`, `no`, `na` (no depende de NO_CONVERGIO) o `pendiente` (aun no comprobado).
- robusto_diseno: `si` (se sostiene solo con LHS y con todos los diseños), `parcial`, `no`, `na` o `pendiente`.
- intervalo: `si` si la cifra principal lleva intervalo o prueba corregida, `na` si no aplica, `no` o `pendiente`.
- un_bloque: `si` si la afirmacion descansa en un solo bloque.

Regla (el orden importa):
  Baja  = (n_min < 10 si el tipo no es determinista), o lineas < 1, o (robusto_diseno = no y lineas < 2), o (robusto_nc = no y un_bloque = si).
  Alta  = tipo recuento o limite con n_min >= 30;  o tipo inferencia con lineas >= 2, n_min >= 30,
          robusto_nc en {si, na}, robusto_diseno en {si, na} e intervalo en {si, na}; o tipo determinista con
          lineas >= 2 y los mismos tres criterios (el intervalo es `na`: la cifra es exacta en su rebanada).
  Media = el resto (cualquier criterio `parcial`, `pendiente` o `no` impide Alta).
"""
import os

import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
EVIDENCIA = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P5", "p5_evidencia.csv")
OK = {"si", "na"}


def regla(x):
    """Devuelve (confianza, explicacion) para una fila de p5_evidencia."""
    razones = []
    if x["n_min"] < 10 and x["tipo"] != "determinista":
        razones.append("n_min < 10")
    if x["lineas"] < 1:
        razones.append("sin linea de evidencia")
    if x["robusto_diseno"] == "no" and x["lineas"] < 2:
        razones.append("depende del diseño con una sola linea")
    if x["robusto_nc"] == "no" and x["un_bloque"] == "si":
        razones.append("cambia al tratar NO_CONVERGIO y descansa en un bloque")
    if razones:
        return "Baja", "; ".join(razones)
    if x["tipo"] in ("recuento", "limite"):
        if x["n_min"] >= 30:
            return "Alta", "%s con n_min = %d" % (x["tipo"], x["n_min"])
        return "Media", "n_min < 30"
    faltan = []
    if x["lineas"] < 2:
        faltan.append("una sola linea de evidencia")
    if x["n_min"] < 30 and x["tipo"] != "determinista":
        faltan.append("n_min < 30")
    for c in ("robusto_nc", "robusto_diseno", "intervalo"):
        if x[c] not in OK:
            faltan.append("%s = %s" % (c, x[c]))
    if not faltan:
        return "Alta", "lineas = %d, n_min = %d, robusta a NO_CONVERGIO y al diseño, con intervalo" % (x["lineas"], x["n_min"])
    return "Media", "; ".join(faltan)


def asignar(base, h=None):
    ev = pd.read_csv(EVIDENCIA).set_index("id")
    faltan = [i for i in base["id"] if i not in ev.index]
    if faltan:
        raise SystemExit("conclusiones sin fila en p5_evidencia.csv: %s" % faltan)
    sal = base.copy()
    res = [regla(ev.loc[i]) for i in sal["id"]]
    sal["confianza"] = [r[0] for r in res]
    sal["criterio_confianza"] = [r[1] for r in res]
    return sal


if __name__ == "__main__":
    ev = pd.read_csv(EVIDENCIA)
    for _, x in ev.iterrows():
        print(x["id"], *regla(x))
