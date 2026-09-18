"""Tests del solver del ciclo (lazos de convergencia sobre los 8 componentes).

Usa un `PropertyBackend` fake determinista (leyes lineales, mismo estilo que
`test_components.py`):

    h = T + 10·x + 1e-3·P ;   s = 0.01·T + x
    T_from_Ph = h − 10·x − 1e-3·P ;   T_from_Ps = 100·(s − x)
    bubble_point = 400 − 100·x ;   dew_point = 420 − 100·x
    equilibrio_liquido_vapor = ((400 − T)/100, (420 − T)/100)  # inversa de las dos

y un caso base con parámetros elegidos para que todo el rango físico de T1
(T_sumidero+1, T_fuente−1) quepa DENTRO de la campana bifásica del fake a
x=0.5 (burbuja 350 K, rocío 370 K): T_sumidero=350, T_fuente=369 → bracket
[351, 368] evaluable en todo su rango y con cambio de signo en F.

El caso real (AmmoniaWaterAdapter con los valores por defecto de CONTEXT.md)
no se mockea: se ejecuta y se reporta en la respuesta final del task (los
tests unitarios del solver usan fakes, como manda CONTEXT.md §"Arquitectura").
"""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from src._cycle_loops import CicloNoConvergeError, _bracketear, evaluar
from src.cycle_solver import resolver_ciclo
from src.properties.adapter import PropertyBackend, PropertyRangeError
from src.state import EstadoTermo

_RAIZ = Path(__file__).resolve().parents[1]

# Caso base del fake: bracket [351, 368] dentro de la campana (350, 370) a x=0.5.
_PARAMS_BASE = dict(P_alta=3000.0, P_baja=400.0, T_fuente=369.0,
                    T_sumidero=350.0, x_b=0.5, m_b=1.0, eta_t=0.85,
                    eta_p=0.75, eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.80)


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


def test_resolver_ciclo_converge_y_devuelve_esquema_completo(backend):
    res = resolver_ciclo(backend, **_PARAMS_BASE)
    assert set(res) == {"estados", "Qi", "Qout", "Wt", "Wp", "Qreg", "Wnet",
                        "eta"}
    estados = res["estados"]
    assert set(estados) == {f"e{i}" for i in range(1, 11)}
    for i, clave in enumerate((f"e{i}" for i in range(1, 11)), start=1):
        assert estados[clave].etiqueta == str(i)
        assert isinstance(estados[clave], EstadoTermo)
    # Masas coherentes: el reparto del separador reconstruye m_b y absorbedor
    # + condensador + bomba llevan siempre m_b.
    assert estados["e3"].m + estados["e5"].m == pytest.approx(1.0)
    for clave in ("e8", "e9", "e10"):
        assert estados[clave].m == pytest.approx(1.0)
    assert estados["e8"].x == pytest.approx(0.5)


def test_resolver_ciclo_balance_global_y_eta(backend):
    res = resolver_ciclo(backend, **_PARAMS_BASE)
    # 1er principio con la convención documentada: Qi + Wp = Qout + Wt.
    lhs = res["Qi"] + res["Wp"]
    err = abs(lhs - (res["Qout"] + res["Wt"])) / lhs
    assert err < 1e-4
    assert res["Qi"] > 0.0
    # El fake con leyes lineales rinde Wnet < 0 (su bomba consume más que su
    # turbina produce: 1e-3·ΔP/η_p > m_v·η_t·1e-3·ΔP) — artefacto del backend.
    # El criterio 0 < η < 1 se verifica con el backend real (respuesta final).
    assert -1.0 < res["eta"] < 1.0
    # Cierre del regenerador a nivel de ciclo: m_l·(h5−h6) = m_b·(h1−h10).
    # Tolerancia rel 1e-4: es el residuo del lazo exterior (brentq xtol=1e-4 K).
    e = res["estados"]
    assert e["e5"].m * (e["e5"].h - e["e6"].h) == pytest.approx(
        e["e1"].h - e["e10"].h, rel=1e-4)


