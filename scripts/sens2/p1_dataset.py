# -*- coding: utf-8 -*-
"""Sens2 P1 - paso 1: dataset unificado de los 3 921 puntos de Sensibilidad 1.

Una fila por punto de todos los estudios (0-11 y 14-16). Se apoya en
`x1_cargar.cargar_todo()` para lo comun y vuelve a leer los CSV de origen solo para
las columnas que el cargador no expone (D, las violaciones O1/O2/O3/O5 y q4).
No se exporta la columna interna del cargador (la de rango experimental); se usa
`fuera_rango`.
"""
import os
import sys

import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))

import x1_cargar as x  # noqa: E402

SALIDA = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P1")

ENTRADAS = list(x.VARIABLES_ORDEN)
EXTRA_CSV = ["D", "viol_O1", "viol_O2", "viol_O3", "viol_O5", "q4"]
COLS = (["id_punto", "estudio", "centro", "clasificacion", "kalina", "fuera_rango"]
        + ENTRADAS
        + ["eta_pct", "Wnet", "D", "viol_O1", "viol_O2", "viol_O3", "viol_O5",
           "rp", "qreg_qi", "dh_turb", "Qi", "Qreg", "q4", "t_s"])


def extras_csv():
    """Columnas D/viol/q4 de los CSV de origen, en el mismo orden que `cargar_todo`."""
    partes = []
    for est in x.ESTUDIOS:
        df = pd.read_csv(est["archivo"])
        if est["barrido"]:
            df = df[df["barrido"] == est["barrido"]].copy()
        df = df.reset_index(drop=True)
        o = pd.DataFrame({"estudio": est["n"], "id_punto": df["id_punto"].astype(str)})
        for c in EXTRA_CSV:
            o[c] = pd.to_numeric(df[c], errors="coerce") if c in df.columns else float("nan")
        partes.append(o)
    return pd.concat(partes, ignore_index=True)


def resumen(df, n_dup, n_grupos):
    largos = ["# Sens2 P1 - paso 1: dataset unificado", "",
              "Total de filas: **%d** (esperado 3 921: %s)." % (
                  len(df), "coincide" if len(df) == 3921 else "NO coincide"),
              "", "## n por estudio y por clase", "",
              "| estudio | puntos | KALINA | CORREGIBLE | NO_CONVERGIO | INVIABLE |",
              "|---|---|---|---|---|---|"]
    for e in sorted(df["estudio"].unique()):
        s = df[df["estudio"] == e]
        c = s["clasificacion"].value_counts()
        largos.append("| %d | %d | %d | %d | %d | %d |" % (
            e, len(s), c.get("KALINA", 0), c.get("CORREGIBLE", 0),
            c.get("NO_CONVERGIO", 0), c.get("INVIABLE", 0)))
    tot = df["clasificacion"].value_counts()
    largos += ["| **total** | **%d** | **%d** | **%d** | **%d** | **%d** |" % (
        len(df), tot.get("KALINA", 0), tot.get("CORREGIBLE", 0),
        tot.get("NO_CONVERGIO", 0), tot.get("INVIABLE", 0)), "",
        "Puntos sin centro asignado en el cargador: %d (estudios N1, N2 y N5)." % (
            int((df["centro"] == "").sum())), "",
        "## Duplicados exactos", "",
        "Se consideran duplicadas dos filas con las **mismas 10 entradas** y el mismo `centro`:",
        "Hay %d grupos con esa condicion (%d filas dentro de ellos)." % (
            n_grupos, n_dup),
        "Cada fila sigue siendo un punto distinto de su estudio (mismo vector de entradas,",
        "otro id de estudio): el dataset conserva las 3 921 filas, una por punto, como pide el paso 1.",
        ""]
    return "\n".join(largos)


def main():
    os.makedirs(SALIDA, exist_ok=True)
    d = x.cargar_todo()
    ext = extras_csv()
    m = d.merge(ext, on=["estudio", "id_punto"], how="left")
    assert len(m) == len(d), "el merge cambio el numero de filas"
    sel = m[COLS].copy()

    key = ENTRADAS + ["centro"]
    dup = sel.duplicated(key, keep=False)
    n_dup = int(dup.sum())
    n_grupos = int(sel[dup].groupby(key, dropna=False).ngroups)

    sel.to_csv(os.path.join(SALIDA, "p1_dataset.csv"), index=False)
    with open(os.path.join(SALIDA, "p1_dataset_resumen.md"), "w", encoding="utf-8") as f:
        f.write(resumen(sel, n_dup, n_grupos))

    print("dataset:", len(sel), "filas,", len(sel.columns), "columnas")
    print("total 3921:", len(sel) == 3921)
    print("duplicados (10 entradas + centro):", n_dup, "filas en", n_grupos, "grupos")
    print("clases:", sel["clasificacion"].value_counts().to_dict())


if __name__ == "__main__":
    main()
