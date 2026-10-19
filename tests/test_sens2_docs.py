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
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))
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


def _texto_hoja(nombre):
    from openpyxl import load_workbook
    ws = load_workbook(G.LIBRO, read_only=True)[nombre]
    return " ".join(str(c) for fila in ws.iter_rows(values_only=True) for c in fila if c is not None)


def test_mapa_de_preguntas_incluye_la_etapa_b():
    """Las conclusiones y hojas de la etapa B figuran en las tablas de preguntas de la consolidada y del LEEME."""
    cons = _texto_hoja("Conclusion consolidada")
    for ref in ("D8; D9", "U1 a U5", "M6; M7", "E9; E10", "F4 Optimo vs T_fuente", "F4 Caudales y bomba", "F3 Pisos 25 kPa y reintento"):
        assert ref in cons, "falta %r en la tabla de preguntas de la consolidada" % ref
    leeme = _texto_hoja("LEEME")
    for hoja in ("F3 Pisos 25 kPa y reintento", "F4 Caudales y bomba", "F4 Optimo vs T_fuente", "F5 Incertidumbre simetrica"):
        assert hoja in leeme, "falta %r en la guia del LEEME" % hoja


def test_pdf_incluye_las_conclusiones_de_la_etapa_b():
    ruta = os.path.join(RAIZ, "docs", "INFORME_TECNICO_SENS2.html")
    with open(ruta, encoding="utf-8") as fh:
        t = fh.read()
    for cid in ("D9", "L10", "E10", "U5", "M7"):
        assert ("<b>%s" % cid in t) or (cid in t), "el PDF no cita %s" % cid
    assert "etapa B" in t


def test_guia_del_leeme_sigue_el_orden_real_de_las_hojas():
    from openpyxl import load_workbook
    import s2_leeme
    real = load_workbook(G.LIBRO, read_only=True).sheetnames
    assert [n for n, _ in s2_leeme.GUIA] == real
