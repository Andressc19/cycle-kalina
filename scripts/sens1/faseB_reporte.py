"""Sensibilidad 1, Fase B — reporte de las mallas 2D (`faseB_filas.csv`).

Escribe en `resultados/2026-10-14_sens1_faseB/`:
- `faseB_mallas.md` (matriz 7x7 de clase y de η por centro y par),
- `faseB_resumen_pares.csv` (métricas y la medida de interacción por par),
- `faseB_resumen.md` (tabla corta, rangos KALINA y preselección de equipos).
La interacción se mide contra las líneas KALINA de la Fase A (incluido el punto
base, ya corregido). Cada número sale de un archivo; no se inventa nada.
Se ejecuta como script, no como módulo.
"""
from __future__ import annotations

import csv
from pathlib import Path

from faseB_corrida import CENTROS, CENTROS_D, PARES
from faseB_reporte2 import (CODIGO, agrega, clase, es_kalina, fmt, fuera_rango,
                            indice, leer_filas, lineas_kalina_faseA, num)

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
OUT = _RAIZ / "resultados" / "2026-10-14_sens1_faseB"
FILAS_A = _RAIZ / "resultados" / "2026-10-14_sens1_faseA" / "faseA_filas.csv"
ETIQ = {"dh_turb": "dh_turb [kJ/kg]", "Wnet": "Wnet/m_b [kW por kg/s]",
        "Qreg_Qi": "Qreg/Qi", "Qout": "Qout/m_b [kW por kg/s]",
        "ratio_P": "P_alta/P_baja"}
CM_PARES = ["centro", "par", "var1", "var2", "n_puntos", "n_kalina",
            "n_corregible", "n_inviable", "n_no_convergio",
            "n_kalina_confiable", "pct_area_kalina", "eta_min_pct",
            "eta_max_pct", "mejor_var1", "mejor_var2", "mejor_eta_pct",
            "kalina_real", "kalina_esperado", "hay_interaccion"]


def _pct(x) -> str:
    return "—" if x is None else f"{x:.2f}"


def _code(f) -> str:
    if f is None:
        return "?"
    if es_kalina(f):
        return "k" if fuera_rango(f) else "K"
    return CODIGO.get(clase(f), "?")


def _eta_txt(f) -> str:
    e = num(f.get("eta")) if f is not None else None
    if f is None or not es_kalina(f) or e is None:
        return "·"
    return f"{100 * e:.4f}"


def _base_idx(a: dict) -> tuple:
    base = CENTROS_D[a["centro"]]

    def buscar(vals, var):
        piso = 273.15 if var == "T_fuente" else 0.0
        return next(k for k, x in enumerate(vals)
                    if abs(x + piso - base[var]) < 1e-6)
    return buscar(a["raw_a"], a["var1"]), buscar(a["raw_b"], a["var2"])


def _matriz(a: dict, campo: str, bi: tuple) -> list:
    out = ["| " + f'{a["var1"]} \\ {a["var2"]}'
           + " | " + " | ".join(f"{x:g}" for x in a["raw_b"]) + " |",
           "|" + "---|" * (len(a["raw_b"]) + 1)]
    for i, x in enumerate(a["raw_a"]):
        fila = []
        for c in a["celdas"]:
            if c["i"] != i:
                continue
            txt = _code(c["row"]) if campo == "clase" else _eta_txt(c["row"])
            fila.append(txt + ("*" if (i, c["j"]) == bi else ""))
        out.append(f"| {x:g} | " + " | ".join(fila) + " |")
    return out


def escribir_mallas(destino, aggs: list) -> None:
    doc = ["# Sensibilidad 1 — Fase B: mallas 2D (clase y η)", "",
           "`K` KALINA · `k` KALINA `fuera_rango` · `c` CORREGIBLE · "
           "`n` NO_CONVERGIO · `i` INVIABLE · `*` punto base. La matriz de η "
           "solo muestra valor en KALINA. T_fuente en K.", ""]
    for a in aggs:
        bi = _base_idx(a)
        doc += [f"## {a['centro']} — {a['par']}: {a['var1']} × {a['var2']}", "",
                "**Clase**", "", *_matriz(a, "clase", bi), "",
                "**η [%]**", "", *_matriz(a, "eta", bi), ""]
    Path(destino).write_text("\n".join(doc) + "\n", encoding="utf-8")


