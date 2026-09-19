"""Validación externa contra Elsayed et al. (2013), IJLCT 8(suppl_1) i69-i78,
doi:10.1093/ijlct/ctt020 — caso citado en el texto: P_alta=15 bar, x_b=0.55,
T_fuente=373 K, T_sumidero=283 K, eta_t=eta_p=0.80, eta_reportada=11.38%.

El paper cierra HRVG/regenerador/condensador por *pinch point* (ΔT_min=4 K)
y usa Ibrahim & Klein (1993) para las propiedades NH3-H2O; este repo cierra
por efectividad (CONTEXT.md) y usa Tillner-Roth & Friend (1998). ε_hrvg,
ε_reg, ε_cond y P_baja de abajo son la traducción aproximada de ese pinch a
efectividad, calibrada una sola vez (no se recalibra en cada corrida del
test — sería carísimo en tiempo de cómputo con el motor real). Metodología
completa y el porqué de cada supuesto: vault, `decisiones/
validacion-elsayed2013-ciclo-kalina-tercero-20260919.md`.

Tolerancia holgada (5% relativo, no la de 1e-3 de los balances internos)
porque aquí se apilan tres fuentes de discrepancia esperadas, no errores:
EOS distinta, traducción aproximada del pinch, y P_baja asumida (el paper
no la da). El resultado medido fue ~2.9% de error relativo — este test deja
margen para no fallar por ruido de una recalibración futura, y sí fallar si
el modelo se rompe de verdad (p. ej. una regresión que mueva eta >5%).
"""

from __future__ import annotations

from src.cycle_solver import resolver_ciclo
from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter

_P_ALTA = 1500.0
_P_BAJA = 273.5454214157179  # presión de burbuja a (T_sumidero+4K, x_b)
_T_FUENTE = 373.0
_T_SUMIDERO = 283.0
_X_B = 0.55
_ETA_T = 0.80
_ETA_P = 0.80
_M_B = 1.0
# eps calibrados (traducción del pinch de 4K, ver docstring del módulo)
_EPS_HRVG = 0.8882023116022899
_EPS_REG = 0.9380325550010874
_EPS_COND = 0.9625029043677631

_ETA_PAPER = 0.1138
_TOL_REL = 0.05


def test_eta_dentro_de_5pct_del_caso_elsayed2013():
    """eta de este repo vs. el 11.38% reportado por Elsayed et al. (2013)
    para el caso P=15 bar / x=0.55 / T_fuente=373K / T_sumidero=283K."""
    backend = AmmoniaWaterAdapter(x=_X_B)
    resultado = resolver_ciclo(
        backend, P_alta=_P_ALTA, P_baja=_P_BAJA, T_fuente=_T_FUENTE,
        T_sumidero=_T_SUMIDERO, x_b=_X_B, m_b=_M_B, eta_t=_ETA_T,
        eta_p=_ETA_P, eps_hrvg=_EPS_HRVG, eps_reg=_EPS_REG,
        eps_cond=_EPS_COND)
    error_rel = abs(resultado["eta"] - _ETA_PAPER) / _ETA_PAPER
    assert error_rel < _TOL_REL, (
        f"eta={resultado['eta']:.5f} vs paper={_ETA_PAPER}, error relativo "
        f"{error_rel:.2%} supera la tolerancia {_TOL_REL:.0%}")
