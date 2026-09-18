"""Tests de la capa de propiedades: interfaz abstracta, adapters (mocks) y humo real.

Los tests con mocks no dependen de que pyfluids/iapws estén instalados (el ambiente de
pyfluids se simula). El humo real de iapws corre si la librería está disponible; el de
pyfluids se salta mientras CoolProp no soporte la mezcla NH3-H2O (razón en la marca).
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.properties import adapter as adapter_mod, iapws_adapter as iapwsa
from src.properties import pyfluids_adapter as pya
from src.properties.adapter import PropertyBackend, PropertyRangeError
from src.properties.iapws_adapter import IAPWSAdapter
from src.properties.pyfluids_adapter import PyfluidsAdapter


class FakeConverter:
    """Reproduce `pyfluids.config.UnitConverter` (config SIWithCelsiusAndPercents)."""
    @staticmethod
    def convert_temperature_from_si(v: float) -> float: return v - 273.15
    @staticmethod
    def convert_temperature_to_si(v: float) -> float: return v + 273.15
    @staticmethod
    def convert_decimal_fraction_from_si(v: float) -> float: return v * 100.0
    @staticmethod
    def convert_decimal_fraction_to_si(v: float) -> float: return v * 0.01


@pytest.fixture
def pf_env():
    """Ambiente pyfluids 100% mockeado (no requiere pyfluids instalado)."""
    with patch.object(pya, "UnitConverter", lambda: FakeConverter()), \
            patch.object(pya, "Input", MagicMock()) as fake_input:
        fake_input.pressure.side_effect = lambda v: ("P", v)
        fake_input.temperature.side_effect = lambda v: ("T", v)
        fake_input.enthalpy.side_effect = lambda v: ("h", v)
        fake_input.entropy.side_effect = lambda v: ("s", v)
        fake_input.quality.side_effect = lambda v: ("q", v)
        swe = MagicMock(enthalpy=400_000.0, entropy=1_500.0, temperature=25.0)
        sat_b, sat_d = MagicMock(temperature=25.0), MagicMock(temperature=30.0)
        mixture = MagicMock()
        mixture.with_state.return_value = swe
        mixture.bubble_point_at_pressure.return_value = sat_b
        mixture.dew_point_at_pressure.return_value = sat_d
        with patch.object(pya, "_build_mixture", return_value=mixture):
            yield mixture


def test_property_backend_es_abstracto():
    metodos = {"h", "s", "T_from_Ph", "T_from_Ps", "bubble_point", "dew_point", "equilibrio_liquido_vapor"}
    with pytest.raises(TypeError):
        PropertyBackend()
    assert metodos <= set(PropertyBackend.__abstractmethods__)
    assert issubclass(PropertyRangeError, Exception)
    assert str(PropertyRangeError("m")) == "m"
    src = Path(adapter_mod.__file__).read_text(encoding="utf-8")
    assert "import pyfluids" not in src and "from pyfluids" not in src
    assert "import iapws" not in src and "from iapws" not in src


def test_pyfluids_h_s_T_convierten_unidades(pf_env):
    adapter = PyfluidsAdapter(x=0.5)
    assert adapter.h(3000.0, T=450.0) == pytest.approx(400.0)
    p_in, t_in = pf_env.with_state.call_args[0]
    assert (p_in[0], p_in[1]) == ("P", 3_000_000.0)                 # kPa -> Pa
    assert (t_in[0], t_in[1]) == ("T", 450.0 - 273.15)              # K -> °C (config)
    assert adapter.h(3000.0, s=2.5) == pytest.approx(400.0)
    _, s_in = pf_env.with_state.call_args[0]
    assert (s_in[0], s_in[1]) == ("s", 2500.0)                      # kJ/kg·K -> J/kg·K
    assert adapter.h(3000.0, quality=0.6) == pytest.approx(400.0)
    _, q_in = pf_env.with_state.call_args[0]
    assert (q_in[0], q_in[1]) == ("q", 60.0)                        # fracción -> %
    assert adapter.s(3000.0, T=450.0) == pytest.approx(1.5)
    assert adapter.T_from_Ph(3000.0, h=400.0) == pytest.approx(298.15)
    _, h_in = pf_env.with_state.call_args[0]
    assert (h_in[0], h_in[1]) == ("h", 400_000.0)                   # kJ/kg -> J/kg
    adapter.T_from_Ps(3000.0, s=1.5)
    assert pf_env.with_state.call_args[0][1][1] == 1500.0
    assert adapter.bubble_point(3000.0, x=0.5) == pytest.approx(298.15)
    assert adapter.dew_point(3000.0, x=0.5) == pytest.approx(303.15)
    pf_env.bubble_point_at_pressure.assert_called_once_with(3_000_000.0)
    pf_env.dew_point_at_pressure.assert_called_once_with(3_000_000.0)


def test_pyfluids_x_por_defecto_usa_composicion_de_instancia(pf_env):
    adapter = PyfluidsAdapter(x=0.5)
    adapter.h(3000.0, T=450.0)                      # x=None -> composicion por defecto
    adapter.h(3000.0, T=450.0, x=0.5)               # igual -> cacheada
    adapter.h(3000.0, T=450.0, x=0.8)               # distinta -> mezcla nueva
    assert pya._build_mixture.call_count == 2
    assert pya._build_mixture.call_args_list[0].args == (0.5,)
    assert pya._build_mixture.call_args_list[1].args == (0.8,)


def test_pyfluids_estado_incompleto_y_envuelve_errores(pf_env):
    with pytest.raises(ValueError):
        PyfluidsAdapter().h(3000.0)                 # sin T/s/quality/h
    with pytest.raises(ValueError):
        PyfluidsAdapter().h(0.0, T=450.0)           # P no positiva
    pf_env.with_state.side_effect = ValueError("boom")
    with pytest.raises(PropertyRangeError):
        PyfluidsAdapter().h(3000.0, T=450.0)
    pf_env.bubble_point_at_pressure.side_effect = KeyError("nope")
    with pytest.raises(PropertyRangeError):
        PyfluidsAdapter().bubble_point(3000.0, x=0.5)


def test_pyfluids_equilibrio_liquido_vapor_no_cubre_la_mezcla_en_este_entorno(pf_env):
    with pytest.raises(PropertyRangeError):
        PyfluidsAdapter(x=0.5).equilibrio_liquido_vapor(3000.0, 420.0)


def test_build_mixture_validacion_x_y_par_binario_no_soportado():
    for x_invalida in (0.0, 1.0, -0.1):
        with pytest.raises(ValueError):
            pya._build_mixture(x_invalida)
    fake_fluids_list = MagicMock(Ammonia="Ammonia", Water="Water")
    with patch.object(pya, "UnitConverter", lambda: FakeConverter()), \
            patch.object(pya, "FluidsList", fake_fluids_list), \
            patch.object(pya, "Mixture",
                         MagicMock(side_effect=ValueError("Could not match the binary pair"))):
        with pytest.raises(PropertyRangeError):
            pya._build_mixture(0.5)

class FakeIAPWS97:
    last_kwargs: dict = {}
    def __init__(self, **kwargs):
        FakeIAPWS97.last_kwargs = kwargs
        self.h, self.s, self.T = 115.0, 0.39, 300.0


def test_iapws_h_s_T_convierten_unidades():
    with patch.object(iapwsa, "IAPWS97", FakeIAPWS97):
        adapter = IAPWSAdapter()
        assert adapter.h(3000.0, T=300.0) == pytest.approx(115.0)
        assert FakeIAPWS97.last_kwargs == {"P": 3.0, "T": 300.0}   # kPa -> MPa
        adapter.h(100.0, s=0.39)
        assert FakeIAPWS97.last_kwargs == {"P": 0.1, "s": 0.39}
        assert adapter.s(100.0, T=300.0) == pytest.approx(0.39)
        assert adapter.T_from_Ph(1000.0, h=115.0) == pytest.approx(300.0)
        assert FakeIAPWS97.last_kwargs == {"P": 1.0, "h": 115.0}
        adapter.T_from_Ps(1000.0, s=0.39)
        assert FakeIAPWS97.last_kwargs == {"P": 1.0, "s": 0.39}


def test_iapws_rechaza_mezcla_quality_y_saturacion():
    adapter = IAPWSAdapter()
    for llamada in (lambda: adapter.h(100.0, T=300.0, x=0.5),
                    lambda: adapter.s(100.0, T=300.0, x=0.5),
                    lambda: adapter.h(100.0, T=300.0, quality=0.5),
                    lambda: adapter.bubble_point(100.0, x=0.5),
                    lambda: adapter.dew_point(100.0, x=0.5),
                    lambda: adapter.equilibrio_liquido_vapor(100.0, 300.0)):
        with pytest.raises(NotImplementedError):
            llamada()


def test_iapws_envuelve_errores_del_backend_y_estado_incompleto():
    with pytest.raises(ValueError):
        IAPWSAdapter().h(100.0)                     # sin T ni s
    with patch.object(iapwsa, "IAPWS97",
                      MagicMock(side_effect=ValueError("estado invalido"))):
        with pytest.raises(PropertyRangeError):
            IAPWSAdapter().h(100.0, T=300.0)
    with patch.object(iapwsa, "IAPWS97",
                      MagicMock(side_effect=NotImplementedError("Incoming out of bound"))):
        with pytest.raises(PropertyRangeError):
            IAPWSAdapter().T_from_Ph(100.0, h=99999.0)


def test_iapws_humo_real_vs_if97():
    pytest.importorskip("iapws")
    adapter = IAPWSAdapter()
    assert adapter.h(3000.0, T=300.0) == pytest.approx(115.331273, abs=1e-5)
    assert adapter.s(3000.0, T=300.0) == pytest.approx(0.392294792, abs=1e-9)
    assert adapter.T_from_Ph(3000.0, 115.331273) == pytest.approx(300.0, abs=1e-3)
    assert adapter.T_from_Ps(3000.0, 0.392294792) == pytest.approx(300.0, abs=1e-3)


def _pyfluids_mixture_disponible() -> bool:
    try:
        pya._build_mixture(0.5)
        return True
    except (PropertyRangeError, ValueError):
        return False


_PYFLUIDS_SKIP = ("CoolProp/pyfluids instalado no soporta la mezcla NH3-H2O (par binario "
                  "amoníaco-agua); se requiere REFPROP/NIST. El test se activa solo cuando el "
                  "backend lo cubra.")


@pytest.mark.skipif(not _pyfluids_mixture_disponible(), reason=_PYFLUIDS_SKIP)
def test_pyfluids_humo_real_mezcla_nh3_h2o():
    adapter = PyfluidsAdapter(x=0.5)
    h = adapter.h(3000.0, T=450.0)
    assert h > 0.0
    assert adapter.h(3000.0, s=adapter.s(3000.0, T=450.0)) == pytest.approx(h, rel=1e-6)
    assert adapter.T_from_Ph(3000.0, h) == pytest.approx(450.0, abs=1e-3)