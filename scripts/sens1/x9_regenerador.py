# -*- coding: utf-8 -*-
"""Sensibilidad 1 - x9: hoja 'E12 Regenerador y turbina'."""

import math

from x1_cargar import CENTRO_TXT, CENTROS as CENTROS_DEF, bases_por_centro
from x2_formato import titulo, condiciones, subtitulo, tabla
from x5_graficos import bloque, grafico_sobre_tabla


CENTROS = [CENTRO_TXT["C1"], CENTRO_TXT["C2"], CENTRO_TXT["C3"], CENTRO_TXT["C4"]]
EST_BARRIDO = (1, 10)


def _r(x, d=4):
    if x is None:
        return None
    try:
        v = float(x)
    except Exception:
        return None
    if math.isnan(v) or math.isinf(v):
        return None
    return round(v, d)


def _barrido(df, var):
    """Puntos del barrido de `var` (estudios 1 y 10) indexados por (centro, valor).

    Incluye el punto base de cada centro con el valor de esa variable en el centro (su `valor`
    en el CSV esta vacio por ser la fila de referencia), de modo que la tabla tiene los 12
    niveles 0.40-0.95 paso 0.05.
    """
    m = {}
    d = df[df["estudio"].isin(EST_BARRIDO) & (df["variable"] == var)]
    for _, r in d.iterrows():
        m[(r["centro"], round(float(r["valor"]), 2))] = r
    for cen, brow in bases_por_centro(df).items():
        bv = CENTROS_DEF.get(cen, {}).get(var)
        if bv is not None:
            m.setdefault((cen, round(float(bv), 2)), brow)
    return m


def _tabla_metric(ws, f, df, var, cat_lbl, ylbl, fn, titulo_chart=None, tipo="linea", x_vals_func=None):
    m = _barrido(df, var)
    vals = sorted({k[1] for k in m})
    filas = []
    for v in vals:
        row = [v]
        for c in CENTROS:
            rr = m.get((c, v))
            row.append(_r(fn(rr)) if rr is not None else None)
        filas.append(row)
    x_vals = vals if x_vals_func is None else x_vals_func(vals)
    return bloque(ws, f,
                  titulo=titulo_chart or f"E12. {ylbl} frente a {cat_lbl}",
                  encabezados=[cat_lbl] + CENTROS,
                  filas=filas,
                  tipo=tipo,
                  x=cat_lbl,
                  y=ylbl,
                  x_vals=x_vals,
                  nota_txt="Incluye: todos los puntos del barrido de una variable en los 4 centros "
                           "(estudios 1 y 10).")


def _tabla_clase(ws, f, df, var, cat_lbl):
    m = _barrido(df, var)
    vals = sorted({k[1] for k in m})
    filas = []
    for v in vals:
        row = [v]
        for c in CENTROS:
            rr = m.get((c, v))
            row.append(rr["clasificacion"] if rr is not None else "")
        filas.append(row)
    tabla(ws, f, [cat_lbl] + CENTROS, filas, anchos=[12] + [20] * 4, clases=None, clave_fila=None)
    return f + 2 + len(filas)


def seccion_regenerador(ws, f, df):
    f = subtitulo(ws, f, "1. Regenerador frente a ε_reg (estudios 1 y 10)")
    f = _tabla_metric(ws, f, df, "eps_reg", "ε_reg (-)", "Qreg (kW por kg/s)",
                      lambda r: r["Qreg"] / r["m_b"] if r is not None else None,
                      titulo_chart="E12. Qreg por kg/s frente a ε_reg (4 centros)")
    f = _tabla_metric(ws, f, df, "eps_reg", "ε_reg (-)", "Qreg/Qi (-)",
                      lambda r: r["qreg_qi"] if r is not None else None,
                      titulo_chart="E12. Qreg/Qi frente a ε_reg (4 centros)")
    f = _tabla_metric(ws, f, df, "eps_reg", "ε_reg (-)", "η (%)",
                      lambda r: r["eta_pct"] if r is not None else None,
                      titulo_chart="E12. η frente a ε_reg (4 centros)")
    f = _tabla_clase(ws, f, df, "eps_reg", "ε_reg (-)")
    return f


