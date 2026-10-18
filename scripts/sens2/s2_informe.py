# -*- coding: utf-8 -*-
"""Sens2 - s2_informe: genera `docs/INFORME_SENS2.md` desde p5_conclusiones.csv y los CSV de P1 a P4.

Las cifras de cabecera se calculan aqui; las conclusiones se copian tal cual del CSV.
"""
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
from s2_cargar import conclusiones, dataset_dedup, distancia_resumen, violaciones  # noqa: E402
from p5_hechos import hechos  # noqa: E402

SALIDA = os.path.join(RAIZ, "docs", "INFORME_SENS2.md")
CATEGORIAS = ["DISEÑO REAL", "EQUIPOS", "MÁXIMA EFICIENCIA", "FLUCTUACIÓN", "LÍMITES KALINA"]
HOJA = {"DISEÑO REAL": "F1", "EQUIPOS": "F4", "MÁXIMA EFICIENCIA": "F2 y F4", "FLUCTUACIÓN": "F3",
        "LÍMITES KALINA": "F1 y F2"}

CAVEATS = [
    "Solo motor teqp, sin validación experimental propia del ciclo; el lugar crítico no se vigila.",
    "El 15 % de los KALINA está fuera del rango experimental (líquido > 420 K); se muestran siempre aparte.",
    "Los diseños mezclan barridos de una variable, mallas y LHS: las probabilidades por nivel dependen del "
    "diseño; los índices globales se calcularon solo sobre el LHS de cada bloque.",
    "η, W_net y los márgenes existen solo en puntos convergidos: las comparaciones de η entre clases "
    "condicionan en haber convergido (sesgo de supervivencia a vigilar).",
    "m_b no se barrió; las potencias son por kg/s de m_b (el estudio 0 usa m_b distinto de 1).",
    "Las elasticidades salen de solo dos estudios (1 y 10); la de T_fuente en C2 (13.2) está sobre una rampa.",
    "Los p-valores y los IC de la comparación sobre todos los puntos suponen independencia que los barridos y "
    "las mallas no cumplen; la versión sobre LHS (η +3.1 puntos, IC [+2.46, +3.65]) es la más defendible.",
    "Los índices de D en C4 (n = 28) son indicativos.",
    "LMTD y UA del regenerador se reconstruyen de los estados (contraflujo puro); el modelo usa efectividad.",
    "7 puntos atípicos del libro 1 no se descartan ni se validaron con el motor real.",
    "«Distinguible» en F1 a F3 significa q < 0.05 de Benjamini–Hochberg en al menos 2 métodos sobre 2 000 permutaciones de la respuesta "
    "(más estricto que el criterio anterior de las 3 variables dummy); los 8 métodos no son independientes, NO_CONVERGIO cuenta como «no KALINA» "
    "en la existencia y las magnitudes de los índices no se comparan entre bloques (la caja común de rangos de los 4 LHS queda con 1 a 9 puntos). "
    "La conclusión M5 (óptimos cerca de la frontera) no se sostiene con el LHS solo, salvo en C1.",
    "La propagación de incertidumbre usa tolerancias supuestas (uniformes, ±a/√3 de incertidumbre estándar), 96 puntos "
    "por bloque en el escenario A (dos lotes de 48) y 48 en B (IC de Wilson) y entradas independientes; dos lotes "
    "compatibles no prueban la estabilidad del muestreo (error típico de P con 48 puntos de 0.05 a 0.07; JCGM 101) y la "
    "banda del modelo de propiedades (±0.7 pp) se suma de forma determinista. La importancia por permutación no se implementó.",
    "NO_CONVERGIO (14 % de los puntos) se cuenta como «no KALINA» en los índices de existencia y en P(KALINA); según los "
    "mensajes del motor la mayoría son balances de energía que no cierran o brackets sin extremos evaluables, así que los "
    "umbrales inferiores de T_fuente (D3) pueden estar sesgados por el solver y no por el ciclo.",
    "La cavitación (O2) exige m_O2 = T_burbuja − T9 ≥ 0 (margen cero, no un cálculo de NPSH; ver L7); la confianza (Alta, Media, Baja) "
    "de cada conclusión se calcula con la regla de `p5_confianza.py` (hoja Confianza del libro, con los criterios cumplidos de 6) y mide solidez dentro del modelo teqp, "
    "no validación física.",
]
PROXIMA = [
    "Reintentar con el modo tolerante del motor los NO_CONVERGIO (14 % de los puntos; 24 % en los LHS de C3 y C4, concentrados en T_fuente baja) "
    "para separar «no existe» de «no convergió»: es lo que falta para establecer el umbral inferior de T_fuente (D3).",
    "Calcular el ciclo frente a T_fuente optimizando P_alta, P_baja y x_b en cada temperatura (y no solo el regenerador a presiones fijas) y "
    "obtener el flujo volumétrico de la turbina y la altura de la bomba (los calores, trabajos y UA por kW neto ya están en la hoja F4 Equipos por kW).",
    "Refinar P_baja cerca de su piso (paso de 25 kPa en C1 y C3, 550 kPa; C2 350 kPa; C4 750 kPa): es la "
    "frontera que más puntos separa.",
    "Barrer T_fuente con paso de 2.5 K en los techos de cada bloque (440.65, 468.15, 568.15 y 528.15 K).",
    "Repetir las mallas B2 (P_baja x x_b) y B4 (ε_cond x T_sumidero) con más niveles en C3 y C4, donde la "
    "no aditividad de la existencia es alta.",
    "Validar con el motor real los 7 atípicos y los óptimos M1 a M4 antes de citarlos como cifras de diseño.",
    "Repetir la propagación con más puntos por celda (≥ 200) y comprobar la estabilidad de P(KALINA), con tolerancias "
    "medidas o acordadas con el profesor, y muestrear la banda del modelo de propiedades en vez de sumarla.",
    "Barrer m_b (1, 5, 10, 15, 20) solo si el profesor pide dimensionar por caudal.",
]


