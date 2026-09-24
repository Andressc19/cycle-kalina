"""Calibracion por punto de P_baja + eps_hrvg/eps_reg/eps_cond — metodo de
`scripts/validacion_elsayed2013.py` generalizado a una malla (tarea
2026-09-22-barrido-literatura-kcs11).

Mismo metodo de un solo paso que el caso base de Elsayed (x_b=0.55,
P_alta=1500, T_fuente=373):
- P_baja = presion de burbuja a (T_sumidero+4 K, x_b), via brentq.
- eps_hrvg/eps_reg/eps_cond: resolver una vez con eps de partida
  (0.85/0.75/0.80), despejar en forma cerrada las efectividades para que
  T2=T_fuente-4, T6=T10+4 y T9=T_sumidero+4, clampear a [0.01, 0.999] y
  re-resolver (paso de verificacion).

Parametros fijos del paper Elsayed et al. (2013) usados en toda la malla:
T_sumidero=283 K, eta_t=eta_p=0.80, m_b=1 kg/s, pinch=4 K. NO modifica
ningun archivo existente.
"""
from __future__ import annotations

from scipy.optimize import brentq

from src.cycle_solver import resolver_ciclo

T_SUMIDERO = 283.0
ETA_T = 0.80
ETA_P = 0.80
M_B = 1.0
PINCH = 4.0
T9_TARGET = T_SUMIDERO + PINCH          # 287.0 K
EPS_PARTIDA = (0.85, 0.75, 0.80)        # defaults del proyecto


def calibrar_P_baja(backend, x_b: float, P_alta: float) -> float:
    """P_baja = presion de burbuja a (T_sumidero+4 K, x_b) [kPa].

    Bracket [50, P_alta-10] kPa (igual que validacion_elsayed2013.py):
    presion de burbuja crece con T; P_baja debe quedar por debajo de
    P_alta para que el ciclo sea fisicamente plausible.
    """
    f = lambda P: backend.bubble_point(P, x_b) - T9_TARGET
    return brentq(f, 50.0, P_alta - 10.0, xtol=1e-4)


def calibrar_eps(backend, *, x_b, P_alta, P_baja, T_fuente) -> dict:
    """Calibra los tres eps (un solo paso, despeje en forma cerrada) y
    re-resuelve el ciclo con ellos.

    Devuelve dict(eps_hrvg, eps_reg, eps_cond, resultado). Si cualquier
    paso falla (p.ej. CicloNoConvergeError o PropertyRangeError del paso
    base o de la verificacion) se propaga la excepcion real tal cual: el
    registro de la fila en el CSV es responsabilidad del llamador y nunca
    se suaviza el error.
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
    h2_target = backend.h(P_alta, T=T_fuente - PINCH, x=x_b)
    eps_hrvg = (h2_target - h1_0) / (h2_ideal - h1_0)

    T6_target = T10_0 + PINCH
    h6_ideal = backend.h(P_alta, T=T10_0, x=x5_0)
    h6_target = backend.h(P_alta, T=T6_target, x=x5_0)
    eps_reg = (h5_0 - h6_target) / (h5_0 - h6_ideal)

    h9_ideal = backend.h(P_baja, T=T_SUMIDERO, x=x_b)
    h9_target = backend.h(P_baja, T=T9_TARGET, x=x_b)
    eps_cond = (h8_0 - h9_target) / (h8_0 - h9_ideal)

    eps_hrvg = min(max(eps_hrvg, 0.01), 0.999)
    eps_reg = min(max(eps_reg, 0.01), 0.999)
    eps_cond = min(max(eps_cond, 0.01), 0.999)

    r1 = resolver(eps_hrvg, eps_reg, eps_cond)   # paso de verificacion
    return dict(eps_hrvg=eps_hrvg, eps_reg=eps_reg, eps_cond=eps_cond,
                resultado=r1)