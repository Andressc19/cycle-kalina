# -*- coding: utf-8 -*-
"""Sensibilidad 1 - x8h: controles 22 a 25 de x8 (frase acotada, rotulos y puntos atipicos).

22 sin la frase «eps_cond < 0.85 no hay KALINA» sin acotar a Husavik; 23 rotulos de dos ejes en
las matrices de E15 y E16; 24 la tabla de puntos atipicos de LEEME con los 7 ids; 25 >= 43
graficos, todos con valores numericos.
"""

from x8b_graficos import _titulo, x8b_textos
from x8c_controles import _norm, _filas_datos
from x8g_controles import _chart_numerico, _plano

IDS_ATIPICOS = ["C1-B6-0236", "N1-T090-10", "N7A-C3-P_alta-001", "N7A-C4-P_alta-001",
                "N7A-C4-eps_hrvg-003", "N8-C4-0141", "N9-C4-B6-0004"]

HOJA_E15, HOJA_E16 = "E15 Pares regenerador", "E16 P_alta alta"


def control22(wb, ok, fail):
    """Ninguna celda ni texto de grafico con «eps_cond < 0.85 no hay KALINA» sin Husavik."""
    malas = []

    def revisa(hoja, donde, texto):
        t = _plano(texto)
        if "eps_cond<0.85" in t and "nohaykalina" in t and "husavik" not in t:
            malas.append((hoja, donde, str(texto)[:50]))

    for s in wb.sheetnames:
        for c in wb[s].iter_rows():
            for celda in c:
                if isinstance(celda.value, str):
                    revisa(s, celda.coordinate, celda.value)
        for ch in wb[s]._charts:
            for texto in x8b_textos(ch):
                revisa(s, "grafico", texto)
    if not malas:
        ok("22. ningun texto del libro generaliza «eps_cond < 0.85 no hay KALINA» sin acotarlo "
           "a la configuracion de Husavik")
    else:
        fail(f"22. {len(malas)} textos sin acotar: {malas[:8]}")


def control23(wb, ok, fail):
    """E15 y E16: la celda de esquina de cada matriz rotula filas y columnas."""
    malas = 0
    for hoja, minimo, terminos in (
            (HOJA_E15, 8, ("eps_reg", "eta_t", "eps_hrvg", "t_fuente")),
            (HOJA_E16, 6, ("p_alta", "p_baja"))):
        ws = wb[hoja]
        rotulos = []
        for fila in ws.iter_rows():
            for c in fila:
                if isinstance(c.value, str):
                    t = _norm(c.value)
                    if "filas:" in t and "columnas:" in t:
                        rotulos.append(t)
        if len(rotulos) < minimo:
            fail(f"23. {hoja}: {len(rotulos)} rotulos de dos ejes (se exigen >= {minimo})")
            malas += 1
        for term in terminos:
            if not any(term in r for r in rotulos):
                fail(f"23. {hoja}: ningun rotulo de esquina menciona '{term}'")
                malas += 1
    if not malas:
        ok("23. E15 (8 matrices) y E16 (6 matrices): celda de esquina con filas y columnas")


def control24(wb, ok, fail):
    """LEEME: tabla de puntos atipicos con exactamente los 7 ids del director."""
    ws = wb["LEEME"]
    enc = None
    for i in range(1, ws.max_row + 1):
        if isinstance(ws.cell(i, 1).value, str) and _norm(ws.cell(i, 1).value) == "id_punto":
            enc = i
            break
    if enc is None:
        fail("24. LEEME: no encuentro la tabla de puntos atipicos (id_punto ...)")
        return
    ids = [ws.cell(i, 1).value for i in _filas_datos(ws, enc)]
    if len(ids) != len(IDS_ATIPICOS):
        fail(f"24. LEEME: la tabla tiene {len(ids)} ids (esperado {len(IDS_ATIPICOS)})")
        return
    faltan = [x for x in IDS_ATIPICOS if x not in ids]
    sobran = [x for x in ids if x not in IDS_ATIPICOS]
    if faltan or sobran:
        fail(f"24. LEEME: faltan {faltan} y sobran {sobran}")
        return
    ok("24. LEEME: tabla de puntos atipicos con los 7 ids del director")


def control25(wb, ok, fail):
    """El libro tiene >= 43 graficos y todos con al menos una serie con valores numericos."""
    total = sum(len(wb[s]._charts) for s in wb.sheetnames)
    malas = 0
    for s in wb.sheetnames:
        for ch in wb[s]._charts:
            if not _chart_numerico(wb, ch):
                fail(f"25. {s} [{_titulo(ch)}]: sin serie con valores numericos")
                malas += 1
    if total < 43:
        fail(f"25. el libro tiene {total} graficos (se exigen >= 43)")
        malas += 1
    if not malas:
        ok(f"25. el libro tiene {total} graficos, todos con valores numericos")


__all__ = ["IDS_ATIPICOS", "control22", "control23", "control24", "control25"]
