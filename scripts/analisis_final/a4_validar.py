# -*- coding: utf-8 -*-
"""A4 · Corredor de la validación cruzada (TASK_CONTEXT af-A4).

Corre todos los checks de a4_checks.py sobre la tabla canónica y escribe:
  analisis_final/05_validacion/validacion_A4.csv
  analisis_final/05_validacion/checks_A4.md
"""
import os
import sys

import pandas as pd

import a4_checks as C
import a4_checks_b as Cb

CHECKS = C.CHECKS + Cb.CHECKS

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CSV = "analisis_final/05_validacion/validacion_A4.csv"
MD = "analisis_final/05_validacion/checks_A4.md"
COLUMNAS = ["id_check", "caso", "filtro", "cifra", "esperado", "recalculado", "resultado", "nota"]


def _celda(texto):
    return str(texto).replace("|", "\\|").replace("\n", " ")


def main():
    df = pd.read_csv(C.TABLA, low_memory=False)
    filas = []
    for check in CHECKS:
        filas.extend(check(df))
    tabla = pd.DataFrame(filas, columns=COLUMNAS)
    os.makedirs(os.path.dirname(CSV), exist_ok=True)
    tabla.to_csv(CSV, index=False)

    n_ok = int((tabla["resultado"] == C.S).sum())
    n_no = int((tabla["resultado"] == C.N).sum())
    n_ne = int((tabla["resultado"] == C.NE).sum())
    fallos = tabla[tabla["resultado"] == C.N]
    ne = tabla[tabla["resultado"] == C.NE]

    lineas = ["# Checks A4 — validación cruzada contra la tabla canónica", "",
              f"Filas: {len(tabla)} · ✔ {n_ok} · ✘ {n_no} · NO EVALUABLE {n_ne}", "",
              "| " + " | ".join(COLUMNAS) + " |",
              "| " + " | ".join(["---"] * len(COLUMNAS)) + " |"]
    for _, r in tabla.iterrows():
        lineas.append("| " + " | ".join(_celda(r[c]) for c in COLUMNAS) + " |")

    lineas += ["", "## Resumen", "",
               f"- ✔ coinciden: {n_ok}",
               f"- ✘ no coinciden: {n_no}",
               f"- NO EVALUABLE: {n_ne}",
               "", "### Lista de ✘", ""]
    if len(fallos):
        for _, r in fallos.iterrows():
            extra = f" — {r['nota']}" if r["nota"] else ""
            lineas.append(f"- {r['id_check']} · {r['caso']} · {r['cifra']}: esperado "
                          f"{r['esperado']} / recalculado {r['recalculado']}{extra}")
    else:
        lineas.append("- ninguna")

    lineas += ["", "### Lista de NO EVALUABLE", ""]
    if len(ne):
        for _, r in ne.iterrows():
            lineas.append(f"- {r['id_check']} · {r['caso']}: {r['nota']}")
    else:
        lineas.append("- ninguno")

    with open(MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")

    print(f"{CSV}: {len(tabla)} filas")
    print(f"coinciden {n_ok} | no coinciden {n_no} | NO EVALUABLE {n_ne}")
    print("FALLOS:")
    if len(fallos):
        for _, r in fallos.iterrows():
            print(f"  {r['id_check']} {r['caso']} {r['cifra']}: "
                  f"{r['esperado']} / {r['recalculado']}")
    else:
        print("  ninguno")


if __name__ == "__main__":
    main()
