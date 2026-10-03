"""Tests PRIMERO del bracket tolerante MA de `resolver_ciclo` (RED hoy: la API no existe).

Fijan los 15 casos de `prompts/TASK_CONTEXT_tests_ma.md` con el andamiaje calibrado de
`tests/test_reintento_tolerante.py` (OBSOLETO_MB) sobre el `FakeBackend` de
`tests/test_cycle_solver.py`: tol_T1=1e-10 / tol_T10=1e-8 (con las defaults el delta
entre brackets llega a 7e-7) y `nF` = llamadas espiadas a `src.cycle_solver.evaluar`
menos 1 (la ultima, con T1 ya resuelto, no es de F).
"""
from __future__ import annotations

import math
import re
import time

import pytest
from src import cycle_solver as cs
from src._cycle_loops import CicloNoConvergeError, evaluar
from src.cycle_solver import resolver_ciclo
from src.properties.adapter import PropertyRangeError
from tests.test_cycle_solver import FakeBackend, _PARAMS_BASE

_TOL = dict(tol_T1=1e-10, tol_T10=1e-8, max_iter_frio=300)
BASE = dict(_PARAMS_BASE, **_TOL)                                    # Ts=350 Tf=369
ANCHO = dict(_PARAMS_BASE, T_sumidero=330.0, T_fuente=365.0, **_TOL)  # [331, 364]
_KW = {k: v for k, v in BASE.items() if k != "tol_T1"}                # para `evaluar`
_LO, _HI = 351.0, 368.0                                              # extremos de BASE

class BackendQueFalla(FakeBackend):
    """Fake instrumentado: cuenta llamadas y falla en las T elegidas. `fallos`: T
    exactas; `bandas`: (T_inf, T_sup) cerradas; `exc`: clase a lanzar (solo se tolera
    `PropertyRangeError`); `delta`: corrimiento de `T_from_Ph` para que F no cambie de
    signo. T=None no se filtra: en el caso real 37 de 40 fallos mueren en la 1a llamada."""

    def __init__(self, fallos=(), bandas=(), exc=PropertyRangeError, delta=0.0):
        super().__init__()
        self.fallos, self.bandas = set(fallos), tuple(bandas)
        self.exc, self.delta = exc, delta
        self.n, self.Ts, self.T_fallos = 0, [], []

    def _chequear(self, T):
        self.n += 1
        self.Ts.append(T)
        if T is not None and (T in self.fallos or any(a <= T <= b for a, b in self.bandas)):
            self.T_fallos.append(T)
            raise self.exc(f"fake: estado no evaluable en T={T:.6g} K")

    def h(self, P, T=None, x=None, s=None, quality=None):
        self._chequear(T); return FakeBackend.h(self, P, T=T, x=x, s=s, quality=quality)

    def s(self, P, T=None, x=None):
        self._chequear(T); return FakeBackend.s(self, P, T=T, x=x)

    def T_from_Ph(self, P, h, x=None):
        return FakeBackend.T_from_Ph(self, P, h, x=x) + self.delta

    def equilibrio_liquido_vapor(self, P, T):
        self._chequear(T); return FakeBackend.equilibrio_liquido_vapor(self, P, T)

_eta, _T1 = (lambda r: r["eta"]), (lambda r: r["estados"]["e1"].T)    # noqa: E731

def _falla(exc, *a, **kw):
    with pytest.raises(exc): resolver_ciclo(*a, **kw)

def _espia_F(monkeypatch, be=None):
    orig, marcas = cs.evaluar, []                                   # espia `evaluar`
    def espia(*a, **kw): marcas.append(be.n if be is not None else None); return orig(*a, **kw)
    monkeypatch.setattr(cs, "evaluar", espia)
    return marcas

def _n_evaluacion_completa():
    ns = []                                                          # cascada completa
    for T10 in (351.0, 355.0, 355.5):
        be = BackendQueFalla(); evaluar(_LO, be, **_KW, T10_inicial=T10); ns.append(be.n)
    return min(ns)

def test_1_sin_flag_identico_bit_a_bit_al_actual():
    be_ref, be = BackendQueFalla(), BackendQueFalla()
    ref, res = resolver_ciclo(be_ref, **_PARAMS_BASE), resolver_ciclo(be, **_PARAMS_BASE)
    assert _eta(res) == _eta(ref) and _T1(res) == _T1(ref) and be.n == be_ref.n
    assert set(res) == set(ref) and "bracket" not in res

