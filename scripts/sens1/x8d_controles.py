# -*- coding: utf-8 -*-
"""Sensibilidad 1 - x8d: controles 11, 12 y 13 de x8 (base en tablas y hojas E12/E13)."""

from x8b_graficos import _vref, _parse, _hay_numero, _titulo
from x8c_controles import _norm, _filas_datos


def _valor_tabla(ws, fila_titulo, etiqueta_var, col):
    """Valor de la fila de `etiqueta_var` en la tabla cuyo encabezado sigue a `fila_titulo`."""
    inicio = (fila_titulo or 0) + 1
    enc = None
    for i in range(inicio, ws.max_row + 1):
        v = ws.cell(i, 1).value
        if isinstance(v, str) and _norm(v).startswith(_norm("Variable barrida")):
            enc = i
            break
    if enc is None:
        return None
    for i in _filas_datos(ws, enc):
        v = ws.cell(i, 1).value
        if isinstance(v, str) and _norm(v).startswith(_norm(etiqueta_var)):
            return ws.cell(i, col).value
    return None


def _valor_par(ws, etiqueta_var, col):
    """Valor de la fila de un par en la tabla 'Par de variables'."""
    for i in _filas_datos_desde(ws, "Par de variables"):
        v = ws.cell(i, 1).value
        if isinstance(v, str) and _norm(v).startswith(_norm(etiqueta_var)):
            return ws.cell(i, col).value
    return None


def _filas_datos_desde(ws, encabezado):
    enc = None
    for i in range(1, ws.max_row + 1):
        v = ws.cell(i, 1).value
        if isinstance(v, str) and _norm(v).startswith(_norm(encabezado)):
            enc = i
            break
    return _filas_datos(ws, enc) if enc else []


def _fila_titulo(ws, texto):
    for i in range(1, ws.max_row + 1):
        v = ws.cell(i, 1).value
        if isinstance(v, str) and texto in v:
            return i
    return None


def control11(wb, ok, fail):
    """Las tablas por variable de E1/E10 y las de pares de E2/E11 incluyen el base."""
    malas = 0

    def check(nombre, obtenido, esperado):
        if obtenido != esperado:
            fail(f"11. {nombre}: {obtenido} != {esperado}")
            return 1
        return 0

    ws = wb["E1 Una variable"]
    t = _fila_titulo(ws, "por variable barrida en C1 Husavik")
    malas += check("eps_cond C1", _valor_tabla(ws, t, "ε_cond (-)", 2), 1)

    ws = wb["E10 Centros nuevos 1 variable"]
    t = _fila_titulo(ws, "por variable barrida en C4 frio 110 C")
    malas += check("eps_cond C4", _valor_tabla(ws, t, "ε_cond (-)", 2), 1)

    ws = wb["E2 Pares"]
    malas += check("B4 C1", _valor_par(ws, "B4", 2), 3)

    ws = wb["E11 Centros nuevos pares"]
    malas += check("B4 C3", _valor_par(ws, "B4", 2), 8)
    malas += check("B4 C4", _valor_par(ws, "B4", 3), 5)

    if not malas:
        ok("11. tablas por variable y par incluyen el base (eps_cond C1=1, C4=1, B4 C1=3, C3=8, C4=5)")


def _graficos_hoja(wb, hoja):
    return wb[hoja]._charts if hoja in wb.sheetnames else []


def control12(wb, ok, fail):
    """E12 y E13 existen con >= 6 graficos nuevos, cada uno con >= 1 serie numerica."""
    malas, n = 0, 0
    for hoja in ("E12 Regenerador y turbina", "E13 Preseleccion de equipos"):
        if hoja not in wb.sheetnames:
            fail(f"12. falta la hoja {hoja}")
            malas += 1
            continue
        for ch in _graficos_hoja(wb, hoja):
            n += 1
            if not ch.series:
                fail(f"12. {hoja} [{_titulo(ch)}]: 0 series")
                malas += 1
                continue
            ok_serie = False
            for se in ch.series:
                ref = _vref(se)
                if ref is None:
                    continue
                h, c1, r1, c2, r2 = _parse(ref)
                if h in wb.sheetnames and _hay_numero(wb[h], c1, r1, c2, r2):
                    ok_serie = True
            if not ok_serie:
                fail(f"12. {hoja} [{_titulo(ch)}]: sin serie con valores numericos")
                malas += 1
    if n < 6:
        fail(f"12. E12+E13 tienen {n} graficos (se exigen >= 6)")
        malas += 1
    if not malas:
        ok(f"12. E12 y E13 presentes con {n} graficos nuevos, cada uno con valores numericos")


def control13(wb, ok, fail):
    """El libro tiene >= 26 graficos en total."""
    total = sum(len(wb[s]._charts) for s in wb.sheetnames)
    if total < 26:
        fail(f"13. el libro tiene {total} graficos (se exigen >= 26)")
    else:
        ok(f"13. el libro tiene {total} graficos en total")
    return total
