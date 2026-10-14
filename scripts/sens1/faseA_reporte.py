"""Sensibilidad 1, Fase A — reporte del barrido OFAT (`faseA_filas.csv`).

Escribe en `resultados/2026-10-14_sens1_faseA/`:
- `faseA_resumen_variables.csv` (una fila por centro y variable),
- `faseA_resumen.md` (clase del punto base, tablas de rangos KALINA por centro,
  ranking de variables por amplitud de η, estadísticas para preselección de
  equipos y conteo de puntos genuinos).
Cada número sale del CSV; no se inventa nada.
Se ejecuta como script, no como módulo.
"""
from __future__ import annotations

from pathlib import Path

from faseA_reporte2 import (CENTROS, VARIABLES, amplitudes_eta, agrupar,
                            clase, escalones, escribir_resumen_variables,
                            estadisticas_equipos, es_genuino, es_kalina, fmt,
                            leer_filas, num, por_centro)

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
OUT = _RAIZ / "resultados" / "2026-10-14_sens1_faseA"
FILAS = OUT / "faseA_filas.csv"
RESUMEN = OUT / "faseA_resumen.md"
RESUMEN_VAR = OUT / "faseA_resumen_variables.csv"


def _borde(r) -> str:
    return "borde del barrido" if r is None else f'{num(r["valor"]):g} → {clase(r)}'


def _pct(x) -> str:
    return "—" if x is None else f"{100 * x:.4f}"


def _tabla_centro(g: dict, centro: str) -> list:
    out = ["| variable | n KALINA | valores KALINA | η min [%] | η max [%] | "
           "↓ deja KALINA | ↑ deja KALINA | contiguo |",
           "|---|---|---|---|---|---|---|---|"]
    for var in VARIABLES:
        rows = g.get((centro, var), [])
        if not rows:
            out.append(f"| {var} | 0 | — | — | — | — | — | — |")
            continue
        esc, (nk, emin, emax, _) = escalones(rows), amplitudes_eta(rows)
        rango = ("—" if esc["min"] is None
                 else f'{esc["min"]:g}–{esc["max"]:g}')
        cont = "—" if esc["contiguo"] is None else ("sí" if esc["contiguo"]
                                                    else "no")
        out.append(f"| {var} | {nk} | {rango} | {_pct(emin)} | {_pct(emax)} | "
                   f'{_borde(esc["abajo"])} | {_borde(esc["arriba"])} | {cont} |')
    return out


def _ranking(g: dict, centro: str) -> list:
    filas = []
    for var in VARIABLES:
        nk, _, _, amp = amplitudes_eta(g.get((centro, var), []))
        filas.append((var, amp, nk))
    filas.sort(key=lambda t: (t[1] is None, -(t[1] or 0.0)))
    out = ["| puesto | variable | n KALINA | amplitud η [pp] |",
           "|---|---|---|---|"]
    for i, (var, amp, nk) in enumerate(filas, 1):
        out.append(f"| {i} | {var} | {nk} | "
                   f"{'—' if amp is None else f'{100 * amp:.4f}'} |")
    return out


def _equipos(g: dict, centro: str) -> list:
    rows = [r for (c, _), rs in g.items() if c == centro for r in rs]
    e = estadisticas_equipos(rows)
    return ["| magnitud | mínimo entre KALINA | máximo entre KALINA |",
            "|---|---|---|",
            f'| dh_turb [kJ/kg] | {fmt(e["dh_turb"][0])} | '
            f'{fmt(e["dh_turb"][1])} |',
            f'| Wnet [kW por kg/s] | {fmt(e["Wnet"][0])} | {fmt(e["Wnet"][1])} |',
            f'| Qreg/Qi | {fmt(e["Qreg_Qi"][0])} | {fmt(e["Qreg_Qi"][1])} |',
            f'| m_O2 | {fmt(e["m_O2"][0])} | {fmt(e["m_O2"][1])} |']


def _base(filas: list, centro: str) -> str:
    for f in filas:
        if f.get("centro") == centro and f.get("variable") == "base":
            return f'{clase(f)} (η {_pct(num(f.get("eta"))) if num(f.get("eta")) is not None else "—"} %)'
    return "no presente"


def _conteos(centros: dict) -> list:
    out = ["| centro | puntos | KALINA | CORREGIBLE | INVIABLE | NO_CONVERGIO "
           "| genuinos |",
           "|---|---|---|---|---|---|---|"]
    for c in CENTROS:
        rs = centros.get(c, [])
        cuenta = {k: sum(1 for r in rs if clase(r) == k)
                  for k in ("KALINA", "CORREGIBLE", "INVIABLE",
                            "NO_CONVERGIO")}
        gen = sum(1 for r in rs if es_genuino(r))
        out.append(f'| {c} | {len(rs)} | {cuenta["KALINA"]} | '
                   f'{cuenta["CORREGIBLE"]} | {cuenta["INVIABLE"]} | '
                   f'{cuenta["NO_CONVERGIO"]} | {gen} |')
    return out


def main() -> None:
    filas = leer_filas(FILAS)
    g = agrupar(filas)
    centros = por_centro(filas)
    g_var = escribir_resumen_variables(g, RESUMEN_VAR)
    n_kal = sum(1 for r in filas if es_kalina(r))
    base1, base2 = _base(filas, "C1"), _base(filas, "C2")
    doc = [
        "# Sensibilidad 1 — Fase A: barridos OFAT alrededor de 2 centros", "",
        f"**Fecha:** 2026-10-14 · **Motor:** teqp · **m_b:** 1.0 fijo · "
        f"**t_amb_diseno:** T_sumidero de cada punto (piso de O2).",
        f"**Puntos:** {len(filas)} ({', '.join(f'{c}={len(centros.get(c, []))}' for c in CENTROS)}) "
        f"· KALINA total: {n_kal}.",
        "Se eliminan combinaciones repetidas: el punto base (misma combinación "
        "que aparece en cada barrido) se evalúa UNA vez por centro con "
        "`variable=\"base\"`.", "",
        "## 1. Clase del punto base", "",
        f"- **C1** (Húsavík): {base1}",
        f"- **C2** (ancla A*, clima del profesor): {base2}", "",
        "## 2. Conteo de puntos por centro y clase", "",
        *_conteos(centros), "",
        "## 3. Rangos KALINA por variable", ""]
    for c in CENTROS:
        doc += [f"### Centro {c}", "", *_tabla_centro(g, c), ""]
    doc += ["## 4. Ranking por amplitud de η entre los puntos KALINA (pp)", ""]
    for c in CENTROS:
        doc += [f"### Centro {c}", "", *_ranking(g, c), ""]
    doc += ["## 5. Preselección de equipos (mín/máx entre los KALINA)", ""]
    for c in CENTROS:
        doc += [f"### Centro {c}", "", *_equipos(g, c), ""]
    doc += ["## 6. Puntos genuinos (convergio=True y clase ≠ NO_CONVERGIO)", ""]
    for c in CENTROS:
        rs = centros.get(c, [])
        gen = sum(1 for r in rs if es_genuino(r))
        doc.append(f"- **{c}**: {gen} genuinos de {len(rs)}; los N2 espurios "
                   f"(convergio=True y clase NO_CONVERGIO) no cuentan.")
    doc += ["", f"Resumen por variable en `{RESUMEN_VAR.name}` "
            f"({g_var} filas)."]
    RESUMEN.write_text("\n".join(doc) + "\n", encoding="utf-8")
    print(f"escrito: {RESUMEN} ({len(doc)} líneas) y {RESUMEN_VAR} "
          f"({g_var} filas)", flush=True)


if __name__ == "__main__":
    main()
