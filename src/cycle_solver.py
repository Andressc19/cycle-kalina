"""Solver del ciclo Kalina KSC-11 (ensamblado de los 8 componentes).

`resolver_ciclo(...)` resuelve los 10 estados del ciclo hasta la convergencia y
devuelve estados + energías. Algoritmo (diseñado por el director, ver
`TASK_CONTEXT.md` 2026-09-17-cycle-solver) con DOS lazos anidados:

- EXTERIOR sobre T1 (entrada al HRVG) por Brent: F(T1) = T1_nuevo − T1, con el
  balance a nivel de ciclo del regenerador  h1 = h10 + (m_l/m_b)·(h5 − h6).
  La búsqueda de bracket físico (T_sumidero, T_fuente) vive en `_bracketear`;
  con `bracket_tolerante=True` la variante MA (extremos replegados hacia
  dentro y presupuesto de tiempo) vive en `_bracket_tolerante`.
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

from ._bracket_tolerante import BracketTolerante
from ._cycle_loops import CicloNoConvergeError, _bracketear, evaluar

__all__ = ["resolver_ciclo", "CicloNoConvergeError"]


def resolver_ciclo(backend, *, P_alta, P_baja, T_fuente, T_sumidero, x_b, m_b,
                   eta_t, eta_p, eps_hrvg, eps_reg, eps_cond,
                   tol_T1=1e-4, tol_T10=1e-3, max_iter_frio=300,
                   bracket_tolerante=False, presupuesto_s=None) -> dict:
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

    Con ``bracket_tolerante=True`` (modo MA, tarea 2026-10-02-implementar-ma)
    el lazo exterior **nunca se rinde ante un estado no evaluable**
    (`PropertyRangeError`, p.ej. dos fases que el motor no cubre):

    - el bracket físico ``(T_sumidero + 1, T_fuente − 1)`` se repliega hacia
      dentro 5 K por extremo y por intento, sin tope, hasta que ambos extremos
      sean evaluables; si entonces F no cambia de signo se rinde (sin el
      ensanche final de `_bracketear`; ver `_bracket_tolerante`);
    - un punto **interior** de Brent no evaluable no tiene recuperación y
      lanza ``CicloNoConvergeError`` con la T en el mensaje; solo se tolera
      ``PropertyRangeError`` (cualquier otra excepción sube sin envolver);
    - ``presupuesto_s`` [s] opcional: con reloj de pared ``time.perf_counter``
      desde el inicio de esta llamada, comprobado **entre evaluaciones de F**
      (nunca a mitad de una); al agotarse lanza ``CicloNoConvergeError`` con
      "presupuesto de tiempo agotado" y el nº de evaluaciones hechas;
    - añade al dict la clave ``bracket`` = ``dict(lo, hi, repliegues_lo,
      repliegues_hi, nF)``, donde ``nF`` es el nº de evaluaciones de F (la
      final, con T1 ya resuelto, no cuenta).

    Con ``bracket_tolerante=False`` (por defecto) el camino es exactamente el
    anterior (mismas llamadas, mismo resultado, mismas claves) y
    ``presupuesto_s`` se ignora.

    Devuelve un dict con ``estados`` (claves e1..e10, ``EstadoTermo``) y las
    energías ``Qi``, ``Qout``, ``Wt``, ``Wp``, ``Qreg``, ``Wnet`` [kW] y
    ``eta`` [-].

    Lanza ``CicloNoConvergeError`` si el bracket agota el rango físico de T1 o
    si el lazo interior no converge; las excepciones reales del backend o de
    los componentes (p.ej. ``PropertyRangeError``, si no se pide tolerancia)
    se propagan sin envolver.
    """
    kwargs = dict(P_alta=P_alta, P_baja=P_baja, T_fuente=T_fuente,
                  T_sumidero=T_sumidero, x_b=x_b, m_b=m_b, eta_t=eta_t,
                  eta_p=eta_p, eps_hrvg=eps_hrvg, eps_reg=eps_reg,
                  eps_cond=eps_cond, tol_T10=tol_T10,
                  max_iter_frio=max_iter_frio)

    if bracket_tolerante:                                # MA (ver _bracket_tolerante)
        ma = BracketTolerante(evaluar, backend, kwargs, T_sumidero=T_sumidero,
                              T_fuente=T_fuente, presupuesto_s=presupuesto_s)
        lo, hi = ma.bracketear()
        res = ma.cerrar(brentq(ma.F_brentq, lo, hi, xtol=tol_T1))
        res["bracket"] = ma.info_bracket(lo, hi)
        return res

    ultimo_T10 = None

    def F(T1):
        nonlocal ultimo_T10
        T1_nuevo, estados, _ = evaluar(T1, backend, **kwargs,
                                       T10_inicial=ultimo_T10)
        ultimo_T10 = estados["e10"].T
        return T1_nuevo - T1

    lo, hi = _bracketear(F, T_sumidero, T_fuente)
    T1_sol = brentq(F, lo, hi, xtol=tol_T1)

    _, estados, energias = evaluar(T1_sol, backend, **kwargs,
                                   T10_inicial=ultimo_T10)
    Wnet = energias["Wt"] - energias["Wp"]
    eta = Wnet / energias["Qi"]
    return dict(estados=estados, **energias, Wnet=Wnet, eta=eta)