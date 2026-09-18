"""Tests de `AmmoniaWaterAdapter` — el camino real de la mezcla NH3-H2O.

El motor portado (`_nh3h2o_engine` + `_kalina_flash`) ya está validado contra
las Tablas 6-8 de IAPWS G4-01 (Tillner-Roth & Friend, 1998) en el proyecto
hermano, así que estos tests NO usan valores de referencia externos: validan
consistencia interna (round-trip h -> T_from_Ph, coherencia burbuja < rocío <
Tsat de los puros, monotonicidad del título) y que los errores de dominio del
motor se envuelven en `PropertyRangeError` (TASK_CONTEXT
2026-09-17-adapter-mezcla-nh3h2o).
"""

from pathlib import Path
import inspect
import math

import pytest

from src.properties import _kalina_flash as kf
from src.properties import _nh3h2o_engine as ng
from src.properties import ammonia_water_adapter as awa
from src.properties.adapter import PropertyBackend, PropertyRangeError
from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter

_P = 3000.0          # kPa — P_high por defecto de CONTEXT.md
_T = 623.15          # K — T_fuente por defecto de CONTEXT.md
_X = 0.5             # composición global por defecto de CONTEXT.md


def test_ammonia_es_property_backend_completo_sin_pyfluids():
    assert issubclass(AmmoniaWaterAdapter, PropertyBackend)
    assert not inspect.isabstract(AmmoniaWaterAdapter)
    src = Path(awa.__file__).read_text(encoding="utf-8")
    for frag in ("import pyfluids", "from pyfluids", "import CoolProp",
                 "from CoolProp"):
        assert frag not in src


def test_ammonia_h_real_con_valores_por_defecto_del_contexto():
    a = AmmoniaWaterAdapter(x=_X)
    h = a.h(_P, T=_T, x=_X)
    # Orden de magnitud típico de h de NH3-H2O en esa región (vapor
    # sobrecalentado a 3 MPa / 350 °C): entre -200 y 3500 kJ/kg.
    assert math.isfinite(h)
    assert -200.0 <= h <= 3500.0


def test_ammonia_round_trip_ph_con_tolerancia_del_motor():
    a = AmmoniaWaterAdapter(x=_X)
    h = a.h(_P, T=_T, x=_X)
    t_rec = a.T_from_Ph(_P, h, x=_X)
    # TOL_T (1e-6 K) es la tolerancia de inversión de brentq del motor portado;
    # la recuperación real es ~1e-10 K, muy por debajo del margen.
    assert abs(t_rec - _T) <= 1e3 * kf.TOL_T


def test_ammonia_round_trip_ps_con_tolerancia_del_motor():
    a = AmmoniaWaterAdapter(x=_X)
    s = a.s(_P, T=_T, x=_X)
    t_rec = a.T_from_Ps(_P, s, x=_X)
    assert abs(t_rec - _T) <= 1e3 * kf.TOL_T


def test_ammonia_burbuja_y_rocio_entre_saturaciones_de_puros():
    a = AmmoniaWaterAdapter(x=_X)
    tb = a.bubble_point(_P, _X)
    td = a.dew_point(_P, _X)
    ta, tw = kf.Tsat_puros(_P * 1e-3)          # motor: P en MPa
    assert tb < td
    assert ta < tb < td < tw                   # coherencia física básica
    assert math.isfinite(tb) and math.isfinite(td)


def test_ammonia_h_por_quality_no_soportado_pero_documentado():
    a = AmmoniaWaterAdapter(x=_X)
    with pytest.raises(NotImplementedError):
        a.h(_P, quality=0.5, x=_X)
    with pytest.raises(ValueError):
        a.h(_P, quality=1.5, x=_X)          # rango inválido se valida antes


def test_ammonia_inversion_dentro_de_la_campana_bifasica():
    a = AmmoniaWaterAdapter(x=_X)
    # Estado bifásico real (T entre burbuja y rocío a 3 MPa, x=0.5): la
    # inversión h -> T debe devolver una T dentro de la campana binaria.
    tb, td = a.bubble_point(_P, _X), a.dew_point(_P, _X)
    tm = 0.5 * (tb + td)
    h = a.h(_P, T=tm, x=_X)
    t_rec = a.T_from_Ph(_P, h, x=_X)
    assert tb < t_rec < td
    assert abs(t_rec - tm) <= 1e3 * kf.TOL_T


def test_ammonia_valida_argumentos_y_envuelve_errores_del_motor():
    a = AmmoniaWaterAdapter(x=_X)
    invalidas = (
        lambda: a.h(0.0, T=300.0, x=_X),            # P no positiva
        lambda: a.h(-1.0, T=300.0, x=_X),
        lambda: a.h(_P, T=300.0, x=0.0),            # composición fuera de (0, 1)
        lambda: a.h(_P, T=300.0, x=1.0),
        lambda: a.h(_P),                            # estado incompleto
        lambda: a.s(_P),                            # s sin T
        lambda: a.h(_P, quality=1.5, x=_X),         # calidad fuera de [0, 1]
        lambda: AmmoniaWaterAdapter(x=0.0),         # composición por defecto mala
    )
    for llamada in invalidas:
        with pytest.raises(ValueError):
            llamada()
    # Dominio del motor: h/s irreales -> RuntimeError del motor -> PropertyRangeError.
    with pytest.raises(PropertyRangeError):
        a.T_from_Ph(_P, h=1e6, x=_X)
    with pytest.raises(PropertyRangeError):
        a.T_from_Ps(_P, s=-999.0, x=_X)


def test_ammonia_x_por_defecto_de_instancia():
    a = AmmoniaWaterAdapter(x=_X)
    assert a.h(_P, T=_T) == pytest.approx(a.h(_P, T=_T, x=_X))
    assert a.s(_P, T=_T) == pytest.approx(a.s(_P, T=_T, x=_X))


def test_ammonia_equilibrio_liquido_vapor_real_dentro_de_la_campana():
    # Caso verificado por Claude (TASK_CONTEXT 2026-09-17-fix-separador-flash-
    # directo): flash_TP(420 K, 3.0 MPa) -> (0.3505675781113534, 0.8890627246074095)
    # MOLAR. El adapter debe devolver las mismas composiciones convertidas a
    # fracción másica con m2w (convención de la interfaz PropertyBackend).
    a = AmmoniaWaterAdapter(x=_X)
    xL, xV = a.equilibrio_liquido_vapor(_P, 420.0)
    xL_esp, xV_esp = kf.flash_TP(420.0, 3.0)
    assert xL == pytest.approx(ng.m2w(xL_esp))
    assert xV == pytest.approx(ng.m2w(xV_esp))
    # Coherencia física: líquido pobre en NH3, vapor rico; ambas en (0, 1).
    assert 0.0 < xL < 0.5 < xV < 1.0
    assert xL < xV


def test_ammonia_equilibrio_liquido_vapor_fuera_de_la_campana_es_range_error():
    # T por debajo de Tsat(NH3) y por encima de Tsat(H2O) a 3 MPa: sin fase
    # bifásica -> flash_TP devuelve None -> PropertyRangeError con mensaje claro.
    a = AmmoniaWaterAdapter(x=_X)
    for T_fuera in (200.0, 600.0):
        with pytest.raises(PropertyRangeError) as excinfo:
            a.equilibrio_liquido_vapor(_P, T_fuera)
        assert "equilibrio_liquido_vapor" in str(excinfo.value)