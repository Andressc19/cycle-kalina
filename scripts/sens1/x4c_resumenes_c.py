# -*- coding: utf-8 -*-
"""Sensibilidad 1 - x4c: secciones propias de las hojas E15 y E16 (Ronda 3).

E15: KALINA por par y centro (con el base), η máxima por par y centro, matrices 7 × 7 de
clase y de η (%) por centro y par, y una línea de η frente a ε_reg (par B5).
E16: matrices 5 × 7 de clase y de η (%) por centro (P_alta × P_baja), η máxima por P_alta y
centro, KALINA por P_alta y centro, y P_alta del máximo de η por centro. Todo sale de los CSV.
"""

from x1_cargar import CENTRO_TXT, PARS, bases_por_centro
from x2_formato import nota, subtitulo, tabla
from x4a_ronda3 import VAR_TXT_LARGO, etiqueta, matriz, valores
from x5_graficos import bloque
from x5b_graficos_a import fuente, kalina_con_base

PAR_VARS = {"B5": ("eps_reg", "eta_t"), "B6": ("eps_hrvg", "T_fuente")}


def _eje(var):
    """Rótulo de eje para la celda de esquina (la temperatura va en °C, como las etiquetas)."""
    return VAR_TXT_LARGO[var].replace("(K)", "(°C)")


def _rotulo(fv, cv):
    """Rótulo de dos ejes de la celda de esquina de una matriz."""
    return f"filas: {_eje(fv)} · columnas: {_eje(cv)}"


def _eta_max(s, cen, bases):
    """η máxima (en %) de un subconjunto de un centro, incluido el punto base del centro."""
    k = s[(s["centro"] == cen) & s["kalina"]]
    v = round(float(k["eta_pct"].max()), 2) if len(k) else None
    b = bases.get(cen)
    if b is not None and b["kalina"]:
        bv = round(float(b["eta_pct"]), 2)
        v = bv if v is None else max(v, bv)
    return v


def _matrices(ws, f, d, cen, p, bases):
    """Matriz 7 × 7 de clase y de η (%) de un par en un centro (incluye el punto base)."""
    fv, cv = PAR_VARS[p]
    dd = d[(d["centro"] == cen) & (d["par"].isin([p, "base"]))]
    fvs, cvs = valores(dd, fv), valores(dd, cv)
    cab = [VAR_TXT_LARGO[fv]] + [etiqueta(cv, x) for x in cvs]
    anchos = [16] + [10] * len(cvs)
    rot = _rotulo(fv, cv)
    f = subtitulo(ws, f, f"Par {p} en {cen}")
    _, ult, _ = tabla(ws, f, [rot + " · Clase"] + cab[1:],
                      matriz(dd, fv, cv, fvs, cvs, "clase"), anchos=anchos)
    _, ult, _ = tabla(ws, ult + 2, [rot + " · η (%)"] + cab[1:],
                      matriz(dd, fv, cv, fvs, cvs, "eta"), anchos=anchos)
    return ult + 2


def _e15(ws, df, f):
    d = df[df["estudio"] == 15]
    bases = bases_por_centro(df)
    c3, c4 = CENTRO_TXT["C3"], CENTRO_TXT["C4"]
    f = subtitulo(ws, f, "1. KALINA (total) por par y centro (contando el punto base)")
    filas = [[PARS[p], kalina_con_base(d[d["par"] == p], c3, bases.get(c3)),
              kalina_con_base(d[d["par"] == p], c4, bases.get(c4))] for p in ("B5", "B6")]
    f = bloque(ws, f, titulo="E15. KALINA por par de variables y centro",
               encabezados=["Par de variables", c3, c4], filas=filas,
               x="Par de variables", y="Numero de puntos",
               nota_txt="Incluye: los KALINA de cada malla 7 × 7 y el punto base de cada centro "
                        f"(el base es un punto de cada par). Fuente: {fuente(15)}.")
    f = subtitulo(ws, f, "2. η máxima por par y centro (entre los KALINA)")
    filas = [[PARS[p], _eta_max(d[d["par"] == p], c3, bases),
              _eta_max(d[d["par"] == p], c4, bases)] for p in ("B5", "B6")]
    f = bloque(ws, f, titulo="E15. η máxima por par de variables y centro",
               encabezados=["Par de variables", c3, c4], filas=filas,
               x="Par de variables", y="eta máxima (%)",
               nota_txt="Incluye: la η máxima entre los KALINA (total) de cada par y centro, "
                        f"con el punto base. Fuente: {fuente(15)}.")
    f = subtitulo(ws, f, "3. Matrices 7 × 7 de clase y de η (%) por centro y par")
    f = _matrices(ws, f, d, c3, "B5", bases)
    f = _matrices(ws, f, d, c3, "B6", bases)
    f = _matrices(ws, f, d, c4, "B5", bases)
    f = _matrices(ws, f, d, c4, "B6", bases)
    f = nota(ws, f, "Los puntos atípicos (Δh de turbina anormalmente baja frente a sus vecinos) "
                    "de estas matrices están señalados en la hoja LEEME, sección «Puntos "
                    "atípicos».")
    f = subtitulo(ws, f, "4. η máxima frente a ε_reg (par B5, una línea por centro)")
    evs = sorted(set(valores(d[(d["centro"] == c3) & (d["par"] == "B5")], "eps_reg")) |
                 set(valores(d[(d["centro"] == c4) & (d["par"] == "B5")], "eps_reg")))
    filas = []
    for ev in evs:
        s = d[(d["par"] == "B5") & (d["eps_reg"].round(2) == ev)]
        row = [ev]
        for cen in (c3, c4):
            k = s[(s["centro"] == cen) & s["kalina"]]
            row.append(round(float(k["eta_pct"].max()), 2) if len(k) else None)
        filas.append(row)
    return bloque(ws, f, titulo="E15. η máxima frente a ε_reg (par B5, una línea por centro)",
                  encabezados=["ε_reg (-)", c3, c4], filas=filas, tipo="linea",
                  x="ε_reg (-)", y="eta máxima (%)", x_vals=evs,
                  nota_txt="Incluye: la η máxima entre los KALINA de cada nivel de ε_reg del par "
                           f"B5 (ε_reg × η_t), por centro. Fuente: {fuente(15)}.")