def test_2_flag_sin_fallos_mismo_eta_T1_y_mismo_nF(monkeypatch):
    marcas = _espia_F(monkeypatch)
    ref = resolver_ciclo(BackendQueFalla(), **BASE); n_ref = len(marcas)
    res = resolver_ciclo(BackendQueFalla(), **BASE, bracket_tolerante=True)
    br = res["bracket"]
    assert abs(_eta(res) - _eta(ref)) < 1e-9 and abs(_T1(res) - _T1(ref)) < 1e-9
    assert (n_ref, len(marcas) - n_ref, br["nF"]) == (10, 10, 9)
    assert (br["lo"], br["hi"], br["repliegues_lo"], br["repliegues_hi"]) == (_LO, _HI, 0, 0)

def test_3_extremo_alto_falla_converge_con_el_mismo_eta():
    ref = resolver_ciclo(BackendQueFalla(), **BASE)
    be = BackendQueFalla(fallos={_HI})                        # extremo hi = Tf-1
    res = resolver_ciclo(be, **BASE, bracket_tolerante=True)
    br = res["bracket"]
    assert abs(_eta(res) - _eta(ref)) < 1e-9 and abs(_T1(res) - _T1(ref)) < 1e-9
    assert (br["hi"], br["repliegues_hi"], br["repliegues_lo"]) == (363.0, 1, 0) and be.T_fallos == [_HI]

def test_4_extremo_bajo_falla_y_ambos_extremos_fallando():
    ref = resolver_ciclo(BackendQueFalla(), **ANCHO)
    lo, hi = 331.0, 364.0                                     # extremos de ANCHO
    res = resolver_ciclo(BackendQueFalla(fallos={lo}), **ANCHO, bracket_tolerante=True)
    br = res["bracket"]
    assert abs(_eta(res) - _eta(ref)) < 1e-9 and br["hi"] == hi and br["repliegues_lo"] >= 1
    res2 = resolver_ciclo(BackendQueFalla(fallos={lo, hi}), **ANCHO, bracket_tolerante=True)
    b2 = res2["bracket"]
    assert abs(_eta(res2) - _eta(ref)) < 1e-9 and b2["repliegues_hi"] >= 1 and b2["lo"] > lo

def test_5_rango_entero_falla_no_converge_y_acota_llamadas():
    be = BackendQueFalla(bandas=[(300.0, 500.0)])            # nada es evaluable
    _falla(CicloNoConvergeError, be, **BASE, bracket_tolerante=True)
    tope = 2 * math.ceil((_HI - _LO) / 5.0) + 4   # 2 intentos/extremo; la 1a llamada muere
    assert 0 < be.n <= tope and 0 < len(be.T_fallos) <= tope and max(be.T_fallos) <= _HI

def test_6_sin_cambio_de_signo_no_converge():
    be = BackendQueFalla(delta=20.0)                          # F no cambia de signo
    _falla(CicloNoConvergeError, be, **BASE, bracket_tolerante=True)
    assert be.n > 0 and be.T_fallos == []                    # fallo de bracket, no backend

def test_7_respeta_max_repliegues():
    ref, fallos = resolver_ciclo(BackendQueFalla(), **ANCHO), {364.0, 359.0, 354.0}
    _falla(CicloNoConvergeError, BackendQueFalla(fallos=fallos), **ANCHO,
           bracket_tolerante=True, max_repliegues=2)         # tope 2 -> 3 intentos
    be = BackendQueFalla(fallos=fallos)
    res = resolver_ciclo(be, **ANCHO, bracket_tolerante=True, max_repliegues=3)
    assert abs(_eta(res) - _eta(ref)) < 1e-9 and res["bracket"]["repliegues_hi"] == 3
    assert 349.0 in be.Ts and be.T_fallos == [364.0, 359.0, 354.0]

def test_8_por_defecto_no_hay_tope_de_repliegues():
    ref = resolver_ciclo(BackendQueFalla(), **BASE)
    fallos = {_HI - i for i in range(12)}                     # 368..357 K fallan
    be = BackendQueFalla(fallos=fallos)
    res = resolver_ciclo(be, **BASE, bracket_tolerante=True, paso_repliegue=1.0)
    assert res["bracket"]["repliegues_hi"] == 12 and be.T_fallos == [_HI - i for i in range(12)]
    assert 356.0 in be.Ts and abs(_eta(res) - _eta(ref)) < 1e-9
    _falla(CicloNoConvergeError, BackendQueFalla(fallos=fallos), **BASE,
           bracket_tolerante=True, paso_repliegue=1.0, max_repliegues=6)   # tope 6 no da