def escribir_resumen_pares(destino, aggs: list) -> None:
    with open(destino, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CM_PARES)
        w.writeheader()
        for a in aggs:
            m = a["mejor"] or (None, None, None)
            w.writerow(dict(
                centro=a["centro"], par=a["par"], var1=a["var1"],
                var2=a["var2"], n_puntos=a["n_puntos"],
                n_kalina=a["n_kalina"], n_corregible=a["n_corregible"],
                n_inviable=a["n_inviable"], n_no_convergio=a["n_no_convergio"],
                n_kalina_confiable=a["n_kalina_confiable"],
                pct_area_kalina=a["pct_area_kalina"],
                eta_min_pct=a["eta_min_pct"], eta_max_pct=a["eta_max_pct"],
                mejor_var1=m[0], mejor_var2=m[1], mejor_eta_pct=m[2],
                kalina_real=a["kalina_real"],
                kalina_esperado=a["kalina_esperado"],
                hay_interaccion=a["hay_interaccion"]))


def _corta(aggs: list) -> list:
    out = ["| centro | par | variable 1 × variable 2 | KALINA | confiables | "
           "área [%] | η min [%] | η max [%] | real | esperado | interacción |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for a in aggs:
        inter = "—" if a["kalina_real"] == a["kalina_esperado"] else (
            "sí" if a["hay_interaccion"] else "no")
        out.append(
            f'| {a["centro"]} | {a["par"]} | {a["var1"]} × {a["var2"]} | '
            f'{a["n_kalina"]} | {a["n_kalina_confiable"]} | '
            f'{_pct(a["pct_area_kalina"])} | {_pct(a["eta_min_pct"])} | '
            f'{_pct(a["eta_max_pct"])} | {a["kalina_real"]} | '
            f'{a["kalina_esperado"]} | {inter} |')
    return out


def _frases(aggs: list) -> list:
    out = ["## 2. Rango conjunto con KALINA", ""]
    for a in aggs:
        if a["rango"] is None:
            out.append(f'- **{a["centro"]} {a["par"]}** ({a["var1"]} × '
                       f'{a["var2"]}): sin KALINA.')
            continue
        x0, x1, y0, y1 = a["rango"]
        extra = ("hay interacción (real < esperado)"
                 if a["hay_interaccion"] else "sin interacción")
        out.append(f'- **{a["centro"]} {a["par"]}**: KALINA con {a["var1"]} ∈ '
                   f'[{x0:g}, {x1:g}] y {a["var2"]} ∈ [{y0:g}, {y1:g}] '
                   f'({a["n_kalina"]}/49 puntos; {extra}).')
    return out


def _equipos(aggs: list) -> list:
    out = ["## 3. Preselección de equipos (mín/máx entre KALINA confiables)",
           "", "| centro | par | magnitud | mínimo | máximo |",
           "|---|---|---|---|---|"]
    for a in aggs:
        for mag, (lo, hi) in a["equipos"].items():
            out.append(f'| {a["centro"]} | {a["par"]} | {ETIQ[mag]} | '
                       f'{fmt(lo)} | {fmt(hi)} |')
    return out


def main() -> None:
    filas = leer_filas(OUT / "faseB_filas.csv")
    idx = indice(filas)
    lineas = lineas_kalina_faseA(FILAS_A)
    aggs = [agrega(c, p, idx, lineas)
            for c, _ in CENTROS for p, _, _ in PARES]
    escribir_resumen_pares(OUT / "faseB_resumen_pares.csv", aggs)
    escribir_mallas(OUT / "faseB_mallas.md", aggs)
    n_por_c = {c: sum(1 for f in filas if f.get("centro") == c)
               for c, _ in CENTROS}
    doc = [
        "# Sensibilidad 1 — Fase B: mallas de 2 variables alrededor de 2 "
        "centros", "",
        "**Fecha:** 2026-10-14 · **Motor:** teqp · **m_b:** 1.0 fijo · "
        "**t_amb_diseno:** T_sumidero de cada punto (piso de O2).",
        f"**Puntos únicos evaluados:** {len(filas)} "
        f"({', '.join(f'{c}={n_por_c[c]}' for c, _ in CENTROS)}). Cada par es "
        "una malla 7×7 (49 celdas); las combinaciones repetidas entre pares "
        "(base y líneas-coordenada) se evalúan una vez y se reutilizan.", "",
        "**KALINA confiable:** `clasificacion == KALINA`, `fuera_rango` falso y "
        "todos los `eta_*`/`eps_*` en [0.40, 0.95].", "",
        "## 1. Tabla por par", "", *_corta(aggs), "",
        *_frases(aggs), "", *_equipos(aggs), ""]
    (OUT / "faseB_resumen.md").write_text("\n".join(doc) + "\n",
                                          encoding="utf-8")
    print(f"escrito: faseB_mallas.md, faseB_resumen_pares.csv ({len(aggs)} "
          f"filas) y faseB_resumen.md en {OUT}", flush=True)


if __name__ == "__main__":
    main()
