"""Interfaz abstracta `PropertyBackend` y excepción controlada `PropertyRangeError`.

Este módulo es el ÚNICO contrato entre la capa de propiedades y el resto del
proyecto (componentes, solver, exergía, UI). Por diseño NO importa ningún
backend concreto (ni pyfluids/CoolProp ni iapws): los adapters concretos viven
en `pyfluids_adapter.py` e `iapws_adapter.py`, y el resto del código nunca debe
importarlos directamente (patrón adapter, ver `Kalina_ksc_11_tercero.md` §3).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

__all__ = ["PropertyBackend", "PropertyRangeError"]


class PropertyRangeError(Exception):
    """El backend de propiedades no puede cubrir el estado solicitado.

    Se lanza exclusivamente desde los adapters cuando la librería subyacente
    falla o no cubre el rango pedido (presión/temperatura/composición fuera de
    validez, mezcla no soportada por el backend instalado, etc.). La excepción
    cruda del backend NUNCA se propaga sin envolver hacia el solver/UI.
    """


class PropertyBackend(ABC):
    """Contrato de propiedades termodinámicas del ciclo Kalina KSC-11.

    Unidades canónicas de la interfaz (independientes del backend):
      - Presión ``P``: kPa.
      - Temperatura: K.
      - Entalpía específica ``h``: kJ/kg.
      - Entropía específica ``s``: kJ/kg·K.
      - Composición ``x``: fracción másica de NH3 en la mezcla NH3-H2O [-],
        definida en (0, 1).
    """

    @abstractmethod
    def h(
        self,
        P: float,
        T: Optional[float] = None,
        x: Optional[float] = None,
        s: Optional[float] = None,
        quality: Optional[float] = None,
    ) -> float:
        """Entalpía específica [kJ/kg].

        Combos mínimos soportados: (P, T, x) para la mezcla NH3-H2O y (P, T)
        para agua pura; los adapters pueden además aceptar (P, s) o (P, quality).
        Si el estado está incompleto o es inválido, lanzan ValueError; si el
        backend no cubre el rango, PropertyRangeError.
        """

    @abstractmethod
    def s(self, P: float, T: Optional[float] = None, x: Optional[float] = None) -> float:
        """Entropía específica [kJ/kg·K]. Combo mínimo: (P, T[, x])."""

    @abstractmethod
    def T_from_Ph(self, P: float, h: float, x: Optional[float] = None) -> float:
        """Temperatura [K] a partir de (P [kPa], h [kJ/kg][, x])."""

    @abstractmethod
    def T_from_Ps(self, P: float, s: float, x: Optional[float] = None) -> float:
        """Temperatura [K] a partir de (P [kPa], s [kJ/kg·K][, x])."""

    @abstractmethod
    def bubble_point(self, P: float, x: float) -> float:
        """Temperatura de burbuja [K] de la mezcla a (P, x) — solo mezcla NH3-H2O.

        La usa la lógica del separador/flash (tareas futuras). Los adapters que
        no modelan mezclas deben lanzar NotImplementedError.
        """

    @abstractmethod
    def dew_point(self, P: float, x: float) -> float:
        """Temperatura de rocío [K] de la mezcla a (P, x) — solo mezcla NH3-H2O.

        La usa la lógica del separador/flash (tareas futuras). Los adapters que
        no modelan mezclas deben lanzar NotImplementedError.
        """

    @abstractmethod
    def equilibrio_liquido_vapor(self, P: float, T: float) -> tuple[float, float]:
        """Composiciones másicas (x_liquido, x_vapor) en equilibrio a (P [kPa], T [K]).

        Es el flash directo (P, T) → composiciones de las fases saturadas,
        independiente de la composición global: la usa el separador ideal
        (regla de la palanca) sin tener que invertir bubble/dew point. Solo
        mezcla NH3-H2O — los adapters que no modelan mezclas lanzan
        NotImplementedError, y los backends que no cubren el rango lanzan
        PropertyRangeError (T fuera de la campana bifásica a esa P).
        """

    def fase_de(self, P: float, T: float, x: float) -> tuple[str, float]:
        """Clasifica un estado (P, T, x) en 'liquido'/'bifasico'/'vapor' y su título q.

        Método concreto (no abstracto): se apoya solo en ``bubble_point``,
        ``dew_point`` y ``equilibrio_liquido_vapor``, así que funciona para
        cualquier backend que implemente esos tres sin necesitar overrides.
        q=0.0 en líquido (saturado o comprimido), q=1.0 en vapor (saturado o
        sobrecalentado), y el título másico por regla de la palanca en la
        región bifásica. Usada por `restricciones.py` para clasificar salidas
        de componentes (condensador, HRVG, turbina) sin que el solver del
        ciclo necesite conocer el título de cada estado.
        """
        T_burbuja = self.bubble_point(P, x)
        T_rocio = self.dew_point(P, x)
        if T <= T_burbuja:
            return "liquido", 0.0
        if T >= T_rocio:
            return "vapor", 1.0
        x_liquido, x_vapor = self.equilibrio_liquido_vapor(P, T)
        q = (x - x_liquido) / (x_vapor - x_liquido)
        return "bifasico", q