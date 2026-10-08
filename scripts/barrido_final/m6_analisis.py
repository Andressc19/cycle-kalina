"""M6 — comparación teqp vs motor real, reporte `REPORTE_M6.md` y cifras.

Lee `m6_verificacion.csv` (24 filas), escribe `m6_comparacion.csv` (12 filas,
una por punto) y arma `REPORTE_M6.md`. `resumen()` da TODAS las líneas con
cifras del reporte; `m6_verificar.py` las recalcula desde los mismos CSV y
exige que estén en el reporte (así ninguna cifra se calcula a mano).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

OUT = _RAIZ / "resultados" / "2026-10-08_final_M6"
CSV_V, CSV_C = "m6_verificacion.csv", "m6_comparacion.csv"
CSV_B1, CSV_S, CSV_E = ("m6_piso_30_4C.csv", "m6_subenfriamiento.csv",
                        "m6_subenfriamiento_evals.csv")
REPORTE = "REPORTE_M6.md"
BANDA = 0.7                                     # banda de incertidumbre de η (G4-01)
CLASES = ("KALINA", "CORREGIBLE", "INVIABLE", "NO_CONVERGIO")
TITULO = ("# M6 — verificación con el motor real, margen de subenfriamiento "
          "y Excel\n")
PIE = ("> Todas las cifras de este reporte salen de los CSV de esta carpeta y "
       "se recalculan con `scripts/barrido_final/m6_verificar.py`.")


def _n(x):
    """`None` para vacío/NaN; `float` en caso contrario."""
    if x is None or x == "" or (isinstance(x, float) and pd.isna(x)):
        return None
    return float(x)


def _clase(x):
    """Texto de una celda de clase, o `None` si falta."""
    if x is None or x == "" or (isinstance(x, float) and pd.isna(x)):
        return None
    return str(x)


def _b(x):
    """Booleano de un CSV (puede venir como texto) o `None` si falta."""
    if x is None or x == "" or (isinstance(x, float) and pd.isna(x)):
        return None
    return x.strip().lower() == "true" if isinstance(x, str) else bool(x)


def comparacion(ver: pd.DataFrame) -> pd.DataFrame:
    """Una fila por punto: clase, η y márgenes de los dos motores."""
    filas = []
    for pid, g in ver.groupby("id", sort=True):
        t, r = g[g["motor"] == "teqp"], g[g["motor"] == "real"]
        if len(t) != 1 or len(r) != 1:
            raise SystemExit(f"{pid}: {len(t)} filas teqp y {len(r)} real")
        t, r = t.iloc[0], r.iloc[0]
        et, er = _n(t["eta"]), _n(r["eta"])
        ct, cr = _clase(t["clasificacion"]), _clase(r["clasificacion"])
        d = None if et is None or er is None else 100.0 * (er - et)
        filas.append(dict(
            id=pid, origen=t["origen"], clase_teqp=ct, clase_real=cr,
            coincide_clase=None if ct is None or cr is None else ct == cr,
            eta_teqp=et, eta_real=er, d_eta_pp=d,
            dentro_banda=None if d is None else abs(d) <= BANDA,
            m_O1_teqp=_n(t["m_O1"]), m_O1_real=_n(r["m_O1"]),
            m_O2_teqp=_n(t["m_O2"]), m_O2_real=_n(r["m_O2"]),
            fuera_rango=_b(t["fuera_rango"]), B_verificado=_b(t["B_verificado"])))
    return pd.DataFrame(filas)


def _f(x, nd=4) -> str:
    return "n/d" if x is None or (isinstance(x, float) and pd.isna(x)) else f"{float(x):.{nd}f}"


def _v(x) -> str:
    if x is None or x == "" or (isinstance(x, float) and pd.isna(x)):
        return "n/d"
    return str(x) if not (isinstance(x, bool) or str(x) in ("True", "False")) \
        else str(x if isinstance(x, bool) else x == "True")


def _tabla(cab, filas) -> list:
    return ["| " + " | ".join(cab) + " |", "|" + "|".join(["---"] * len(cab)) + "|",
            *["| " + " | ".join(f) + " |" for f in filas]]


def _min_max(s) -> tuple:
    v = [x for x in (_n(y) for y in s) if x is not None]
    return (min(v), max(v)) if v else (None, None)


def _cuenta(s) -> int:
    """Cuántos `True` hay en una columna de booleanos con posibles huecos."""
    return int(sum(1 for x in s if _b(x)))


def _tabla_A(cmp: pd.DataFrame) -> list:
    cab = ["id", "origen", "clase_teqp", "clase_real", "coincide", "eta_teqp",
           "eta_real", "d_eta_pp", "±0.7 pp", "m_O2_teqp", "m_O2_real"]
    filas = [[r["id"], r["origen"], _v(r["clase_teqp"]), _v(r["clase_real"]),
              _v(r["coincide_clase"]), _f(r["eta_teqp"]), _f(r["eta_real"]),
              _f(r["d_eta_pp"], 3), _v(r["dentro_banda"]), _f(r["m_O2_teqp"], 3),
              _f(r["m_O2_real"], 3)] for r in cmp.sort_values("id").to_dict("records")]
    return _tabla(cab, filas)


def _tabla_B1(b1: pd.DataFrame) -> list:
    cab = ["id", "origen", "clase", "eta", "m_O2"]
    filas = [[r["id"], r["origen"], _v(r["clasificacion"]), _f(r["eta"]),
              _f(r["m_O2"], 3)] for r in b1.sort_values("id").to_dict("records")]
    return _tabla(cab, filas)


def _tabla_B2(b2: pd.DataFrame) -> list:
    cab = ["id", "ΔT_sub", "alcanzable", "P_baja_orig", "P_baja_req", "ΔP_baja",
           "eta_orig", "eta_req", "d_eta_pp", "rP_req", "m_O1_req", "iter", "nota"]
    filas = [[r["id"], _f(r["ΔT_sub"], 1), _v(r["alcanzable"]), _f(r["P_baja_orig"], 1),
              _f(r["P_baja_req"], 1), _f(r["ΔP_baja"], 1), _f(r["eta_orig"]), _f(r["eta_req"]),
              _f(r["d_eta_pp"], 3), _f(r["rP_req"], 3), _f(r["m_O1_req"], 4),
              _v(r["iteraciones"]), _v(r["nota"])]
             for r in b2.sort_values(["id", "ΔT_sub"]).to_dict("records")]
    return _tabla(cab, filas)


def resumen(cmp: pd.DataFrame, b1: pd.DataFrame, b2: pd.DataFrame,
            ev: pd.DataFrame) -> list:
    """TODAS las líneas con cifras del reporte (recalculables desde los CSV)."""
    n = len(cmp)
    coin, banda = _cuenta(cmp["coincide_clase"]), _cuenta(cmp["dentro_banda"])
    sin_eta = int(cmp["eta_real"].isna().sum())
    dmin, dmax = _min_max(cmp["d_eta_pp"])
    L = ["## Parte A — teqp vs motor real", ""] + _tabla_A(cmp) + [""]
    L.append(f"A: {n} puntos · coincide_clase = {coin}/{n} · "
             f"dentro_banda (|d_eta_pp| ≤ 0.7 pp) = {banda}/{n} · fuera = {n - banda}")
    for etq, col in (("teqp", "clase_teqp"), ("real", "clase_real")):
        c = cmp[col].value_counts()
        L.append(f"A clases {etq}: " + " · ".join(f"{k} = {int(c.get(k, 0))}"
                                                  for k in CLASES))
    L.append(f"A d_eta_pp ({n - sin_eta}/{n} computables): mín = {_f(dmin, 3)} pp · máx = {_f(dmax, 3)} pp")
    L.append(f"A (teqp): fuera_rango = {_cuenta(cmp['fuera_rango'])}/{n} · B_verificado = {_cuenta(cmp['B_verificado'])}/{n}")
    for col in ("m_O2_teqp", "m_O2_real"):
        a, b = _min_max(cmp[col])
        L.append(f"A {col}: mín = {_f(a, 3)} K · máx = {_f(b, 3)} K")
    L += ["", "## Parte B1 — piso de O2 = 303.55 K (30.4 °C)", ""] + _tabla_B1(b1) + [""]
    nk = int((b1["clasificacion"] == "KALINA").sum())
    nk_a = int((cmp["clase_teqp"] == "KALINA").sum())
    por_id = dict(zip(cmp["id"], cmp["clase_teqp"]))
    dif = sum(1 for r in b1.to_dict("records") if _clase(r["clasificacion"]) != por_id.get(r["id"]))
    a1, b1m = _min_max(b1["eta"])
    a2, b2m = _min_max(b1["m_O2"])
    L.append(f"B1: {len(b1)} puntos · KALINA = {nk} (en A con teqp: {nk_a}) · "
             f"clases distintas entre A(teqp) y B1 = {dif}")
    L.append(f"B1: eta mín = {_f(a1)} · máx = {_f(b1m)} · m_O2 mín = "
             f"{_f(a2, 3)} K · máx = {_f(b2m, 3)} K")
    L += ["", "## Parte B2 — P_baja mínima para un ΔT_sub dado", ""] + _tabla_B2(b2) + [""]
    alcanz = _cuenta(b2["alcanzable"])
    notas, it = int(b2["nota"].notna().sum()), _n(b2["iteraciones"].max())
    ap = b2[[bool(_b(x)) for x in b2["alcanzable"]]]
    dp_a, dp_b = (_min_max(ap["ΔP_baja"]) if len(ap) else (None, None))
    de_a, de_b = (_min_max(ap["d_eta_pp"]) if len(ap) else (None, None))
    L.append(f"B2: {len(b2)} casos (8 puntos × ΔT_sub ∈ {{2.0, 5.0}} K) · "
             f"alcanzables = {alcanz} · no alcanzables = {len(b2) - alcanz} · "
             f"con nota = {notas}")
    L.append(f"B2 alcanzables: ΔP_baja mín = {_f(dp_a, 1)} kPa · máx = {_f(dp_b, 1)} kPa · "
             f"d_eta_pp mín = {_f(de_a, 3)} pp · máx = {_f(de_b, 3)} pp · "
             f"iteraciones máx = {_f(it, 0)} · evaluaciones = {len(ev)}")
    L += ["", "## Lo que no se sabe", ""]
    L.append(f"- {sin_eta} de {n} puntos no tienen η_real: el motor real agotó los "
             f"300 s (NO_CONVERGIO); la banda ±0.7 pp solo se comprueba en {banda}/{n}.")
    L.append(f"- los {alcanz} de {len(b2)} casos B2 son alcanzables: no se sabe "
             "si existe un P_baja_req menor fuera del [lo, hi] bisecado.")
    L.append(f"- {notas} casos con nota (hueco NO_CONVERGIO): no se sabe si el "
             "predicado es monótono en todo el intervalo.")
    L.append(f"- B1 cambia la clase de {dif} de {len(b1)} puntos frente a la Parte A: "
             "no se sabe si ese piso cambiaría las otras fases.")
    L.append("- El motor real no corre la verificación B: B_verificado solo existe "
             "para teqp, no se sabe qué diría el motor real.")
    return L


def main() -> None:
    ver = pd.read_csv(OUT / CSV_V)
    cmp = comparacion(ver)
    cmp.to_csv(OUT / CSV_C, index=False, encoding="utf-8")
    b1 = pd.read_csv(OUT / CSV_B1)
    b2 = pd.read_csv(OUT / CSV_S)
    ev = pd.read_csv(OUT / CSV_E)
    lineas = resumen(cmp, b1, b2, ev)
    (OUT / REPORTE).write_text(TITULO + "\n" + "\n".join(lineas) + "\n\n" +
                               PIE + "\n", encoding="utf-8")
    print(f"{CSV_C}: {len(cmp)} filas · {REPORTE}: {len(lineas)} líneas")
    print("\n".join(lineas))


if __name__ == "__main__":
    main()
