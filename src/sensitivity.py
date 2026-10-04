"""Barrido paramétrico del ciclo Kalina KSC-11: producto cartesiano sobre
cualquier combinación de variables de entrada declaradas `Fijo`/`Barrido`.

Diseño:
- Cada variable de `resolver_ciclo` es `Fijo(valor)` o `Barrido(inicio, fin,
  paso)` (cerrando en `fin`); un `Fijo` es un `Barrido` de un punto. Varias en
  `Barrido` dan su producto cartesiano (la rejilla completa, no un optimizador:
  el dominio tiene discontinuidades del separador y huecos por cavitación).
- Un punto que no converge (`CicloNoConvergeError`) o cuyo backend no cubre
  el estado pedido (`PropertyRangeError`) se marca `NO_CONVERGIO` con la
  razón, y el barrido CONTINÚA con el siguiente punto — nunca se detiene.
- VERIFICACIÓN A+B (opcional, retrocompatible). Con `motor_real=`,
  `verificar_turbina` (opción B) recalcula la salida isentrópica de turbina de
  cada punto KALINA y la compara con la que usó el motor del barrido. Un KALINA
  no verificado NO se reclasifica ni se oculta: se señala en `B_*` (señalar, no
  corregir). Con un `TeqpVerificado` (opción A) cada fila anota las recurrencias
  del punto; `T_amb_diseno=` fija el piso O2 (ver `ejecutar_barrido`).
- RANGO CONFIABLE (opcional): con `motor_rango=` cada fila lleva `COLUMNAS_RANGO`
  (ver `rangos_motor`); la clasificación no cambia.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass

import pandas as pd

from ._cycle_loops import CicloNoConvergeError
from ._rango_barrido import COLUMNAS_RANGO, anotar_rango
from .cycle_solver import resolver_ciclo
from .properties.adapter import PropertyRangeError
from .restricciones import Clasificacion, evaluar_ciclo
from .verificacion_motor_real import verificar_turbina

__all__ = ["Fijo", "Barrido", "generar_valores", "generar_combinaciones",
           "ejecutar_barrido", "tabla_barrido", "COLUMNAS_A", "COLUMNAS_B",
           "COLUMNAS_RANGO"]

VARIABLES_BARRIBLES = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b",
                       "m_b", "eta_t", "eta_p", "eps_hrvg", "eps_reg",
                       "eps_cond")

# Las que `evaluar_ciclo` recibe del combo: las 11 menos las efectividades.
_CRIT = tuple(v for v in VARIABLES_BARRIBLES if v not in ("eta_t", "eta_p"))

# Columnas de la verificación A (respaldo del motor real en el ciclo) y B
# (comparación final de la turbina). Las rellena `ejecutar_barrido`, con None
# en lo que no aplique; `B_error` es None si no hubo error (el mensaje real
# queda en `B_verificado` = None).
COLUMNAS_A = ("A_recurrencias", "A_verificacion_incompleta")
COLUMNAS_B = ("B_verificado", "B_dh4s", "B_t_s", "B_error")


@dataclass(frozen=True)
class Fijo:
    """Una variable con un único valor en toda la corrida."""
    valor: float


@dataclass(frozen=True)
class Barrido:
    """Una variable barrida en `[inicio, fin]` con paso `paso` (mismas unidades)."""
    inicio: float
    fin: float
    paso: float


def generar_valores(spec: Fijo | Barrido) -> list[float]:
    """Expande un `Fijo`/`Barrido` a la lista de valores de esa variable.

    Un `Barrido` cierra el rango incluyendo siempre `fin`, aun si `paso` no
    divide exacto el intervalo (se añade `fin` como último punto si no cayó
    ya dentro de la rejilla, con una tolerancia de 1e-9·paso).
    """
    if isinstance(spec, Fijo):
        return [spec.valor]
    if not isinstance(spec, Barrido):
        raise TypeError(f"se esperaba Fijo o Barrido; se recibió {spec!r}")
    if spec.paso <= 0:
        raise ValueError(f"paso debe ser > 0; se recibió {spec.paso!r}")
    if spec.inicio > spec.fin:
        raise ValueError(
            f"inicio debe ser <= fin; se recibió inicio={spec.inicio!r}, "
            f"fin={spec.fin!r}")
    tol = spec.paso * 1e-9
    valores: list[float] = []
    v = spec.inicio
    while v <= spec.fin + tol:
        valores.append(round(v, 10))
        v += spec.paso
    if not valores or abs(valores[-1] - spec.fin) > tol:
        valores.append(spec.fin)
    return valores


def generar_combinaciones(variables: dict[str, Fijo | Barrido]
                          ) -> list[dict[str, float]]:
    """Producto cartesiano de los valores de cada variable declarada."""
    claves = list(variables)
    listas = [generar_valores(variables[k]) for k in claves]
    return [dict(zip(claves, combo)) for combo in itertools.product(*listas)]


def _contadores(backend):
    """`(n_recurrencias, n_fallos)` del backend ANTES de resolver este punto;
    `(None, None)` si no lleva registro de A. Son contadores acumulados: su
    diferencia antes/después es lo que pasó en ESE punto."""
    return (getattr(backend, "n_recurrencias", None),
            getattr(backend, "n_fallos", None))


def _anotar_ab(fila, combo, resultado, backend, motor_real, antes):
    """Rellena en `fila` las columnas A/B de UN punto y la devuelve. `B_*` solo
    con `motor_real` y punto KALINA (que conserva su clase aunque no verifique);
    `A_*` requiere el registro de `TeqpVerificado` (delta de ESE punto)."""
    n_antes, fallos_antes = antes
    if n_antes is not None:
        fila["A_recurrencias"] = backend.n_recurrencias - n_antes
        fila["A_verificacion_incompleta"] = (
            None if fallos_antes is None else (backend.n_fallos - fallos_antes) > 0)
    if motor_real is None:
        return fila
    fila.update(dict.fromkeys(COLUMNAS_B))
    if resultado is not None and (
            fila["clasificacion"] == Clasificacion.KALINA.value):
        v = verificar_turbina(resultado, P_baja=combo["P_baja"],
                              motor_real=motor_real, eta_t=combo["eta_t"])
        fila.update(B_verificado=v["verificado"], B_dh4s=v["dh4s"],
                    B_t_s=v["t_real_s"], B_error=v["error"] or None)
    return fila


def ejecutar_barrido(backend, variables: dict[str, Fijo | Barrido], *,
                     motor_real=None, T_amb_diseno: float | None = None,
                     motor_rango: str | None = None,
                     modo_rango: str = "extrapolar_marcar") -> list[dict]:
    """Resuelve el ciclo para cada combinación y clasifica cada punto.

    ``variables`` debe declarar las 11 variables de `resolver_ciclo`
    (``VARIABLES_BARRIBLES``) como `Fijo` o `Barrido`. Cada fila registra los
    valores usados, si convergió, su clasificación (`NO_CONVERGIO`/`INVIABLE`/
    `CORREGIBLE`/`KALINA`) y `eta`/`Wnet`.

    ``motor_real`` (un `AmmoniaWaterAdapter`) activa la verificación B de cada
    KALINA; con `TeqpVerificado` las filas llevan `COLUMNAS_A`. ``T_amb_diseno``
    es el piso O2 de `evaluar_ciclo` (``None`` = 303.55 K; para la zona KALINA,
    ``T_sumidero``). ``motor_rango`` ("real"/"teqp") añade `COLUMNAS_RANGO`.
    Sin estos keywords el resultado es exactamente el de siempre.
    """
    faltantes = set(VARIABLES_BARRIBLES) - set(variables)
    if faltantes:
        raise ValueError(
            f"faltan variables en el barrido: {sorted(faltantes)}; se "
            f"requieren las 11 de VARIABLES_BARRIBLES")

    filas = []
    for combo in generar_combinaciones(variables):
        fila = dict(combo)
        antes = _contadores(backend)
        try:
            resultado = resolver_ciclo(backend, **combo)
        except (CicloNoConvergeError, PropertyRangeError) as exc:
            fila.update(convergio=False,
                       clasificacion=Clasificacion.NO_CONVERGIO.value,
                       eta=None, Wnet=None, mensaje=str(exc))
            fila = _anotar_ab(fila, combo, None, backend, motor_real, antes)
            filas.append(anotar_rango(fila, combo, None, motor_rango, backend,
                                      modo_rango))
            continue
        crit = {k: combo[k] for k in _CRIT}
        if T_amb_diseno is not None:
            crit["T_amb_diseno"] = T_amb_diseno
        validacion = evaluar_ciclo(backend, resultado, **crit)
        fila.update(convergio=True, clasificacion=validacion.clasificacion.value,
                   eta=resultado["eta"], Wnet=resultado["Wnet"],
                   mensaje=validacion.mensaje_reporte())
        fila = _anotar_ab(fila, combo, resultado, backend, motor_real, antes)
        filas.append(anotar_rango(fila, combo, resultado, motor_rango, backend,
                                  modo_rango))
    return filas


def tabla_barrido(filas: list[dict]) -> pd.DataFrame:
    """DataFrame del barrido: una fila por punto, en el orden ya resuelto.

    Las columnas de verificación se añaden al final solo si la verificación llegó
    a correrse (alguna fila con `B_verificado` o `A_recurrencias` no nulo); sin
    ellas, la tabla es exactamente la de siempre.
    """
    columnas = list(VARIABLES_BARRIBLES) + [
        "convergio", "clasificacion", "eta", "Wnet", "mensaje"]
    if filas:
        if any(f.get("A_recurrencias") is not None for f in filas):
            columnas += list(COLUMNAS_A)
        if any(f.get("B_verificado") is not None for f in filas):
            columnas += list(COLUMNAS_B)
        if any(f.get("fuera_rango") is not None for f in filas):
            columnas += list(COLUMNAS_RANGO)
    return pd.DataFrame(filas)[columnas]
