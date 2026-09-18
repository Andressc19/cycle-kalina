"""Adapter de propiedades de la mezcla NH3-H2O sobre pyfluids (mecanismo CoolProp).

NOTA (2026-09-17): ESTE ADAPTER **NO** ES FUNCIONAL PARA NH3-H2O EN ESTE ENTORNO.
El **camino real** para la mezcla es `AmmoniaWaterAdapter` (ver
`src/properties/ammonia_water_adapter.py`), que envuelve el motor portado
IAPWS G4-01 (iapws 1.5.5). pyfluids/CoolProp no incluye el par binario
amoníaco-agua sin el backend REFPROP (licencia NIST) y por eso este adapter se
conserva SOLO como referencia para un futuro con licencia — no debe usarlo el
solver del ciclo. Su código funcional no se ha modificado.

Expone la interfaz `PropertyBackend` en sus unidades canónicas (P en kPa, T en K,
h en kJ/kg, s en kJ/kg·K, x = fracción másica de NH3 en (0, 1)) y traduce
internamente a pyfluids/CoolProp usando el propio `UnitConverter` de pyfluids,
por lo que su comportamiento no depende de la configuración de unidades activa.

NOTA DE CAPACIDAD DEL BACKEND (verificada con pyfluids 4.0.0 / CoolProp 8.0.0):
CoolProp no incluye el par binario amoníaco-agua (CAS 7664-41-7 + 7732-18-5) en
sus backends HEOS/BICUBIC; solo REFPROP (NIST, con licencia) lo cubre. Si el
backend no puede crear la mezcla, se lanza `PropertyRangeError` con mensaje claro
en lugar de propagar el error crudo.
"""

from __future__ import annotations

from typing import Optional

from .adapter import PropertyBackend, PropertyRangeError

try:  # import con guarda: el módulo debe poder importarse sin pyfluids instalado
    from pyfluids import FluidsList, Input, Mixture
    from pyfluids.config import UnitConverter
except ImportError as _import_error:  # pragma: no cover
    _IMPORT_ERROR = _import_error
    FluidsList = Input = Mixture = UnitConverter = None
else:
    _IMPORT_ERROR = None

__all__ = ["PyfluidsAdapter"]

_PA_PER_KPA = 1000.0
_J_PER_KJ = 1000.0


def _build_mixture(x: float) -> "Mixture":
    """Crea la mezcla NH3-H2O con fracción másica de NH3 ``x`` (en (0, 1)).

    Separada de la clase para poder mockearla fácilmente en los tests. Lanza
    ValueError si ``x`` es inválida y PropertyRangeError si el backend no
    soporta la mezcla.
    """
    if not 0.0 < x < 1.0:
        raise ValueError(
            f"x (fracción másica de NH3) debe estar en (0, 1); se recibió {x!r}."
        )
    if Mixture is None:  # pragma: no cover - solo cuando pyfluids no está instalado
        raise PropertyRangeError(
            "pyfluids no está instalado; no se puede crear la mezcla NH3-H2O. "
            f"Detalle del import: {_IMPORT_ERROR}"
        )
    converter = UnitConverter()
    frac_nh3 = converter.convert_decimal_fraction_from_si(x)
    frac_h2o = converter.convert_decimal_fraction_from_si(1.0 - x)
    try:
        return Mixture([FluidsList.Ammonia, FluidsList.Water], [frac_nh3, frac_h2o])
    except ValueError as exc:
        raise PropertyRangeError(
            "El backend pyfluids/CoolProp instalado no soporta la mezcla NH3-H2O "
            f"(par binario amoníaco-agua). Se requiere REFPROP/NIST u otro backend "
            f"que cubra la mezcla. Detalle del backend: {exc}"
        ) from exc


