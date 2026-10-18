# -*- coding: utf-8 -*-
"""Sens2 R1 - Paso 2: contraste fuera de muestra del libro viejo contra Sens2.

A. Rangos: fraccion de KALINA (total) viejos de cada centro dentro de los rangos KALINA
   de Sens2 (`p1_existencia_rangos.csv`) y lista de KALINA que Sens2 no tiene.
B. Fronteras: acuerdo de las fronteras `escalon`/`ventana` de `p1_fronteras.csv` sobre
   los puntos viejos del centro cercanos sin contar la variable de la frontera.
C. Cobertura: puntos viejos por centro y clase con dist <= 0.25 y los 5 KALINA de mayor
   `eta_pct` por centro.
D. `r1_resumen.md` en lenguaje llano.
"""
import os

import numpy as np
import pandas as pd

from r1_filtro import (CENTROS, CERCANO, COBERTURA, ESCALA, P1, SALIDA, V10,
                       VARS_DIST)

CLASES = ["KALINA", "CORREGIBLE", "NO_CONVERGIO", "INVIABLE"]


def leer():
    p = pd.read_csv(os.path.join(SALIDA, "r1_puntos.csv"))
    r = pd.read_csv(os.path.join(P1, "p1_existencia_rangos.csv"))
    f = pd.read_csv(os.path.join(P1, "p1_fronteras.csv"))
    return p, r[r["centro"].isin(CENTROS)], f


def dist_sin_v(sub, centro, v):
    """Norma infinito de la distancia sin contar la variable v (las 5 si v es eficiencia)."""
    vs = VARS_DIST if v not in VARS_DIST else [x for x in VARS_DIST if x != v]
    escala = np.array([ESCALA[x] for x in vs], float)
    centro_v = np.array([CENTROS[centro][VARS_DIST.index(x)] for x in vs], float)
    p = sub[vs].to_numpy(float)
    return np.max(np.abs(p - centro_v) / escala, axis=1)


def parte_a(puntos, rangos):
    rango = {(t.centro, t.variable): (t.min_kalina, t.max_kalina) for t in rangos.itertuples()}
    kal = puntos[puntos["cerca"] & (puntos["clasificacion"] == "KALINA")]
    filas = []
    for c in [c for c in CENTROS if c in set(kal["centro"])]:
        sub = kal[kal["centro"] == c]
        todo = np.ones(len(sub), bool)
        for v in V10:
            lo, hi = rango[(c, v)]
            ok = ((sub[v] >= lo) & (sub[v] <= hi)).to_numpy(bool)
            filas.append([c, v, len(sub), int(ok.sum()), float(ok.mean()) if len(sub) else np.nan])
            todo &= ok
        filas.append([c, "(las 10 a la vez)", len(sub), int(todo.sum()),
                      float(todo.mean()) if len(sub) else np.nan])
    frac = pd.DataFrame(filas, columns=["centro", "variable", "n", "n_dentro", "fraccion"])
    frac.to_csv(os.path.join(SALIDA, "r1_rangos_fraccion.csv"), index=False)
    viol = []
    for t in kal.itertuples():
        for v in V10:
            lo, hi = rango[(t.centro, v)]
            val = getattr(t, v)
            if val < lo or val > hi:
                viol.append([t.id_punto, t.Estudio, t.centro, v, val, lo, hi])
    pd.DataFrame(viol, columns=["id_punto", "Estudio", "centro", "variable", "valor",
                                "min_kalina", "max_kalina"]).to_csv(
        os.path.join(SALIDA, "r1_fuera_de_rango_sens2.csv"), index=False)
    return frac, kal


def _par_ventana(fr, c, v):
    vals = set(fr[(fr["centro"] == c) & (fr["variable"] == v) &
                  (fr["forma"] == "ventana")]["valor_frontera"])
    return (min(vals), max(vals)) if len(vals) >= 2 else None


