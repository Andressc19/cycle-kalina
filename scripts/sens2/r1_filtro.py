# -*- coding: utf-8 -*-
"""Sens2 R1 - Paso 1: filtro y asignacion de centro de los puntos del libro viejo.

Lee `datos/Excel_kalina_final_final_final.xlsx` (hoja `Datos`), aplica la cascada de
7 filtros del TASK_CONTEXT, deduplica por las 10 variables redondeadas a 4 decimales
(uniendo las partes), quita los puntos que ya estan en `dataset_dedup()` y asigna a
cada punto restante el centro mas cercano (norma infinito) con su distancia `dist`.

Salidas (en resultados/2026-10-18_sens2_R1/): `r1_cascada.csv`, `r1_puntos.csv`,
`r1_resumen.csv`. Este modulo expone ademas las constantes y utilidades que usan
`r1_contraste.py` y `r1_verificacion.py`.
"""
import os
import sys

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens2"))

LIBRO_VIEJO = os.path.join(RAIZ, "datos", "Excel_kalina_final_final_final.xlsx")
SALIDA = os.path.join(RAIZ, "resultados", "2026-10-18_sens2_R1")
P1 = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P1")

V10 = ["T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "eta_t", "eta_p",
       "eps_hrvg", "eps_reg", "eps_cond"]
VARS_DIST = ["T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b"]
CENTROS = {"C1 Husavik": (394.15, 278.15, 3300.0, 690.0, 0.82),
           "C2 ancla A*": (403.0, 300.15, 3000.0, 563.64, 0.50),
           "C3 caliente 150 C": (423.15, 280.5, 3150.0, 950.0, 0.75),
           "C4 frio 110 C": (383.15, 282.5, 3880.0, 910.0, 0.88)}
ESCALA = {"T_fuente": 230.0, "T_sumidero": 25.15, "P_alta": 7180.0,
          "P_baja": 1900.0, "x_b": 0.65}
DOMINIO = {"T_fuente": (343.15, 573.15), "T_sumidero": (278.0, 303.15),
           "P_alta": (820.0, 8000.0), "P_baja": (100.0, 2000.0),
           "x_b": (0.30, 0.95), "eta_t": (0.40, 0.95), "eta_p": (0.40, 0.95),
           "eps_hrvg": (0.40, 0.95), "eps_reg": (0.40, 0.95), "eps_cond": (0.40, 0.95)}
CERCANO = 0.15
COBERTURA = 0.25
SAL_COLS = ["id_punto", "Estudio", "partes"] + V10 + ["clasificacion", "fuera_rango",
            "eta_pct", "Wnet", "codigos_falla", "centro", "dist", "cerca"]


def clave10(df):
    """Clave de las 10 variables redondeadas a 4 decimales, una por fila."""
    sub = pd.DataFrame(df)[V10].round(4)
    return sub.astype("float64").apply(lambda r: "|".join("%.4f" % x for x in r), axis=1)


def claves_dedup():
    """Conjunto de claves de `dataset_dedup()` (misma clave de 10 variables)."""
    from s2_cargar import dataset_dedup
    return set(clave10(dataset_dedup()))


def asignar_centro(df):
    """(centro, dist) del centro mas cercano en norma infinito sobre las 5 variables."""
    nombres = list(CENTROS)
    p = df[VARS_DIST].to_numpy(float)
    escala = np.array([ESCALA[v] for v in VARS_DIST], float)
    d = np.empty((len(df), len(nombres)), float)
    for j, c in enumerate(nombres):
        d[:, j] = np.max(np.abs(p - np.array(CENTROS[c], float)) / escala, axis=1)
    idx = d.argmin(axis=1)
    return [nombres[i] for i in idx], d[np.arange(len(df)), idx]


def _fila(paso, f):
    key = clave10(f)
    kal = f.loc[f["clasificacion"] == "KALINA", :].pipe(clave10) if len(f) else pd.Series(dtype=str)
    return {"paso": paso, "n_filas": int(len(f)), "n_unicos": int(key.nunique()),
            "n_kalina": int(kal.nunique())}


def main():
    os.makedirs(SALIDA, exist_ok=True)
    df = pd.read_excel(LIBRO_VIEJO, sheet_name="Datos")
    filas = [_fila("1 hoja Datos", df)]
    df = df[df["omitido"] == False].copy()  # noqa: E712
    filas.append(_fila("2 omitido=False", df))
    df = df[df[V10].notna().all(axis=1)].copy()
    filas.append(_fila("3 10 variables no nulas", df))
    comp = df["T_amb_diseno"].isna() | (df["T_amb_diseno"] <= df["T_sumidero"] + 1e-6)
    df = df[comp].copy()
    filas.append(_fila("4 piso de O2 comparable", df))
    dentro = np.ones(len(df), bool)
    for v, (lo, hi) in DOMINIO.items():
        dentro &= (df[v] >= lo) & (df[v] <= hi)
    df = df[dentro].copy()
    filas.append(_fila("5 dentro del dominio de Sens2", df))
    df["key"] = clave10(df)
    partes = df.groupby("key")["Parte"].apply(
        lambda s: ";".join(sorted({str(p) for p in s.dropna()})))
    df = df.drop_duplicates("key", keep="first").reset_index(drop=True)
    df["partes"] = df["key"].map(partes)
    filas.append(_fila("6 unicos por 10 variables", df))
    fuera = set(clave10(df)) & claves_dedup()
    df = df[~clave10(df).isin(fuera)].copy()
    filas.append(_fila("7 fuera de dataset_dedup", df))
    cascada = pd.DataFrame(filas)
    cascada.to_csv(os.path.join(SALIDA, "r1_cascada.csv"), index=False)

    df["centro"], df["dist"] = asignar_centro(df)
    df["cerca"] = df["dist"] <= CERCANO
    puntos = df[SAL_COLS].reset_index(drop=True)
    puntos.to_csv(os.path.join(SALIDA, "r1_puntos.csv"), index=False)

    cerca = puntos[puntos["cerca"]]
    resumen = (cerca.groupby(["Estudio", "centro", "clasificacion"])
               .size().reset_index(name="n"))
    resumen.to_csv(os.path.join(SALIDA, "r1_resumen.csv"), index=False)

    print("cascada:")
    for _, r in cascada.iterrows():
        print("  %-28s filas=%-5d unicos=%-5d kalina=%d"
              % (r["paso"], r["n_filas"], r["n_unicos"], r["n_kalina"]))
    print("puntos escritos:", len(puntos), "| cerca:", int(puntos["cerca"].sum()))
    print("centros:", puntos["centro"].value_counts().to_dict())


if __name__ == "__main__":
    main()
