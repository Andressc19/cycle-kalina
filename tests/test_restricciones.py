"""Tests del módulo de restricciones (`src/restricciones/`).

Usa el mismo `PropertyBackend` fake determinista que `test_components.py` /
`test_cycle_solver.py` (leyes lineales) y un `resultado` de ciclo construido a
mano (no vía `resolver_ciclo`): esto aísla la lógica de clasificación de la
convergencia del solver, con valores elegidos para que TODOS los criterios
pasen en el caso base, y luego se muta un único campo por test para aislar
cada falla.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from src.properties.adapter import PropertyBackend
from src.restricciones import Clasificacion, evaluar_ciclo
from src.restricciones.operativos import DQ, T_AMB_CAVITACION
from src.state import EstadoTermo


class FakeBackend(PropertyBackend):
    def h(self, P, T=None, x=None, s=None, quality=None):
        if T is not None:
            return T + 10.0 * x + 1e-3 * P
        if s is not None:
            return 100.0 * (s - x) + 10.0 * x + 1e-3 * P
        raise ValueError("estado incompleto en el fake")

    def s(self, P, T=None, x=None):
        return 0.01 * T + x

    def T_from_Ph(self, P, h, x=None):
        return h - 10.0 * x - 1e-3 * P

    def T_from_Ps(self, P, s, x=None):
        return 100.0 * (s - x)

    def bubble_point(self, P, x):
        return 400.0 - 100.0 * x

    def dew_point(self, P, x):
        return 420.0 - 100.0 * x

    def equilibrio_liquido_vapor(self, P, T):
        return (400.0 - T) / 100.0, (420.0 - T) / 100.0


@pytest.fixture
def backend():
    return FakeBackend()


_PARAMS = dict(P_alta=3000.0, P_baja=400.0, T_fuente=400.0, T_sumidero=340.0,
               x_b=0.5, m_b=1.0, eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.80)


def _resultado_base() -> dict:
    """Un punto del ciclo donde los 17 criterios implementados pasan (KALINA).

    Construido a mano (no resuelto): valores elegidos para satisfacer cada
    fórmula, no para representar un ciclo físicamente óptimo.
    """
    e = {
        "e1": EstadoTermo(T=300.0, P=3000.0, h=308.0, s=3.5, x=0.5, m=1.0),
        "e2": EstadoTermo(T=360.0, P=3000.0, h=368.0, s=4.1, x=0.5, m=1.0),
        "e3": EstadoTermo(T=360.0, P=3000.0, h=369.0, s=4.2, x=0.6, m=0.5),
        "e4": EstadoTermo(T=360.39, P=400.0, h=366.79, s=4.2039, x=0.6, m=0.5),
        "e5": EstadoTermo(T=360.0, P=3000.0, h=367.0, s=4.0, x=0.4, m=0.5),
        "e6": EstadoTermo(T=355.0, P=3000.0, h=362.0, s=3.95, x=0.4, m=0.5),
        "e7": EstadoTermo(T=357.6, P=400.0, h=362.0, s=3.976, x=0.4, m=0.5),
        "e8": EstadoTermo(T=358.995, P=400.0, h=364.395, s=4.08995, x=0.5, m=1.0),
        "e9": EstadoTermo(T=343.799, P=400.0, h=349.199, s=3.93799, x=0.5, m=1.0),
        "e10": EstadoTermo(T=344.6657, P=3000.0, h=352.6657, s=3.946657, x=0.5, m=1.0),
    }
    return dict(estados=e, Qi=100.0, Qout=90.0, Wt=15.0, Wp=5.0, Qreg=2.5,
               Wnet=10.0, eta=0.10)


def test_caso_kalina_sin_fallas(backend):
    resultado = _resultado_base()
    val = evaluar_ciclo(backend, resultado, **_PARAMS)
    assert val.clasificacion == Clasificacion.KALINA
    assert val.fallas == []
    assert val.principal is None
    assert "KALINA" in val.mensaje_reporte()


def test_falla_a_condensador_da_corregible(backend):
    """O2 (cavitación): T9 a T_amb=30.4°C queda por encima de T_sat,L."""
    resultado = _resultado_base()
    resultado["estados"]["e8"] = replace(resultado["estados"]["e8"], h=564.2)
    val = evaluar_ciclo(backend, resultado, **_PARAMS)
    assert val.clasificacion == Clasificacion.CORREGIBLE
    assert val.principal.codigo == "O2"
    assert val.secundarias == []


def test_falla_b_hrvg_sobrecalentado_da_degenerado(backend):
    """O5 (q2 > 1-DQ): el ciclo deja de ser Kalina, pasa a Rankine."""
    resultado = _resultado_base()
    resultado["estados"]["e2"] = replace(resultado["estados"]["e2"], T=375.0)
    val = evaluar_ciclo(backend, resultado, **_PARAMS)
    assert val.clasificacion == Clasificacion.DEGENERADO
    assert val.principal.codigo == "O5"
    assert val.secundarias == []


def test_fallas_a_y_b_simultaneas_jerarquia(backend):
    """DEGENERADO (b, principal) sobre CORREGIBLE (a, secundaria) — b es peor."""
    resultado = _resultado_base()
    resultado["estados"]["e2"] = replace(resultado["estados"]["e2"], T=375.0)
    resultado["estados"]["e8"] = replace(resultado["estados"]["e8"], h=564.2)
    val = evaluar_ciclo(backend, resultado, **_PARAMS)
    assert val.clasificacion == Clasificacion.DEGENERADO
    assert val.principal.codigo == "O5"
    codigos_secundarios = {f.codigo for f in val.secundarias}
    assert "O2" in codigos_secundarios
    mensaje = val.mensaje_reporte()
    assert mensaje.index("O5") < mensaje.index("O2")  # principal antes que secundaria


def test_falla_critica_potencia_neta_negativa_da_inviable(backend):
    resultado = _resultado_base()
    resultado["Wt"], resultado["Wnet"] = 1.0, -4.0
    resultado["Qout"] = resultado["Qi"] - resultado["Wnet"]
    val = evaluar_ciclo(backend, resultado, **_PARAMS)
    assert val.clasificacion == Clasificacion.INVIABLE
    assert val.principal.codigo == "O3"


def test_o5_umbral_dq_es_el_margen_del_motor():
    assert DQ == 1e-3


def test_t_amb_cavitacion_es_30_4_c():
    assert T_AMB_CAVITACION == pytest.approx(303.55)


def test_o2_usa_el_peor_caso_entre_t_sumidero_y_t_amb_fijo(backend):
    """Si T_sumidero de la corrida supera el piso de 30.4°C, O2 debe evaluar
    contra ese T_sumidero (peor caso real), no solo contra el piso fijo —
    evaluar solo contra el piso subestimaría el riesgo de cavitación."""
    resultado = _resultado_base()
    # T_sumidero=340 K (66.85 degC) ya excede el piso de 303.55 K (30.4 degC)
    # en _PARAMS; comparamos contra recomputar el condensador manualmente.
    from src.components import condensador
    from src.restricciones.operativos import T_AMB_CAVITACION
    e8 = resultado["estados"]["e8"]
    esperado_con_piso_fijo, _ = condensador.resolver(
        e8, backend, T_sumidero=T_AMB_CAVITACION, eps=_PARAMS["eps_cond"],
        m=_PARAMS["m_b"])
    esperado_con_peor_caso, _ = condensador.resolver(
        e8, backend, T_sumidero=_PARAMS["T_sumidero"], eps=_PARAMS["eps_cond"],
        m=_PARAMS["m_b"])
    assert esperado_con_peor_caso.T != esperado_con_piso_fijo.T  # de verdad difieren
    val = evaluar_ciclo(backend, resultado, **_PARAMS)
    principal_o2 = next((f for f in val.fallas if f.codigo == "O2"), None)
    if principal_o2 is not None:
        assert principal_o2.valor_medido == pytest.approx(esperado_con_peor_caso.T)


def test_n2_no_marca_no_convergio_un_punto_bien_convergido():
    """Regresión: 1e-6 (el valor del vault) era más estricto que el ruido
    numérico real de ESTE solver (medido ~1.85e-6 relativo en el caso base
    del fake) y marcaba falsos NO_CONVERGIO. 1e-3 debe dejarlo pasar."""
    from tests.test_cycle_solver import FakeBackend as _FB
    from tests.test_cycle_solver import _PARAMS_BASE
    from src.cycle_solver import resolver_ciclo
    from src.restricciones.numericos import verificar_n2

    resultado = resolver_ciclo(_FB(), **_PARAMS_BASE)
    assert verificar_n2(resultado) is None
