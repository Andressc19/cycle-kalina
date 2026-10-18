# -*- coding: utf-8 -*-
"""Sens2 P2 - Paso 4: robustez del optimo.

Para los KALINA (total) con eta valida, por centro, se mide la distancia L1 normalizada
al punto no-KALINA mas cercano del mismo centro (frontera). Se compara el 10 % de KALINA
con mayor eta frente al resto (KS y medianas), se cuentan los del 10 % superior a una
sola variable de la frontera, y se listan el top-10 de eta por centro con su distancia a
la frontera, su situacion de rango experimental y su coincidencia con los 7 atipicos.

Salida: `p2_robustez.csv` (formato largo) y `p2_robustez.md`.
"""
import os

import numpy as np
import pandas as pd

import p2_comun as c

SALIDA = c.SALIDA
TOL = 1e-9


def puntos_frontera(d, lim):
    """Tabla por KALINA con eta valida: distancia y detalle de la frontera no-KALINA."""
    m = c.matriz_norm(d, lim)
    completo = ~np.isnan(m).any(axis=1)
    filas = []
    for centro in c.grupos_centro(d):
        idx = d.index[(d["centro"] == centro) & completo]
        kal = [i for i in idx if d.at[i, "kalina"] and np.isfinite(d.at[i, "eta_pct"])]
        nok = [i for i in idx if not d.at[i, "kalina"]]
        if not kal or not nok:
            continue
        idxk, dist = c.mas_cercano_l1(m[kal], m[nok])
        etas = np.array([d.at[i, "eta_pct"] for i in kal], float)
        thr = np.percentile(etas, 90)
        for i, gi in enumerate(kal):
            vec = nok[idxk[i]]
            dif = m[gi] - m[vec]
            nvars = int((np.abs(dif) > TOL).sum())
            j = int(np.argmax(np.abs(dif)))
            filas.append({
                "id_punto": d.at[gi, "id_punto"], "centro": centro,
                "eta": float(d.at[gi, "eta_pct"]), "D": float(d.at[gi, "D"]),
                "dist_frontera": float(dist[i]), "nvars_frontera": nvars,
                "var_frontera": c.ENTRADAS[j],
                "zona": "Top10" if d.at[gi, "eta_pct"] >= thr else "resto",
                "rango": "fuera del rango experimental" if d.at[gi, "fuera_rango"]
                         else "dentro del rango experimental",
                "atipico": "si" if d.at[gi, "id_punto"] in c.ATIPICOS else "no"})
    return pd.DataFrame(filas)


def fila(seccion, centro, clave, subclave, valor, txt=""):
    return {"seccion": seccion, "centro": centro, "clave": clave,
            "subclave": subclave, "valor": valor, "txt": txt}


def arma_tabla(pt):
    filas = []
    for centro in ["todos"] + list(pt["centro"].unique()):
        s = pt if centro == "todos" else pt[pt["centro"] == centro]
        top = s[s["zona"] == "Top10"]["dist_frontera"]
        res = s[s["zona"] == "resto"]["dist_frontera"]
        ks, p = c.ks(top, res)
        filas.append(fila("comparacion", centro, "dist_frontera", "Top10 vs resto",
                          ks, "med_top=%.4g;med_resto=%.4g;ks_p=%.4g;n_top=%d;n_resto=%d" % (
                              float(np.median(top)), float(np.median(res)), p,
                              len(top), len(res))))
        u = s[(s["zona"] == "Top10") & (s["nvars_frontera"] == 1)]
        for var, n in u["var_frontera"].value_counts().items():
            filas.append(fila("univariado_top", centro, "variable", var, int(n)))
        for lugar, (_, r) in enumerate(s.sort_values("eta", ascending=False).head(10)
                                       .iterrows(), 1):
            filas.append(fila("top10_eta", centro, "lugar", str(lugar), r["eta"],
                              "id=%s;dist=%.4g;rango=%s;atipico=%s" % (
                                  r["id_punto"], r["dist_frontera"], r["rango"],
                                  r["atipico"])))
    return pd.DataFrame(filas)


def markdown(tab, pt):
    comp = tab[tab["seccion"] == "comparacion"]
    l = ["# Sens2 P2 - Paso 4: robustez del optimo", "",
         "Distancia L1 normalizada de cada KALINA (total) con eta valida a la frontera",
         "no-KALINA mas cercana del mismo centro.", "",
         "## Top 10 % de eta frente al resto (distancia a la frontera)", "",
         "| centro | n Top10 | n resto | mediana Top10 | mediana resto | KS | p |",
         "|---|---|---|---|---|---|---|"]
    for _, r in comp.iterrows():
        d = dict(x.split("=") for x in r["txt"].split(";"))
        l.append("| %s | %s | %s | %s | %s | %.3g | %s |" % (
            r["centro"], d["n_top"], d["n_resto"], d["med_top"], d["med_resto"],
            r["valor"], d["ks_p"]))
    g = comp[comp["centro"] == "todos"].iloc[0]
    gd = dict(x.split("=") for x in g["txt"].split(";"))
    cerca = float(gd["med_top"]) < float(gd["med_resto"])
    l += ["", "## Respuesta: zona segura o cerca de la frontera",
          ("La mediana de la distancia a la frontera del 10 %% de mayor eta es %s y la "
           "del resto es %s. Por tanto el optimo esta %s.") % (
              gd["med_top"], gd["med_resto"],
              "MAS CERCA de la frontera que el resto" if cerca
              else "MAS LEJOS de la frontera que el resto (zona mas segura)"),
          "", "## Top-10 de eta por centro", "",
          "| centro | lugar | id | eta | dist frontera | rango | atipico |",
          "|---|---|---|---|---|---|---|"]
    t10 = tab[tab["seccion"] == "top10_eta"]
    for _, r in t10.iterrows():
        d = dict(x.split("=", 1) for x in r["txt"].split(";"))
        l.append("| %s | %s | %s | %.4g | %s | %s | %s |" % (
            r["centro"], r["subclave"], d["id"], r["valor"], d["dist"], d["rango"],
            d["atipico"]))
    u = tab[(tab["seccion"] == "univariado_top") & (tab["centro"] == "todos")]
    if len(u):
        ut = ", ".join("%s %d" % (r["subclave"], r["valor"]) for _, r in u.iterrows())
        l += ["", "Del 10 %% de mayor eta a una sola variable de la frontera: %s." % ut, ""]
    return "\n".join(l)


def main():
    d = c.cargar_dedup()
    lim = c.limites_normalizacion(d)
    pt = puntos_frontera(d, lim)
    tab = arma_tabla(pt)
    tab.to_csv(os.path.join(SALIDA, "p2_robustez.csv"), index=False)
    with open(os.path.join(SALIDA, "p2_robustez.md"), "w", encoding="utf-8") as f:
        f.write(markdown(tab, pt))
    g = tab[(tab["seccion"] == "comparacion") & (tab["centro"] == "todos")].iloc[0]
    print("p2_robustez.csv:", len(tab), "filas;", len(pt), "KALINA con eta valida")
    print("todos:", g["txt"])


if __name__ == "__main__":
    main()
