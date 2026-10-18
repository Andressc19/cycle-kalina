# -*- coding: utf-8 -*-
"""Sensibilidad 1 - x5c: bloques de grafico de los estudios 4 a 11 (E4…E11).

Usa los ayudantes comunes de x5b_graficos_a (contar, bloque_kv, fuente). Cada grafico sale de
la tabla que se escribe a su izquierda; todos los numeros se calculan desde el DataFrame.
"""
from x1_cargar import CENTRO_TXT, PARS
from x5_graficos import bloque
from x5b_graficos_a import PARS_VARS, bloque_kv, contar, fuente, kalina_malla

C3 = CENTRO_TXT["C3"]
C4 = CENTRO_TXT["C4"]


def _eta(sub):
    """Eta maxima (en %) del subconjunto, o None si esta vacio."""
    if len(sub) == 0:
        return None
    return round(float(sub["eta_pct"].max()), 3)


def _e4(ws, d, f):
    niveles = sorted(int(round(t - 273.15)) for t in set(d["T_fuente"].round(1)))
    filas1, filas2 = [], []
    for lv in niveles:
        s = d[(d["T_fuente"] - 273.15).round(0) == lv]
        filas1.append([lv, contar(s, "confiable"), contar(s, "fuera_motor")])
        filas2.append([lv, _eta(s[s["confiable"]]), _eta(s[s["kalina"]])])
    n_total = len(d)
    f = bloque(ws, f, titulo="KALINA por nivel de T_fuente (dentro y fuera del rango experimental)",
               encabezados=["T_fuente (°C)", "dentro del rango experimental",
                            "fuera del rango experimental"],
               filas=filas1, x="T_fuente (°C)", y="Numero de puntos", apiladas=True,
               colores=["2E7D32", "C0392B"],
               nota_txt=f"Incluye: los KALINA de los {len(niveles)} niveles de T_fuente. "
                         f"Fuente: {fuente(4)}. n = {n_total}.")
    return bloque(ws, f, titulo="E4. Rendimiento (eta, %) maximo por nivel de T_fuente",
                  encabezados=["T_fuente (°C)", "eta maxima dentro del rango experimental (%)",
                               "eta maxima entre todos los KALINA (%)"],
                  filas=filas2, x="T_fuente (°C)", y="eta (%)", tipo="linea", x_vals=niveles,
                  nota_txt=f"Incluye: la eta maxima por nivel (vacio donde no hay KALINA dentro "
                            f"del rango experimental). Fuente: {fuente(4)}. n = {n_total}.")


def _e5(ws, d, f):
    ecs = sorted(set(d["eps_cond"].round(2)))
    tss = sorted(set(d["T_sumidero"].round(1)))
    filas1, filas2 = [], []
    for ec in ecs:
        r1, r2 = [round(float(ec), 2)], [round(float(ec), 2)]
        for ts in tss:
            s = d[(d["eps_cond"].round(2) == ec) & (d["T_sumidero"].round(1) == ts) & d["kalina"]]
            r1.append(round(float(s["P_baja"].min()), 1) if len(s) else None)
            r2.append(_eta(s[s["confiable"]]))
        filas1.append(r1)
        filas2.append(r2)
    ets = [f"T_sumidero {int(round(t - 273.15))} °C" for t in tss]
    n_total = len(d)
    f = bloque(ws, f, titulo="E5. P_baja minima con KALINA frente a eps_cond",
               encabezados=["eps_cond (-)"] + ets, filas=filas1, tipo="linea",
               x="eps_cond (-)", y="P_baja minima con KALINA (kPa)", x_vals=ecs,
               nota_txt=f"Incluye: la P_baja minima con KALINA en cada celda eps_cond x "
                         f"T_sumidero (vacio donde no hay KALINA). Fuente: {fuente(5)}. n = {n_total}.")
    return bloque(ws, f, titulo="E5. Eta maxima del KALINA frente a eps_cond",
                  encabezados=["eps_cond (-)"] + ets, filas=filas2, tipo="linea",
                  x="eps_cond (-)", y="eta maxima dentro del rango experimental (%)", x_vals=ecs,
                  nota_txt=f"Incluye: la eta maxima del KALINA en cada celda eps_cond x "
                            f"T_sumidero (vacio donde no hay KALINA dentro del rango experimental). "
                            f"Fuente: {fuente(5)}. n = {n_total}.")


