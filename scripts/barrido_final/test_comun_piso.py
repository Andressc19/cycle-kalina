"""Pruebas del piso de O2 por punto (TASK_CONTEXT final_M2S, paso 1).

Tres comportamientos pedidos, con backend falso y el ciclo mockeado (aquí no
se resuelve ningún punto real): (1) el default no cambia — sin
`t_amb_diseno` manda `T_AMB_DISENO`; (2) con `t_amb_diseno=283.15` y
`T_sumidero=278.15` manda 283.15; (3) si `T_sumidero` supera al piso, manda
`T_sumidero`.
"""

from __future__ import annotations

import sys
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
for _p in (str(_RAIZ), str(_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import comun  # noqa: E402
from comun import PROFESOR, T_AMB_DISENO, margenes  # noqa: E402


class _Estado:
    """Estado mínimo: a `margenes` solo le importan `.T` (e4/e2) y `.x` (e4)."""

    def __init__(self, T: float, x: float = 0.5) -> None:  # noqa: N803
        self.T, self.x = T, x


class _BackendFalso:
    """Devuelve los números que el test le fije, sin thermodynamics real."""

    def __init__(self, q4: float = 0.87, q2: float = 0.5,
                 t_bub: float = 310.0) -> None:
        self._q = {400.0: q4, 3000.0: q2}   # solo se piden P_baja y P_alta
        self.t_bub = t_bub

    def fase_de(self, P, T, x):                       # noqa: N803 - firma física
        return (self._q[P], self._q[P])

    def bubble_point(self, P, x):                     # noqa: N803
        return self.t_bub


def _res(Wnet=12.5):                                 # noqa: N803 - W es potencia
    return {"estados": {"e2": _Estado(600.0), "e4": _Estado(400.0),
                        "e8": _Estado(309.0)},
            "Wnet": Wnet}


def _combo(**kw):
    return dict(PROFESOR, **kw)


def _valor(clase: str, codigos=()):
    """`evaluar_ciclo` falso con la clasificación dada."""
    return type("V", (), {
        "clasificacion": type("C", (), {"value": clase})(),
        "fallas": [type("F", (), {"codigo": c})() for c in codigos],
        "mensaje_reporte": lambda s: "simulado"})()


def _piso_que_llega_al_condensador(monkeypatch, t_sum: float,
                                   t_amb_diseno=None) -> float:
    """Piso real que `margenes` le pasa al condensador: `max(T_sumidero, piso)`."""
    visto = {}

    def _resol(e8, be, **kw):
        visto["T"] = kw["T_sumidero"]
        return (_Estado(309.0),)

    monkeypatch.setattr(comun.condensador, "resolver", _resol)
    margenes(_BackendFalso(), _res(), _combo(T_sumidero=t_sum),
             t_amb_diseno=t_amb_diseno)
    return visto["T"]


def _ciclo_mockeado(monkeypatch, visto: dict) -> None:
    """Ciclo resuelto y clasificado a mano, capturando el piso de O2."""
    def _resol(e8, be, **kw):
        visto["T_cond"] = kw["T_sumidero"]
        return (_Estado(309.0),)

    monkeypatch.setattr(comun.condensador, "resolver", _resol)
    monkeypatch.setattr(comun, "resolver_ciclo",
                        lambda *a, **k: {**_res(), "eta": 0.07})
    monkeypatch.setattr(comun, "anotar_rango", lambda f, *a, **k: f)

    def _eval(backend, res, **crit):
        visto["crit"] = dict(crit)
        return _valor("KALINA")

    monkeypatch.setattr("src.restricciones.evaluar_ciclo", _eval)


# -- 1. el default no cambia --------------------------------------------------
def test_default_margenes_sigue_usando_T_AMB_DISENO(monkeypatch):
    assert _piso_que_llega_al_condensador(monkeypatch, t_sum=278.15) == T_AMB_DISENO
    assert _piso_que_llega_al_condensador(monkeypatch, t_sum=320.0) == 320.0


def test_default_evaluar_punto_guarda_T_AMB_DISENO(monkeypatch):
    visto = {}
    _ciclo_mockeado(monkeypatch, visto)
    f = comun.evaluar_punto(_combo(T_sumidero=278.15), motor="real", tag="def")
    assert visto["crit"]["T_amb_diseno"] == T_AMB_DISENO
    assert visto["T_cond"] == T_AMB_DISENO
    assert f["T_amb_diseno"] == T_AMB_DISENO


def test_T_amb_diseno_esta_en_COLS():
    assert "T_amb_diseno" in comun.COLS


# -- 2. piso propio por punto -------------------------------------------------
def test_piso_283_con_sumidero_278_manda_el_piso(monkeypatch):
    assert _piso_que_llega_al_condensador(monkeypatch, t_sum=278.15,
                                          t_amb_diseno=283.15) == 283.15


def test_evaluar_punto_pasa_su_piso_a_evaluar_ciclo_y_a_margenes(monkeypatch):
    visto = {}
    _ciclo_mockeado(monkeypatch, visto)
    f = comun.evaluar_punto(_combo(T_sumidero=278.15), motor="real",
                            t_amb_diseno=283.15)
    assert visto["crit"]["T_amb_diseno"] == 283.15
    assert visto["T_cond"] == 283.15
    assert f["T_amb_diseno"] == 283.15


# -- 3. el sumidero manda si supera al piso -----------------------------------
def test_sumidero_mayor_que_el_piso_manda_el_sumidero(monkeypatch):
    assert _piso_que_llega_al_condensador(monkeypatch, t_sum=293.15,
                                          t_amb_diseno=283.15) == 293.15


def test_sumidero_mayor_que_el_piso_tambien_en_evaluar_punto(monkeypatch):
    visto = {}
    _ciclo_mockeado(monkeypatch, visto)
    f = comun.evaluar_punto(_combo(T_sumidero=300.032917), motor="real",
                            t_amb_diseno=283.15)
    assert visto["crit"]["T_amb_diseno"] == 283.15      # el piso del punto
    assert visto["T_cond"] == 300.032917                # el condensador, el sitio
    assert f["T_amb_diseno"] == 283.15
