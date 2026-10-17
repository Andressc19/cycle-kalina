# -*- coding: utf-8 -*-
"""Sens2 P2 - Paso 5: verificacion y resumen.

Controles (una linea OK/FALLA cada uno):
1. n deduplicado = filas de P1 - duplicados exactos.
2. la suma de clases por clasificacion = n.
3. cada vecino KALINA de p2_distancia existe, es KALINA y es del mismo centro.
4. la distancia L1 es >= 0 y = 0 solo si las entradas coinciden.
5. el n de variables que difieren es coherente con la distancia L1.
6. sin palabras prohibidas en las salidas.

Ademas escribe `p2_resumen.md` con las cuatro respuestas del Paso 5.
"""
import os

import numpy as np
import pandas as pd

import p2_comun as c

SALIDA = c.SALIDA
PROHIBIDAS = ["confiable", "citable", "fuera de rango del motor"]
CLASES = {"KALINA", "CORREGIBLE", "NO_CONVERGIO", "INVIABLE", "NO_CONVERGIO"}
TOL = 1e-9


def linea(nombre, ok, detalle):
    print("Control %s: %s - %s" % (nombre, "OK" if ok else "FALLA", detalle))
    return ok


def control_1(d):
    p1 = pd.read_csv(c.P1)
    p1["centro"] = p1["centro"].fillna(c.SIN_CENTRO)
    quitadas = int(p1.duplicated(c.ENTRADAS + ["centro"], keep="first").sum())
    esperado = len(p1) - quitadas
    ok = len(d) == esperado and len(d) < len(p1)
    return linea("1", ok, "n=%d, P1=%d, duplicados=%d, esperado=%d" % (
        len(d), len(p1), quitadas, esperado))


def control_2(d):
    vc = d["clasificacion"].value_counts()
    ok = int(vc.sum()) == len(d) and set(vc.index).issubset(CLASES)
    return linea("2", ok, "suma clases=%d, n=%d, clases=%s" % (
        int(vc.sum()), len(d), list(vc.index)))


def control_3(d, dist):
    clave = d.drop_duplicates(["centro", "id_punto"]).set_index(["centro", "id_punto"])
    faltan, mal, n = 0, 0, 0
    for _, r in dist.iterrows():
        n += 1
        k = (r["centro"], r["vecino_id"])
        if k not in clave.index:
            faltan += 1
        elif clave.at[k, "clasificacion"] != "KALINA":
            mal += 1
    return linea("3", faltan == 0 and mal == 0,
                 "vecinos=%d, inexistentes=%d, no-KALINA=%d" % (n, faltan, mal))


def control_4(d, dist):
    fin = dist[np.isfinite(dist["l1"])]
    neg = int((fin["l1"] < 0).sum())
    ceros = fin[fin["l1"] <= TOL]
    clave = d.drop_duplicates(["centro", "id_punto"]).set_index(["centro", "id_punto"])
    mal = 0
    for _, r in ceros.iterrows():
        a = clave.loc[(r["centro"], r["id_punto"]), c.ENTRADAS].to_numpy(float)
        b = clave.loc[(r["centro"], r["vecino_id"]), c.ENTRADAS].to_numpy(float)
        if not np.allclose(a, b, atol=1e-12):
            mal += 1
    return linea("4", neg == 0 and mal == 0,
                 "l1<0=%d, l1=0=%d, con entradas distintas=%d" % (neg, len(ceros), mal))


def control_5(dist):
    l1 = dist["l1"].to_numpy(float)
    nv = dist["nvars_diff"].to_numpy(float)
    rango_ok = bool((nv >= 0).all() and (nv <= len(c.ENTRADAS)).all())
    coh = bool(((l1 > TOL) == (nv >= 1)).all())
    return linea("5", rango_ok and coh,
                 "nvars fuera de [0,10]=%d, incoherentes=%d" % (
                     0 if rango_ok else 1, 0 if coh else 1))


def control_6():
    malos = []
    for nombre in sorted(os.listdir(SALIDA)):
        ruta = os.path.join(SALIDA, nombre)
        if not os.path.isfile(ruta) or not nombre.lower().endswith((".md", ".csv", ".txt")):
            continue
        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            txt = f.read().lower()
        for p in PROHIBIDAS:
            if p in txt:
                malos.append("%s:%s" % (nombre, p))
    return linea("6", len(malos) == 0, "archivos con palabra prohibida: %s" % (malos or "0"))


