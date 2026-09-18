"""Criterios de segunda ley S1-S8 (todos críticos: INVIABLE si fallan).

S9 (no-cruce interno con C_g finito) no aplica: este repo modela fuente y
sumidero como reservorios de capacidad térmica infinita (sin `dimensionar()`
ni C_g finito), así que S5 (T2 <= T_fuente) ya es suficiente — ver
kcs11-formulacion-matematica.md, nota de alcance de S5/S9.
"""

from __future__ import annotations

from .modelos import Clasificacion, Falla, Severidad

__all__ = ["verificar_segunda_ley"]


def _crit(codigo, mensaje, variable, medido, esperado, causa, sugerencia) -> Falla:
    return Falla(codigo=codigo, severidad=Severidad.CRITICO,
                clasificacion=Clasificacion.INVIABLE, mensaje=mensaje,
                variable=variable, valor_medido=medido, valor_esperado=esperado,
                causa_probable=causa, sugerencia=sugerencia)


def verificar_segunda_ley(resultado: dict, *, T_fuente: float,
                          T_sumidero: float, eps_hrvg: float, eps_reg: float,
                          eps_cond: float) -> list[Falla]:
    fallas: list[Falla] = []
    e = resultado["estados"]

    if e["e4"].s < e["e3"].s:  # S1
        fallas.append(_crit(
            "S1", "la entropía cae en la turbina (imposible, 2ª ley)", "s4-s3",
            e["e4"].s - e["e3"].s, ">= 0",
            "eta_t fuera de un rango físico o error en h4s",
            "revisar eta_t y el cálculo isentrópico de la turbina"))

    if e["e10"].s < e["e9"].s:  # S2
        fallas.append(_crit(
            "S2", "la entropía cae en la bomba (imposible, 2ª ley)", "s10-s9",
            e["e10"].s - e["e9"].s, ">= 0",
            "eta_p fuera de un rango físico o error en h10s",
            "revisar eta_p y el cálculo isentrópico de la bomba"))

    if e["e7"].s < e["e6"].s:  # S3
        fallas.append(_crit(
            "S3", "la entropía cae en la válvula (imposible, 2ª ley)", "s7-s6",
            e["e7"].s - e["e6"].s, ">= 0",
            "error numérico en la válvula isoentálpica",
            "revisar `valvula.py` y las propiedades a P_baja"))

    if e["e5"].T <= e["e1"].T or e["e6"].T <= e["e10"].T:  # S4
        fallas.append(_crit(
            "S4", "cruce de temperaturas en el regenerador (imposible)",
            "T5,T6 vs T1,T10",
            min(e["e5"].T - e["e1"].T, e["e6"].T - e["e10"].T), "> 0 en ambos extremos",
            "efectividad del regenerador (eps_reg) demasiado alta para las "
            "temperaturas del ciclo",
            "reducir eps_reg o revisar T1/T10 de ese punto"))

    if e["e2"].T > T_fuente:  # S5 (bajo H10, fuente de capacidad infinita)
        fallas.append(_crit(
            "S5", "la salida del HRVG supera la temperatura de la fuente",
            "T2", e["e2"].T, f"<= {T_fuente:.3f} K",
            "eps_hrvg demasiado alta o T_fuente insuficiente para ese punto",
            "reducir eps_hrvg o aumentar T_fuente"))

    if e["e9"].T < T_sumidero:  # S6 (T_sumidero real de la corrida)
        fallas.append(_crit(
            "S6", "la salida del condensador queda bajo la temperatura del sumidero",
            "T9", e["e9"].T, f">= {T_sumidero:.3f} K",
            "eps_cond demasiado alta para T_sumidero en ese punto",
            "reducir eps_cond o revisar T_sumidero"))

    for nombre, valor in (("eps_hrvg", eps_hrvg), ("eps_reg", eps_reg),
                          ("eps_cond", eps_cond)):
        if not 0.0 <= valor <= 1.0:  # S7
            fallas.append(_crit(
                "S7", f"efectividad {nombre} fuera de [0, 1]", nombre, valor,
                "[0, 1]", "entrada de usuario fuera de rango físico",
                f"corregir {nombre} a un valor en [0, 1]"))

    eta_carnot = 1.0 - T_sumidero / T_fuente
    if resultado["eta"] >= eta_carnot:  # S8
        fallas.append(_crit(
            "S8", "la eficiencia del ciclo supera la cota de Carnot (Kelvin-Planck)",
            "eta", resultado["eta"], f"< {eta_carnot:.6g} (Carnot)",
            "error en el balance de energía o en las temperaturas de reservorio",
            "revisar N2 y las temperaturas T_fuente/T_sumidero de entrada"))

    return fallas
