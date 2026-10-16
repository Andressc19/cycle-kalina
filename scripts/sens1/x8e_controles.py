# -*- coding: utf-8 -*-
"""Sensibilidad 1 - x8e: controles 14, 15 y 16 de x8 (estudios 14/15/16 de la Ronda 3).

14 datos de 14/15/16 (filas e ids), 15 S1 con 15 filas, 16 totales de clase y η máximas citadas.
Los controles 17 a 19 viven en x8f_controles.
"""

from x8c_controles import _norm, _num, _fila_encabezado, _filas_datos

NUEVOS = {14: ("E14 Datos LHS C3 C4", 465), 15: ("E15 Datos Pares", 194),
          16: ("E16 Datos P_alta", 105)}


def _fila_con_texto(ws, texto):
    for i in range(1, ws.max_row + 1):
        v = ws.cell(i, 1).value
        if isinstance(v, str) and texto in v:
            return i
    return None


def _encabezado_desde(ws, desde, texto):
    for i in range(desde, ws.max_row + 1):
        v = ws.cell(i, 1).value
        if isinstance(v, str) and _norm(v).startswith(_norm(texto)):
            return i
    return None


def _ids_datos(ws, col=1):
    """Ids (columna 1) de una hoja de datos: desde la fila 4 hasta la 1a vacia o la descripcion."""
    ids = []
    for i in range(4, ws.max_row + 1):
        v = ws.cell(i, col).value
        if v is None or v == "" or (isinstance(v, str) and "Descrip" in v):
            break
        ids.append(str(v))
    return ids


def control14(wb, df, ok, fail):
    """Estudios 14/15/16: filas del CSV 465/194/105 y los ids de las hojas iguales a los CSV."""
    malas = 0
    for n, (hoja, n_filas) in NUEVOS.items():
        real = int((df["estudio"] == n).sum())
        if real != n_filas:
            fail(f"14. estudio {n}: el CSV tiene {real} filas (esperado {n_filas})")
            malas += 1
        if hoja not in wb.sheetnames:
            fail(f"14. falta la hoja {hoja}")
            malas += 1
            continue
        lista = _ids_datos(wb[hoja])
        ids_csv = set(df[df["estudio"] == n]["id_punto"].astype(str))
        if len(lista) != n_filas:
            fail(f"14. {hoja}: {len(lista)} filas de datos (esperado {n_filas})")
            malas += 1
        if set(lista) != ids_csv:
            fail(f"14. {hoja}: los ids de la hoja no coinciden con el CSV")
            malas += 1
    if not malas:
        ok("14. estudios 14/15/16: 465/194/105 filas y los ids de las hojas coinciden con los CSV")


def control15(wb, ok, fail):
    """S1: 15 filas (estudios 0-11 y 14-16) y el Total = suma de las 4 clases."""
    ws = wb["Conclusion consolidada"]
    enc = _fila_encabezado(ws, "Estudio")
    if enc is None:
        fail("15. no encuentro la tabla S1 (Estudio ... Total)")
        return
    filas = _filas_datos(ws, enc)
    ests = [ws.cell(i, 1).value for i in filas]
    malas = 0
    if len(filas) != 15:
        fail(f"15. S1 tiene {len(filas)} filas (esperado 15)")
        malas += 1
    for n in (14, 15, 16):
        if n not in ests:
            fail(f"15. S1 no incluye el estudio {n}")
            malas += 1
    for i in filas:
        est = ws.cell(i, 1).value
        vals = [ws.cell(i, j).value for j in range(2, 9)]
        if vals[6] != vals[0] + vals[3] + vals[4] + vals[5]:
            fail(f"15. S1 estudio {est}: Total {vals[6]} != suma de las 4 clases")
            malas += 1
    if not malas:
        ok("15. S1 tiene 15 filas (0-11 y 14-16) y el Total es la suma de las 4 clases")


def control16(wb, df, ok, fail):
    """Totales de clase de los estudios nuevos y las η máximas citadas (E14, E15 y E16)."""
    malas = 0
    ws = wb["Conclusion consolidada"]
    enc = _fila_encabezado(ws, "Estudio")
    s1 = {ws.cell(i, 1).value: [ws.cell(i, j).value for j in range(2, 9)]
          for i in _filas_datos(ws, enc)}
    for n, k, fuera in ((14, 258, 28), (15, 184, 11), (16, 47, 0)):
        fila = s1.get(n)
        if fila is None:
            fail(f"16. S1 no tiene el estudio {n}")
            malas += 1
            continue
        if fila[0] != k:
            fail(f"16. S1 estudio {n}: KALINA (total) {fila[0]} != {k}")
            malas += 1
        if fila[2] != fuera:
            fail(f"16. S1 estudio {n}: fuera del rango experimental {fila[2]} != {fuera}")
            malas += 1
    for cen, esp in (("C3 caliente 150 C", 12.1), ("C4 frio 110 C", 11.2)):
        sub = df[(df["estudio"] == 14) & df["kalina"] & (df["centro"] == cen)]
        v = round(float(sub["eta_pct"].max()), 1)
        if abs(v - esp) > 0.05:
            fail(f"16. estudio 14 {cen}: eta maxima {v} != {esp}")
            malas += 1
    ws = wb["E15 Pares regenerador"]
    t = _fila_con_texto(ws, "η máxima por par y centro")
    enc = _encabezado_desde(ws, t or 1, "Par de variables")
    if enc is None:
        fail("16. E15: no encuentro la tabla de eta maxima por par")
        malas += 1
    else:
        tabla = {str(ws.cell(i, 1).value)[:2]: [ws.cell(i, 2).value, ws.cell(i, 3).value]
                 for i in _filas_datos(ws, enc)}
        for par, c3, c4 in (("B5", 10.9, 13.0), ("B6", 9.5, 12.3)):
            row = tabla.get(par)
            if row is None:
                fail(f"16. E15: falta la fila {par}")
                malas += 1
                continue
            for lbl, val, esp in (("C3", row[0], c3), ("C4", row[1], c4)):
                if val is None or abs(float(val) - esp) > 0.05:
                    fail(f"16. E15 {par} {lbl}: eta maxima {val} != {esp}")
                    malas += 1
    ws = wb["E16 P_alta alta"]
    t = _fila_con_texto(ws, "P_alta del máximo de η por centro")
    enc = _encabezado_desde(ws, t or 1, "Centro")
    if enc is None:
        fail("16. E16: no encuentro la tabla de P_alta del maximo de eta")
        malas += 1
    else:
        tabla = {ws.cell(i, 1).value: (ws.cell(i, 2).value, ws.cell(i, 3).value)
                 for i in _filas_datos(ws, enc)}
        for cen, pa, eta in (("C1 Husavik", 5000, 14.0), ("C3 caliente 150 C", 6000, 14.5),
                             ("C4 frio 110 C", 4000, 12.2)):
            row = tabla.get(cen)
            if row is None:
                fail(f"16. E16: falta la fila {cen}")
                malas += 1
                continue
            if row[0] is None or abs(float(row[0]) - pa) > 0.5:
                fail(f"16. E16 {cen}: P_alta del maximo {row[0]} != {pa}")
                malas += 1
            if row[1] is None or abs(float(row[1]) - eta) > 0.05:
                fail(f"16. E16 {cen}: eta maxima {row[1]} != {eta}")
                malas += 1
    if not malas:
        ok("16. totales de clase de 14/15/16 y eta maxima citada (E14 12.1/11.2; E15 10.9/9.5/"
           "13.0/12.3; E16 14.0@5000/14.5@6000/12.2@4000)")


__all__ = ["control14", "control15", "control16"]
