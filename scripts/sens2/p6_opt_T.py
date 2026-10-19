# -*- coding: utf-8 -*-
"""Sens2 etapa B - eta maxima frente a T_fuente con busqueda local (archivos s2b_opt_<K>.csv de `s2b_opt_T.py`).

Por banda de T_fuente (353.15 a 573.15 K): evaluaciones, KALINA, eta maxima encontrada y los P_alta, P_baja y x_b donde ocurre, si ese punto cae
fuera del rango experimental, y la eta maxima del conjunto muestreado a menos de 10 K de la banda (KALINA dentro del rango) para comparar.
Salidas en resultados/2026-10-18_sens2_F1: p6_opt_T.csv y p6_opt_T.md. El resto de variables quedan fijas (supuesto de escenario, ver `s2b_opt_T.py`).
"""
import glob
import os

import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
ENT = os.environ.get("S2B_DIR", os.path.join(RAIZ, "resultados", "2026-10-18_sens2_B"))
SAL = os.environ.get("S2B_OUT", os.path.join(RAIZ, "resultados", "2026-10-18_sens2_F1"))
DEDUP = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P2", "p2_dataset_dedup.csv")


def main():
    fs = sorted(glob.glob(os.path.join(ENT, "s2b_opt_*.csv")))
    if not fs:
        print("sin archivos s2b_opt_*.csv: nada que analizar")
        return 0
    o = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
    ref = pd.read_csv(DEDUP)
    ref = ref[ref["clasificacion"] == "KALINA"]
    filas = []
    for T, g in o.groupby("banda"):
        k = g[g["clasificacion"] == "KALINA"]
        m = ref[(ref["T_fuente"] - T).abs() <= 10.0]
        md_ = m[~m["fuera_rango"].astype(bool)]
        fila = dict(T_fuente_K=float(T), T_fuente_C=float(T) - 273.15, n_eval=len(g), n_kalina=len(k),
                    eta_max_muestreo_pct=float(m["eta_pct"].max()) if len(m) else float("nan"), n_muestreo=len(m),
                    eta_max_muestreo_dentro_pct=float(md_["eta_pct"].max()) if len(md_) else float("nan"))
        if len(k):
            b = k.loc[k["eta"].astype(float).idxmax()]
            fila.update(eta_max_pct=100.0 * float(b["eta"]), P_alta=float(b["P_alta"]), P_baja=float(b["P_baja"]), x_b=float(b["x_b"]),
                        fuera_rango=bool(b["fuera_rango"]))
            kd = k[~k["fuera_rango"].astype(str).eq("True")]
            fila["eta_max_dentro_pct"] = 100.0 * float(kd["eta"].astype(float).max()) if len(kd) else float("nan")
        filas.append(fila)
    t = pd.DataFrame(filas).sort_values("T_fuente_K")
    if "eta_max_dentro_pct" not in t:
        t["eta_max_dentro_pct"] = float("nan")
    if "eta_max_pct" not in t:
        t["eta_max_pct"] = float("nan")
    t["mejora_pp"] = t["eta_max_pct"] - t["eta_max_muestreo_pct"]
    t["mejora_dentro_pp"] = t["eta_max_dentro_pct"] - t["eta_max_muestreo_dentro_pct"]
    os.makedirs(SAL, exist_ok=True)
    t.to_csv(os.path.join(SAL, "p6_opt_T.csv"), index=False, encoding="utf-8", lineterminator="\r\n")
    md = ["# Sens2 etapa B - eta maxima frente a T_fuente con busqueda local", "",
          "Busqueda coordenada a coordenada de P_alta, P_baja y x_b por banda; solo cuentan los puntos KALINA. Es un maximo local con tope de evaluaciones, no un optimo global. "
          "Comparacion: eta maxima del conjunto muestreado (todos los KALINA) a menos de 10 K de la banda, con y sin los puntos fuera del rango experimental (liquido > 420 K).", "",
          "| T_fuente (C) | evaluaciones | KALINA | eta max (%) | P_alta | P_baja | x_b | fuera de rango | eta max dentro del rango (%) | eta max muestreo (%) | mejora (pp) | eta max muestreo dentro del rango (%) | mejora dentro del rango (pp) |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in t.itertuples():
        mu = "-" if pd.isna(r.eta_max_muestreo_pct) else "%.2f" % r.eta_max_muestreo_pct
        if pd.isna(r.eta_max_pct):
            md.append("| %.0f | %d | %d | sin KALINA | - | - | - | - | - | %s | - | - | - |" % (r.T_fuente_C, r.n_eval, r.n_kalina, mu))
        else:
            md.append("| %.0f | %d | %d | %.2f | %.0f | %.0f | %.3f | %s | %s | %s | %s | %s | %s |" % (
                r.T_fuente_C, r.n_eval, r.n_kalina, r.eta_max_pct, r.P_alta, r.P_baja, r.x_b, "si" if r.fuera_rango else "no",
                "-" if pd.isna(r.eta_max_dentro_pct) else "%.2f" % r.eta_max_dentro_pct, mu,
                "-" if pd.isna(r.mejora_pp) else "%+.2f" % r.mejora_pp,
                "-" if pd.isna(r.eta_max_muestreo_dentro_pct) else "%.2f" % r.eta_max_muestreo_dentro_pct,
                "-" if pd.isna(r.mejora_dentro_pp) else "%+.2f" % r.mejora_dentro_pp))
    with open(os.path.join(SAL, "p6_opt_T.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    print("opt_T: %d bandas" % len(t))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
