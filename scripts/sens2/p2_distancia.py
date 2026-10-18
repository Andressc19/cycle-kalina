# -*- coding: utf-8 -*-
"""Sens2 P2 - Paso 3: distancia a KALINA y que mover.

Espacio normalizado con el min/max observado de cada una de las 10 entradas. Para cada
CORREGIBLE se busca, dentro del mismo centro, el KALINA (total) mas cercano por distancia
L1 normalizada (numpy por bloques). Se reporta por punto y se resumen: rescate
univariado, distribucion de L1 y n de variables distintas, cambio de eta al rescatar y
relacion D <-> L1 (Spearman).
"""
import os

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

import p2_comun as c

SALIDA = c.SALIDA
TOL = 1e-9


def por_punto(d, lim):
    m = c.matriz_norm(d, lim)
    filas = []
    for centro in c.grupos_centro(d):
        idxs = d.index[d["centro"] == centro]
        cor = idxs[d.loc[idxs, "clasificacion"] == "CORREGIBLE"]
        kal = idxs[d.loc[idxs, "kalina"]]
        if len(cor) == 0 or len(kal) == 0:
            continue
        kn = m[kal]
        idx, dist = c.mas_cercano_l1(m[cor], kn)
        for i, gi in enumerate(cor):
            vec = kal[idx[i]]
            dif = m[gi] - m[vec]
            nvars = int((np.abs(dif) > TOL).sum())
            j = int(np.argmax(np.abs(dif)))
            var = c.ENTRADAS[j]
            vo = float(d.at[gi, var])
            vd = float(d.at[vec, var])
            direccion = "sube" if vd > vo else ("baja" if vd < vo else "igual")
            filas.append({
                "id_punto": d.at[gi, "id_punto"], "centro": centro,
                "D": float(d.at[gi, "D"]),
                "viol_dominante": c.violacion_dominante(d.loc[gi]),
                "vecino_id": d.at[vec, "id_punto"], "l1": float(dist[i]),
                "nvars_diff": nvars, "var_cambia": var, "val_origen": vo,
                "val_destino": vd, "direccion": direccion,
                "eta_cor": float(d.at[gi, "eta_pct"]),
                "eta_vecino": float(d.at[vec, "eta_pct"])})
    return pd.DataFrame(filas)


def fila(seccion, centro, clave, subclave, n, p10=np.nan, mediana=np.nan, p90=np.nan,
         valor=np.nan, extra=""):
    return {"seccion": seccion, "centro": centro, "clave": clave, "subclave": subclave,
            "n": n, "p10": p10, "mediana": mediana, "p90": p90, "valor": valor,
            "extra": extra}


def resumen_l1_eta(d):
    filas = []
    for centro in c.grupos_centro(d) + ["todos"]:
        s = d if centro == "todos" else d[d["centro"] == centro]
        for clave, col in [("l1", "l1"), ("nvars", "nvars_diff")]:
            n, med, p10, p90 = c.resumen(s[col])
            filas.append(fila("distribucion", centro, clave, "", n, p10, med, p90))
        e = s.dropna(subset=["eta_cor", "eta_vecino"])
        n = len(e)
        if n:
            dif = (e["eta_vecino"] - e["eta_cor"]).to_numpy(float)
            lo, hi = c.bootstrap_dif_medianas(e["eta_vecino"], e["eta_cor"])
            filas.append(fila("eta", centro, "eta_vecino_minus_cor", "", n,
                              mediana=float(np.median(dif)), valor=lo,
                              extra="ic_lo=%.4g;ic_hi=%.4g" % (lo, hi)))
        r = spearmanr(s["D"], s["l1"])
        filas.append(fila("spearman", centro, "D_vs_l1", "", len(s),
                          valor=float(r.statistic), extra="p=%.4g" % r.pvalue))
    return filas


def resumen_univariado(d):
    filas = []
    for centro in ["todos"] + [x for x in c.grupos_centro(d)]:
        s = d if centro == "todos" else d[d["centro"] == centro]
        total = len(s)
        u = s[s["nvars_diff"] == 1]
        g = u.groupby(["var_cambia", "direccion"]).size()
        for (var, dr), n in g.items():
            filas.append(fila("univariado", centro, var, dr, int(n),
                              valor=float(n) / total))
        g2 = u.groupby(["viol_dominante", "var_cambia", "direccion"]).size()
        for (dom, var, dr), n in g2.items():
            filas.append(fila("univariado_dom", centro, dom, "%s|%s" % (var, dr),
                              int(n), valor=float(n) / total))
    return filas


def markdown(d, res):
    u = res[(res["seccion"] == "univariado") & (res["centro"] == "todos")]
    u1 = u[u["n"] > 0].sort_values("valor", ascending=False)
    dist = res[(res["seccion"] == "distribucion") & (res["centro"] == "todos")]
    l1 = dist[dist["clave"] == "l1"].iloc[0]
    nv = dist[dist["clave"] == "nvars"].iloc[0]
    eta = res[(res["seccion"] == "eta") & (res["centro"] == "todos")].iloc[0]
    sp = res[(res["seccion"] == "spearman") & (res["centro"] == "todos")].iloc[0]
    top = ", ".join("%s %s %.0f %%" % (r["clave"], r["subclave"], 100 * r["valor"])
                    for _, r in u1.head(5).iterrows())
    l = ["# Sens2 P2 - Paso 3: distancia a KALINA y que mover", "",
         "Distancia L1 normalizada (10 entradas al rango [0, 1] observado) al KALINA",
         "(total) mas cercano dentro del mismo centro.", "",
         "## Rescate univariado",
         "Fraccion de CORREGIBLE a una sola variable de un KALINA (sobre el total de",
         "CORREGIBLE): %s." % top, "",
         "## Distribucion (todos)",
         "- L1: P10 %.4g, mediana %.4g, P90 %.4g." % (l1["p10"], l1["mediana"], l1["p90"]),
         "- N de variables distintas: P10 %.0f, mediana %.0f, P90 %.0f." % (
             nv["p10"], nv["mediana"], nv["p90"]), "",
         "## Cambio de eta al rescatar",
         "eta(vecino KALINA) - eta(CORREGIBLE): mediana %+.4g; IC 95 %% %s (n = %d)." % (
             eta["mediana"], eta["extra"], eta["n"]), "",
         "## D frente a L1",
         "Spearman rho = %+.3f (%s)." % (sp["valor"], sp["extra"]), "",
         "Los detalles por centro y por violacion dominante estan en",
         "`p2_distancia_resumen.csv`.", ""]
    return "\n".join(l)


def main():
    d = c.cargar_dedup()
    lim = c.limites_normalizacion(d)
    pp = por_punto(d, lim)
    pp.to_csv(os.path.join(SALIDA, "p2_distancia.csv"), index=False)
    res = pd.concat([pd.DataFrame(resumen_l1_eta(pp)),
                     pd.DataFrame(resumen_univariado(pp))], ignore_index=True)
    res.to_csv(os.path.join(SALIDA, "p2_distancia_resumen.csv"), index=False)
    with open(os.path.join(SALIDA, "p2_distancia_resumen.md"), "w", encoding="utf-8") as f:
        f.write(markdown(pp, res))
    print("p2_distancia.csv:", len(pp), "puntos")
    print("p2_distancia_resumen.csv:", len(res), "filas")


if __name__ == "__main__":
    main()
