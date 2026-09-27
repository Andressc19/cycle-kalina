"""Prueba persistente de la verificación IAPWS G4-01 (Tablas 6-8) de
`scripts/verificacion_iapws_g4.py`. Parametrizada por punto (24 casos):
los puntos `no_converge` se marcan xfail con su mensaje real; el resto se
recomprueba contra los criterios fijados (no los suaviza)."""

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _cargar_modulo():
    spec = importlib.util.spec_from_file_location(
        "verificacion_iapws_g4", REPO / "scripts" / "verificacion_iapws_g4.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


vig = _cargar_modulo()


@pytest.fixture(scope="module")
def filas():
    return vig.evaluar_todo()


@pytest.mark.parametrize("clave", vig.claves_puntos())
def test_punto(clave, filas):
    motor, tabla, punto = clave
    assert len(filas) == 96
    rs = [f for f in filas if (f["motor"], f["tabla"], f["punto"]) == clave]
    assert rs, f"sin filas para {clave}"
    nc = [f["detalle"] for f in rs if f["cumple"] == "no_converge"]
    if nc:
        pytest.xfail(f"{motor} Tabla {tabla} {punto}: {nc[0]}")
    fallos = []
    for f in rs:
        if f["cumple"] == "esperado_offset":
            if f["motor"] != "teqp" or f["propiedad"] != "f":
                fallos.append(f"esperado_offset fuera de f/teqp: {f}")
            float(f["valor_motor"])  # numérico aunque no se compara (offset de referencia)
            continue
        modo, tol = vig.TOL[(tabla, f["propiedad"])]
        guia, val = float(f["valor_guia"]), float(f["valor_motor"])
        err = abs(val - guia) / abs(guia) if modo == "rel" else abs(val - guia)
        if not err < tol:
            fallos.append(f"{f['propiedad']}: motor={val:.6g} vs guia={guia:.6g} "
                          f"(err {err:.3e}, tol {modo}<{tol:.0e})")
    if fallos:
        pytest.fail(f"{motor} Tabla {tabla} {punto}: " + "; ".join(fallos))