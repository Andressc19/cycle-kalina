"""M6 — verificación de la campaña M6 (TASK_CONTEXT final_M6 §C2 y §C5).

Sin recalcular el ciclo: recomputa desde los CSV los conteos y las cifras de
`REPORTE_M6.md` (una comprobación POR cifra) y comprueba la estructura de las
salidas (24 filas de verificación, 12 de comparación, 12 de B1 y 16 de B2).
Imprime OK/FALLA por cada comprobación y sale con 1 si algo falla.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

import m6_analisis as an  # noqa: E402
from comun import COLS  # noqa: E402

FAL = 0
TOL = 1e-6
IDS8 = ("P01", "P02", "P03", "P05", "P06", "P07", "P08", "P09")
PISO_B1, OBJ = 303.55, (2.0, 5.0)


def chk(ok: bool, msg: str) -> None:
    global FAL
    FAL += 0 if ok else 1
    print(("OK    " if ok else "FALLO ") + msg, flush=True)


def _falta(x) -> bool:
    """`True` para None, vacío o NaN (lo que el CSV deja en blanco)."""
    if x is None or x == "":
        return True
    try:
        return bool(pd.isna(x))
    except (TypeError, ValueError):
        return False


def _cerca(a, b, tol=TOL) -> bool:
    """`a ≈ b` (tolerancia relativa); dos faltantes cuentan como iguales.

    Con booleanos/Textos (`True` vs `"True"`) cae a la comparación textual.
    """
    if _falta(a) or _falta(b):
        return _falta(a) and _falta(b)
    try:
        fa, fb = float(a), float(b)
    except (TypeError, ValueError):
        return str(a).strip().lower() == str(b).strip().lower()
    return abs(fa - fb) <= tol * max(1.0, abs(fb))


def _estructura(ver, cmp, b1, b2, ev) -> None:
    chk(len(ver) == 24, f"m6_verificacion.csv tiene 24 filas (12×2): {len(ver)}")
    chk(list(ver.columns) == ["id", "origen"] + list(COLS),
        "m6_verificacion.csv = id, origen + comun.COLS")
    por_id = {i: g for i, g in ver.groupby("id")}
    chk(len(por_id) == 12 and all(len(g) == 2 for g in por_id.values()),
        f"12 ids con 2 filas cada uno: {sorted(por_id)}")
    chk(all(set(g["motor"]) == {"teqp", "real"} for g in por_id.values()),
        "cada punto tiene una fila teqp y una real")
    chk(len(cmp) == 12 and set(cmp["id"]) == set(por_id),
        f"m6_comparacion.csv tiene los 12 ids: {len(cmp)} filas")
    for c in ("clase_teqp", "clase_real", "coincide_clase", "eta_teqp",
              "eta_real", "d_eta_pp", "dentro_banda", "m_O1_teqp", "m_O1_real",
              "m_O2_teqp", "m_O2_real", "fuera_rango", "B_verificado"):
        chk(c in cmp.columns, f"m6_comparacion.csv tiene la columna {c}")


def _coherencia(ver, cmp) -> None:
    mal_cc, mal_d, mal_bd, mal_x = [], [], [], []
    n_bd = 0
    for r in cmp.to_dict("records"):
        g = ver[ver["id"] == r["id"]]
        t = g[g["motor"] == "teqp"].iloc[0]
        rl = g[g["motor"] == "real"].iloc[0]
        if an._b(r["coincide_clase"]) != (r["clase_teqp"] == r["clase_real"]):
            mal_cc.append(r["id"])
        d = 100.0 * (float(rl["eta"]) - float(t["eta"]))
        if not _cerca(r["d_eta_pp"], d):
            mal_d.append(r["id"])
        n_bd += not _falta(r["d_eta_pp"])
        if _falta(r["d_eta_pp"]):   # sin η_real no hay d_eta_pp: el CSV deja la banda en blanco
            mal_bd += [f'{r["id"]}:sin d_eta_pp, dentro_banda en blanco'] * (not _falta(r["dentro_banda"]))
        elif an._b(r["dentro_banda"]) != (abs(d) <= 0.7):
            mal_bd.append(r["id"])
        for a, b in (("m_O1_teqp", "m_O1"), ("m_O1_real", "m_O1"),
                     ("m_O2_teqp", "m_O2"), ("m_O2_real", "m_O2"),
                     ("fuera_rango", "fuera_rango"), ("B_verificado", "B_verificado")):
            ref = t if a.endswith("teqp") or a.startswith("fuera") or \
                a.startswith("B_") else rl
            if not _cerca(r[a], ref[b]):
                mal_x.append(f'{r["id"]}:{a}')
    chk(not mal_cc, f"coincide_clase == (clase_teqp == clase_real) en 12 → {mal_cc}")
    chk(not mal_d, f"d_eta_pp == 100·(eta_real − eta_teqp) en 12 → {mal_d}")
    chk(not mal_bd, f"dentro_banda == |d_eta_pp| ≤ 0.7 en {n_bd}/12 con η real → {mal_bd}")
    chk(not mal_x, f"m_O1/m_O2/fuera_rango/B_verificado = los de verificacion → {mal_x[:4]}")


def _piso(b1, cmp) -> None:
    chk(len(b1) == 12, f"m6_piso_30_4C.csv tiene 12 filas: {len(b1)}")
    chk(set(b1["motor"]) == {"teqp"}, "B1 es solo motor teqp")
    chk(set(b1["id"]) == set(cmp["id"]), "B1 tiene los mismos 12 ids")
    chk(all(_cerca(x, PISO_B1) for x in b1["T_amb_diseno"]),
        f"B1 usa t_amb_diseno = {PISO_B1} K en las 12 filas")


def _biseccion(ver, b2, ev) -> None:
    chk(len(b2) == 16, f"m6_subenfriamiento.csv tiene 16 casos: {len(b2)}")
    pares = {(r["id"], float(r["ΔT_sub"])) for r in b2.to_dict("records")}
    chk(pares == {(i, o) for i in IDS8 for o in OBJ},
        f"16 casos = 8 puntos × {{2.0, 5.0}} K → {sorted(pares)}")
    mal, ge = [], []
    for r in b2.to_dict("records"):
        t = ver[(ver["id"] == r["id"]) & (ver["motor"] == "teqp")].iloc[0]
        hi = min(0.6 * float(t["P_alta"]), 2500.0)
        lo, req = float(r["P_baja_orig"]), an._n(r["P_baja_req"])
        al = an._b(r["alcanzable"])
        if int(r["iteraciones"]) > 12:
            mal.append(f'{r["id"]}:iteraciones={r["iteraciones"]}')
        if al:
            if req is None or not lo - 1e-6 <= req <= hi + 1e-6:
                mal.append(f'{r["id"]}:req={req} fuera [{lo}, {hi}]')
            if not _cerca(r["ΔP_baja"], req - lo, 1e-9):
                mal.append(f'{r["id"]}:ΔP_baja')
            if not _cerca(r["rP_req"], float(t["P_alta"]) / req, 1e-9):
                mal.append(f'{r["id"]}:rP_req')
            if not _cerca(r["d_eta_pp"], 100.0 * (float(r["eta_req"]) -
                                                   float(r["eta_orig"])), 1e-9):
                mal.append(f'{r["id"]}:d_eta_pp')
            ge.append(r["id"])
        elif req is not None or r["ΔP_baja"] is not None:
            mal.append(f'{r["id"]}:no alcanzable con P_baja_req')
    chk(not mal, f"B2 respeta lo, hi, ΔP, rP y d_eta → {mal[:4]}")
    cl = ev[ev["cumple"].map(lambda x: an._b(x) is True)]
    chk(len(cl) > 0 and all(cl["clasificacion"] == "KALINA") and
        all(float(m) >= float(o) for m, o in zip(cl["m_O2"], cl["ΔT_sub"])),
        "toda evaluación con cumple=True es KALINA y m_O2 ≥ ΔT_sub")
    grupos = ev.groupby(["id", "ΔT_sub"])
    chk(all({"lo", "hi"} <= set(g["paso"]) or
            set(g["paso"]) == {"lo"} for _, g in grupos),
        f"cada bisección evalúa lo (y hi si hizo falta): {len(grupos)} grupos")
    faltan = []
    for r in b2.to_dict("records"):
        g = grupos.get_group((r["id"], r["ΔT_sub"])) if (r["id"], r["ΔT_sub"]) in grupos.groups else None
        if g is None:
            faltan.append(f'{r["id"]}:sin evaluaciones')
            continue
        if an._b(r["alcanzable"]) and not _cerca(r["P_baja_req"], r["P_baja_orig"]):
            ok = any(_cerca(p, r["P_baja_req"]) and an._b(c) is True
                     for p, c in zip(g["P_baja"], g["cumple"]))
            if not ok:
                faltan.append(f'{r["id"]}:sin eval en P_baja_req')
    chk(not faltan, f"todo P_baja_req alcanzable tiene su evaluación → {faltan[:4]}")


def _reporte(ver, cmp, b1, b2, ev) -> None:
    p = an.OUT / an.REPORTE
    if not p.exists():
        chk(False, f"existe {an.REPORTE}")
        return
    txt = p.read_text(encoding="utf-8", errors="replace")
    lineas = an.resumen(cmp, b1, b2, ev)
    for lin in lineas:
        if lin.strip():
            chk(lin in txt, f"reporte: {lin}")


def main() -> None:
    print(f"m6_verificar | OUT={an.OUT}", flush=True)
    nombres = [an.CSV_V, an.CSV_C, an.CSV_B1, an.CSV_S, an.CSV_E]
    faltan = [n for n in nombres if not (an.OUT / n).exists()]
    chk(not faltan, f"están los 5 CSV (faltan: {faltan})")
    if faltan:
        print(f"FIN: {FAL} fallo(s)", flush=True)
        sys.exit(1)
    ver = pd.read_csv(an.OUT / an.CSV_V)
    cmp = an.comparacion(ver)          # idéntico a lo que escribió m6_analisis
    b1 = pd.read_csv(an.OUT / an.CSV_B1)
    b2 = pd.read_csv(an.OUT / an.CSV_S)
    ev = pd.read_csv(an.OUT / an.CSV_E)
    disco = pd.read_csv(an.OUT / an.CSV_C)
    chk(len(disco) == len(cmp) and set(disco["id"]) == set(cmp["id"]),
        f"{an.CSV_C} en disco == la comparación recalculada ({len(disco)})")
    _estructura(ver, cmp, b1, b2, ev)
    _coherencia(ver, cmp)
    _piso(b1, cmp)
    _biseccion(ver, b2, ev)
    _reporte(ver, cmp, b1, b2, ev)
    print(f"FIN: {FAL} fallo(s)", flush=True)
    sys.exit(1 if FAL else 0)


if __name__ == "__main__":
    main()
