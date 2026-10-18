# -*- coding: utf-8 -*-
"""Sensibilidad 1 - x4b: secciones propias de la hoja E14 (estudio 14, LHS de 9 variables).

Escribe la tabla de clases (con su grafico apilado), las ventanas p10/mediana/p90 de las 9
variables, el PRCC con η y el KS de cada variable (con su grafico) y las causas de los
NO_CONVERGIO (con su grafico). Todo sale del DataFrame (los CSV).
"""

from x1_cargar import CENTRO_TXT
from x2_formato import subtitulo, tabla
from x4a_ronda3 import VARS_N8, VAR_TXT_LARGO, causas_por_centro, ks_d, prcc, ventana
from x5_graficos import grafico_sobre_tabla
from x5b_graficos_a import fuente
from x6_sintesis import COLOR_CLASE

ENC_CLASES = ["Centro", "KALINA (total)", "de ellos dentro del rango experimental",
              "de ellos fuera del rango experimental", "CORREGIBLE", "NO_CONVERGIO",
              "INVIABLE", "Total"]


def _r(x, d=4):
    return None if x is None else round(float(x), d)


def _tabla_clases(ws, f, d, titulo_chart):
    """Tabla de clases por centro del estudio 14 + grafico apilado de las 4 clases."""
    filas = []
    for cen in (CENTRO_TXT["C3"], CENTRO_TXT["C4"]):
        s = d[d["centro"] == cen]
        k = s[s["clasificacion"] == "KALINA"]
        dentro = int((k["en_rango"] & ~k["fuera_rango"]).sum())
        filas.append([cen, int(k.shape[0]), dentro, int(k["fuera_rango"].sum()),
                      int((s["clasificacion"] == "CORREGIBLE").sum()),
                      int((s["clasificacion"] == "NO_CONVERGIO").sum()),
                      int((s["clasificacion"] == "INVIABLE").sum()), len(s)])
    enc = f
    tabla(ws, f, ENC_CLASES, filas, anchos=[20, 12, 22, 22, 14, 14, 12, 10])
    return grafico_sobre_tabla(
        ws, enc, len(filas), [2, 5, 6, 7],
        titulo=titulo_chart, x="Centro", y="Numero de puntos", apiladas=True,
        colores=COLOR_CLASE,
        nota_txt="Incluye: los puntos del muestreo LHS de 9 variables (C3 y C4). Cada barra "
                 "apila KALINA (total), CORREGIBLE, NO_CONVERGIO e INVIABLE; la suma es el "
                 f"total del centro. Fuente: {fuente(14)}.")


def _tabla_ventanas(ws, f, d):
    """Ventanas p10 / mediana / p90 de las 9 variables entre los KALINA (total)."""
    filas = []
    for var in VARS_N8:
        for cen in (CENTRO_TXT["C3"], CENTRO_TXT["C4"]):
            k = d[(d["centro"] == cen) & d["kalina"]]
            p10, med, p90, n = ventana(list(k[var]))
            if n:
                filas.append([VAR_TXT_LARGO[var], cen, _r(p10), _r(med), _r(p90), n])
    _, ultima, _ = tabla(ws, f, ["Variable", "Centro", "p10", "Mediana", "p90",
                                 "n KALINA (total)"], filas,
                         anchos=[16, 20, 12, 12, 12, 14])
    return ultima + 2


def _tabla_prcc_ks(ws, f, d):
    """PRCC con η y KS de cada variable, por centro, con grafico de |PRCC|."""
    pr, ks = {}, {}
    for cen in (CENTRO_TXT["C3"], CENTRO_TXT["C4"]):
        k = d[(d["centro"] == cen) & d["kalina"]]
        resto = d[(d["centro"] == cen) & d["clasificacion"].isin(["CORREGIBLE", "INVIABLE"])]
        pr[cen] = prcc(k)
        ks[cen] = ks_d(k, resto)
    c3, c4 = CENTRO_TXT["C3"], CENTRO_TXT["C4"]
    filas = []
    for var in VARS_N8:
        p3, p4 = pr[c3][var], pr[c4][var]
        filas.append([VAR_TXT_LARGO[var], _r(p3, 3),
                      _r(abs(p3), 3) if p3 is not None else None, _r(ks[c3][var], 3),
                      _r(p4, 3), _r(abs(p4), 3) if p4 is not None else None,
                      _r(ks[c4][var], 3)])
    enc = f
    tabla(ws, f, ["Variable", "PRCC C3", "|PRCC| C3", "KS C3", "PRCC C4", "|PRCC| C4",
                  "KS C4"], filas, anchos=[16, 10, 10, 10, 10, 10, 10])
    return grafico_sobre_tabla(
        ws, enc, len(filas), [3, 6],
        titulo="E14. |PRCC| con η por variable y centro", x="Variable", y="|PRCC| (-)",
        nota_txt="Incluye: el valor absoluto del PRCC con η entre los KALINA (total) de cada "
                 f"variable, por centro. Fuente: {fuente(14)}.")


def _tabla_causas(ws, f, d):
    """Causas de los NO_CONVERGIO agrupadas por centro, con grafico de barras."""
    filas, centros = causas_por_centro(d)
    enc = f
    tabla(ws, f, ["Causa del NO_CONVERGIO"] + centros + ["Total"], filas,
          anchos=[36, 10, 10, 10])
    return grafico_sobre_tabla(
        ws, enc, len(filas), [2, 3],
        titulo="E14. Causas de los NO_CONVERGIO por centro", x="Causa del NO_CONVERGIO",
        y="Numero de puntos",
        nota_txt="Incluye: los NO_CONVERGIO del muestreo agrupados por causa del motor "
                 f"(«otros» recoge los mensajes no clasificados). Fuente: {fuente(14)}.")


def _e14(ws, df, f):
    d = df[df["estudio"] == 14]
    f = subtitulo(ws, f, "1. Clases por centro (muestreo LHS de 9 variables)")
    f = _tabla_clases(ws, f, d, "E14. Puntos por clase y centro")
    f = subtitulo(ws, f, "2. Ventanas p10 / mediana / p90 de las 9 variables entre los KALINA "
                         "(total)")
    f = _tabla_ventanas(ws, f, d)
    f = subtitulo(ws, f, "3. PRCC con η y estadistico KS de cada variable, por centro")
    f = _tabla_prcc_ks(ws, f, d)
    f = subtitulo(ws, f, "4. Causas de los NO_CONVERGIO")
    return _tabla_causas(ws, f, d)


def secciones_extra(ws, n, df, f):
    """Secciones propias de los estudios 14, 15 y 16 (van en su hoja de resumen)."""
    if n == 14:
        return _e14(ws, df, f)
    if n in (15, 16):
        from x4c_resumenes_c import _e15, _e16
        return _e15(ws, df, f) if n == 15 else _e16(ws, df, f)
    return f
