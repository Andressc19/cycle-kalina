# -*- coding: utf-8 -*-
"""A2 · Tablas de resultados calculadas desde el canónico (no copiadas de resultados/**):
TAB-M03-02 (ranking con Δη y distancia a la frontera de O2) y TAB-M10b-02 (x_b bajo).
"""
import os

import pandas as pd

from a2_comun import (RAIZ, leer, leer_canon, nombre_es, tipo_de, formatear,
                      escribir_tabla, subcasos_de)
from a2_tablas_casos import _meta

CRITERIOS = ["O1", "O2", "O3", "O5"]


def criterio_dominante(series):
    """Código O1/O2/O3/O5 más frecuente en una serie de cadenas codigos_falla."""
    cuenta = {c: 0 for c in CRITERIOS}
    for txt in series.dropna():
        for cod in str(txt).split(","):
            cod = cod.strip()
            if cod in cuenta:
                cuenta[cod] += 1
    mejor = max(CRITERIOS, key=lambda c: cuenta[c])
    return mejor if cuenta[mejor] else ""


def tabla_m03():
    d = leer_canon()
    d = d[d["bloque_director"] == "B06"]
    rs = leer(os.path.join(RAIZ, "resultados", "2026-10-06_final_M3", "m3_resumen.csv"))
    cr = leer(os.path.join(RAIZ, "resultados", "2026-10-06_final_M3", "m3_cruces.csv"))
    filas = []
    for _, r in rs.iterrows():
        var = r["variable"]
        tipo = tipo_de(var)
        sub = d[d["variable"] == var]
        gen = sub[(sub["genuino"].astype(bool)) & (sub["wnet_pos"].astype(bool))
                  & (sub["tipo_punto"] == "malla")]
        delta = gen["eta_pct"].max() - gen["eta_pct"].min() if len(gen) else None
        kal = sub[(sub["clasificacion"] == "KALINA") & (sub["tipo_punto"] == "malla")]
        if len(kal):
            i = kal["eta_pct"].idxmax()
            eta_max = kal.loc[i, "eta_pct"]
            val_max = kal.loc[i, "valor"]
        else:
            eta_max = val_max = None
        crv = cr[(cr["variable"] == var) & (cr["criterio"] == "m_O2")]
        dist = None
        if len(crv):
            dist = abs(crv["v_cruce"].iloc[0] - r["valor_ancla"]) / (r["b"] - r["a"])
        filas.append({
            "Variable": nombre_es(var) or var,
            "Rango explorado": f"{formatear(tipo, r['a'])} – {formatear(tipo, r['b'])}",
            "Valor en A*": formatear(tipo, r["valor_ancla"]),
            "Elasticidad E en A*": r["E_eta"],
            "Δη (genuinos) [pp]": delta,
            "η máx. KALINA en la malla [%]": eta_max,
            "Valor de esa η máx.": val_max,
            "Zona KALINA": (f"{formatear(tipo, r['kalina_desde'])} – "
                            f"{formatear(tipo, r['kalina_hasta'])}")
            if pd.notna(r["kalina_desde"]) else "sin KALINA",
            "Criterios que bloquean": r["criterios_bloqueantes"] if pd.notna(r["criterios_bloqueantes"]) else "ninguno",
            "Distancia a la frontera de O2 [–]": dist,
        })
    df = pd.DataFrame(filas)
    df["_orden"] = df["Elasticidad E en A*"].abs()
    df = df.sort_values("_orden", ascending=False).drop(columns="_orden").reset_index(drop=True)
    tipos = {"Variable": "txt", "Rango explorado": "txt", "Valor en A*": "gen",
             "Elasticidad E en A*": "idx", "Δη (genuinos) [pp]": "pp", "η máx. KALINA en la malla [%]": "pct",
             "Valor de esa η máx.": "gen", "Zona KALINA": "txt",
             "Criterios que bloquean": "txt", "Distancia a la frontera de O2 [–]": "idx"}
    meta = _meta("M03", "02", "ranking_delta", "Influencia y margen por variable (Δη y O2)",
                 "KF-M03", subcasos_de("KF-M03"),
                 "puntos genuinos con W_net > 0 de la malla B06", "canónico + m3_resumen.csv + m3_cruces.csv",
                 len(df), "Ordenado por |E| de mayor a menor. η máx. KALINA: solo los 15 puntos de la malla "
                 "(sin A* ni sus vecinos ±1 %), como en la nota del director de REPORTE_M3 §11.")
    escribir_tabla(meta, df, tipos)


def tabla_m10b():
    d = leer_canon()
    m = d[d["id_subcaso"] == "KF-M10b-MALLA"].copy()
    m["xb"] = m["x_b"].round(3)
    filas = []
    for xb in sorted(m["xb"].unique()):
        g = m[m["xb"] == xb]
        kal = g[g["clasificacion"] == "KALINA"]
        if len(kal):
            i = kal["P_baja"].idxmin()
            pb_min = kal.loc[i, "P_baja"]
            eta = kal.loc[i, "eta_pct"]
        else:
            pb_min = eta = None
        fuera = g[g["clasificacion"] != "KALINA"]
        filas.append({"x_b": xb, "P_baja mínima KALINA [kPa]": pb_min,
                      "η en ese punto [%]": eta,
                      "Criterio que más bloquea": criterio_dominante(fuera["codigos_falla"])})
    df = pd.DataFrame(filas)
    tipos = {"x_b": "dec3", "P_baja mínima KALINA [kPa]": "pres", "η en ese punto [%]": "pct",
             "Criterio que más bloquea": "txt"}
    meta = _meta("M10b", "02", "xb_bajo", "Frontera KALINA al variar x_b (Húsavík, x_b bajo)",
                 "KF-M10b", subcasos_de("KF-M10b"),
                 "todos los puntos de KF-M10b-MALLA", "canónico (KF-M10b-MALLA)",
                 len(df), "Una fila por valor de x_b; el criterio cuenta solo O1/O2/O3/O5.")
    escribir_tabla(meta, df, tipos)


def main():
    tabla_m03()
    tabla_m10b()
    print("Tablas calculadas escritas (TAB-M03-02, TAB-M10b-02).")


if __name__ == "__main__":
    main()
