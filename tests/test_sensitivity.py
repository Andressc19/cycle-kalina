"""Tests del barrido paramétrico (`src/sensitivity.py`).

Reusa el `PropertyBackend` fake y el caso base de `test_cycle_solver.py`
(mismo bracket físico [351, 368] dentro de la campana bifásica del fake a
x=0.5: burbuja 350 K, rocío 370 K).
"""

from __future__ import annotations

import pytest

from src.properties.adapter import PropertyBackend
from src.sensitivity import (Barrido, Fijo, ejecutar_barrido,
                             generar_combinaciones, generar_valores,
                             tabla_barrido)


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


_BASE = dict(P_alta=Fijo(3000.0), P_baja=Fijo(400.0), T_fuente=Fijo(369.0),
            T_sumidero=Fijo(350.0), x_b=Fijo(0.5), m_b=Fijo(1.0),
            eta_t=Fijo(0.85), eta_p=Fijo(0.75), eps_hrvg=Fijo(0.85),
            eps_reg=Fijo(0.75), eps_cond=Fijo(0.80))


def test_barrido_3000_a_4000_paso_250():
    assert generar_valores(Barrido(3000.0, 4000.0, 250.0)) == [
        3000.0, 3250.0, 3500.0, 3750.0, 4000.0]


def test_barrido_con_paso_que_no_divide_exacto_cierra_en_fin():
    valores = generar_valores(Barrido(3000.0, 4000.0, 300.0))
    assert valores == [3000.0, 3300.0, 3600.0, 3900.0, 4000.0]


def test_barrido_paso_no_positivo_lanza_valueerror():
    with pytest.raises(ValueError, match="paso"):
        generar_valores(Barrido(3000.0, 4000.0, 0.0))
    with pytest.raises(ValueError, match="paso"):
        generar_valores(Barrido(3000.0, 4000.0, -100.0))


def test_barrido_inicio_mayor_que_fin_lanza_valueerror():
    with pytest.raises(ValueError, match="inicio"):
        generar_valores(Barrido(4000.0, 3000.0, 250.0))


def test_fijo_es_un_barrido_de_un_solo_punto():
    assert generar_valores(Fijo(42.0)) == [42.0]


def test_barrer_mas_de_una_variable_a_la_vez_producto_cartesiano():
    variables = dict(_BASE)
    variables["eta_t"] = Barrido(0.80, 0.90, 0.05)   # 3 valores
    variables["eta_p"] = Barrido(0.70, 0.80, 0.05)   # 3 valores
    combinaciones = generar_combinaciones(variables)
    assert len(combinaciones) == 3 * 3
    pares = {(c["eta_t"], c["eta_p"]) for c in combinaciones}
    assert len(pares) == 9  # todas las combinaciones son distintas
    for c in combinaciones:
        assert c["P_alta"] == 3000.0  # las variables Fijo no varían


def test_ejecutar_barrido_registra_valores_de_todas_las_variables(backend):
    filas = ejecutar_barrido(backend, dict(_BASE))
    assert len(filas) == 1
    fila = filas[0]
    for clave in _BASE:
        assert fila[clave] == _BASE[clave].valor
    assert fila["convergio"] is True
    # El caso base del fake resuelve; la clasificación puede caer en
    # NO_CONVERGIO si N2/N3 exceden la tolerancia numérica del fake (no es lo
    # que este test verifica — solo que se registran las 11 variables).
    assert fila["clasificacion"] in {
        "KALINA", "INVIABLE", "DEGENERADO", "CORREGIBLE", "VALIDO_ADVERTENCIA",
        "NO_CONVERGIO"}


def test_ejecutar_barrido_marca_no_convergio_y_continua(backend):
    variables = dict(_BASE)
    # T_fuente=350.5 con T_sumidero=350 es un bracket degenerado (< 2 K de
    # margen físico): _bracketear lanza CicloNoConvergeError de inmediato.
    variables["T_fuente"] = Barrido(350.5, 369.0, 18.5)
    filas = ejecutar_barrido(backend, variables)
    assert len(filas) == 2
    por_t_fuente = {f["T_fuente"]: f for f in filas}
    assert por_t_fuente[350.5]["convergio"] is False
    assert por_t_fuente[350.5]["clasificacion"] == "NO_CONVERGIO"
    assert por_t_fuente[350.5]["eta"] is None
    assert "bracket" in por_t_fuente[350.5]["mensaje"].lower()
    # El barrido siguió: el segundo punto (T_fuente=369, caso base) sí converge.
    assert por_t_fuente[369.0]["convergio"] is True


def test_ejecutar_barrido_falta_variable_lanza_valueerror(backend):
    incompleto = dict(_BASE)
    del incompleto["m_b"]
    with pytest.raises(ValueError, match="m_b"):
        ejecutar_barrido(backend, incompleto)


def test_tabla_barrido_devuelve_dataframe_con_columnas_esperadas(backend):
    filas = ejecutar_barrido(backend, dict(_BASE))
    df = tabla_barrido(filas)
    assert list(df.columns)[-5:] == [
        "convergio", "clasificacion", "eta", "Wnet", "mensaje"]
    assert len(df) == 1
