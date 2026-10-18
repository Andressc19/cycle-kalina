# -*- coding: utf-8 -*-
"""Sensibilidad 1 - x8b: controles 4 y 5 de x8 (graficos nativos, estrictos).

Control 4: para CADA grafico del libro (a) >= 1 serie; (b) cada serie con referencia de valores
a celdas del mismo libro, en hoja visible y con al menos una celda numerica; (c) el numero de
puntos de cada serie coincide con el de su tabla (la columna de categorias); (d) imprime una
linea por grafico (hoja, titulo, numero de series, numero de puntos). Falla si hay < 20 graficos
o si alguna hoja E0…E11 de resumen se queda sin ninguno.

Control 5: cada grafico ocupa 16 cm x 8 cm (10 columnas x 16 filas); falla si dos graficos de la
misma hoja se solapan o si una tabla (celda con cuadricula) cae dentro del rectangulo de un
grafico.
"""
import re

ANCHO_COL, ALTO_FILA = 10, 16
CEL = re.compile(r"([A-Z]{1,3})\$?(\d+)")


def _ascii(s):
    """Titulos solo-ASCII para imprimir en consola (Windows cp1252 no traga η, ε, °)."""
    for a, b in (("η", "eta"), ("ε", "eps"), ("°", " deg"), ("·", "-"), ("–", "-"), ("—", "-")):
        s = s.replace(a, b)
    return s.encode("ascii", "replace").decode("ascii")


def _celda(t):
    m = CEL.match(t.replace("$", ""))
    return m.group(1), int(m.group(2))


def _col_letra_a_num(letras):
    n = 0
    for ch in letras:
        n = n * 26 + (ord(ch) - 64)
    return n


def _parse(ref):
    """'Hoja!'!$B$6:$B$17' -> (hoja, c1, r1, c2, r2) en 1-based."""
    hoja, rng = ref.rsplit("!", 1)
    hoja = hoja.strip().strip("'")
    a, b = rng.split(":")
    la, ra = _celda(a)
    lb, rb = _celda(b)
    return hoja, _col_letra_a_num(la), ra, _col_letra_a_num(lb), rb


def _vref(se):
    v = getattr(se, "val", None)
    if v is not None and getattr(v, "numRef", None) is not None:
        return v.numRef.f
    y = getattr(se, "yVal", None)
    if y is not None and getattr(y, "numRef", None) is not None:
        return y.numRef.f
    return None


def _cref(se):
    c = getattr(se, "cat", None)
    if c is not None:
        if getattr(c, "numRef", None) is not None:
            return c.numRef.f
        if getattr(c, "strRef", None) is not None:
            return c.strRef.f
    x = getattr(se, "xVal", None)
    if x is not None:
        if getattr(x, "numRef", None) is not None:
            return x.numRef.f
        if getattr(x, "strRef", None) is not None:
            return x.strRef.f
    return None


def _titulo(ch):
    t = getattr(ch, "title", None)
    if t is not None and t.tx is not None and t.tx.rich is not None and t.tx.rich.p:
        return "".join(r.t for r in (t.tx.rich.p[0].r or []))
    return "(sin titulo)"


def x8b_textos(ch):
    """Todos los textos de un grafico (titulo, titulos de eje y nombres de serie), para control 7."""
    textos = [_titulo(ch)]
    for eje in (getattr(ch, "x_axis", None), getattr(ch, "y_axis", None)):
        t = getattr(eje, "title", None) if eje is not None else None
        if t is not None and t.tx is not None and t.tx.rich is not None and t.tx.rich.p:
            textos.append("".join(r.t for r in (t.tx.rich.p[0].r or [])))
    for se in ch.series:
        tx = getattr(se, "tx", None)
        if tx is None:
            continue
        if getattr(tx, "v", None) is not None:
            textos.append(str(tx.v))
        elif getattr(tx, "strRef", None) is not None:
            textos.append(tx.strRef.f)
    return textos


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _hay_numero(ws, c1, r1, c2, r2):
    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            if _num(ws.cell(r, c).value):
                return True
    return False


def control4(wb, ok, fail, hojas_estudio):
    total, por_hoja, lineas = 0, {}, []
    for s in wb.sheetnames:
        for ch in wb[s]._charts:
            total += 1
            por_hoja[s] = por_hoja.get(s, 0) + 1
            tit = _titulo(ch)
            series = ch.series
            if len(series) < 1:
                fail(f"4 {s} [{tit}]: 0 series")
                lineas.append((s, tit, 0, 0))
                continue
            largos = []
            for k, se in enumerate(series):
                ref = _vref(se)
                if ref is None:
                    fail(f"4 {s} [{tit}]: serie {k} sin referencia de valores")
                    continue
                hoja, c1, r1, c2, r2 = _parse(ref)
                if hoja not in wb.sheetnames or wb[hoja].sheet_state != "visible":
                    fail(f"4 {s} [{tit}]: serie {k} apunta a hoja no visible {hoja}")
                elif not _hay_numero(wb[hoja], c1, r1, c2, r2):
                    fail(f"4 {s} [{tit}]: serie {k} sin celdas numericas en {ref}")
                largos.append(r2 - r1 + 1)
            cref = _cref(series[0])
            largo_cat = None
            if cref is not None:
                _, _, cr1, _, cr2 = _parse(cref)
                largo_cat = cr2 - cr1 + 1
            if len(set(largos)) > 1:
                fail(f"4 {s} [{tit}]: series con distinto numero de puntos {largos}")
            if largo_cat is not None and any(x != largo_cat for x in largos):
                fail(f"4 {s} [{tit}]: puntos de serie {largos} != tabla ({largo_cat})")
            lineas.append((s, tit, len(series), largos[0] if largos else 0))
    for s, tit, ns, np_ in lineas:
        print("   grafico: %-28s | %-58s | series=%2d | puntos=%d" % (_ascii(s), _ascii(tit), ns, np_))
    if total < 20:
        fail(f"4 total: {total} graficos (se exigen >= 20)")
    else:
        ok(f"4. {total} graficos, cada uno con >= 1 serie y valores numericos visibles")
    for e in hojas_estudio:
        if por_hoja.get(e, 0) < 1:
            fail(f"4 hoja {e}: sin ningun grafico")
    return total


def _solapan(a, b):
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


def _cuadricula(cell):
    b = cell.border
    return any(getattr(b, lado, None) is not None and getattr(b, lado).style
               for lado in ("left", "right", "top", "bottom"))


def control5(wb, ok, fail):
    n_graf, choques = 0, 0
    for s in wb.sheetnames:
        ws = wb[s]
        rects = []
        for ch in ws._charts:
            r0 = ch.anchor._from.row + 1
            c0 = ch.anchor._from.col + 1
            rects.append((r0, c0, r0 + ALTO_FILA - 1, c0 + ANCHO_COL - 1))
        n_graf += len(rects)
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                if _solapan(rects[i], rects[j]):
                    choques += 1
                    fail(f"5 {s}: graficos en {rects[i][:2]} y {rects[j][:2]} se solapan")
        for (r0, c0, r1, c1) in rects:
            for rr in range(r0, r1 + 1):
                for cc in range(c0, c1 + 1):
                    if _cuadricula(ws.cell(rr, cc)):
                        choques += 1
                        fail(f"5 {s}: tabla en r{rr}c{cc} dentro del grafico anclado en r{r0}c{c0}")
    if not choques:
        ok(f"5. {n_graf} graficos sin solapes entre si ni con ninguna tabla")
    return n_graf
