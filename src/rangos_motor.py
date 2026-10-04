"""Rango confiable de los motores NH3-H2O y su chequeo (modo A: extrapolar y marcar).

Los dos motores del proyecto (`real` = AmmoniaWaterAdapter, `teqp` = TeqpAdapter /
TeqpVerificado) implementan el MISMO modelo, Tillner-Roth & Friend (1998) = IAPWS
G4-01, así que los límites son los declarados en G4-01 §6 (copia en
`reference/IAPWS_G4-01_nh3h2o.pdf`) y valen para ambos. No se incluyen límites del
envoltorio numérico de cada motor: esos fallos se tratan aparte (p. ej. A+B).

NO vigilado: el techo real del modelo es el lugar crítico de la mezcla; la propia
guía avisa que calcularlo da problemas de convergencia y que su ubicación es
incierta, así que no se aproxima.

La marca va APARTE de la clasificación del ciclo: el punto se calcula igual y solo
se señala que el número sale de una extrapolación.
"""

from __future__ import annotations

import logging
import math
import warnings
from dataclasses import dataclass

from .properties._nh3h2o_engine import w2m
from .properties.adapter import PropertyRangeError

__all__ = ["MOTORES", "MODOS", "LIMITES", "Violacion", "RangoMotorWarning",
           "T_triple", "validar_config", "evaluar_rango", "evaluar_rango_entradas"]

log = logging.getLogger(__name__)

MOTORES = ("real", "teqp")
MODOS = ("extrapolar_marcar",)

P_MAX_MODELO = 40000.0   # kPa, G4-01 §6: válido hasta 40 MPa
T_MAX_LIQUIDO = 420.0    # K, G4-01 §6: datos de líquido solo por debajo de 420 K
P_MAX_VAPOR = 10000.0    # kPa, G4-01 §6: datos de vapor solo por debajo de 10 MPa

# Tabla 5 de G4-01 (línea de puntos triples, ec. 9).
_C = dict(c11=-0.3439823, c12=-1.3274271, c13=-274.973, c21=-4.987368,
          c31=-4.886151, c32=10.37298, c41=-0.323998, c42=-15.87560)

LIMITES = (
    dict(parametro="P", limite=f"<= {P_MAX_MODELO:g} kPa", tipo="modelo",
         motores=MOTORES, fuente="IAPWS G4-01 §6"),
    dict(parametro="T", limite=">= T_tr(x), línea sólido-líquido-vapor",
         tipo="modelo", motores=MOTORES, fuente="IAPWS G4-01 §6, ec. (9), Tabla 5"),
    dict(parametro="T", limite=f"<= {T_MAX_LIQUIDO:g} K en líquido",
         tipo="respaldo_experimental", motores=MOTORES, fuente="IAPWS G4-01 §6"),
    dict(parametro="P", limite=f"<= {P_MAX_VAPOR:g} kPa en vapor",
         tipo="respaldo_experimental", motores=MOTORES, fuente="IAPWS G4-01 §6"),
)


class RangoMotorWarning(UserWarning):
    """Un estado del ciclo cae fuera del rango confiable del motor."""


@dataclass(frozen=True)
class Violacion:
    parametro: str      # "T", "P" o "fase"
    estado: str         # etiqueta "1".."10" o el nombre de la entrada
    valor: float
    limite: float
    motor: str
    tipo: str           # "modelo" | "respaldo_experimental"
    columna: str        # "T4", "P2", "P_alta", ...
    unidad: str
    sentido: str        # ">" o "<": cómo se cruzó el límite

    def texto(self) -> str:
        if self.parametro == "fase":
            return (f"fase{self.estado}: no se pudo determinar la fase "
                    f"({self.tipo}) [motor: {self.motor}]")
        return (f"{self.columna}={self.valor:.6g} {self.unidad} {self.sentido} "
                f"{self.limite:.6g} {self.unidad} ({self.tipo}) [motor: {self.motor}]")


