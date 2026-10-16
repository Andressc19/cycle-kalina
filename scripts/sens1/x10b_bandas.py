# -*- coding: utf-8 -*-
"""Sensibilidad 1 - x10b: eps_cond minima con KALINA (por centro y por banda de x_b).

Los dos calculos salen de los CSV (todos los estudios, sin el estudio 0 de referencia): la
eps_cond minima con KALINA de cada centro con el estudio y la P_baja del punto que la logra, y
la eps_cond minima con KALINA de cada banda de x_b con el numero de puntos y la P_baja mediana.
"""

from x1_cargar import CENTRO_TXT
from x2_formato import tabla
from x5_graficos import grafico_sobre_tabla

CENTROS = [CENTRO_TXT["C1"], CENTRO_TXT["C2"], CENTRO_TXT["C3"], CENTRO_TXT["C4"]]
BANDAS_XB = [(0.30, 0.45), (0.45, 0.55), (0.55, 0.65), (0.65, 0.75), (0.75, 0.85), (0.85, 0.95)]


def _r(x, d=3):
    if x is None:
        return None
    try:
        v = float(x)
    except Exception:
        return None
    if v != v or v in (float("inf"), float("-inf")):
        return None
    return round(v, d)


def min_epscond_centro(df):
    """[Centro, eps_cond minima con KALINA, estudio, P_baja] por centro (todos los estudios)."""
    filas = []
    for cen in CENTROS:
        d = df[(df["centro"] == cen) & df["kalina"]]
        if len(d) == 0:
            filas.append([cen, None, None, None])
            continue
        m = d["eps_cond"].min()
        dm = d[d["eps_cond"] == m]
        r = dm.loc[dm["P_baja"].idxmin()]
        filas.append([cen, _r(m), int(r["estudio"]), _r(r["P_baja"], 1)])
    return filas


def filas_bandas_xb(df):
    """[banda, eps_cond minima con KALINA, n KALINA, P_baja mediana] de las 6 bandas de x_b."""
    k = df[(df["estudio"] >= 1) & df["kalina"]]
    filas = []
    for i, (a, b) in enumerate(BANDAS_XB):
        if i == 0:                       # la primera banda es cerrada por la izquierda
            s = k[(k["x_b"] >= a) & (k["x_b"] <= b)]
        else:
            s = k[(k["x_b"] > a) & (k["x_b"] <= b)]
        if len(s) == 0:
            filas.append([f"{a:.2f}-{b:.2f}", None, 0, None])
        else:
            filas.append([f"{a:.2f}-{b:.2f}", _r(s["eps_cond"].min()), int(s.shape[0]),
                          _r(s["P_baja"].median(), 1)])
    return filas


def tabla_bandas(ws, f, df, titulo_chart):
    """Escribe la tabla por banda de x_b y su grafico de barras; devuelve la fila siguiente libre."""
    filas = filas_bandas_xb(df)
    enc = f
    tabla(ws, f, ["Banda de x_b (-)", "ε_cond mínima con KALINA (-)", "n KALINA (total)",
                  "P_baja mediana (kPa)"], filas, anchos=[16, 18, 14, 16],
          clases=None, clave_fila=None)
    return grafico_sobre_tabla(
        ws, enc, len(filas), [2], titulo=titulo_chart, x="Banda de x_b (-)",
        y="ε_cond mínima (-)",
        nota_txt="Incluye: la ε_cond mínima con KALINA (total) de todos los estudios en cada "
                 "banda de x_b, con el número de puntos KALINA y la P_baja mediana. Fuente: los "
                 "CSV de resultados/.")


__all__ = ["CENTROS", "BANDAS_XB", "min_epscond_centro", "filas_bandas_xb", "tabla_bandas"]
