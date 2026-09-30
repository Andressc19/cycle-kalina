"""Tests de piezas deterministas de la Fase 1 (datos EXACTOS del profesor).

Verifica: lectura de la tabla horaria (24 filas, promedio 300.032917 K),
rejillas de los barridos P_alta (9 puntos) y x_b (7 puntos), que `BASE`
contiene exactamente las 11 variables de VARIABLES_BARRIBLES, y que un punto
resuelto tiene el esquema de fila completo de `tabla_barrido`.

NO corre los 3 barridos ni el punto base con el motor real (40 puntos con
TeqpAdapter y ~1-2 min con el motor iapws): eso lo hace
`correr_fase1_profesor.py`. Un único punto con TeqpAdapter (~8 s, el punto
base) se corre en `test_resolver_punto...` para verificar el esquema y el
síntoma documentado (NO converge con T_fuente alto).

El módulo a probar vive bajo un directorio con guiones (no importable por
nombre), así que se carga por ruta con importlib (mismo patrón que el
test_b0_scan.py de la Fase B0).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from src.sensitivity import VARIABLES_BARRIBLES, Barrido, generar_valores

_RAIZ = Path(__file__).resolve().parents[3]  # fase1_profesor -> raíz del repo
if str(_RAIZ) not in sys.path:
    sys.path.insert(0, str(_RAIZ))

_RUTA = Path(__file__).resolve().parent / "correr_fase1_profesor.py"
_spec = importlib.util.spec_from_file_location("fase1_profesor", _RUTA)
f1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(f1)


def test_leer_tamb_tabla_horaria_24_horas():
    df = f1.leer_tamb()
    assert list(df.columns) == ["hora", "T_amb_K"]
    assert len(df) == 24
    assert df["hora"].tolist() == list(range(1, 25))
    assert round(df["T_amb_K"].mean(), 6) == 300.032917


def test_base_contiene_las_11_variables_barribles():
    assert set(f1.BASE) == set(VARIABLES_BARRIBLES)


def test_rejilla_p_alta_9_puntos():
    v = generar_valores(Barrido(2000.0, 4000.0, 250.0))
    assert len(v) == 9
    assert v[0] == 2000.0 and v[-1] == 4000.0
    assert all(b - a == 250.0 for a, b in zip(v, v[1:]))


def test_rejilla_x_b_7_puntos():
    v = generar_valores(Barrido(0.40, 0.70, 0.05))
    assert len(v) == 7
    assert v[0] == 0.40 and v[-1] == 0.70
    assert all(round(b - a, 10) == 0.05 for a, b in zip(v, v[1:]))


def test_resolver_punto_esquema_y_sintoma_documentado():
    """El punto base con T_fuente=623.15 K NO converge (síntoma conocido).

    Es exactamente el incidente que esta fase debe dejar documentado: el
    estado 2 del HRVG queda sobrecalentado fuera de la campana bifásica y el
    separador no puede flashear. La fila debe conservar el esquema completo.
    """
    fila = f1.resolver_punto(dict(f1.BASE))
    assert set(fila) == set(VARIABLES_BARRIBLES) | {
        "convergio", "clasificacion", "eta", "Wnet", "mensaje"}
    assert fila["convergio"] is False
    assert fila["clasificacion"] == "NO_CONVERGIO"
    assert fila["eta"] is None and fila["Wnet"] is None
    assert "equilibrio_liquido_vapor" in fila["mensaje"]