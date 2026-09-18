"""Componentes del ciclo Kalina KSC-11.

Implementados como funciones puras `resolver(...)`: consumen `EstadoTermo` de
entrada, un `PropertyBackend` (solo la interfaz — nunca un backend concreto) y
sus parámetros propios, y devuelven `EstadoTermo(s)` de salida más las
cantidades de energía relevantes en kW. Fórmulas y mapa de estados en
`CONTEXT.md`.
"""
