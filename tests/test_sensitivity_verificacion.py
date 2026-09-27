"""Tests de la verificación A+B del barrido (`sensitivity.ejecutar_barrido`).

Reutiliza el `FakeBackend`, el fixture `backend` y el caso base `_BASE` de
`tests/test_sensitivity.py` (no se duplican: ese archivo está en la lista de
convenciones de `test_restricciones_convenciones.py` y tiene su propio tope de
200 líneas). Cubre las columnas que el barrido añade con `motor_real=`
(`B_verificado`, `B_dh4s`, `B_t_s`, `B_error`) y con un backend con registro
de A (`A_recurrencias`, `A_verificacion_incompleta`), que sin `motor_real` las
filas no cambian, y que `T_amb_diseno` solo llega a `evaluar_ciclo` si se pide.

El `FakeBackend` es un modelo lineal de juguete y NUNCA da un punto KALINA por
física propia, así que aquí se sustituye `evaluar_ciclo` por una etiqueta
forzada: lo que se verifica es el anotado de columnas, no los criterios de
admisibilidad (de esos se ocupa `test_restricciones.py`).
"""
from __future__ import annotations

import pytest

from src.cycle_solver import resolver_ciclo
from src.sensitivity import (Barrido, ejecutar_barrido, generar_combinaciones,
                             tabla_barrido)
from tests.test_sensitivity import _BASE, FakeBackend

AB = ("B_verificado", "B_dh4s", "B_t_s", "B_error",
      "A_recurrencias", "A_verificacion_incompleta")


class _StubReal:
    """Motor real falso de B: devuelve `valor` siempre, o lanza si `error`."""

    def __init__(self, valor=1.0, error=None):
        self.valor, self.error, self.llamadas = valor, error, 0

    def h(self, P, T=None, x=None, s=None, quality=None):
        self.llamadas += 1
        if self.error is not None:
            raise self.error
        return self.valor


class _FalsoRegistrado(FakeBackend):
    """`FakeBackend` con el registro de recurrencias de `TeqpVerificado`.

    Como A, lleva un contador acumulado `n_recurrencias` y `n_fallos` (las
    recurrencias que el motor real no pudo verificar). La señal se emite una
    vez por resolución —la primera llamada a `h`—, que es cuando el ciclo
    empieza a pedir propiedades; `nuevo_punto()` rearma el disparo.
    """

    def __init__(self, n=0, fallo=False):
        super().__init__()
        self.n_recurrencias, self.n_fallos, self._n, self._fallo = 0, 0, n, fallo
        self._hecho = False

    def nuevo_punto(self):
        self._hecho = False

    def h(self, P, T=None, x=None, s=None, quality=None):
        v = super().h(P, T=T, x=x, s=s, quality=quality)
        if not self._hecho:
            self._hecho = True
            self.n_recurrencias += self._n
            self.n_fallos += 1 if self._fallo else 0
        return v


def _etiquetador():
    """`evaluar_ciclo` de juguete: KALINA si `P_alta` == 3000 kPa."""
    from src.restricciones import (Clasificacion, Falla, ResultadoValidacion,
                                   Severidad)

    def _etiqueta(backend, resultado, **kw):
        if kw["P_alta"] == 3000.0:
            return ResultadoValidacion(clasificacion=Clasificacion.KALINA)
        falla = Falla(codigo="Z1", severidad=Severidad.CRITICO,
                      clasificacion=Clasificacion.INVIABLE,
                      mensaje="etiqueta forzada por el test", variable="P_alta",
                      valor_medido=kw["P_alta"], valor_esperado="—",
                      causa_probable="test", sugerencia="test")
        return ResultadoValidacion(clasificacion=Clasificacion.INVIABLE,
                                   fallas=[falla])
    return _etiqueta


@pytest.fixture
def backend():
    return FakeBackend()


def _doble_base():
    """Caso base con `P_alta` en Barrido: 2 filas; la de 3000 kPa, KALINA."""
    variables = dict(_BASE)
    variables["P_alta"] = Barrido(3000.0, 4000.0, 1000.0)
    return variables


def _h4s_del_ciclo(combo: dict) -> float:
    """`h4s` que el ciclo usó, por la inversa exacta de `turbina.resolver`.

    Es lo que hace `verificar_turbina` para el lado "teqp" cuando no se le pasa
    `backend_teqp`; con este valor el motor real falso coincide y B sale
    verificado con dh4s = 0.
    """
    e = resolver_ciclo(FakeBackend(), **combo)["estados"]
    return e["e3"].h - (e["e3"].h - e["e4"].h) / combo["eta_t"]


def test_sin_motor_real_las_filas_no_cambian(backend):
    """(a) Retrocompat.: sin `motor_real` ni registro, ninguna columna A_/B_."""
    filas = ejecutar_barrido(backend, dict(_BASE))
    for clave in AB:
        assert clave not in filas[0]
    assert filas[0]["clasificacion"] == "INVIABLE"   # el caso base no cambia
    assert filas[0]["eta"] == pytest.approx(-0.13928229432107786)
    columnas = list(tabla_barrido(filas).columns)
    assert not any(c.startswith(("A_", "B_")) for c in columnas)


