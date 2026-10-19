# -*- coding: utf-8 -*-
"""Sens2 - p5_cruce: mismo dato con distinto valor entre conclusiones.

Lee `p5_conclusiones.csv` (id, afirmacion, evidencia, implicacion), extrae los numeros con
unidad, toma como clave el par (unidad, las dos palabras que preceden al numero, en
minusculas y sin puntuacion) y agrupa entre conclusiones distintas. Un grupo con al menos 2
conclusiones y al menos 2 valores distintos (redondeados a 2 decimales) es un candidato a
contradiccion. Salidas: `p5_cruce.csv` (una fila por aparicion) y `p5_cruce.md` (lista de
candidatos). Es una lista para revision manual: un candidato no es un error. Sale con 0.
"""
import os
import re
import sys
from collections import defaultdict

import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
R = os.path.join(RAIZ, "resultados")
D = os.path.join(R, "2026-10-17_sens2_P5")
sys.path.insert(0, AQUI)

CONCL = "p5_conclusiones.csv"
CAMPOS = ("afirmacion", "evidencia", "implicacion")
PAT = re.compile(r"(-?\d+(?:[.,]\d+)?)\s*(%|kPa|K|°C|kJ/kg|pp|puntos|kW|L/s|kg/m³|m)(?![A-Za-z])")
PUNTO = re.compile(r"[^\w]", re.UNICODE)
COLS = ("clave", "unidad", "valor", "id", "campo", "contexto")
LADO = 60


def _contexto(texto, ini, fin):
    a, b = max(0, ini - LADO), min(len(texto), fin + LADO)
    return texto[a:b].replace("\r", " ").replace("\n", " ").replace("|", "/")


def _clave(texto, ini):
    """Las dos palabras inmediatamente anteriores al numero, en minusculas y sin puntuacion."""
    toks = [PUNTO.sub("", t).lower() for t in texto[:ini].split()]
    toks = [t for t in toks if t]
    return " ".join(toks[-2:])


def apariciones():
    """Una fila por numero con unidad en los tres campos de texto de las conclusiones."""
    base = pd.read_csv(os.path.join(D, CONCL))
    filas = []
    for _, r in base.iterrows():
        for campo in CAMPOS:
            if campo not in base.columns:
                continue
            txt = str(r[campo])
            for m in PAT.finditer(txt):
                filas.append({"clave": _clave(txt, m.start()), "unidad": m.group(2),
                              "valor": float(m.group(1).replace(",", ".")),
                              "id": str(r["id"]), "campo": campo,
                              "contexto": _contexto(txt, m.start(), m.end())})
    return filas


def agrupar(filas):
    """Grupos {(clave, unidad): apariciones} y candidatos con sus apariciones."""
    grupos = defaultdict(list)
    for x in filas:
        grupos[(x["clave"], x["unidad"])].append(x)
    candidatos = []
    for k, ap in grupos.items():
        ids = {a["id"] for a in ap}
        valores = {round(a["valor"], 2) for a in ap}
        if len(ids) >= 2 and len(valores) >= 2:
            candidatos.append((k, ap))
    candidatos.sort(key=lambda t: (t[0][0], t[0][1]))
    return grupos, candidatos


def _informe(filas, grupos, candidatos):
    md = ["# Sens2 P5 - cruce de cifras entre conclusiones", "",
          "Numeros con unidad de `%s` agrupados por (unidad, dos palabras previas). Un grupo "
          "con al menos 2 conclusiones distintas y al menos 2 valores distintos (a 2 decimales) "
          "es un candidato a contradiccion. La lista es para revision manual: un candidato no "
          "es un error." % CONCL, "",
          "- apariciones: %d" % len(filas),
          "- claves (pares clave, unidad): %d" % len(grupos),
          "- candidatos: %d" % len(candidatos), "",
          "## Candidatos", ""]
    for (clave, unidad), ap in candidatos:
        ids = sorted({a["id"] for a in ap})
        vals = sorted({round(a["valor"], 2) for a in ap})
        md += ["### %s | %s" % (clave if clave else "(sin palabras previas)", unidad), "",
               "- conclusiones: %s" % ", ".join(ids),
               "- valores (2 decimales): %s" % ", ".join("%g" % v for v in vals), "",
               "| id | campo | valor | contexto |", "|---|---|---:|---|"]
        for a in ap:
            md.append("| %s | %s | %s | %s |" % (a["id"], a["campo"], a["valor"], a["contexto"]))
        md += [""]
    with open(os.path.join(D, "p5_cruce.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")


def _ascii(texto):
    return texto.encode("ascii", "replace").decode("ascii")


def main():
    filas = apariciones()
    grupos, candidatos = agrupar(filas)
    tabla = pd.DataFrame(filas, columns=list(COLS)).sort_values(
        ["clave", "unidad", "id", "campo"], kind="stable")
    tabla.to_csv(os.path.join(D, "p5_cruce.csv"), index=False, encoding="utf-8",
                 lineterminator="\r\n")
    _informe(filas, grupos, candidatos)
    print("apariciones: %d" % len(filas))
    print("claves: %d" % len(grupos))
    print("candidatos: %d" % len(candidatos))
    print("primeros 15 candidatos:")
    for (clave, unidad), ap in candidatos[:15]:
        vals = ", ".join("%s=%g" % (a["id"], a["valor"]) for a in ap)
        print("  %-24s %-6s %s" % (_ascii(clave) if clave else "(vacia)", _ascii(unidad), vals))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR: %s" % _ascii(str(e)))
    raise SystemExit(0)
