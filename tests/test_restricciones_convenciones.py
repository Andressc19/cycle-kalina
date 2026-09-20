"""Convenciones del proyecto (CONTEXT.md) sobre los archivos nuevos de esta
tarea: límite de 200 líneas por archivo y patrón adapter (nunca importar un
backend concreto fuera de `src/properties/*_adapter.py`).
"""

from __future__ import annotations

from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]

_MODULOS_NUEVOS = [
    "src/restricciones/__init__.py",
    "src/restricciones/modelos.py",
    "src/restricciones/numericos.py",
    "src/restricciones/segunda_ley.py",
    "src/restricciones/operativos.py",
    "src/restricciones/composicion.py",
    "src/restricciones/clasificacion.py",
    "src/sensitivity.py",
    "src/ui_campos.py",
    "tests/test_restricciones.py",
    "tests/test_sensitivity.py",
]


def test_archivos_nuevos_dentro_del_limite_de_200_lineas():
    for ruta in _MODULOS_NUEVOS:
        n = len((_RAIZ / ruta).read_text(encoding="utf-8").splitlines())
        assert n <= 200, f"{ruta}: {n} líneas"


def test_restricciones_y_sensitivity_no_importan_backends_concretos():
    prohibidos = ("import pyfluids", "from pyfluids", "import iapws",
                 "from iapws", "from . import _kalina_flash",
                 "from . import _nh3h2o_engine", "from .. import _kalina_flash",
                 "from .. import _nh3h2o_engine")
    for ruta in _MODULOS_NUEVOS:
        if not ruta.startswith("src/"):
            continue
        lineas_import = [l for l in
                         (_RAIZ / ruta).read_text(encoding="utf-8").splitlines()
                         if l.startswith(("import ", "from "))]
        for p in prohibidos:
            assert not any(p in l for l in lineas_import), \
                f"{ruta} importa un backend concreto: {p!r}"
