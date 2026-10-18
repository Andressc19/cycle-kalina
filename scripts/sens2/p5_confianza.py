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
- robusto_diseno: `si` (se sostiene solo con LHS y con todos los diseños), `acotado`, `parcial`, `no`, `na` o `pendiente`.
  `acotado` = el enunciado de la conclusion limita su alcance a la rebanada o escenario donde se midio (por ejemplo
  "con las demas variables en el centro" o "con tolerancias supuestas") y la cifra vale en esa rebanada.
  `parcial` = se enuncia en general pero depende del diseno de muestreo.
- intervalo: `si` si la cifra principal lleva intervalo o prueba corregida, `na` si no aplica, `no` o `pendiente`.
- un_bloque: `si` si la afirmacion descansa en un solo bloque.
- alcance_en_enunciado: `si` si el propio texto de la conclusion dice la rebanada o el escenario donde vale; solo entonces
  `robusto_diseno = acotado` cuenta como valido para Alta.

Regla (el orden importa):
  Baja  = (n_min < 10 si el tipo no es determinista), o lineas < 1, o cumple 2 o menos de 6 criterios, o (robusto_diseno = no y lineas < 2), o (robusto_nc = no y un_bloque = si).
  No aplica = tipo limite (una declaracion de limites del analisis no es una inferencia y no lleva confianza).
  Alta  = tipo recuento con n_min >= 30;  o tipo inferencia con lineas >= 2, n_min >= 30,
          robusto_nc en {si, na}, robusto_diseno en {si, acotado, na} e intervalo en {si, na}; o tipo determinista con
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
        razones.append("depende del diseño (robusto_diseno = no) con una sola linea")
    if x["robusto_nc"] == "no" and x["un_bloque"] == "si":
        razones.append("cambia al tratar NO_CONVERGIO y descansa en un bloque")
    if x["tipo"] != "limite" and puntaje(x) <= 2:
        razones.append("cumple %d de 6 criterios" % puntaje(x))
    if razones:
        return "Baja", "; ".join(razones)
    if x["tipo"] == "limite":
        return "No aplica", "declaracion de limites del analisis, no una inferencia"
    if x["tipo"] == "recuento":
        if x["n_min"] >= 30:
            return "Alta", "recuento con n_min = %d" % x["n_min"]
        return "Media", "n_min < 30"
    faltan = []
    if x["lineas"] < 2:
        faltan.append("una sola linea de evidencia")
    if x["n_min"] < 30 and x["tipo"] != "determinista":
        faltan.append("n_min < 30")
    acotado = x["robusto_diseno"] == "acotado" and x.get("alcance_en_enunciado", "no") == "si"
    for c in ("robusto_nc", "robusto_diseno", "intervalo"):
        if x[c] not in OK and not (c == "robusto_diseno" and acotado):
            faltan.append("%s = %s%s" % (c, x[c], " (alcance no dicho en el enunciado)" if x[c] == "acotado" else ""))
    if not faltan:
        return "Alta", "lineas = %d, n_min = %d, robusta a NO_CONVERGIO y al diseño, con intervalo" % (x["lineas"], x["n_min"])
    return "Media", "cumple %d de 6 criterios (contando los que no aplican); falta: %s" % (puntaje(x), "; ".join(faltan))


def puntaje(x):
    """Criterios cumplidos de 6: 2 lineas, n_min, robusta a NO_CONVERGIO, robusta al diseño (o acotada y dicha), intervalo y varios bloques."""
    acotado = x["robusto_diseno"] == "acotado" and x.get("alcance_en_enunciado", "no") == "si"
    n_ok = x["tipo"] == "determinista" or x["n_min"] >= 30
    return int(x["lineas"] >= 2) + int(n_ok) + int(x["robusto_nc"] in OK) + int(x["robusto_diseno"] in OK or acotado) + \
        int(x["intervalo"] in OK) + int(x["un_bloque"] != "si")


def asignar(base, h=None):
    ev = pd.read_csv(EVIDENCIA).set_index("id")
    faltan = [i for i in base["id"] if i not in ev.index]
    if faltan:
        raise SystemExit("conclusiones sin fila en p5_evidencia.csv: %s" % faltan)
    sal = base.copy()
    res = [regla(ev.loc[i]) for i in sal["id"]]
    sal["confianza"] = [r[0] for r in res]
    sal["criterio_confianza"] = [r[1] for r in res]
    sal["criterios_cumplidos"] = [("" if r[0] == "No aplica" else puntaje(ev.loc[i])) for r, i in zip(res, sal["id"])]
    return sal


if __name__ == "__main__":
    ev = pd.read_csv(EVIDENCIA)
    for _, x in ev.iterrows():
        print(x["id"], *regla(x))
