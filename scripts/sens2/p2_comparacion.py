# -*- coding: utf-8 -*-
"""Sens2 P2 - Paso 1: comparacion de distribuciones CORREGIBLE frente a KALINA.

Para cada variable (eta_pct, Wnet/m_b, rp, qreg_qi, dh_turb, q4), por centro y "todos",
frente a KALINA (total) y a KALINA dentro del rango experimental: n validos, mediana,
P10, P90 de cada grupo, KS con p-valor, diferencia de medianas (CORREGIBLE - KALINA)
con IC bootstrap y delta de Cliff. Se hace dos veces: (a) todos los puntos; (b) solo
LHS (estudios 3 y 14).
"""
import os

import numpy as np
import pandas as pd

import p2_comun as c

SALIDA = c.SALIDA
LHS = (3, 14)


def veredicto(dif, lo, hi):
    if not np.isfinite(dif):
        return "sin datos"
    if lo > 0:
        return "CORREGIBLE sobreestima"
    if hi < 0:
        return "CORREGIBLE subestima"
    return "sin diferencia clara"


def comparar(sub, centro, ref, kg, cor):
    filas = []
    for var in c.VARIABLES:
        xc = cor[var].to_numpy(float)
        xk = kg[var].to_numpy(float)
        nc, mc, c10, c90 = c.resumen(xc)
        nk, mk, k10, k90 = c.resumen(xk)
        ks_s, ks_p = c.ks(xc, xk)
        cd = c.cliff_delta(xc, xk)
        dif = mc - mk if (nc and nk) else np.nan
        lo, hi = c.bootstrap_dif_medianas(xc, xk)
        filas.append({"ambito": "", "centro": centro, "ref": ref, "variable": var,
                      "n_cor": nc, "n_kal": nk, "med_cor": mc, "p10_cor": c10,
                      "p90_cor": c90, "med_kal": mk, "p10_kal": k10, "p90_kal": k90,
                      "ks": ks_s, "ks_p": ks_p, "dif_mediana": dif, "ic_lo": lo,
                      "ic_hi": hi, "cliff_delta": cd})
    return filas


def bloque(df, ambito):
    filas = []
    for centro in c.grupos_centro(df) + ["todos"]:
        s = df if centro == "todos" else df[df["centro"] == centro]
        cor = s[s["clasificacion"] == "CORREGIBLE"]
        ktot = s[s["kalina"]]
        krang = s[s["kalina"] & (~s["fuera_rango"])]
        for ref, kg in [(c.REF_TOTAL, ktot), (c.REF_RANGO, krang)]:
            filas += comparar(s, centro, ref, kg, cor)
    for f in filas:
        f["ambito"] = ambito
    return filas


def leer(tabla, ambito, ref, variable, centro="todos"):
    m = tabla[(tabla["ambito"] == ambito) & (tabla["ref"] == ref)
              & (tabla["variable"] == variable) & (tabla["centro"] == centro)]
    return m.iloc[0] if len(m) else None


def seccion_mb(d):
    mb = c.m_b_por_estudio()
    no_uno = [e for e, v in mb.items() if any(abs(x - 1.0) > 1e-12 for x in v)]
    lin = ["", "## m_b por estudio (dataset completo, antes de deduplicar)", "",
           "Toda comparacion de W_net usa W_net especifico = Wnet/m_b (kW por kg/s).",
           "Estudios con algun m_b distinto de 1: %s." % (
               ", ".join(str(e) for e in no_uno) or "ninguno"), "",
           "| estudio | valores de m_b |", "|---|---|"]
    for e in sorted(mb):
        vals = ", ".join("%.3g" % v for v in mb[e])
        lin.append("| %d%s | %s |" % (e, " *" if e in no_uno else "", vals))
    lin += ["", "(*) Estudios que usan m_b distinto de 1 (el resto usa m_b = 1).",
            "En el dataset deduplicado de P2, los puntos con distinto m_b se conservan",
            "con su m_b; los W_net se comparan siempre divididos por m_b.", ""]
    return lin


