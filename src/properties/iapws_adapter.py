"""Adapter de propiedades de AGUA PURA sobre iapws 1.5.5 (IAPWS-IF97).

Solo agua pura. IAPWS nunca se usa para la mezcla NH3-H2O (ver CONTEXT.md): si se
pide una composición ``x`` distinta de None (o el parámetro ``quality``), se lanza
NotImplementedError con mensaje claro en vez de interpretar el valor.

Unidades de la interfaz: P en kPa, T en K, h en kJ/kg, s en kJ/kg·K. Internamente
iapws usa MPa (P/1000) y las mismas unidades para h y s, así que solo hay que
convertir la presión.
"""

from __future__ import annotations

from typing import Optional

from .adapter import PropertyBackend, PropertyRangeError

try:  # import con guarda: el módulo debe poder importarse sin iapws instalado
    from iapws import IAPWS97
except ImportError as _import_error:  # pragma: no cover
    _IMPORT_ERROR = _import_error
    IAPWS97 = None
else:
    _IMPORT_ERROR = None

__all__ = ["IAPWSAdapter"]

_MPA_PER_KPA = 0.001


class IAPWSAdapter(PropertyBackend):
    """Propiedades de agua pura vía iapws 1.5.5 (IAPWS-IF97, regiones 1–5)."""

    @staticmethod
    def _require_backend() -> None:  # pragma: no cover
        if IAPWS97 is None:
            raise PropertyRangeError(
                "iapws no está instalado; no se puede calcular agua pura. "
                f"Detalle del import: {_IMPORT_ERROR}"
            )

    @staticmethod
    def _raise_if_mixture_requested(x: Optional[float]) -> None:
        if x is not None:
            raise NotImplementedError(
                "IAPWSAdapter solo modela agua pura (IAPWS-IF97); no acepta "
                f"composición x de mezcla NH3-H2O (se recibió x={x!r}). Use "
                "PyfluidsAdapter para la mezcla."
            )

    @staticmethod
    def _raise_if_quality_given(quality: Optional[float]) -> None:
        if quality is not None:
            raise NotImplementedError(
                f"IAPWSAdapter modela agua pura con (P, T) o (P, s); no interpreta "
                f"el parámetro quality (se recibió quality={quality!r})."
            )

    def _state(self, *, P: float, T: Optional[float] = None,
               s: Optional[float] = None, h: Optional[float] = None):
        """Evalúa un estado de agua pura y envuelve los errores del backend."""
        self._require_backend()
        kwargs = {"P": P * _MPA_PER_KPA}
        if T is not None:
            kwargs["T"] = T
        elif s is not None:
            kwargs["s"] = s
        elif h is not None:
            kwargs["h"] = h
        else:
            raise ValueError(
                "Estado de agua pura incompleto — se requiere (P, T), (P, s) o "
                "(P, h), con P en kPa, T en K, h en kJ/kg y s en kJ/kg·K."
            )
        try:
            return IAPWS97(**kwargs)
        except (ValueError, OverflowError, NotImplementedError) as exc:
            raise PropertyRangeError(
                f"agua pura: iapws no cubre el estado pedido {kwargs} "
                f"(P en MPa, T en K). Detalle del backend: {exc}"
            ) from exc

    # -- interfaz PropertyBackend ---------------------------------------------

    def h(self, P: float, T: Optional[float] = None, x: Optional[float] = None,
          s: Optional[float] = None, quality: Optional[float] = None) -> float:
        self._raise_if_mixture_requested(x)
        self._raise_if_quality_given(quality)
        return self._state(P=P, T=T, s=s).h

    def s(self, P: float, T: Optional[float] = None, x: Optional[float] = None) -> float:
        self._raise_if_mixture_requested(x)
        return self._state(P=P, T=T).s

    def T_from_Ph(self, P: float, h: float, x: Optional[float] = None) -> float:
        self._raise_if_mixture_requested(x)
        return self._state(P=P, h=h).T

    def T_from_Ps(self, P: float, s: float, x: Optional[float] = None) -> float:
        self._raise_if_mixture_requested(x)
        return self._state(P=P, s=s).T

    def bubble_point(self, P: float, x: float) -> float:
        raise NotImplementedError(
            "IAPWSAdapter solo modela agua pura; no existe punto de burbuja de "
            "mezcla. Use PyfluidsAdapter para el equilibrio L-V de NH3-H2O."
        )

    def dew_point(self, P: float, x: float) -> float:
        raise NotImplementedError(
            "IAPWSAdapter solo modela agua pura; no existe punto de rocío de "
            "mezcla. Use PyfluidsAdapter para el equilibrio L-V de NH3-H2O."
        )

    def equilibrio_liquido_vapor(self, P: float, T: float) -> tuple[float, float]:
        raise NotImplementedError(
            "IAPWSAdapter solo modela agua pura (IAPWS-IF97); no existe "
            "equilibrio líquido-vapor de mezcla NH3-H2O a (P, T). Use "
            "AmmoniaWaterAdapter para el flash binario."
        )