def T_triple(w: float) -> float:
    """T [K] de la línea sólido-líquido-vapor, ec. (9) de G4-01; w = fracción másica."""
    x = w2m(w)
    c = _C
    if x <= 0.33367:
        return 273.16 * (1 + c["c11"] * x + c["c12"] * x**2 + c["c13"] * x**7)
    if x <= 0.58396:
        return 193.549 * (1 + c["c21"] * (x - 0.5) ** 2)
    if x <= 0.81473:
        d = x - 2 / 3
        return 194.380 * (1 + c["c31"] * d**2 + c["c32"] * d**3)
    return 195.495 * (1 + c["c41"] * (1 - x) + c["c42"] * (1 - x) ** 4)


def validar_config(motor: str, modo: str) -> None:
    if modo not in MODOS:
        raise NotImplementedError(f"modo {modo!r} reservado, no implementado; "
                                  f"modos disponibles: {MODOS}")
    if motor not in MOTORES:
        raise ValueError(f"motor debe ser uno de {MOTORES}; se recibió {motor!r}")


def _avisar(violaciones: list[Violacion]) -> list[Violacion]:
    for v in violaciones:
        msg = "fuera de rango confiable: " + v.texto()
        log.warning(msg)
        warnings.warn(msg, RangoMotorWarning, stacklevel=3)
    return violaciones


def _chequear(et, T, P, x, fase, motor):
    """Violaciones de UN estado (T [K], P [kPa], x másica, fase o None)."""
    out = []
    V = lambda par, val, lim, tipo, col, u, s: out.append(
        Violacion(par, et, val, lim, motor, tipo, col, u, s))
    cT = f"T{et}" if et.isdigit() else et
    cP = f"P{et}" if et.isdigit() else et
    if P is not None and P > P_MAX_MODELO:
        V("P", P, P_MAX_MODELO, "modelo", cP, "kPa", ">")
    if T is not None and x is not None and 0 < x < 1:
        t_tr = T_triple(x)
        if T < t_tr:
            V("T", T, t_tr, "modelo", cT, "K", "<")
    if fase in ("liquido", "bifasico") and T is not None and T > T_MAX_LIQUIDO:
        V("T", T, T_MAX_LIQUIDO, "respaldo_experimental", cT, "K", ">")
    if fase in ("vapor", "bifasico") and P is not None and P > P_MAX_VAPOR:
        V("P", P, P_MAX_VAPOR, "respaldo_experimental", cP, "kPa", ">")
    return out


def evaluar_rango(motor: str, resultado: dict, backend=None,
                  modo: str = "extrapolar_marcar") -> list[Violacion]:
    """Violaciones de rango de los estados `e1..e10` de un ciclo ya resuelto.

    La fase sale de `estado.fase`; si es None y hay `backend`, de
    `backend.fase_de(P, T, x)`. Si la fase no se puede determinar, se registra una
    violación `parametro="fase"` en vez de adivinarla.
    """
    validar_config(motor, modo)
    out = []
    estados = resultado["estados"]
    for clave in sorted(estados, key=lambda k: int(k[1:])):
        e = estados[clave]
        et = clave[1:]
        fase = e.fase
        if fase is None and backend is not None:
            try:
                fase, _ = backend.fase_de(e.P, e.T, e.x)
            except PropertyRangeError as exc:
                out.append(Violacion("fase", et, math.nan, math.nan, motor,
                                     f"no determinable: {exc}", f"T{et}", "", "?"))
        out.extend(_chequear(et, e.T, e.P, e.x, fase, motor))
    return _avisar(out)


def evaluar_rango_entradas(motor: str, combo: dict,
                           modo: str = "extrapolar_marcar") -> list[Violacion]:
    """Violaciones de las entradas de un punto sin estados (p. ej. NO_CONVERGIO).

    Sin estados no hay fase, así que solo aplican los límites del modelo: P_alta y
    P_baja contra 40 MPa, y T_sumidero contra la línea de puntos triples de x_b.
    """
    validar_config(motor, modo)
    out = []
    x = combo.get("x_b")
    for nombre in ("P_alta", "P_baja"):
        out.extend(_chequear(nombre, None, combo.get(nombre), x, None, motor))
    out.extend(_chequear("T_sumidero", combo.get("T_sumidero"), None, x, None, motor))
    return _avisar(out)
