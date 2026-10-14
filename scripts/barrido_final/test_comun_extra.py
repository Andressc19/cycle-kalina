"""Pruebas rápidas de la columna nueva `extra` de `comun.evaluar_punto`.

Sin motor real: se monkeypatchean `resolver_ciclo`, `evaluar_ciclo`, `margenes`
y `anotar_rango`. Comprueban (a) `COLS_EXTRA` y `_extra`, (b) que con
`extra=False` la fila NO trae columnas extra (no-regresión) y con `extra=True`
sí, y (c) que un punto no convergido deja las columnas extra en `None`.
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
from comun import COLS_EXTRA, PROFESOR, _extra  # noqa: E402

_ESPERADO = (["Qi", "Qout", "Wt", "Wp", "Qreg", "m_v", "m_l", "dh_turb"]
             + [f"T_e{i}" for i in range(1, 11)]
             + [f"h_e{i}" for i in range(1, 11)])


class _E:
    def __init__(self, T, h, m):                       # noqa: N803
        self.T, self.h, self.m = T, h, m


def _res() -> dict:
    e = {f"e{i}": _E(300.0 + i, 1000.0 - i, 1.0 + i) for i in range(1, 11)}
    return {"estados": e, "Qi": 1.0, "Qout": 2.0, "Wt": 3.0, "Wp": 4.0,
            "Qreg": 5.0, "Wnet": 6.0, "eta": 0.07}


def _combo(**kw) -> dict:
    return dict(PROFESOR, **kw)


def _clase(value: str):
    return type("V", (), dict(
        clasificacion=type("C", (), {"value": value})(), fallas=[],
        mensaje_reporte=lambda s: "simulado"))()


def _montar(monkeypatch, val) -> None:
    """Deja `evaluar_punto` corriendo sin motor real ni márgenes."""
    monkeypatch.setattr(comun, "resolver_ciclo", lambda *a, **k: _res())
    monkeypatch.setattr("src.restricciones.evaluar_ciclo", lambda *a, **k: val)
    monkeypatch.setattr(comun, "anotar_rango", lambda f, *a, **k: f)
    monkeypatch.setattr(comun, "margenes", lambda *a, **k: dict.fromkeys(
        comun.MARGENES + ("q4", "q2", "T9_amb", "T_bub")))


# -- COLS_EXTRA / _extra -----------------------------------------------------
def test_cols_extra_nombres_y_orden():
    assert list(COLS_EXTRA) == _ESPERADO
    assert len(COLS_EXTRA) == 28


def test_extra_extrae_energias_caudales_y_estados():
    d = _extra(_res())
    assert (d["Qi"], d["Qout"], d["Wt"], d["Wp"], d["Qreg"]) == (
        1.0, 2.0, 3.0, 4.0, 5.0)
    assert d["m_v"] == _res()["estados"]["e3"].m == 4.0
    assert d["m_l"] == _res()["estados"]["e5"].m == 6.0
    assert d["dh_turb"] == pytest.approx(1.0)          # (997) - (996)
    assert d["T_e1"] == 301.0 and d["h_e10"] == 990.0


# -- evaluar_punto(extra=...) ------------------------------------------------
def test_extra_false_no_trae_columnas_extra(monkeypatch):
    _montar(monkeypatch, _clase("KALINA"))
    f = comun.evaluar_punto(_combo(), motor="real")
    assert not any(c in f for c in COLS_EXTRA)
    assert f["clasificacion"] == "KALINA"


def test_extra_true_anade_las_columnas_extra(monkeypatch):
    _montar(monkeypatch, _clase("KALINA"))
    f = comun.evaluar_punto(_combo(), motor="real", extra=True)
    assert all(c in f for c in COLS_EXTRA)
    assert f["Qi"] == 1.0 and f["T_e1"] == 301.0 and f["m_v"] == 4.0


def test_extra_true_no_convergido_deja_las_columnas_en_None(monkeypatch):
    def _boom(*a, **k):
        raise comun.CicloNoConvergeError("prueba")

    monkeypatch.setattr(comun, "resolver_ciclo", _boom)
    monkeypatch.setattr(comun, "anotar_rango", lambda f, *a, **k: f)
    f = comun.evaluar_punto(_combo(), motor="real", extra=True)
    assert f["clasificacion"] == "NO_CONVERGIO"
    assert all(f[c] is None for c in COLS_EXTRA)
