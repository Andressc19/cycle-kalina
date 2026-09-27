"""Tests de `verificar_turbina` (opción B de TASK_CONTEXT
2026-09-27-medicion-tiempos-A-B).

B recalcula, para un punto YA resuelto, la salida isentrópica de turbina
`h4s = h(P_baja, s3, x3)` con el motor real y la compara con la que usó el motor
que resolvió el ciclo; si |Δh4s| > umbral (2.0 kJ/kg) el punto queda NO
verificado.

  - LENTOS (1-3, usan el motor real `AmmoniaWaterAdapter`): el caso espurio se
    marca `verificado=False` con |Δh4s| > 100 kJ/kg, y un punto normal pasa con
    `verificado=True`. También se comprueba que la reconstrucción de `h4s` desde
    `e3.h`/`e4.h`/`eta_t` coincide con `backend_teqp.h(...)` — de eso depende toda
    laeconomía de B.
  - RÁPIDOS (4-8, sin motor real): equivalencia vía `backend_teqp`, camino de
    fallo (`verificado=None` + mensaje real) con un stub, `eta_t` obligatorio,
    umbral configurable y una sola llamada al motor.

Valores esperados del TASK_CONTEXT: con `x_b=0.60, P_alta=4000, T_fuente=394,
P_baja=423.914831 kPa` teqp da h4s≈1625.7 y el motor real ≈1486.7 (139 kJ/kg);
en puntos normales `h4s_teqp - h4s_real` = -0.7 a -1.6 kJ/kg.
"""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from src.cycle_solver import resolver_ciclo
from src.properties.adapter import PropertyRangeError
from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter
from src.properties.teqp_adapter import TeqpAdapter
from src.verificacion_motor_real import UMBRAL_KJKG, verificar_turbina

_RAIZ = Path(__file__).resolve().parents[1]
EPS = (0.85, 0.80, 0.85)
ETA = 0.80
UMBRAL = UMBRAL_KJKG

# Caso espurio documentado y punto normal exigido por el TASK_CONTEXT.
X_B, P_ALTA, T_FUENTE, P_ESPURIA = 0.60, 4000.0, 394.0, 423.914831
NORMAL = (0.65, 5000.0, 423.0, 704.644595)
H_ESPURIO_TEQP, H_ESPURIO_REAL = 1625.7, 1486.7     # +/- 3 kJ/kg


def resolver(x_b, P_alta, T_fuente, P_baja):
    return resolver_ciclo(
        TeqpAdapter(x=x_b), P_alta=P_alta, P_baja=P_baja, T_fuente=T_fuente,
        T_sumidero=283.0, x_b=x_b, m_b=1.0, eta_t=ETA, eta_p=ETA,
        eps_hrvg=EPS[0], eps_reg=EPS[1], eps_cond=EPS[2])


# -- 1. el caso espurio queda NO verificado -----------------------------------

def test_caso_espurio_detectado_por_B():
    """Con `TeqpAdapter` el ciclo usa la raíz falsa: B debe marcarlo NO verificado."""
    res = resolver(X_B, P_ALTA, T_FUENTE, P_ESPURIA)
    v = verificar_turbina(res, P_baja=P_ESPURIA,
                          motor_real=AmmoniaWaterAdapter(x=X_B), eta_t=ETA)
    assert v["verificado"] is False
    assert abs(v["dh4s"]) > 100.0                        # ~139 kJ/kg
    assert v["h4s_teqp"] == pytest.approx(H_ESPURIO_TEQP, abs=3.0)
    assert v["h4s_real"] == pytest.approx(H_ESPURIO_REAL, abs=3.0)
    assert v["error"] == "" and v["h4s_teqp_fuente"] == "reconstruido"
    assert v["t_real_s"] > 0.0
    assert v["dh4s"] == pytest.approx(v["h4s_teqp"] - v["h4s_real"], rel=1e-15)
    assert v["s3"] == pytest.approx(res["estados"]["e3"].s, rel=1e-15)
    assert v["x3"] == pytest.approx(res["estados"]["e3"].x, rel=1e-15)


# -- 2. un punto normal pasa la verificación ---------------------------------

def test_punto_normal_verificado():
    res = resolver(*NORMAL)
    v = verificar_turbina(res, P_baja=NORMAL[3],
                          motor_real=AmmoniaWaterAdapter(x=NORMAL[0]), eta_t=ETA)
    assert v["verificado"] is True
    assert abs(v["dh4s"]) <= UMBRAL
    assert -1.6 <= v["dh4s"] <= -0.7                     # offset sistemático medido


# -- 3. la reconstrucción de h4s es la h4s de teqp ----------------------------

