"""Capa de propiedades termodinámicas (patrón adapter).

Este paquete exporta SOLO la interfaz abstracta y la excepción controlada, nunca
los backends concretos (pyfluids / iapws) — así `import src.properties` funciona
sin que estén instalados. Los adapters concretos se importan explícitamente:

    from src.properties.pyfluids_adapter import PyfluidsAdapter
    from src.properties.iapws_adapter import IAPWSAdapter
"""

from .adapter import PropertyBackend, PropertyRangeError

__all__ = ["PropertyBackend", "PropertyRangeError"]