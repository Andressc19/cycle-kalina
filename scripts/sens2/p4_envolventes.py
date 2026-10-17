# -*- coding: utf-8 -*-
"""Sens2 P4 - Paso 1: envolventes por centro y conjunto.

Para cada centro (C1..C4 y "Sin centro") y cada conjunto (KALINA total, KALINA
dentro del rango experimental y el 10 % de KALINA total con mayor eta) resume
n, minimo, P5, mediana (P50), P95 y maximo de cada cantidad derivada de equipo.
Salidas: p4_envolventes.csv y p4_envolventes.md (con la tabla llana de lo que
debe cubrir cada equipo).
"""
import os

import numpy as np
import pandas as pd

import p4_comun as c

SALIDA = c.SALIDA
COLS = ["centro", "conjunto", "cantidad", "n", "minimo", "p5", "p50", "p95", "maximo"]


def filas_centro(d, centro, grupo):
    s = d if centro == "todos" else d[d["centro"] == centro]
    sub = s[c.mascara(s, grupo)]
    filas = []
    for q in c.CANTIDADES:
        r = c.resumen_serie(sub[q])
        filas.append([centro, grupo, q, r["n"], r["minimo"], r["p5"], r["p50"],
                      r["p95"], r["maximo"]])
    return filas


def construir_tabla(d):
    filas = []
    for centro in c.grupos(d) + ["todos"]:
        for grupo in c.GRUPOS:
            filas += filas_centro(d, centro, grupo)
    return pd.DataFrame(filas, columns=COLS)


def tabla_equipo(d, equipo, cantidades, total, top10):
    """Filas (equipo, cantidad, P5/P50/P95 de KALINA total y del 10 % superior)."""
    filas = []
    for q in cantidades:
        a = c.resumen_serie(total[q])
        b = c.resumen_serie(top10[q])
        filas.append([equipo, q, a["n"], c.fmt(a["p5"]), c.fmt(a["p50"]),
                      c.fmt(a["p95"]), b["n"], c.fmt(b["p5"]), c.fmt(b["p50"]),
                      c.fmt(b["p95"])])
    return filas


def markdown(d, tabla):
    tot = d[c.mask_total(d)]
    t10 = d[c.mask_top10(d)]
    l = ["# Sens2 P4 - Paso 1: envolventes y lo que debe cubrir cada equipo", "",
         "Todos los numeros salen del dataset P2 unido a los estados del motor.",
         "m_b = 1 salvo el estudio 0 (m_b != 1); toda cantidad extensiva va dividida",
         "entre m_b (por kg/s de m_b). Presiones en kPa, temperaturas en K, h en",
         "kJ/kg, potencia en kW.", "",
         "## n por centro y conjunto", ""]
    l.append(c.tabla_md(["centro", "KALINA (total)", "KALINA dentro del rango",
                         "10 % de KALINA (total) con mayor eta"],
                        [[cen,
                          int(c.mask_total(d[d["centro"] == cen]).sum()),
                          int(c.mask_rango(d[d["centro"] == cen]).sum()),
                          int(c.mask_top10(d[d["centro"] == cen]).sum())]
                         for cen in c.grupos(d)]))
    l += ["", "## Lo que debe cubrir cada equipo (P5-P95)", "",
          "P5 y P95 del conjunto KALINA (total) y del 10 % de KALINA (total) con mayor",
          "eta, sobre todos los centros juntos. n = puntos con la cantidad disponible.", ""]
    filas = []
    for nombre, cant in c.EQUIPOS:
        filas += tabla_equipo(d, nombre, cant, tot, t10)
    l.append(c.tabla_md(["equipo", "cantidad", "n total", "P5 total", "P50 total",
                         "P95 total", "n top10", "P5 top10", "P50 top10", "P95 top10"],
                        filas))
    l += ["", "## Detalle por centro (KALINA total: P5 / P50 / P95)", "",
          "| centro | cantidad | n | P5 | P50 | P95 |", "|---|---|---|---|---|---|"]
    for cen in c.grupos(d):
        for q in c.CANTIDADES:
            r = tabla[(tabla["centro"] == cen) & (tabla["conjunto"] == c.REF_TOTAL)
                      & (tabla["cantidad"] == q)].iloc[0]
            l.append("| %s | %s | %d | %s | %s | %s |" % (
                cen, q, r["n"], c.fmt(r["p5"]), c.fmt(r["p50"]), c.fmt(r["p95"])))
    l += ["", "Lectura: P5-P95 es el cuerpo del conjunto (deja fuera el 5 % mas bajo y",
          "el 5 % mas alto); es lo que un equipo preseleccionado debe poder cubrir.",
          "`minimo` y `maximo` quedan en el CSV, no en esta tabla.", ""]
    return "\n".join(l)


def main():
    d = c.cargar()
    tabla = construir_tabla(d)
    os.makedirs(SALIDA, exist_ok=True)
    tabla.to_csv(os.path.join(SALIDA, "p4_envolventes.csv"), index=False)
    c.guardar("p4_envolventes.md", markdown(d, tabla))
    print("p4_envolventes.csv:", len(tabla), "filas")
    for cen in c.grupos(d):
        print("  %-28s KALINA=%d rango=%d top10=%d" % (
            cen, int(c.mask_total(d[d["centro"] == cen]).sum()),
            int(c.mask_rango(d[d["centro"] == cen]).sum()),
            int(c.mask_top10(d[d["centro"] == cen]).sum())))
    print("KALINA total:", int(c.mask_total(d).sum()), "| top10:", int(c.mask_top10(d).sum()))


if __name__ == "__main__":
    main()
