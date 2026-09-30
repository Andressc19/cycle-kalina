"""Tests de la lógica determinista del pre-escaneo de eps_hrvg (Fase 2).

Cubre las piezas baratas y deterministas: la generación de combos (6 puntos,
solo eps_hrvg variado sobre el candidato v2, dentro de CAMPOS_CICLO) y el
esquema de columnas del CSV `prescan_eps_hrvg.csv` (tabla_barrido +
diagnósticos q2/T2/O2). NO corre el solver (lento): eso es responsabilidad
del script `prescan_eps_hrvg.py`.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd
import pytest

_RAIZ = Path(__file__).resolve().parents[3]  # ruta: scripts/.../fase2_libre/
if str(_RAIZ) not in sys.path:
    sys.path.insert(0, str(_RAIZ))

from src.ui_helpers import CAMPOS_CICLO  # noqa: E402  (bounds de la UI)

_RUTA = (_RAIZ / "scripts" / "barridos_2026-09-19" / "fase2_libre"
         / "prescan_eps_hrvg.py")
_spec = importlib.util.spec_from_file_location("fase2_libre_prescan", _RUTA)
f2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f2)

_LIMITES = {c.clave: (c.vmin, c.vmax) for c in CAMPOS_CICLO}


def test_combos_6_puntos_solo_eps_hrvg_variado():
    puntos = f2.combos_eps_hrvg()
    assert len(puntos) == 6
    assert [p["eps_hrvg"] for p in puntos] == [0.70, 0.75, 0.80, 0.85, 0.90,
                                               0.95]
    for p in puntos:
        resto = {k: v for k, v in p.items() if k != "eps_hrvg"}
        resto_esperado = {k: v for k, v in f2.CANDIDATO.items()
                          if k != "eps_hrvg"}
        assert resto == resto_esperado


def test_combos_dentro_de_campos_ciclo():
    for combo in f2.combos_eps_hrvg():
        for var, (vmin, vmax) in _LIMITES.items():
            assert vmin <= combo[var] <= vmax, (
                f"{var}={combo[var]} fuera de [{vmin}, {vmax}]")


def test_esquema_columnas_empieza_por_tabla_barrido():
    from src.sensitivity import VARIABLES_BARRIBLES
    esperado_base = list(VARIABLES_BARRIBLES) + ["convergio", "clasificacion",
                                                 "eta", "Wnet", "mensaje"]
    # Las 16 columnas de tabla_barrido están presentes, en orden, como prefijo
    # del esquema completo (las extra de diagnóstico van en medio, patrón v2).
    sin_extra = [c for c in f2.COLUMNAS if c in esperado_base]
    assert sin_extra == esperado_base


def test_csv_registrado_tiene_esquema_y_6_puntos():
    csv = f2.CSV
    if not csv.exists():
        pytest.skip("el CSV aún no existe (correr prescan_eps_hrvg.py)")
    df = pd.read_csv(csv)
    assert list(df.columns) == f2.COLUMNAS
    assert len(df) == 6
    assert set(df["clasificacion"]) <= {"KALINA", "CORREGIBLE",
                                        "NO_CONVERGIO", "INVIABLE",
                                        "DEGENERADO", "VALIDO_ADVERTENCIA"}
    assert sorted(df["eps_hrvg"]) == list(f2.EPS_HRVG_GRID)