"""Tests de `TeqpVerificado` (TASK_CONTEXT 2026-09-27-teqp-verificado).

`TeqpVerificado` es `TeqpAdapter` + respaldo del motor real SOLO en la zona de
riesgo de `_teqp_flash._fase_monofasica` (src/properties/_teqp_flash.py:138-140,
la franja `Ta < T <= Ta + 0.3` K). Estos tests comprueban las dos mitades:

  - LENTOS (1-3, usan el motor real `AmmoniaWaterAdapter`): el caso espurio se
    corrige y, fuera de la zona, el resultado es IDÉNTICO a `TeqpAdapter`.
  - RÁPIDOS (4, sin motor real): el criterio de zona, la pereza del motor real,
    el camino de fallo (`fallo=True` + `verificacion_incompleta`) con un stub y
    `reiniciar_registro()`.

Valores esperados tomados del caso documentado en el TASK_CONTEXT: con
`x_b=0.60, P_alta=4000, T_fuente=394, P_baja=423.914831 kPa` la salida
isentrópica de turbina `h(423.914831, s=5.704153, x=0.974965)` vale ~1626 kJ/kg
con `TeqpAdapter` (raíz falsa) y ~1486 kJ/kg con el motor real.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.cycle_solver import resolver_ciclo
from src.properties.adapter import PropertyRangeError
from src.properties.teqp_adapter import TeqpAdapter
from src.properties.teqp_verificado import TeqpVerificado
from src.properties import _teqp_engine as ng

_RAIZ = Path(__file__).resolve().parents[1]

# Caso espurio documentado (ver docstring del módulo).
X_B, P_ALTA, T_FUENTE = 0.60, 4000.0, 394.0
P_ESPURIA = 423.914831
S_3, X_3 = 5.704153, 0.974965
H_ESPURIO_TEQP, H_ESPURIO_REAL = 1626.0, 1486.0     # +/- 3 kJ/kg
# Puntos "normales" del mismo barrido: deben salir idénticos a TeqpAdapter.
NORMALES = [(0.65, 5000.0, 423.0, 704.644595), (0.80, 5000.0, 394.0, 952.892781)]
_UMBRAL = 3.0


def resolver(backend, x_b, P_alta, T_fuente, P_baja):
    return resolver_ciclo(
        backend, P_alta=P_alta, P_baja=P_baja, T_fuente=T_fuente, T_sumidero=283.0,
        x_b=x_b, m_b=1.0, eta_t=0.80, eta_p=0.80, eps_hrvg=0.85, eps_reg=0.80,
        eps_cond=0.85)


# -- 1. unitario del caso espurio ---------------------------------------------

def test_caso_espurio_corregido_por_el_motor_real():
    """`h(P, s, x)` en la zona: teqp da ~1626 (raíz falsa), verificado ~1486."""
    v = TeqpVerificado(x=X_B)
    h_real = v.h(P_ESPURIA, s=S_3, x=X_3)
    assert h_real == pytest.approx(H_ESPURIO_REAL, abs=_UMBRAL)
    assert v.n_recurrencias >= 1
    assert not v.verificacion_incompleta
    rec = v.recurrencias[0]
    assert rec["metodo"] == "h(P,s,x)"
    assert rec["criterio"] == "rico_NH3"
    assert rec["origen"] == "T_invertida"
    assert abs(rec["T_teqp"] - rec["Ta"]) < 1.0        # la T cayó en la franja
    assert rec["valor_teqp"] == pytest.approx(H_ESPURIO_TEQP, abs=_UMBRAL)
    assert rec["valor_real"] == pytest.approx(h_real, abs=1e-6)
    assert rec["t_real_s"] > 0.0

    # Documenta el bug: el mismo llamado con `TeqpAdapter` NO lo reproduce ya,
    # en cuyo caso este test debe decirlo explícitamente en vez de callar.
    h_teqp = TeqpAdapter(x=X_B).h(P_ESPURIA, s=S_3, x=X_3)
    if abs(h_teqp - H_ESPURIO_TEQP) > _UMBRAL:
        pytest.fail(
            f"TeqpAdapter ya NO reproduce el caso espurio: h={h_teqp:.3f} kJ/kg "
            f"en vez de ~{H_ESPURIO_TEQP}. El bug de _fase_monofasica "
            f"(_teqp_flash.py:138-140) fue corregido en el motor: revisar este "
            f"test y el criterio de zona de TeqpVerificado."
        )
    assert abs(h_real - h_teqp) > 100.0                 # ~139 kJ/kg de diferencia


# -- 2. ciclo espurio corregido ----------------------------------------------

def test_ciclo_espurio_recupera_eta_fisica():
    """El ciclo completo en la P_baja espuria: η ~0.080, no ~0.034."""
    v = TeqpVerificado(x=X_B)
    res = resolver(v, X_B, P_ALTA, T_FUENTE, P_ESPURIA)
    assert 0.079 <= res["eta"] <= 0.082
    assert v.n_recurrencias >= 1
    assert not v.verificacion_incompleta


# -- 3. fuera de zona, resultado idéntico ------------------------------------

@pytest.mark.parametrize("x_b, P_alta, T_fuente, P_baja", NORMALES)
def test_fuera_de_zona_identico_a_teqp_adapter(x_b, P_alta, T_fuente, P_baja):
    eta_teqp = resolver(TeqpAdapter(x=x_b), x_b, P_alta, T_fuente, P_baja)["eta"]
    v = TeqpVerificado(x=x_b)
    eta_v = resolver(v, x_b, P_alta, T_fuente, P_baja)["eta"]
    assert eta_v == eta_teqp                            # igualdad exacta
    assert v.n_recurrencias == 0
    assert not v.verificacion_incompleta


# -- 4. rápidos: criterio de zona, pereza, fallo y registro -------------------

def test_criterio_de_zona_rico_en_nh3():
    """x_molar >= 0.9 y |T - Ta| < 1 K -> zona; fuera de la franja -> None."""
    v = TeqpVerificado(x=X_B)
    Ta, Tw = ng.Tsat_pure(P_ESPURIA * 1000.0)
    assert v._criterio(P_ESPURIA * 1000.0, X_3, Ta)[:1] == ("rico_NH3",)
    assert ng.w2m(X_3) >= 0.9
    assert v._criterio(P_ESPURIA * 1000.0, X_3, Ta + 0.5) is not None
    assert v._criterio(P_ESPURIA * 1000.0, X_3, Ta - 0.5) is not None
    assert v._criterio(P_ESPURIA * 1000.0, X_3, Ta + 1.5) is None   # umbral
    assert v._criterio(P_ESPURIA * 1000.0, X_3, Tw + 40.0) is None


def test_criterio_de_zona_pobre_en_nh3_y_umbral_de_composicion():
    v = TeqpVerificado(x=0.05)
    Ta, Tw = ng.Tsat_pure(3000.0 * 1000.0)
    assert ng.w2m(0.05) <= 0.1
    assert v._criterio(3000.0 * 1000.0, 0.05, Tw)[:1] == ("pobre_NH3",)
    assert v._criterio(3000.0 * 1000.0, 0.05, Tw - 0.9) is not None
    assert v._criterio(3000.0 * 1000.0, 0.05, Tw + 1.2) is None
    # x=0.85 -> x_molar 0.857 < 0.9: ni rico ni pobre, nunca en zona
    v2 = TeqpVerificado(x=0.85)
    assert 0.85 < ng.w2m(0.85) < 0.9
    assert v2._criterio(P_ESPURIA * 1000.0, 0.85, Ta) is None
    assert v2._criterio(P_ESPURIA * 1000.0, 0.85, Tw) is None


def test_umbral_y_composiciones_configurables():
    v = TeqpVerificado(x=X_B, umbral_K=0.1, x_molar_rico=0.5)
    Ta, _ = ng.Tsat_pure(P_ESPURIA * 1000.0)
    assert v._criterio(P_ESPURIA * 1000.0, 0.80, Ta + 0.5) is None   # |dT|=0.5>0.1
    assert v._criterio(P_ESPURIA * 1000.0, 0.60, Ta + 0.05) is not None
    assert TeqpVerificado(x=X_B).x_molar_pobre == 0.1


def test_motor_real_perezoso_y_llamadas_fuera_de_zona_no_lo_crean():
    v = TeqpVerificado(x=0.5)
    assert v._real is None
    h = v.h(3000.0, T=350.0, x=0.5)
    s = v.s(3000.0, T=350.0, x=0.5)
    T = v.T_from_Ph(3000.0, h, x=0.5)
    assert T == pytest.approx(350.0, abs=1e-3)
    assert v.s(3000.0, T=T, x=0.5) == pytest.approx(s, abs=1e-6)
    assert v.h(3000.0, s=s, x=0.5) == pytest.approx(h, abs=1e-6)
    assert v.T_from_Ps(3000.0, s, x=0.5) == pytest.approx(350.0, abs=1e-3)
    assert v.n_recurrencias == 0 and v._real is None      # ni una recurrencia
    assert not v.verificacion_incompleta


class _StubReal:
    """Motor real falso: devuelve 1.0 siempre, o lanza si `error`."""

    def __init__(self, error=None):
        self.error, self.llamadas = error, 0

    def _ok(self, *a, **k):
        self.llamadas += 1
        if self.error:
            raise self.error
        return 1.0

    h = s = T_from_Ph = T_from_Ps = _ok


def test_camino_de_fallo_del_motor_real_no_inventa_valores():
    """Si el motor real falla: se devuelve el valor de teqp, `fallo=True`."""
    v = TeqpVerificado(x=X_B)
    v._real = _StubReal(error=PropertyRangeError("fuera de rango"))
    h = v.h(P_ESPURIA, s=S_3, x=X_3)
    assert h == pytest.approx(H_ESPURIO_TEQP, abs=_UMBRAL)   # el de teqp
    assert v.n_recurrencias == 1 and v.n_fallos == 1
    assert v.verificacion_incompleta
    rec = v.recurrencias[0]
    assert rec["fallo"] is True and rec["valor_real"] is None
    assert "PropertyRangeError" in rec["error"]


def test_camino_de_exito_del_respaldo_usa_el_motor_real():
    v = TeqpVerificado(x=X_B)
    stub = _StubReal()
    v._real = stub
    h = v.h(P_ESPURIA, s=S_3, x=X_3)
    assert h == 1.0 and stub.llamadas == 1
    assert v.recurrencias[0]["valor_real"] == 1.0
    assert not v.verificacion_incompleta


def test_reiniciar_registro_deja_el_adapter_limpio():
    v = TeqpVerificado(x=X_B)
    v._real = _StubReal()
    v.h(P_ESPURIA, s=S_3, x=X_3)
    assert v.recurrencias and v.t_real > 0.0
    v.reiniciar_registro()
    assert v.recurrencias == [] and v.n_recurrencias == 0
    assert v.n_fallos == 0 and v.t_real == 0.0
    assert not v.verificacion_incompleta


def test_hereda_de_teqp_adapter_y_no_crea_motor_real_al_invertir_fuera_de_zona():
    v = TeqpVerificado(x=0.5)
    assert isinstance(v, TeqpAdapter)
    h = v.h(3000.0, s=2.0, x=0.5)          # fuerza la inversión de teqp
    assert v._ultima is not None            # la T quedó capturada
    assert v._criterio(3000.0 * 1000.0, 0.5, v._ultima[2]) is None
    assert v.n_recurrencias == 0 and v._real is None
    assert h == pytest.approx(TeqpAdapter(x=0.5).h(3000.0, s=2.0, x=0.5))


def test_modulo_dentro_del_limite_de_200_lineas():
    n = len((_RAIZ / "src/properties/teqp_verificado.py").read_text(encoding="utf-8").splitlines())
    assert n <= 200, f"teqp_verificado.py: {n} lineas"
