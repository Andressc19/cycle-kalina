"""Tests del barrido de sensibilidad FINAL Fase 3 (Husavik).

Cubren lo que se puede probar sin correr los 71 puntos completos del barrido:
la definicion de las rejillas (5 OFAT de 7 + malla 2D de 36), la regla del
criterio ligante, el esquema de columnas de los CSV, y una prueba de humo con
TeqpAdapter del punto ancla (una sola resolucion, ~segundos).

Los puntos de la malla 2D quedan cerrando el rango: 6x6 = 36 combinaciones.
"""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

from src.sensitivity import Barrido, Fijo, generar_combinaciones, \
    generar_valores

_RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_RAIZ))

_RUTA_COMUN = _RAIZ / "scripts" / "barridos_2026-09-19" / "fase3_real" / \
    "sensibilidad_fase3_comun.py"
_spec = importlib.util.spec_from_file_location("sensibilidad_fase3_comun",
                                               _RUTA_COMUN)
comun = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(comun)

OFAT = {
    "P_baja": Barrido(600.0, 800.0, 200.0 / 6),
    "eps_cond": Barrido(0.90, 0.99, 0.09 / 6),
    "eps_reg": Barrido(0.75, 0.95, 0.20 / 6),
    "x_b": Barrido(0.78, 0.86, 0.08 / 6),
    "eta_t": Barrido(0.85, 0.95, 0.10 / 6),
}


def test_barridos_ofat_7_puntos_cerrando_el_rango():
    for var, spec in OFAT.items():
        valores = generar_valores(spec)
        assert len(valores) == 7, var
        assert math.isclose(valores[0], spec.inicio, rel_tol=1e-9), var
        assert math.isclose(valores[-1], spec.fin, rel_tol=1e-9), var
        assert all(b > a for a, b in zip(valores, valores[1:])), var


def test_malla_2d_36_puntos_con_rejillas_cerradas():
    pb = generar_valores(Barrido(600.0, 800.0, 40.0))
    er = generar_valores(Barrido(0.75, 0.95, 0.04))
    assert pb == [600.0, 640.0, 680.0, 720.0, 760.0, 800.0]
    assert len(er) == 6
    assert math.isclose(er[0], 0.75) and math.isclose(er[-1], 0.95)
    variables = {k: Fijo(v) for k, v in comun.CENTRO.items()}
    variables["P_baja"] = Barrido(600.0, 800.0, 40.0)
    variables["eps_reg"] = Barrido(0.75, 0.95, 0.04)
    combos = generar_combinaciones(variables)
    assert len(combos) == 36
    pares = {(c["P_baja"], round(c["eps_reg"], 3)) for c in combos}
    assert len(pares) == 36  # todas las celdas de la malla, sin repetir


def test_ejecutar_barrido_no_pasa_t_amb_diseno():
    """Documenta por que NO se usa `ejecutar_barrido` (default O2=303.55 K):
    la firma no acepta T_amb_diseno y el esquema de la tarea exige 283.15."""
    import inspect
    from src.sensitivity import ejecutar_barrido
    assert "T_amb_diseno" not in inspect.signature(
        ejecutar_barrido).parameters


def test_criterio_ligante():
    # Falla principal O1 -> su margen es el ligante.
    m = {"O1": 0.011, "O2": 3.2, "S5": 9.0}
    assert comun.criterio_ligante(m, "O1") == ("O1", 0.011)
    assert comun.criterio_ligante(m, "O2") == ("O2", 3.2)
    assert comun.criterio_ligante(m, "S5") == ("S5", 9.0)
    # Otra falla principal (p.ej. S4) no aplica spot O1/O2/S5.
    assert comun.criterio_ligante(m, "S4") == (None, None)
    # KALINA (sin fallas): el criterio proporcionalmente mas cerca del borde.
    assert comun.criterio_ligante({"O1": 0.10, "O2": 1.19, "S5": 8.0},
                                  None) == ("O2", 1.19)   # 1.19/1.5 < resto
    assert comun.criterio_ligante({"O1": 0.01, "O2": 3.0, "S5": 10.0},
                                  None) == ("O1", 0.01)   # 0.01/0.02 es menor


def test_esquema_columnas_csv():
    esperado = list(comun.VARIABLES) + [
        "convergio", "clasificacion", "eta", "Wnet", "mensaje",
        "margen_O1", "margen_O2", "margen_S5", "criterio_ligante",
        "margen_ligante", "spot_check",
        "motor_confirmado", "motor_real_clasificacion", "motor_real_eta"]
    assert comun.COLUMNAS == esperado
    assert len(comun.COLUMNAS) == len(set(comun.COLUMNAS))  # sin duplicados
    # La malla 2D pide P_baja y eps_reg primero (esquema del mapa).
    mapa = ["P_baja", "eps_reg"] + [
        c for c in comun.COLUMNAS if c not in ("P_baja", "eps_reg")]
    assert mapa[:2] == ["P_baja", "eps_reg"]
    assert len(mapa) == len(comun.COLUMNAS)


def test_resolver_punto_ancla_con_teqp():
    """Humo: el ancla (centro) converge, es KALINA y eta ~= 0.1273 (motor
    real confirmado 0.12730; Teqp da 0.12732, ver CASO_HUSAVIK_v2 §1.0)."""
    fila = comun.resolver_punto(dict(comun.CENTRO))
    assert fila["convergio"] is True
    assert fila["clasificacion"] == "KALINA"
    assert 0.125 <= fila["eta"] <= 0.130
    assert 0.5 <= fila["margen_O2"] <= 1.5  # Teqp da ~0.87 K; motor real 1.19 K
    assert fila["criterio_ligante"] == "O2"
    assert fila["spot_check"] is True  # |~0.9-1.2| <= 1.5 K -> candidato a revisar