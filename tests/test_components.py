"""Tests unitarios de los 8 componentes del ciclo Kalina KSC-11.

`PropertyBackend` fake determinista (nunca los backends reales), con leyes
lineales para comparar cada fórmula de CONTEXT.md contra el cálculo a mano:
    h = T + 10·x + 1e-3·P ;   s = 0.01·T + x
    T_from_Ph = h − 10·x − 1e-3·P ;   T_from_Ps = 100·(s − x)
    bubble_point = 400 − 100·x ;   dew_point = 420 − 100·x
    equilibrio_liquido_vapor = ((400 − T)/100, (420 − T)/100)  # inversa de las dos
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.components import (absorbedor, bomba, condensador, hrvg, regenerador,
                            separador, turbina, valvula)
from src.properties.adapter import PropertyBackend, PropertyRangeError
from src.state import EstadoTermo

_RAIZ = Path(__file__).resolve().parents[1]


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


def test_estado_termo_defaults():
    e = EstadoTermo(T=300.0, P=100.0, h=1.0, s=2.0, x=0.5)
    assert (e.m, e.q, e.fase, e.exergia_fisica, e.etiqueta) == (None,) * 5


def test_hrvg_efectividad(backend):
    # h1 = 308; h2,max = 608; h2 = 308 + 0.8·300 = 548; T2 = 540; s2 = 5.9
    entrada = EstadoTermo(T=300.0, P=3000.0, h=308.0, s=3.5, x=0.5, m=9.9)
    estado2, res = hrvg.resolver(entrada, backend, T_fuente=600.0, eps=0.8, m_b=1.0)
    assert estado2.h == pytest.approx(548.0)
    assert estado2.T == pytest.approx(540.0)
    assert estado2.s == pytest.approx(5.9)
    assert estado2.P == 3000.0 and estado2.x == 0.5
    assert estado2.m == 1.0 and estado2.etiqueta == "2"
    assert res["Qi"] == pytest.approx(240.0)              # m_b·(h2 − h1)


def test_separador_regla_de_la_palanca(backend):
    # T=360 entre burbuja (350) y rocío (370): x_líq = 0.4, y_vap = 0.6
    # f_vapor = (0.5−0.4)/(0.6−0.4) = 0.5 → m_vap = m_líq = 0.5
    entrada = EstadoTermo(T=360.0, P=3000.0, h=368.0, s=4.1, x=0.5, m=1.0)
    vapor, liquido, res = separador.resolver(entrada, backend)
    assert vapor.x == pytest.approx(0.6) and liquido.x == pytest.approx(0.4)
    assert vapor.m == pytest.approx(0.5) and liquido.m == pytest.approx(0.5)
    assert vapor.h == pytest.approx(369.0) and liquido.h == pytest.approx(367.0)
    assert vapor.s == pytest.approx(4.2) and liquido.s == pytest.approx(4.0)
    assert (vapor.q, vapor.fase, vapor.etiqueta) == (1.0, "vapor", "3")
    assert (liquido.q, liquido.fase, liquido.etiqueta) == (0.0, "liquido", "5")
    assert res == {}
    assert vapor.m + liquido.m == pytest.approx(entrada.m)
    reconstruida = (vapor.m * vapor.x + liquido.m * liquido.x) / entrada.m
    assert reconstruida == pytest.approx(entrada.x)
    # Sin caudal de entrada, los caudales de salida quedan sin fijar.
    sin_m = EstadoTermo(T=360.0, P=3000.0, h=368.0, s=4.1, x=0.5)
    v2, l2, _ = separador.resolver(sin_m, backend)
    assert v2.m is None and l2.m is None


def test_separador_propaga_excepcion_del_backend():
    class BackendFueraDeRango(FakeBackend):
        def equilibrio_liquido_vapor(self, P, T):
            raise PropertyRangeError("equilibrio L-V fuera de rango")

    entrada = EstadoTermo(T=360.0, P=3000.0, h=368.0, s=4.1, x=0.5, m=1.0)
    with pytest.raises(PropertyRangeError):
        separador.resolver(entrada, BackendFueraDeRango())


def test_turbina_eficiencia_isentropica(backend):
    # h4s = 505.4; h4 = 508 − 0.9·2.6 = 505.66; T4 = 500.26; s4 = 5.5026
    entrada = EstadoTermo(T=500.0, P=3000.0, h=508.0, s=5.5, x=0.5, m=1.0)
    estado4, res = turbina.resolver(entrada, backend, P_salida=400.0, eta_t=0.9)
    assert estado4.h == pytest.approx(505.66)
    assert estado4.T == pytest.approx(500.26)
    assert estado4.s == pytest.approx(5.5026)
    assert estado4.P == 400.0 and estado4.x == 0.5 and estado4.m == 1.0
    assert estado4.etiqueta == "4" and res["Wt"] == pytest.approx(2.34)
    # Sin caudal, Wt queda normalizado por unidad de masa (kJ/kg).
    sin_m = EstadoTermo(T=500.0, P=3000.0, h=508.0, s=5.5, x=0.5)
    e4, r4 = turbina.resolver(sin_m, backend, P_salida=400.0, eta_t=0.9)
    assert e4.m is None and r4["Wt"] == pytest.approx(2.34)


def test_regenerador_efectividad_y_lado_frio_pass_through(backend):
    # h6,min = h(3000, T=313, x=0.5) = 321; h6 = 368 − 0.75·47 = 332.75
    caliente = EstadoTermo(T=360.0, P=3000.0, h=368.0, s=4.1, x=0.5, m=1.0)
    fria = EstadoTermo(T=313.0, P=3000.0, h=321.0, s=3.63, x=0.5, m=1.0)
    estado6, salida_fria, res = regenerador.resolver(caliente, fria, backend, eps=0.75)
    assert estado6.h == pytest.approx(332.75)
    assert estado6.T == pytest.approx(324.75)
    assert estado6.s == pytest.approx(3.7475)
    assert estado6.etiqueta == "6" and estado6.m == 1.0
    # Lado frío sin cambiar: CONTEXT.md no define el estado 1 (pass-through).
    assert salida_fria == fria and salida_fria is not fria
    assert res["Qreg"] == pytest.approx(35.25)


def test_valvula_isoentalpica(backend):
    # h7 = 358; T7 = 358 − 5 − 0.4 = 352.6; s7 = 4.026
    entrada = EstadoTermo(T=350.0, P=3000.0, h=358.0, s=4.0, x=0.5, m=0.5)
    estado7, res = valvula.resolver(entrada, backend, P_salida=400.0)
    assert estado7.h == pytest.approx(entrada.h)
    assert estado7.T == pytest.approx(352.6)
    assert estado7.s == pytest.approx(4.026)
    assert estado7.P == 400.0 and estado7.x == 0.5 and estado7.m == 0.5
    assert estado7.etiqueta == "7" and res == {}


def test_absorbedor_mezcla_adiabatica(backend):
    turbina_sal = EstadoTermo(T=340.0, P=400.0, h=346.4, s=3.9, x=0.6, m=0.5)
    valvula_sal = EstadoTermo(T=352.6, P=400.0, h=357.0, s=4.0, x=0.4, m=0.5)
    estado8, res = absorbedor.resolver(
        turbina_sal, valvula_sal, backend, m_turbina=0.5, m_valvula=0.5
    )
    assert estado8.m == pytest.approx(1.0)                # ṁ8 = ṁ4 + ṁ7
    assert estado8.h == pytest.approx(351.7)              # (ṁ4h4 + ṁ7h7)/ṁ8
    assert estado8.x == pytest.approx(0.5)                # reconstruye x_b
    assert estado8.T == pytest.approx(346.3)
    assert estado8.s == pytest.approx(3.963)
    assert estado8.etiqueta == "8" and res == {}


def test_condensador_efectividad(backend):
    # h9,min = 305.4; h9 = 365.4 − 0.8·60 = 317.4; T9 = 312; s9 = 3.62
    entrada = EstadoTermo(T=360.0, P=400.0, h=365.4, s=4.1, x=0.5, m=1.0)
    estado9, res = condensador.resolver(
        entrada, backend, T_sumidero=300.0, eps=0.8, m=1.0
    )
    assert estado9.h == pytest.approx(317.4)
    assert estado9.T == pytest.approx(312.0)
    assert estado9.s == pytest.approx(3.62)
    assert estado9.P == 400.0 and estado9.m == 1.0
    assert estado9.etiqueta == "9" and res["Qout"] == pytest.approx(48.0)


def test_bomba_eficiencia_isentropica(backend):
    # h10s = 320; h10 = 317.4 + 2.6/0.75 = 320.8667; T10 = 312.8667
    entrada = EstadoTermo(T=312.0, P=400.0, h=317.4, s=3.62, x=0.5, m=1.0)
    estado10, res = bomba.resolver(entrada, backend, P_salida=3000.0, eta_p=0.75, m=1.0)
    assert estado10.h == pytest.approx(320.8666667)
    assert estado10.T == pytest.approx(312.8666667)
    assert estado10.s == pytest.approx(3.628666667)
    assert estado10.P == 3000.0 and estado10.m == 1.0
    assert estado10.etiqueta == "10" and res["Wp"] == pytest.approx(3.4666667)


_MODULOS = ["src/state.py"] + [
    f"src/components/{c}.py" for c in ("hrvg", "separador", "turbina",
                                       "regenerador", "valvula", "absorbedor",
                                       "condensador", "bomba")
]


def test_archivos_dentro_del_limite_de_200_lineas():
    for ruta in _MODULOS:
        assert len((_RAIZ / ruta).read_text(encoding="utf-8").splitlines()) <= 200, ruta


def test_componentes_no_importan_backends_concretos():
    prohibidos = ("iapws", "AmmoniaWaterAdapter", "IAPWSAdapter",
                  "PyfluidsAdapter", "pyfluids", "CoolProp")
    for ruta in _MODULOS[1:]:
        texto = (_RAIZ / ruta).read_text(encoding="utf-8")
        assert not any(p in texto for p in prohibidos), ruta
