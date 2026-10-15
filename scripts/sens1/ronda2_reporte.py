"""Sensibilidad 1, Ronda 2 — reportes de N2, N5 y N6 (paso 3); leen ronda2_filas.csv."""
from __future__ import annotations

import csv
from pathlib import Path

from ronda2_reporte2 import (BARRIDOS, N2_VARS, STATS, celda, centros_de,
                             confiable, es_kalina, fmt, grupo, leer_filas,
                             n2_top5, n2_ventanas, n5_frontera,
                             n5_mallas_por_tf, n6_cubos, n6_mejor_barato, num,
                             percentiles, resumen_por, tiempo_agotado)

_DIR = Path(__file__).resolve().parent
OUT = _DIR.parents[1] / "resultados" / "2026-10-15_sens1_ronda2"
MAGS = (("dh_turb", "dh_turb [kJ/kg]"), ("Wnet_m_b", "Wnet/m_b [kW por kg/s]"), ("Qin", "Qi/m_b [kW por kg/s]"), ("Qreg_Qi", "Qreg/Qi"), ("Qout_m_b", "Qout/m_b [kW por kg/s]"), ("ratio_P", "P_alta/P_baja"))
MAGF = {"dh_turb": lambda f, d: num(f.get("dh_turb")),
        "Wnet_m_b": lambda f, d: d(f.get("Wnet"), f.get("m_b")),
        "Qin": lambda f, d: d(f.get("Qi"), f.get("m_b")),
        "Qreg_Qi": lambda f, d: d(f.get("Qreg"), f.get("Qi")),
        "Qout_m_b": lambda f, d: d(f.get("Qout"), f.get("m_b")),
        "ratio_P": lambda f, d: d(f.get("P_alta"), f.get("P_baja"))}
CM = {
    "res": ["barrido", "centro", "n_puntos", "n_kalina", "n_corregible", "n_inviable", "n_no_convergio", "n_kalina_confiable", "n_kalina_fuera_rango", "eta_min_pct", "eta_mediana_pct", "eta_max_pct"],
    "n2v": ["n_puntos", "n_kal_total"] + [f"{v}_{s}" for v in N2_VARS for s in STATS],
    "n2t": ["pos", "id_punto", "eta_pct"] + list(N2_VARS),
    "n5f": ["T_fuente", "T_fuente_C", "T_sumidero", "T_sumidero_C", "P_baja_min", "eta_max_pct", "P_baja_eta_max", "hay_confiable"],
    "eq": ["barrido", "centro", "magnitud", "n", "minimo", "mediana", "maximo"],
}


def _div(a, b):
    a, b = num(a), num(b)
    return None if a is None or not b else a / b


def _escribir(path, cols: list, filas: list) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)


def _pct(x) -> str:
    return "—" if x is None else f"{x:.2f}"


def _eta_pct(f: dict) -> str:
    e = num(f.get("eta"))
    return _pct(None if e is None else 100 * e)


def _tabla(cab: list, cel: list) -> list:
    return ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)] + ["| " + " | ".join(c) + " |" for c in cel]


def equipos_filas(filas: list, barrido: str, centro: str) -> list:
    g = [f for f in grupo(filas, barrido, centro) if confiable(f)]
    out = []
    for nombre, etiqueta in MAGS:
        q = percentiles([v for v in (MAGF[nombre](f, _div) for f in g)
                         if v is not None])
        out.append(dict(barrido=barrido, centro=centro, magnitud=etiqueta,
                        n=q["n"], minimo=q["minimo"], mediana=q["mediana"],
                        maximo=q["maximo"]))
    return out


def _frase(c: str, b) -> str:
    """Frase de la combinacion más barata que sigue siendo KALINA confiable."""
    if not b:
        return f"- {c}: ninguna combinacion KALINA confiable entre las 3x3x3."
    return (f"- {c}: combinacion mas barata (suma de efectividades minima) que "
            f"sigue siendo KALINA confiable: eta_t={fmt(b.get('eta_t'))}, "
            f"eps_hrvg={fmt(b.get('eps_hrvg'))}, "
            f"eps_reg={fmt(b.get('eps_reg'))} (eta={_eta_pct(b)}%).")