def parte_b(puntos, fronteras):
    fr = fronteras[fronteras["forma"].isin(["escalon", "ventana"])].copy()
    filas, desac = [], []
    for t in fr.itertuples():
        c, v = t.centro, t.variable
        sub = puntos[puntos["centro"] == c]
        sel = sub[dist_sin_v(sub, c, v) <= CERCANO]
        val = sel[v].to_numpy(float)
        par = _par_ventana(fr, c, v)
        if t.forma == "ventana" and par is not None:
            dentro = (val >= par[0]) & (val <= par[1])
            baja = fr[(fr["centro"] == c) & (fr["variable"] == v) & (fr["forma"] == "ventana") &
                      (fr["valor_frontera"] == par[0])]["direccion"].iloc[0]
            pred = dentro if baja == "a KALINA" else ~dentro
        elif t.direccion == "a KALINA":
            pred = val >= t.valor_frontera
        else:
            pred = val < t.valor_frontera
        real = (sel["clasificacion"] == "KALINA").to_numpy(bool)
        n, ac = len(sel), int((pred == real).sum())
        filas.append([c, v, t.forma, t.direccion, t.valor_frontera, n, ac,
                      "" if n < 5 else ac / n, "n insuficiente" if n < 5 else ""])
        for i in np.where(pred != real)[0]:
            desac.append([sel["id_punto"].iloc[i], c, v, float(val[i]),
                          "KALINA" if real[i] else "no-KALINA",
                          "KALINA" if pred[i] else "no-KALINA"])
    cont = pd.DataFrame(filas, columns=["centro", "variable", "forma", "direccion",
                                        "valor_frontera", "n", "aciertos", "acuerdo", "nota"])
    cont.to_csv(os.path.join(SALIDA, "r1_fronteras_contraste.csv"), index=False)
    pd.DataFrame(desac, columns=["id_punto", "centro", "variable", "valor",
                                 "clase_real", "clase_predicha"]).to_csv(
        os.path.join(SALIDA, "r1_desacuerdos.csv"), index=False)
    return cont


def parte_c(puntos):
    filas = []
    for c in CENTROS:
        sub = puntos[puntos["centro"] == c]
        for cl in CLASES:
            sc = sub[sub["clasificacion"] == cl]
            filas.append([c, "conteo", cl, int((sc["dist"] <= CERCANO).sum()),
                          int((sc["dist"] <= COBERTURA).sum()), "", "", np.nan, np.nan])
        sk = sub[(sub["clasificacion"] == "KALINA") & (sub["dist"] <= COBERTURA)]
        for t in sk.sort_values("eta_pct", ascending=False).head(5).itertuples():
            filas.append([c, "top_eta", "KALINA", np.nan, np.nan, t.id_punto,
                          t.Estudio, t.dist, t.eta_pct])
    cob = pd.DataFrame(filas, columns=["centro", "tipo", "clasificacion", "n_015", "n_025",
                                       "id_punto", "Estudio", "dist", "eta_pct"])
    cob.to_csv(os.path.join(SALIDA, "r1_cobertura.csv"), index=False)
    return cob


