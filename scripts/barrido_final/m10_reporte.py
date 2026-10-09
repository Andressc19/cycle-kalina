"""M10 — Parte C: `REPORTE_M10.md`, cifras tomadas de los CSV.

Lenguaje llano; no inventa nada: cada número sale de `m10_catalogo.csv`,
`m10_ofat_rangos.csv`, `m10_recorrida_fase3.csv`, `m10_ofat.csv` o
`m10_malla_xb_pbaja.csv`.
"""
from __future__ import annotations

import sys  # noqa: E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

import m10_datos as d  # noqa: E402

RUTA = d.OUT / "REPORTE_M10.md"


def _tabla(cols: list, filas: list) -> list:
    """Tabla markdown sencilla."""
    out = ["| " + " | ".join(cols) + " |",
           "|" + "|".join("---" for _ in cols) + "|"]
    for f in filas:
        out.append("| " + " | ".join(
            "—" if f.get(c) in (None, "") else str(f.get(c)) for c in cols) + " |")
    return out


def _fmt(v, n=4):
    return "—" if v is None else f"{v:.{n}g}"


def _motivo(f) -> str:
    """Criterio + señales A/B/MA que explican un cambio de clase."""
    p = [f"criterio={f.get('codigos_falla') or 'ninguno'}"]
    if f.get("A_verificacion_incompleta"):
        p.append("A: verificación incompleta")
    if f.get("A_recurrencias") not in (None, 0):
        p.append(f"A_recurrencias={f['A_recurrencias']}")
    if f.get("B_verificado") is False:
        p.append("B no verificado")
    if f.get("B_error"):
        p.append(f"B_error={f['B_error']}")
    if f.get("repliegues_lo") or f.get("repliegues_hi"):
        p.append("MA: repliegue de bracket")
    if f.get("fuera_rango"):
        p.append("fuera de rango del motor")
    return "; ".join(p)


def _seccion_f3() -> list:
    """Confirmaciones y cambios de clase de los KALINA de septiembre."""
    f3 = d.leer(d.OUT / "m10_recorrida_fase3.csv")
    n = len(f3)
    conf = sum(1 for f in f3 if f["coincide_clase"])
    cambian = [f for f in f3 if not f["coincide_clase"]]
    confiab = sum(1 for f in f3 if d.confiable(f))
    out = [f"De los **{n}** puntos KALINA de septiembre re-evaluados, **{conf}** "
           f"siguen KALINA (**{confiab}** además confiables: fuera_rango=False y "
           f"B_verificado=True). Cambian de clase: **{len(cambian)}**."]
    if cambian:
        out += ["", *_tabla(
            ["familia", "archivo", "fila", "clase ahora", "códigos", "motivo"],
            [dict(familia=f["familia"], archivo=f["archivo_origen"],
                  fila=f["fila_origen"], **{"clase ahora": f["clasificacion"],
                  "códigos": f.get("codigos_falla"), "motivo": _motivo(f)})
             for f in cambian])]
        out += ["", "(Criterio = código de la restricción que falla, p. ej. O2; "
                    "A = recurrencia/verificación del motor; B = verificación "
                    "B no pasó; MA = bracket tolerante con repliegue.)"]
    else:
        out += ["", "Ninguno cambió de clase: el motor actual (teqp con la "
                    "protección A+B y el bracket tolerante) reproduce la "
                    "clasificación de septiembre en los 97 puntos."]
    return out


def _seccion_rangos(ran: list) -> list:
    """Tabla de rangos de B1, con x_b destacada."""
    out = ["| variable | mín KALINA | máx KALINA | rompe abajo | rompe arriba "
           "| η mín | η máx | n KALINA |",
           "|---|---|---|---|---|---|---|---|"]
    for r in ran:
        fila = (f'| **{r["variable"]}** ' if r["variable"] == "x_b"
                else f'| {r["variable"]} ')
        out.append(fila
                   + f'| {_fmt(r["min_kalina"])} | {_fmt(r["max_kalina"])} '
                   + f'| {r["criterio_bajo"] or "—"} | {r["criterio_alto"] or "—"} '
                   + f'| {_fmt(r["eta_min"])} | {_fmt(r["eta_max"])} '
                   + f'| {r["n_kalina"]} |')
    xb = next((r for r in ran if r["variable"] == "x_b"), None)
    if xb:
        out += ["", f"**x_b (lo que se pedía ampliar):** con el resto en el "
                    f"ancla, el punto es KALINA de x_b = {_fmt(xb['min_kalina'])} "
                    f"a {_fmt(xb['max_kalina'])}; por debajo lo rompe "
                    f"{xb['criterio_bajo'] or '—'} y por arriba "
                    f"{xb['criterio_alto'] or '—'}. En septiembre solo se había "
                    f"mirado 0.78–0.86."]
    return out