def _e6(ws, d, f):
    xbs = sorted(set(d["x_b"].round(2)))
    filas = []
    for xb in xbs:
        s = d[d["x_b"].round(2) == xb]
        filas.append([round(float(xb), 2), contar(s[s["centro"] == CENTRO_TXT["C1"]], "kalina"),
                      contar(s[s["centro"] == CENTRO_TXT["C2"]], "kalina")])
    nota = (f"Incluye: los KALINA de cada x_b (malla 7x7 de P_alta x x_b por centro). "
            f"Fuente: {fuente(6)}. n = {len(d)}.")
    return bloque(ws, f, titulo="E6. KALINA por x_b (C1 Husavik y C2 ancla A*)",
                  encabezados=["x_b (-)", CENTRO_TXT["C1"], CENTRO_TXT["C2"]],
                  filas=filas, x="x_b (-)", y="Numero de puntos", nota_txt=nota)


def _e7(ws, d, f):
    bandas = [(70, 80), (80, 90), (90, 100), (100, 110), (110, 120), (120, 130)]
    tfc = d["T_fuente"] - 273.15
    filas1, filas2 = [], []
    for a, b in bandas:
        s = d[(tfc > a) & (tfc <= b)]
        filas1.append([f"{a}-{b}", contar(s, "kalina")])
        filas2.append([f"{a}-{b}", _eta(s[s["confiable"]])])
    n_total = len(d)
    f = bloque(ws, f, titulo="E7. KALINA por banda de T_fuente (fuente fria)",
               encabezados=["Banda de T_fuente (°C)", "KALINA (total)"], filas=filas1,
               x="Banda de T_fuente (°C)", y="Numero de puntos",
               nota_txt=f"Incluye: los KALINA en cada banda de T_fuente (70 a 130 °C). "
                         f"Fuente: {fuente(7)}. n = {n_total}.")
    return bloque(ws, f, titulo="E7. Eta maxima del KALINA por banda de T_fuente (fuente fria)",
                  encabezados=["Banda de T_fuente (°C)", "eta maxima dentro del rango experimental (%)"],
                  filas=filas2, x="Banda de T_fuente (°C)", y="eta (%)",
                  nota_txt=f"Incluye: la eta maxima del KALINA por banda (vacio donde no hay "
                            f"KALINA dentro del rango experimental). Fuente: {fuente(7)}. n = {n_total}.")


def _e8(ws, d, f):
    tfs = sorted(int(round(t - 273.15)) for t in set(d["T_fuente"].round(1)))
    tss = sorted(int(round(t - 273.15)) for t in set(d["T_sumidero"].round(1)))
    filas1, filas2 = [], []
    for ts in tss:
        r1, r2 = [ts], [ts]
        for tf in tfs:
            s = d[((d["T_fuente"] - 273.15).round(0) == tf) &
                  ((d["T_sumidero"] - 273.15).round(0) == ts) & d["kalina"]]
            r1.append(round(float(s["P_baja"].min()), 1) if len(s) else None)
            r2.append(_eta(s))
        filas1.append(r1)
        filas2.append(r2)
    ets = [f"T_fuente {tf} °C" for tf in tfs]
    n_total = len(d)
    f = bloque(ws, f, titulo="E8. P_baja minima con KALINA frente a T_sumidero (una linea por T_fuente)",
               encabezados=["T_sumidero (°C)"] + ets, filas=filas1, tipo="linea",
               x="T_sumidero (°C)", y="P_baja minima con KALINA (kPa)", x_vals=tss,
               nota_txt=f"Incluye: la P_baja minima con KALINA del mapa fuente x clima "
                         f"(vacio donde no hay KALINA). Fuente: {fuente(8)}. n = {n_total}.")
    return bloque(ws, f, titulo="E8. Eta maxima entre todos los KALINA frente a T_sumidero (una linea por T_fuente)",
                  encabezados=["T_sumidero (°C)"] + ets, filas=filas2, tipo="linea",
                  x="T_sumidero (°C)", y="eta maxima entre todos los KALINA (%)", x_vals=tss,
                  nota_txt=f"Incluye: la eta maxima entre todos los KALINA del mapa fuente x clima "
                            f"(vacio donde no hay KALINA). Fuente: {fuente(8)}. n = {n_total}.")


