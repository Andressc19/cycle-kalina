# -*- coding: utf-8 -*-
"""A4 · Checks de validación cruzada V01-V12 (TASK_CONTEXT af-A4).

Una función por check. Cada función recibe la tabla canónica y devuelve una
lista de filas del CSV de validación. No corrige nada: solo mide y reporta.
Los checks V13-V23 viven en a4_checks_b.py; a4_validar.py corre ambos.
Tolerancias del TASK_CONTEXT: conteos exactos; η ±5e-4; presiones ±1 kPa;
temperaturas ±0.5 K; r_P ±0.01.
"""
import numpy as np
import pandas as pd

TABLA = "analisis_final/01_datos/todos_los_puntos.csv"
ESCALERA = "resultados/2026-10-08_final_M9/m9_escalera.csv"

S, N, NE = "✔", "✘", "NO EVALUABLE"
T_ETA, T_P, T_T, T_RP = 5e-4, 1.0, 0.5, 0.01

CLAVES_PUNTO = ["T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "eta_t",
                "eta_p", "eps_hrvg", "eps_reg", "eps_cond", "eta"]


def fila(idc, caso, filtro, cifra, esperado, recalc, ok, nota=""):
    """Fila del CSV: ok True/False/None -> ✔/✘/NO EVALUABLE."""
    r = NE if ok is None else (S if ok else N)
    return {"id_check": idc, "caso": caso, "filtro": filtro, "cifra": cifra,
            "esperado": esperado, "recalculado": recalc, "resultado": r, "nota": nota}


def Kalina(g):
    return g[g["clasificacion"] == "KALINA"]


def num(s):
    return pd.to_numeric(s, errors="coerce")


def p5p95(g, col):
    s = num(g[col]).dropna()
    return np.percentile(s, [5, 95]) if len(s) else (np.nan, np.nan)


def cerca(a, b, tol):
    return abs(float(a) - float(b)) <= tol


def v01(df):
    m = df[df["id_caso"] == "KF-M01"]
    n, g = len(m), int(m["genuino"].sum())
    return [fila("V01", "KF-M01", "todas las filas", "filas; genuinas",
                 "42 filas; 42 NO_CONVERGIO o N2 (0 genuinas)",
                 f"{n} filas; {g} genuinas", n == 42 and g == 0)]


def v02(df):
    m = df[df["id_caso"] == "KF-M02-N1"]
    k = int((m["clasificacion"] == "KALINA").sum())
    return [fila("V02", "KF-M02-N1", "malla + bisección", "n KALINA", "0 KALINA",
                 f"{k} KALINA", k == 0)]


def v03(df):
    m = df[df["id_subcaso"] == "KF-M02-N2-A"]
    k = int((m["clasificacion"] == "KALINA").sum())
    return [fila("V03", "KF-M02-N2-A", "todas las filas", "n KALINA", "0 KALINA",
                 f"{k} KALINA", k == 0)]


def v04(df):
    k = Kalina(df[df["id_subcaso"] == "KF-M02-N2-B"])
    tf = sorted(float(x) for x in num(k["T_fuente"]).unique())
    i = k["P_baja"].idxmin()
    pb, et, tfe = float(k.loc[i, "P_baja"]), float(k.loc[i, "eta"]), float(k.loc[i, "T_fuente"])
    ok = (len(tf) == 4 and np.allclose(tf, [390, 403, 420, 434])
          and cerca(pb, 445.455, T_P) and cerca(et, 0.0245, T_ETA) and cerca(tfe, 390, T_T))
    return [fila("V04", "KF-M02-N2-B", "KALINA", "T_fuente; mín P_baja KALINA",
                 "T_fuente ∈ {390,403,420,434} K; mín P_baja 445.455 kPa con η 0.0245 (T_fuente 390)",
                 f"T_fuente {tf}; mín P_baja {pb:.3f} kPa con η {et:.4f} (T_fuente {tfe:.0f})", ok)]


def v05(df):
    k = Kalina(df[df["id_subcaso"] == "KF-M02-N2-B"])
    n, f = len(k), int(k["fuera_rango"].sum())
    return [fila("V05", "KF-M02-N2-B", "KALINA", "n KALINA; fuera de rango", "59; 11",
                 f"{n}; {f}", (n, f) == (59, 11))]


def v06(df):
    k = Kalina(df[df["id_caso"] == "KF-M02R"])
    n, f = len(k), int(k["fuera_rango"].sum())
    u = len(k.drop_duplicates(CLAVES_PUNTO))
    uf = len(k[k["fuera_rango"]].drop_duplicates(CLAVES_PUNTO))
    return [fila("V06", "KF-M02R", "todas las filas", "n KALINA; fuera de rango",
                 "14; 13", f"{n}; {f}", (n, f) == (14, 13),
                 nota=f"El reporte (m2r_kalina.csv) cuenta puntos distintos: {u} y {uf} fuera. "
                      f"La canónica no deduplica (malla y bisección solapan).")]