def test_9_paso_repliegue_se_respeta():
    be = BackendQueFalla(fallos={_HI})
    br = resolver_ciclo(be, **BASE, bracket_tolerante=True, paso_repliegue=2.0)["bracket"]
    assert be.T_fallos == [_HI] and 366.0 in be.Ts and 363.0 not in be.Ts   # paso de 2 K
    assert br["hi"] == 366.0 and br["repliegues_hi"] == 1

def test_10_otra_excepcion_se_propaga_sin_reintento():
    be = BackendQueFalla(fallos={_HI}, exc=ValueError)
    _falla(ValueError, be, **BASE, bracket_tolerante=True)
    assert be.T_fallos == [_HI]                              # no hubo segundo intento

def test_11_punto_interior_no_evaluable_durante_brentq():
    # 368 repliega a 363; la banda solo la toca un punto INTERIOR de brentq
    # (T=355.555093 K medido con el prototipo), nunca la cascada de los extremos.
    be = BackendQueFalla(fallos={_HI}, bandas=[(355.5, 355.6)])
    with pytest.raises(CicloNoConvergeError) as ei:
        resolver_ciclo(be, **BASE, bracket_tolerante=True)
    T_int, nums = be.T_fallos[-1], [float(x) for x in re.findall(r"\d+\.\d+", str(ei.value))]
    assert 355.5 <= T_int <= 355.6 and any(abs(n - T_int) < 0.05 for n in nums)

def test_12_presupuesto_de_tiempo_agota(monkeypatch):
    be = BackendQueFalla()
    marcas = _espia_F(monkeypatch, be)                        # llamadas al backend hechas
    monkeypatch.setattr(time, "perf_counter", lambda: be.n * 10.0)   # 10 s por llamada
    with pytest.raises(CicloNoConvergeError) as ei:
        resolver_ciclo(be, **BASE, bracket_tolerante=True, presupuesto_s=5.0)
    msg = str(ei.value)
    assert "presupuesto de tiempo agotado" in msg
    assert marcas and sum(1 for m in marcas if m > 1) <= 1   # <=1 evaluacion posterior
    assert be.n >= _n_evaluacion_completa()                  # no corta a mitad de una
    assert any(abs(int(x) - len(marcas)) <= 1 for x in re.findall(r"\d+", msg))

def test_13_presupuesto_none_o_muy_grande_no_cambia_el_resultado():
    base = resolver_ciclo(BackendQueFalla(), **BASE, bracket_tolerante=True)
    for pres in (None, 1e9):
        res = resolver_ciclo(BackendQueFalla(), **BASE, bracket_tolerante=True,
                             presupuesto_s=pres)
        assert _eta(res) == _eta(base) and _T1(res) == _T1(base) and res["bracket"] == base["bracket"]

def test_14a_sin_flag_no_hay_estado_compartido():
    be1, be2 = BackendQueFalla(), BackendQueFalla()
    r1, r2 = resolver_ciclo(be1, **_PARAMS_BASE), resolver_ciclo(be2, **_PARAMS_BASE)
    assert _eta(r1) == _eta(r2) and _T1(r1) == _T1(r2) and be1.n == be2.n
    _falla(PropertyRangeError, BackendQueFalla(fallos={364.0}), **ANCHO)  # fallida
    be3 = BackendQueFalla()
    r3 = resolver_ciclo(be3, **_PARAMS_BASE)                 # no contamina la siguiente
    assert _eta(r3) == _eta(r1) and _T1(r3) == _T1(r1) and be3.n == be1.n

def test_14b_llamada_fallida_con_el_flag_no_contamina_la_siguiente():
    be1 = BackendQueFalla(bandas=[(300.0, 500.0)])           # se agota el rango
    _falla(CicloNoConvergeError, be1, **BASE, bracket_tolerante=True)
    ref = resolver_ciclo(BackendQueFalla(), **BASE, bracket_tolerante=True)
    be2 = BackendQueFalla()
    res = resolver_ciclo(be2, **BASE, bracket_tolerante=True)
    assert be1.n > 0 and _eta(res) == _eta(ref) and res["bracket"] == ref["bracket"]

def test_15_clave_bracket_solo_con_el_flag_y_coherente():
    assert "bracket" not in resolver_ciclo(BackendQueFalla(), **_PARAMS_BASE)
    be = BackendQueFalla(fallos={_HI})
    br = resolver_ciclo(be, **BASE, bracket_tolerante=True)["bracket"]
    assert set(br) == {"lo", "hi", "repliegues_lo", "repliegues_hi", "nF"}
    assert (br["lo"], br["hi"], br["repliegues_lo"], br["repliegues_hi"]) == (351.0, 363.0, 0, 1)
    assert br["nF"] >= 2 and {351.0, _HI, 363.0} <= set(be.Ts)     # coherente con las T