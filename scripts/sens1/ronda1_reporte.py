"""Sensibilidad 1, Ronda 1 — reportes de los barridos N1, N3 y N4.

Escribe en `resultados/2026-10-14_sens1_ronda1/`: 4 CSV (resumen por barrido y
centro, N1 por temperatura, frontera de N3, equipos) y 3 MD (mallas de N3 y
N4 y `ronda1_resumen.md` con tablas y conclusiones). Cada numero sale de un
archivo generado. Se ejecuta como script, no como modulo.
"""
from __future__ import annotations

import csv
from pathlib import Path

from ronda1_reporte2 import (BARRIDOS, N1_VARS, STATS, celda, centros_de,
                             confiable, fmt, grupo, leer_filas,
                             n1_por_temperatura, n3_frontera, n3_mallas,
                             n4_mallas, num, percentiles, resumen_por,
                             tiempo_agotado)

_DIR = Path(__file__).resolve().parent
OUT = _DIR.parents[1] / "resultados" / "2026-10-14_sens1_ronda1"
MAGS = (("dh_turb", "dh_turb [kJ/kg]"), ("Wnet_m_b", "Wnet/m_b [kW por kg/s]"),
        ("Qin", "Qi/m_b [kW por kg/s]"), ("Qreg_Qi", "Qreg/Qi"),
        ("Qout_m_b", "Qout/m_b [kW por kg/s]"), ("ratio_P", "P_alta/P_baja"))
CM = {
    "res": ["barrido", "centro", "n_puntos", "n_kalina", "n_corregible",
            "n_inviable", "n_no_convergio", "n_kalina_confiable",
            "n_kalina_fuera_rango", "eta_min_pct", "eta_mediana_pct",
            "eta_max_pct"],    "n1": (["t_fuente_C", "t_fuente_K", "n_puntos", "n_kalina_confiable",
            "n_kalina_fuera_rango"]
           + [f"{v}_{s}" for v in N1_VARS for s in STATS]
           + ["eta_max", "eta_max_id"] + [f"eta_max_{v}" for v in N1_VARS]),
    "n3": ["T_sumidero", "T_sumidero_C", "eps_cond", "P_baja_min", "eta",
           "estado"],
    "eq": ["barrido", "centro", "magnitud", "n", "minimo", "mediana",
           "maximo"]}


def _escribir(path, cols: list, filas: list) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)


def _pct(x) -> str:
    return "—" if x is None else f"{x:.2f}"


def _tabla(cab: list, cel: list) -> list:
    return ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)] + \
           ["| " + " | ".join(c) + " |" for c in cel]


def _mag(nombre: str, f: dict):
    def d(a, b):
        a, b = num(a), num(b)
        return None if a is None or not b else a / b
    return {"dh_turb": lambda: num(f.get("dh_turb")),
            "Wnet_m_b": lambda: d(f.get("Wnet"), f.get("m_b")),
            "Qin": lambda: d(f.get("Qi"), f.get("m_b")),
            "Qreg_Qi": lambda: d(f.get("Qreg"), f.get("Qi")),
            "Qout_m_b": lambda: d(f.get("Qout"), f.get("m_b")),
            "ratio_P": lambda: d(f.get("P_alta"), f.get("P_baja"))}[nombre]()


def equipos_filas(filas: list, barrido: str, centro: str) -> list:
    """min/mediana/max de cada magnitud entre KALINA confiables."""
    g = [f for f in grupo(filas, barrido, centro) if confiable(f)]
    out = []
    for nombre, etiqueta in MAGS:
        q = percentiles([v for v in (_mag(nombre, f) for f in g)
                         if v is not None])
        out.append(dict(barrido=barrido, centro=centro, magnitud=etiqueta,
                        n=q["n"], minimo=q["minimo"], mediana=q["mediana"],
                        maximo=q["maximo"]))
    return out


