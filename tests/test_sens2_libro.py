# -*- coding: utf-8 -*-
"""Sens2 A5 - pruebas del libro `datos/Kalina_anal_sensible_2.xlsx` (solo lectura).

No escribe ningun archivo del proyecto: abre el libro con openpyxl, comprueba la estructura de
hojas, que ninguna celda de texto use el vocabulario prohibido y que las conclusiones de la hoja
`Conclusion consolidada` coincidan una a una con `p5_conclusiones.csv`.
"""
import os
import re
import sys
import zipfile

import openpyxl
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIBRO = os.path.join(RAIZ, "datos", "Kalina_anal_sensible_2.xlsx")
CONCLUSIONES = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P5", "p5_conclusiones.csv")
EVIDENCIA = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P5", "p5_evidencia.csv")
INFORME = os.path.join(RAIZ, "docs", "INFORME_SENS2.md")
VALIDACION = os.path.join(RAIZ, "docs", "VALIDACION_SENS2.md")

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


def _hojas_y_graficos():
    """Cuenta hojas con openpyxl y graficos (xl/charts/chart<N>.xml) con zipfile."""
    n_hojas = len(_wb().sheetnames)
    with zipfile.ZipFile(LIBRO) as z:
        n_graficos = sum(1 for n in z.namelist() if re.match(r"^xl/charts/chart\d+\.xml$", n))
    return n_hojas, n_graficos


def test_informe_y_validacion_dicen_hojas_y_graficos_reales():
    n_hojas, n_graficos = _hojas_y_graficos()
    texto = "(%d hojas, %d gráficos)" % (n_hojas, n_graficos)
    for doc in (INFORME, VALIDACION):
        with open(doc, encoding="utf-8") as f:
            contenido = f.read()
        assert texto in contenido, "%s no contiene %r" % (os.path.basename(doc), texto)


def test_confianza_tiene_los_41_ids():
    ids = set(pd.read_csv(CONCLUSIONES)["id"].astype(str))
    wb = _wb()
    col_a = [str(r[0]) for r in wb["Confianza"].iter_rows(values_only=True) if r[0] is not None]
    encontrados = [v for v in col_a if v in ids]
    assert len(encontrados) == len(set(encontrados)) == len(ids) >= 43
    assert set(encontrados) == ids


def test_toda_hoja_esta_en_la_guia_del_leeme():
    wb = _wb()
    hojas = set(wb.sheetnames)
    col_a = [str(r[0]) for r in wb["LEEME"].iter_rows(values_only=True) if r[0] is not None]
    for hoja in wb.sheetnames:
        if hoja != "LEEME":
            assert hoja in col_a, "hoja %r no listada en la columna A de LEEME" % hoja
    for texto in col_a:
        if texto in hojas:
            assert texto in hojas


def test_confianza_coincide_con_la_regla():
    sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens2"))
    from p5_confianza import regla  # noqa: E402

    ev = pd.read_csv(EVIDENCIA)
    c = pd.read_csv(CONCLUSIONES).set_index("id")
    for _, fila in ev.iterrows():
        cid = fila["id"]
        assert cid in c.index, "conclusion %r sin confianza" % cid
        esperado = regla(fila)[0]
        obtenido = c.loc[cid, "confianza"]
        assert obtenido == esperado, "%s: confianza %r, regla dice %r" % (cid, obtenido, esperado)
