"""Sensibilidad 1, Ronda 3 - reporte del paso 3 (N9, N10 y N8 con filas).

Escribe en `resultados/2026-10-16_sens1_ronda3/`: `ronda3_resumen_barridos.csv`
(por barrido y centro), `ronda3_N9_matrices.md` y `ronda3_resumen.md` (todo en
lenguaje llano, con las mallas 5x7 de N10, su tendencia en P_alta y la seccion
N8 de `ronda3_reporte3.py`). Todos los numeros salen de `ronda3_filas.csv` o
de `ronda3_diseno.csv`.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from ronda3_puntos import P_ALTA_N10, P_BAJA_N10, PARES
from ronda3_reporte2 import (BARRIDOS, _k, agotados_por, centros_de, es_kalina,
                             fmt, leer_filas, n9_par_resumen, n9_tabla,
                             n10_idx, n10_tabla, num, planificados, resumen_por)
from ronda3_reporte3 import n8_bloque

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
    return ["| " + " | ".join(str(c) for c in cab) + " |",
            "|" + "---|" * len(cab)] + [
        "| " + " | ".join(str(x) for x in f) + " |" for f in cel]


def _md_matrices(filas, nivel, barrido):
    """Cabeceras + matrices (clase y eta) de N9 (por par) o N10 (malla 5x7)."""
    out = []
    for centro in centros_de(filas, barrido):
        for par, a, b in (PARES if barrido == "N9" else [("", "", "")]):
            tit = (f"{nivel} {centro} - par {par} ({a} x {b})" if barrido == "N9"
                   else f"{nivel} {centro} - malla 5x7 (P_alta x P_baja)")
            out += [tit, "",
                    "Clase (K/c/n/i; la letra en minuscula marca los fuera "
                    "del rango experimental):", ""]
            for modo in ("clase", "eta"):
                if modo == "eta":
                    out += ["", "eta [%]:", ""]
                cab, lin = (n9_tabla(filas, centro, par, modo) if barrido == "N9"
                            else n10_tabla(filas, centro, modo))
                out += _tabla(cab, lin) + ([""] if modo == "eta" else [])
    return out


def n10_max_p(filas, centro):
    """Por P_alta: (P_alta, id del mejor KALINA, eta max [%] entre KALINA)."""
    idx, out, pb = n10_idx(filas), [], P_BAJA_N10[centro]
    for a in P_ALTA_N10:
        mej, e = "", None
        for b in pb:
            f = idx.get((centro, _k(a), _k(b)))
            if f is not None and es_kalina(f):
                x = num(f.get("eta"))
                if x is not None and (e is None or x > e):
                    mej, e = f.get("id_punto"), x
        out.append((float(a), mej, None if e is None else 100 * e))
    return out


def _n10_tendencia(filas):
    """Lineas llanas: eta max por P_alta y si sube o tiene maximo interior."""
    out, lo, hi = [], P_ALTA_N10[0], P_ALTA_N10[-1]
    for c in centros_de(filas, "N10"):
        maxs = n10_max_p(filas, c)
        cel = ", ".join(f"{a:g} -> " + ("?" if e is None else f"{e:.2f}")
                        for a, _, e in maxs)
        nums = [(a, i, e) for a, i, e in maxs if e is not None]
        if not nums:
            out.append(f"- **{c}**: eta max por P_alta [kPa -> %]: {cel}. Sin "
                       "eta util: no se puede decidir la tendencia.")
            continue
        a, i, e = max(nums, key=lambda t: (t[2], t[0]))
        ver = ("la eta maxima sigue subiendo con P_alta" if a == hi else
               "maximo interior" if lo < a < hi else
               "la eta maxima desciende con P_alta")
        out.append(f"- **{c}**: eta max por P_alta [kPa -> %]: {cel}. "
                   f"Veredicto: {ver} (eta max en {a:g} kPa); mejor punto "
                   f"{i} ({_pct(e)} %).")
    return out


def _filas_resumen(res):
    cl = ("n_puntos", "n_kalina_total", "n_dentro", "n_fuera", "n_corregible",
          "n_inviable", "n_no_convergio")
    et = [f"eta_{k}_{g}_pct" for g in ("kal", "dentro") for k in ("min", "med", "max")]
    return [[r["barrido"], r["centro"]] + [str(r[k]) for k in cl]
            + [_pct(r[k]) for k in et] for r in res]


def main():
    filas = leer_filas(OUT / "ronda3_filas.csv")
    res = []
    for b in BARRIDOS:
        cs = centros_de(filas, b)
        tot = ["TOTAL"] if len(cs) > 1 else []
        for c in cs + tot:
            res.append(resumen_por(filas, b, c))
    _escribir(OUT / "ronda3_resumen_barridos.csv", CM_RES, res)
    par = n9_par_resumen(filas)
    (OUT / "ronda3_N9_matrices.md").write_text(
        "# N9 - mallas 7x7 de clase y eta por centro y par\n\n"
        + "\n".join(_md_matrices(filas, "##", "N9")) + "\n", encoding="utf-8")

    plan = planificados(OUT / "ronda3_diseno.csv")
    ev = dict(Counter(f.get("barrido") for f in filas))
    plan_ev = [f"- **{b}**: planeados {plan.get(b, 0)} (ronda3_diseno.csv) vs "
               f"evaluados {ev.get(b, 0)} (ronda3_filas.csv)."
               for b in sorted(set(plan) | set(ev))]
    c_n9 = [r for r in res if r["barrido"] == "N9" and r["centro"] != "TOTAL"]
    txt_c = "\n".join(
        f"- **{r['centro']}**: {r['n_puntos']} puntos evaluados; "
        f"{r['n_kalina_total']} KALINA (total), de los cuales "
        f"{r['n_dentro']} estan dentro del rango experimental y {r['n_fuera']} "
        f"fuera del rango experimental (liquido > 420 K). Ademas "
        f"{r['n_no_convergio']} NO_CONVERGIO. La eta mas alta entre los "
        f"KALINA (total) es {_pct(r['eta_max_kal_pct'])}% (mediana "
        f"{_pct(r['eta_med_kal_pct'])}%, minima {_pct(r['eta_min_kal_pct'])}%)."
        for r in c_n9)
    filas_par = [[p["centro"], p["par"], str(p["n_celdas"]), str(p["n_kalina"]),
                  p["var1"], p["var2"], fmt(p["val1_mejor"]), fmt(p["val2_mejor"]),
                  p["id_mejor"], _pct(p["eta_mejor_pct"])] for p in par]
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
        *_md_matrices(filas, "###", "N9"),
        "Tambien en `ronda3_N9_matrices.md`.", "",
        "## 3. N10 - extension de P_alta mas alla de 5000 kPa", "",
        "Malla 5x7 por centro (P_alta en {4000, 5000, 6000, 7000, 8000} kPa; "
        "P_baja segun el centro) y sin punto base: 35 puntos por centro. Cada "
        "celda es el punto de esa combinacion.", "",
        *_md_matrices(filas, "###", "N10"),
        "### La eta maxima sube con P_alta o tiene maximo interior?", "",
        *_n10_tendencia(filas),
        "- En el veredicto, `eta max en X kPa` dice en que P_alta esta el "
        "maximo de ese centro; `sigue subiendo` significa que el maximo cae en "
        "el borde superior de la caja (8000 kPa).", "",
        *n8_bloque(filas),
        "### Puntos con tiempo agotado: tope duro de 600 s y presupuesto de 300 s", "",
        *(to or ["- Ninguno."]), "",
    ]
    (OUT / "ronda3_resumen.md").write_text("\n".join(doc) + "\n",
                                           encoding="utf-8")
    print(f"escrito: ronda3_resumen_barridos.csv ({len(res)} filas) + "
          f"ronda3_N9_matrices.md + ronda3_resumen.md sobre {len(filas)} "
          f"filas de ronda3_filas.csv", flush=True)


if __name__ == "__main__":
    main()
