# -*- coding: utf-8 -*-
"""Sens2 - s2_limites: unica lista de los limites declarados del trabajo (lo que no se resuelve sin motor, datos externos o otro metodo).

La tabla del LEEME y la de `docs/VALIDACION_SENS2.md` (bloque `<!--t:limites-->`, mantenido por `docs_sync.py`) salen de esta lista;
`tests/test_sens2_docs.py` comprueba que la conclusion citada en cada limite exista.
"""
ENCABEZADOS = ["Limite", "Conclusion", "Que lo resolveria", "Costo aproximado"]
LIMITES = [
    ("Separar «no existe» de «no convergió» en los NO_CONVERGIO (el reintento con más tiempo no recupera ninguno)", "L10, D3, F3",
     "Otro método de resolución del motor", "No estimado"),
    ("η máxima frente a T_fuente: un solo punto de partida por banda, 21 a 32 evaluaciones", "M7",
     "3 a 5 puntos de partida por banda (motor)", "≈ 1 400 puntos, 5 a 6 h"),
    ("Criterio de cavitación de margen cero, no NPSH", "D9, L7",
     "Datos de la bomba (externos) y un margen acordado", "Externo"),
    ("Solo el motor teqp: sin validación experimental propia del ciclo", "L5, L8",
     "Datos experimentales del ciclo (externos)", "Externo"),
    ("Caja común de rangos entre bloques inviable (1 a 9 puntos por bloque)", "F1, F2",
     "Muestreo dirigido a la caja común (motor)", "No estimado"),
]


def tabla_md():
    """Tabla Markdown de los limites declarados."""
    filas = ["| " + " | ".join(ENCABEZADOS) + " |", "|" + "---|" * len(ENCABEZADOS)]
    filas += ["| " + " | ".join(f) + " |" for f in LIMITES]
    return "\n".join(filas)


def conclusiones_citadas():
    ids = []
    for _, c, _, _ in LIMITES:
        ids += [x.strip() for x in c.split(",")]
    return ids
