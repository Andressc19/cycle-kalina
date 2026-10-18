# -*- coding: utf-8 -*-
"""Sens2 R2 - repite el contraste B de R1 (fronteras de una variable) exigiendo ademas que las 5 eficiencias
y efectividades del punto viejo esten a +-0.10 de las del centro (valores de la base de Sens1), y compara con el
acuerdo de un predictor trivial (la clase mayoritaria del mismo subconjunto)."""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_contraste import _par_ventana, dist_sin_v, leer  # noqa: E402
from r1_filtro import CERCANO, SALIDA  # noqa: E402

EFIC = ["eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond"]
BASE = {"C1 Husavik": [0.85, 0.80, 0.85, 0.75, 0.95], "C2 ancla A*": [0.85, 0.75, 0.85, 0.75, 0.95],
        "C3 caliente 150 C": [0.85, 0.80, 0.85, 0.75, 0.95], "C4 frio 110 C": [0.85, 0.80, 0.85, 0.75, 0.95]}
TOL_EF = 0.10


def predecir(fr, t, val):
    par = _par_ventana(fr, t.centro, t.variable)
    if t.forma == "ventana" and par is not None:
        dentro = (val >= par[0]) & (val <= par[1])
        baja = fr[(fr["centro"] == t.centro) & (fr["variable"] == t.variable) & (fr["forma"] == "ventana") &
                  (fr["valor_frontera"] == par[0])]["direccion"].iloc[0]
        return dentro if baja == "a KALINA" else ~dentro
    return val >= t.valor_frontera if t.direccion == "a KALINA" else val < t.valor_frontera


def main():
    puntos, _, fronteras = leer()
    fr = fronteras[fronteras["forma"].isin(["escalon", "ventana"])]
    filas = []
    for t in fr.itertuples():
        sub = puntos[puntos["centro"] == t.centro]
        ef = np.ones(len(sub), bool)
        for e, b in zip(EFIC, BASE[t.centro]):
            if e != t.variable:
                ef &= (sub[e] - b).abs().to_numpy() <= TOL_EF + 1e-9
        sel = sub[(dist_sin_v(sub, t.centro, t.variable) <= CERCANO) & ef]
        real = (sel["clasificacion"] == "KALINA").to_numpy(bool)
        n = len(sel)
        ac = int((predecir(fr, t, sel[t.variable].to_numpy(float)) == real).sum())
        base = int(max(real.sum(), n - real.sum()))
        filas.append([t.centro, t.variable, t.forma, t.direccion, t.valor_frontera, n, ac,
                      "" if n < 5 else ac / n, "" if n < 5 else base / n,
                      "" if n < 5 else ac / n - base / n, "n insuficiente" if n < 5 else ""])
    c = pd.DataFrame(filas, columns=["centro", "variable", "forma", "direccion", "valor_frontera", "n", "aciertos",
                                     "acuerdo", "acuerdo_clase_mayoritaria", "ganancia", "nota"])
    c.to_csv(os.path.join(SALIDA, "r2_fronteras_eficiencias.csv"), index=False)
    ok = c[c["n"] >= 5]
    g = ok["aciertos"].sum() / ok["n"].sum()
    gb = (ok["acuerdo_clase_mayoritaria"].astype(float) * ok["n"]).sum() / ok["n"].sum()
    grande = ok[ok["n"] >= 30]
    print("filas n>=5: %d de %d | acuerdo global %.3f (%d/%d) | clase mayoritaria %.3f | ganancia %+.3f" % (
        len(ok), len(c), g, ok["aciertos"].sum(), ok["n"].sum(), gb, g - gb))
    if len(grande):
        print("filas n>=30: %d | acuerdo %.3f | mayoritaria %.3f" % (
            len(grande), grande["aciertos"].sum() / grande["n"].sum(),
            (grande["acuerdo_clase_mayoritaria"].astype(float) * grande["n"]).sum() / grande["n"].sum()))
    print(ok.sort_values("n", ascending=False).head(14)[["centro", "variable", "direccion", "valor_frontera", "n", "acuerdo",
                                                         "acuerdo_clase_mayoritaria"]].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