def v07(df):
    k = Kalina(df[df["id_caso"] == "KF-M02S"])
    u = len(k.drop_duplicates(["base", "T_sumidero", "P_baja"]))
    b4 = int((k["base"] == "B4").sum())
    return [fila("V07", "KF-M02S", "KALINA", "únicos (base,T_sumidero,P_baja); KALINA en B4",
                 "123; 0", f"{u}; {b4}", (u, b4) == (123, 0))]


def v08(df):
    s = Kalina(df[df["id_caso"] == "KF-M02S"])
    esp = {"B1": [0.1041, 290.625, 0.0849, 562.5], "B2": [0.1191, 393.75, 0.0911, 740.625],
           "B3": [0.0969, 750.0, 0.0630, 1312.5]}
    filas = []
    for b, e in esp.items():
        vals = []
        for ts in (278.15, 300.032917):
            g = s[(s["base"] == b) & np.isclose(num(s["T_sumidero"]), ts, atol=1e-4)]
            vals += [float(g["eta"].max()), float(g["P_baja"].min())]
        ok = all(cerca(v, w, T_ETA if i % 2 == 0 else T_P) for i, (v, w) in enumerate(zip(vals, e)))
        filas.append(fila("V08", f"KF-M02S-{b}", "KALINA en T_sumidero 278.15 y 300.032917",
                          "η máx; P_baja mín",
                          f"278.15: ({e[0]}; {e[1]:g}) / 300.03: ({e[2]}; {e[3]:g})",
                          f"278.15: ({vals[0]:.4f}; {vals[1]:g}) / 300.03: ({vals[2]:.4f}; {vals[3]:g})",
                          ok, nota="η en la P_baja mínima coincide con η máx (η baja al subir P_baja)."))
    return filas


def v09(df):
    m = df[df["id_caso"] == "KF-M03"]
    vals = (len(m), int(m["genuino"].sum()),
            int((m["clasificacion"] == "KALINA").sum()), int(m["fuera_rango"].sum()))
    return [fila("V09", "KF-M03", "todas las filas", "filas; genuinas; KALINA; fuera",
                 "171; 148; 86; 8", "; ".join(map(str, vals)), vals == (171, 148, 86, 8))]


def v10(df):
    m = df[(df["id_caso"] == "KF-M03") & (df["tipo_punto"] == "malla")
           & (df["genuino"]) & (df["wnet_pos"])]
    esp = {"x_b": 10.78, "P_baja": 6.80, "eps_hrvg": 6.69, "eta_t": 6.32, "P_alta": 5.14,
           "eps_reg": 4.99, "T_fuente": 3.67, "eta_p": 1.38, "T_sumidero": 0.85, "eps_cond": 0.82}
    filas = []
    for v, e in esp.items():
        g = m[m["variable"] == v]
        d = (float(g["eta"].max()) - float(g["eta"].min())) * 100
        filas.append(fila("V10", "KF-M03", "malla, genuinas con W_net>0", f"Δη {v} [pp]",
                          f"{e:.2f}", f"{d:.2f}", cerca(d, e, 0.02)))
    return filas


def v11(df):
    m = df[(df["id_caso"] == "KF-M03") & (df["tipo_punto"] == "malla")
           & (df["clasificacion"] == "KALINA")]
    esp = {"eps_reg": (0.1096, 0.95), "eta_t": (0.0962, 0.95)}
    filas = []
    for v, (e_eta, e_val) in esp.items():
        g = m[m["variable"] == v]
        i = g["eta"].idxmax()
        et, va = float(g.loc[i, "eta"]), float(g.loc[i, "valor"])
        filas.append(fila("V11", "KF-M03", "malla, KALINA", f"η máx {v}",
                          f"{e_eta:.4f} en {e_val:g}", f"{et:.4f} en {va:g}",
                          cerca(et, e_eta, T_ETA) and cerca(va, e_val, 1e-6)))
    return filas


def v12(df):
    g = df[df["id_caso"].isin(["KF-M04", "KF-M04b"])]
    vals = (len(g), int((g["clasificacion"] == "KALINA").sum()), int(g["fuera_rango"].sum()))
    return [fila("V12", "KF-M04 + KF-M04b", "todas las filas", "filas; KALINA; fuera",
                 "500; 121; 222", "; ".join(map(str, vals)), vals == (500, 121, 222))]


CHECKS = [v01, v02, v03, v04, v05, v06, v07, v08, v09, v10, v11, v12]
