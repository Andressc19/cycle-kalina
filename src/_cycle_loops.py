"""Lazos de convergencia del solver del ciclo Kalina KSC-11 (helpers privados).

`resolver_ciclo` (en `src/cycle_solver.py`) orquesta DOS lazos anidados
diseñados por el director (ver `TASK_CONTEXT.md` 2026-09-17-cycle-solver):

- Lazo INTERIOR (`lazo_frio`): sustitución sucesiva sobre T10 (salida de la
  bomba), porque el regenerador necesita T10 — que depende de todo lo que viene
  después de él — para cerrar su propia salida (estado 6).
- Lazo EXTERIOR (`_bracketear` + `brentq` en `cycle_solver.py`): sobre T1
  (entrada al HRVG), por el balance de energía del regenerador a nivel de ciclo:
      h1 = h10 + (m_liquido / m_b) · (h5 − h6)

`CicloNoConvergeError` se define aquí (módulo pequeño propio, re-exportado por
`cycle_solver.py` como API pública) para que el lazo interior y la búsqueda de
bracket puedan lanzarla sin importar `cycle_solver` (evita el ciclo de imports).

Este módulo solo consume la interfaz `PropertyBackend` (patrón adapter):
nunca importa un backend concreto.
"""

from __future__ import annotations

from .components import (absorbedor, bomba, condensador, hrvg, regenerador,
                         separador, turbina, valvula)
from .properties.adapter import PropertyBackend
from .state import EstadoTermo

__all__ = ["CicloNoConvergeError", "lazo_frio", "evaluar", "_bracketear"]


class CicloNoConvergeError(Exception):
    """El lazo de convergencia del ciclo no alcanzó el punto fijo.

    Se lanza cuando el lazo interior (T10) agota ``max_iter_frio`` sin cerrar,
    o cuando la búsqueda de bracket exterior no encuentra cambio de signo de
    F en todo el rango físico de T1, (T_sumidero, T_fuente). NO se usa para
    envolver errores reales del backend o de los componentes: esos se
    propagan tal cual (constraint del TASK_CONTEXT).
    """


def lazo_frio(estado4, estado5, m_v, m_l, backend, *, P_alta, P_baja, x_b,
              m_b, T_sumidero, eps_reg, eps_cond, eta_p, T10_inicial,
              tol_T10=1e-4, max_iter=300):
    """Lazo interior: sustitución sucesiva sobre T10 (6 → 7 → 8 → 9 → 10).

    Parte de ``T10_inicial``, recorre regenerador → válvula → absorbedor →
    condensador → bomba con el estado 4 (salida turbina) y el 5 (líquido del
    separador) ya resueltos, y repite hasta que ``|estado10.T − T10_guess|``
    baja de ``tol_T10`` o se agotan ``max_iter``.

    Devuelve ``(estado6, estado7, estado8, estado9, estado10, info_reg,
    info_cond, info_bomba, convergio)`` — si no converge, los estados quedan en
    ``None`` y `evaluar` es quien lanza ``CicloNoConvergeError``.
    """
    T10_guess = T10_inicial
    estado6 = estado7 = estado8 = estado9 = estado10 = None
    info_reg = info_cond = info_bomba = None
    for _ in range(max_iter):
        h_fria = backend.h(P_alta, T=T10_guess, x=x_b)
        s_fria = backend.s(P_alta, T=T10_guess, x=x_b)
        entrada_fria = EstadoTermo(T=T10_guess, P=P_alta, h=h_fria, s=s_fria,
                                   x=x_b)
        estado6, _salida_fria_sin_usar, info_reg = regenerador.resolver(
            estado5, entrada_fria, backend, eps=eps_reg)
        estado7, _ = valvula.resolver(estado6, backend, P_salida=P_baja)
        estado8, _ = absorbedor.resolver(
            estado4, estado7, backend, m_turbina=m_v, m_valvula=m_l)
        estado9, info_cond = condensador.resolver(
            estado8, backend, T_sumidero=T_sumidero, eps=eps_cond, m=m_b)
        estado10, info_bomba = bomba.resolver(
            estado9, backend, P_salida=P_alta, eta_p=eta_p, m=m_b)
        if abs(estado10.T - T10_guess) < tol_T10:
            return (estado6, estado7, estado8, estado9, estado10,
                    info_reg, info_cond, info_bomba, True)
        T10_guess = estado10.T
    return (estado6, estado7, estado8, estado9, estado10,
            info_reg, info_cond, info_bomba, False)


