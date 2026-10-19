# -*- coding: utf-8 -*-
"""Sens2 - s2_mapa: unica definicion del mapa de preguntas del profesor, conclusiones y hojas del libro.

La tabla de preguntas de `Conclusion consolidada` y la del LEEME salen de aqui (no se escriben a mano). `tests/test_sens2_docs.py` exige que cada
conclusion de `p5_conclusiones.csv` y cada hoja del libro figure en este mapa (en una pregunta o en el apoyo), de modo que una conclusion u hoja nueva
no puede quedar sin asignar.
"""
import re

PREGUNTAS = [
    dict(texto="En que rangos hay KALINA (total)?",
         hojas=["F1 Existencia", "F1 Reglas y zonas grises", "F3 Pisos 25 kPa y reintento"],
         conclusiones=["D1", "D2", "D3", "D4", "D5", "D6", "D8", "D9"]),
    dict(texto="Partiendo de un KALINA, que pasa al mover una o dos variables?",
         hojas=["F1 Margenes de operacion", "F2 CORREGIBLE vs KALINA", "F2 Distancia y rescate", "F5 Superficies de respuesta", "F5 Incertidumbre",
                "F5 Incertidumbre simetrica"],
         conclusiones=["D7", "L6", "L2", "F6", "F5", "R1", "D8", "U1", "U2", "U3", "U4", "U5"]),
    dict(texto="Como se comporta el regenerador y el ciclo con la temperatura de la fuente?",
         hojas=["F4 Regenerador vs T_fuente", "F4 Regenerador y condensador", "F4 Ciclo vs T_fuente", "F4 Optimo vs T_fuente"],
         conclusiones=["E8", "E4", "M6", "M7"]),
    dict(texto="Que datos necesito para preseleccionar los equipos?",
         hojas=["F4 Preseleccion", "F4 Equipos por kW", "F4 Caudales y bomba"],
         conclusiones=["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E9", "E10"]),
]

# Apoyo: conclusiones y hojas que no responden una pregunta concreta pero sostienen el analisis.
APOYO_CONCLUSIONES = {
    "Maxima eficiencia y sensibilidad": ["M1", "M2", "M3", "M4", "M5", "F1", "F2", "F3", "F4"],
    "Limites del analisis y de KALINA": ["L1", "L3", "L4", "L5", "L7", "L8", "L9", "L10"],
}
APOYO_HOJAS = ["LEEME", "Conclusion consolidada", "F3 Indices globales", "F3 Interacciones", "F3 Elasticidades", "F6 Respaldo libro viejo",
               "F7 Rigor estadistico", "F7 Nulo y correccion FDR", "Confianza", "D1 Datos puntos", "D2 Datos fronteras", "D3 Datos zonas grises",
               "D4 Datos distancia", "D5 Datos indices", "D6 Datos equipos", "F4 Turbina"]


def compacto(ids):
    """['D1','D2','D3','D4','D5','D6','D8','D9'] -> 'D1 a D6; D8; D9' (corridas de 3 o mas con el mismo prefijo y numeros seguidos)."""
    partes, i = [], 0
    while i < len(ids):
        m = re.fullmatch(r"([A-Z]+)(\d+)", ids[i])
        j = i
        if m:
            while j + 1 < len(ids) and ids[j + 1] == "%s%d" % (m.group(1), int(re.fullmatch(r"[A-Z]+(\d+)", ids[j])[1]) + 1):
                j += 1
        if j - i >= 2:
            partes.append("%s a %s" % (ids[i], ids[j]))
            i = j + 1
        else:
            partes.append(ids[i])
            i += 1
    return "; ".join(partes)


def tabla_consolidada():
    """Filas (pregunta, hojas, conclusiones) de `Conclusion consolidada`."""
    return [(p["texto"], "; ".join(p["hojas"]), compacto(p["conclusiones"])) for p in PREGUNTAS]


def tabla_leeme():
    """Filas (pregunta, hojas) del LEEME."""
    return [(p["texto"], "; ".join(p["hojas"])) for p in PREGUNTAS]


def conclusiones_asignadas():
    ids = [c for p in PREGUNTAS for c in p["conclusiones"]]
    ids += [c for v in APOYO_CONCLUSIONES.values() for c in v]
    return ids


def hojas_asignadas():
    return [h for p in PREGUNTAS for h in p["hojas"]] + list(APOYO_HOJAS)
