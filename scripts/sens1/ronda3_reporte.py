"""Sensibilidad 1, Ronda 3 - reporte del paso 3 (hoy solo N9 tiene filas).

Escribe en `resultados/2026-10-16_sens1_ronda3/`: `ronda3_resumen_barridos.csv`
(por barrido y centro), `ronda3_N9_matrices.md` (mallas 7x7 de clase y eta por
centro y par) y `ronda3_resumen.md` (lo anterior en lenguaje llano). N10 y N8
no se reportan hasta que se definan y se corran. Cada numero sale de
`ronda3_filas.csv` o de `ronda3_diseno.csv`.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from ronda3_puntos import PARES
from ronda3_reporte2 import (BARRIDOS, agotados_por, centros_de, fmt, leer_filas,
                             n9_par_resumen, n9_tabla, planificados,
                             resumen_por)

_DIR = Path(__file__).resolve().parent
OUT = _DIR.parents[1] / "resultados" / "2026-10-16_sens1_ronda3"
CM_RES = ["barrido", "centro", "n_puntos", "n_kalina_total", "n_corregible",
          "n_inviable", "n_no_convergio", "n_dentro", "n_fuera",
          "eta_min_kal_pct", "eta_med_kal_pct", "eta_max_kal_pct",
          "eta_min_dentro_pct", "eta_med_dentro_pct", "eta_max_dentro_pct"]
CAB1 = ["barrido", "centro", "puntos", "KALINA (total)", "dentro", "fuera",
        "CORR", "INV", "NOCONV", "eta min (KALINA) [%]",
        "eta med (KALINA) [%]", "eta max (KALINA) [%]",
        "eta min (dentro) [%]", "eta med (dentro) [%]", "eta max (dentro) [%]"]
CAB_PAR = ["centro", "par", "celdas", "KALINA (contando base)", "var1",
           "var2", "val1 del mejor", "val2 del mejor", "mejor id", "eta [%]"]


def _escribir(path, cols, filas):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)


def _pct(x):
    return "?" if x is None else f"{x:.2f}"


def _tabla(cab, cel):
    out = ["| " + " | ".join(str(c) for c in cab) + " |",
           "|" + "---|" * len(cab)]
    out += ["| " + " | ".join(str(x) for x in fila) + " |" for fila in cel]
    return out


def _md_n9_matrices(filas, nivel="##"):
    out = []
    for centro in centros_de(filas, "N9"):
        for par, a, b in PARES:
            out += [f"{nivel} {centro} - par {par} ({a} x {b})", "",
                    "Clase (K/c/n/i; la letra en minuscula marca los fuera "
                    "del rango experimental):", ""]
            cab, lin = n9_tabla(filas, centro, par, "clase")
            out += _tabla(cab, lin)
            out += ["", "eta [%]:", ""]
            cab, lin = n9_tabla(filas, centro, par, "eta")
            out += _tabla(cab, lin) + [""]
    return out


def _filas_resumen(res):
    out = []
    for r in res:
        out.append([r["barrido"], r["centro"], str(r["n_puntos"]),
                    str(r["n_kalina_total"]), str(r["n_dentro"]),
                    str(r["n_fuera"]), str(r["n_corregible"]),
                    str(r["n_inviable"]), str(r["n_no_convergio"]),
                    _pct(r["eta_min_kal_pct"]), _pct(r["eta_med_kal_pct"]),
                    _pct(r["eta_max_kal_pct"]), _pct(r["eta_min_dentro_pct"]),
                    _pct(r["eta_med_dentro_pct"]),
                    _pct(r["eta_max_dentro_pct"])])
    return out


def main():
    filas = leer_filas(OUT / "ronda3_filas.csv")
    res = []
    for b in BARRIDOS:
        cs = centros_de(filas, b)
        if not cs:
            continue
        for c in cs + (["TOTAL"] if len(cs) > 1 else []):
            res.append(resumen_por(filas, b, c))
    _escribir(OUT / "ronda3_resumen_barridos.csv", CM_RES, res)
    par = n9_par_resumen(filas)
    (OUT / "ronda3_N9_matrices.md").write_text(
        "# N9 - mallas 7x7 de clase y eta por centro y par\n\n"
        + "\n".join(_md_n9_matrices(filas, "##")) + "\n", encoding="utf-8")

    plan = planificados(OUT / "ronda3_diseno.csv")
    ev = dict(Counter(f.get("barrido") for f in filas))
    plan_ev = [f"- **{b}**: planeados {plan.get(b, 0)} "
               f"(ronda3_diseno.csv) vs evaluados {ev.get(b, 0)} "
               f"(ronda3_filas.csv)."
               for b in sorted(set(plan) | set(ev))]
    c_n9 = [r for r in res if r["barrido"] == "N9" and r["centro"] != "TOTAL"]
    txt_c = "\n".join(
        f"- **{r['centro']}**: {r['n_puntos']} puntos evaluados; "
        f"{r['n_kalina_total']} KALINA (total), de los cuales "
        f"{r['n_dentro']} estan dentro del rango experimental y "
        f"{r['n_fuera']} fuera del rango experimental (liquido > 420 K). "
        f"Ademas {r['n_no_convergio']} NO_CONVERGIO. La eta mas alta entre "
        f"los KALINA (total) es {_pct(r['eta_max_kal_pct'])}% (mediana "
        f"{_pct(r['eta_med_kal_pct'])}%, minima "
        f"{_pct(r['eta_min_kal_pct'])}%)."
        for r in c_n9)
    filas_par = [[p["centro"], p["par"], str(p["n_celdas"]),
                  str(p["n_kalina"]), p["var1"], p["var2"],
                  fmt(p["val1_mejor"]), fmt(p["val2_mejor"]), p["id_mejor"],
                  _pct(p["eta_mejor_pct"])] for p in par]
    to = agotados_por(filas)
    doc = [
        "# Sensibilidad 1 - Ronda 3 (barridos N9, N10 y N8)", "",
        "**Fecha:** 2026-10-16 - **Motor:** teqp - **m_b:** 1.0 - "
        "**t_amb_diseno:** T_sumidero de cada punto.", "",
        "**Como se lee.** *KALINA (total)* es toda fila clasificada KALINA; "
        "*dentro del rango experimental* es KALINA sin la marca `fuera_rango` "
        "y con eta/eps entre 0.40 y 0.95; *fuera del rango experimental "
        "(liquido > 420 K)* es KALINA con esa marca. En las matrices, "
        "K/c/n/i = KALINA/CORREGIBLE/NO_CONVERGIO/INVIABLE.", "",
        "## 1. Resumen por barrido y centro", "",
        *_tabla(CAB1, _filas_resumen(res)), "",
        "### Planeados vs evaluados", "", *plan_ev, "",
        "## 2. N9 - pares del regenerador y la turbina en C3 y C4", "",
        "Dos mallas 7x7 por centro con el resto de variables en el valor del "
        "centro (B5: eps_reg x eta_t; B6: eps_hrvg x T_fuente). El punto base "
        "se evaluo una sola vez por centro y ocupa la celda central de las "
        "dos mallas.", "",
        txt_c, "",
        "- El diseno de N9 queda en 194 puntos (la referencia previa era de "
        "aproximadamente 196): el dedup por (barrido, centro, combinacion) "
        "deja el punto base una sola vez por centro, asi que cada centro "
        "aporta 1 base + 48 celdas de B5 + 48 de B6.", "",
        "### KALINA por par (contando el punto base) y eta mas alta", "",
        *_tabla(CAB_PAR, filas_par), "",
        "### Matrices 7x7 (clase y eta) por centro y par", "",
        *_md_n9_matrices(filas, "###"),
        "Tambien en `ronda3_N9_matrices.md`.", "",
        "## 3. N10 y N8", "",
        "- N10 y N8: todavia no se definieron ni se corrieron; el corredor ya "
        "acepta los argumentos N10, N8 y all, y el reporte se limita a los "
        "barridos con filas.", "",
        "### Puntos con tiempo agotado (tope de 600 s)", "",
        *(to or ["- Ninguno."]), "",
    ]
    (OUT / "ronda3_resumen.md").write_text("\n".join(doc) + "\n",
                                           encoding="utf-8")
    print(f"escrito: ronda3_resumen_barridos.csv ({len(res)} filas) + "
          f"ronda3_N9_matrices.md + ronda3_resumen.md sobre {len(filas)} "
          f"filas de ronda3_filas.csv", flush=True)


if __name__ == "__main__":
    main()
