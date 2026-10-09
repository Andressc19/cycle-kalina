"""M10b — `REPORTE_M10b.md`, cifras tomadas de los CSV.

Lenguaje llano; no inventa nada: cada número sale de `m10b_ofat_xb.csv` o
`m10b_malla_xb_pbaja.csv`. `pbaja_min_kalina` y `criterio_bajo` son las cifras
que `m10b_verificar.py` recalcula.
"""
from __future__ import annotations

import sys  # noqa: E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

import m10_datos as d10  # noqa: E402
import m10b_datos as d  # noqa: E402

RUTA = d.OUT / "REPORTE_M10b.md"
CRIT = ("P_baja", "clasificacion", "eta", "m_O1", "m_O2", "m_O5",
        "codigos_falla", "fuera_rango")


def _tabla(cols: list, filas: list) -> list:
    out = ["| " + " | ".join(cols) + " |",
           "|" + "|".join("---" for _ in cols) + "|"]
    for f in filas:
        out.append("| " + " | ".join(
            "—" if f.get(c) in (None, "") else str(f.get(c)) for c in cols) + " |")
    return out


def _fmt(v, n=4):
    return "—" if v is None else f"{v:.{n}g}"


def _ma() -> list:
    return d10.leer(d.OUT / "m10b_malla_xb_pbaja.csv")


def pbaja_min_kalina(ma: list) -> dict:
    """{x_b: P_baja mínima KALINA o None} de la malla."""
    res = {}
    for xb in d.XB_MALLA:
        kal = [f["P_baja"] for f in ma if f["x_b"] == xb and d10.es_kalina(f)]
        res[xb] = min(kal) if kal else None
    return res


def _margen_neg(f) -> str | None:
    """Primer margen negativo (O1/O2/O3/O5), o None."""
    peor, val = None, 0.0
    for k in ("m_O1", "m_O2", "m_O3", "m_O5"):
        v = f.get(k)
        if v is not None and v < val:
            peor, val = k, v
    return peor


def criterio_bajo(ma: list) -> dict:
    """{codigo: [n_filas, fila_ejemplo]} con x_b < 0.55 (la de margen peor)."""
    res = {}
    for f in ma:
        if f["x_b"] >= d.XB_BAJO:
            continue
        for cod in (f.get("codigos_falla") or "").split(","):
            cod = cod.strip()
            if not cod:
                continue
            cur = res.get(cod)
            if cur is None:
                res[cod] = [1, f]
            else:
                cur[0] += 1
                if _peor(f, cur[1]):
                    cur[1] = f
    return res


def _peor(f, g) -> bool:
    mf, mg = _margen_neg(f), _margen_neg(g)
    return (f.get(mf) if mf else 0.0) < (g.get(mg) if mg else 0.0)


def _seccion_por_xb(ma: list) -> list:
    out = []
    for xb in d.XB_MALLA:
        sub = sorted((f for f in ma if f["x_b"] == xb), key=lambda f: f["P_baja"])
        etiq = (" — **x_b bajo (< 0.55), fuera de lo habitual en Kalina**"
                if xb < d.XB_BAJO else "")
        out += [f"### x_b = {xb:.2f}{etiq}", "",
                *_tabla(list(CRIT), [dict(f, eta=_fmt(f.get("eta")),
                                         m_O1=_fmt(f.get("m_O1")),
                                         m_O2=_fmt(f.get("m_O2")),
                                         m_O5=_fmt(f.get("m_O5")))
                                     for f in sub]), ""]
    return out


def _seccion_pmin(ma: list) -> list:
    pm = pbaja_min_kalina(ma)
    out = ["| x_b | P_baja mín KALINA (kPa) | n KALINA | etiqueta |",
           "|---|---|---|---|"]
    for xb in d.XB_MALLA:
        sub = [f for f in ma if f["x_b"] == xb]
        nk = sum(1 for f in sub if d10.es_kalina(f))
        et = "x_b bajo (<0.55)" if xb < d.XB_BAJO else ""
        pb = "—" if pm[xb] is None else f"{pm[xb]:.0f}"
        out.append(f"| {xb:.2f} | {pb} | {nk}/{len(sub)} | {et} |")
    return out


