# -*- coding: utf-8 -*-
"""Sensibilidad 1 - x8c: controles 8, 9 y 10 de x8 (tablas de clases, S1 y sintesis S2-S4)."""

from x1_cargar import etiqueta_centro


def _norm(s):
    t = str(s).lower()
    for a, b in (("ε", "eps"), ("η", "eta"), ("°", " "), (" ", "")):
        t = t.replace(a, b)
    return t


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _fila_encabezado(ws, primera_palabra):
    """Fila (1-based) cuyo primer texto empieza por `primera_palabra`, o None."""
    for i in range(1, ws.max_row + 1):
        v = ws.cell(i, 1).value
        if isinstance(v, str) and _norm(v).startswith(_norm(primera_palabra)):
            return i
    return None


def _filas_datos(ws, fila_enc):
    """Filas con contenido justo debajo de un encabezado, hasta la primera fila vacia."""
    filas = []
    i = fila_enc + 1
    while i <= ws.max_row and any(ws.cell(i, j).value not in (None, "") for j in range(1, 9)):
        filas.append(i)
        i += 1
    return filas


def _cuenta_centro(sub, etiqueta):
    """[KALINA, dentro, fuera, CORREGIBLE, NO_CONVERGIO, INVIABLE, Total] para un centro."""
    etqs = sub["centro"].map(etiqueta_centro)
    s = sub[etqs == etiqueta]
    k = s[s["clasificacion"] == "KALINA"]
    dentro = int((k["en_rango"] & ~k["fuera_rango"]).sum())
    fuera = int(k["fuera_rango"].sum())
    return [int(k.shape[0]), dentro, fuera,
            int((s["clasificacion"] == "CORREGIBLE").sum()),
            int((s["clasificacion"] == "NO_CONVERGIO").sum()),
            int((s["clasificacion"] == "INVIABLE").sum()),
            int(s.shape[0])]


def control8(wb, df, ok, fail):
    """En cada hoja E0..E11, la tabla de clases por centro suma los puntos del estudio."""
    malas = 0
    for e in range(12):
        hojas = [s for s in wb.sheetnames if s.startswith(f"E{e} ") and "Datos" not in s]
        if not hojas:
            continue
        ws = wb[hojas[0]]
        enc = _fila_encabezado(ws, "Centro")
        if enc is None or _norm(ws.cell(enc, 2).value) != _norm("KALINA (total)") or \
                _norm(ws.cell(enc, 8).value) != "total":
            fail(f"8. estudio {e}: no encuentro la tabla de clases por centro")
            malas += 1
            continue
        sub = df[df["estudio"] == e]
        suma_total = 0
        for i in _filas_datos(ws, enc):
            cen = ws.cell(i, 1).value
            vals = [ws.cell(i, j).value for j in range(2, 9)]
            etiqueta = etiqueta_centro("" if cen in (None, "") else cen)
            esperado = _cuenta_centro(sub, etiqueta)
            if vals != esperado:
                fail(f"8. estudio {e} centro {etiqueta}: {vals} != CSV {esperado}")
                malas += 1
            if vals[6] != vals[0] + vals[3] + vals[4] + vals[5]:
                fail(f"8. estudio {e}: Total {vals[6]} != suma de clases")
                malas += 1
            suma_total += vals[6]
        if suma_total != len(sub):
            fail(f"8. estudio {e}: Total {suma_total} != puntos {len(sub)}")
            malas += 1
    if not malas:
        ok("8. tabla de clases por centro: total y filas coinciden con los CSV en E0..E11")


def control9(wb, df, ok, fail):
    """S1: la columna Total = suma de las 4 clases = puntos del estudio."""
    ws = wb["Conclusion consolidada"]
    enc = _fila_encabezado(ws, "Estudio")
    if enc is None or _norm(ws.cell(enc, 8).value) != "total":
        fail("9. no encuentro la tabla S1 (Estudio ... Total)")
        return
    malas = 0
    for i in _filas_datos(ws, enc):
        est = ws.cell(i, 1).value
        vals = [ws.cell(i, j).value for j in range(2, 9)]
        total = vals[6]
        if total != vals[0] + vals[3] + vals[4] + vals[5]:
            fail(f"9. estudio {est}: Total {total} != suma de clases")
            malas += 1
        if total != int((df["estudio"] == est).sum()):
            fail(f"9. estudio {est}: Total {total} != puntos")
            malas += 1
    if not malas:
        ok("9. S1: Total = suma de las 4 clases = puntos del estudio")


def control10(wb, df, ok, fail):
    """S2 (40 filas), S3 y S4 presentes con valores numericos."""
    ws = wb["Conclusion consolidada"]
    malas = 0
    enc = None
    for i in range(1, ws.max_row + 1):
        v = ws.cell(i, 1).value
        if isinstance(v, str) and _norm(v).startswith("variable") and \
                _norm(ws.cell(i, 2).value) == "centro":
            enc = i
            break
    if enc is None:
        fail("10. no encuentro la tabla S2 (Variable | Centro ...)")
        malas += 1
    else:
        filas = _filas_datos(ws, enc)
        if len(filas) != 40:
            fail(f"10. S2 tiene {len(filas)} filas (esperado 40)")
            malas += 1
        for i in filas:
            if not all(_num(ws.cell(i, j).value) for j in (3, 4, 5)):
                fail(f"10. S2 fila {i}: valores no numericos")
                malas += 1
                break
    for etq in ("S3", "S4"):
        hay = any(isinstance(ws.cell(i, 1).value, str) and
                  ws.cell(i, 1).value.startswith(etq + ".") for i in range(1, ws.max_row + 1))
        if not hay:
            fail(f"10. falta la seccion {etq}")
            malas += 1
    if not malas:
        ok("10. S2 (40 filas) y S3 y S4 presentes con valores")
