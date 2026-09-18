"""Análisis exergético del ciclo Kalina KSC-11 (exergía FÍSICA, sin química).

Tarea 2026-09-17-exergia. Implementa:
- `exergia_fisica`: exergía física específica [kJ/kg] de una corriente,
  `ex = (h − h0) − T0·(s − s0)`, con `h0`/`s0` evaluados a (`P0`, `T0`) con la
  composición PROPIA de la corriente (CONTEXT.md "Estado muerto") — se excluye
  la exergía química/de mezcla por alcance del proyecto.
- `calcular_exergia`: exergía física de los 10 estados, `Sgen`/`Ed` de los 8
  componentes (las 8 fórmulas exactas de CONTEXT.md "Balance de
  entropía/exergía por componente"), `Ed_total` y el cierre del balance global
  `Ex_Qi − Wnet − Ex_Qout ≈ Ed_total`.

Estado muerto: `T0 = 300.032917 K` (confirmado en CONTEXT.md) y
`P0 = 101.325 kPa` (supuesto explícito documentado en CONTEXT.md, configurable).
Los estados NO se mutan: `calcular_exergia` devuelve copias
(`dataclasses.replace`) con `exergia_fisica` rellenada. Solo consume la
interfaz `PropertyBackend` (patrón adapter, CONTEXT.md): nunca importa un
backend concreto.
"""

from __future__ import annotations

from dataclasses import replace

from .properties.adapter import PropertyBackend
from .state import EstadoTermo

__all__ = ["exergia_fisica", "calcular_exergia"]

T0_POR_DEFECTO = 300.032917      # K — CONTEXT.md: media del perfil horario ambiente
P0_POR_DEFECTO = 101.325         # kPa — CONTEXT.md: supuesto explícito (atm. estándar)


def exergia_fisica(
    estado: EstadoTermo,
    backend: PropertyBackend,
    *,
    T0: float = T0_POR_DEFECTO,
    P0: float = P0_POR_DEFECTO,
) -> float:
    """Exergía física específica [kJ/kg] de ``estado``.

    ``ex = (h − h0) − T0·(s − s0)``, con ``h0 = h(P0, T0, x_estado)`` y
    ``s0 = s(P0, T0, x_estado)``. El estado de referencia usa la composición
    propia de la corriente (``x0 = x_corriente``), no una composición ambiental
    universal — precisamente lo que distingue la exergía física de la química
    (CONTEXT.md "Estado muerto"). La corriente se enfría/despresuriza hasta
    (T0, P0) manteniendo su propia composición.
    """
    h0 = backend.h(P0, T=T0, x=estado.x)
    s0 = backend.s(P0, T=T0, x=estado.x)
    return (estado.h - h0) - T0 * (estado.s - s0)


def calcular_exergia(
    resultado_ciclo: dict,
    backend: PropertyBackend,
    *,
    T_fuente: float,
    T_sumidero: float,
    T0: float = T0_POR_DEFECTO,
    P0: float = P0_POR_DEFECTO,
) -> dict:
    """Balance exergético completo de un ciclo resuelto por ``resolver_ciclo``.

    ``resultado_ciclo`` es el dict de ``resolver_ciclo`` (``estados`` e1..e10
    con ``.m`` ya fijados, y ``Qi``, ``Qout``, ``Wnet``). ``T_fuente`` y
    ``T_sumidero`` son parámetros de ENTRADA de la llamada al solver (no viven
    en su salida) y por eso se pasan aquí como argumentos propios.

    Devuelve un dict con:
    - ``estados``: copias de los 10 estados con ``exergia_fisica`` [kJ/kg];
    - ``sgen`` [kW/K] y ``ed`` [kW] por componente (los 8) y ``ed_total``;
    - ``ex_qi`` / ``ex_qout`` [kW]: exergía de los flujos de calor;
    - ``residual`` [kW] y ``residual_rel`` [-]: cierre del balance global
      ``Ex_Qi − Wnet − Ex_Qout − Ed_total`` y su valor relativo a ``Ex_Qi``.
    """
    E = resultado_ciclo["estados"]
    Qi = resultado_ciclo["Qi"]
    Qout = resultado_ciclo["Qout"]
    Wnet = resultado_ciclo["Wnet"]

    estados = {
        k: replace(e, exergia_fisica=exergia_fisica(e, backend, T0=T0, P0=P0))
        for k, e in E.items()
    }

    # Las 8 fórmulas de CONTEXT.md "Balance de entropía/exergía por componente"
    # (los caudales son los ``.m`` que ya fijan los estados del solver).
    sgen = dict(
        hrvg=E["e1"].m * (E["e2"].s - E["e1"].s) - Qi / T_fuente,
        separador=(E["e3"].m * E["e3"].s + E["e5"].m * E["e5"].s
                   - E["e2"].m * E["e2"].s),
        turbina=E["e3"].m * (E["e4"].s - E["e3"].s),
        regenerador=(E["e5"].m * (E["e6"].s - E["e5"].s)
                     + E["e10"].m * (E["e1"].s - E["e10"].s)),
        valvula=E["e6"].m * (E["e7"].s - E["e6"].s),
        absorbedor=(E["e8"].m * E["e8"].s
                    - E["e4"].m * E["e4"].s - E["e7"].m * E["e7"].s),
        condensador=E["e8"].m * (E["e9"].s - E["e8"].s) + Qout / T_sumidero,
        bomba=E["e9"].m * (E["e10"].s - E["e9"].s),
    )
    ed = {k: T0 * v for k, v in sgen.items()}
    ed_total = sum(ed.values())

    ex_qi = Qi * (1.0 - T0 / T_fuente)
    ex_qout = Qout * (1.0 - T0 / T_sumidero)

    residual = ex_qi - Wnet - ex_qout - ed_total      # kW
    residual_rel = abs(residual) / ex_qi if ex_qi else float("nan")

    return dict(estados=estados, sgen=sgen, ed=ed, ed_total=ed_total,
                ex_qi=ex_qi, ex_qout=ex_qout, residual=residual,
                residual_rel=residual_rel)