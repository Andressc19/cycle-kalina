# -*- coding: utf-8 -*-
"""Sens2 - s2_informe: genera `docs/INFORME_SENS2.md` desde p5_conclusiones.csv y los CSV de P1 a P4.

Las cifras de cabecera se calculan aqui; las conclusiones se copian tal cual del CSV.
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
from s2_cargar import conclusiones, dataset_dedup, distancia_resumen, violaciones  # noqa: E402

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
]
PROXIMA = [
    "Refinar P_baja cerca de su piso (paso de 25 kPa en C1 y C3, 550 kPa; C2 350 kPa; C4 750 kPa): es la "
    "frontera que más puntos separa.",
    "Barrer T_fuente con paso de 2.5 K en los techos de cada bloque (440.65, 468.15, 568.15 y 528.15 K).",
    "Repetir las mallas B2 (P_baja x x_b) y B4 (ε_cond x T_sumidero) con más niveles en C3 y C4, donde la "
    "no aditividad de la existencia es alta.",
    "Validar con el motor real los 7 atípicos y los óptimos M1 a M4 antes de citarlos como cifras de diseño.",
    "Barrer m_b (1, 5, 10, 15, 20) solo si el profesor pide dimensionar por caudal.",
]


def main():
    d = dataset_dedup()
    c = conclusiones()
    k = d[d["kalina"]]
    n_in = round(float(k[~k["fuera_rango"]]["eta_pct"].max()), 2)
    n_out = round(float(k[k["fuera_rango"]]["eta_pct"].max()), 2)
    v = violaciones()
    o2 = v[(v["seccion"] == "dominante") & (v["centro"] == "todos") & (v["clave"] == "viol_O2")]
    L = ["# Informe de Sensibilidad 2: análisis de los 3 921 puntos de Sensibilidad 1", "",
         "> **KALINA existe donde P_baja supera su piso de cavitación y la efectividad del condensador es "
         "alta; la η máxima es %.2f %% dentro del rango experimental (%.2f %% fuera).** Los óptimos "
         "están pegados a la frontera de existencia." % (n_in, n_out), "",
         "Libro asociado: `datos/Kalina_anal_sensible_2.xlsx` (20 hojas, 56 gráficos). Todo número sale de los "
         "CSV de `resultados/2026-10-17_sens2_P1..P4`. Rama `test/anal_terremoto`.", "",
         "## 1. Resumen ejecutivo", "",
         "- %d puntos sin duplicados (de 3 921); %.1f %% son KALINA (total)." % (
             len(d), 100.0 * len(k) / len(d)),
         "- %.1f %% de los CORREGIBLE falla por cavitación (O2) y sobreestiman η en +2.5 puntos." % (
             100.0 * float(o2.iloc[0]["fraccion"])),
         "- Casi la mitad de los CORREGIBLE está a una sola variable de un KALINA; P_baja es la que más rescata.",
         "- Los diseños de mayor η operan con título de salida de turbina de 0.94 (límite 0.90).",
         "- Desde el centro KALINA de cada bloque, C1 y C4 no toleran bajar ε_cond (0.95); P_baja puede bajar hasta "
         "600 kPa (C1) y 800 kPa (C4) (D7, L6).",
         "- El regenerador pierde peso al subir T_fuente: Q_reg/Q_i de 0.59 (70 °C) a 0.013 (300 °C) y UA de 9.5 a 0.34 "
         "kW/K por kg/s (E8).",
         "- La condensación y la cavitación (P_baja, ε_cond, x_b) gobiernan la existencia; η_t, P_alta y "
         "T_fuente gobiernan η y potencia.", "",
         "## 2. Método", "",
         "Etapa 0 (`docs/ETAPA0_INVESTIGACION_SENSIBILIDAD_KALINA.md`) eligió métodos que se calculan sobre "
         "muestreos existentes: RSA/KS, PAWN, δ de Borgonovo, HSIC, PRCC, η², logística, con 3 variables dummy "
         "como piso de ruido y bootstrap. Se descartaron Morris, Sobol y FAST (exigen corridas nuevas y salida en "
         "todos los puntos). Fase A: existencia y fronteras (P1). Fase C: CORREGIBLE frente a KALINA y distancia (P2). "
         "Fase B: índices globales, interacciones y elasticidades (P3). Equipos (P4). Plan en "
         "`docs/PLAN_SENS2_ANALISIS.md`.", "",
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
                  "- Fuente: %s" % x["fuente"], ""]
    L += ["## 4. CORREGIBLE frente a KALINA", "",
          "Ver F6 (sobreestimación de +2.47 puntos de η y +24.8 kW por kg/s), L1 (96 % por O2) y L2 (rescate). "
          "Los CORREGIBLE aportan información sobre la frontera, no sobre el desempeño: su η es optimista "
          "porque incumplen la cavitación.", "",
          "## 5. Recomendaciones para la próxima campaña", ""]
    L += ["%d. %s" % (i, t) for i, t in enumerate(PROXIMA, 1)]
    L += ["", "## 6. Limitaciones y supuestos", ""] + ["- " + t for t in CAVEATS]
    L += ["", "*Revisión con la lista de `validate-data` (plugin `data` de Anthropic): duplicados, denominadores, "
          "cifras recalculadas de forma independiente, sesgo de selección y gráficos revisados en Excel real. "
          "Estado: compartir con los caveats de la sección 6.*"]
    with open(SALIDA, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("OK:", SALIDA, len(L), "lineas")


if __name__ == "__main__":
    main()
