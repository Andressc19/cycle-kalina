"""Tests de la lógica de apoyo del escaneo B0 (caso cementera).

Cubre las piezas deterministas que el escaneo usa (rejillas, calibración de
P_baja contra bubble_point, anotación de la sonda del bracket). NO corre el
escaneo completo (352 puntos, lento): eso es responsabilidad de ejecutar
`b0_scan_cementera.py`.

Usa TeqpAdapter (rápido, validado al <0.01% en saturación contra el motor
real) para la calibración de P_baja. Mismas constantes que el script. El
módulo a probar vive en un directorio con guiones (no importable por nombre),
así que se carga por ruta con importlib.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from src.properties.adapter import PropertyRangeError
from src.properties.teqp_adapter import TeqpAdapter

_RAIZ = Path(__file__).resolve().parents[2]  # script vive en scripts/barridos_2026-09-19/
if str(_RAIZ) not in sys.path:
    sys.path.insert(0, str(_RAIZ))

_RUTA_B0 = (_RAIZ / "scripts" / "barridos_2026-09-19"
            / "b0_scan_cementera.py")
_spec = importlib.util.spec_from_file_location("b0_scan_cementera", _RUTA_B0)
b0 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(b0)

T_OBJ = b0.T_SUMIDERO + b0.DT_COND  # 303.032917 K


@pytest.fixture(scope="module")
def backend():
    return TeqpAdapter(x=0.5)


def test_rejillas():
    p = b0.rejilla_p_alta()
    assert p == [2000.0, 2500.0, 3000.0, 3500.0, 4000.0, 4500.0,
                 5000.0, 5500.0, 6000.0, 6500.0, 7000.0]
    assert len(p) == 11
    x = b0.rejilla_x_b()
    assert x == [0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]
    assert len(x) == 8
    assert len(b0.EPS_GRID) == 4
    # 11 x 8 x 4 = 352 puntos (tope del TASK_CONTEXT: 300-400)
    assert 11 * 8 * len(b0.EPS_GRID) == 352
    assert 300 <= 352 <= 400


def test_calibrar_p_baja_raiz_dentro_de_campos_ciclo(backend):
    for xb in (0.35, 0.50, 0.70):
        pb, modo = b0.calibrar_p_baja(backend, xb)
        assert modo == "raiz"
        assert b0.P_BAJA_MIN <= pb <= b0.P_BAJA_MAX
        bubble = backend.bubble_point(pb, xb)
        assert abs(bubble - T_OBJ) < 1e-3  # objetivo a 1 mK
    # Referencia del caso heredado: x_b=0.6 -> ~575-585 kPa
    pb60, _ = b0.calibrar_p_baja(backend, 0.60)
    assert abs(pb60 - 575.7) < 5.0


def test_anotar_sonda_sobrecalentado(backend):
    # sonda a 582.7 K en P_alta=4000, x_b=0.6: dew=475.2 K -> sobrecalentado
    bub = backend.bubble_point(4000.0, 0.6)
    dew = backend.dew_point(4000.0, 0.6)
    an = b0.anotar_sonda(bub, dew, 582.7)
    assert "sobrecalentado" in an


def test_anotar_sonda_liquido(backend):
    # sonda a 442 K en P_alta=7000, x_b=0.35: bubble=472 K -> liquido
    bub = backend.bubble_point(7000.0, 0.35)
    dew = backend.dew_point(7000.0, 0.35)
    an = b0.anotar_sonda(bub, dew, 442.0)
    assert "liquido" in an


def test_anotar_sonda_dentro_de_campana_sospechosa(backend):
    # T2 dentro de la campana: 430 K a P=4000, x=0.6 (bubble 385, dew 475)
    bub = backend.bubble_point(4000.0, 0.6)
    dew = backend.dew_point(4000.0, 0.6)
    an = b0.anotar_sonda(bub, dew, 430.0)
    assert "DENTRO de campana" in an
    assert "SOSPECHOSO" in an


def test_mensaje_fallo_parsea_t_de_la_excepcion(backend):
    exc = PropertyRangeError(
        "equilibrio_liquido_vapor(P=4000.0 kPa, T=582.9499 K): no existe "
        "equilibrio bifásico para ninguna composición")
    bub = backend.bubble_point(4000.0, 0.60)
    dew = backend.dew_point(4000.0, 0.60)
    msg = b0.mensaje_fallo(exc, 4000.0, 575.7, bub, dew)
    assert "bracket_sonda" in msg
    assert "sobrecalentado" in msg
    assert "582.9" in msg


def test_mensaje_fallo_lado_frio_p_baja(backend):
    # Estado del lado frio (P_baja): fallo de cobertura del motor teqp, NO
    # debe clasificarse como sonda de campana aunque la T este en el mensaje.
    exc = PropertyRangeError(
        "T_from_Ph(P, h, x): el motor teqp no cubre el estado pedido (ver "
        "TASK_CONTEXT 2026-09-18-validar-teqp-nh3h2o). Detalle: equilibrio no "
        "resoluble en T=290.75 K, P=1.5789e+05 Pa, x=0.0813")
    bub = backend.bubble_point(2000.0, 0.35)
    dew = backend.dew_point(2000.0, 0.35)
    msg = b0.mensaje_fallo(exc, 2000.0, 157.9, bub, dew)
    assert "lado_frio" in msg
    assert "P_baja=157.9" in msg
    assert "290.75" in msg
    assert "bracket_sonda" not in msg


def test_mensaje_fallo_lazo_frio_no_convergio():
    # CicloNoConvergeError del lazo interior: sin P/T, etiqueta propia.
    msg = b0.mensaje_fallo(
        Exception("lazo interior (frio) no convergio tras max_iter_frio"),
        3500.0, 218.7, 400.0, 480.0)
    assert "lazo_frio_no_conv" in msg
    assert "bracket_sonda" not in msg