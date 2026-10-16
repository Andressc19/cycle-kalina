# -*- coding: utf-8 -*-
"""Sensibilidad 1 - conclusiones: textos de los Apendices A y B (sin logica).

Los estudios 4, 7, 8 y 11 citan una eta maxima, y ademas de la de los KALINA dentro del
rango experimental anaden la eta maxima entre *todos* los KALINA del estudio. Esa segunda
cifra se calcula desde el DataFrame (no se escribe a mano) para no inventar valores.
"""

# Apendice A estatico: conclusiones de los estudios que no necesitan calcular nada.
APENDICE_A_ESTATICO = {
    0: ("Estudio 0, referencia de Husavik (fase 0). Con eps_cond = 0.90, Husavik "
        "(T_fuente 394.15 K, P_alta 3300, P_baja 690, x_b 0.82) es CORREGIBLE por cavitacion "
        "(m_O2 -0.26 K con piso 283.15 K); con eps_cond = 0.95 es KALINA (eta 12.0 %, m_O2 +0.80 K). "
        "El caudal no cambia eta ni la clase: m_b de 1 a 20 kg/s solo multiplica las potencias "
        "(diferencia de eta 1.6e-11)."),
    1: ("Estudio 1, una variable. Las eficiencias y efectividades (eta_t, eta_p, eps_HRVG, eps_reg) "
        "mantienen KALINA en todo 0.40–0.95 en ambos centros. Lo que saca al ciclo de KALINA es la "
        "condensacion, la presion baja y la composicion: en C1 eps_cond solo funciona en 0.95 y x_b "
        "en 0.55–0.90; en C2 x_b solo en 0.45–0.55 y P_alta hasta 3750 kPa. En C1 eta_t mueve eta "
        "8.1 puntos porcentuales entre sus KALINA; en C2 P_alta 6.8 y T_fuente 6.8."),
    2: ("Estudio 2, pares. eps_reg x eta_t mantiene KALINA en las 49 combinaciones de ambos centros. "
        "eps_cond x T_sumidero en C1 solo tiene 3 de 49 KALINA (eps_cond 0.95 con sumidero de 5 a 10 °C); "
        "en C2 tiene 33 de 49. Hay interaccion (la combinacion se cae antes que cada variable sola) en C1 "
        "eps_HRVG x T_fuente y en C2 T_fuente x P_baja y eps_HRVG x T_fuente."),
    3: ("Estudio 3, LHS de 9 variables. Con las 9 variables moviendose a la vez, ~47 % (C1) y ~52 % (C2) "
        "de los puntos son KALINA. Separan KALINA del resto: x_b, P_baja y eps_cond en C1; T_fuente, "
        "P_baja y T_sumidero en C2. Mueven eta (PRCC): eta_t (+0.74 y +0.71), P_baja (-0.61 y -0.69) y x_b "
        "(+0.58 y +0.69). eta maxima en el muestreo: 13.7 % (C1) y 12.4 % (C2)."),
    5: ("Estudio 5, condensador x clima. Con eps_cond < 0.85 no hay KALINA en ningun clima probado. La "
        "P_baja minima con eps_cond 0.95 es 700 kPa (10 °C), 1000 (20 °C) y 1250 (30 °C); con 0.90 sube a 1000 "
        "y 1250 (10 y 20 °C); con 0.85 solo hay KALINA a 10 °C con 1250 kPa. Cada -0.05 de eps_cond cuesta "
        "+250 a +300 kPa de P_baja."),
    6: ("Estudio 6, P_alta baja x composicion. En C1 hay KALINA desde P_alta = 1000 kPa con x_b 0.40–0.80 "
        "(34 de 49 celdas; eta maxima 12.0 %). En C2 solo con x_b 0.40–0.50, para cualquier P_alta entre 1000 "
        "y 3000 kPa (13 de 49; eta maxima 8.7 %)."),
    9: ("Estudio 9, equipos baratos (eps_cond 0.95). En C1, 25 de 27 combinaciones de eta_t, eps_HRVG y "
        "eps_reg en {0.40, 0.55, 0.70} son KALINA; con 0.40/0.40/0.40 sigue siendo KALINA pero con eta 0.2 %; "
        "con 0.70/0.70/0.70, eta 9.2 %. En C2, 18 de 27 son KALINA."),
    10: ("Estudio 10, centros nuevos, una variable. C3 (150 °C): KALINA con P_baja >= 600 kPa, T_sumidero "
         "hasta 22.5 °C y eps_cond 0.90–0.95. C4 (110 °C): P_baja >= 800 kPa, T_sumidero hasta 17.5 °C y solo "
         "eps_cond 0.95. Las eficiencias 0.40–0.95 no sacan a ninguno de KALINA (salvo eps_HRVG baja en C4, "
         "con eta de hasta 1.6 %)."),
}


def _eta_max(sub):
    """(eta en %, T_fuente en °C) del punto de mayor eta del subconjunto, o None."""
    if sub is None or len(sub) == 0:
        return None
    r = sub.loc[sub["eta_pct"].idxmax()]
    return r["eta_pct"], r["T_fuente"] - 273.15


