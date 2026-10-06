"""Pruebas de `scripts/barrido_final/comun.py` (núcleo de M0/M1).

Solo lógica rápida y determinista: el índice D, las cuatro fórmulas de márgenes
con un backend falso (sin resolver el ciclo) y los conteos de M1. La corrida
real de un punto se prueba aparte con el comando de humo del TASK_CONTEXT.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
for _p in (str(_RAIZ), str(_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import comun  # noqa: E402
from comun import PROFESOR, T_AMB_DISENO, TAU, indice_D, margenes  # noqa: E402


class _Estado:
    """Estado mínimo: a `margenes` solo le importan `.T` (e4/e2) y `.x` (e4)."""

    def __init__(self, T: float, x: float = 0.5) -> None:  # noqa: N803
        self.T, self.x = T, x


class _BackendFalso:
    """Devuelve los números que el test le fije, sin thermodynamics real."""

    def __init__(self, q4: float, q2: float, t_bub: float) -> None:
        self._q = {400.0: q4, 3000.0: q2}   # solo se piden P_baja y P_alta
        self.t_bub = t_bub

    def fase_de(self, P, T, x):                       # noqa: N803 - firma física
        return (self._q[P], self._q[P])

    def bubble_point(self, P, x):                     # noqa: N803
        return self.t_bub


def _res(Wnet=12.5):                                 # noqa: N803 - W es potencia
    return {"estados": {"e2": _Estado(600.0), "e4": _Estado(400.0),
                        "e8": _Estado(300.0)},
            "Wnet": Wnet}


def _combo(**kw):
    return dict(PROFESOR, **kw)


# -- indice_D ----------------------------------------------------------------
def test_indice_D_cero_si_los_margenes_son_positivos():
    m = {"m_O1": 0.05, "m_O2": 3.0, "m_O3": 10.0, "m_O5": 0.1}
    D, viol = indice_D(m)
    assert D == 0.0
    assert set(viol.values()) == {0.0}


def test_indice_D_ejemplo_del_tarea():
    """m_O1 −0.03, m_O2 −2.0, m_O3 +5.0, m_O5 +0.002 -> D = 3/0.01 + 2/1 = 302."""
    m = {"m_O1": -0.03, "m_O2": -2.0, "m_O3": 5.0, "m_O5": 0.002}
    D, viol = indice_D(m)
    assert D == pytest.approx(0.03 / TAU["O1"] + 2.0 / TAU["O2"])
    assert viol == {"viol_O1": pytest.approx(0.03),
                    "viol_O2": pytest.approx(2.0),
                    "viol_O3": 0.0, "viol_O5": 0.0}


def test_indice_D_none_si_falta_un_margen():
    D, viol = indice_D({"m_O1": -0.03, "m_O2": None, "m_O3": 5.0, "m_O5": 0.002})
    assert D is None
    assert viol["viol_O2"] is None
    assert viol["viol_O1"] == pytest.approx(0.03)


def test_indice_D_none_si_falta_la_clave():
    assert indice_D({})[0] is None


def test_indice_D_pesos_tau():
    """O1 pesa 100x más que O2: la misma violación unitaria da D 100 veces mayor."""
    base = {"m_O2": 0.0, "m_O3": 0.0, "m_O5": 0.0}
    assert indice_D({**base, "m_O1": -0.01})[0] == pytest.approx(1.0)
    assert indice_D({**base, "m_O1": 0.0, "m_O2": -0.01})[0] == pytest.approx(0.01)


# -- margenes ----------------------------------------------------------------
def test_margenes_las_cuatro_formulas(monkeypatch):
    b = _BackendFalso(q4=0.87, q2=0.5004, t_bub=310.0)
    monkeypatch.setattr(comun.condensador, "resolver",
                        lambda e8, be, **kw: (_Estado(309.0),))
    m = margenes(b, _res(Wnet=12.5), _combo())
    assert m["q4"] == 0.87
    assert m["m_O1"] == pytest.approx(0.87 - 0.90)
    assert m["T9_amb"] == 309.0
    assert m["T_bub"] == 310.0
    assert m["m_O2"] == pytest.approx(1.0)
    assert m["m_O3"] == 12.5
    assert m["q2"] == 0.5004
    assert m["m_O5"] == pytest.approx(min(0.5004 - 0.001, 0.999 - 0.5004))
    assert m["err_margenes"] is None
    D, _ = indice_D(m)
    assert D is not None


def test_margenes_m_O5_toma_el_minimo_de_los_dos_lados(monkeypatch):
    b = _BackendFalso(q4=0.87, q2=0.9995, t_bub=310.0)   # q2 pegado a 1
    monkeypatch.setattr(comun.condensador, "resolver",
                        lambda e8, be, **kw: (_Estado(309.0),))
    assert margenes(b, _res(), _combo())["m_O5"] == pytest.approx(-0.0005)
    b2 = _BackendFalso(q4=0.87, q2=0.0005, t_bub=310.0)  # q2 pegado a 0
    assert margenes(b2, _res(), _combo())["m_O5"] == pytest.approx(-0.0005)


def test_margenes_o2_usa_el_piso_de_diseno_no_el_sumidero(monkeypatch):
    """Con T_sumidero < T_AMB_DISENO manda el piso de diseño (300.032917 K)."""
    visto = {}

    def _resolutor(e8, be, **kw):
        visto.update(kw)
        return (_Estado(309.0),)

    monkeypatch.setattr(comun.condensador, "resolver", _resolutor)
    b = _BackendFalso(q4=0.87, q2=0.5, t_bub=310.0)
    margenes(b, _res(), _combo(T_sumidero=280.0))
    assert visto["T_sumidero"] == T_AMB_DISENO
    margenes(b, _res(), _combo(T_sumidero=320.0))
    assert visto["T_sumidero"] == 320.0


def test_margenes_un_calculo_que_lanza_deja_None_y_anota(monkeypatch):
    def _boom(*a, **k):
        raise RuntimeError("falla de prueba")

    monkeypatch.setattr(comun.condensador, "resolver", _boom)
    b = _BackendFalso(q4=0.87, q2=0.5, t_bub=310.0)
    m = margenes(b, _res(), _combo())
    assert m["T9_amb"] is None
    assert m["m_O2"] is None          # sin T9 no hay m_O2
    assert "T9_amb: RuntimeError: falla de prueba" in m["err_margenes"]
    assert m["m_O1"] == pytest.approx(-0.03)   # lo demás sí se calcula


# -- configuración congelada -------------------------------------------------
def test_configuracion_congelada_de_m0():
    assert PROFESOR["T_fuente"] == 623.15
    assert PROFESOR["P_alta"] == 3000.0 and PROFESOR["P_baja"] == 400.0
    assert PROFESOR["x_b"] == 0.50 and PROFESOR["m_b"] == 1.0
    assert (PROFESOR["eta_t"], PROFESOR["eta_p"]) == (0.85, 0.75)
    assert (PROFESOR["eps_hrvg"], PROFESOR["eps_reg"],
            PROFESOR["eps_cond"]) == (0.85, 0.75, 0.80)
    assert PROFESOR["T_sumidero"] == T_AMB_DISENO == 300.032917
    assert comun.PRESUPUESTO_S == 300
    assert TAU == {"O1": 0.01, "O2": 1.0, "O3": 1.0, "O5": 0.01}


def test_cols_contiene_margenes_y_d():
    for c in ("m_O1", "m_O2", "m_O3", "m_O5", "D", "err_margenes",
              "clasificacion", "convergio", "t_s"):
        assert c in comun.COLS


# -- conteos de M1 -----------------------------------------------------------
def test_m1_construye_42_tareas_y_41_comparables():
    import m1_reproducir_f1 as m1
    t = m1.construir_tareas()
    assert len(t) == 42
    assert len(m1.comparables(t)) == 41
    assert [x["grupo"] for x in t].count("P_alta") == 9
    assert [x["grupo"] for x in t].count("x_b") == 7
    assert [x["grupo"] for x in t].count("T_amb") == 24
    assert [x["motor"] for x in t if x["grupo"] == "base"] == ["teqp", "real"]


def test_m1_las_tareas_cubren_el_enunciado():
    import m1_reproducir_f1 as m1
    t = m1.construir_tareas()
    pa = sorted(x["valor"] for x in t if x["grupo"] == "P_alta")
    xb = sorted(x["valor"] for x in t if x["grupo"] == "x_b")
    assert pa == pytest.approx([2000.0, 2250.0, 2500.0, 2750.0, 3000.0,
                                3250.0, 3500.0, 3750.0, 4000.0])
    assert xb == pytest.approx([0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70])
    assert all(x["hora"] is not None for x in t if x["grupo"] == "T_amb")
    assert all(x["combo"]["P_alta"] == x["valor"] for x in t
               if x["grupo"] == "P_alta")
    assert all(x["combo"]["x_b"] == x["valor"] for x in t if x["grupo"] == "x_b")
    assert all(x["combo"]["T_sumidero"] == x["valor"] for x in t
               if x["grupo"] == "T_amb")
    assert all(x["combo"]["T_fuente"] == 623.15 for x in t)