def test_reconstruccion_de_h4s_coincide_con_backend_teqp():
    """`h3 - (h3 - h4)/eta_t` debe reproducir `backend_teqp.h(P_baja, s3, x3)`."""
    res = resolver(X_B, P_ALTA, T_FUENTE, P_ESPURIA)
    a = verificar_turbina(res, P_baja=P_ESPURIA,
                          motor_real=AmmoniaWaterAdapter(x=X_B), eta_t=ETA)
    b = verificar_turbina(res, P_baja=P_ESPURIA,
                          motor_real=AmmoniaWaterAdapter(x=X_B),
                          backend_teqp=TeqpAdapter(x=X_B))
    assert a["h4s_teqp_fuente"] == "reconstruido"
    assert b["h4s_teqp_fuente"] == "backend_teqp"
    assert abs(a["h4s_teqp"] - b["h4s_teqp"]) < 1e-9      # ulp, no kJ/kg
    assert b["dh4s"] == pytest.approx(a["dh4s"], abs=1e-9)
    assert b["verificado"] is False


# -- 4-8. rápidos: sin motor real ---------------------------------------------

class _StubReal:
    """Motor real falso: devuelve `valor` siempre, o lanza si `error`."""

    def __init__(self, valor=1.0, error=None):
        self.valor, self.error, self.llamadas = valor, error, 0

    def h(self, P, T=None, x=None, s=None, quality=None):
        self.llamadas += 1
        if self.error is not None:
            raise self.error
        return self.valor


class _Estado:
    def __init__(self, T, h, s, x):
        self.T, self.h, self.s, self.x = T, h, s, x


class _Resultado(dict):
    """`resultado` de `resolver_ciclo` reducido a lo que B lee (subscripTABLE)."""

    def __init__(self, e3, e4):
        super().__init__(estados={"e3": e3, "e4": e4})


def _sintetico(h3=1600.0, h4=1400.0, s3=5.5, x3=0.95, eta=0.8):
    """Punto sintético que cumple la relación de `turbina.resolver` al revés."""
    h4s = h3 - (h3 - h4) / eta
    return _Resultado(_Estado(400.0, h3, s3, x3), _Estado(320.0, h4, 0.0, x3)), h4s


def test_una_sola_llamada_al_motor_y_umbral_configurable():
    res, h4s = _sintetico()
    assert verificar_turbina(res, P_baja=1000.0, motor_real=_StubReal(h4s),
                             eta_t=0.8)["verificado"] is True
    stub = _StubReal(h4s - 0.5)                          # 0.5 kJ/kg de diferencia
    assert verificar_turbina(res, P_baja=1000.0, motor_real=stub,
                             eta_t=0.8)["verificado"] is True
    v = verificar_turbina(res, P_baja=1000.0, motor_real=stub, eta_t=0.8,
                          umbral_kJkg=0.4)
    assert v["verificado"] is False
    assert v["dh4s"] == pytest.approx(0.5, abs=1e-12)
    assert stub.llamadas == 2                            # una por llamada, ni una más


def test_camino_de_fallo_del_motor_real_no_inventa_valores():
    res, h4s = _sintetico()
    v = verificar_turbina(res, P_baja=1000.0, eta_t=0.8,
                          motor_real=_StubReal(error=PropertyRangeError("fuera de rango")))
    assert v["verificado"] is None
    assert v["h4s_real"] is None and v["dh4s"] is None
    assert "PropertyRangeError" in v["error"] and "fuera de rango" in v["error"]
    assert v["h4s_teqp"] == pytest.approx(h4s, rel=1e-15)   # el lado teqp sí está
    assert not math.isnan(v["t_real_s"])


def test_fallo_crudo_del_motor_portado_tambien_se_reporta():
    """Los errores crudos del motor portado (no envueltos) no tumban la corrida."""
    res, _ = _sintetico()
    for exc in (RuntimeError("sin cambio de signo"), NotImplementedError("no"),
                ZeroDivisionError("0/0"), OverflowError("exp")):
        v = verificar_turbina(res, P_baja=1000.0, eta_t=0.8,
                              motor_real=_StubReal(error=exc))
        assert v["verificado"] is None
        assert v["error"].startswith(type(exc).__name__)


def test_eta_t_obligatorio_y_positivo_en_la_via_reconstruida():
    res, _ = _sintetico()
    with pytest.raises(ValueError, match="eta_t"):
        verificar_turbina(res, P_baja=1000.0, motor_real=_StubReal(), eta_t=None)
    with pytest.raises(ValueError, match="eta_t"):
        verificar_turbina(res, P_baja=1000.0, motor_real=_StubReal(), eta_t=0.0)
    # Con `backend_teqp` no hace falta `eta_t` (stub: aquí no importa el valor).
    v = verificar_turbina(res, P_baja=1000.0, motor_real=_StubReal(1500.0),
                          backend_teqp=_StubReal(999.0))
    assert v["h4s_teqp_fuente"] == "backend_teqp" and v["h4s_teqp"] == 999.0
    assert v["h4s_real"] == 1500.0 and v["verificado"] is False


def test_modulo_dentro_del_limite_de_120_lineas():
    n = len((_RAIZ / "src/verificacion_motor_real.py").read_text(
        encoding="utf-8").splitlines())
    assert n <= 120, f"verificacion_motor_real.py: {n} lineas"
