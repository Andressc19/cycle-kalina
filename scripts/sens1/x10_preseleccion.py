# -*- coding: utf-8 -*-
"""Sensibilidad 1 - x10: hoja 'E13 Preseleccion de equipos'."""

import math

from x1_cargar import CENTRO_TXT
from x2_formato import titulo, condiciones, subtitulo, tabla
from x5_graficos import grafico_sobre_tabla
from x10b_bandas import min_epscond_centro, tabla_bandas


CENTROS = [CENTRO_TXT["C1"], CENTRO_TXT["C2"], CENTRO_TXT["C3"], CENTRO_TXT["C4"]]
M_CAUDAL = [1, 5, 10, 15, 20]


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


def _top5_por_centro(df, cen):
    d = df[(df["centro"] == cen) & df["kalina"]].copy()
    d = d.sort_values("eta_pct", ascending=False).head(5).reset_index(drop=True)
    return d.to_dict("records")


def _attr_row(label, func, tops):
    row = [label]
    for t in tops:
        row.append(func(t))
    return row


def seccion_referencia(ws, f, df):
    f = subtitulo(ws, f, "1. Diseños de referencia (5 KALINA con mayor η por centro)")
    f = condiciones(ws, f, ["Los 5 mejores KALINA (total) por η (%) de cada centro, considerando todos los estudios de ese centro."])
    for cen in CENTROS:
        tops = _top5_por_centro(df, cen)
        if len(tops) == 0:
            continue
        f = subtitulo(ws, f, cen)
        filas = [
            _attr_row("id_punto", lambda t: t["id_punto"], tops),
            _attr_row("Estudio", lambda t: int(t["estudio"]), tops),
            _attr_row("T_fuente (K)", lambda t: _r(t["T_fuente"], 2), tops),
            _attr_row("T_sumidero (K)", lambda t: _r(t["T_sumidero"], 2), tops),
            _attr_row("P_alta (kPa)", lambda t: _r(t["P_alta"], 1), tops),
            _attr_row("P_baja (kPa)", lambda t: _r(t["P_baja"], 1), tops),
            _attr_row("x_b (-)", lambda t: _r(t["x_b"], 3), tops),
            _attr_row("eta_t (-)", lambda t: _r(t["eta_t"], 3), tops),
            _attr_row("eta_p (-)", lambda t: _r(t["eta_p"], 3), tops),
            _attr_row("eps_HRVG (-)", lambda t: _r(t["eps_hrvg"], 3), tops),
            _attr_row("eps_reg (-)", lambda t: _r(t["eps_reg"], 3), tops),
            _attr_row("eps_cond (-)", lambda t: _r(t["eps_cond"], 3), tops),
            _attr_row("eta (%)", lambda t: _r(t["eta_pct"], 2), tops),
            _attr_row("dh turbina (kJ/kg)", lambda t: _r(t["dh_turb"], 2), tops),
            _attr_row("r_P = P_alta/P_baja (-)", lambda t: _r(t["rp"], 3), tops),
            _attr_row("Qreg/Qi (-)", lambda t: _r(t["qreg_qi"], 3), tops),
            _attr_row("Wnet (kW por kg/s)", lambda t: _r((t["Wnet"] / t["m_b"]) if t["m_b"] else t["Wnet"], 3), tops),
            _attr_row("Qi (kW por kg/s)", lambda t: _r((t["Qi"] / t["m_b"]) if t["m_b"] else t["Qi"], 3), tops),
            _attr_row("Qreg (kW por kg/s)", lambda t: _r((t["Qreg"] / t["m_b"]) if t["m_b"] else t["Qreg"], 3), tops),
            _attr_row("Qout (kW por kg/s)", lambda t: _r((t["Qout"] / t["m_b"]) if t["m_b"] else t["Qout"], 3), tops),
            _attr_row("m_v (kg/s por kg/s)", lambda t: _r(t["m_v"], 3), tops),
            _attr_row("m_l (kg/s por kg/s)", lambda t: _r(t["m_l"], 3), tops),
            _attr_row("rango experimental", lambda t: "dentro" if (t["en_rango"] and not t["fuera_rango"]) else "fuera", tops),
        ]
        tabla(ws, f, ["Atributo", "D1", "D2", "D3", "D4", "D5"], filas,
              anchos=[26] + [14] * 5, clases=None, clave_fila=None)
        f += 2 + len(filas)
    return f


def _top1_por_centro(df, cen):
    tops = _top5_por_centro(df, cen)
    return tops[0] if tops else None


