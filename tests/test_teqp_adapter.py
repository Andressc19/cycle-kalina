"""Tests de `TeqpAdapter` — alternativa de rendimiento a `AmmoniaWaterAdapter`
(ver TASK_CONTEXT 2026-09-18-validar-teqp-nh3h2o).

No repite tablas de referencia externas (eso ya lo hace
`test_ammonia_water_adapter.py` contra IAPWS G4-01): compara contra el motor
YA validado, con dos tipos de aserción distintos:
  - Valores absolutos (h, s): tolerancia laxa, porque hay un offset de
    estado de referencia constante y conocido (~1.3 kJ/kg en h, ~0.006
    kJ/kg-K en s) entre las dos bases de datos termodinámicas.
  - DIFERENCIAS entre dos estados (Δh, Δs) y saturación (bubble/dew point,
    equilibrio L-V): tolerancia estricta, porque el offset se cancela ahí y
    es lo que de verdad usa el solver del ciclo.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.cycle_solver import resolver_ciclo
from src.properties.adapter import PropertyBackend, PropertyRangeError
from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter
from src.properties.teqp_adapter import TeqpAdapter

_RAIZ = Path(__file__).resolve().parents[1]
_W = 0.5  # fraccion masica de NH3


@pytest.fixture(scope="module")
def real():
    return AmmoniaWaterAdapter(x=_W)


@pytest.fixture(scope="module")
def teqp_b():
    return TeqpAdapter(x=_W)


def test_teqp_adapter_es_property_backend_completo():
    assert issubclass(TeqpAdapter, PropertyBackend)
    assert not PropertyBackend.__abstractmethods__ - set(dir(TeqpAdapter))


def test_x_fuera_de_rango_lanza_valueerror():
    with pytest.raises(ValueError):
        TeqpAdapter(x=0.0)
    with pytest.raises(ValueError):
        TeqpAdapter(x=1.0)


def test_h_s_offset_constante_frente_al_motor_real(real, teqp_b):
    """El offset de referencia es constante: no es ruido, es una resta fija."""
    puntos = [(360.0, 3000.0), (420.0, 7000.0), (450.0, 10000.0), (400.0, 6000.0)]
    offsets_h, offsets_s = [], []
    for T, P in puntos:
        h_r, h_t = real.h(P, T=T, x=_W), teqp_b.h(P, T=T, x=_W)
        s_r, s_t = real.s(P, T=T, x=_W), teqp_b.s(P, T=T, x=_W)
        offsets_h.append(h_t - h_r)
        offsets_s.append(s_t - s_r)
    # el offset varia poco entre puntos (< 0.15 kJ/kg de dispersion en h)
    assert max(offsets_h) - min(offsets_h) < 0.15
    assert max(offsets_s) - min(offsets_s) < 0.001
    # y esta en el rango medido en TASK_CONTEXT 2026-09-18 (~1.3-1.4 kJ/kg)
    for off in offsets_h:
        assert 1.0 < off < 1.6


def test_delta_h_entre_dos_estados_coincide_con_el_motor(real, teqp_b):
    """Lo que de verdad usa el ciclo: Δh entre dos estados, no h absoluto."""
    T1, T2, P = 380.0, 420.0, 5000.0
    dh_real = real.h(P, T=T2, x=_W) - real.h(P, T=T1, x=_W)
    dh_teqp = teqp_b.h(P, T=T2, x=_W) - teqp_b.h(P, T=T1, x=_W)
    assert dh_teqp == pytest.approx(dh_real, rel=0.01)


def test_bubble_point_coincide_con_el_motor_real(real, teqp_b):
    for P in (1500.0, 3000.0, 5000.0):
        Tb_r = real.bubble_point(P, _W)
        Tb_t = teqp_b.bubble_point(P, _W)
        assert Tb_t == pytest.approx(Tb_r, abs=0.05)


def test_dew_point_coincide_con_el_motor_real(real, teqp_b):
    for P in (1500.0, 3000.0):
        Td_r = real.dew_point(P, _W)
        Td_t = teqp_b.dew_point(P, _W)
        assert Td_t == pytest.approx(Td_r, abs=0.1)


def test_equilibrio_liquido_vapor_coincide_con_el_motor_real(real, teqp_b):
    xL_r, xV_r = real.equilibrio_liquido_vapor(3000.0, 400.0)
    xL_t, xV_t = teqp_b.equilibrio_liquido_vapor(3000.0, 400.0)
    assert xL_t == pytest.approx(xL_r, abs=1e-4)
    assert xV_t == pytest.approx(xV_r, abs=1e-4)


def test_t_from_ph_round_trip(teqp_b):
    T0, P = 400.0, 5000.0
    h0 = teqp_b.h(P, T=T0, x=_W)
    T_back = teqp_b.T_from_Ph(P, h0, x=_W)
    assert T_back == pytest.approx(T0, abs=1e-3)


def test_t_from_ps_round_trip(teqp_b):
    T0, P = 400.0, 5000.0
    s0 = teqp_b.s(P, T=T0, x=_W)
    T_back = teqp_b.T_from_Ps(P, s0, x=_W)
    assert T_back == pytest.approx(T0, abs=1e-3)


def test_quality_no_soportado_lanza_notimplementederror(teqp_b):
    with pytest.raises(NotImplementedError):
        teqp_b.h(3000.0, quality=0.5)


def test_presion_no_positiva_lanza_valueerror(teqp_b):
    with pytest.raises(ValueError):
        teqp_b.h(0.0, T=400.0, x=_W)


def test_equilibrio_fuera_de_la_campana_lanza_propertyrangeerror(teqp_b):
    with pytest.raises(PropertyRangeError):
        teqp_b.equilibrio_liquido_vapor(3000.0, 200.0)


def test_resolver_ciclo_completo_con_teqp_adapter():
    """Regresión: resolver_ciclo end-to-end recorre estados/temperaturas que
    ninguno de los tests puntuales cubre (bracket de Brent, sustitución
    sucesiva de T10, estados de válvula/regenerador en cascada). Encontró
    dos bugs reales en integración (ver TASK_CONTEXT 2026-09-18): una raíz
    de densidad "líquida" espuria en vapor sobrecalentado, y una falla
    aislada de convergencia de `flash_TP` en un punto rodeado de puntos que
    sí convergen — ambos corregidos en `_teqp_flash.py`. No compara contra
    el motor real (tardaría ~8-15 min); solo verifica que converge y que el
    resultado es físicamente plausible.
    """
    backend = TeqpAdapter(x=0.5)
    res = resolver_ciclo(
        backend, P_alta=3000.0, P_baja=400.0, T_fuente=470.0,
        T_sumidero=300.032917, x_b=0.5, m_b=1.0, eta_t=0.85, eta_p=0.75,
        eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.80)
    assert 0.0 < res["eta"] < 1.0
    assert res["Wnet"] > 0.0
    assert len(res["estados"]) == 10


_MODULOS_NUEVOS = [
    "src/properties/_teqp_engine.py",
    "src/properties/_teqp_flash.py",
    "src/properties/teqp_adapter.py",
    "tests/test_teqp_adapter.py",
]


def test_archivos_nuevos_dentro_del_limite_de_200_lineas():
    for ruta in _MODULOS_NUEVOS:
        n = len((_RAIZ / ruta).read_text(encoding="utf-8").splitlines())
        assert n <= 200, f"{ruta}: {n} lineas"
