# -*- coding: utf-8 -*-
"""Sensibilidad 1 - x8g: controles 20 y 21 de x8 (piso del condensador por centro y por banda).

20 E13 §3 con la eps_cond minima por centro de todos los estudios (valores del director,
contrastados con los CSV); 21 la tabla por banda de x_b en E13 y en S3 (c) con su grafico de
series numericas.
"""

from x1_cargar import CENTRO_TXT
from x8b_graficos import _vref, _parse, _hay_numero, _titulo
from x8c_controles import _norm, _num, _filas_datos

import unicodedata


def _plano(t):
    """Texto normalizado y sin acentos (para comparar «mínima»/«Húsavík»)."""
    d = unicodedata.normalize("NFKD", _norm(t))
    return "".join(c for c in d if not unicodedata.combining(c))


BANDAS_XB = [("0.30-0.45", 0.70, 113), ("0.45-0.55", 0.65, 461), ("0.55-0.65", 0.75, 207),
             ("0.65-0.75", 0.80, 685), ("0.75-0.85", 0.85, 434), ("0.85-0.95", 0.85, 342)]

# centro: (eps_cond minima, estudio, P_baja del punto que la logra) dados por el director.
EPS_CENTRO = {"c1": (0.80, 3, 520.0), "c2": (0.65, 2, 563.6),
              "c3": (0.85, 14, 570.0), "c4": (0.85, 14, 760.0)}


def _enc_cond(ws):
    """Fila del encabezado «Centro | ε_cond mínima ...» de la E13, o None."""
    for i in range(1, ws.max_row + 1):
        v = ws.cell(i, 1).value
        if isinstance(v, str) and _plano(v) == "centro" and \
                _plano(ws.cell(i, 2).value).startswith("eps_condminima"):
            return i
    return None


def control20(wb, df, ok, fail):
    """E13 §3: eps_cond minima por centro (0.80 / 0.65 / 0.85 / 0.85) con estudio y P_baja."""
    ws = wb["E13 Preseleccion de equipos"]
    enc = _enc_cond(ws)
    if enc is None:
        fail("20. E13: no encuentro la tabla de eps_cond minima con KALINA por centro")
        return
    malas, vistos = 0, set()
    filas = _filas_datos(ws, enc)
    if len(filas) != 4:
        fail(f"20. E13: la tabla tiene {len(filas)} filas (esperado 4)")
        malas += 1
    for i in filas:
        cen = ws.cell(i, 1).value
        clave = _norm(cen)[:2]
        if clave not in EPS_CENTRO:
            fail(f"20. E13: centro inesperado '{cen}'")
            malas += 1
            continue
        vistos.add(clave)
        eps, est, pb = EPS_CENTRO[clave]
        v2, v3, v4 = ws.cell(i, 2).value, ws.cell(i, 3).value, ws.cell(i, 4).value
        if not _num(v2) or round(float(v2), 2) != eps:
            fail(f"20. E13 {cen}: eps_cond minima {v2} != {eps}")
            malas += 1
        if not _num(v3) or int(v3) != est:
            fail(f"20. E13 {cen}: estudio {v3} != {est}")
            malas += 1
        if not _num(v4) or abs(float(v4) - pb) > 0.01:
            fail(f"20. E13 {cen}: P_baja {v4} != {pb}")
            malas += 1
        for k, nom in zip((5, 6, 7), ("eps_reg", "eps_HRVG", "eta_t")):
            if not _num(ws.cell(i, k).value):
                fail(f"20. E13 {cen}: celda {nom} vacia")
                malas += 1
    if vistos != set(EPS_CENTRO):
        fail(f"20. E13: centros hallados {sorted(vistos)} != {sorted(EPS_CENTRO)}")
        malas += 1
    # Contraste con los CSV: la eps_cond minima y su P_baja salen del DataFrame.
    for clave, raw in (("c1", "C1"), ("c2", "C2"), ("c3", "C3"), ("c4", "C4")):
        d = df[(df["centro"] == CENTRO_TXT[raw]) & df["kalina"]]
        if len(d) == 0:
            fail(f"20. CSV {raw}: sin KALINA")
            malas += 1
            continue
        m = round(float(d["eps_cond"].min()), 2)
        dm = d[d["eps_cond"] == d["eps_cond"].min()]
        pb = round(float(dm["P_baja"].min()), 1)
        eps, _est, pbe = EPS_CENTRO[clave]
        if abs(m - eps) > 0.005 or abs(pb - pbe) > 0.1:
            fail(f"20. CSV {raw}: eps_cond minima {m} (P_baja {pb}) != {eps} ({pbe})")
            malas += 1
    if not malas:
        ok("20. E13 seccion 3: eps_cond minima por centro 0.80 / 0.65 / 0.85 / 0.85 (con estudio "
           "y P_baja), igual que los CSV")


def _tabla_bandas_en(ws):
    for i in range(1, ws.max_row + 1):
        v = ws.cell(i, 1).value
        if isinstance(v, str) and _norm(v).startswith("bandadex_b"):
            return i
    return None


def _chart_numerico(wb, ch):
    for se in ch.series:
        ref = _vref(se)
        if ref is None:
            continue
        h, c1, r1, c2, r2 = _parse(ref)
        if h in wb.sheetnames and _hay_numero(wb[h], c1, r1, c2, r2):
            return True
    return False


def control21(wb, ok, fail):
    """Tabla por banda de x_b (6 bandas) en E13 y en S3 (c), con grafico de series numericas."""
    malas = 0
    for hoja in ("E13 Preseleccion de equipos", "Conclusion consolidada"):
        ws = wb[hoja]
        enc = _tabla_bandas_en(ws)
        if enc is None:
            fail(f"21. {hoja}: falta la tabla por banda de x_b")
            malas += 1
            continue
        filas = _filas_datos(ws, enc)
        if len(filas) != 6:
            fail(f"21. {hoja}: la tabla por banda de x_b tiene {len(filas)} filas (esperado 6)")
            malas += 1
        for k, i in enumerate(filas):
            if k >= len(BANDAS_XB):
                break
            banda, eps, n = BANDAS_XB[k]
            vb, ve, vn = ws.cell(i, 1).value, ws.cell(i, 2).value, ws.cell(i, 3).value
            if _norm(vb) != _norm(banda):
                fail(f"21. {hoja}: banda r{i} '{vb}' != {banda}")
                malas += 1
            if not _num(ve) or round(float(ve), 2) != eps:
                fail(f"21. {hoja} banda {banda}: eps_cond minima {ve} != {eps}")
                malas += 1
            if not _num(vn) or int(vn) != n:
                fail(f"21. {hoja} banda {banda}: n {vn} != {n}")
                malas += 1
        hay = any("bandadex_b" in _norm(_titulo(ch)) and _chart_numerico(wb, ch)
                  for ch in ws._charts)
        if not hay:
            fail(f"21. {hoja}: el grafico de la tabla por banda de x_b no tiene series numericas")
            malas += 1
    if not malas:
        ok("21. tabla por banda de x_b (6 bandas y sus valores) en E13 y en S3 (c), con grafico "
           "de series numericas")


__all__ = ["BANDAS_XB", "EPS_CENTRO", "control20", "control21", "_chart_numerico", "_plano"]