def seccion_escalado(ws, f, df):
    f = subtitulo(ws, f, "2. Escalado con el caudal (mejor diseño por centro)")
    f = condiciones(ws, f, ["Para el mejor diseño de cada centro, Wnet, Qi, Qreg, Qout con m_b = 1, 5, 10, 15, 20 kg/s (multiplicación exacta)."])
    bases = []
    for cen in CENTROS:
        b = _top1_por_centro(df, cen)
        bases.append((cen, b))
    filas_chart = []
    for mb in M_CAUDAL:
        row = [mb]
        for _, b in bases:
            if b is None:
                row.append(None)
            else:
                mb_b = b["m_b"] or 1.0
                row.append(_r((b["Wnet"] / mb_b) * mb, 3))
        filas_chart.append(row)
    f_enc = f
    tabla(ws, f, ["m_b (kg/s)"] + CENTROS, filas_chart, anchos=[14] + [14] * 4, clases=None, clave_fila=None)
    f = grafico_sobre_tabla(ws, f_enc, len(filas_chart), [2, 3, 4, 5],
                            titulo="E13. Wnet por m_b, agrupado por centro (mejor diseño de cada centro)",
                            x="m_b (kg/s)",
                            y="Wnet (kW)",
                            cat_col=1,
                            tipo="barras",
                            nota_txt="Wnet escalado linealmente con m_b; η y clase no varían con m_b (Fase 0). Fuente: los CSV de resultados/.")
    for i, (cen, b) in enumerate(bases):
        if b is None:
            continue
        mb_b = b["m_b"] or 1.0
        filas = []
        for mb in M_CAUDAL:
            filas.append([
                mb,
                _r((b["Wnet"] / mb_b) * mb, 3),
                _r((b["Qi"] / mb_b) * mb, 3),
                _r((b["Qreg"] / mb_b) * mb, 3),
                _r((b["Qout"] / mb_b) * mb, 3),
            ])
        tabla(ws, f, ["m_b (kg/s)", "Wnet (kW)", "Qi (kW)", "Qreg (kW)", "Qout (kW)"], filas,
              anchos=[14] * 5, clases=None, clave_fila=None)
        f += 2 + len(filas)
    return f


def _min_epsreg_hrvg_etat(df, cen):
    # Estudios 1 y 2 (una variable y pares en C1/C2) y 10 y 11 (en C3/C4).
    d = df[(df["centro"] == cen) & df["estudio"].isin((1, 2, 10, 11)) & df["kalina"]]
    if len(d) == 0:
        return (None, None, None)
    return (_r(d["eps_reg"].min(), 3),
            _r(d["eps_hrvg"].min(), 3),
            _r(d["eta_t"].min(), 3))


def seccion_minimos(ws, f, df):
    f = subtitulo(ws, f, "3. Efectividad mínima por equipo (todos los estudios de cada centro)")
    f = condiciones(ws, f, [
        "ε_cond mínima con KALINA (total) por centro, sobre TODOS los estudios, con el estudio y "
        "la P_baja del punto que la logra. ε_reg, ε_HRVG y η_t mínimas con KALINA (total) de los "
        "barridos de una variable y de pares (estudios 1 y 2 y 5 para C1 y C2; 10 y 11 para C3 y "
        "C4)."])
    filas = []
    for cen, epsc, est, pbc in min_epscond_centro(df):
        epsr, epsh, etat = _min_epsreg_hrvg_etat(df, cen)
        filas.append([cen, epsc, est, pbc, epsr, epsh, etat])
    enc = f
    tabla(ws, f,
          ["Centro", "ε_cond mínima con KALINA (-)", "Estudio a ε_cond mínima",
           "P_baja a ε_cond mínima (kPa)", "ε_reg mínima con KALINA (-)",
           "ε_HRVG mínima con KALINA (-)", "η_t mínima con KALINA (-)"],
          filas,
          anchos=[20, 16, 14, 16, 16, 16, 16],
          clases=None,
          clave_fila=None)
    return grafico_sobre_tabla(
        ws, enc, len(filas), [2],
        titulo="E13. ε_cond mínima con KALINA por centro", x="Centro",
        y="ε_cond mínima (-)",
        nota_txt="Incluye: la ε_cond mínima con KALINA (total) de todos los estudios de cada "
                 "centro, con el estudio y la P_baja del punto que la logra. Fuente: los CSV de "
                 "resultados/.")


def hoja_e13(wb, df):
    ws = wb.create_sheet("E13 Preseleccion de equipos")
    f = 1
    f = titulo(ws, f, "E13. Preselección de equipos")
    f = condiciones(ws, f, [
        "Datos leídos directamente de los CSV (sin inventar cifras). Se seleccionan KALINA (total) "
        "por centro y se escalan las potencias por m_b, por unidad."])
    f = seccion_referencia(ws, f, df)
    f = seccion_escalado(ws, f, df)
    f = seccion_minimos(ws, f, df)
    f = subtitulo(ws, f, "4. ε_cond mínima con KALINA por banda de x_b (todos los estudios)")
    f = tabla_bandas(ws, f, df,
                     titulo_chart="E13. ε_cond mínima con KALINA por banda de x_b")
    return "E13 Preseleccion de equipos"