def _md_mallas(filas: list) -> str:
    m5 = n5_mallas_por_tf(filas)
    out = ["# N5 — mallas de clases (K/c/n/i; minuscula si fuera de rango) "
           "por T_fuente", ""]
    for tfc in sorted(m5):
        cab, lines = m5[tfc][0], m5[tfc][1]
        out += [f"## T_fuente = {tfc:.0f} °C", "| " + " | ".join(cab) + " |",
                "|" + "---|" * len(cab)]
        out += ["| " + " | ".join(str(c) for c in cells) + " |"
                for cells in lines]
        out.append("")
    return "\n".join(out) + "\n"


def _md_cubos(filas: list) -> str:
    c6, best = n6_cubos(filas), n6_mejor_barato(filas)
    out = ["# N6 — cubos 3x3x3 por centro", ""]
    for centro in sorted(c6):
        out += [f"## {centro}",
                "| idx | eta_t | eps_hrvg | eps_reg | clase | eta [%] |",
                "|---|---|---|---|---|---|"]
        out += [f"| {i:02d} | {fmt(f.get('eta_t'))} | "
                f"{fmt(f.get('eps_hrvg'))} | {fmt(f.get('eps_reg'))} | "
                f"{celda(f)} | {_eta_pct(f)} |"
                for i, f in enumerate(c6[centro], 1)]
        out.append("")
    out += [_frase(c, best.get(c)) for c in ("C1", "C2")]
    return "\n".join(out + [""])


def _conclusiones(filas: list, n5f: list) -> list:
    n2k = [f for f in filas if f.get("barrido") == "N2" and es_kalina(f)]
    casos = sum(1 for r in n5f if r["P_baja_min"] is not None)
    keep = [r for r in n5f if r["eta_max_pct"] is not None]
    out = ["## 5. Conclusiones", "",
           "### N2 — esquina 70-130 °C con presiones bajas", "",
           f"- KALINA (confiables+fuera rango) en {len(n2k)} puntos de N2.",
           "- Ver `ronda2_N2_ventanas.csv` y `ronda2_N2_top5.csv`.", "",
           "### N5 — frontera por fuente y clima", "",
           f"- Hay KALINA en {casos} combinaciones (T_fuente,C)x(T_sum,C)."]
    if keep:
        mx = max(keep, key=lambda x: x["eta_max_pct"])
        out.append(f"- Eta maxima {_pct(mx['eta_max_pct'])}% a "
                   f"T_fuente={mx['T_fuente_C']:.0f}°C, "
                   f"T_sum={mx['T_sumidero_C']:.0f}°C con "
                   f"P_baja={fmt(mx['P_baja_eta_max'])} kPa.")
    out += ["", "### N6 — equipos de baja efectividad", ""]
    best = n6_mejor_barato(filas)
    out += [_frase(c, best.get(c)) for c in ("C1", "C2")]
    return out


