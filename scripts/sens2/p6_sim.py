# -*- coding: utf-8 -*-
"""Sens2 etapa B - P(KALINA) con eps_cond perturbado de forma simetrica (barrido SIM) frente a U1 escenario A.

Entrada: s2b_sim_filas.csv (48 puntos por centro, eps_cond centrado en 0.90 y +-0.05) y u1_filas.csv (escenario U1A, eps_cond centrado en el tope
0.95 y solo hacia abajo). Por centro: n, puntos KALINA, P(KALINA) con intervalo de Wilson de 95 %, clases, y la misma P de U1A. Los NO_CONVERGIO
cuentan como no KALINA. Salidas en resultados/2026-10-18_sens2_F1: p6_sim.csv y p6_sim.md.
"""
import os
import sys

import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
import p6_comun as K  # noqa: E402

ENT = os.environ.get("S2B_DIR", os.path.join(RAIZ, "resultados", "2026-10-18_sens2_B"))
SAL = os.environ.get("S2B_OUT", os.path.join(RAIZ, "resultados", "2026-10-18_sens2_F1"))
U1 = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_U1", "u1_filas.csv")


def _fila(g, centro, escenario):
    n, k = len(g), int((g["clasificacion"] == "KALINA").sum())
    lo, hi = K.wilson(k, n)
    return dict(centro=centro, escenario=escenario, n=n, n_kalina=k, p_kalina=k / n if n else float("nan"), ic_lo=lo, ic_hi=hi,
                n_corregible=int((g["clasificacion"] == "CORREGIBLE").sum()), n_inviable=int((g["clasificacion"] == "INVIABLE").sum()),
                n_no_convergio=int((g["clasificacion"] == "NO_CONVERGIO").sum()))


def main():
    ruta = os.path.join(ENT, "s2b_sim_filas.csv")
    if not os.path.exists(ruta):
        print("sin s2b_sim_filas.csv: nada que analizar")
        return 0
    s = pd.read_csv(ruta)
    u = pd.read_csv(U1)
    u = u[u["barrido"] == "U1A"]
    filas = []
    for c in ("C1", "C2", "C3", "C4"):
        for g, esc in ((s[s["centro"] == c], "SIM (eps_cond 0.90 +-0.05)"), (u[u["centro"] == c], "U1A (eps_cond 0.95 solo hacia abajo)")):
            if len(g):
                filas.append(_fila(g, c, esc))
    t = pd.DataFrame(filas)
    os.makedirs(SAL, exist_ok=True)
    t.to_csv(os.path.join(SAL, "p6_sim.csv"), index=False, encoding="utf-8", lineterminator="\r\n")
    md = ["# Sens2 etapa B - P(KALINA) con eps_cond simetrico", "",
          "SIM centra eps_cond en 0.90 y lo perturba +-0.05 (uniforme); las otras nueve variables igual que en U1A. U1A centra eps_cond en el tope 0.95 y solo puede bajar. "
          "Los NO_CONVERGIO cuentan como no KALINA. Intervalo de Wilson de 95 %.", "",
          "| centro | escenario | n | KALINA | P(KALINA) | IC 95 % | CORREGIBLE | INVIABLE | NO_CONVERGIO |", "|---|---|---|---|---|---|---|---|---|"]
    md += ["| %s | %s | %d | %d | %.2f | %.2f a %.2f | %d | %d | %d |" % (r.centro, r.escenario, r.n, r.n_kalina, r.p_kalina, r.ic_lo, r.ic_hi, r.n_corregible,
                                                                      r.n_inviable, r.n_no_convergio) for r in t.itertuples()]
    with open(os.path.join(SAL, "p6_sim.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    print("sim: %d filas" % len(t))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