def _mds_tablas(res, n1, n3, eq) -> list:
    r1 = [[r["barrido"], r["centro"], str(r["n_puntos"]), str(r["n_kalina"]),
           str(r["n_corregible"]), str(r["n_inviable"]),
           str(r["n_no_convergio"]), str(r["n_kalina_confiable"]),
           str(r["n_kalina_fuera_rango"]), _pct(r["eta_min_pct"]),
           _pct(r["eta_mediana_pct"]), _pct(r["eta_max_pct"])] for r in res]
    r2 = [[f"{r['t_fuente_C']:.0f}", str(r["n_puntos"]),
           str(r["n_kalina_confiable"]), str(r["n_kalina_fuera_rango"]),
           f"{fmt(r['P_alta_p10'])}–{fmt(r['P_alta_p90'])}",
           f"{fmt(r['P_baja_p10'])}–{fmt(r['P_baja_p90'])}",
           f"{fmt(r['x_b_p10'])}–{fmt(r['x_b_p90'])}",
           f"{fmt(r['T_sumidero_p10'])}–{fmt(r['T_sumidero_p90'])}",
           _pct(100 * r["eta_max"] if r["eta_max"] is not None else None),
           r["eta_max_id"] or "—"] for r in n1]
    r3 = [[f"{r['T_sumidero_C']:.0f}", f"{r['eps_cond']:.2f}",
           fmt(r["P_baja_min"]),
           _pct(100 * r["eta"] if r["eta"] is not None else None),
           r["estado"]] for r in n3]
    r4 = [[r["barrido"], r["centro"], r["magnitud"], str(r["n"]),
           fmt(r["minimo"]), fmt(r["mediana"]), fmt(r["maximo"])] for r in eq]
    return [
        "## 1. Resumen por barrido y centro", "",
        *_tabla(["barrido", "centro", "puntos", "KALINA", "CORR", "INV",
                 "NOCONV", "confiables", "fuera rango", "eta min [%]",
                 "eta med [%]", "eta max [%]"], r1), "",
        "## 2. N1 — ventana de presiones por temperatura de fuente", "",
        *_tabla(["T [C]", "puntos", "conf", "fuera", "P_alta p10-p90",
                 "P_baja p10-p90", "x_b p10-p90", "T_sum p10-p90",
                 "eta_max [%]", "punto eta_max"], r2), "",
        "## 3. N3 — frontera del condensador (P_baja minima con KALINA)", "",
        *_tabla(["T_sum [C]", "eps_cond", "P_baja min [kPa]", "eta [%]",
                 "estado"], r3), "",
        "Mallas: ver `ronda1_N3_mallas.md` y `ronda1_N4_mallas.md`.", "",
        "## 4. Equipos (min / mediana / max entre KALINA confiables)", "",
        *_tabla(["barrido", "centro", "magnitud", "n", "minimo", "mediana",
                 "maximo"], r4), ""]