class PyfluidsAdapter(PropertyBackend):
    """Propiedades de la mezcla NH3-H2O vía pyfluids/CoolProp.

    ``x`` es la composición por defecto de la instancia: si una llamada no pasa
    ``x``, se usa ese valor; si pasa un ``x`` distinto, se crea la mezcla para ese
    valor sobre la marcha (cacheada solo para la composición por defecto).
    """

    def __init__(self, x: float = 0.5):
        self._x = float(x)
        self._mixture = _build_mixture(self._x)  # falla temprano si no hay soporte
        self._converter = UnitConverter()

    # -- helpers internos ----------------------------------------------------

    @staticmethod
    def _require_positive(value: float, name: str) -> None:
        if value <= 0:
            raise ValueError(f"{name} debe ser positivo; se recibió {value!r}.")

    def _mixture_for(self, x: Optional[float]) -> "Mixture":
        if x is None or x == self._x:
            return self._mixture
        return _build_mixture(x)

    def _state(self, P: float, *, x: Optional[float], what: str,
               T: Optional[float] = None, s: Optional[float] = None,
               quality: Optional[float] = None, h: Optional[float] = None):
        """Evalúa un estado de la mezcla y envuelve los errores del backend."""
        mixture = self._mixture_for(x)
        inputs = [Input.pressure(P * _PA_PER_KPA)]
        if T is not None:
            self._require_positive(T, "T")
            inputs.append(Input.temperature(self._converter.convert_temperature_from_si(T)))
        elif s is not None:
            self._require_positive(s, "s")
            inputs.append(Input.entropy(s * _J_PER_KJ))
        elif quality is not None:
            inputs.append(Input.quality(self._converter.convert_decimal_fraction_from_si(quality)))
        elif h is not None:
            self._require_positive(h, "h")
            inputs.append(Input.enthalpy(h * _J_PER_KJ))
        else:
            raise ValueError(
                f"{what}: estado mixto incompleto — se requiere (P, T), (P, s), "
                "(P, quality) o (P, h), con P en kPa y T en K."
            )
        try:
            return mixture.with_state(*inputs)
        except (ValueError, TypeError, KeyError, OverflowError) as exc:
            raise PropertyRangeError(
                f"{what}: el backend pyfluids/CoolProp no cubre el estado pedido "
                f"(P={P} kPa). Detalle del backend: {exc}"
            ) from exc

    def _sat_temperature(self, P: float, x: Optional[float], kind: str) -> float:
        self._require_positive(P, "P")
        mixture = self._mixture_for(x)
        method = (
            mixture.dew_point_at_pressure if kind == "dew"
            else mixture.bubble_point_at_pressure
        )
        try:
            return self._converter.convert_temperature_to_si(method(P * _PA_PER_KPA).temperature)
        except (ValueError, TypeError, KeyError, OverflowError) as exc:
            raise PropertyRangeError(
                f"punto de {kind}: el backend pyfluids/CoolProp no cubre (P={P} kPa). "
                f"Detalle del backend: {exc}"
            ) from exc

    # -- interfaz PropertyBackend ---------------------------------------------

    def h(self, P: float, T: Optional[float] = None, x: Optional[float] = None,
          s: Optional[float] = None, quality: Optional[float] = None) -> float:
        self._require_positive(P, "P")
        return self._state(P, x=x, what="h", T=T, s=s, quality=quality).enthalpy / _J_PER_KJ

    def s(self, P: float, T: Optional[float] = None, x: Optional[float] = None) -> float:
        self._require_positive(P, "P")
        return self._state(P, x=x, what="s", T=T).entropy / _J_PER_KJ

    def T_from_Ph(self, P: float, h: float, x: Optional[float] = None) -> float:
        self._require_positive(P, "P")
        state = self._state(P, x=x, what="T_from_Ph", h=h)
        return self._converter.convert_temperature_to_si(state.temperature)

    def T_from_Ps(self, P: float, s: float, x: Optional[float] = None) -> float:
        self._require_positive(P, "P")
        state = self._state(P, x=x, what="T_from_Ps", s=s)
        return self._converter.convert_temperature_to_si(state.temperature)

    def bubble_point(self, P: float, x: float) -> float:
        return self._sat_temperature(P, x, kind="bubble")

    def dew_point(self, P: float, x: float) -> float:
        return self._sat_temperature(P, x, kind="dew")

    def equilibrio_liquido_vapor(self, P: float, T: float) -> tuple[float, float]:
        raise PropertyRangeError(
            "equilibrio_liquido_vapor: el backend pyfluids/CoolProp instalado "
            "no soporta la mezcla NH3-H2O (par binario amoníaco-agua; requiere "
            "REFPROP/NIST) ni expone composiciones de fase desde un flash "
            "(P, T). No es el camino real de la mezcla en este entorno — use "
            "AmmoniaWaterAdapter (ver CONTEXT.md)."
        )