def test_motor_real_solo_verifica_las_filas_kalina(backend, monkeypatch):
    """(b) Las KALINA llevan `B_*` rellenas; las no KALINA, en None."""
    monkeypatch.setattr("src.sensitivity.evaluar_ciclo", _etiquetador())
    combos = generar_combinaciones(_doble_base())
    stub = _StubReal(valor=_h4s_del_ciclo(combos[0]))   # coincide con el ciclo
    filas = ejecutar_barrido(backend, _doble_base(), motor_real=stub)
    kalina = [f for f in filas if f["clasificacion"] == "KALINA"]
    otras = [f for f in filas if f["clasificacion"] != "KALINA"]
    assert len(kalina) == 1 and len(otras) == 1
    assert kalina[0]["B_verificado"] is True
    assert kalina[0]["B_dh4s"] == pytest.approx(0.0, abs=1e-9)
    assert kalina[0]["B_t_s"] >= 0.0 and kalina[0]["B_error"] is None
    for f in otras:
        assert tuple(f[c] for c in AB[:4]) == (None, None, None, None)
    assert stub.llamadas == 1              # se paga una sola vez, solo la KALINA
    assert list(tabla_barrido(filas).columns)[-4:] == list(AB[:4])


def test_kalina_no_verificado_no_se_reclasifica(backend, monkeypatch):
    """`B_verificado=False` se señala en la fila; la clasificación no cambia."""
    monkeypatch.setattr("src.sensitivity.evaluar_ciclo", _etiquetador())
    filas = ejecutar_barrido(backend, dict(_BASE),
                             motor_real=_StubReal(valor=-1.0e6))
    assert filas[0]["clasificacion"] == "KALINA"
    assert filas[0]["B_verificado"] is False
    assert abs(filas[0]["B_dh4s"]) > 2.0      # muy por encima del umbral


def test_motor_real_que_falla_deja_error_sin_veredicto(backend, monkeypatch):
    """Si el motor real no cubre el estado, `B_verificado=None` + el mensaje."""
    monkeypatch.setattr("src.sensitivity.evaluar_ciclo", _etiquetador())
    filas = ejecutar_barrido(
        backend, dict(_BASE),
        motor_real=_StubReal(error=RuntimeError("sin cambio de signo")))
    assert filas[0]["B_verificado"] is None and filas[0]["B_dh4s"] is None
    assert "sin cambio de signo" in filas[0]["B_error"]


def test_columnas_A_solo_si_el_backend_lleva_registro(backend, monkeypatch):
    """Sin registro de A, sus columnas no aparecen; con registro, se rellenan."""
    monkeypatch.setattr("src.sensitivity.evaluar_ciclo", _etiquetador())
    filas = ejecutar_barrido(backend, _doble_base())
    assert all("A_recurrencias" not in f for f in filas)
    assert all("A_verificacion_incompleta" not in f for f in filas)

    filas = ejecutar_barrido(_FalsoRegistrado(n=0), _doble_base())
    assert [f["A_recurrencias"] for f in filas] == [0, 0]
    assert [f["A_verificacion_incompleta"] for f in filas] == [False, False]
    assert "A_recurrencias" in tabla_barrido(filas).columns


def test_columnas_A_son_el_delta_de_ese_punto(backend, monkeypatch):
    """`A_recurrencias` cuenta lo de ESE punto, no el acumulado del backend."""
    monkeypatch.setattr("src.sensitivity.evaluar_ciclo", _etiquetador())
    fake = _FalsoRegistrado(n=2)
    filas = ejecutar_barrido(fake, dict(_BASE))
    assert filas[0]["A_recurrencias"] == 2 and fake.n_recurrencias == 2
    fake.nuevo_punto()                       # 2ª fila, el MISMO backend
    filas = ejecutar_barrido(fake, dict(_BASE))
    assert filas[0]["A_recurrencias"] == 2   # el delta, no el total (ya es 4)
    assert fake.n_recurrencias == 4
    # En un barrido de 2 puntos el fake solo dispara en el primero, así que la
    # segunda fila lleva SU delta (0, sin fallo) y no el acumulado.
    filas = ejecutar_barrido(_FalsoRegistrado(n=2, fallo=True), _doble_base())
    assert [f["A_recurrencias"] for f in filas] == [2, 0]
    assert [f["A_verificacion_incompleta"] for f in filas] == [True, False]


def test_T_amb_diseno_se_reenvia_a_evaluar_ciclo(backend, monkeypatch):
    """El piso O2 es opcional: solo llega a `evaluar_ciclo` si se pide."""
    vistos = []

    def _espia(be, res, **kw):
        vistos.append(kw)
        return _etiquetador()(be, res, **kw)

    monkeypatch.setattr("src.sensitivity.evaluar_ciclo", _espia)
    ejecutar_barrido(backend, dict(_BASE))
    assert "T_amb_diseno" not in vistos[-1]     # lo de siempre
    ejecutar_barrido(backend, dict(_BASE), T_amb_diseno=283.15)
    assert vistos[-1]["T_amb_diseno"] == pytest.approx(283.15)
