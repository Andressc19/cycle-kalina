# -*- coding: utf-8 -*-
"""Sens2 etapa B - caudal volumetrico de turbina y altura de bomba por kW neto (barrido DENS del motor).

Entrada: s2b_dens_filas.csv (150 KALINA representativos re-resueltos, m_b = 1 kg/s, con densidades de `s2b_dens.py`). Se usan las filas
KALINA dentro del rango experimental. Por ambito (cuatro centros LHS, resto de estudios y todos) P5, P50 y P95 de: densidades, relacion
de volumenes de la turbina, caudales volumetricos por kW neto y altura de la bomba. Salidas en resultados/2026-10-18_sens2_F1: p6_dens.csv y p6_dens.md.
Son envolventes de un muestreo numerico (por kg/s de fluido, luego por kW neto); no son especificaciones de compra.
"""
import os

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
ENT = os.environ.get("S2B_DIR", os.path.join(RAIZ, "resultados", "2026-10-18_sens2_B"))
SAL = os.environ.get("S2B_OUT", os.path.join(RAIZ, "resultados", "2026-10-18_sens2_F1"))
AMBITOS = [("todos", None), ("C1", "C1"), ("C2", "C2"), ("C3", "C3"), ("C4", "C4"), ("resto de estudios", "SC")]
MAGN = [("rho3", "kg/m3", "densidad del vapor a la entrada de turbina", 1.0), ("rho4", "kg/m3", "densidad a la salida de turbina", 1.0),
        ("rho9", "kg/m3", "densidad del liquido a la entrada de bomba", 1.0), ("RV_turb", "-", "relacion de volumenes de la turbina (V4/V3)", 1.0),
        ("V3_kW", "L/s por kW neto", "caudal volumetrico a la entrada de turbina", 1000.0), ("V4_kW", "L/s por kW neto", "caudal volumetrico a la salida de turbina", 1000.0),
        ("V9_kW", "L/s por kW neto", "caudal volumetrico de la bomba", 1000.0), ("H_bomba_m", "m", "altura de la bomba", 1.0)]


def main():
    ruta = os.path.join(ENT, "s2b_dens_filas.csv")
    if not os.path.exists(ruta):
        print("sin s2b_dens_filas.csv: nada que analizar")
        return 0
    d = pd.read_csv(ruta)
    d = d[(d["clasificacion"] == "KALINA") & ~d["fuera_rango"].astype(bool) & d["rho3"].notna() & (d["Wnet"] > 0)].copy()
    if d.empty:
        print("sin filas KALINA con densidades")
        return 0
    d["RV_turb"] = d["rho3"] / d["rho4"]
    for v in ("V3", "V4", "V9"):
        d[v + "_kW"] = d[v + "_m3s"] / d["Wnet"]                       # m3/s por kW neto (m_b = 1 kg/s)
    filas = []
    for amb, cod in AMBITOS:
        g = d if cod is None else d[d["centro"] == cod]
        for col, uni, desc, esc in MAGN:
            x = g[col].dropna().to_numpy(float) * esc
            if len(x):
                filas.append(dict(ambito=amb, magnitud=col, descripcion=desc, unidad=uni, n=len(x), p5=np.percentile(x, 5), p50=np.percentile(x, 50), p95=np.percentile(x, 95)))
    t = pd.DataFrame(filas)
    os.makedirs(SAL, exist_ok=True)
    t.to_csv(os.path.join(SAL, "p6_dens.csv"), index=False, encoding="utf-8", lineterminator="\r\n")
    md = ["# Sens2 etapa B - caudales volumetricos y altura de bomba por kW neto", "",
          "Ambito 'todos'. Son envolventes de un muestreo numerico (m_b = 1 kg/s, luego por kW neto); no son especificaciones de compra.", "",
          "| magnitud | unidad | n | P5 | P50 | P95 |", "|---|---|---|---|---|---|"]
    md += ["| %s | %s | %d | %.4g | %.4g | %.4g |" % (r.descripcion, r.unidad, r.n, r.p5, r.p50, r.p95) for r in t[t["ambito"] == "todos"].itertuples()]
    with open(os.path.join(SAL, "p6_dens.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    print("dens: %d filas KALINA; %d filas de tabla" % (len(d), len(t)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
