# -*- coding: utf-8 -*-
"""Sens2 A1c - p5_cifras_check_c: recalculo independiente de las variables distinguibles (FDR).

Lee `p6_nulo_perm.csv`, calcula para cada (bloque, respuesta) los q-valores de Benjamini-Hochberg de
los `p_perm` de las variables reales (implementacion propia) y marca una variable como distinguible si
tiene q < 0.05 en al menos 2 metodos. Compara ese conjunto con la lista que escriben las conclusiones
(F1, F2, F3) en `p5_conclusiones.csv` y cuenta, por respuesta, cuantas variables son distinguibles con
umbral de 1, 2 y 3 metodos (suma de los 4 bloques). Escribe p5_cifras_check_c.csv y .md; sale con
codigo 1 si hay FALLA. No modifica ningun texto.
"""
import os
import re
import sys

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
ENTRADA = os.path.join(RAIZ, "resultados", "2026-10-18_sens2_F1", "p6_nulo_perm.csv")
P5 = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P5")
CONCLUSIONES = os.path.join(P5, "p5_conclusiones.csv")
SAL_CSV = os.path.join(P5, "p5_cifras_check_c.csv")
SAL_MD = os.path.join(P5, "p5_cifras_check_c.md")

Q = 0.05
UMBRAL = 2
CKS = ("C1", "C2", "C3", "C4")
BLOQUES = {"C1": "E3 C1 Husavik", "C2": "E3 C2 ancla A*",
           "C3": "E14 C3 caliente 150 C", "C4": "E14 C4 frio 110 C"}
MAPA = {"Y2 eta (%)": "F1", "Y3 W_net/m_b": "F2", "Y1 KALINA (total)": "F3"}
ORDEN = ["Y1 KALINA (total)", "Y2 eta (%)", "Y3 W_net/m_b"]


def bh(p):
    """q-valores de Benjamini-Hochberg propios (NaN se conservan)."""
    p = np.asarray(p, float)
    q = np.full(len(p), np.nan)
    ok = np.where(np.isfinite(p))[0]
    if len(ok) == 0:
        return q
    o = ok[np.argsort(p[ok], kind="stable")]
    m = len(o)
    vals = p[o] * m / np.arange(1, m + 1)
    vals = np.minimum.accumulate(vals[::-1])[::-1]
    q[o] = np.clip(vals, 0.0, 1.0)
    return q


def recalcular(df):
    """Anade la columna q (BH por bloque y respuesta) a las filas reales."""
    r = df[df["tipo"] == "real"].copy()
    r["q"] = np.nan
    for _, ix in r.groupby(["bloque", "respuesta"]).groups.items():
        r.loc[ix, "q"] = bh(r.loc[ix, "p_perm"])
    return r


def distinguibles(r, bloque, respuesta, umbral=UMBRAL):
    """Variables con q < Q en al menos `umbral` metodos del grupo (bloque, respuesta)."""
    g = r[(r["bloque"] == bloque) & (r["respuesta"] == respuesta)]
    s = g[g["q"] < Q].groupby("variable").size()
    return set(s[s >= umbral].index)


def lista_texto(texto, ck):
    """Lista de variables que sigue a `C<k> `, tomada despues de la palabra 'distinguibles'."""
    pos = texto.rfind("distinguibles")
    frag = texto[pos:] if pos >= 0 else texto
    m = re.search(re.escape(ck) + r" (.*?)(?:;|\.)", frag)
    if not m:
        return None
    trozo = re.sub(r"\([^)]*\)", "", m.group(1))          # quita el parentetico final de C4 en F2
    return [v.strip() for v in trozo.split(",") if v.strip()]


def comparar(r, texto, cid):
    """12 (cid, bloque) -> control sobre el conjunto de variables distinguibles."""
    filas = []
    respuesta = [k for k, v in MAPA.items() if v == cid][0]
    for ck in CKS:
        bloque = BLOQUES[ck]
        recalc = distinguibles(r, bloque, respuesta)
        lista = lista_texto(texto, ck)
        control = "%s %s" % (cid, ck)
        if lista is None:
            filas.append([control, "FALLA", "sin lista C%s en el texto de %s" % (ck, cid)])
            continue
        texto_set = set(lista)
        ok = recalc == texto_set
        detalle = "%s: recalculado %d, texto %d" % (bloque, len(recalc), len(texto_set))
        if not ok:
            detalle += "; sobra recalculado %s; falta en recalculado %s" % (
                sorted(recalc - texto_set), sorted(texto_set - recalc))
        filas.append([control, "OK" if ok else "FALLA", detalle])
    return filas


def umbrales(r):
    """[cid, respuesta, #distinguibles con 1, 2 y 3 metodos (suma de los 4 bloques)]."""
    tabla = []
    for respuesta in ORDEN:
        cid = MAPA[respuesta]
        row = [cid, respuesta]
        for umbral in (1, 2, 3):
            row.append(sum(len(distinguibles(r, BLOQUES[ck], respuesta, umbral)) for ck in CKS))
        tabla.append(row)
    return tabla


def main():
    df = pd.read_csv(ENTRADA)
    r = recalcular(df)
    concl = pd.read_csv(CONCLUSIONES).set_index("id")
    filas = []
    for respuesta in ORDEN:
        cid = MAPA[respuesta]
        if cid not in concl.index:
            filas.append([cid, "FALLA", "conclusion %s ausente de p5_conclusiones.csv" % cid])
            continue
        filas += comparar(r, str(concl.loc[cid, "evidencia"]), cid)
    tabla = umbrales(r)

    salida = pd.DataFrame(filas, columns=["control", "resultado", "detalle"])
    salida.to_csv(SAL_CSV, index=False, encoding="utf-8", lineterminator="\r\n")
    nf = int((salida["resultado"] == "FALLA").sum())
    with open(SAL_MD, "w", encoding="utf-8") as f:
        f.write("# Sens2 A1c - comprobacion independiente de las variables distinguibles (FDR)\n\n")
        f.write("q de Benjamini-Hochberg propios por bloque y respuesta sobre p6_nulo_perm.csv; "
                "distinguible = q < %.2f en al menos %d metodos; comillas = lista del texto de cada conclusion.\n\n"
                % (Q, UMBRAL))
        f.write("- controles: %d\n- OK: %d\n- FALLA: %d\n\n" % (len(salida), len(salida) - nf, nf))
        f.write("## Umbral de metodos (variables distinguibles, suma de los 4 bloques)\n\n")
        f.write("| conclusion | respuesta | 1 metodo | 2 metodos | 3 metodos |\n|---|---|---|---|---|\n")
        for cid, respuesta, u1, u2, u3 in tabla:
            f.write("| %s | %s | %d | %d | %d |\n" % (cid, respuesta, u1, u2, u3))
        f.write("\n## FALLA\n\n| control | detalle |\n|---|---|\n")
        for _, fila in salida[salida["resultado"] == "FALLA"].iterrows():
            f.write("| %s | %s |\n" % (fila["control"], fila["detalle"]))
    for _, fila in salida.iterrows():
        print("%-5s %s :: %s" % (fila["resultado"], fila["control"], fila["detalle"]))
    for cid, respuesta, u1, u2, u3 in tabla:
        print("%s %s -> 1: %d  2: %d  3: %d" % (cid, respuesta, u1, u2, u3))
    print("\ncontroles: %d  OK: %d  FALLA: %d" % (len(salida), len(salida) - nf, nf))
    return nf


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
