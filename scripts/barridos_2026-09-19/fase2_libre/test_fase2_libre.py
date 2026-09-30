"""Tests de la lógica determinista de la Fase 2 (búsqueda libre).

Cubre las piezas baratas y deterministas: la generación de combinaciones de la
etapa 1 (dentro de CAMPOS_CICLO, empieza por el punto por defecto exacto) y el
esquema de columnas del CSV `busqueda_libre.csv` (idéntico a `tabla_barrido`).
NO corre el solver (lento): eso es responsabilidad del script 01.

Los módulos viven en un directorio con guiones (no importable por nombre),
así que se cargan por ruta con importlib (mismo patrón que test_b0_scan.py).
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

_RUTA_01 = (_RAIZ / "scripts" / "barridos_2026-09-19" / "fase2_libre"
            / "01_punto_default_y_scan.py")
_spec = importlib.util.spec_from_file_location("fase2_libre_01", _RUTA_01)
f2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f2)

_LIMITES = {c.clave: (c.vmin, c.vmax) for c in CAMPOS_CICLO}


def test_combinaciones_etapa1_vigésimo_por_defecto():
    puntos = f2.combos_etapa1()
    assert len(puntos) == 10
    assert puntos[0] == f2.DEFAULTS  # el punto 0 es el default exacto


def test_combinaciones_etapa1_dentro_de_campos_ciclo():
    for combo in f2.combos_etapa1():
        for var, (vmin, vmax) in _LIMITES.items():
            assert vmin <= combo[var] <= vmax, (
                f"{var}={combo[var]} fuera de [{vmin}, {vmax}]")


def test_esquema_columnas_igual_a_tabla_barrido():
    from src.sensitivity import VARIABLES_BARRIBLES
    esperado = list(VARIABLES_BARRIBLES) + ["convergio", "clasificacion",
                                            "eta", "Wnet", "mensaje"]
    assert f2.COLUMNAS == esperado


def test_csv_registrado_tiene_esquema_y_10_puntos():
    csv = f2.CSV
    if not csv.exists():
        pytest.skip("el CSV aún no existe (correr 01_punto_default_y_scan.py)")
    df = pd.read_csv(csv)
    assert list(df.columns) == f2.COLUMNAS
    assert len(df) == 10
    assert set(df["clasificacion"]) <= {"KALINA", "CORREGIBLE",
                                        "NO_CONVERGIO", "INVIABLE",
                                        "DEGENERADO", "VALIDO_ADVERTENCIA"}