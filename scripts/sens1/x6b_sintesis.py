# -*- coding: utf-8 -*-
"""Sensibilidad 1 - x6b: secciones S2, S3 y S4 de la hoja 'Conclusion consolidada'.

S2 (ventanas KALINA por variable y centro), S3 (fronteras de P_baja minima con KALINA) y S4
(rangos de equipos por kg/s de caudal). Todos los numeros salen del DataFrame (los CSV).
"""

from x1_cargar import etiqueta_centro


def _filas_ventanas_cols(filas):
    """Reduce las filas de ventanas a [Variable, Centro, minimo, maximo, n]."""
    return [[r[0], r[2], r[3], r[5], r[6]] for r in filas]


def seccion_s2(ws, f, df):
    """S2. Ventanas KALINA por variable y centro (C1/C2 del estudio 1; C3/C4 del 10)."""
    from x2_formato import titulo, condiciones, tabla
    from x4_resumenes import filas_ventanas
    f = titulo(ws, f, "S2. Ventanas KALINA por variable y centro")
    f = condiciones(ws, f, [
        "Ventanas del barrido propio de cada variable (mas el punto base) en C1 y C2 (estudio 1) "
        "y C3 y C4 (estudio 10); todos entre los KALINA (total)."])
    sub = df[(df["estudio"] == 1) | (df["estudio"] == 10)]
    filas = _filas_ventanas_cols(filas_ventanas(sub))
    tabla(ws, f, ["Variable", "Centro", "Valor minimo con KALINA", "Valor maximo con KALINA",
                  "n KALINA (total)"], filas, anchos=[16, 20, 24, 24, 16], clases=None,
          clave_fila=None)
    return f + 2 + len(filas)


def _frontera_epscond(d):
    """Filas [eps_cond, P_baja min por T_sumidero] de un estudio (frontera eps_cond x sumidero)."""
    ecs = sorted(set(d["eps_cond"].round(2)))
    tss = sorted(set(d["T_sumidero"].round(1)))
    filas = []
    for ec in ecs:
        r = [round(float(ec), 2)]
        for ts in tss:
            s = d[(d["eps_cond"].round(2) == ec) & (d["T_sumidero"].round(1) == ts) & d["kalina"]]
            r.append(round(float(s["P_baja"].min()), 1) if len(s) else None)
        filas.append(r)
    ets = [f"T_sumidero {int(round(t - 273.15))} °C" for t in tss]
    return filas, ets


def _frontera_tfuente(d):
    """Filas [T_sumidero, P_baja min por T_fuente] (frontera fuente x sumidero)."""
    tfs = sorted(int(round(t - 273.15)) for t in set(d["T_fuente"].round(1)))
    tss = sorted(int(round(t - 273.15)) for t in set(d["T_sumidero"].round(1)))
    filas = []
    for ts in tss:
        r = [ts]
        for tf in tfs:
            s = d[((d["T_fuente"] - 273.15).round(0) == tf) &
                  ((d["T_sumidero"] - 273.15).round(0) == ts) & d["kalina"]]
            r.append(round(float(s["P_baja"].min()), 1) if len(s) else None)
        filas.append(r)
    etf = [f"T_fuente {tf} °C" for tf in tfs]
    return filas, etf


