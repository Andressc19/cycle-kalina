"""Tests PRIMERO del reintento tolerante de `resolver_ciclo` (RED hoy: la API no existe).

Los 11 casos fijan el comportamiento de `reintento_tolerante`, `max_repliegues` y
`paso_repliegue` (spec en `prompts/TASK_CONTEXT_tests_reintento_tolerante.md`).
Usan un `PropertyBackend` fake (leyes lineales de `tests/test_cycle_solver.py`)
extendido con una subclase que inyecta `PropertyRangeError` (u otra excepción) en
las T elegidas y cuenta las llamadas. Nada de teqp ni motor real: es rápido.

Elección de las T de fallo: el extremo que se rompe (368.0 / 364.0 / 331.0) es un
estado INEXISTENTE de la cascada interna (verificado con medición), así que el
fallo ocurre en la PRIMERA llamada de la evaluación de ese extremo, como en el
caso real (37 de 40 fallos en un extremo).
"""
from __future__ import annotations

import re

import pytest

from src._cycle_loops import CicloNoConvergeError
from src.cycle_solver import resolver_ciclo
from src.properties.adapter import PropertyRangeError
from tests.test_cycle_solver import FakeBackend, _PARAMS_BASE

# Tolerancias justas para comparar eta entre brackets distintos (verificado:
# con las defaults el delta llega a 7e-7; con estas baja a <1e-12).
_TOL = dict(tol_T1=1e-10, tol_T10=1e-8, max_iter_frio=300)
BASE = dict(_PARAMS_BASE, **_TOL)                                # Ts=350, Tf=369
BASE_ANCHO = dict(_PARAMS_BASE, T_sumidero=330.0, T_fuente=365.0, **_TOL)


class BackendQueFalla(FakeBackend):
    """Fake instrumentado: cuenta llamadas y falla en T elegidas.

    `fallos`: T exactas. `bandas`: (T_inf, T_sup) cerradas. `exc`: clase a
    lanzar (para comprobar que solo se tolera `PropertyRangeError`).
    """

    def __init__(self, fallos=(), bandas=(), exc=PropertyRangeError):
        super().__init__()
        self.fallos, self.bandas, self.exc = set(fallos), tuple(bandas), exc
        self.n, self.Ts, self.T_fallos = 0, [], []

    def _chequear(self, T):
        self.n += 1
        self.Ts.append(T)
        if T is None:
            return
        if T in self.fallos or any(a <= T <= b for a, b in self.bandas):
            self.T_fallos.append(T)
            raise self.exc(f"fake: estado no evaluable en T={T:.6g} K")

    def h(self, P, T=None, x=None, s=None, quality=None):
        self._chequear(T)
        return super().h(P, T=T, x=x, s=s, quality=quality)

    def s(self, P, T=None, x=None):
        self._chequear(T)
        return super().s(P, T=T, x=x)

    def equilibrio_liquido_vapor(self, P, T):
        self._chequear(T)
        return super().equilibrio_liquido_vapor(P, T)


class BackendDesplazado(BackendQueFalla):
    """Fake con `T_from_Ph` desplazado `delta` K: F no cambia de signo en el rango."""

    def __init__(self, delta, **kw):
        super().__init__(**kw)
        self.delta = delta

    def T_from_Ph(self, P, h, x=None):
        return super().T_from_Ph(P, h, x=x) + self.delta


def _eta(res):
    return res["eta"]


def _T1(res):
    return res["estados"]["e1"].T


def test_1_sin_flag_identico_bit_a_bit_al_actual():
    be_ref, be = BackendQueFalla(), BackendQueFalla()
    ref = resolver_ciclo(be_ref, **_PARAMS_BASE)              # camino actual
    res = resolver_ciclo(be, **_PARAMS_BASE)                  # flag ausente
    assert _eta(res) == _eta(ref) and _T1(res) == _T1(ref)
    assert set(res) == set(ref) and "reintento_usado" not in res
    assert be.n == be_ref.n


def test_2_flag_sin_fallos_no_reintenta():
    be_ref, be = BackendQueFalla(), BackendQueFalla()
    ref = resolver_ciclo(be_ref, **_PARAMS_BASE)
    res = resolver_ciclo(be, **_PARAMS_BASE, reintento_tolerante=True)
    assert _eta(res) == _eta(ref) and _T1(res) == _T1(ref)
    assert be.n == be_ref.n and be.T_fallos == []
    assert res["reintento_usado"] is False


def test_3_extremo_alto_falla_converge_con_el_mismo_eta():
    ref = resolver_ciclo(BackendQueFalla(), **BASE)
    be = BackendQueFalla(fallos={368.0})                       # extremo hi = Tf-1
    res = resolver_ciclo(be, **BASE, reintento_tolerante=True)
    assert res["reintento_usado"] is True
    assert abs(_eta(res) - _eta(ref)) < 1e-9
    assert abs(_T1(res) - _T1(ref)) < 1e-6
    # el extremo se evalúa en el intento original y en el reintento, y en ambos
    # falla en la PRIMERA llamada (368 K no es estado interno de la cascada)
    assert be.T_fallos == [368.0, 368.0]