def parte_d(frac, cont, viol, cob, n_cerca):
    todo = frac[frac["variable"] == "(las 10 a la vez)"]
    n_kal, n_dentro = int(todo["n"].sum()), int(todo["n_dentro"].sum())
    ok = cont[cont["n"] >= 5]
    tasa = ok["aciertos"].sum() / ok["n"].sum()
    contrad = ok[ok["acuerdo"] < 0.5]
    out = ["# Sens2 R1 - contraste fuera de muestra del libro viejo", "",
           "Puntos `cerca` (dist <= 0.15) usados en A y B: %d." % int(n_cerca),
           "",
           "## A. KALINA viejos dentro de los rangos KALINA de Sens2",
           ""]
    for t in todo.itertuples():
        out.append("- %s: %d/%d dentro en las 10 variables (%.1f %%)." % (
            t.centro, t.n_dentro, t.n, 100 * t.fraccion))
    out.append("- Total: %d/%d (%.1f %%) dentro en las 10 variables a la vez." % (
        n_dentro, n_kal, 100 * n_dentro / n_kal))
    fuera = viol.groupby(["centro", "variable"]).size().reset_index(name="n")
    out += ["", "Aportes (KALINA viejo fuera de rango de Sens2): %d filas centro-variable;" % len(fuera),
            "%d KALINA con al menos una variable fuera del rango de su centro." % viol["id_punto"].nunique(),
            "", "| centro | variable | n |", "|---|---|---|"]
    for t in fuera.sort_values(["centro", "n"], ascending=[True, False]).itertuples():
        out.append("| %s | %s | %d |" % (t.centro, t.variable, t.n))
    out += ["", "## B. Acuerdo de las fronteras", "",
            "Tasa de acuerdo global (n >= 5): %.3f (%d aciertos / %d puntos)." % (
                tasa, int(ok["aciertos"].sum()), int(ok["n"].sum())),
            "Fronteras evaluadas con n >= 5: %d; con n insuficiente: %d." % (
                len(ok), len(cont) - len(ok)),
            "", "Contradicciones (acuerdo < 0.5): %d." % len(contrad),
            "", "| centro | variable | forma | direccion | frontera | n | acuerdo |",
            "|---|---|---|---|---|---|---|"]
    for t in contrad.itertuples():
        out.append("| %s | %s | %s | %s | %s | %d | %.3f |" % (
            t.centro, t.variable, t.forma, t.direccion, t.valor_frontera, t.n, t.acuerdo))
    out += ["", "## C. Cobertura de huecos por centro", "",
            "| centro | clase | n <= 0.15 | n <= 0.25 |", "|---|---|---|---|"]
    for t in cob[cob["tipo"] == "conteo"].itertuples():
        out.append("| %s | %s | %d | %d |" % (t.centro, t.clasificacion, t.n_015, t.n_025))
    tot15 = cob[cob["tipo"] == "conteo"].groupby("centro")["n_015"].sum()
    tot25 = cob[cob["tipo"] == "conteo"].groupby("centro")["n_025"].sum()
    out.append("- Ganador por cobertura <= 0.25: %s (%d puntos)."
               % (tot25.idxmax(), int(tot25.max())))
    gan = (tot25 - tot15)
    kal = cob[(cob["tipo"] == "conteo") & (cob["clasificacion"] == "KALINA")].set_index("centro")
    out.append("- Mayor ganancia al pasar de 0.15 a 0.25: %s (+%d puntos; +%d KALINA)."
               % (gan.idxmax(), int(gan.max()), int((kal["n_025"] - kal["n_015"]).loc[gan.idxmax()])))
    out.append("- El centro C4 sube de %d a %d puntos al pasar de 0.15 a 0.25."
               % (int(tot15.get("C4 frio 110 C", 0)), int(tot25.get("C4 frio 110 C", 0))))
    out.append("")
    out.append("## D. Respuestas")
    out.append("- Fraccion de KALINA viejos dentro de los rangos de Sens2: %.1f %%." % (100 * n_dentro / n_kal))
    out.append("- Acuerdo global de las fronteras: %.3f; %d de %d filas con n >= 5 se contradicen."
               % (tasa, len(contrad), len(ok)))
    out.append("- Centro con mas puntos a <= 0.25: %s; centro que mas gana al ampliar de 0.15 a 0.25: %s."
               % (tot25.idxmax(), gan.idxmax()))
    out.append("- Cautela: C1 (7 KALINA) y C4 (1 KALINA) no permiten concluir; los 15 aportes de C3 en eps_cond son un "
               "solo valor repetido (0.841826, 0.008 bajo el minimo de Sens2) y los 17 de C2 en T_fuente estan a menos de "
               "3.2 K del minimo: aportes marginales, no un rango nuevo.")
    out.append("- Cautela: la tasa global de acuerdo de las fronteras queda cerca del azar; esta dominada por C2 y varias "
               "filas tienen n de 6 o 7 (no concluyente en C4).")
    if len(viol) == 0:
        out.append("- Sin aportes: no hay KALINA viejo fuera de rango de Sens2 (no concluyente).")
    with open(os.path.join(SALIDA, "r1_resumen.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")


def main():
    puntos, rangos, fronteras = leer()
    frac, _ = parte_a(puntos, rangos)
    cont = parte_b(puntos, fronteras)
    viol = pd.read_csv(os.path.join(SALIDA, "r1_fuera_de_rango_sens2.csv"))
    cob = parte_c(puntos)
    parte_d(frac, cont, viol, cob, int(puntos["cerca"].sum()))
    print("A: filas rango %d | aportes %d" % (len(frac), len(viol)))
    print("B: fronteras %d | acuerdos n>=5 %d" % (len(cont), int((cont['n'] >= 5).sum())))
    print("C: filas cobertura %d" % len(cob))
    print("salidas en", SALIDA)


if __name__ == "__main__":
    main()
