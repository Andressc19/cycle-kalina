"""Sensibilidad 1, Fase C — reporte del LHS (`faseC_filas.csv`).

Escribe en `resultados/2026-10-14_sens1_faseC/`:
- `faseC_resumen_centros.csv` (conteos por clase, KALINA confiables, eta),
- `faseC_ventanas.csv` (percentiles por variable: KALINA confiable vs no KALINA),
- `faseC_ks.csv` (KS KALINA confiables vs demas genuinos),
- `faseC_prcc.csv` (PRCC de cada variable con eta, KALINA confiables),
- `faseC_top10.csv` (10 mejores KALINA confiables por eta),
- `faseC_equipos.csv` (min/mediana/max de las magnitudes de equipos),
- `faseC_resumen.md` (tablas y conclusion por centro; incluye la linea de
  puntos que agotaron el tope de 600 s).
Cada numero sale de un archivo generado; no se inventa nada.
Se ejecuta como script, no como modulo.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import numpy as np

from faseC_reporte2 import (VARIABLES, clase, confiable, equipos_filas, fmt,
                            ks_filas, leer_filas, num, prcc_filas, top10,
                            ventanas)

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
OUT = _RAIZ / "resultados" / "2026-10-14_sens1_faseC"
CENTROS = ("C1", "C2")
CM_RES = ["centro", "n_puntos", "n_kalina", "n_corregible", "n_inviable",
          "n_no_convergio", "n_kalina_confiable", "pct_kalina", "eta_min_pct",
          "eta_mediana_pct", "eta_max_pct"]
CM_VEN = ["centro", "variable", "grupo", "n", "minimo", "p10", "mediana", "p90",
          "maximo"]
CM_KS = ["centro", "variable", "ks", "p_valor", "n_kalina", "n_otros"]
CM_PRCC = ["centro", "variable", "prcc", "abs_prcc", "n"]
CM_TOP = (["centro", "rank", "id_punto", "eta"] + list(VARIABLES))
CM_EQ = ["centro", "magnitud", "n", "minimo", "mediana", "maximo"]


def _escribir(path, cols: list, filas: list) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for f in filas:
            w.writerow(f)


def _pct(x) -> str:
    return "—" if x is None else f"{x:.2f}"


def _resumen_centro(filas: list, centro: str) -> dict:
    rs = [f for f in filas if f.get("centro") == centro]
    cnt = Counter(clase(f) for f in rs)
    conf = [f for f in rs if confiable(f)]
    etas = [num(f.get("eta")) for f in conf]
    etas = [e for e in etas if e is not None]
    q = np.percentile(etas, [0, 50, 100]) if etas else [None, None, None]
    return dict(centro=centro, n_puntos=len(rs),
                n_kalina=cnt.get("KALINA", 0),
                n_corregible=cnt.get("CORREGIBLE", 0),
                n_inviable=cnt.get("INVIABLE", 0),
                n_no_convergio=cnt.get("NO_CONVERGIO", 0),
                n_kalina_confiable=len(conf),
                pct_kalina=(100 * cnt.get("KALINA", 0) / len(rs)
                            if rs else None),
                eta_min_pct=(100 * float(q[0]) if etas else None),
                eta_mediana_pct=(100 * float(q[1]) if etas else None),
                eta_max_pct=(100 * float(q[2]) if etas else None))


def _timeout(filas: list) -> dict:
    """Puntos que agotaron el tope: n, centros y min/max de cada variable."""
    to = [f for f in filas
          if (f.get("mensaje") or "").startswith("tiempo_agotado")]
    zonas = {}
    for v in VARIABLES:
        vals = [num(f.get(v)) for f in to if num(f.get(v)) is not None]
        zonas[v] = (min(vals), max(vals)) if vals else (None, None)
    return dict(n=len(to), centros=sorted({f.get("centro") for f in to}),
                zonas=zonas)


def _tabla(cab: list, filas_celdas: list) -> list:
    out = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    out += ["| " + " | ".join(c) + " |" for c in filas_celdas]
    return out


def _markdown(res: dict, ven: dict, ks: dict, prcc: dict, eq: dict,
              to: dict, filas: list) -> list:
    n_c = {c: sum(1 for f in filas if f.get("centro") == c) for c in CENTROS}
    doc = [
        "# Sensibilidad 1 — Fase C: LHS de 9 variables alrededor de 2 centros",
        "",
        "**Fecha:** 2026-10-14 · **Motor:** teqp · **m_b:** 1.0 fijo · "
        "**t_amb_diseno:** T_sumidero de cada punto (piso de O2).",
        f"**Puntos:** {len(filas)} "
        f"({', '.join(f'{c}={n_c[c]}' for c in CENTROS)}); semilla 20261014, "
        "250 por centro, redondeo por tipo de variable.",
        "**KALINA confiable:** `clasificacion == KALINA`, `fuera_rango` falso y "
        "todos los `eta_*`/`eps_*` en [0.40, 0.95].", "",
        "## 1. Puntos y clases por centro", "",
        *_tabla(["centro", "puntos", "KALINA", "CORREGIBLE", "INVIABLE",
                 "NO_CONVERGIO", "confiables", "% KALINA", "eta min [%]",
                 "eta med [%]", "eta max [%]"],
                [[r["centro"], str(r["n_puntos"]), str(r["n_kalina"]),
                  str(r["n_corregible"]), str(r["n_inviable"]),
                  str(r["n_no_convergio"]), str(r["n_kalina_confiable"]),
                  _pct(r["pct_kalina"]), _pct(r["eta_min_pct"]),
                  _pct(r["eta_mediana_pct"]), _pct(r["eta_max_pct"])]
                 for r in res]), "",
        "## 2. Ventanas (p10–p90) entre KALINA confiables", ""]
    for c in CENTROS:
        doc += [f"### {c}", "",
                *_tabla(["variable", "n", "min", "p10", "mediana", "p90",
                         "max"],
                        [[r["variable"], str(r["n"]), fmt(r["minimo"]),
                          fmt(r["p10"]), fmt(r["mediana"]), fmt(r["p90"]),
                          fmt(r["maximo"])]
                         for r in ven[c] if r["grupo"] == "KALINA_confiable"]),
                ""]
    doc += ["## 3. KS (KALINA confiable vs demás genuinos) — top 3 por centro",
            ""]
    for c in CENTROS:
        doc += [f"- **{c}:** " + "; ".join(
            f'{r["variable"]} KS={fmt(r["ks"])} (p={fmt(r["p_valor"])})'
            for r in ks[c][:3]), ""]
    doc += ["## 4. PRCC con eta (KALINA confiables) — top 3 por centro", ""]
    for c in CENTROS:
        doc += [f"- **{c}:** " + "; ".join(
            f'{r["variable"]} PRCC={fmt(r["prcc"])}' for r in prcc[c][:3]), ""]
    doc += ["## 5. Equipos (mín / mediana / máx entre KALINA confiables)", "",
            *_tabla(["centro", "magnitud", "n", "mínimo", "mediana", "máximo"],
                    [[r["centro"], r["magnitud"], str(r["n"]), fmt(r["minimo"]),
                      fmt(r["mediana"]), fmt(r["maximo"])]
                     for c in CENTROS for r in eq[c]]), "",
            "## 6. Puntos con tiempo agotado (tope 600 s)", ""]
    if to["n"]:
        doc += [f"- {to['n']} punto(s), centro(s) {', '.join(to['centros'])}. "
                + "; ".join(f"{v}: [{fmt(z[0])}, {fmt(z[1])}]"
                            for v, z in to["zonas"].items())]
    else:
        doc += ["- Ninguno."]
    doc += ["", "## 7. Conclusión por centro", ""]
    for c in CENTROS:
        iv = next(r for r in res if r["centro"] == c)
        doc += [f"- **{c}:** {iv['n_kalina_confiable']} KALINA confiables de "
                f"{iv['n_puntos']} puntos ({_pct(iv['pct_kalina'])}% KALINA). "
                f"Con mayor KS: "
                + ", ".join(r["variable"] for r in ks[c][:3])
                + ". Con mayor |PRCC| con eta: "
                + ", ".join(r["variable"] for r in prcc[c][:3]) + "."]
    return doc


def main() -> None:
    filas = leer_filas(OUT / "faseC_filas.csv")
    res = [_resumen_centro(filas, c) for c in CENTROS]
    ven = {c: ventanas(filas, c) for c in CENTROS}
    ks = {c: ks_filas(filas, c) for c in CENTROS}
    prcc = {c: prcc_filas(filas, c) for c in CENTROS}
    eq = {c: equipos_filas(filas, c) for c in CENTROS}
    top = [r for c in CENTROS for r in top10(filas, c)]
    to = _timeout(filas)
    _escribir(OUT / "faseC_resumen_centros.csv", CM_RES, res)
    _escribir(OUT / "faseC_ventanas.csv", CM_VEN,
              [r for c in CENTROS for r in ven[c]])
    _escribir(OUT / "faseC_ks.csv", CM_KS, [r for c in CENTROS for r in ks[c]])
    _escribir(OUT / "faseC_prcc.csv", CM_PRCC,
              [r for c in CENTROS for r in prcc[c]])
    _escribir(OUT / "faseC_top10.csv", CM_TOP, top)
    _escribir(OUT / "faseC_equipos.csv", CM_EQ, [r for c in CENTROS
                                                 for r in eq[c]])
    doc = _markdown(res, ven, ks, prcc, eq, to, filas)
    (OUT / "faseC_resumen.md").write_text("\n".join(doc) + "\n",
                                          encoding="utf-8")
    print(f"escrito: 6 CSV + faseC_resumen.md en {OUT} "
          f"({len(filas)} puntos; {to['n']} con tiempo agotado)", flush=True)


if __name__ == "__main__":
    main()
