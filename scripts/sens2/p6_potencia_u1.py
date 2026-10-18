# -*- coding: utf-8 -*-
"""Sens2 F1 - A2b, Parte 3: potencia de U1.

Con u1_resumen.csv: por escenario y centro calcula el error tipico sqrt(p(1-p)/n), el
ancho del intervalo de Wilson, y el n necesario para una semiamplitud de +/-0.05 y
+/-0.10 con la p observada (n = 1.96^2 p(1-p)/h^2, redondeo hacia arriba) y con el peor
caso p = 0.5 (tabla precision). Para la comparacion entre lotes (U1A frente a U1A2 por
centro) calcula la diferencia de proporciones, el z con sqrt(phat(1-phat)(2/n)) (phat
combinada; z vacio si phat es 0 o 1) y la diferencia minima detectable con potencia
80 % y nivel 5 % (2.8 sqrt(2 phat(1-phat)/n), y con phat = 0.5 como peor caso) (tabla
entre_lotes). Salidas: p6_potencia_u1.csv y p6_potencia_u1.md.
"""
import math
import os

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
U1 = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_U1", "u1_resumen.csv")
SALIDA = os.path.join(RAIZ, "resultados", "2026-10-18_sens2_F1")
ESC = ["U1A", "U1A2", "U1Ap", "U1B", "U1C"]
CENTROS = ["C1", "C2", "C3", "C4"]
Z95 = 1.96
Z_POT = 2.8
COLS = ["tabla", "escenario", "centro", "n", "p_kalina", "error_tipico", "ancho_wilson",
        "n_obs_h05", "n_obs_h10", "n_peor_h05", "n_peor_h10", "p1", "p2", "dif", "z",
        "d_min", "d_min_peor"]


def n_necesario(p, h):
    return int(math.ceil(Z95 ** 2 * p * (1.0 - p) / (h ** 2)))


def filas_precision(d):
    filas = []
    for esc in ESC:
        for cen in CENTROS:
            r = d[(d["escenario"] == esc) & (d["centro"] == cen)].iloc[0]
            p, n = float(r["p_kalina"]), int(r["n"])
            filas.append({"tabla": "precision", "escenario": esc, "centro": cen,
                          "n": n, "p_kalina": p,
                          "error_tipico": math.sqrt(p * (1.0 - p) / n),
                          "ancho_wilson": float(r["p_hi"]) - float(r["p_lo"]),
                          "n_obs_h05": n_necesario(p, 0.05),
                          "n_obs_h10": n_necesario(p, 0.10),
                          "n_peor_h05": n_necesario(0.5, 0.05),
                          "n_peor_h10": n_necesario(0.5, 0.10)})
    return filas


def filas_entre_lotes(d):
    filas = []
    for cen in CENTROS:
        a = d[(d["escenario"] == "U1A") & (d["centro"] == cen)].iloc[0]
        b = d[(d["escenario"] == "U1A2") & (d["centro"] == cen)].iloc[0]
        p1, p2, n1, n2 = float(a["p_kalina"]), float(b["p_kalina"]), int(a["n"]), int(b["n"])
        phat = (p1 * n1 + p2 * n2) / (n1 + n2)
        n = n1
        dif = p1 - p2
        if 0.0 < phat < 1.0:
            z = dif / math.sqrt(phat * (1.0 - phat) * 2.0 / n)
        else:
            z = np.nan
        if 0.0 < phat < 1.0:
            d_min = Z_POT * math.sqrt(2.0 * phat * (1.0 - phat) / n)
        else:
            d_min = 0.0
        d_peor = Z_POT * math.sqrt(2.0 * 0.25 / n)
        filas.append({"tabla": "entre_lotes", "escenario": "U1A vs U1A2", "centro": cen,
                      "n": n, "p1": p1, "p2": p2, "dif": dif, "z": z, "d_min": d_min,
                      "d_min_peor": d_peor})
    return filas


def markdown(tab, esc):
    e = tab[tab["tabla"] == "entre_lotes"]
    l = ["# Sens2 F1 - A2b, Parte 3: potencia de U1", "",
         "Cada escenario de U1 tiene 48 puntos nuevos por centro. `precision` resume el",
         "error tipico (sqrt(p(1-p)/n)), el ancho del intervalo de Wilson y el n que haria",
         "falta para una semiamplitud de +/-0.05 y +/-0.10 con la p observada y con el peor",
         "caso p = 0.5. `entre_lotes` compara los lotes U1A y U1A2 por centro.", "",
         "## Que diferencia entre lotes no se habria detectado", ""]
    l.append("Con 48 puntos por lote, una diferencia de proporcion entre los lotes U1A y "
             "U1A2 menor que ~%.1f puntos no se habria detectado con potencia 80 %% y nivel "
             "5 %%: es el limite en el peor caso (p = 0.5), que es el mismo en todos los "
             "centros porque todos tienen 48 puntos. Con la p observada el limite es menor "
             "en cada centro (columna de la tabla)." % (100 * e["d_min_peor"].max()))
    l += ["", "Detalle por centro de la comparacion entre lotes:", "",
          "| centro | p U1A | p U1A2 | dif | z | dif. minima detectable | peor caso |",
          "|---|---|---|---|---|---|---|"]
    for _, r in e.iterrows():
        zt = "." if not np.isfinite(r["z"]) else "%.2f" % r["z"]
        l.append("| %s | %.3f | %.3f | %+.3f | %s | %.4f | %.4f |" % (
            r["centro"], r["p1"], r["p2"], r["dif"], zt, r["d_min"], r["d_min_peor"]))
    l += ["", "n por escenario y centro: %s." % (
        ", ".join("%s n=%d" % (esc_, int(tab[(tab["tabla"] == "precision") &
                (tab["escenario"] == esc_)]["n"].iloc[0])) for esc_ in esc)),
        "", "La tabla de precision completa esta en `p6_potencia_u1.csv`.", ""]
    return "\n".join(l)


def main():
    d = pd.read_csv(U1)
    d = d[d["centro"].isin(CENTROS)]
    tab = pd.DataFrame(filas_precision(d) + filas_entre_lotes(d), columns=COLS)
    os.makedirs(SALIDA, exist_ok=True)
    tab.to_csv(os.path.join(SALIDA, "p6_potencia_u1.csv"), index=False)
    with open(os.path.join(SALIDA, "p6_potencia_u1.md"), "w", encoding="utf-8") as f:
        f.write(markdown(tab, ESC))
    print("p6_potencia_u1.csv:", len(tab), "filas")
    e = tab[tab["tabla"] == "entre_lotes"]
    for _, r in e.iterrows():
        print("  %s dif=%+.3f z=%s d_min=%.4f peor=%.4f" % (
            r["centro"], r["dif"], "." if not np.isfinite(r["z"]) else "%.2f" % r["z"],
            r["d_min"], r["d_min_peor"]))


if __name__ == "__main__":
    main()
