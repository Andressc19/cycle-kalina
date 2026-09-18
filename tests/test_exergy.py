"""Tests del módulo de exergía física del ciclo Kalina KSC-11.

Usa el mismo `PropertyBackend` fake determinista que `test_components.py` /
`test_cycle_solver.py` (leyes lineales para calcular a mano cada valor
esperado): h = T + 10·x + 1e-3·P ;  s = 0.01·T + x ;  T_from_Ph = h − 10·x −
1e-3·P. Cubre: la fórmula de exergía física de CONTEXT.md, las 8 fórmulas de
`Sgen`/`Ed` traducidas 1:1, el cierre del balance global sobre el resultado
real de `resolver_ciclo` (con el fake) y la no mutación de los estados.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src import exergy
from src.cycle_solver import resolver_ciclo
from src.properties.adapter import PropertyBackend
from src.state import EstadoTermo

_RAIZ = Path(__file__).resolve().parents[1]

_PARAMS_BASE = dict(P_alta=3000.0, P_baja=400.0, T_fuente=369.0,
                    T_sumidero=350.0, x_b=0.5, m_b=1.0, eta_t=0.85,
                    eta_p=0.75, eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.80)


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


def _estado(T, P, x, m):
    """EstadoTermo coherente con las leyes lineales del fake."""
    return EstadoTermo(T=T, P=P, h=T + 10.0 * x + 1e-3 * P,
                       s=0.01 * T + x, x=x, m=m)


def _resultado_mano():
    """Estados + energías elegidos para calcular cada Sgen a mano."""
    estados = dict(
        e1=_estado(350.0, 3000.0, 0.5, 1.0), e2=_estado(400.0, 3000.0, 0.5, 1.0),
        e3=_estado(400.0, 3000.0, 0.6, 0.5), e4=_estado(380.0, 400.0, 0.6, 0.5),
        e5=_estado(410.0, 3000.0, 0.4, 0.5), e6=_estado(370.0, 3000.0, 0.4, 0.5),
        e7=_estado(365.0, 400.0, 0.4, 0.5), e8=_estado(374.0, 400.0, 0.5, 1.0),
        e9=_estado(330.0, 400.0, 0.5, 1.0), e10=_estado(340.0, 3000.0, 0.5, 1.0),
    )
    return dict(estados=estados, Qi=50.0, Qout=44.0, Wt=11.3, Wp=12.6,
                Wnet=-1.3, Qreg=35.0, eta=-0.026)


def test_defaults_del_estado_muerto_son_los_documentados():
    assert exergy.T0_POR_DEFECTO == pytest.approx(300.032917)
    assert exergy.P0_POR_DEFECTO == pytest.approx(101.325)


def test_exergia_fisica_formula_exacta_de_context(backend):
    # e1: h=358, s=4.0, x=0.5. Con T0=300, P0=100: h0=305.1, s0=3.5
    # ex = (358−305.1) − 300·(4.0−3.5) = 52.9 − 150 = −97.1
    e1 = _estado(350.0, 3000.0, 0.5, 1.0)
    assert exergy.exergia_fisica(e1, backend, T0=300.0, P0=100.0) == \
        pytest.approx(-97.1)
    # e5: x=0.4 → h0=304.1, s0=3.4: ex = 112.9 − 300·1.1 = −217.1
    e5 = _estado(410.0, 3000.0, 0.4, 0.5)
    assert exergy.exergia_fisica(e5, backend, T0=300.0, P0=100.0) == \
        pytest.approx(-217.1)


def test_exergia_fisica_usa_x_propia_de_la_corriente(backend):
    # La referencia se evalúa con x0 = x_corriente (sin química): se
    # comprueba con un spy que backend.h/backend.s reciben x=estado.x (con
    # leyes lineales, ex es independiente de x al evaluar a la MISMA x).
    llamadas = []

    class Spy(FakeBackend):
        def h(self, P, T=None, x=None, s=None, quality=None):
            llamadas.append(("h", P, T, x))
            return super().h(P, T=T, x=x)

        def s(self, P, T=None, x=None):
            llamadas.append(("s", P, T, x))
            return super().s(P, T=T, x=x)

    e = _estado(360.0, 3000.0, 0.5, 1.0)
    exergy.exergia_fisica(e, Spy(), T0=300.0, P0=100.0)
    assert ("h", 100.0, 300.0, 0.5) in llamadas
    assert ("s", 100.0, 300.0, 0.5) in llamadas
    # Y con otra composición la referencia se evalúa con esa x.
    exergy.exergia_fisica(_estado(360.0, 3000.0, 0.4, 1.0), Spy(),
                          T0=300.0, P0=100.0)
    assert ("h", 100.0, 300.0, 0.4) in llamadas
    assert ("s", 100.0, 300.0, 0.4) in llamadas


def test_exergia_fisica_con_defaults_devuelve_finito(backend):
    valor = exergy.exergia_fisica(_estado(400.0, 3000.0, 0.5, 1.0), backend)
    assert isinstance(valor, float) and abs(valor) < 1e6


def test_calcular_exergia_8_formulas_de_sgen_a_mano(backend):
    res = exergy.calcular_exergia(_resultado_mano(), backend, T_fuente=400.0,
                                  T_sumidero=300.0, T0=300.0, P0=100.0)
    esperado_sgen = dict(
        hrvg=1.0 * (4.5 - 4.0) - 50.0 / 400.0,          # 0.375
        separador=0.5 * 4.6 + 0.5 * 4.5 - 1.0 * 4.5,    # 0.05
        turbina=0.5 * (4.4 - 4.6),                      # -0.1
        regenerador=0.5 * (4.1 - 4.5) + 1.0 * (4.0 - 3.9),  # -0.1
        valvula=0.5 * (4.05 - 4.1),                     # -0.025
        absorbedor=1.0 * 4.24 - 0.5 * 4.4 - 0.5 * 4.05, # 0.015
        condensador=1.0 * (3.8 - 4.24) + 44.0 / 300.0,  # -0.293333
        bomba=1.0 * (3.9 - 3.8),                        # 0.1
    )
    for comp, val in esperado_sgen.items():
        assert res["sgen"][comp] == pytest.approx(val), comp
        assert res["ed"][comp] == pytest.approx(300.0 * val), comp
    assert res["ed_total"] == pytest.approx(300.0 * sum(esperado_sgen.values()))
    assert res["ex_qi"] == pytest.approx(12.5)          # 50·(1 − 300/400)
    assert res["ex_qout"] == pytest.approx(0.0)         # 44·(1 − 300/300)
    # El residual es la aritmética definicional del balance global.
    assert res["residual"] == pytest.approx(
        res["ex_qi"] - (-1.3) - res["ex_qout"] - res["ed_total"])


def test_calcular_exergia_rellena_exergia_fisica_sin_mutar(backend):
    resultado = _resultado_mano()
    res = exergy.calcular_exergia(resultado, backend, T_fuente=400.0,
                                  T_sumidero=300.0, T0=300.0, P0=100.0)
    for k, e in resultado["estados"].items():
        assert e.exergia_fisica is None                 # original intacto
        copia = res["estados"][k]
        assert copia is not e
        assert copia.exergia_fisica == pytest.approx(exergy.exergia_fisica(
            e, backend, T0=300.0, P0=100.0))
    assert set(res["estados"]) == {f"e{i}" for i in range(1, 11)}


def test_calcular_exergia_exige_t_fuente_y_t_sumidero(backend):
    with pytest.raises(TypeError):
        exergy.calcular_exergia(_resultado_mano(), backend, T0=300.0, P0=100.0)


def test_cierre_del_balance_global_con_resultado_real_del_solver(backend):
    # Balance global sobre el ciclo resuelto (fake): Ex_Qi − Wnet − Ex_Qout
    # debe cuadrar con Ed_total dentro de tolerancia relativa razonable.
    ciclo = resolver_ciclo(backend, **_PARAMS_BASE)
    res = exergy.calcular_exergia(ciclo, backend, T_fuente=369.0,
                                  T_sumidero=350.0, T0=300.0, P0=100.0)
    assert res["residual_rel"] < 1e-3
    assert res["residual"] == pytest.approx(
        res["ex_qi"] - ciclo["Wnet"] - res["ex_qout"] - res["ed_total"])
    # Todas las magnitudes finitas y los 8 componentes presentes.
    for comp in ("hrvg", "separador", "turbina", "regenerador", "valvula",
                 "absorbedor", "condensador", "bomba"):
        assert comp in res["sgen"] and comp in res["ed"]
        assert res["ed"][comp] == pytest.approx(300.0 * res["sgen"][comp])


_MODULOS_NUEVOS = ["src/exergy.py", "tests/test_exergy.py"]


def test_nuevos_archivos_dentro_del_limite_de_200_lineas():
    for ruta in _MODULOS_NUEVOS:
        assert len((_RAIZ / ruta).read_text(encoding="utf-8").splitlines()) <= 200


def test_exergy_no_importa_backends_concretos():
    prohibidos = ("iapws", "AmmoniaWaterAdapter", "IAPWSAdapter",
                  "PyfluidsAdapter", "pyfluids", "CoolProp")
    texto = (_RAIZ / "src/exergy.py").read_text(encoding="utf-8")
    assert not any(p in texto for p in prohibidos)