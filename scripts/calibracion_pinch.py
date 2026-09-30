"""Calibracion por punto de P_baja + eps_hrvg/eps_reg/eps_cond con el pinch
como PARAMETRO — metodo EXACTO de `scripts/calibracion_elsayed_malla.py`
(tarea 2026-09-23-barrido-pinch6-realista).

Unico cambio respecto del original: la constante `PINCH=4.0` pasa a ser el
argumento `pinch` de cada funcion, de modo que la misma malla se pueda
recorrer con pinch de 6 K sin duplicar el metodo:

- P_baja = presion de burbuja a (T_sumidero+pinch, x_b), via brentq en
  [50, P_alta-10] kPa.
- eps_hrvg/eps_reg/eps_cond: resolver una vez con eps de partida
  (0.85/0.75/0.80), despejar en forma cerrada las efectividades para que
  T2=T_fuente-pinch, T6=T10+pinch y T9=T_sumidero+pinch, clampear a
  [0.01, 0.999] y re-resolver (paso de verificacion).

Constantes fijas reutilizadas por import de `calibracion_elsayed_malla`
(T_sumidero=283 K, eta_t=eta_p=0.80, m_b=1 kg/s, EPS_PARTIDA). NO modifica
ningun archivo existente.

Verificacion de equivalencia (tarea, TESTS): con pinch=4.0 y el caso base
(x_b=0.55, P_alta=1500, T_fuente=373) reproduce el P_baja y los eps del
script original.
"""
from __future__ import annotations

from scipy.optimize import brentq

from calibracion_elsayed_malla import (
    EPS_PARTIDA, ETA_P, ETA_T, M_B, T_SUMIDERO)
from src.cycle_solver import resolver_ciclo


def calibrar_P_baja(backend, x_b: float, P_alta: float, pinch: float) -> float:
    """P_baja = presion de burbuja a (T_sumidero+pinch, x_b) [kPa].

    Bracket [50, P_alta-10] kPa (igual que validacion_elsayed2013.py):
    presion de burbuja crece con T; P_baja debe quedar por debajo de
    P_alta para que el ciclo sea fisicamente plausible.
    """
    t9_objetivo = T_SUMIDERO + pinch
    f = lambda P: backend.bubble_point(P, x_b) - t9_objetivo
    return brentq(f, 50.0, P_alta - 10.0, xtol=1e-4)


def calibrar_eps(backend, *, x_b, P_alta, P_baja, T_fuente, pinch) -> dict:
    """Calibra los tres eps (un solo paso, despeje en forma cerrada) con el
    pinch dado y re-resuelve el ciclo con ellos.

    Mismo metodo que `calibracion_elsayed_malla.calibrar_eps`, con el pinch
    como parametro: T2 = T_fuente - pinch, T6 = T10 + pinch,
    T9 = T_sumidero + pinch. Devuelve dict(eps_hrvg, eps_reg, eps_cond,
    resultado). Si cualquier paso falla (p.ej. CicloNoConvergeError o
    PropertyRangeError del paso base o de la verificacion) se propaga la
    excepcion real tal cual: el registro de la fila en el CSV es
    responsabilidad del llamador y nunca se suaviza el error.
    """
    def resolver(eps_hrvg, eps_reg, eps_cond):
        return resolver_ciclo(
            backend, P_alta=P_alta, P_baja=P_baja, T_fuente=T_fuente,
            T_sumidero=T_SUMIDERO, x_b=x_b, m_b=M_B, eta_t=ETA_T,
            eta_p=ETA_P, eps_hrvg=eps_hrvg, eps_reg=eps_reg,
            eps_cond=eps_cond)

    r0 = resolver(*EPS_PARTIDA)                  # paso base
    e0 = r0["estados"]
    h1_0, T10_0 = e0["e1"].h, e0["e10"].T
    h5_0, x5_0 = e0["e5"].h, e0["e5"].x
    h8_0 = e0["e8"].h

    h2_ideal = backend.h(P_alta, T=T_fuente, x=x_b)
    h2_target = backend.h(P_alta, T=T_fuente - pinch, x=x_b)
    eps_hrvg = (h2_target - h1_0) / (h2_ideal - h1_0)

    T6_target = T10_0 + pinch
    h6_ideal = backend.h(P_alta, T=T10_0, x=x5_0)
    h6_target = backend.h(P_alta, T=T6_target, x=x5_0)
    eps_reg = (h5_0 - h6_target) / (h5_0 - h6_ideal)

    h9_ideal = backend.h(P_baja, T=T_SUMIDERO, x=x_b)
    h9_target = backend.h(P_baja, T=T_SUMIDERO + pinch, x=x_b)
    eps_cond = (h8_0 - h9_target) / (h8_0 - h9_ideal)

    eps_hrvg = min(max(eps_hrvg, 0.01), 0.999)
    eps_reg = min(max(eps_reg, 0.01), 0.999)
    eps_cond = min(max(eps_cond, 0.01), 0.999)

    r1 = resolver(eps_hrvg, eps_reg, eps_cond)   # paso de verificacion
    return dict(eps_hrvg=eps_hrvg, eps_reg=eps_reg, eps_cond=eps_cond,
                resultado=r1)
