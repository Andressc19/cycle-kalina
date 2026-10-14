"""Sensibilidad 1, Fase A — resumen CORREGIDO de los barridos OFAT.

El resumen original (`faseA_resumen_variables.csv`) contaba solo los puntos
propiamente del barrido y dejaba fuera el punto base, que la corrida deduplica
con `variable="base"` (misma combinación que el valor de centro de cada
variable). Aquí, para cada (centro, variable), se AÑADE al conjunto del barrido
la fila base de ese centro, con `valor` = valor base de esa variable, y se
recalcula lo mismo que el resumen original: nº por clase, nº KALINA confiables,
rango KALINA, rango de η entre KALINA, contiguo sí/no, nº INVIABLE.

Escribe en `resultados/2026-10-14_sens1_faseA/`:
- `faseA_resumen_variables_corregido.csv`
- `faseA_resumen_corregido.md`

Cada número sale de `faseA_filas.csv`; no se inventa nada. Se ejecuta como
script, no como módulo.
"""
from __future__ import annotations

import csv
from pathlib import Path

from faseA_reporte2 import (CENTROS, VARIABLES, _CAMPOS_VAR, fila_resumen,
                            leer_filas, num)

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
OUT = _RAIZ / "resultados" / "2026-10-14_sens1_faseA"
FILAS = OUT / "faseA_filas.csv"
CSV_OUT = OUT / "faseA_resumen_variables_corregido.csv"
MD_OUT = OUT / "faseA_resumen_corregido.md"

# Valor de centro (base) de cada variable, por centro (los de la Fase A).
BASES = {
    "C1": dict(T_fuente=394.15, T_sumidero=278.15, P_alta=3300.0, P_baja=690.0,
               x_b=0.82, eta_t=0.85, eta_p=0.80, eps_hrvg=0.85, eps_reg=0.75,
               eps_cond=0.95),
    "C2": dict(T_fuente=403.0, T_sumidero=300.15, P_alta=3000.0, P_baja=563.64,
               x_b=0.50, eta_t=0.85, eta_p=0.75, eps_hrvg=0.85, eps_reg=0.75,
               eps_cond=0.95),
}


def _valor(r):
    v = num(r.get("valor"))
    return -1e9 if v is None else v


def con_base(rows: list, base_fila: dict, valor: float) -> list:
    """Copia de `rows` más la fila base con `valor`, si ese valor no está ya."""
    if any(abs(_valor(r) - valor) < 1e-9 for r in rows):
        return list(rows)
    return list(rows) + [dict(base_fila, valor=valor)]


def _pct(x) -> str:
    return "—" if x is None else f"{x:.4f}"


def _rango(r: dict) -> str:
    if r["valor_min"] is None:
        return "—"
    return f'{num(r["valor_min"]):g}–{num(r["valor_max"]):g}'


def _tabla(resumenes: list) -> list:
    out = ["| variable | n KALINA | KALINA confiables | valores KALINA | "
           "η min [%] | η max [%] | INVIABLE | contiguo |",
           "|---|---|---|---|---|---|---|---|"]
    for r in resumenes:
        cont = "—" if r["contiguo"] is None else ("sí" if r["contiguo"]
                                                  else "no")
        out.append(f'| {r["variable"]} | {r["n_kalina"]} | '
                   f'{r["n_kalina_confiable"]} | {_rango(r)} | '
                   f'{_pct(r["eta_min_pct"])} | {_pct(r["eta_max_pct"])} | '
                   f'{r["n_inviable"]} | {cont} |')
    return out


def main() -> None:
    filas = leer_filas(FILAS)
    grupo = {}
    for f in filas:
        grupo.setdefault((f.get("centro"), f.get("variable")), []).append(f)
    bases = {c: grupo[(c, "base")][0] for c in CENTROS}

    resumenes = {c: [] for c in CENTROS}
    for c in CENTROS:
        resumenes[c].append(fila_resumen(c, "base", grupo[(c, "base")]))
        for var in VARIABLES:
            rows = con_base(grupo.get((c, var), []), bases[c], BASES[c][var])
            resumenes[c].append(fila_resumen(c, var, rows))

    with open(CSV_OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=_CAMPOS_VAR)
        w.writeheader()
        for c in CENTROS:
            w.writerows(resumenes[c])

    doc = [
        "# Sensibilidad 1 — Fase A: resumen CORREGIDO (base incluida en cada "
        "barrido)", "",
        "El resumen original (`faseA_resumen_variables.csv`) no contaba dentro "
        "de cada barrido el punto base (que la corrida deduplica con "
        "`variable=\"base\"`). Aquí se añade la fila base de cada centro al "
        "conjunto de puntos de cada variable, con su `valor` = valor base de "
        "esa variable, y se recalcula todo. Fuente: `faseA_filas.csv`.", ""]
    for c in CENTROS:
        doc += [f"## Centro {c}", "", *_tabla(resumenes[c]), ""]

    def nk(var, c="C1"):
        for r in resumenes[c]:
            if r["variable"] == var:
                return r["n_kalina"]
        return None

    v1, v2 = nk("T_sumidero"), nk("eps_cond")
    doc += [
        "## Verificación (esperado)", "",
        f"- **C1 T_sumidero** → n KALINA = **{v1}** (esperado 3)",
        f"- **C1 eps_cond** → n KALINA = **{v2}** (esperado 1)", ""]
    MD_OUT.write_text("\n".join(doc) + "\n", encoding="utf-8")

    print(f"escrito: {CSV_OUT} y {MD_OUT}", flush=True)
    print(f"VERIF C1 T_sumidero n_kalina={v1} (esperado 3)", flush=True)
    print(f"VERIF C1 eps_cond   n_kalina={v2} (esperado 1)", flush=True)


if __name__ == "__main__":
    main()