def _matrices_e16(ws, f, d, cen):
    """Matriz 5 × 7 de clase y de η (%) de un centro (P_alta × P_baja)."""
    dd = d[d["centro"] == cen]
    pas, pbs = valores(dd, "P_alta"), valores(dd, "P_baja")
    cab = ["P_alta (kPa)"] + [int(round(x)) for x in pbs]
    anchos = [14] + [10] * len(pbs)
    rot = _rotulo("P_alta", "P_baja")
    f = subtitulo(ws, f, cen)
    _, ult, _ = tabla(ws, f, [rot + " · Clase"] + cab[1:],
                      matriz(dd, "P_alta", "P_baja", pas, pbs, "clase"), anchos=anchos)
    _, ult, _ = tabla(ws, ult + 2, [rot + " · η (%)"] + cab[1:],
                      matriz(dd, "P_alta", "P_baja", pas, pbs, "eta"), anchos=anchos)
    return ult + 2


def _e16(ws, df, f):
    d = df[df["estudio"] == 16]
    centros = [CENTRO_TXT["C1"], CENTRO_TXT["C3"], CENTRO_TXT["C4"]]
    f = subtitulo(ws, f, "1. Matrices 5 × 7 de clase y de η (%) por centro (P_alta × P_baja)")
    for cen in centros:
        f = _matrices_e16(ws, f, d, cen)
    pas = sorted(set().union(*[set(valores(d[d["centro"] == c], "P_alta")) for c in centros]))
    f = subtitulo(ws, f, "2. η máxima por P_alta y centro")
    filas = []
    for pa in pas:
        row = [pa]
        for cen in centros:
            k = d[(d["centro"] == cen) & (d["P_alta"].round(2) == pa) & d["kalina"]]
            row.append(round(float(k["eta_pct"].max()), 2) if len(k) else None)
        filas.append(row)
    f = bloque(ws, f, titulo="E16. η máxima frente a P_alta (una línea por centro)",
               encabezados=["P_alta (kPa)"] + centros, filas=filas, tipo="linea",
               x="P_alta (kPa)", y="eta máxima (%)", x_vals=pas,
               nota_txt="Incluye: la η máxima entre los KALINA de cada P_alta (P_baja de la "
                        f"malla), por centro; vacío donde no hay KALINA. Fuente: {fuente(16)}.")
    f = subtitulo(ws, f, "3. KALINA (total) por P_alta y centro")
    filas = []
    for pa in pas:
        s = d[d["P_alta"].round(2) == pa]
        filas.append([pa] + [int(s[(s["centro"] == cen) & s["kalina"]].shape[0])
                             for cen in centros])
    f = bloque(ws, f, titulo="E16. KALINA por P_alta y centro",
               encabezados=["P_alta (kPa)"] + centros, filas=filas,
               x="P_alta (kPa)", y="Numero de puntos",
               nota_txt="Incluye: los KALINA (total) de cada P_alta de la malla, por centro. "
                        f"Fuente: {fuente(16)}.")
    f = subtitulo(ws, f, "4. P_alta del máximo de η por centro")
    filas = []
    for cen in centros:
        k = d[(d["centro"] == cen) & d["kalina"]]
        if len(k):
            r = k.loc[k["eta_pct"].idxmax()]
            filas.append([cen, float(r["P_alta"]), round(float(r["eta_pct"]), 2)])
    return bloque(ws, f, titulo="E16. P_alta del máximo de η por centro",
                  encabezados=["Centro", "P_alta del máximo de η (kPa)"], filas=filas,
                  x="Centro", y="P_alta (kPa)",
                  nota_txt="Incluye: la P_alta con mayor η entre los KALINA de cada centro. "
                           f"Fuente: {fuente(16)}.")


__all__ = ["_e15", "_e16"]