def _conclusiones(n1, n3, filas) -> list:
    out = ["## 5. Conclusiones", "", "### N1 — ventana por temperatura", ""]
    con = [r for r in n1 if r["n_kalina_confiable"] > 0]
    if con:
        out.append(f"- KALINA confiable en {len(con)} de {len(n1)} niveles "
                   f"({con[0]['t_fuente_C']:.0f} a {con[-1]['t_fuente_C']:.0f}"
                   " C).")
        mx = max((r for r in n1 if r["eta_max"] is not None),
                 key=lambda r: r["eta_max"], default=None)
        if mx:
            out.append(f"- eta maxima {100 * mx['eta_max']:.2f}% a "
                       f"T={mx['t_fuente_C']:.0f} C (punto {mx['eta_max_id']}:"
                       f" P_alta={fmt(mx['eta_max_P_alta'])}, "
                       f"P_baja={fmt(mx['eta_max_P_baja'])}, "
                       f"x_b={fmt(mx['eta_max_x_b'])}, "
                       f"T_sum={fmt(mx['eta_max_T_sumidero'])} K).")
        out.append("- Ventanas p10-p90 por nivel: ver tabla de la seccion 2 y "
                   "`ronda1_N1_por_temperatura.csv`.")
    else:
        out.append("- Ningun KALINA confiable en N1.")
    por_ts = {}
    for r in n3:
        if r["estado"] == "kalina":
            por_ts.setdefault(r["T_sumidero"], []).append(r)
    out += ["", "### N3 — menor eps_cond que sirve por clima", ""]
    for ts in sorted(por_ts) or [None]:
        if ts is None:
            out.append("- Ningun KALINA en N3.")
            break
        r = min(por_ts[ts], key=lambda d: d["eps_cond"])
        out.append(f"- T={ts - 273.15:.0f} C: eps_cond min "
                   f"{r['eps_cond']:.2f} con KALINA a P_baja="
                   f"{fmt(r['P_baja_min'])} kPa (eta "
                   f"{100 * r['eta']:.2f}%).")
    out += ["", "### N4 — KALINA confiable con P_alta <= 2000 kPa", ""]
    for c in ("C1", "C2"):
        g = [f for f in filas if f.get("barrido") == "N4" and f.get("centro") == c
             and confiable(f) and (num(f.get("P_alta")) or 9e9) <= 2000.0]
        etas = [num(f.get("eta")) for f in g if num(f.get("eta")) is not None]
        out.append(f"- {c}: {len(g)} KALINA con P_alta<=2000 kPa; eta max "
                   f"{100 * max(etas):.2f}%." if etas
                   else f"- {c}: ninguna KALINA confiable con P_alta<=2000.")
    return out


def main() -> None:
    filas = leer_filas(OUT / "ronda1_filas.csv")
    res, eq = [], []
    for b in BARRIDOS:
        cs = centros_de(filas, b)
        for c in cs + (["TOTAL"] if len(cs) > 1 else []):
            res.append(resumen_por(filas, b, c))
            eq += equipos_filas(filas, b, c)
    n1 = n1_por_temperatura(filas)
    n3 = n3_frontera(filas)
    to = tiempo_agotado(filas)
    _escribir(OUT / "ronda1_resumen_barridos.csv", CM["res"], res)
    _escribir(OUT / "ronda1_N1_por_temperatura.csv", CM["n1"], n1)
    _escribir(OUT / "ronda1_N3_frontera.csv", CM["n3"], n3)
    _escribir(OUT / "ronda1_equipos.csv", CM["eq"], eq)
    doc = ["# Sensibilidad 1 — Ronda 1 (barridos N1, N3, N4)", "",
           "**Fecha:** 2026-10-14 · **Motor:** teqp · **m_b:** 1.0 · "
           "**t_amb_diseno:** T_sumidero de cada punto. **KALINA confiable:** "
           "clase KALINA, `fuera_rango` falso/vacio y `eta_*`/`eps_*` en "
           "[0.40, 0.95]; **KALINA fuera de rango** se reporta aparte.", ""]
    doc += _mds_tablas(res, n1, n3, eq) + _conclusiones(n1, n3, filas)
    doc += ["", "### Puntos con tiempo agotado (tope 600 s)", "",
            *(to or ["- Ninguno."]), ""]
    (OUT / "ronda1_N3_mallas.md").write_text(
        "\n".join(["# N3 — mallas de clases por T_sumidero", "",
                   "Letra: K=KALINA, c=CORREGIBLE, i=INVIABLE, "
                   "n=NO_CONVERGIO; minuscula si el punto esta fuera de rango.",
                   ""] + n3_mallas(filas)) + "\n", encoding="utf-8")
    (OUT / "ronda1_N4_mallas.md").write_text(
        "\n".join(["# N4 — mallas de clase y eta por centro", ""]
                  + n4_mallas(filas)) + "\n", encoding="utf-8")
    (OUT / "ronda1_resumen.md").write_text("\n".join(doc) + "\n",
                                           encoding="utf-8")
    print(f"escrito: 4 CSV + 3 MD en {OUT} ({len(filas)} puntos; "
          f"{len(to)} grupo(s) con tiempo agotado)", flush=True)


if __name__ == "__main__":
    main()
