"""Selección de motor de propiedades para la UI Streamlit.

Separado de `ui_helpers.py` (que solo formatea datos ya calculados) porque
esto construye instancias reales de `PropertyBackend`. Dos motores cubren
la mezcla NH3-H2O en este entorno: `AmmoniaWaterAdapter` (motor riguroso,
IAPWS G4-01, el camino por defecto del proyecto) y `TeqpAdapter` (NIST
teqp, alternativa de rendimiento — ver TASK_CONTEXT 2026-09-18). Los otros
dos listados (`IAPWSAdapter`, `PyfluidsAdapter`) no soportan el par NH3-H2O
en este entorno y se muestran solo como referencia; si se eligen, se cae a
`AmmoniaWaterAdapter` con una advertencia.
"""

from __future__ import annotations

__all__ = ["BACKENDS", "BACKEND_REAL", "BACKEND_TEQP", "construir_backend"]

BACKEND_REAL = "AmmoniaWaterAdapter"
BACKEND_TEQP = "TeqpAdapter"
BACKENDS = (
    f"{BACKEND_REAL} — mezcla NH3-H2O (motor riguroso IAPWS G4-01, "
    "recomendado, ~8-9 min por corrida)",
    f"{BACKEND_TEQP} — mezcla NH3-H2O (NIST teqp, ~10-20x más rápido; "
    "validado dentro de <0.5% en h/s vs el motor riguroso, ver "
    "TASK_CONTEXT 2026-09-18)",
    "IAPWSAdapter (agua pura) — no aplica a la mezcla NH3-H2O en este entorno",
    "PyfluidsAdapter (CoolProp) — no soporta el par NH3-H2O en este entorno",
)


def construir_backend(backend_sel: str, x: float):
    """Backend real a partir de la selección de la UI.

    Devuelve ``(instancia, nombre_plano, advertencia)``; ``advertencia`` es
    ``None`` salvo que ``backend_sel`` sea uno de los motores que no cubren
    la mezcla NH3-H2O en este entorno, en cuyo caso se cae a
    `AmmoniaWaterAdapter` y se devuelve el texto a mostrar con `st.warning`.
    """
    from .properties.ammonia_water_adapter import AmmoniaWaterAdapter
    from .properties.teqp_adapter import TeqpAdapter

    if backend_sel == BACKENDS[1]:
        return TeqpAdapter(x=x), BACKEND_TEQP, None
    advertencia = None
    if backend_sel != BACKENDS[0]:
        advertencia = (
            "⚠️ El motor elegido no cubre la mezcla NH3-H2O en este entorno; "
            f"se usará **{BACKEND_REAL}** (IAPWS G4-01)."
        )
    return AmmoniaWaterAdapter(x=x), BACKEND_REAL, advertencia
