"""Sensibilidad 1, N7 — reportes de N7A (una variable) y N7B (pares). Lee
`n7_filas.csv`; escribe 3 CSV + 2 MD en 2026-10-15_sens1_N7/; C1/C2 de faseA.
"""
import csv
from collections import Counter
from pathlib import Path

from n7_puntos import (CENTROS_D, PARES, PARES_D, VARIABLES, clave, valores,
                       valores_brutos)
from n7_reporte2 import (CAMPOS_EQ, CAMPOS_PAR, CAMPOS_VAR, CENTROS, CODIGO,
                         clase, confiable, conteos, equipos, es_kalina, fmt,
                         fuera_rango, leer_filas, num, resumenes_centro,
                         tiempo_agotado)

_RAIZ = Path(__file__).resolve().parents[2]
OUT = _RAIZ / "resultados" / "2026-10-15_sens1_N7"
FILAS_A = (_RAIZ / "resultados" / "2026-10-14_sens1_faseA" /
           "faseA_resumen_variables_corregido.csv")


def _escribir(path, cols, filas):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)


def _pct(x):
    return "—" if x is None else f"{x:.4f}"


def _tabla(cab, cel):
    return (["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
            + ["| " + " | ".join(str(c) for c in r) + " |" for r in cel])


def _code(f):
    if f is None:
        return "-"
    return (("k" if fuera_rango(f) else "K") if es_kalina(f)
            else CODIGO.get(clase(f), "?"))


def _eta_cell(f):
    e = None if f is None else num(f.get("eta"))
    return "·" if e is None or not es_kalina(f) else f"{100 * e:.4f}"


def _clave_fila(f):
    vals = [num(f.get(k)) for k in VARIABLES]
    if any(v is None for v in vals):
        return None
    return tuple(round(v, 6) for v in vals)


def _indice(filas):
    d = {}
    for f in filas:
        k = _clave_fila(f) if f.get("barrido") == "N7B" else None
        if k is not None and k not in d:
            d[k] = f
    return d


def _celdas(centro, par, idx):
    a, b = PARES_D[par]
    ra, da = valores_brutos(a, centro), valores(a, centro)
    rb, db = valores_brutos(b, centro), valores(b, centro)
    out = []
    for i, va in enumerate(da):
        for j, vb in enumerate(db):
            combo = dict(CENTROS_D[centro], **{a: float(va), b: float(vb)})
            out.append(dict(i=i, j=j, ra=ra[i], rb=rb[j],
                            row=idx.get(clave(combo))))
    return out, ra, rb, a, b


def agrega_par(centro, par, idx):
    cl, ra, rb, a, b = _celdas(centro, par, idx)
    ev = [c for c in cl if c["row"] is not None]
    cnt = Counter(clase(c["row"]) for c in ev)
    kal = [c for c in ev if es_kalina(c["row"])]
    conf = [c for c in kal if confiable(c["row"])]
    etas = [e for e in (num(c["row"].get("eta")) for c in kal) if e is not None]
    mm = (None, None, None)
    if conf:
        cm = max(conf, key=lambda c: num(c["row"].get("eta")) or -1.0)
        mm = (cm["ra"], cm["rb"], 100 * (num(cm["row"].get("eta")) or 0.0))
    return dict(centro=centro, par=par, var1=a, var2=b, n_celdas=len(cl),
                n_puntos=len(ev), n_descartado=len(cl) - len(ev),
                n_kalina=cnt["KALINA"], n_corregible=cnt["CORREGIBLE"],
                n_inviable=cnt["INVIABLE"], n_no_convergio=cnt["NO_CONVERGIO"],
                n_kalina_confiable=len(conf),
                pct_area_kalina=(100 * len(kal) / len(cl) if cl else None),
                eta_min_pct=(100 * min(etas) if etas else None),
                eta_max_pct=(100 * max(etas) if etas else None),
                mejor_var1=mm[0], mejor_var2=mm[1], mejor_eta_pct=mm[2],
                celdas=cl, raw_a=ra, raw_b=rb)


def _matriz(a, campo):
    cab = [f'{a["var1"]} \\ {a["var2"]}'] + [f"{x:g}" for x in a["raw_b"]]
    fun = _code if campo == "clase" else _eta_cell
    return _tabla(cab, [[f"{x:g}"]
                        + [fun(c["row"]) for c in a["celdas"] if c["i"] == i]
                        for i, x in enumerate(a["raw_a"])])


def escribir_mallas(destino, aggs):
    doc = ["# N7B — mallas 7x7 (clase K/c/n/i; minuscula si fuera de rango)", "",
           "`-` = celda descartada (P_alta < 1.3*P_baja) o ausente; `·` = sin η. "
           "T_fuente en °C.", ""]
    for a in aggs:
        doc += [f'## {a["centro"]} — {a["par"]}: {a["var1"]} × {a["var2"]}', "",
                "**Clase**", "", *_matriz(a, "clase"), "", "**η [%]**", "",
                *_matriz(a, "eta"), ""]
    Path(destino).write_text("\n".join(doc) + "\n", encoding="utf-8")


def _amp(res_vars, cmp_a, c, var):
    """Amplitud de η entre KALINA (pp) de C3/C4 (res) o de C1/C2 (cmp)."""
    if c in CENTROS:
        return next((r["eta_amplitud_kalina_pp"] for r in res_vars
                     if r["centro"] == c and r["variable"] == var), None)
    return cmp_a.get((c, var))


def main():
    filas = leer_filas(OUT / "n7_filas.csv")
    idx = _indice(filas)
    res_vars = [r for c in CENTROS for r in resumenes_centro(filas, c)]
    aggs = [agrega_par(c, p, idx) for c in CENTROS for p, _, _ in PARES]
    eq = [r for c in CENTROS for r in equipos(filas, c)]
    _escribir(OUT / "n7_resumen_variables.csv", CAMPOS_VAR, res_vars)
    _escribir(OUT / "n7_resumen_pares.csv", CAMPOS_PAR, aggs)
    _escribir(OUT / "n7_equipos.csv", CAMPOS_EQ, eq)
    escribir_mallas(OUT / "n7_mallas.md", aggs)
    cmp_a = {(r["centro"], r["variable"]): num(r.get("eta_amplitud_pp"))
             for r in leer_filas(FILAS_A)}
    doc = ["# Sensibilidad 1 — N7 (N7A una variable; N7B pares; C3 y C4)", "",
           "**Fecha:** 2026-10-15 · **Motor:** teqp · **m_b:** 1.0 · "
           "**t_amb_diseno:** T_sumidero de cada punto.",
           "**KALINA confiable:** clase KALINA, `fuera_rango` falso/vacio y "
           "`eta_*`/`eps_*` en [0.40, 0.95]; **KALINA fuera de rango** aparte.",
           "", "## 1. Resumen por barrido y centro", ""]
    doc += _tabla(["barrido", "centro", "puntos", "KALINA", "CORR", "INV",
                   "NOCONV", "confiables", "fuera rango"],
                  [[r["barrido"], r["centro"], r["n_puntos"], r["n_kalina"],
                    r["n_corregible"], r["n_inviable"], r["n_no_convergio"],
                    r["n_kalina_confiable"], r["n_kalina_fuera_rango"]]
                   for r in conteos(filas)]) + [""]
    doc += ["## 2. Ranking de variables por amplitud de η entre KALINA", ""]
    for c in CENTROS:
        rk = sorted([r for r in res_vars if r["centro"] == c
                     and r["variable"] != "base"],
                    key=lambda r: (r["eta_amplitud_kalina_pp"] is None,
                                   -(r["eta_amplitud_kalina_pp"] or 0)))
        doc += [f"### {c}", ""]
        doc += _tabla(["#", "variable", "amplitud KALINA [pp]", "η min [%]",
                       "η max [%]"],
                      [[i, r["variable"], _pct(r["eta_amplitud_kalina_pp"]),
                        _pct(r["eta_min_kalina_pct"]),
                        _pct(r["eta_max_kalina_pct"])]
                       for i, r in enumerate(rk, 1)]) + [""]
    doc += ["## 3. N7B — mallas de pares (resumen)", "",
            "Matrices 7x7 de clase y η: ver `n7_mallas.md`.", ""]
    doc += _tabla(["centro", "par", "var1 × var2", "puntos", "descartado",
                   "KALINA", "confiables", "área [%]", "η min [%]",
                   "mejor η [%]"],
                  [[r["centro"], r["par"], f'{r["var1"]} × {r["var2"]}',
                    r["n_puntos"], r["n_descartado"], r["n_kalina"],
                    r["n_kalina_confiable"], _pct(r["pct_area_kalina"]),
                    _pct(r["eta_min_pct"]), _pct(r["mejor_eta_pct"])]
                   for r in aggs]) + [""]
    doc += ["## 4. Equipos (min / mediana / max entre KALINA confiables)", ""]
    doc += _tabla(["centro", "magnitud", "n", "minimo", "mediana", "maximo"],
                  [[r["centro"], r["magnitud"], r["n"], fmt(r["minimo"]),
                    fmt(r["mediana"]), fmt(r["maximo"])] for r in eq]) + [""]
    doc += ["## 5. Comparacion con C1 y C2 (amplitud de η entre KALINA, pp)",
            "", "Fuente C1/C2: `faseA_resumen_variables_corregido.csv`.", ""]
    doc += _tabla(["variable", "C1", "C2", "C3", "C4"],
                  [[v] + [_pct(_amp(res_vars, cmp_a, c, v))
                          for c in ("C1", "C2", "C3", "C4")]
                   for v in ["base"] + list(VARIABLES)]) + [""]
    doc += ["## 6. Descartes y tiempo agotado", "",
            "Descartes N7B (`P_alta < 1.3*P_baja`; N7A no aplica):", ""]
    doc += _tabla(["barrido", "centro", "n_candidatas", "n_descartados",
                   "n_duplicados", "n_final"],
                  [[r["barrido"], r["centro"], r["n_candidatas"],
                    r["n_descartados"], r["n_duplicados"], r["n_final"]]
                   for r in leer_filas(OUT / "n7_descartes.csv")]) + [""]
    to = tiempo_agotado(filas)
    doc += ["Puntos con tiempo agotado (tope 600 s):", "",
            *(to or ["- Ninguno."]), ""]
    (OUT / "n7_resumen.md").write_text("\n".join(doc) + "\n", encoding="utf-8")
    print(f"escrito: 3 CSV + 2 MD en {OUT} ({len(res_vars)} vars, "
          f"{len(aggs)} pares, {len(eq)} equipos)", flush=True)

if __name__ == "__main__":
    main()