def _frase_todos(df_e):
    """Frase con la eta maxima entre todos los KALINA del estudio (calculada desde los datos)."""
    todo = _eta_max(df_e[df_e["kalina"]])
    return (f"η máxima entre todos los KALINA de este estudio: {todo[0]:.1f} % a "
            f"{int(round(todo[1]))} °C.")


def _estudio4(df_e):
    return ("Estudio 4, fuente de 70 a 300 °C. Hay KALINA en los 13 niveles de T_fuente. A 70 °C "
            "aparece el primer KALINA (2 puntos; P_alta 1630–2200, P_baja 770–840, x_b 0.70–0.75; "
            "eta 5.3 %). Hasta ~150 °C todos están dentro del rango experimental de la ecuación; "
            "entre 150 y 170 °C una parte (≈31–76 %) queda fuera de él, y por encima de 170 °C casi "
            "todos (≈93–100 %). Los resultados fuera del rango experimental forman parte de las "
            "conclusiones. η máxima entre los KALINA dentro del rango experimental: 13.6 % a 150 °C; "
            + _frase_todos(df_e))


def _estudio7(df_e):
    return ("Estudio 7, fuente fria con presiones bajas. Con fuente de 70–130 °C hay 45 KALINA "
            "dentro del rango experimental, con P_baja 260–870 kPa, P_alta 820–2970 kPa y x_b "
            "0.35–0.79. η máxima entre los KALINA dentro del rango experimental: 10.5 % a 101 °C "
            "(P_alta 2970, P_baja 570, x_b 0.71); " + _frase_todos(df_e))


def _estudio8(df_e):
    return ("Estudio 8, mapa fuente x clima x P_baja (P_alta 3000, x_b 0.70). La P_baja minima con "
            "KALINA sube alrededor de 100 kPa por cada +5 K de T_sumidero y con la T_fuente: de 400 kPa "
            "(90 °C, clima 5 °C) a 1250 kPa (170–200 °C, 25–30 °C). η máxima entre los KALINA dentro del "
            "rango experimental: 13.1 % (150 °C, 5 °C, P_baja 500); " + _frase_todos(df_e) +
            " A 170 y 200 °C hay KALINA, todos fuera del rango experimental.")


def _estudio11(df_e):
    return ("Estudio 11, centros nuevos, pares. η máxima entre los KALINA dentro del rango experimental: "
            "14.4 % (C3, 150 °C, P_alta 5000 kPa (borde de la caja), P_baja 650, x_b 0.75) y 13.2 % "
            "(C4, 150 °C, P_baja 800, x_b 0.88); " + _frase_todos(df_e) +
            " El par eps_cond x T_sumidero es el mas restrictivo (C3: 8 de 49 KALINA; C4: 5 de 49, "
            "contando el punto base de cada malla). Hubo 3 puntos que agotaron el tope de 600 s, los tres "
            "en C4 con eps_cond 0.60–0.65.")


_CON_DATOS = {4: _estudio4, 7: _estudio7, 8: _estudio8, 11: _estudio11}


def apendice_a(n, df_e=None):
    """Conclusion del Apendice A para el estudio `n`; usa `df_e` cuando la cifra se calcula.

    `df_e` puede ser el DataFrame completo: aqui se filtra al estudio `n` antes de calcular las
    etas maximas (si ya viniera filtrado, el filtro no cambia nada).
    """
    f = _CON_DATOS.get(n)
    if f is not None and df_e is not None:
        return f(df_e[df_e["estudio"] == n])
    return APENDICE_A_ESTATICO.get(n, "")


APENDICE_B = """1. Hay KALINA en todo el rango de fuente de 70 a 300 °C. Hasta ~150 °C todos están dentro del rango experimental de la ecuación; entre 150 y 170 °C una parte (≈31–76 %) queda fuera de él, y por encima de 170 °C casi todos (≈93–100 %). Los resultados fuera del rango experimental forman parte de las conclusiones.

2. El condensador manda. Con eps_cond < 0.85 no hay KALINA; cada -0.05 cuesta +250 a +300 kPa de P_baja (y por tanto eficiencia), y un clima calido exige la efectividad maxima.

3. Las eficiencias de turbina, bomba, HRVG y regenerador no sacan al ciclo de KALINA en 0.40–0.95; solo mueven eta. La palanca principal de eta es eta_t, seguida de P_baja (a menor P_baja, mayor eta) y x_b.

4. Presiones por clima y fuente: la P_baja minima sube ~100 kPa por cada +5 K de clima, y con la T_fuente. P_alta tiene mucho margen (desde 1000 kPa hay KALINA en C1; en C2 casi no influye).

5. Eficiencia alcanzable: 13–14.4 % entre los KALINA dentro del rango experimental con fuente de ~150 °C, clima de 5–10 °C, P_baja 410–800 kPa y equipos de 0.85–0.95; con equipos de 0.70, ~9 %.

6. Para preseleccion de equipos, los rangos por kg/s de caudal (Delta h de turbina, Wnet, Qreg/Qi, r_P, Qout) estan en la sintesis S4; el caudal solo escala las potencias.

7. Limites: modelo teqp sin validacion experimental; los KALINA a fuente > 170 °C quedan fuera del rango experimental; los muestreos (estudios 3, 4 y 7) dan ventanas aproximadas, no fronteras exactas; m_b no se barrió porque solo escala las potencias.
"""
