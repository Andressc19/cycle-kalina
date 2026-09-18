"""Criterios de composición C1, C2, C3.

C1b (nunca definido formalmente por el propio vault, ver su "Nota de
recuperación") no se implementa — queda en UNRESOLVED.
"""

from __future__ import annotations

from .modelos import Clasificacion, Falla, Severidad

__all__ = ["verificar_composicion"]

_BANDA_C1 = 0.01  # incertidumbre de composición de equilibrio del motor G4-01


def verificar_composicion(resultado: dict, x_b: float) -> list[Falla]:
    fallas: list[Falla] = []
    e = resultado["estados"]

    # C1 — orden y significancia: x5 (pobre) < x_b < x3 (rico)
    x_pobre, x_rico = e["e5"].x, e["e3"].x
    if not (x_pobre < x_b < x_rico):
        fallas.append(Falla(
            codigo="C1", severidad=Severidad.CRITICO,
            clasificacion=Clasificacion.INVIABLE,
            mensaje="orden de composiciones invertido (x_pobre < x_b < x_rico "
                    "no se cumple)",
            variable="x5, x_b, x3", valor_medido=(x_pobre, x_b, x_rico),
            valor_esperado="x5 < x_b < x3",
            causa_probable="flash de equilibrio del separador fuera de rango "
                            "o error de composición corriente arriba",
            sugerencia="revisar `separador.py` y el flash del backend",
        ))
    elif (x_rico - x_pobre) <= _BANDA_C1:
        fallas.append(Falla(
            codigo="C1", severidad=Severidad.TECNOLOGICO,
            clasificacion=Clasificacion.VALIDO_ADVERTENCIA,
            mensaje="separación de composiciones bajo la banda de incertidumbre "
                    "del motor de propiedades",
            variable="x3 - x5", valor_medido=x_rico - x_pobre,
            valor_esperado=f"> {_BANDA_C1}",
            causa_probable="el punto opera cerca de la campana bifásica "
                            "(equilibrio casi degenerado)",
            sugerencia="tratar la composición de fases en ese punto como no "
                        "resuelta con precisión; no es un error, es un límite "
                        "del modelo",
        ))

    # C2 — fracciones acotadas en todos los estados
    for clave in sorted(e, key=lambda k: int(k[1:])):
        x = e[clave].x
        if not 0.0 < x < 1.0:
            fallas.append(Falla(
                codigo="C2", severidad=Severidad.CRITICO,
                clasificacion=Clasificacion.INVIABLE,
                mensaje=f"composición fuera de (0, 1) en el estado {clave}",
                variable=f"{clave}.x", valor_medido=x, valor_esperado="(0, 1)",
                causa_probable="error de propagación de composición o backend "
                                "fuera de rango",
                sugerencia="revisar la cadena de componentes hasta ese estado",
            ))

    # C3 — caudales acotados y suma unitaria (m_i / m_b)
    m_b_ref = e["e8"].m or e["e9"].m or e["e10"].m
    if m_b_ref:
        suma = (e["e3"].m or 0.0) + (e["e5"].m or 0.0)
        residuo = abs(suma - m_b_ref) / m_b_ref
        if residuo > 1e-6:
            fallas.append(Falla(
                codigo="C3", severidad=Severidad.CRITICO,
                clasificacion=Clasificacion.INVIABLE,
                mensaje="los caudales de vapor y líquido del separador no "
                        "suman el caudal base",
                variable="m3 + m5", valor_medido=suma,
                valor_esperado=f"{m_b_ref:.6g} kg/s",
                causa_probable="regla de la palanca del separador con "
                                "composiciones fuera de banda",
                sugerencia="revisar `separador.py`",
            ))
        for clave in ("e3", "e5"):
            frac = (e[clave].m or 0.0) / m_b_ref
            if not 0.0 <= frac <= 1.0:
                fallas.append(Falla(
                    codigo="C3", severidad=Severidad.CRITICO,
                    clasificacion=Clasificacion.INVIABLE,
                    mensaje=f"fracción de caudal fuera de [0, 1] en {clave}",
                    variable=f"{clave}.m / m_b", valor_medido=frac,
                    valor_esperado="[0, 1]",
                    causa_probable="regla de la palanca fuera de rango físico",
                    sugerencia="revisar la composición de entrada al separador",
                ))

    return fallas
