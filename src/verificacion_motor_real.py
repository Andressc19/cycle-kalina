"""`verificar_turbina` — verificación final (opción **B**) de la salida
isentrópica de turbina contra el motor real NH3-H2O (TASK_CONTEXT
2026-09-27-medicion-tiempos-A-B).

QUÉ ES. La opción A (`src/properties/teqp_verificado.py`) corrige DENTRO del ciclo
cada llamada de teqp que cae en la zona de riesgo de fase. B hace una sola
comprobación, al final: para el punto ya resuelto recalcula con el motor real la
salida isentrópica `h4s = h(P_baja, s3, x3)` y la compara con la que usó el motor
que resolvió el ciclo. Si la diferencia supera el umbral, el punto queda marcado
como **no verificado** (no se corrige: se señala).

POR QUÉ ES BARATA. Una sola llamada al motor real por punto (~2-4 s medidos) frente
a las N llamadas que puede hacer A. Y el lado "teqp" NO cuesta ninguna consulta:
`h4s` se reconstruye con la inversa exacta de `src/components/turbina.py:36`
(`h4 = h3 - eta_t*(h3 - h4s)` -> `h4s = h3 - (h3 - h4)/eta_t`), que solo lee
`e3.h`, `e4.h` y `eta_t`, ya calculados. En aritmética real la reconstrucción es
idéntica; en binario64 difiere en unos pocos ulp (medido: 0.0 y 2.3e-13 kJ/kg en
los dos puntos de los tests, a ~1.6e3 kJ/kg), trece órdenes de magnitud por debajo
del umbral de 2.0 kJ/kg y por debajo del offset sistemático de 0.7-1.6 kJ/kg entre
los dos motores. `tests/test_verificacion_motor_real.py` lo comprueba contra
`backend_teqp.h(...)`, que sí se paga: 0.16-0.20 s por llamada (brentq sobre
`_teqp_flash.estado`), o sea un 4-9 % del costo de B. Esa es la razón de NO pasar
`backend_teqp` en las mediciones de costo: mantiene `t_B` igual al costo del motor
real y nada más.

OJO CON LA SEMÁNTICA EN MODO A+B. Si el ciclo se resolvió con `TeqpVerificado`, la
`h4s_teqp` reconstruida es la que el ciclo USÓ, que puede ser ya el valor del motor
real (si una recurrencia de A la sustituyó). Ahí `dh4s ~ 0` significa "A ya lo
corrigió", NO "teqp acertó". `h4s_teqp_fuente` dice de dónde salió el valor.

NO INVENTA. Si el motor real falla, devuelve `verificado=None` y el mensaje real de
la excepción en `error`: jamás devuelve el valor de teqp como si estuviera
verificado. La falta de `eta_t` en la vía reconstruida sí es un error de
programación (argumento obligatorio) y se lanza como `ValueError`.
"""

from __future__ import annotations

import time

from .properties.adapter import PropertyRangeError

__all__ = ["verificar_turbina", "UMBRAL_KJKG"]

UMBRAL_KJKG = 2.0        # kJ/kg — tolerancia de B sobre |h4s_teqp - h4s_real|

# Errores que el motor real puede lanzar por no cubrir el estado pedido: los de
# dominio del adapter (`PropertyRangeError`) y los crudos del motor portado
# (RuntimeError/ValueError/NotImplementedError) y los aritméticos de numpy. Mismo
# criterio que `teqp_verificado._EXC_REAL`, para que un fallo suyo NUNCA tumbe la
# corrida: se registra y se devuelve `verificado=None`.
_EXC_REAL = (PropertyRangeError, RuntimeError, ValueError, NotImplementedError,
             ArithmeticError)


def verificar_turbina(resultado, *, P_baja, motor_real,
                      umbral_kJkg: float = UMBRAL_KJKG, backend_teqp=None,
                      eta_t=None) -> dict:
    """Verifica contra el motor real la salida isentrópica de turbina de un punto.

    Parámetros: ``resultado`` es el dict de `src.cycle_solver.resolver_ciclo` (se
    leen `estados.e3` para `s3`/`x3`/`h3` y `estados.e4` para `h4`); ``P_baja``
    [kPa]; ``motor_real`` un `AmmoniaWaterAdapter`; ``umbral_kJkg`` tolerancia.

    ``h4s_teqp`` sale de ``backend_teqp.h(P_baja, s=s3, x=x3)`` si se pasa un
    ``backend_teqp``; si no, se reconstruye con la inversa exacta de
    `turbina.resolver` a partir de ``e3.h``, ``e4.h`` y ``eta_t`` (argumento
    obligatorio en esa vía, ver docstring del módulo).

    Devuelve ``dict`` con ``h4s_teqp``, ``h4s_real``, ``dh4s = h4s_teqp -
    h4s_real``, ``verificado = |dh4s| <= umbral_kJkg``, ``t_real_s`` (segundos en
    el motor real), ``error`` ("" o el mensaje real de la excepción) y, como
    campos extra de trazabilidad, ``h4s_teqp_fuente``, ``P_baja``, ``s3``, ``x3``.
    Si el motor real falla: ``h4s_real=None``, ``dh4s=None``, ``verificado=None``
    y ``error`` con el mensaje real.
    """
    estados = resultado["estados"]
    e3, e4 = estados["e3"], estados["e4"]
    s3, x3 = float(e3.s), float(e3.x)

    # -- lado "teqp": reconstruido (gratis) o consultado (una llamada) ----------
    if backend_teqp is not None:
        h4s_teqp = float(backend_teqp.h(P_baja, s=s3, x=x3))
        fuente = "backend_teqp"
    else:
        if eta_t is None:
            raise ValueError(
                "verificar_turbina: sin `backend_teqp` hace falta `eta_t` para "
                "reconstruir h4s como h3 - (h3 - h4)/eta_t (inversa exacta de "
                "src/components/turbina.py). Se recibió eta_t=None."
            )
        eta_t = float(eta_t)
        if eta_t <= 0.0:
            raise ValueError(f"eta_t debe ser > 0; se recibió {eta_t!r}.")
        h3, h4 = float(e3.h), float(e4.h)
        h4s_teqp = h3 - (h3 - h4) / eta_t
        fuente = "reconstruido"

    # -- lado real: una sola llamada, cronometrada ------------------------------
    t0 = time.perf_counter()
    h4s_real, error = None, ""
    try:
        h4s_real = float(motor_real.h(P_baja, s=s3, x=x3))
    except _EXC_REAL as exc:
        error = f"{type(exc).__name__}: {exc}"[:200]
    t_real = time.perf_counter() - t0

    comun = dict(h4s_teqp=h4s_teqp, h4s_real=h4s_real, t_real_s=t_real,
                 h4s_teqp_fuente=fuente, P_baja=P_baja, s3=s3, x3=x3)
    if h4s_real is None:
        return dict(comun, dh4s=None, verificado=None, error=error)
    dh4s = h4s_teqp - h4s_real
    return dict(comun, dh4s=dh4s,
                verificado=abs(dh4s) <= float(umbral_kJkg), error="")
