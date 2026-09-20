"""Criterios operativos O1, O2, O3, O5.

O4 (P_alta > P_baja) fue eliminado deliberadamente por el propio catálogo del
vault (evaluaba entradas, no la solución convergida; redundante con O3) — no
se implementa aquí, es validación de entrada. O6/CD (rocío ácido, cierre
declarado) no aplican: requieren C_g finito, no implementado en este repo.

O2 se evalúa contra un T_amb de diseño de al menos 30.4 °C por defecto
(margen de diseño conservador — decisión explícita del vault, "no la media").
Ese piso es el parámetro configurable `T_amb_diseno` de `verificar_operativos`
(default 303.55 K = 30.4 °C, expuesto también en la UI de la app): se
re-resuelve el condensador con `max(T_sumidero_de_la_corrida, T_amb_diseno)`
a partir del mismo estado 8 ya convergido, sin re-resolver todo el ciclo
(estado 8 no depende de T_sumidero). El máximo es necesario porque, si un
barrido explora un T_sumidero por encima del piso, evaluar solo contra el
fijo subestimaría el riesgo real de cavitación en ese punto — el piso es un
mínimo de diseño, no un techo. Etiqueta CORREGIBLE, no INVIABLE (decisión
del usuario: es una falla operativa evitable ajustando subenfriamiento, no
una imposibilidad física).
"""

from __future__ import annotations

from ..components import condensador
from .modelos import Clasificacion, Falla, Severidad

__all__ = ["verificar_operativos"]

DQ = 1e-3               # margen del criterio O5 (mismo valor que el motor: ver
                        # `_kalina_flash.py::DQ`, "margen del criterio O5")


def verificar_operativos(resultado: dict, backend, *, P_alta: float,
                         P_baja: float, T_sumidero: float, x_b: float,
                         m_b: float, eps_cond: float,
                         T_amb_diseno: float = 303.55) -> list[Falla]:
    """Criterios O1, O2, O3 y O5 sobre un punto ya resuelto.

    ``T_amb_diseno`` es el PISO de diseño del criterio O2 (cavitación) en K:
    el condensador se re-resuelve contra `max(T_sumidero, T_amb_diseno)`.
    Default 303.55 K (30.4 °C, decisión del vault); configurable desde la UI
    sin cambiar el comportamiento de quien no lo pase.
    """
    fallas: list[Falla] = []
    e = resultado["estados"]

    # O1 — título de turbina (tecnológico, VALIDO_ADVERTENCIA)
    _, q4 = backend.fase_de(P_baja, e["e4"].T, e["e4"].x)
    if q4 < 0.90:
        fallas.append(Falla(
            codigo="O1", severidad=Severidad.TECNOLOGICO,
            clasificacion=Clasificacion.VALIDO_ADVERTENCIA,
            mensaje="título de vapor a la salida de la turbina bajo el umbral "
                    "tecnológico usual (erosión de álabes)",
            variable="q4", valor_medido=q4, valor_esperado=">= 0.90",
            causa_probable="expansión hasta P_baja deja la mezcla demasiado "
                            "húmeda para ese eta_t y esa composición",
            sugerencia="considerar recalentamiento o revisar P_baja/x_b; se "
                        "excluye del ranking de SELECCION pero se conserva en "
                        "las tablas",
        ))

    # O2 — cavitación de bomba, contra el peor caso: max(T_sumidero, T_amb_diseno)
    T_amb_evaluar = max(T_sumidero, T_amb_diseno)
    estado9_amb, _ = condensador.resolver(
        e["e8"], backend, T_sumidero=T_amb_evaluar, eps=eps_cond, m=m_b)
    T_sat_L = backend.bubble_point(P_baja, x_b)
    if estado9_amb.T > T_sat_L:
        fallas.append(Falla(
            codigo="O2", severidad=Severidad.CRITICO,
            clasificacion=Clasificacion.CORREGIBLE,
            mensaje="succión de la bomba bifásica bajo el peor caso de T_amb "
                    "(riesgo de cavitación)",
            variable=f"T9 (a T_amb={T_amb_evaluar:.3f} K)",
            valor_medido=estado9_amb.T,
            valor_esperado=f"<= {T_sat_L:.3f} K",
            causa_probable="subenfriamiento insuficiente a la salida del "
                            "condensador bajo el peor caso ambiental",
            sugerencia="aumentar eps_cond o el margen de subenfriamiento de "
                        "diseño del condensador",
        ))

    # O3 — potencia neta positiva (crítico)
    if resultado["Wnet"] <= 0.0:
        fallas.append(Falla(
            codigo="O3", severidad=Severidad.CRITICO,
            clasificacion=Clasificacion.INVIABLE,
            mensaje="potencia neta no positiva: el ciclo no genera trabajo útil",
            variable="Wnet", valor_medido=resultado["Wnet"], valor_esperado="> 0 kW",
            causa_probable="Wt <= Wp para esos parámetros",
            sugerencia="revisar P_alta/P_baja, eta_t/eta_p o m_b",
        ))

    # O5 — operación del separador: calidad del estado 2 dentro de (DQ, 1-DQ)
    _, q2 = backend.fase_de(P_alta, e["e2"].T, x_b)
    if q2 < DQ:
        fallas.append(Falla(
            codigo="O5", severidad=Severidad.CRITICO,
            clasificacion=Clasificacion.INVIABLE,
            mensaje="salida del HRVG líquida (el separador no tiene mezcla que repartir)",
            variable="q2", valor_medido=q2, valor_esperado=f">= {DQ}",
            causa_probable="temperatura de la fuente insuficiente o "
                            "efectividad del HRVG muy baja",
            sugerencia="aumentar T_fuente o eps_hrvg",
        ))
    elif q2 > 1.0 - DQ:
        fallas.append(Falla(
            codigo="O5", severidad=Severidad.TOPOLOGICO,
            clasificacion=Clasificacion.DEGENERADO,
            mensaje="salida del HRVG sobrecalentada: el ciclo deja de ser "
                    "Kalina y pasa a comportarse como Rankine",
            variable="q2", valor_medido=q2, valor_esperado=f"<= {1.0 - DQ}",
            causa_probable="temperatura de la fuente muy alta o efectividad "
                            "del HRVG muy alta",
            sugerencia="reducir T_fuente o eps_hrvg si se busca régimen Kalina",
        ))

    return fallas
