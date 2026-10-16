# -*- coding: utf-8 -*-
"""Sensibilidad 1 - x8i: controles 26 y 27 de x8 (KALINA por par de E2/E11 por malla).

26 La tabla «KALINA por par» de E2 y E11 cuenta los KALINA por pertenencia a la malla del par
   (valores del director), no por su etiqueta `par`.
27 El grafico «KALINA por par» de E2 y E11 lee esas cifras: sus series apuntan a las celdas de la
   tabla y tienen valores numericos.
"""

from x8b_graficos import _parse, _titulo, _vref
from x8c_controles import _filas_datos, _norm
from x8g_controles import _chart_numerico

# Columnas de la tabla «KALINA por par» (2 = primer centro, 3 = segundo centro): recuento por
# pertenencia a la malla, contrastado por el director contra los CSV.
ESPERADO = {
    "E2 Pares": {"B1": (39, 35), "B2": (43, 23), "B3": (41, 41), "B4": (3, 33),
                 "B5": (49, 49), "B6": (46, 39)},
    "E11 Centros nuevos pares": {"B1": (40, 25), "B2": (36, 39), "B3": (40, 34),
                                 "B4": (8, 5)},
}


def _tabla_pares(ws):
    """Fila del encabezado «Par de variables ...» de una hoja, o None."""
    for i in range(1, ws.max_row + 1):
        v = ws.cell(i, 1).value
        if isinstance(v, str) and _norm(v).startswith(_norm("Par de variables")):
            return i
    return None


def control26(wb, ok, fail):
    """E2 y E11: cada cifra de KALINA por par y centro coincide con el recuento por malla."""
    malas = 0
    for hoja, esperado in ESPERADO.items():
        ws = wb[hoja]
        enc = _tabla_pares(ws)
        if enc is None:
            fail(f"26. {hoja}: no encuentro la tabla «KALINA por par»")
            malas += 1
            continue
        vistos = {}
        for i in _filas_datos(ws, enc):
            etq = ws.cell(i, 1).value
            if not isinstance(etq, str):
                continue
            par = etq.strip()[:2]
            if par not in esperado:
                continue
            v2, v3 = ws.cell(i, 2).value, ws.cell(i, 3).value
            vistos[par] = (v2, v3)
            c1, c2 = esperado[par]
            if v2 != c1 or v3 != c2:
                fail(f"26. {hoja} {par}: ({v2}, {v3}) != ({c1}, {c2})")
                malas += 1
        faltan = [p for p in esperado if p not in vistos]
        if faltan:
            fail(f"26. {hoja}: faltan los pares {faltan}")
            malas += 1
    if not malas:
        ok("26. E2 y E11: KALINA por par y centro por pertenencia a la malla (coincide con los "
           "valores del director)")


def _series_tabla(wb, ch):
    """Series numericas de un grafico, leidas de las celdas referenciadas del libro."""
    out = []
    for se in ch.series:
        ref = _vref(se)
        if ref is None:
            continue
        hoja, c1, r1, c2, r2 = _parse(ref)
        if hoja not in wb.sheetnames:
            continue
        vals = [wb[hoja].cell(r, c).value
                for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]
        out.append([v for v in vals
                    if isinstance(v, (int, float)) and not isinstance(v, bool)])
    return out


def control27(wb, ok, fail):
    """E2 y E11: el grafico «KALINA por par» lee la tabla y tiene series numericas."""
    malas = 0
    for hoja, esperado in ESPERADO.items():
        ws = wb[hoja]
        col1 = [esperado[p][0] for p in esperado]
        col2 = [esperado[p][1] for p in esperado]
        charts = [ch for ch in ws._charts if "kalinaporpar" in _norm(_titulo(ch))]
        if not charts:
            fail(f"27. {hoja}: no encuentro el grafico «KALINA por par»")
            malas += 1
            continue
        for ch in charts:
            if not _chart_numerico(wb, ch):
                fail(f"27. {hoja} [{_titulo(ch)}]: sin series numericas")
                malas += 1
                continue
            series = _series_tabla(wb, ch)
            if col1 not in series or col2 not in series:
                fail(f"27. {hoja} [{_titulo(ch)}]: las series {series} no son las cifras de la "
                     f"tabla ({col1}, {col2})")
                malas += 1
    if not malas:
        ok("27. E2 y E11: el grafico «KALINA por par» lee las cifras de la tabla, con series "
           "numericas")


__all__ = ["ESPERADO", "control26", "control27"]
