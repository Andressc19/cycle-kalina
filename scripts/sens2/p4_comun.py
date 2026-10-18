# -*- coding: utf-8 -*-
"""Sens2 P4 - modulo comun: carga, union por id_punto y cantidades derivadas.

Carga el dataset deduplicado de P2 y le une, por `id_punto` (y su estudio), las
columnas de estado del cargador de Sensibilidad 1 (Qout, Wt, Wp, m_v, m_l,
T_e1..T_e10, h_e1..h_e10). Deriva las cantidades por equipo con la numeracion de
estados de `CONTEXT.md`: 3 entrada de turbina, 4 salida, 8 entrada de condensador,
9 salida de condensador, 10 salida de bomba, 1 salida fria del regenerador, y el
lado caliente 5 -> 6. Divide toda cantidad extensiva entre m_b (el estudio 0 usa
m_b != 1). Umbrales y parametros salen de los datos y se reportan.
"""
import os
import sys

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))

P2 = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P2", "p2_dataset_dedup.csv")
SALIDA = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P4")

SEMILLA = 20261017
SIN_CENTRO = "Sin centro (muestreo o malla)"
CENTROS = ["C1 Husavik", "C2 ancla A*", "C3 caliente 150 C", "C4 frio 110 C", SIN_CENTRO]
REF_TOTAL = "KALINA (total)"
REF_RANGO = "KALINA dentro del rango experimental"
REF_TOP10 = "10 % de KALINA (total) con mayor eta"
GRUPOS = [REF_TOTAL, REF_RANGO, REF_TOP10]

ENTRADAS = ["T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "eta_t", "eta_p",
            "eps_hrvg", "eps_reg", "eps_cond"]

Q_TURBINA = ["rp", "dh_turb", "Wt_mb", "q4", "T3", "T4", "m_v_mb"]
Q_REG = ["dT_A", "dT_B", "pinch_reg", "LMTD_reg", "UA_reg", "qreg_qi"]
Q_COND = ["Qout_mb", "aprox_cond_sal", "aprox_cond_ent"]
Q_HRVG = ["Qi_mb", "aprox_fuente"]
Q_BOMBA = ["Wp_mb", "Wp_Wt", "P_alta", "P_baja"]
Q_CICLO = ["eta_pct", "wnet_mb"]
CANTIDADES = Q_TURBINA + Q_REG + Q_COND + Q_HRVG + Q_BOMBA + Q_CICLO
EQUIPOS = [("Turbina", Q_TURBINA), ("Regenerador", Q_REG), ("Condensador", Q_COND),
           ("HRVG", Q_HRVG), ("Bomba", Q_BOMBA)]
# Cantidades de equipo del Paso 2 (no incluye las de ciclo ni T/m de la turbina).
CANT_DEP = ["rp", "dh_turb", "Wt_mb", "q4", "UA_reg", "pinch_reg", "qreg_qi",
            "Qout_mb", "aprox_cond_sal", "Qi_mb", "Wp_Wt"]
BANDAS = [(1.0, 1.5), (1.5, 2.0), (2.0, 3.0), (3.0, 4.0), (4.0, 6.0), (6.0, 10.0)]
PROHIBIDAS = ["confiable", "citable", "fuera de rango del motor"]
ESTADOS = [f"T_e{i}" for i in range(1, 11)] + [f"h_e{i}" for i in range(1, 11)]


def grupos(df):
    """Centros presentes, en el orden C1..C4 y luego el grupo sin centro."""
    pres = list(df["centro"].unique())
    orden = [c for c in CENTROS[:4] if c in pres]
    if SIN_CENTRO in pres:
        orden.append(SIN_CENTRO)
    return orden


def _estados():
    """Columnas de estado del cargador de Sensibilidad 1 (id_punto como texto)."""
    import x1_cargar as x  # import perezoso
    d = x.cargar_todo()
    d["id_punto"] = d["id_punto"].astype(str)
    cols = ["estudio", "id_punto", "Qout", "Wt", "Wp", "m_v", "m_l"] + ESTADOS
    return d[cols]