def _seccion_criterio(ma: list) -> list:
    bajos = [f for f in ma if f["x_b"] < d.XB_BAJO]
    nc = sorted({f["x_b"] for f in bajos if not f.get("convergio")})
    conv = [f for f in bajos if f.get("convergio")]
    out = []
    if nc:
        out.append(f"- Con x_b = {', '.join(f'{x:.2f}' for x in nc)} el solver "
                   f"**no converge** (NO_CONVERGIO sin códigos): el ciclo no "
                   f"cierra y no hay margen que evaluar.")
    if conv:
        for k in ("m_O1", "m_O2", "m_O3", "m_O5"):
            vals = [f.get(k) for f in conv if f.get(k) is not None]
            if not vals:
                continue
            neg = sum(1 for v in vals if v < 0)
            if neg:
                out.append(f"- **{k[2:]} sí falla** en x_b < 0.55: margen de "
                           f"{min(vals):.4g} a {max(vals):.4g} "
                           f"({neg} de {len(vals)} filas convergidas).")
            else:
                out.append(f"- {k[2:]} no falla en x_b < 0.55 "
                           f"(margen mínimo {min(vals):.4g}).")
        otros = sorted({c.strip() for f in conv
                        for c in (f.get("codigos_falla") or "").split(",")
                        if c.strip() and c.strip() not in ("O1", "O2", "O3", "O5")})
        if otros:
            out.append(f"- Además esos puntos convergidos traen otros códigos "
                       f"({', '.join(otros)}): N2 = no genuino; S6/C1/C3 = otras "
                       f"restricciones del solver.")
    if not out:
        out.append(f"Con x_b < 0.55 hay {len(bajos)} filas; ninguna reporta falla.")
    kal = sorted({f["x_b"] for f in ma if d10.es_kalina(f)})
    if kal:
        xk = min(kal)
        out.append(f"- El x_b más bajo con KALINA en la malla es **{xk:.2f}** "
                   f"(P_baja mínima {pbaja_min_kalina(ma)[xk]:.0f} kPa).")
    return out


def escribir() -> int:
    """Escribe `REPORTE_M10b.md` y devuelve su número de líneas."""
    ma = _ma()
    n_of = sum(1 for _f in d10.leer(d.OUT / "m10b_ofat_xb.csv"))
    doc = [
        "# REPORTE M10b — Húsavík con poco amoníaco (x_b 0.30–0.70)",
        "",
        "**Fecha:** 2026-10-09 · **Rama:** `test/barrido_final` · "
        "**Motor:** teqp (protección A+B, bracket tolerante).",
        "",
        "## 1. La pregunta",
        "",
        "M10 barrió x_b de 0.60 a 0.95. ¿Qué pasa con Húsavík si la mezcla tiene "
        "poco amoníaco, entre 0.30 y 0.70? ¿Sigue habiendo KALINA? ¿Con qué "
        "P_baja? ¿Qué criterio falla?",
        "",
        "## 2. Método",
        "",
        f"- OFAT de x_b: `numpy.linspace(0.30, 0.70, 17)` con P_baja 690 y el "
        f"resto en el ancla de Húsavík ({n_of} corridas).",
        f"- Malla x_b × P_baja: x_b {list(d.XB_MALLA)} × P_baja "
        f"{[int(p) for p in d.PB_MALLA]} ({len(ma)} corridas).",
        "- Ancla: P_alta 3300, T_fuente 394.15, T_sumidero 278.15, eta_t 0.90, "
        "eta_p 0.80, eps_hrvg 0.85, eps_reg 0.75, eps_cond 0.95, m_b 1.0; piso "
        "de O2 283.15 K.",
        "- **x_b bajo (< 0.55), fuera de lo habitual en Kalina:** es una "
        "etiqueta de reporte, no un filtro.",
        "",
        "## 3. Por cada x_b de la malla (una tabla por valor)",
        "",
        *_seccion_por_xb(ma),
        "## 4. P_baja mínima KALINA para cada x_b",
        "",
        *_seccion_pmin(ma),
        "",
        "## 5. Qué criterio falla con x_b bajo",
        "",
        *_seccion_criterio(ma),
        "",
        "## 6. Lo que no se sabe",
        "",
        "- La malla muestrea 6 P_baja (200–700 kPa): la P_baja mínima KALINA "
        "real queda entre dos muestras; no se bisecó la frontera.",
        "- El OFAT usa pasos de 0.025 en x_b: la frontera exacta entre clases "
        "queda entre dos muestras.",
        "- Todo es teqp; no se re-confirmó con el motor real.",
        "- Cambiar el ancla (T_fuente, T_sumidero, eta_t/eta_p, eps_*) mueve la "
        "frontera de clase.",
    ]
    RUTA.write_text("\n".join(doc) + "\n", encoding="utf-8")
    return len(doc)
