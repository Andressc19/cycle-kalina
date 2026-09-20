"""Tests deterministas del barrido de sensibilidad FINAL de Fase 2.

Cubre las piezas baratas y deterministas (NO corre el solver — lento):
los rangos/counts de los 5 OFAT y la malla 2D (dentro de CAMPOS_CICLO), el
esquema de columnas de los CSV (tabla_barrido + COLUMNAS_DIAG), la logica de
criterio ligante / spot-check con motor real y las factories de backend.
Los modulos viven en un directorio con guiones (no importable por nombre),
asi que se cargan por ruta con importlib (mismo patron que test_b0_scan.py).
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

from src.sensitivity import VARIABLES_BARRIBLES  # noqa: E402
from src.ui_helpers import CAMPOS_CICLO  # noqa: E402

_CARPETA = _RAIZ / "scripts" / "barridos_2026-09-19" / "fase2_libre"


def _cargar(nombre, archivo):
    spec = importlib.util.spec_from_file_location(nombre, _CARPETA / archivo)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


comun = _cargar("comun_sensibilidad", "comun_sensibilidad.py")
ofat = _cargar("ofat_sensibilidad", "ofat_sensibilidad.py")
malla = _cargar("malla_2d", "malla_2d_sensibilidad.py")

_LIMITES = {c.clave: (c.vmin, c.vmax) for c in CAMPOS_CICLO}


# ------------------------------------------------------------------ OFAT ---

def test_ofat_5_barridos_y_count_total_33():
    from src.sensitivity import generar_combinaciones
    assert set(ofat.BARRIDOS) == {"x_b", "P_baja", "eps_cond", "eta_t",
                                  "eps_hrvg"}
    total = sum(len(generar_combinaciones(ofat.especificacion(v)))
                for v in ofat.BARRIDOS)
    assert total == 33


def test_ofat_valores_por_variable_dentro_de_campos_ciclo():
    from src.sensitivity import generar_valores
    esperados = {
        "x_b": [0.35, 0.37, 0.39, 0.41, 0.43, 0.45],
        "P_baja": [400.0, 420.0, 440.0, 460.0, 480.0, 500.0],
        "eps_cond": [0.85, 0.87, 0.89, 0.91, 0.93, 0.95],
        "eta_t": [0.80, 0.82, 0.84, 0.86, 0.88, 0.90],
        "eps_hrvg": [0.80, 0.825, 0.85, 0.875, 0.90, 0.925, 0.95,
                     0.975, 0.99],
    }
    for var, espec in ofat.BARRIDOS.items():
        assert generar_valores(espec) == esperados[var]
        for v in generar_valores(espec):
            assert _LIMITES[var][0] <= v <= _LIMITES[var][1]


def test_ofat_esquema_columnas_tabla_barrido_mas_diag():
    esperado = (list(VARIABLES_BARRIBLES) + ["convergio", "clasificacion",
                                             "eta", "Wnet", "mensaje"]
                + list(comun.COLUMNAS_DIAG))
    # El CSV de un barrido debe tener exactamente ese esquema (verificado
    # sobre la primera fila real si el CSV existe).
    csv = ofat.SALIDAS / "sensibilidad_x_b.csv"
    if not csv.exists():
        pytest.skip("aun no se corrio ofat_sensibilidad.py")
    df = pd.read_csv(csv)
    assert list(df.columns) == esperado


# ----------------------------------------------------------------- malla ---

def test_malla_6x6_36_puntos_dentro_de_campos_ciclo():
    from src.sensitivity import generar_combinaciones
    combos = generar_combinaciones(malla.especificacion())
    assert len(combos) == 36
    for combo in combos:
        assert combo["P_baja"] in malla.P_BAJA_GRID
        assert combo["eps_cond"] in malla.EPS_COND_GRID
        for var, (vmin, vmax) in _LIMITES.items():
            assert vmin <= combo[var] <= vmax, f"{var}={combo[var]} fuera de rango"


def test_malla_esquema_columnas():
    assert list(malla.COLUMNAS)[:5] == ["P_baja", "eps_cond", "clasificacion",
                                        "eta", "O2_margen"]
    csv = malla.CSV
    if not csv.exists():
        pytest.skip("aun no se corrio malla_2d_sensibilidad.py")
    df = pd.read_csv(csv)
    assert list(df.columns) == list(malla.COLUMNAS)
    assert len(df) == 36


# ----------------------------------------------------- logica de margenes ---

def test_ligante_kalina_elige_frontera_mas_cercana():
    m = dict(margen_O1=2.5, margen_O2=1.2, margen_S5=6.0, margen_O5=0.4)
    assert comun.ligante("KALINA", None, m) == ("O2", 1.2)


def test_ligante_no_kalina_usa_falla_principal():
    m = dict(margen_O1=0.15, margen_O2=-0.8, margen_S5=6.0, margen_O5=0.4)
    assert comun.ligante("CORREGIBLE", "O2", m) == ("O2", -0.8)
    assert comun.ligante("INVIABLE", "O3", m) == ("O3", None)


def test_spot_necesario_umbrales():
    m = dict(margen_O1=0.01, margen_O2=3.0, margen_S5=6.0, margen_O5=0.4)
    assert comun.spot_necesario("KALINA", None, m) is True   # O1 a 0.01
    m2 = dict(margen_O1=0.13, margen_O2=1.9, margen_S5=6.0, margen_O5=0.4)
    assert comun.spot_necesario("KALINA", None, m2) is True  # O2 a 1.9 K
    m3 = dict(margen_O1=0.13, margen_O2=3.0, margen_S5=6.0, margen_O5=0.4)
    assert comun.spot_necesario("KALINA", None, m3) is False
    m4 = dict(margen_O1=0.13, margen_O2=-0.8, margen_S5=6.0, margen_O5=0.4)
    assert comun.spot_necesario("CORREGIBLE", "O2", m4) is True
    assert comun.spot_necesario("INVIABLE", "O3", m4) is False


def test_factories_crean_adapters():
    assert comun.importar_teqp().__class__.__name__ == "TeqpAdapter"
    assert comun.importar_real().__class__.__name__ == "AmmoniaWaterAdapter"


# -------------------------------------------------------- CSV registrados ---

def test_csvs_registrados_tienen_esquema_y_clasificaciones_validas():
    validas = {"KALINA", "CORREGIBLE", "NO_CONVERGIO", "INVIABLE",
               "DEGENERADO", "VALIDO_ADVERTENCIA"}
    n = 0
    for var in ofat.BARRIDOS:
        csv = ofat.SALIDAS / f"sensibilidad_{var}.csv"
        if not csv.exists():
            continue
        df = pd.read_csv(csv)
        assert set(df["clasificacion"]) <= validas
        n += len(df)
    if n == 0:
        pytest.skip("aun no hay CSVs de OFAT")
    assert n == 33