def evaluar(T1_trial, backend, *, P_alta, P_baja, T_fuente, T_sumidero, x_b,
            m_b, eta_t, eta_p, eps_hrvg, eps_reg, eps_cond, tol_T10,
            max_iter_frio, T10_inicial=None):
    """Evalúa F(T1) = T1_nuevo − T1 para un T1 de prueba y recoge estados.

    Construye la cascada 1 → 2 → 3/5 → 4 → (lazo_frio 6..10) y cierra el
    balance a nivel de ciclo del regenerador:
        h1_nuevo = h10 + (m_l / m_b) · (h5 − h6)     (CONTEXT.md, mapa)
    Devuelve ``(T1_nuevo, estados, energias)`` con los 10 estados y las
    energías ``Qi``, ``Wt``, ``Qreg``, ``Qout``, ``Wp`` [kW]. Las excepciones
    reales del backend/componentes se propagan sin envolver.

    ``T10_inicial`` (opcional): arranque tibio del lazo interior. Si se omite
    (None) se parte de ``T1_trial`` (comportamiento histórico). Si se pasa el
    último T10 convergido por una evaluación previa, el lazo interior cierra
    en ~2-3 iteraciones en vez de ~5 — mismo principio que el arranque tibio
    de `_kalina_flash.py`, medido en la tarea 2026-09-17-diagnostico-
    rendimiento-solver. No cambia ninguna fórmula ni criterio físico.
    """
    T10_guess_inicial = T1_trial if T10_inicial is None else T10_inicial

    h1 = backend.h(P_alta, T=T1_trial, x=x_b)
    s1 = backend.s(P_alta, T=T1_trial, x=x_b)
    estado1 = EstadoTermo(T=T1_trial, P=P_alta, h=h1, s=s1, x=x_b, m=m_b,
                          etiqueta="1")

    estado2, info_hrvg = hrvg.resolver(estado1, backend, T_fuente=T_fuente,
                                       eps=eps_hrvg, m_b=m_b)
    estado3, estado5, _ = separador.resolver(estado2, backend)
    m_v, m_l = estado3.m, estado5.m
    estado4, info_turb = turbina.resolver(estado3, backend, P_salida=P_baja,
                                          eta_t=eta_t)

    (estado6, estado7, estado8, estado9, estado10,
     info_reg, info_cond, info_bomba, conv_frio) = lazo_frio(
        estado4, estado5, m_v, m_l, backend, P_alta=P_alta, P_baja=P_baja,
        x_b=x_b, m_b=m_b, T_sumidero=T_sumidero, eps_reg=eps_reg,
        eps_cond=eps_cond, eta_p=eta_p, T10_inicial=T10_guess_inicial,
        tol_T10=tol_T10, max_iter=max_iter_frio)
    if not conv_frio:
        raise CicloNoConvergeError(
            "lazo interior (frio) no convergio tras max_iter_frio")

    h1_nuevo = estado10.h + (m_l / m_b) * (estado5.h - estado6.h)
    T1_nuevo = backend.T_from_Ph(P_alta, h1_nuevo, x=x_b)

    estados = dict(e1=estado1, e2=estado2, e3=estado3, e4=estado4, e5=estado5,
                   e6=estado6, e7=estado7, e8=estado8, e9=estado9, e10=estado10)
    energias = dict(Qi=info_hrvg["Qi"], Wt=info_turb["Wt"],
                    Qreg=info_reg["Qreg"], Qout=info_cond["Qout"],
                    Wp=info_bomba["Wp"])
    return T1_nuevo, estados, energias


def _bracketear(F, T_sumidero, T_fuente):
    """Devuelve ``(lo, hi)`` con cambio de signo de F dentro del rango físico.

    T1 (entrada al HRVG) debe estar estrictamente entre ``T_sumidero`` y
    ``T_fuente``. El bracket inicial usa un margen de 1.0 K sobre esos extremos;
    si F(lo)·F(hi) > 0 se amplía el margen en pasos de 5.0 K hacia los extremos
    SIN salir de (T_sumidero, T_fuente). Si se agota el rango físico completo
    sin cambio de signo, lanza ``CicloNoConvergeError`` (no se inventa un
    bracket más amplio que el físicamente permitido).
    """
    paso, eps = 5.0, 1e-6
    lo, hi = T_sumidero + 1.0, T_fuente - 1.0
    if not lo < hi:
        raise CicloNoConvergeError(
            "rango físico de T1 degenerado: T_fuente <= T_sumidero + 2 K; "
            "no hay bracket posible")
    while True:
        f_lo, f_hi = F(lo), F(hi)
        if f_lo * f_hi <= 0.0:
            return lo, hi
        lo_nuevo = max(T_sumidero + eps, lo - paso)
        hi_nuevo = min(T_fuente - eps, hi + paso)
        if (lo_nuevo, hi_nuevo) == (lo, hi):
            break
        lo, hi = lo_nuevo, hi_nuevo
    raise CicloNoConvergeError(
        "no hay cambio de signo de F en todo el rango físico (T_sumidero, "
        "T_fuente); el ciclo no converge en T1")