def test_4_extremo_bajo_y_ambos_extremos_fallando():
    ref = resolver_ciclo(BackendQueFalla(), **BASE_ANCHO)
    be = BackendQueFalla(fallos={331.0})                       # extremo lo = Ts+1
    res = resolver_ciclo(be, **BASE_ANCHO, reintento_tolerante=True)
    assert res["reintento_usado"] is True
    assert abs(_eta(res) - _eta(ref)) < 1e-9
    assert be.T_fallos == [331.0, 331.0]
    be2 = BackendQueFalla(fallos={331.0, 364.0})              # los dos extremos
    res2 = resolver_ciclo(be2, **BASE_ANCHO, reintento_tolerante=True)
    assert res2["reintento_usado"] is True
    assert abs(_eta(res2) - _eta(ref)) < 1e-9
    assert sorted(be2.T_fallos) == [331.0, 331.0, 364.0]


def test_5_rango_entero_falla_no_converge_y_acota_llamadas():
    mr = 6
    be = BackendQueFalla(bandas=[(300.0, 500.0)])              # nada es evaluable
    with pytest.raises(CicloNoConvergeError):
        resolver_ciclo(be, **BASE, reintento_tolerante=True, max_repliegues=mr)
    # cada intento muere en su primera llamada -> n == nº de extremos intentados
    assert 0 < be.n <= 2 * mr + 4
    assert len(be.T_fallos) <= 2 * mr + 4


def test_6_sin_cambio_de_signo_no_converge():
    be = BackendDesplazado(delta=20.0)                         # F no cambia de signo
    with pytest.raises(CicloNoConvergeError):
        resolver_ciclo(be, **BASE, reintento_tolerante=True)
    assert be.n > 0 and be.T_fallos == []


def test_7_respeta_max_repliegues():
    ref = resolver_ciclo(BackendQueFalla(), **BASE_ANCHO)
    fallos = {364.0, 359.0, 354.0}                            # hi falla 3 veces (paso 5)
    be2 = BackendQueFalla(fallos=fallos)
    with pytest.raises(CicloNoConvergeError):
        resolver_ciclo(be2, **BASE_ANCHO, reintento_tolerante=True, max_repliegues=2)
    assert sorted(set(be2.T_fallos)) == [354.0, 359.0, 364.0]
    assert 349.0 not in be2.Ts                                # tope 2: no hay 4º intento
    be = BackendQueFalla(fallos=fallos)
    res = resolver_ciclo(be, **BASE_ANCHO, reintento_tolerante=True, max_repliegues=3)
    assert res["reintento_usado"] is True
    assert abs(_eta(res) - _eta(ref)) < 1e-9
    assert be.T_fallos[0] == 364.0 and be.T_fallos[1:] == [364.0, 359.0, 354.0]
    assert 349.0 in be.Ts                                     # tope 3: sí llega al 4º


def test_8_paso_repliegue_se_respeta():
    ref = resolver_ciclo(BackendQueFalla(), **BASE)
    be = BackendQueFalla(fallos={368.0})
    res = resolver_ciclo(be, **BASE, reintento_tolerante=True, paso_repliegue=2.0)
    assert be.T_fallos == [368.0, 368.0]
    assert 366.0 in be.Ts and 363.0 not in be.Ts               # repliegue de 2 K, no de 5 K
    assert abs(_eta(res) - _eta(ref)) < 1e-9


def test_9_otra_excepcion_se_propaga_sin_reintento():
    be = BackendQueFalla(fallos={368.0}, exc=ValueError)
    with pytest.raises(ValueError):
        resolver_ciclo(be, **BASE, reintento_tolerante=True)
    assert be.T_fallos == [368.0]                              # no hubo segundo intento


def test_10_punto_interior_no_evaluable_durante_brentq():
    # el extremo 368 falla -> hay reintento; la banda solo la toca un punto
    # INTERIOR de brentq (T=355.555 K medido), nunca la cascada de los extremos.
    be = BackendQueFalla(fallos={368.0}, bandas=[(355.5, 355.6)])
    with pytest.raises(CicloNoConvergeError) as ei:
        resolver_ciclo(be, **BASE, reintento_tolerante=True)
    T_int = be.T_fallos[-1]
    assert 355.5 <= T_int <= 355.6
    nums = [float(x) for x in re.findall(r"\d+\.\d+", str(ei.value))]
    assert any(abs(n - T_int) < 0.05 for n in nums), str(ei.value)


def test_11_el_intento_fallido_no_deja_estado_compartido():
    be1 = BackendQueFalla(fallos={368.0})
    be2 = BackendQueFalla(fallos={368.0})
    r1 = resolver_ciclo(be1, **BASE, reintento_tolerante=True)
    r2 = resolver_ciclo(be2, **BASE, reintento_tolerante=True)
    assert _eta(r1) == _eta(r2) and _T1(r1) == _T1(r2)
    assert be1.n == be2.n and be1.Ts == be2.Ts
    assert r1["reintento_usado"] is True and r2["reintento_usado"] is True