def markdown(tabla, d):
    l = ["# Sens2 P2 - Paso 1: comparacion de distribuciones", "",
         "CORREGIBLE frente a KALINA, por centro y todos, frente a KALINA (total) y",
         "KALINA dentro del rango experimental. KS (scipy), diferencia de medianas",
         "con IC bootstrap (1000 remuestreos, semilla %d, 95 %%) y delta de Cliff." % c.SEMILLA,
         "", "## Respuesta: eta y W_net especifico (Wnet/m_b)", "",
         "| ambito | referencia | variable | mediana CORREGIBLE | mediana KALINA | dif (COR-KAL) | IC 95 % | lectura |",
         "|---|---|---|---|---|---|---|---|"]
    var_txt = {"eta_pct": "eta (%)", "wnet_mb": "Wnet/m_b (kW/kg/s)"}
    for ambito in ["todos los puntos", "LHS (estudios 3 y 14)"]:
        for ref in [c.REF_TOTAL, c.REF_RANGO]:
            for var in ["eta_pct", "wnet_mb"]:
                r = leer(tabla, ambito, ref, var)
                if r is None:
                    continue
                l.append("| %s | %s | %s | %.4g | %.4g | %+.4g | [%+.4g, %+.4g] | %s |" % (
                    ambito, ref, var_txt[var], r["med_cor"], r["med_kal"],
                    r["dif_mediana"], r["ic_lo"], r["ic_hi"],
                    veredicto(r["dif_mediana"], r["ic_lo"], r["ic_hi"])))
    l += ["", "## eta y W_net especifico por centro (KALINA total, todos los puntos)", "",
          "| centro | variable | n COR | n KAL | mediana COR | mediana KAL | dif | IC 95 % | KS | p | lectura |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for centro in [x for x in tabla["centro"].unique() if x != "todos"]:
        for var in ["eta_pct", "wnet_mb"]:
            r = leer(tabla, "todos los puntos", c.REF_TOTAL, var, centro)
            if r is None:
                continue
            l.append("| %s | %s | %d | %d | %.4g | %.4g | %+.4g | [%+.4g, %+.4g] | %.3g | %.3g | %s |" % (
                centro, var_txt[var], r["n_cor"], r["n_kal"], r["med_cor"], r["med_kal"],
                r["dif_mediana"], r["ic_lo"], r["ic_hi"], r["ks"], r["ks_p"],
                veredicto(r["dif_mediana"], r["ic_lo"], r["ic_hi"])))
    l += ["", "Lectura: dif = mediana(CORREGIBLE) - mediana(KALINA); dif > 0 = el",
          "CORREGIBLE sobreestima, dif < 0 = subestima; si el IC cruza 0, sin diferencia",
          "clara. n validos = puntos con la variable presente y finita."]
    l += seccion_mb(d)
    return "\n".join(l)


def main():
    d = c.cargar_dedup()
    filas = bloque(d, "todos los puntos")
    filas += bloque(d[d["estudio"].isin(LHS)], "LHS (estudios 3 y 14)")
    tabla = pd.DataFrame(filas)
    tabla.to_csv(os.path.join(SALIDA, "p2_comparacion.csv"), index=False)
    with open(os.path.join(SALIDA, "p2_comparacion.md"), "w", encoding="utf-8") as f:
        f.write(markdown(tabla, d))
    print("p2_comparacion.csv:", len(tabla), "filas")
    mb = c.m_b_por_estudio()
    print("estudios con m_b != 1:", [e for e, v in mb.items()
                                     if any(abs(x - 1.0) > 1e-12 for x in v)])
    for ambito in ["todos los puntos", "LHS (estudios 3 y 14)"]:
        for ref in [c.REF_TOTAL, c.REF_RANGO]:
            r = leer(tabla, ambito, ref, "eta_pct")
            print("%s | %s | eta dif=%+.4g IC[%+.4g, %+.4g] %s" % (
                ambito, ref, r["dif_mediana"], r["ic_lo"], r["ic_hi"],
                veredicto(r["dif_mediana"], r["ic_lo"], r["ic_hi"])))


if __name__ == "__main__":
    main()
