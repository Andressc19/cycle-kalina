# -*- coding: utf-8 -*-
"""Sens2 A5 - pruebas del libro `datos/Kalina_anal_sensible_2.xlsx` (solo lectura).

No escribe ningun archivo del proyecto: abre el libro con openpyxl, comprueba la estructura de
hojas, que ninguna celda de texto use el vocabulario prohibido y que las conclusiones de la hoja
`Conclusion consolidada` coincidan una a una con `p5_conclusiones.csv`.
"""
import os
import re

import openpyxl
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIBRO = os.path.join(RAIZ, "datos", "Kalina_anal_sensible_2.xlsx")
CONCLUSIONES = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P5", "p5_conclusiones.csv")

PROHIBIDAS = ["confiable", "no citable", "fuera de rango del motor", "indicio", "extrapol",
              "sin respaldo"]
HOJAS = ["F5 Incertidumbre", "F6 Respaldo libro viejo"]


def _wb():
    return openpyxl.load_workbook(LIBRO, read_only=True, data_only=True)


def test_abre_y_estructura():
    wb = _wb()
    assert wb.sheetnames[0] == "LEEME"
    assert len(wb.sheetnames) >= 23
    for hoja in HOJAS:
        assert hoja in wb.sheetnames, hoja


def _definidas_en_leeme(wb):
    """Palabras prohibidas que la propia hoja LEEME enuncia (se excluyen solo en LEEME)."""
    dichas = set()
    for fila in wb["LEEME"].iter_rows(values_only=True):
        for celda in fila:
            if isinstance(celda, str):
                bajo = celda.lower()
                dichas.update(w for w in PROHIBIDAS if w in bajo)
    return dichas


def test_sin_palabras_prohibidas():
    wb = _wb()
    permitidas_leeme = _definidas_en_leeme(wb)
    for nombre in wb.sheetnames:
        for fila in wb[nombre].iter_rows(values_only=True):
            for celda in fila:
                if not isinstance(celda, str):
                    continue
                bajo = celda.lower()
                for w in PROHIBIDAS:
                    if w not in bajo:
                        continue
                    if nombre == "LEEME" and w in permitidas_leeme:
                        continue
                    raise AssertionError("palabra prohibida %r en la hoja %r: %r"
                                         % (w, nombre, celda[:80]))


def test_conclusiones_coinciden_con_csv():
    ids = set(pd.read_csv(CONCLUSIONES)["id"].astype(str))
    patron = re.compile(r"^(?:" + "|".join(re.escape(i) for i in sorted(ids)) + r")(?![0-9A-Za-z])")
    wb = _wb()
    n = 0
    for fila in wb["Conclusion consolidada"].iter_rows(values_only=True):
        if fila and fila[0] is not None and patron.match(str(fila[0])):
            n += 1
    assert n == len(ids)
