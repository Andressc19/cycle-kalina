# -*- coding: utf-8 -*-
"""Sens2 - pruebas de coherencia entre documentos y datos (solo lectura).

Las cifras globales de los documentos escritos a mano van marcadas como `<!--g:clave-->valor<!--/g-->`; estas pruebas fallan si alguna no
coincide con `p5_globales.py` (que las calcula de los archivos) o si desaparece un marcador. Ejecuta `scripts/sens2/docs_sync.py` para corregirlas.
"""
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens2"))
import docs_sync as DS  # noqa: E402
import p5_globales as G  # noqa: E402

MINIMO_MARCADORES = 9


def test_cifras_marcadas_al_dia():
    malas, total = DS.revisar(escribir=False)
    assert not malas, "documentos desactualizados (ejecuta docs_sync.py): %s" % malas
    assert total >= MINIMO_MARCADORES, "faltan marcadores de cifras globales (%d)" % total


def test_leeme_cita_los_puntos_del_motor():
    from openpyxl import load_workbook
    ws = load_workbook(G.LIBRO, read_only=True)["LEEME"]
    texto = " ".join(str(c) for fila in ws.iter_rows(values_only=True) for c in fila if c is not None)
    u1, b = G.puntos_motor()
    assert "anade %d puntos nuevos" % u1 in texto
    assert "%d puntos de la etapa B" % sum(b.values()) in texto


def test_informe_cita_hojas_y_graficos_del_libro():
    g = G.globales()
    with open(os.path.join(RAIZ, "docs", "INFORME_SENS2.md"), encoding="utf-8") as fh:
        t = fh.read()
    assert "(%d hojas, %d gráficos)" % (g["n_hojas"][0], g["n_graficos"][0]) in t


def test_marcadores_bien_formados():
    for ruta in DS.DOCS:
        with open(ruta, encoding="utf-8") as fh:
            s = fh.read()
        assert s.count("<!--g:") == s.count("<!--/g-->"), os.path.basename(ruta)
        assert len(re.findall(r"<!--g:", s)) == len(DS.PATRON.findall(s)), os.path.basename(ruta)
