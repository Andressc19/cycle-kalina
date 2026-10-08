"""M6 — los 12 puntos de verificación cruzada (TASK_CONTEXT final_M6 §Parte A).

Cada punto es `{"id": "P01", "origen": <texto>, "combo": <las 11 variables de
`comun.PROFESOR`>, "piso": <T_sumidero de diseño, K>}`. P01–P04 se arman desde
`comun.PROFESOR`; P02 y P05–P12 salen de los CSV de las fases M2, M7, M4b, M4c
y M2R (las columnas indicadas en el TASK_CONTEXT). Si la fila de origen falta
o es ambigua, el punto se OMITE y el motivo queda en `AVISOS`, que la tarea
manda a UNRESOLVED en vez de inventar el dato.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
if str(_RAIZ) not in sys.path:
    sys.path.insert(0, str(_RAIZ))

from comun import PROFESOR  # noqa: E402

RES = _RAIZ / "resultados"
PISO_DEF = 300.032917        # piso de O2 de la Parte A
PISO_B1 = 303.55             # default de `verificar_operativos` (30.4 °C)
VARS_FILA = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "eta_t",
             "eta_p", "eps_hrvg", "eps_reg", "eps_cond")
AVISOS: list[str] = []


def _combo(**kw) -> dict:
    c = dict(PROFESOR)
    c.update(kw)
    return c


def _unica(vals, que: str) -> float:
    """El único valor distinto de `vals`; con más de uno lanza (ambiguo)."""
    u = {round(float(v), 9) for v in vals}
    if len(u) != 1:
        raise ValueError(f"{que}: {len(u)} valores distintos {sorted(u)}")
    return float(next(iter(u)))


def _csv(rel: str) -> pd.DataFrame:
    p = RES / rel
    if not p.exists():
        raise FileNotFoundError(f"falta {rel}")
    return pd.read_csv(p)


def _de_fila(fila) -> tuple:
    """`(combo, piso)` de una fila con las variables de `VARS_FILA`."""
    c = {v: float(fila[v]) for v in VARS_FILA}
    c["m_b"] = float(fila["m_b"]) if "m_b" in fila.index else 1.0
    return c, float(fila["T_sumidero"])


def _p02() -> tuple:
    """M2: fila de `m2n2_kalina.csv` con T_fuente 420 K y la mayor η."""
    df = _csv("2026-10-06_final_M2/m2n2_kalina.csv")
    fil = df[(df["var1"] == "T_fuente") & (df["val1"].astype(float) == 420.0)]
    if fil.empty:
        raise ValueError("m2n2_kalina.csv sin filas con T_fuente = 420 K")
    eta = fil["eta"].astype(float)
    pb = _unica(fil.loc[eta == eta.max(), "P_baja"], "P_baja de mayor η")
    return _combo(T_fuente=420.0, P_baja=pb), PISO_DEF


def _de_m7(df: pd.DataFrame, arr: str):
    def f() -> tuple:
        fil = df[df["arranque"] == arr]
        if len(fil) != 1:
            raise ValueError(f"m7_optimos.csv: {len(fil)} filas para {arr}")
        return _de_fila(fil.iloc[0])
    return f


def _m4b() -> tuple:
    df = _csv("2026-10-07_final_M4b/m4b_top_kalina.csv")
    fil = df[df["puesto"].astype(float) == 1.0]
    if len(fil) != 1:
        raise ValueError(f"m4b_top_kalina.csv: {len(fil)} filas con puesto=1")
    return _de_fila(fil.iloc[0])


def _m4c() -> tuple:
    """M4c: la fila KALINA de `m4c_lhs.csv` con la mayor P_baja."""
    df = _csv("2026-10-07_final_M4c/m4c_lhs.csv")
    fil = df[df["clasificacion"] == "KALINA"]
    if fil.empty:
        raise ValueError("m4c_lhs.csv sin filas KALINA")
    m = float(fil["P_baja"].astype(float).max())
    top = fil[fil["P_baja"].astype(float) == m]
    if len(top) != 1:
        raise ValueError(f"m4c_lhs.csv: {len(top)} filas KALINA con P_baja máx")
    return _de_fila(top.iloc[0])


def _m2r() -> tuple:
    """M2R: la de menor P_baja entre las de ε_HRVG 0.40 y fuente 623.15 K.

    En `m2r_kalina.csv` las filas con `var1 = eps_hrvg` dejan la fuente en el
    valor de `PROFESOR` (623.15 K); el combo se reconstruye como `PROFESOR` +
    `var1/val1` + `var2/val2`.
    """
    df = _csv("2026-10-06_final_M2R/m2r_kalina.csv")
    fil = df[(df["var1"] == "eps_hrvg") & (df["val1"].astype(float) == 0.40)]
    if fil.empty:
        raise ValueError("m2r_kalina.csv sin filas con ε_HRVG = 0.40")
    if set(fil["var2"]) != {"P_baja"}:
        raise ValueError(f"m2r_kalina.csv: var2 = {sorted(set(fil['var2']))}")
    pb = _unica([fil["val2"].astype(float).min()], "menor P_baja con ε_HRVG 0.40")
    return _combo(eps_hrvg=0.40, P_baja=pb), PISO_DEF


def _agrega(out: list, pid: str, origen: str, fn) -> None:
    try:
        combo, piso = fn()
        out.append(dict(id=pid, origen=origen, combo=combo, piso=piso))
    except Exception as exc:                       # noqa: BLE001 - se anota
        AVISOS.append(f"{pid} ({origen}): {type(exc).__name__}: {exc}")


def puntos() -> list:
    """Los 12 puntos P01–P12 (los que no se puedan armar quedan en `AVISOS`)."""
    out: list = []
    _agrega(out, "P01", "Ancla A*",
            lambda: (_combo(T_fuente=403.0, P_baja=563.6363636363637), PISO_DEF))
    _agrega(out, "P02", "M2, mayor η", _p02)
    _agrega(out, "P03", "M5c, presiones del profesor, techo",
            lambda: (_combo(T_fuente=410.0, eps_cond=0.95), PISO_DEF))
    _agrega(out, "P04", "M5c, presiones del profesor, ε_cond mínima",
            lambda: (_combo(T_fuente=390.0, eps_cond=0.875), PISO_DEF))
    m7 = _csv("2026-10-07_final_M7/m7_optimos.csv")
    for n, arr in enumerate(("A1", "A2", "A3", "A4", "A5"), 5):
        _agrega(out, f"P{n:02d}", f"M7, óptimo {arr}", _de_m7(m7, arr))
    _agrega(out, "P10", "M4b, top 1", _m4b)
    _agrega(out, "P11", "M4c, mayor P_baja KALINA", _m4c)
    _agrega(out, "P12", "M2R, fuente del profesor", _m2r)
    return out


def por_id() -> dict:
    return {p["id"]: p for p in puntos()}