def test_energias_finitas_y_residuo_del_lazo_exterior(backend):
    res = resolver_ciclo(backend, **_PARAMS_BASE)
    for nombre in ("Qi", "Qout", "Wt", "Wp", "Qreg", "Wnet", "eta"):
        assert math.isfinite(res[nombre])
    # Magnitudes [kW]: calor y trabajo entran/salen en sentidos definidos.
    assert res["Qi"] > 0.0 and res["Wt"] > 0.0 and res["Wp"] >= 0.0
    # Residuo del lazo exterior: F(T1) ≈ 0 en la solución dentro de tol_T1.
    T1_nuevo, _, _ = evaluar(res["estados"]["e1"].T, backend, **_PARAMS_BASE,
                             tol_T10=1e-4, max_iter_frio=300)
    assert abs(T1_nuevo - res["estados"]["e1"].T) < 1e-3


def test_caso_fisicamente_imposible_lanza_ciclo_no_converge(backend):
    # T_fuente < T_sumidero hace degenerado el rango físico -> bracket inviable.
    con_tfuente_baja = dict(_PARAMS_BASE, T_fuente=349.0)
    with pytest.raises(CicloNoConvergeError):
        resolver_ciclo(backend, **con_tfuente_baja)


def test_lazo_interior_sin_convergencia_lanza_ciclo_no_converge(backend):
    # max_iter_frio=0: el lazo interior nunca itera -> conv_frio=False.
    with pytest.raises(CicloNoConvergeError):
        resolver_ciclo(backend, **_PARAMS_BASE, max_iter_frio=0)


def test_propaga_excepcion_real_del_backend_sin_envolver():
    class BackendRoto(FakeBackend):
        def h(self, P, T=None, x=None, s=None, quality=None):
            raise PropertyRangeError("motor no cubre el estado")

    with pytest.raises(PropertyRangeError):
        resolver_ciclo(BackendRoto(), **_PARAMS_BASE)


def test_arranque_tibio_no_cambia_el_resultado(backend):
    # T10_inicial (arranque tibio entre evaluaciones del lazo exterior) es
    # solo una optimización numérica: el punto fijo convergido debe ser el
    # mismo que arrancando de T1_trial.
    r_frio, e_frio, _ = evaluar(360.0, backend, **_PARAMS_BASE,
                                tol_T10=1e-4, max_iter_frio=300,
                                T10_inicial=None)
    r_tibio, e_tibio, _ = evaluar(360.0, backend, **_PARAMS_BASE,
                                  tol_T10=1e-4, max_iter_frio=300,
                                  T10_inicial=375.0)
    assert r_frio == pytest.approx(r_tibio, rel=1e-6)
    for k in ("e6", "e10"):
        # El truncado de la sustitución sucesiva está acotado por tol_T10.
        assert e_frio[k].T == pytest.approx(e_tibio[k].T, abs=1e-4)


def test_evaluar_y_bracketear_privados(backend):
    # evaluar en un T1 del interior del bracket: cascada completa y F acotada.
    T1_nuevo, estados, energias = evaluar(360.0, backend, **_PARAMS_BASE,
                                          tol_T10=1e-4, max_iter_frio=300)
    assert set(estados) == {f"e{i}" for i in range(1, 11)}
    assert set(energias) == {"Qi", "Wt", "Qreg", "Qout", "Wp"}
    assert abs(T1_nuevo - 360.0) < 50.0

    def F(T1):
        T1n, _, _ = evaluar(T1, backend, **_PARAMS_BASE, tol_T10=1e-4,
                            max_iter_frio=300)
        return T1n - T1

    lo, hi = _bracketear(F, 350.0, 369.0)
    assert 350.0 < lo < hi < 369.0
    assert F(lo) * F(hi) <= 0.0


_MODULOS_NUEVOS = ["src/cycle_solver.py", "src/_cycle_loops.py",
                   "tests/test_cycle_solver.py"]


def test_nuevos_archivos_dentro_del_limite_de_200_lineas():
    for ruta in _MODULOS_NUEVOS:
        assert len((_RAIZ / ruta).read_text(encoding="utf-8").splitlines()) <= 200


def test_solver_no_importa_backends_concretos():
    prohibidos = ("iapws", "AmmoniaWaterAdapter", "IAPWSAdapter",
                  "PyfluidsAdapter", "pyfluids", "CoolProp")
    for ruta in _MODULOS_NUEVOS[:2]:
        texto = (_RAIZ / ruta).read_text(encoding="utf-8")
        assert not any(p in texto for p in prohibidos), ruta