"""Constancia del benchmark contra Nemati et al. (2017), Case Stud. Therm. Eng. 9, 1-13
(segunda fuente independiente de KCS11; Tabla 5, 5000/1061 kPa, x_b = 0.90).

Comprueba sobre el resultado GUARDADO (`resultados/2026-10-03_benchmark_nemati/
benchmark_nemati.json`, generado por `scripts/benchmark_nemati2017.py` con el motor real,
~12 min) los criterios con los que se aceptó la comparación. No recalcula el ciclo. Los
umbrales fijan lo medido con margen; reporte: REPORTE_BENCHMARK_NEMATI.md.
"""
import json
from pathlib import Path

import pytest

F = (Path(__file__).resolve().parents[1] / "resultados" / "2026-10-03_benchmark_nemati"
     / "benchmark_nemati.json")
M_A, M_W = 17.03052, 18.015268


def _molar(w):
    return (w / M_A) / (w / M_A + (1 - w) / M_W)


@pytest.fixture(scope="module")
def r():
    if not F.exists():
        pytest.skip("falta benchmark_nemati.json (regenerar con scripts/benchmark_nemati2017.py)")
    return json.loads(F.read_text())


def test_burbuja_condensador(r):
    b = r["Tbub_1061kPa_x090"]
    assert abs(b["motor"] - b["nemati"]) < 1.0


def test_equilibrio_separador(r):
    v = r["VLE_5000kPa_415K"]
    assert abs(_molar(v["x_vap_motor"]) - _molar(v["x_vap_nemati"])) < 0.01   # dentro de G4-01
    assert abs(_molar(v["x_liq_motor"]) - _molar(v["x_liq_nemati"])) < 0.02   # medido 0.014


@pytest.mark.parametrize("estado", ["1", "2", "4", "8", "9", "10"])
def test_temperaturas_de_estado(r, estado):
    dT = r["ciclo_motor"][estado]["T"] - r["nemati"][estado]["T"]
    assert abs(dT) <= 3.0, f"estado {estado}: dT = {dT:+.2f} K"


def test_reparto_del_separador(r):
    assert abs(r["ciclo_motor"]["3"]["m"] - r["fraccion_vapor_masica_nemati"]) < 0.03
