"""Constancia de la verificación cruzada con DWSIM (2026-10-03).

Comprueba, sobre los resultados GUARDADOS en `resultados/2026-10-03_dato_a_dato/`, los
criterios con los que se aceptó la comparación dato a dato entre el solver del proyecto
(motor real, `AmmoniaWaterAdapter`) y DWSIM (Peng-Robinson) resolviendo el MISMO cierre por
efectividad en 6 ciclos KALINA con P_alta = 3000 kPa. Reporte:
`resultados/2026-10-03_dato_a_dato/REPORTE_DATO_A_DATO.md`.

No vuelve a correr DWSIM ni el motor (DWSIM necesita pythonnet + `D:\\DWSIM`, fuera del
`.venv`; el motor real tarda 10–19 min por ciclo). Para regenerar los JSON:
`scripts/dwsim/dato_a_dato_motor.py` (.venv) y `scripts/dwsim/dato_a_dato_dwsim.py`
(Python global). Los umbrales fijan lo medido con margen; no se ajustan para que pase.

Entalpía: cada modelo tiene su propio cero, así que se compara
h_rel = h − h(P_alta, T0, x_estado) (misma mezcla líquida a T0).
"""
import json
from pathlib import Path

import pytest

DIR = Path(__file__).resolve().parents[1] / "resultados" / "2026-10-03_dato_a_dato"
CICLOS = ["KALINA-01", "KALINA-03", "KALINA-06", "KALINA-09", "KALINA-12", "KALINA-17"]
LIQ_FRIOS = (1, 6, 7, 9, 10)          # estados líquidos a <= ~356 K


def _cargar(prefijo, et):
    f = DIR / f"{prefijo}_{et}.json"
    if not f.exists():
        pytest.skip(f"falta {f.name} (regenerar con scripts/dwsim/dato_a_dato_*.py)")
    return json.loads(f.read_text())


def _balances(est):
    """Balances internos [kW] a partir de los estados (deben ser ~0 en cualquier modelo)."""
    e = {int(k): v for k, v in est.items()}
    sep = e[2]["m"] * e[2]["h"] - e[3]["m"] * e[3]["h"] - e[5]["m"] * e[5]["h"]
    absb = e[4]["m"] * e[4]["h"] + e[7]["m"] * e[7]["h"] - e[8]["m"] * e[8]["h"]
    reg = e[5]["m"] * (e[5]["h"] - e[6]["h"]) - e[10]["m"] * (e[1]["h"] - e[10]["h"])
    val = e[6]["h"] - e[7]["h"]
    return dict(separador=sep, absorbedor=absb, regenerador=reg, valvula=val)


@pytest.mark.parametrize("et", CICLOS)
def test_dwsim_convergio_y_cuadra(et):
    dw = _cargar("dwsim", et)
    assert dw["convergio"], f"{et}: DWSIM no convergió"
    assert all(abs(v) < 0.01 for v in dw["equipo"].values()), dw["equipo"]
    assert abs(dw["cierre"]) < 0.05
    for k in ("hrvg", "reg", "cond"):
        assert abs(dw[f"eps_{k}_res"] - dw["punto"][f"eps_{k}"]) < 1e-4


@pytest.mark.parametrize("et", CICLOS)
@pytest.mark.parametrize("modelo", ["motor", "dwsim"])
def test_balances_internos(et, modelo):
    b = _balances(_cargar(modelo, et)["estados"])
    assert all(abs(v) < 0.05 for v in b.values()), f"{modelo} {et}: {b}"


@pytest.mark.parametrize("et", CICLOS)
def test_estados_dato_a_dato(et):
    mo, dw = _cargar("motor", et), _cargar("dwsim", et)
    for k in range(1, 11):
        a, b = mo["estados"][str(k)], dw["estados"][str(k)]
        assert abs(b["T"] - a["T"]) <= 3.0, f"{et} estado {k}: dT={b['T'] - a['T']:.2f} K"
        if k in (1, 2, 8, 9, 10):                       # composición global x_b
            assert abs(b["x"] - a["x"]) < 1e-4, f"{et} estado {k}"
        if k in LIQ_FRIOS:
            dh = (b["h"] - b["h0L"]) - (a["h"] - a["h0L"])
            assert abs(dh) <= 5.0, f"{et} estado {k}: dh_rel={dh:.2f} kJ/kg"


@pytest.mark.parametrize("et", CICLOS)
def test_eta_diferencia_acotada(et):
    """DWSIM-PR da η algo mayor en todos los ciclos (+0.02 a +0.37 pp medidos)."""
    d = 100 * (_cargar("dwsim", et)["eta"] - _cargar("motor", et)["eta"])
    assert 0.0 < d < 0.5, f"{et}: d_eta={d:+.3f} pp"


def test_mismo_orden_de_ciclos_por_eta():
    """Tendencia: los dos modelos ordenan los 6 ciclos igual por eficiencia."""
    eta = {m: {et: _cargar(m, et)["eta"] for et in CICLOS} for m in ("motor", "dwsim")}
    orden = {m: sorted(CICLOS, key=eta[m].get, reverse=True) for m in eta}
    assert orden["motor"] == orden["dwsim"], orden
