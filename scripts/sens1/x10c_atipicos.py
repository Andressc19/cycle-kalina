# -*- coding: utf-8 -*-
"""Sensibilidad 1 - x10c: seccion «Puntos atipicos» de LEEME.

Regla (estudios 1-11 y 14-16): KALINA (total) con eta_t >= 0.8 y dh_turb por debajo de 0.6 veces
la mediana de dh_turb de los KALINA de su banda de r_P = P_alta/P_baja, con las bandas
[1, 1.5), [1.5, 2), [2, 3), [3, 4), [4, 6) y [6, 10). La tabla reune los ids senalados por el
director (ver UNRESOLVED: la regla reproduce 6 de los 7; N1-T090-10 no baja del umbral de su
banda) con la mediana de la banda y el resto de columnas calculadas desde los CSV.
"""

import pandas as pd

from x1_cargar import etiqueta_centro
from x2_formato import subtitulo, tabla, nota

ESTUDIOS_R = list(range(1, 12)) + [14, 15, 16]
BANDAS_RP = [1, 1.5, 2.0, 3.0, 4.0, 6.0, 10.0]
IDS = ["C1-B6-0236", "N1-T090-10", "N7A-C3-P_alta-001", "N7A-C4-P_alta-001",
       "N7A-C4-eps_hrvg-003", "N8-C4-0141", "N9-C4-B6-0004"]


def _r(x, d=2):
    if x is None:
        return None
    try:
        v = float(x)
    except Exception:
        return None
    if v != v:
        return None
    return round(v, d)


def _kal(cal):
    """KALINA (total) con eta_t >= 0.8 de los estudios 1-11 y 14-16, con su banda de r_P."""
    d = cal[(cal["estudio"].isin(ESTUDIOS_R)) & cal["kalina"] & (cal["eta_t"] >= 0.8)].copy()
    d["banda"] = pd.cut(d["rp"], bins=BANDAS_RP, right=False)
    return d


def medianas_banda(df):
    """{banda: mediana de dh_turb} entre los KALINA con eta_t >= 0.8 de cada banda de r_P."""
    d = _kal(df)
    med = d.groupby("banda", observed=False)["dh_turb"].median()
    return {str(k): float(v) for k, v in med.items()}


def candidatos_regla(df):
    """Ids que cumple la regla (dh_turb < 0.6 x mediana de su banda), ordenados."""
    med = medianas_banda(df)
    d = _kal(df)
    d["med"] = d["banda"].astype(str).map(med)
    a = d[d["dh_turb"] < 0.6 * d["med"]]
    return sorted(a["id_punto"].astype(str).tolist())


def filas_atipicos(df):
    """Filas [id, estudio, centro, T_fuente (K), r_P, dh, mediana de la banda, eta (%), t_s]."""
    med = medianas_banda(df)
    filas = []
    for pid in IDS:
        s = df[df["id_punto"] == pid].head(1)
        if len(s) == 0:
            continue
        r = s.iloc[0]
        b = pd.cut([r["rp"]], bins=BANDAS_RP, right=False)[0]
        filas.append([pid, int(r["estudio"]), etiqueta_centro(r["centro"]), _r(r["T_fuente"], 2),
                      _r(r["rp"], 3), _r(r["dh_turb"], 2), _r(med.get(str(b))),
                      _r(r["eta_pct"], 2), _r(r["t_s"], 1)])
    return filas


def seccion_atipicos(ws, fila, df):
    """Escribe «Puntos atipicos» (tabla + nota) y devuelve la fila siguiente."""
    f = subtitulo(ws, fila, "Puntos atípicos")
    _, ult, _ = tabla(ws, f,
                      ["id_punto", "Estudio", "Centro", "T_fuente (K)",
                       "r_P = P_alta/P_baja (-)", "Δh de turbina (kJ/kg)",
                       "Mediana de la banda (kJ/kg)", "η (%)", "Tiempo de cómputo (s)"],
                      filas_atipicos(df),
                      anchos=[18, 8, 20, 12, 18, 18, 18, 10, 18], clases=None, clave_fila=None)
    return nota(ws, ult + 2,
                "No se descartan: se señalan porque su caída de entalpía de turbina es "
                "anormalmente baja respecto de puntos vecinos; pueden ser soluciones del solver "
                "en otra rama.")


__all__ = ["ESTUDIOS_R", "BANDAS_RP", "IDS", "medianas_banda", "candidatos_regla",
           "filas_atipicos", "seccion_atipicos"]