def lmt_reg(a, b):
    """LMTD del regenerador; NaN si algunos de dT_A/dT_B es <= 0 (cruce)."""
    a = np.asarray(pd.to_numeric(pd.Series(a), errors="coerce"), float)
    b = np.asarray(pd.to_numeric(pd.Series(b), errors="coerce"), float)
    out = np.full(len(a), np.nan)
    fin = np.isfinite(a) & np.isfinite(b)
    eq = fin & (a == b) & (a > 0)
    out[eq] = a[eq]
    dif = fin & (a != b) & (a > 0) & (b > 0)
    out[dif] = (a[dif] - b[dif]) / np.log(a[dif] / b[dif])
    return out


def derivar(d):
    """Cantidades derivadas por equipo (division por m_b de lo extensivo)."""
    o = d.copy()
    mb = o["m_b"].to_numpy(float)
    o["Wt_mb"] = o["Wt"].to_numpy(float) / mb
    o["Wp_mb"] = o["Wp"].to_numpy(float) / mb
    o["Qout_mb"] = o["Qout"].to_numpy(float) / mb
    o["Qi_mb"] = o["Qi"].to_numpy(float) / mb
    o["m_v_mb"] = o["m_v"].to_numpy(float) / mb
    o["T3"] = o["T_e3"]
    o["T4"] = o["T_e4"]
    o["dT_A"] = o["T_e5"] - o["T_e1"]
    o["dT_B"] = o["T_e6"] - o["T_e10"]
    o["pinch_reg"] = np.minimum(o["dT_A"].to_numpy(float), o["dT_B"].to_numpy(float))
    o["LMTD_reg"] = lmt_reg(o["dT_A"], o["dT_B"])
    o["UA_reg"] = (o["Qreg"].to_numpy(float) / mb) / o["LMTD_reg"].to_numpy(float)
    o["aprox_cond_sal"] = o["T_e9"] - o["T_sumidero"]
    o["aprox_cond_ent"] = o["T_e8"] - o["T_sumidero"]
    o["aprox_fuente"] = o["T_fuente"] - o["T_e3"]
    o["Wp_Wt"] = o["Wp"].to_numpy(float) / o["Wt"].to_numpy(float)
    return o


def cargar():
    """Dataset P2 deduplicado + estados, con las cantidades derivadas."""
    d = pd.read_csv(P2)
    d["id_punto"] = d["id_punto"].astype(str)
    d["centro"] = d["centro"].fillna(SIN_CENTRO)
    m = d.merge(_estados(), on=["estudio", "id_punto"], how="left")
    return derivar(m)


def mask_total(s):
    return s["kalina"] == True  # noqa: E712


def mask_rango(s):
    return mask_total(s) & (~s["fuera_rango"].astype(bool))


def mask_top10(s, frac=0.10):
    """El 10 % de KALINA (total) con mayor eta_pct (al menos 1 si hay KALINA)."""
    k = s[mask_total(s)]
    if len(k) == 0:
        return pd.Series(False, index=s.index)
    n = max(1, int(round(frac * len(k))))
    idx = k.sort_values("eta_pct", ascending=False).head(n).index
    return s.index.isin(idx)


def mascara(s, grupo):
    if grupo == REF_TOTAL:
        return mask_total(s)
    if grupo == REF_RANGO:
        return mask_rango(s)
    return mask_top10(s)


def resumen_serie(x):
    """n, min, P5, P50 (mediana), P95 y max ignorando NaN."""
    v = np.asarray(pd.to_numeric(pd.Series(x), errors="coerce"), float)
    v = v[np.isfinite(v)]
    if len(v) == 0:
        return dict(n=0, minimo=np.nan, p5=np.nan, p50=np.nan, p95=np.nan, maximo=np.nan)
    return dict(n=int(len(v)), minimo=float(v.min()), p5=float(np.percentile(v, 5)),
                p50=float(np.median(v)), p95=float(np.percentile(v, 95)),
                maximo=float(v.max()))


def fmt(x, dec=4):
    return "." if not np.isfinite(x) else ("%%.%df" % dec) % x


def tabla_md(cab, filas):
    l = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    for f in filas:
        l.append("| " + " | ".join(str(c) for c in f) + " |")
    return "\n".join(l)


def guardar(nombre, texto):
    os.makedirs(SALIDA, exist_ok=True)
    ruta = os.path.join(SALIDA, nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(texto)
    return ruta