def seccion_s3(ws, f, df):
    """S3. Fronteras de P_baja minima con KALINA (estudios 5 y 8) y eps_cond minima por banda de x_b."""
    from x2_formato import titulo, subtitulo, condiciones
    from x5_graficos import bloque
    from x10b_bandas import tabla_bandas
    f = titulo(ws, f, "S3. Fronteras: P_baja minima con KALINA")
    f = condiciones(ws, f, [
        "(a) P_baja minima con KALINA por eps_cond x T_sumidero (estudio 5, C1 Husavik). "
        "(b) por T_fuente x T_sumidero (estudio 8). Son los mismos valores que E5 y E8, aqui "
        "reunidos con referencia a su origen. (c) eps_cond minima con KALINA por banda de x_b "
        "(todos los estudios): el piso del condensador depende de la composicion."])
    filas, ets = _frontera_epscond(df[df["estudio"] == 5])
    f = bloque(ws, f, titulo="S3a. P_baja minima con KALINA frente a eps_cond (estudio 5)",
               encabezados=["eps_cond (-)"] + ets, filas=filas, tipo="linea",
               x="eps_cond (-)", y="P_baja minima con KALINA (kPa)",
               x_vals=[r[0] for r in filas],
               nota_txt="Incluye: la P_baja minima con KALINA en cada celda eps_cond x "
                        "T_sumidero (vacio donde no hay KALINA). Origen: hoja E5.")
    filas, etf = _frontera_tfuente(df[df["estudio"] == 8])
    f = bloque(ws, f, titulo="S3b. P_baja minima con KALINA frente a T_sumidero (estudio 8)",
               encabezados=["T_sumidero (°C)"] + etf, filas=filas, tipo="linea",
               x="T_sumidero (°C)", y="P_baja minima con KALINA (kPa)",
               x_vals=[r[0] for r in filas],
               nota_txt="Incluye: la P_baja minima con KALINA del mapa fuente x clima (vacio "
                        "donde no hay KALINA). Origen: hoja E8.")
    f = subtitulo(ws, f, "S3c. ε_cond mínima con KALINA por banda de x_b (todos los estudios)")
    return tabla_bandas(ws, f, df,
                        titulo_chart="S3c. ε_cond mínima con KALINA por banda de x_b")


# (columna del DataFrame, columna normalizada por kg/s, etiqueta de la variable)
_METRICAS = [
    ("dh_turb", None, "dh de turbina (kJ/kg)"),
    ("Wnet", "Wnet_kg", "Wnet (kW por kg/s)"),
    ("Qi", "Qi_kg", "Qi (kW por kg/s)"),
    ("Qreg", "Qreg_kg", "Qreg (kW por kg/s)"),
    ("Qout", "Qout_kg", "Qout (kW por kg/s)"),
    ("qreg_qi", None, "Qreg/Qi (-)"),
    ("rp", None, "r_P = P_alta/P_baja (-)"),
]


def seccion_s4(ws, f, df):
    """S4. Rangos de equipos por kg/s de caudal, por estudio y centro, entre los KALINA."""
    from x2_formato import titulo, condiciones, tabla
    from x5_graficos import bloque
    f = titulo(ws, f, "S4. Rangos de equipos por kg/s de caudal")
    f = condiciones(ws, f, [
        "Entre los KALINA (total) de cada estudio y centro, por kg/s de m_b: minimo, mediana y "
        "maximo de Delta h de turbina, Wnet, Qi, Qreg, Qout, Qreg/Qi y r_P = P_alta/P_baja."])
    d = df[df["kalina"]].copy()
    for col, norm, _ in _METRICAS:
        if norm:
            d[norm] = d[col] / d["m_b"]
    filas = []
    for (est, cen), g in d.groupby(["estudio", "centro"], sort=True):
        for col, norm, nom in _METRICAS:
            v = g[norm if norm else col].dropna()
            if len(v) == 0:
                continue
            filas.append([int(est), etiqueta_centro(cen), nom, round(float(v.min()), 4),
                          round(float(v.median()), 4), round(float(v.max()), 4)])
    tabla(ws, f, ["Estudio", "Centro", "Variable", "minimo", "mediana", "maximo"], filas,
          anchos=[10, 18, 26, 12, 12, 12], clases=None, clave_fila=None)
    f += 2 + len(filas)
    med = d.groupby("estudio")["Wnet_kg"].median()
    filas_ch = [[int(n), round(float(v), 4)] for n, v in med.items()]
    return bloque(ws, f, titulo="S4. Mediana de Wnet por estudio (por kg/s de caudal)",
                  encabezados=["Estudio", "mediana de Wnet (kW por kg/s)"], filas=filas_ch,
                  x="Estudio", y="mediana de Wnet (kW por kg/s)",
                  nota_txt="Incluye: la mediana de Wnet entre los KALINA (total) de cada estudio, "
                           "por kg/s de caudal. Fuente: los CSV de resultados/.")