def _seccion_malla() -> list:
    """P_baja mínima KALINA para cada x_b de B2."""
    ma = d.leer(d.OUT / "m10_malla_xb_pbaja.csv")
    out = ["| x_b | P_baja mín KALINA | P_baja máx KALINA | n KALINA | total |",
           "|---|---|---|---|---|"]
    for xb in d.XB_MALLA:
        sub = [f for f in ma if f["x_b"] == xb]
        kal = [f for f in sub if d.es_kalina(f)]
        pbs = [f["P_baja"] for f in kal]
        out.append(f'| {xb:.2f} | {min(pbs):.0f} | {max(pbs):.0f} '
                   f'| {len(kal)} | {len(sub)} |' if pbs
                   else f'| {xb:.2f} | — | — | 0 | {len(sub)} |')
    kal = [f for f in ma if d.es_kalina(f)]
    if kal:
        lo = min(f["P_baja"] for f in kal)
        filas = [f for f in kal if f["P_baja"] == lo]
        out += ["", f"El P_baja KALINA más bajo de la malla es **{lo:.0f} kPa**, "
                    f"con x_b = {', '.join(f'{f['x_b']:.2f}' for f in filas)}."]
    return out


def escribir(cat: list, ran: list) -> int:
    """Escribe `REPORTE_M10.md` y devuelve su número de líneas."""
    doc = [
        "# REPORTE M10 — Húsavík revisitado (Fase 3 + barridos que faltaban)",
        "",
        "**Fecha:** 2026-10-09 · **Rama:** `test/barrido_final` · "
        "**Motor:** teqp (protección A+B, bracket tolerante).",
        "",
        "## 1. La pregunta",
        "",
        "¿Con el motor actual (después del bracket tolerante y de la protección "
        "A+B de teqp), se confirman los KALINA que en septiembre encontró la Fase "
        "3 de Húsavík? ¿Y qué pasa en las variables que entonces no se movieron "
        "(T_fuente, T_sumidero, P_alta, P_baja, x_b fino, eta_p, eps_hrvg) y en "
        "una malla x_b × P_baja?",
        "",
        "## 2. Catálogo (una fila por familia)",
        "",
        *_tabla(["familia", "origen", "variables movidas", "piso O2", "n",
                 "KALINA sept", "KALINA ahora", "confiables ahora", "coincide",
                 "d_eta_pp medio", "d_eta_pp máx"],
                [dict(familia=c["familia"], origen=c["origen"],
                      **{"variables movidas": c["variables_movidas"],
                         "piso O2": _fmt(c["piso_O2"]), "n": c["n"],
                         "KALINA sept": c["KALINA_sept"],
                         "KALINA ahora": c["KALINA_ahora"],
                         "confiables ahora": c["confiables_ahora"],
                         "coincide": c["coincide"],
                         "d_eta_pp medio": _fmt(c["d_eta_pp_medio_abs"]),
                         "d_eta_pp máx": _fmt(c["d_eta_pp_max_abs"])})
                 for c in cat]),
        "",
        "## 3. ¿Se confirman los KALINA de septiembre?",
        "",
        *_seccion_f3(),
        "",
        "## 4. Rangos de B1 (OFAT de 15 puntos) — x_b destacada",
        "",
        *_seccion_rangos(ran),
        "",
        "## 5. B2 — la malla x_b × P_baja",
        "",
        *_seccion_malla(),
        "",
        "## 6. Lo que no se sabe",
        "",
        "- B1 muestrea 15 puntos por variable: los límites exactos entre clases "
        "quedan entre dos muestras; no se bisecó la frontera.",
        "- Solo se re-evaluaron las filas KALINA de septiembre; los puntos "
        "CORREGIBLE/INVIABLE/no convergidos de entonces no se volvieron a correr.",
        "- B2 usa un ancla fija (T_fuente 394.15, T_sumidero 278.15, "
        "eta_t/eta_p 0.90/0.80, eps_hrvg 0.85, eps_reg 0.75, eps_cond 0.95): "
        "cambiar cualquiera de esas mueve la frontera.",
        "- Todo es teqp; no se re-confirmó con el motor real.",
    ]
    RUTA.write_text("\n".join(doc) + "\n", encoding="utf-8")
    return len(doc)