def _etq(c):
    return "%.2f / %.2f / %.2f" % (c[0], c[1], c[2])


def _e9(ws, d, f):
    combos = sorted(set(zip(d["eta_t"].round(2), d["eps_hrvg"].round(2), d["eps_reg"].round(2))))
    filas = []
    for c in combos:
        s = d[(d["eta_t"].round(2) == c[0]) & (d["eps_hrvg"].round(2) == c[1]) &
              (d["eps_reg"].round(2) == c[2])]
        filas.append([_etq(c), _eta(s[(s["centro"] == CENTRO_TXT["C1"]) & s["kalina"]]),
                      _eta(s[(s["centro"] == CENTRO_TXT["C2"]) & s["kalina"]])])
    n_total = len(d)
    return bloque(ws, f, titulo="E9. Rendimiento (eta, %) por combinacion de equipos baratos",
                  encabezados=["eta_t / eps_HRVG / eps_reg (-)", CENTRO_TXT["C1"], CENTRO_TXT["C2"]],
                  filas=filas, x="eta_t / eps_HRVG / eps_reg (-)", y="eta (%)",
                  nota_txt=f"Incluye: la eta maxima del KALINA en cada combinacion (eps_cond "
                            f"0.95; vacio donde no hay KALINA). Fuente: {fuente(9)}. n = {n_total}.")


def _e10(ws, d, f, bases):
    n_total = len(d)
    f = bloque_kv(ws, f, d[d["centro"] == C3], C3, 10, n_total, bases)
    return bloque_kv(ws, f, d[d["centro"] == C4], C4, 10, n_total, bases)


def _e11(ws, d, f, bases):
    filas = []
    for p in ["B1", "B2", "B3", "B4"]:
        a, b = PARS_VARS[p]
        filas.append([PARS[p], kalina_malla(d, C3, a, b), kalina_malla(d, C4, a, b)])
    nota = (f"Incluye: los KALINA de los 4 pares de variables (malla por par y centro) y el "
            f"punto base de cada centro. Fuente: {fuente(11)}. n = {len(d)}.")
    return bloque(ws, f, titulo="E11. KALINA por par de variables (C3 caliente 150 C y C4 frio 110 C)",
                  encabezados=["Par de variables", C3, C4], filas=filas,
                  x="Par de variables", y="Numero de puntos", nota_txt=nota)


def dibujar_estudio_b(ws, n, df, f, bases):
    """Escribe los bloques de grafico del estudio n (4 a 11)."""
    d = df[df["estudio"] == n]
    if n == 4:
        return _e4(ws, d, f)
    if n == 5:
        return _e5(ws, d, f)
    if n == 6:
        return _e6(ws, d, f)
    if n == 7:
        return _e7(ws, d, f)
    if n == 8:
        return _e8(ws, d, f)
    if n == 9:
        return _e9(ws, d, f)
    if n == 10:
        return _e10(ws, d, f, bases)
    if n == 11:
        return _e11(ws, d, f, bases)
    return f
