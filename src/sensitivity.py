"""Barrido paramétrico del ciclo Kalina KSC-11: producto cartesiano sobre
cualquier combinación de variables de entrada declaradas `Fijo`/`Barrido`.

Diseño (ver TASK_CONTEXT.md de la tarea de barrido + restricciones):
- Cada variable de `resolver_ciclo` se declara como `Fijo(valor)` (constante)
  o `Barrido(inicio, fin, paso)` (rejilla equiespaciada, cerrando el rango en
  `fin` aunque `paso` no lo divida exacto). Un `Fijo` es un `Barrido` de un
  solo punto: no hay dos modos separados, uno es caso particular del otro.
- Con varias variables en `Barrido`, el resultado es su producto cartesiano
  (decisión ya tomada en el diseño del proyecto, no una elección de esta
  tarea: la rejilla completa —no un optimizador— es el resultado, porque el
  dominio tiene discontinuidades del separador y huecos por cavitación).
- Un punto que no converge (`CicloNoConvergeError`) o cuyo backend no cubre
  el estado pedido (`PropertyRangeError`) se marca `NO_CONVERGIO` con la
  razón, y el barrido CONTINÚA con el siguiente punto — nunca se detiene.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass

import pandas as pd

from ._cycle_loops import CicloNoConvergeError
from .cycle_solver import resolver_ciclo
from .properties.adapter import PropertyRangeError
from .restricciones import Clasificacion, evaluar_ciclo

__all__ = ["Fijo", "Barrido", "generar_valores", "generar_combinaciones",
          "ejecutar_barrido", "resolver_combinacion", "tabla_barrido"]

VARIABLES_BARRIBLES = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b",
                       "m_b", "eta_t", "eta_p", "eps_hrvg", "eps_reg",
                       "eps_cond")


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


def resolver_combinacion(backend, combo: dict[str, float]) -> dict:
    """Resuelve un único punto del barrido (una fila de resultado).

    Reutilizado por `ejecutar_barrido` y por la UI cuando resuelve la rejilla
    en lotes (para poder cancelarla entre puntos). ``combo`` es una
    combinación de las 11 variables de `VARIABLES_BARRIBLES`.
    """
    fila = dict(combo)
    try:
        resultado = resolver_ciclo(backend, **combo)
    except (CicloNoConvergeError, PropertyRangeError) as exc:
        fila.update(convergio=False,
                    clasificacion=Clasificacion.NO_CONVERGIO.value,
                    eta=None, Wnet=None, mensaje=str(exc))
        return fila
    validacion = evaluar_ciclo(
        backend, resultado, P_alta=combo["P_alta"], P_baja=combo["P_baja"],
        T_fuente=combo["T_fuente"], T_sumidero=combo["T_sumidero"],
        x_b=combo["x_b"], m_b=combo["m_b"], eps_hrvg=combo["eps_hrvg"],
        eps_reg=combo["eps_reg"], eps_cond=combo["eps_cond"])
    fila.update(convergio=True, clasificacion=validacion.clasificacion.value,
                eta=resultado["eta"], Wnet=resultado["Wnet"],
                mensaje=validacion.mensaje_reporte())
    return fila


def ejecutar_barrido(backend, variables: dict[str, Fijo | Barrido]
                     ) -> list[dict]:
    """Resuelve el ciclo para cada combinación y clasifica cada punto.

    ``variables`` debe declarar las 11 variables de `resolver_ciclo`
    (``VARIABLES_BARRIBLES``), cada una como `Fijo` o `Barrido`. Cada fila del
    resultado registra los valores de entrada usados, si convergió, la
    clasificación (`NO_CONVERGIO`/`INVIABLE`/`DEGENERADO`/`CORREGIBLE`/
    `VALIDO_ADVERTENCIA`/`KALINA`) y, si convergió, `eta`/`Wnet` y el mensaje
    de validación jerárquico (principal + secundarias).
    """
    faltantes = set(VARIABLES_BARRIBLES) - set(variables)
    if faltantes:
        raise ValueError(
            f"faltan variables en el barrido: {sorted(faltantes)}; se "
            f"requieren las 11 de VARIABLES_BARRIBLES")

    return [resolver_combinacion(backend, combo)
            for combo in generar_combinaciones(variables)]


def tabla_barrido(filas: list[dict]) -> pd.DataFrame:
    """DataFrame del barrido: una fila por punto, en el orden ya resuelto."""
    columnas = list(VARIABLES_BARRIBLES) + [
        "convergio", "clasificacion", "eta", "Wnet", "mensaje"]
    return pd.DataFrame(filas)[columnas]
