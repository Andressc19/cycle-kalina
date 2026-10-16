# -*- coding: utf-8 -*-
"""Sensibilidad 1 - x8f: controles 17, 18 y 19 de x8 (cierre de D5/D6 y recuento de graficos).

17 E12 con los 12 niveles (incluye 0.75 y 0.85), 18 E13 seccion 3 con la eps_cond minima de los
4 centros (sin fila "Sin centro") y 19 el libro con >= 40 graficos, todos con valores numericos.
"""

from x8b_graficos import _vref, _parse, _hay_numero, _titulo
from x8c_controles import _norm, _num, _filas_datos


def _col_nums(ws, enc):
    out = []
    for i in _filas_datos(ws, enc):
        v = ws.cell(i, 1).value
        if _num(v):
            out.append(round(float(v), 2))
    return out


def control17(wb, ok, fail):
    """E12: las tablas de ε_reg y η_t tienen 12 filas e incluyen 0.75 y 0.85."""
    ws = wb["E12 Regenerador y turbina"]
    malas, n_eps, n_eta = 0, 0, 0
    for i in range(1, ws.max_row + 1):
        v = ws.cell(i, 1).value
        if not isinstance(v, str):
            continue
        if v.startswith("ε_reg (-)"):
            n_eps += 1
            vals = _col_nums(ws, i)
            if len(vals) != 12:
                fail(f"17. E12 tabla de eps_reg en r{i}: {len(vals)} filas (esperado 12)")
                malas += 1
            if 0.75 not in vals:
                fail(f"17. E12 tabla de eps_reg en r{i}: falta el nivel base 0.75")
                malas += 1
        elif v.startswith("η_t (-)"):
            n_eta += 1
            vals = _col_nums(ws, i)
            if len(vals) != 12:
                fail(f"17. E12 tabla de eta_t en r{i}: {len(vals)} filas (esperado 12)")
                malas += 1
            if 0.85 not in vals:
                fail(f"17. E12 tabla de eta_t en r{i}: falta el nivel base 0.85")
                malas += 1
    if n_eps < 1 or n_eta < 1:
        fail(f"17. E12: tablas de eps_reg {n_eps} y de eta_t {n_eta} (se exige >= 1 de cada)")
        malas += 1
    if not malas:
        ok(f"17. E12: {n_eps} tablas de eps_reg y {n_eta} de eta_t con 12 filas (incluyen 0.75 y 0.85)")


def control18(wb, ok, fail):
    """E13 seccion 3: la ε_cond mínima de los 4 centros está y no hay fila "Sin centro"."""
    ws = wb["E13 Preseleccion de equipos"]
    enc = None
    for i in range(1, ws.max_row + 1):
        v = ws.cell(i, 1).value
        if isinstance(v, str) and _norm(v) == _norm("Centro") and \
                _norm(ws.cell(i, 2).value).startswith(_norm("ε_cond mínima")):
            enc = i
            break
    if enc is None:
        fail("18. E13: no encuentro la tabla de eps_cond minima con KALINA por centro")
        return
    filas = _filas_datos(ws, enc)
    malas = 0
    if len(filas) != 4:
        fail(f"18. E13: la tabla de eps_cond minima tiene {len(filas)} filas (esperado 4)")
        malas += 1
    for i in filas:
        cen = ws.cell(i, 1).value
        if "sincentro" in _norm(cen):
            fail(f"18. E13: hay una fila '{cen}' (no se admite una fila sin centro)")
            malas += 1
        if not _num(ws.cell(i, 2).value):
            fail(f"18. E13 {cen}: eps_cond minima vacia")
            malas += 1
    if not malas:
        ok("18. E13 seccion 3: eps_cond minima con KALINA en los 4 centros y sin fila 'Sin centro'")


def control19(wb, ok, fail):
    """El libro tiene >= 40 gráficos y todos con al menos una serie con valores numéricos."""
    total = sum(len(wb[s]._charts) for s in wb.sheetnames)
    malas = 0
    for s in wb.sheetnames:
        for ch in wb[s]._charts:
            ok_serie = False
            for se in ch.series:
                ref = _vref(se)
                if ref is None:
                    continue
                h, c1, r1, c2, r2 = _parse(ref)
                if h in wb.sheetnames and _hay_numero(wb[h], c1, r1, c2, r2):
                    ok_serie = True
                    break
            if not ok_serie:
                fail(f"19. {s} [{_titulo(ch)}]: sin serie con valores numericos")
                malas += 1
    if total < 40:
        fail(f"19. el libro tiene {total} graficos (se exigen >= 40)")
        malas += 1
    if not malas:
        ok(f"19. el libro tiene {total} graficos, todos con valores numericos "
           "(los solapes los vigila el control 5)")


__all__ = ["control17", "control18", "control19"]
