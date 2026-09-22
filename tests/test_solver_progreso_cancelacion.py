"""Tests de la instrumentación del solver (progreso + cancelación cooperativa).

`resolver_ciclo` acepta `progreso` (callback por iteración) y `cancelar`
(`threading.Event`) opcionales para la UI de corrida larga (ver
`src/ui_ejecucion.py`). Con `None` el comportamiento es el histórico (cubierto
por `test_cycle_solver.py`); acá se verifica que con valores no nulos reporta
las iteraciones de ambos lazos y aborta con `CicloCancelado`.
"""

from __future__ import annotations

import threading

import pytest

from src._cycle_loops import CicloCancelado
from src.cycle_solver import resolver_ciclo
from tests.test_cycle_solver import FakeBackend, _PARAMS_BASE


def test_progreso_reporta_iteraciones_exteriores_e_interiores():
    eventos = []
    resolver_ciclo(FakeBackend(), **_PARAMS_BASE, progreso=eventos.append)
    fases = {e["fase"] for e in eventos}
    assert "exterior" in fases and "interior" in fases
    exteriores = [e for e in eventos if e["fase"] == "exterior"]
    assert [e["iteracion"] for e in exteriores] == list(
        range(1, len(exteriores) + 1))
    assert all({"T1", "residual"} <= set(e) for e in exteriores)
    interiores = [e for e in eventos if e["fase"] == "interior"]
    assert all({"T10", "delta"} <= set(e) for e in interiores)


def test_cancelar_activo_aborta_con_ciclo_cancelado():
    cancelar = threading.Event()
    cancelar.set()
    with pytest.raises(CicloCancelado):
        resolver_ciclo(FakeBackend(), **_PARAMS_BASE, cancelar=cancelar)


def test_progreso_no_cambia_el_resultado():
    r_sin = resolver_ciclo(FakeBackend(), **_PARAMS_BASE)
    r_con = resolver_ciclo(FakeBackend(), **_PARAMS_BASE,
                           progreso=lambda _evento: None)
    assert r_sin["eta"] == pytest.approx(r_con["eta"], rel=1e-12)
    assert r_sin["Wnet"] == pytest.approx(r_con["Wnet"], rel=1e-12)
