"""Solver del ciclo Kalina KSC-11 (ensamblado de los 8 componentes).

`resolver_ciclo(...)` resuelve los 10 estados del ciclo hasta la convergencia y
devuelve estados + energías. Algoritmo (diseñado por el director, ver
`TASK_CONTEXT.md` 2026-09-17-cycle-solver) con DOS lazos anidados:

- EXTERIOR sobre T1 (entrada al HRVG) por Brent: F(T1) = T1_nuevo − T1, con el
  balance a nivel de ciclo del regenerador  h1 = h10 + (m_l/m_b)·(h5 − h6).
  La búsqueda de bracket físico (T_sumidero, T_fuente) vive en `_bracketear`.
- INTERIOR (`_cycle_loops.lazo_frio`): sustitución sucesiva sobre T10.

Convención de signos de las energías (todas magnitudes [kW]): Qi entra al
fluido en el HRVG, Qout sale al sumidero en el condensador, Wt sale de la
turbina, Wp entra en la bomba; el regenerador (Qreg) es interno al ciclo.
Con eso el balance global del 1er principio es  Qi + Wp = Qout + Wt  y
Wnet = Wt − Wp, η = Wnet / Qi.

Solo consume la interfaz `PropertyBackend` (patrón adapter, CONTEXT.md):
nunca importa un backend concreto.
"""

from __future__ import annotations

from scipy.optimize import brentq

from ._cycle_loops import (CicloCancelado, CicloNoConvergeError, _bracketear,
                           evaluar)

__all__ = ["resolver_ciclo", "CicloNoConvergeError", "CicloCancelado"]


def resolver_ciclo(backend, *, P_alta, P_baja, T_fuente, T_sumidero, x_b, m_b,
                   eta_t, eta_p, eps_hrvg, eps_reg, eps_cond,
                   tol_T1=1e-4, tol_T10=1e-3, max_iter_frio=300,
                   progreso=None, cancelar=None) -> dict:
    """Resuelve los 10 estados del ciclo KSC-11 hasta la convergencia.

    Parámetros: ``backend`` (PropertyBackend), P [kPa], T [K], ``x_b`` =
    fracción másica global de NH3 [-], ``m_b`` [kg/s], η isentrópicas [-],
    ε de efectividad [-] y tolerancias de los lazos [K].

    ``tol_T10`` por defecto es 1e-3 K (relajado desde 1e-4 con la medición de
    la tarea 2026-09-17-diagnostico-rendimiento-solver: el ruido numérico del
    motor en T10 es ~7e-5 K, así que 1e-3 mantiene un margen de ~15× y el
    lazo interior cierra con una iteración menos por evaluación; la energía
    asociada cambia < 1e-2 kJ/kg).

    El lazo interior se re-arranca en tibio entre evaluaciones del lazo
    exterior (Brent): se guarda el último T10 convergido y se pasa como
    ``T10_inicial`` a la siguiente ``evaluar`` (ver `_cycle_loops.evaluar`)
    en vez de partir siempre de ``T1_trial``. Optimización numérica pura: no
    cambia ninguna fórmula ni criterio físico.

    Devuelve un dict con ``estados`` (claves e1..e10, ``EstadoTermo``) y las
    energías ``Qi``, ``Qout``, ``Wt``, ``Wp``, ``Qreg``, ``Wnet`` [kW] y
    ``eta`` [-].

    Lanza ``CicloNoConvergeError`` si el bracket agota el rango físico de T1 o
    si el lazo interior no converge; las excepciones reales del backend o de
    los componentes (p.ej. ``PropertyRangeError``) se propagan sin envolver.

    ``progreso`` y ``cancelar`` (ambos opcionales, default ``None``) son el
    gancho de la UI para una corrida larga: ``progreso`` es un callable que
    recibe un dict por iteración (``{"fase": "exterior"/"interior", ...}``) y
    ``cancelar`` un ``threading.Event`` chequeado entre iteraciones. Con
    ``None`` el comportamiento es idéntico al histórico y, si ``cancelar`` se
    activa, se lanza ``CicloCancelado`` (también re-exportado aquí).
    """
    kwargs = dict(P_alta=P_alta, P_baja=P_baja, T_fuente=T_fuente,
                  T_sumidero=T_sumidero, x_b=x_b, m_b=m_b, eta_t=eta_t,
                  eta_p=eta_p, eps_hrvg=eps_hrvg, eps_reg=eps_reg,
                  eps_cond=eps_cond, tol_T10=tol_T10,
                  max_iter_frio=max_iter_frio, cancelar=cancelar,
                  progreso=progreso)

    ultimo_T10 = None
    iteraciones = [0]

    def F(T1):
        nonlocal ultimo_T10
        T1_nuevo, estados, _ = evaluar(T1, backend, **kwargs,
                                       T10_inicial=ultimo_T10)
        ultimo_T10 = estados["e10"].T
        iteraciones[0] += 1
        if progreso is not None:
            progreso({"fase": "exterior", "iteracion": iteraciones[0],
                      "T1": T1, "residual": T1_nuevo - T1})
        return T1_nuevo - T1

    lo, hi = _bracketear(F, T_sumidero, T_fuente, cancelar=cancelar)
    T1_sol = brentq(F, lo, hi, xtol=tol_T1)

    _, estados, energias = evaluar(T1_sol, backend, **kwargs,
                                   T10_inicial=ultimo_T10)
    Wnet = energias["Wt"] - energias["Wp"]
    eta = Wnet / energias["Qi"]
    return dict(estados=estados, **energias, Wnet=Wnet, eta=eta)