# -*- coding: utf-8 -*-
"""Sens2 P1 - paso 4: fronteras por variable (OFAT) y zonas grises (CORREGIBLE).

(1) Fronteras en los estudios de una sola variable (OFAT), por centro: donde la
clase cambia, con el nivel anterior y el siguiente y la forma observada (escalon,
rampa o ventana de dos fronteras). (2) Zonas grises: los CORREGIBLE con D en el
cuantil 25 % mas bajo de D entre los CORREGIBLE, con su violacion dominante.
"""
import os

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
import sys  # noqa: E402

sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))
import x1_cargar as x  # noqa: E402

SALIDA = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P1")

VIOLACIONES = ["viol_O1", "viol_O2", "viol_O3", "viol_O5"]


def niveles_de(g):
    """Niveles ordenados de un barrido: (valor, n, n_kalina)."""
    a = g.groupby("valor").agg(n=("valor", "size"), n_kalina=("kalina", "sum"))
    a = a.reset_index().sort_values("valor")
    return [(float(r.valor), int(r.n), int(r.n_kalina)) for r in a.itertuples()]


def clase(frac):
    return "KALINA" if frac >= 0.5 else "no-KALINA"


def forma_de(niv):
    """Forma observada a partir de las transiciones entre niveles consecutivos."""
    cl = [clase(k / n) for (_, n, k) in niv]
    trans = [i for i in range(1, len(cl)) if cl[i] != cl[i - 1]]
    mixto = any(0 < (k / n) < 1 for (_, n, k) in niv)
    if len(trans) == 0:
        return "sin cambio", []
    if len(trans) == 1:
        return ("rampa" if mixto else "escalon"), trans
    if len(trans) == 2:
        return "ventana", trans
    return "rampa", trans


def filas_frontera(centro, variable, niv):
    forma, trans = forma_de(niv)
    out = []
    for i in trans:
        (v0, n0, k0), (v1, n1, k1) = niv[i - 1], niv[i]
        c0, c1 = clase(k0 / n0), clase(k1 / n1)
        out.append({
            "centro": centro, "variable": variable, "forma": forma,
            "direccion": "a %s" % c1, "valor_frontera": (v0 + v1) / 2.0,
            "valor_anterior": v0, "clase_anterior": c0, "frac_anterior": k0 / n0,
            "n_anterior": n0, "valor_siguiente": v1, "clase_siguiente": c1,
            "frac_siguiente": k1 / n1, "n_siguiente": n1})
    return out


def fronteras(d, resumen_forma):
    ofat = d[d["variable"].fillna("").ne("") & d["variable"].ne("base")]
    filas = []
    for (centro, variable), g in ofat.groupby(["centro", "variable"]):
        if g["valor"].isna().any():
            continue
        niv = niveles_de(g)
        if len(niv) < 2:
            continue
        forma, trans = forma_de(niv)
        resumen_forma.append((centro, variable, forma, len(niv), len(trans)))
        filas += filas_frontera(centro, variable, niv)
    return filas


def zonas_grises(d, q25):
    corr = d[d["clasificacion"] == "CORREGIBLE"].copy()
    corr["dominante"] = corr[VIOLACIONES].to_numpy().argmax(axis=1)
    corr["dominante"] = [VIOLACIONES[i] for i in corr["dominante"]]
    corr["valor_dominante"] = corr[VIOLACIONES].to_numpy().max(axis=1)
    gris = corr[corr["D"] <= q25].copy()
    cols = (["id_punto", "estudio", "centro", "D", "dominante", "valor_dominante"]
            + VIOLACIONES)
    return gris[cols], corr


def main():
    os.makedirs(SALIDA, exist_ok=True)
    d = pd.read_csv(os.path.join(SALIDA, "p1_dataset.csv"))
    d["kalina"] = d["kalina"].astype(bool)
    aux = x.cargar_todo()[["estudio", "id_punto", "variable", "valor"]]
    d = d.merge(aux, on=["estudio", "id_punto"], how="left")

    resumen_forma = []
    filas = fronteras(d, resumen_forma)
    pd.DataFrame(filas).to_csv(os.path.join(SALIDA, "p1_fronteras.csv"), index=False)

    corr0 = d[d["clasificacion"] == "CORREGIBLE"]
    q25 = float(corr0["D"].quantile(0.25))
    gris, corr = zonas_grises(d, q25)
    gris.to_csv(os.path.join(SALIDA, "p1_zonas_grises.csv"), index=False)

    with open(os.path.join(SALIDA, "p1_fronteras.md"), "w", encoding="utf-8") as f:
        f.write(md(resumen_forma, filas, gris, corr, q25))
    print("fronteras:", len(filas), "| barridos:", len(resumen_forma))
    print("cuantil 25%% de D entre CORREGIBLE:", q25)
    print("zonas grises:", len(gris), "de", len(corr), "CORREGIBLE")
    print("dominantes:", gris["dominante"].value_counts().to_dict())


def md(resumen_forma, filas, gris, corr, q25):
    formas = ["escalon", "rampa", "ventana", "sin cambio"]
    L = ["# Sens2 P1 - paso 4: fronteras y zonas grises", "",
         "## 1. Fronteras en los barridos de una sola variable (OFAT)", "",
         "Estudios con la columna `variable` (estudios 1 y 10). Por centro y variable: donde la",
         "clase cambia, con el nivel anterior y el siguiente. Forma = escalon (un cambio), rampa",
         "(mas de un cambio o niveles intermedios mixtos) o ventana (dos cambios).", "",
         "| centro | variable | forma | niveles | fronteras |", "|---|---|---|---|---|"]
    for centro, variable, forma, n_niv, n_tr in resumen_forma:
        L.append("| %s | %s | %s | %d | %d |" % (centro, variable, forma, n_niv, n_tr))
    conteo = {}
    for _, _, forma, _, _ in resumen_forma:
        conteo[forma] = conteo.get(forma, 0) + 1
    L += ["", "Conteo de formas: " + ", ".join("%s=%d" % (k, conteo[k]) for k in formas
                                               if k in conteo) + ".", "",
          "## 2. Zonas grises (CORREGIBLE con D bajo)", "",
          "Cuantil 25 %% de D entre los CORREGIBLE: **%.4f**." % q25,
          "Zonas grises = CORREGIBLE con D <= ese cuantil: **%d** de %d CORREGIBLE." % (
              len(gris), len(corr)), "",
          "### Conteo por centro", "", "| centro | zonas grises |", "|---|---|"]
    for centro, n in gris["centro"].fillna("(sin centro)").value_counts().items():
        L.append("| %s | %d |" % (centro, n))
    L += ["", "### Conteo por violacion dominante", "",
          "| violacion dominante | zonas grises |", "|---|---|"]
    for dom, n in gris["dominante"].value_counts().items():
        L.append("| %s | %d |" % (dom, n))
    return "\n".join(L)


if __name__ == "__main__":
    main()