def resumen():
    comp = pd.read_csv(os.path.join(SALIDA, "p2_comparacion.csv"))
    res = pd.read_csv(os.path.join(SALIDA, "p2_distancia_resumen.csv"))
    rob = pd.read_csv(os.path.join(SALIDA, "p2_robustez.csv"))
    filas = lambda t, ref, var: t[(t["ambito"] == "todos los puntos")
                                  & (t["ref"] == ref) & (t["variable"] == var)
                                  & (t["centro"] == "todos")].iloc[0]
    e = filas(comp, c.REF_TOTAL, "eta_pct")
    w = filas(comp, c.REF_TOTAL, "wnet_mb")
    u = res[(res["seccion"] == "univariado") & (res["centro"] == "todos")
            & (res["n"] > 0)]
    top = u.sort_values("valor", ascending=False)
    eta = res[(res["seccion"] == "eta") & (res["centro"] == "todos")].iloc[0]
    g = rob[(rob["seccion"] == "comparacion") & (rob["centro"] == "todos")].iloc[0]
    gd = dict(x.split("=") for x in g["txt"].split(";"))
    t = []
    t.append("# Sens2 P2 - resumen (Paso 5)\n")
    t.append("## 1. Los CORREGIBLE, sobreestiman o subestiman a los KALINA (total)?\n")
    t.append("- eta: mediana CORREGIBLE %.4g frente a KALINA %.4g; diferencia %+.4g "
             "con IC 95 %% [%+.4g, %+.4g] -> %s.\n" % (
                 e["med_cor"], e["med_kal"], e["dif_mediana"], e["ic_lo"], e["ic_hi"],
                 "sobreestiman" if e["ic_lo"] > 0 else (
                     "subestiman" if e["ic_hi"] < 0 else "sin diferencia clara")))
    t.append("- W_net especifico: mediana CORREGIBLE %.4g frente a KALINA %.4g; "
             "diferencia %+.4g con IC 95 %% [%+.4g, %+.4g] -> %s.\n" % (
                 w["med_cor"], w["med_kal"], w["dif_mediana"], w["ic_lo"], w["ic_hi"],
                 "sobreestiman" if w["ic_lo"] > 0 else (
                     "subestiman" if w["ic_hi"] < 0 else "sin diferencia clara")))
    t.append("## 2. Vale rescatar un CORREGIBLE?\n")
    t.append("Llevarlo a un KALINA cercano cambia eta en mediana %+.4g por punto "
             "(IC 95 %% %s para eta(vecino) - eta(CORREGIBLE)).\n" % (
                 eta["mediana"], eta["extra"]))
    t.append("## 3. Que variable rescata mas?\n")
    t.append("La variable que mas veces deja a un CORREGIBLE a una sola variable de un "
             "KALINA es %s (%s, %.0f %% de los CORREGIBLE).\n" % (
                 top.iloc[0]["clave"], top.iloc[0]["subclave"],
                 100 * top.iloc[0]["valor"]))
    t.append("## 4. El optimo esta en zona segura?\n")
    t.append("La distancia a la frontera no-KALINA del 10 %% de mayor eta (%.4g) es %s "
             "que la del resto (%.4g); el optimo esta %s.\n" % (
                 float(gd["med_top"]),
                 "menor" if float(gd["med_top"]) < float(gd["med_resto"]) else "mayor",
                 float(gd["med_resto"]),
                 "cerca de la frontera" if float(gd["med_top"]) < float(gd["med_resto"])
                 else "en una zona mas segura"))
    with open(os.path.join(SALIDA, "p2_resumen.md"), "w", encoding="utf-8") as f:
        f.write("".join(t))
    print("p2_resumen.md escrito.")


def main():
    d = c.cargar_dedup()
    dist = pd.read_csv(os.path.join(SALIDA, "p2_distancia.csv"))
    oks = [control_1(d), control_2(d), control_3(d, dist), control_4(d, dist),
           control_5(dist), control_6()]
    resumen()
    print("RESULTADO GLOBAL: %s" % ("OK" if all(oks) else "FALLA"))


if __name__ == "__main__":
    main()