def _tabla_metric_eta(ws, f, df, var, cat_lbl, ylbl, fn, titulo_chart=None):
    m = _barrido(df, var)
    vals = sorted({k[1] for k in m})
    filas = []
    for v in vals:
        row = [v]
        for c in CENTROS:
            rr = m.get((c, v))
            row.append(_r(fn(rr)) if rr is not None else None)
        filas.append(row)
    return bloque(ws, f,
                  titulo=titulo_chart or f"E12. {ylbl} frente a {cat_lbl}",
                  encabezados=[cat_lbl] + CENTROS,
                  filas=filas,
                  tipo="linea",
                  x=cat_lbl,
                  y=ylbl,
                  x_vals=vals,
                  nota_txt="Incluye: los puntos del barrido de una variable en los 4 centros "
                           "(estudios 1 y 10).")


def seccion_turbina(ws, f, df):
    f = subtitulo(ws, f, "2. Turbina frente a η_t (estudios 1 y 10)")
    f = _tabla_metric_eta(ws, f, df, "eta_t", "η_t (-)", "Δh turbina (kJ/kg)",
                          lambda r: r["dh_turb"] if r is not None else None,
                          titulo_chart="E12. Δh de turbina frente a η_t (4 centros)")
    f = _tabla_metric_eta(ws, f, df, "eta_t", "η_t (-)", "Wnet (kW por kg/s)",
                          lambda r: r["Wnet"] / r["m_b"] if r is not None else None,
                          titulo_chart="E12. Wnet frente a η_t (4 centros)")
    f = _tabla_metric_eta(ws, f, df, "eta_t", "η_t (-)", "η (%)",
                          lambda r: r["eta_pct"] if r is not None else None,
                          titulo_chart="E12. η frente a η_t (4 centros)")
    return f


def _fila_banda(banda, s):
    if len(s) == 0:
        return [banda, 0, None, None, None, None, None, None, None]
    s = s.copy()
    s["Wnet_kg"] = s["Wnet"] / s["m_b"]
    return [
        banda,
        len(s),
        _r(s["dh_turb"].min()),
        _r(s["dh_turb"].median()),
        _r(s["dh_turb"].max()),
        _r(s["Wnet_kg"].min()),
        _r(s["Wnet_kg"].median()),
        _r(s["Wnet_kg"].max()),
        _r(s["eta_pct"].median()),
    ]


def seccion_rp(ws, f, df):
    f = subtitulo(ws, f, "3. Turbina frente a r_P = P_alta/P_baja (todos los KALINA)")
    f = condiciones(ws, f, [
        "Todos los KALINA (total) de todos los estudios. r_P grande sin salto de presión útil "
        "(p. ej. P_alta 1000 kPa) da η de ~0.4 % (puntos triviales)."])
    d = df[df["kalina"]].copy()
    bandas = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9)]
    filas = []
    for a, b in bandas:
        s = d[(d["rp"] >= a) & (d["rp"] < b)]
        filas.append(_fila_banda(f"{a}-{b}", s))
    s = d[d["rp"] >= 9]
    filas.append(_fila_banda("> 9", s))
    f_enc = f
    tabla(ws, f,
          ["r_P = P_alta/P_baja (-)", "n", "dh min (kJ/kg)", "dh mediana (kJ/kg)",
           "dh max (kJ/kg)", "Wnet min (kW por kg/s)", "Wnet mediana (kW por kg/s)",
           "Wnet max (kW por kg/s)", "eta mediana (%)"],
          filas,
          anchos=[18, 8, 12, 12, 12, 12, 12, 12, 12],
          clases=None,
          clave_fila=None)
    f = grafico_sobre_tabla(ws, f_enc, len(filas), [4],
                            titulo="E12. Mediana de dh de turbina por banda de r_P",
                            x="r_P = P_alta/P_baja (-)",
                            y="dh mediana (kJ/kg)",
                            cat_col=1,
                            tipo="barras",
                            nota_txt="Incluye: todos los KALINA (total) de todos los estudios. Fuente: los CSV de resultados/.")
    return f


def hoja_e12(wb, df):
    ws = wb.create_sheet("E12 Regenerador y turbina")
    f = 1
    f = titulo(ws, f, "E12. Comportamiento del regenerador y de la turbina")
    f = condiciones(ws, f, [
        "Datos leídos directamente de los CSV (sin inventar cifras). Barridos de una variable "
        "de estudios 1 y 10, y análisis global de todos los KALINA para r_P."])
    f = seccion_regenerador(ws, f, df)
    f = seccion_turbina(ws, f, df)
    f = seccion_rp(ws, f, df)
    return "E12 Regenerador y turbina"