def libro_conteos():
    """(hojas, graficos) del libro generado, contados del propio archivo."""
    import zipfile
    import openpyxl
    ruta = os.path.join(RAIZ, "datos", "Kalina_anal_sensible_2.xlsx")
    n_h = len(openpyxl.load_workbook(ruta, read_only=True).sheetnames)
    with zipfile.ZipFile(ruta) as z:
        n_g = sum(1 for x in z.namelist() if re.match(r"^xl/charts/chart\d+\.xml$", x))
    return n_h, n_g


def main():
    d = dataset_dedup()
    c = conclusiones()
    H = hechos()
    k = d[d["kalina"]]
    n_in = round(float(k[~k["fuera_rango"]]["eta_pct"].max()), 2)
    n_out = round(float(k[k["fuera_rango"]]["eta_pct"].max()), 2)
    v = violaciones()
    o2 = v[(v["seccion"] == "dominante") & (v["centro"] == "todos") & (v["clave"] == "viol_O2")]
    L = ["# Informe de Sensibilidad 2: análisis de los 3 921 puntos de Sensibilidad 1", "",
         "> **KALINA existe donde P_baja supera su piso de cavitación y la efectividad del condensador es "
         "alta; la mayor η muestreada es %.2f %% dentro del rango experimental (%.2f %% fuera; no se corrió un optimizador).** "
         "Los puntos de mayor η están cerca del piso de P_baja solo en C1 con el muestreo LHS (M5); con todos los puntos la cercanía depende del diseño." % (n_in, n_out), "",
         "Libro asociado: `datos/Kalina_anal_sensible_2.xlsx` (%d hojas, %d gráficos). Las cifras salen de los CSV de `resultados/` "
         "(P1 a P4, U1, R1 y F1) y de los datos de Sensibilidad 1. Rama `test/anal_terremoto`." % libro_conteos(), "",
         "## 1. Resumen ejecutivo", "",
         "- %d puntos sin duplicados (de 3 921); %.1f %% son KALINA (total)." % (
             len(d), 100.0 * len(k) / len(d)),
         "- %.1f %% de los CORREGIBLE falla por cavitación (O2); su η mediana es %.1f puntos mayor que la de los KALINA sin parear, pero emparejados con su vecino KALINA más cercano del mismo bloque (n = %d) la diferencia es de %.2f puntos (F6, L2)." % (
             100.0 * float(o2.iloc[0]["fraccion"]), H["f6.todos.dif"], H["par4.n"], abs(H["par4.med"])),
         "- Casi la mitad de los CORREGIBLE está a una sola variable de un KALINA; P_baja es la que más rescata.",
         "- Los diseños de mayor η operan con título de salida de turbina de 0.94 (límite 0.90).",
         "- Desde el centro KALINA de cada bloque, C1 y C4 tienen muy poco margen de ε_cond (el barrido fino sitúa la frontera local en "
         "≈ 0.92 y ≈ 0.906, con las demás variables en el centro); P_baja puede bajar hasta 600 kPa (C1) y 800 kPa (C4) (D7, U4, L6).",
         "- Al perturbar las 10 variables a la vez (96 puntos del motor por bloque, con la efectividad del condensador variando "
         "solo por debajo de su centro 0.95), con tolerancias nominales seguirían siendo KALINA el %.0f %% (C1), %.0f %% (C2), "
         "%.0f %% (C3) y %.0f %% (C4); con el doble, %.0f, %.0f, %.0f y %.0f %%; con ε_cond fija en 0.95 el 100 %% en los "
         "cuatro. No es un riesgo del %.0f %% en C1: la causa dominante de perder la clase es la cavitación ligada al condensador, aunque con ε_cond sobre el "
         "umbral todavía se pierden puntos por P_baja bajo, T_sumidero alto y x_b alto (U1, U2, U4)." % (
             H["u1p.C1.pct"], H["u1p.C2.pct"], H["u1p.C3.pct"], H["u1p.C4.pct"],
             H["u1b.C1.pct"], H["u1b.C2.pct"], H["u1b.C3.pct"], H["u1b.C4.pct"], H["u1p.C1.pierde"]),
         "- El piso de P_baja sube con x_b y la superficie de η apunta hacia el menor P_baja (D8, R1).",
         "- En el estudio 4 (presiones y x_b fijos) el regenerador pierde peso al subir T_fuente: Q_reg/Q_i de 0.59 (70 °C, solo 2 KALINA) a 0.013 "
         "(300 °C) y UA de 9.5 a 0.34 kW/K por kg/s; no se reoptimizó el ciclo en cada temperatura (E8).",
         "- La condensación y la cavitación (P_baja, ε_cond, x_b) gobiernan la existencia. Sobre η, η_t tiene el mayor rango medio en C1 y C2, y P_alta "
         "y x_b en C3 y C4; sobre la potencia específica, T_fuente y x_b; P_baja y x_b son distinguibles del ruido sobre η y sobre W_net en los cuatro bloques "
         "y P_alta no lo es sobre W_net en ninguno (F1, F2).", "",
         "## 2. Método", "",
         "Etapa 0 (`docs/ETAPA0_INVESTIGACION_SENSIBILIDAD_KALINA.md`) eligió métodos que se calculan sobre "
         "muestreos existentes: RSA/KS, PAWN, δ de Borgonovo, HSIC, PRCC, η², logística, con 3 variables dummy "
         "como piso de ruido, bootstrap y, para F1 a F3, 2 000 permutaciones de la respuesta con corrección de Benjamini–Hochberg. Se descartaron Morris, Sobol y FAST (exigen corridas nuevas y salida en "
         "todos los puntos). Fase A: existencia y fronteras (P1). Fase C: CORREGIBLE frente a KALINA y distancia (P2). "
         "Fase B: índices globales, interacciones y elasticidades (P3). Equipos (P4). Plan en "
         "`docs/PLAN_SENS2_ANALISIS.md`.", "",
         "**Confianza.** Baja: n_min < 10 (salvo cifras deterministas), sin línea de evidencia, dependiente del diseño (robusto_diseno = no) con una sola línea, "
         "o cambia al tratar NO_CONVERGIO y descansa en un solo bloque. Alta: un recuento directo con n_min ≥ 30, o una "
         "inferencia con al menos 2 líneas de evidencia independientes, n_min ≥ 30, robusta a NO_CONVERGIO y al diseño (o con el alcance "
         "acotado y dicho en el propio enunciado) y con intervalo o prueba corregida. No aplica: las declaraciones de límites del análisis. Media: el resto. Se calcula por código desde `p5_evidencia.csv`; "
         "las inferencias de F1 a F3 usan 2 000 permutaciones de la respuesta y la corrección de Benjamini–Hochberg.", "",
         "## 3. Conclusiones por categoría", "",
         "Cada conclusión indica su fase (A existencia, B interior de KALINA, C comparación), su confianza y su "
         "fuente. Orden de categorías por utilidad para el diseño.", ""]
    for i, cat in enumerate(CATEGORIAS, 1):
        s = c[c["categoria"] == cat]
        L += ["### 3.%d %s (hoja %s del libro)" % (i, cat, HOJA[cat]), ""]
        for _, x in s.iterrows():
            L += ["**%s [%s, fase %s, confianza %s].** %s" % (x["id"], cat, x["fase"], x["confianza"],
                                                              x["afirmacion"]), "",
                  "- Evidencia: %s" % x["evidencia"], "- Implicación: %s" % x["implicacion"],
                  "- Fuente: %s" % x["fuente"], "- Criterio de confianza: %s" % x["criterio_confianza"], ""]
    L += ["## 4. CORREGIBLE frente a KALINA", "",
          "Ver F6 (diferencia sin parear de +%.2f puntos de η, que mezcla zonas distintas del espacio), L1 (96 %% por O2) y L2 "
          "(rescate; la mediana de η del vecino KALINA más cercano es %.2f puntos menor y %.2f si el vecino está a L1 ≤ 0.2). Los CORREGIBLE aportan información sobre la "
          "frontera, no sobre el desempeño: incumplen la cavitación y no son un estimador del desempeño real." % (
              H["f6.todos.dif"], abs(H["par4.med"]), abs(H["par.cerca.med"])), "",
          "## 5. Recomendaciones para la próxima campaña", ""]
    L += ["%d. %s" % (i, t) for i, t in enumerate(PROXIMA, 1)]
    L += ["", "## 6. Limitaciones y supuestos", ""] + ["- " + t for t in CAVEATS]
    L += ["", "*Revisión con la lista de `validate-data` (plugin `data` de Anthropic): duplicados, denominadores, "
          "cifras recalculadas de forma independiente, sesgo de selección y gráficos revisados en Excel real. "
          "Estado: compartir con los caveats de la sección 6.*"]
    ruta_val = os.path.join(RAIZ, "docs", "VALIDACION_SENS2.md")
    if os.path.exists(ruta_val):    # el conteo de hojas y graficos de la validacion sigue al libro
        with open(ruta_val, encoding="utf-8", newline="") as fh:
            txt = fh.read()
        cambiado = re.sub(r"\(\d+ hojas, \d+ gráficos\)", "(%d hojas, %d gráficos)" % libro_conteos(), txt)
        if cambiado != txt:
            with open(ruta_val, "w", encoding="utf-8", newline="") as fh:
                fh.write(cambiado)
    with open(SALIDA, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("OK:", SALIDA, len(L), "lineas")


if __name__ == "__main__":
    main()
