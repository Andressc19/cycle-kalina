"""Criterios numéricos N2, N3 (N1 se cubre fuera de este módulo: ver
`clasificacion.py` — es la ausencia de `CicloNoConvergeError` del solver.
N4, dominio de validez del motor de propiedades, queda fuera de alcance:
UNRESOLVED, sin rango de T declarado en este repo — ver TASK_CONTEXT.md).

Tolerancia común: 1e-3 relativo. El catálogo del vault usa 1e-6, pero ese
valor fue calibrado para un solver distinto (`kalina.py` monolítico); ESTE
solver relajó deliberadamente `tol_T10` de 1e-4 a 1e-3 K por rendimiento
(`cycle_solver.py`, ruido medido ~7e-5 K → ~1e-2 kJ/kg de energía). Medido
empíricamente con el backend fake y los parámetros por defecto: un punto que
converge correctamente deja un residuo relativo de N2 de ~1.85e-6 — MÁS
ESTRICTO que 1e-6 habría marcado ese punto, ya bien convergido, como
NO_CONVERGIO. 1e-3 deja ~500x de margen sobre ese ruido medido, consistente
con el criterio de relajación ya usado en este proyecto.
"""

from __future__ import annotations

from .modelos import Clasificacion, Falla, Severidad

__all__ = ["verificar_n2", "verificar_n3"]

_TOL = 1e-3


def verificar_n2(resultado: dict) -> Falla | None:
    """N2 — balance global de energía: |Qi - Qout - Wnet| <= 1e-3*Qi."""
    Qi, Qout, Wnet = resultado["Qi"], resultado["Qout"], resultado["Wnet"]
    residuo = abs(Qi - Qout - Wnet)
    limite = _TOL * abs(Qi)
    if residuo <= limite:
        return None
    return Falla(
        codigo="N2", severidad=Severidad.NUMERICO,
        clasificacion=Clasificacion.NO_CONVERGIO,
        mensaje="el balance global de energía no cierra dentro de la tolerancia",
        variable="Qi - Qout - Wnet", valor_medido=residuo,
        valor_esperado=f"<= {limite:.6g} kW (1e-3 relativo a Qi)",
        causa_probable="residuo numérico del lazo de convergencia por encima de "
                        "lo esperado, o un componente con un balance mal cerrado",
        sugerencia="revisar tolerancias del solver (tol_T1, tol_T10) o si algún "
                    "componente cambió sin actualizar su balance de energía",
    )


def verificar_n3(resultado: dict, x_b: float) -> list[Falla]:
    """N3 — balance de especie en separador y absorbedor.

    ``x_b`` es la composición global de entrada del ciclo (parámetro del
    caso, no derivada de ningún estado): el separador reparte la corriente 2
    (que entra con x=x_b, invariante en HRVG) en vapor/líquido, y el
    absorbedor debe reconstruirla en la corriente 8.
    """
    fallas: list[Falla] = []
    e = resultado["estados"]
    e2, e3, e5, e8 = e["e2"], e["e3"], e["e5"], e["e8"]

    if e2.m is not None and e3.m is not None and e5.m is not None:
        # Referencia: la masa REAL de entrada al separador (e2.m), no la suma
        # de sus salidas — así el criterio también detecta una violación del
        # balance de masa total (m3+m5 != m2), no solo de composición.
        m_entrada = e2.m
        residuo = abs(m_entrada * x_b - e3.m * e3.x - e5.m * e5.x)
        limite = _TOL * m_entrada * x_b
        if residuo > limite:
            fallas.append(Falla(
                codigo="N3", severidad=Severidad.NUMERICO,
                clasificacion=Clasificacion.NO_CONVERGIO,
                mensaje="balance de especie del separador no cierra",
                variable="m*x (separador)", valor_medido=residuo,
                valor_esperado=f"<= {limite:.6g} (1e-3 relativo)",
                causa_probable="error numérico en la regla de la palanca del "
                                "separador o en el flash de equilibrio, o "
                                "m3+m5 no reconstruye m2 (balance de masa total)",
                sugerencia="revisar `separador.py` y el flash "
                            "`equilibrio_liquido_vapor` del backend",
            ))

    residuo_abs = abs(e8.x - x_b)
    limite_abs = _TOL * x_b
    if residuo_abs > limite_abs:
        fallas.append(Falla(
            codigo="N3", severidad=Severidad.NUMERICO,
            clasificacion=Clasificacion.NO_CONVERGIO,
            mensaje="balance de especie del absorbedor no reconstruye x_b",
            variable="x8", valor_medido=e8.x,
            valor_esperado=f"{x_b:.6g} +/- {limite_abs:.3g}",
            causa_probable="el lazo del ciclo no convergió con precisión "
                            "suficiente en composición",
            sugerencia="revisar el cierre del regenerador a nivel de ciclo en "
                        "`_cycle_loops.py`",
        ))
    return fallas