def main() -> None:
    filas = leer_filas(OUT / "ronda2_filas.csv")
    res, eq = [], []
    for b in BARRIDOS:
        cs = centros_de(filas, b)
        for c in cs + (["TOTAL"] if len(cs) > 1 else []):
            res.append(resumen_por(filas, b, c))
            eq += equipos_filas(filas, b, c)
    nv, nt = n2_ventanas(filas), n2_top5(filas)
    _escribir(OUT / "ronda2_resumen_barridos.csv", CM["res"], res)
    _escribir(OUT / "ronda2_equipos.csv", CM["eq"], eq)
    _escribir(OUT / "ronda2_N2_ventanas.csv", CM["n2v"], [dict(nv)])
    _escribir(OUT / "ronda2_N2_top5.csv", CM["n2t"],
              [dict(pos=i, id_punto=f.get("id_punto"), eta_pct=_eta_pct(f),
                    **{v: f.get(v) for v in N2_VARS})
               for i, f in enumerate(nt, 1)])
    n5f = n5_frontera(filas)
    _escribir(OUT / "ronda2_N5_frontera.csv", CM["n5f"], n5f)
    (OUT / "ronda2_N5_mallas.md").write_text(_md_mallas(filas),
                                             encoding="utf-8")
    (OUT / "ronda2_N6_cubos.md").write_text(_md_cubos(filas), encoding="utf-8")
    doc = ["# Sensibilidad 1 — Ronda 2 (barridos N2, N5, N6)", "",
           "**Fecha:** 2026-10-15 · **Motor:** teqp · **m_b:** 1.0 · **t_amb_diseno:** T_sumidero de cada punto.",
           "**KALINA confiable:** clase KALINA, `fuera_rango` falso/vacio y `eta_*`/`eps_*` en [0.40, 0.95]; **KALINA fuera de rango** se reporta aparte.", ""]
    r1 = [[r["barrido"], r["centro"], str(r["n_puntos"]), str(r["n_kalina"]),
           str(r["n_corregible"]), str(r["n_inviable"]),
           str(r["n_no_convergio"]), str(r["n_kalina_confiable"]),
           str(r["n_kalina_fuera_rango"]), _pct(r["eta_min_pct"]),
           _pct(r["eta_mediana_pct"]), _pct(r["eta_max_pct"])] for r in res]
    doc += ["## 1. Resumen por barrido y centro", "",
            *_tabla(["barrido", "centro", "puntos", "KALINA", "CORR", "INV",
                     "NOCONV", "confiables", "fuera rango", "eta min [%]",
                     "eta med [%]", "eta max [%]"], r1), ""]
    doc += ["## 2. N2 — ventanas entre KALINA (confiables+no)", "",
            f"- n_puntos={nv.get('n_puntos')}, "
            f"n_kal_total={nv.get('n_kal_total')}", "",
            "### Top 5 KALINA por eta", "",
            *_tabla(["pos", "id_punto", "eta [%]", "T_fuente", "P_alta",
                     "P_baja", "x_b", "T_sumidero"],
                    [[str(i), f.get("id_punto"), _eta_pct(f),
                      fmt(f.get("T_fuente")), fmt(f.get("P_alta")),
                      fmt(f.get("P_baja")), fmt(f.get("x_b")),
                      fmt(f.get("T_sumidero"))]
                     for i, f in enumerate(nt, 1)]), ""]
    r5 = [[f"{r['T_fuente_C']:.0f}", f"{r['T_sumidero_C']:.0f}",
           fmt(r["P_baja_min"]), _pct(r["eta_max_pct"]),
           fmt(r["P_baja_eta_max"]), "si" if r["hay_confiable"] else "no"]
          for r in n5f[:30]]
    doc += ["## 3. N5 — frontera (primeras 30 filas de "
            "ronda2_N5_frontera.csv)", "",
            *_tabla(["T_fuente [C]", "T_sum [C]", "P_baja_min [kPa]",
                     "eta_max [%]", "P_baja_eta_max", "hay_confiable"], r5), "",
            "Mallas completas: ver `ronda2_N5_mallas.md`.", ""]
    r4 = [[r["barrido"], r["centro"], r["magnitud"], str(r["n"]),
           fmt(r["minimo"]), fmt(r["mediana"]), fmt(r["maximo"])] for r in eq]
    doc += ["## 4. Equipos (min / mediana / max entre KALINA confiables)", "",
            *_tabla(["barrido", "centro", "magnitud", "n", "minimo",
                     "mediana", "maximo"], r4), ""]
    doc += _conclusiones(filas, n5f)
    to = tiempo_agotado(filas)
    doc += ["", "### Puntos con tiempo agotado (tope 600 s)", "",
            *(to or ["- Ninguno."]), ""]
    (OUT / "ronda2_resumen.md").write_text("\n".join(doc) + "\n",
                                           encoding="utf-8")
    print(f"escrito: CSVs + MDs en {OUT} ({len(filas)} puntos; "
          f"{len(to)} grupo(s) con tiempo agotado)", flush=True)


if __name__ == "__main__":
    main()
