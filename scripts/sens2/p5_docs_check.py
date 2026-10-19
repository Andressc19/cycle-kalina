# -*- coding: utf-8 -*-
"""Sens2 - p5_docs_check: cifras de los documentos frente a los CSV.

Extrae de `docs/INFORME_SENS2.md` y `docs/VALIDACION_SENS2.md` todos los numeros con
decimales o con `%` y los compara con (a) todo el texto de `p5_conclusiones.csv`, (b) los CSV
de `resultados/2026-10-17_sens2_P*` y `resultados/2026-10-18_sens2_*` y (c)
`p5_trazado_permitidos.csv`, reutilizando las funciones de `p5_trazado` (`extraer`,
`clasificar`, `permitidos`, `_agregar`). Salidas: `p5_docs_check.csv` (archivo, linea, numero,
estado, contexto) y `p5_docs_check.md` (conteo por estado y lista de los no_trazado). Imprime
siempre el resumen completo y sale con codigo 1 si queda alguna cifra no_trazado.
"""
import glob
import os
import re
import sys
from collections import Counter

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
R = os.path.join(RAIZ, "resultados")
D = os.path.join(R, "2026-10-17_sens2_P5")
DOCS = os.path.join(RAIZ, "docs")
sys.path.insert(0, AQUI)
import p5_trazado as T  # noqa: E402

NOMBRES = ("INFORME_SENS2.md", "VALIDACION_SENS2.md")
CARPETAS = ("2026-10-17_sens2_P*", "2026-10-18_sens2_*")
EXCLUIR = ("p5_docs_check.csv", "p5_lint_texto.csv")
COLS = ("archivo", "linea", "numero", "estado", "contexto")
ESTADOS = ("en_conclusiones", "en_csv", "permitido", "trivial", "no_trazado")
PCT = re.compile(r"\s*%")


def numeros(texto, campo):
    """Numeros de `texto` con decimales o seguidos de `%` (valor, decimales, inicio, fin)."""
    out = []
    for num, dec, valor, _, ini, fin in T.extraer(texto, campo):
        if dec > 0 or PCT.match(texto[fin:]):
            out.append((num, dec, valor, ini, fin))
    return out


def ref_conclusiones():
    """Referencia {d: {valor: fuente}} con todos los numeros del texto de p5_conclusiones.csv."""
    ref = {d: {} for d in range(5)}
    base = pd.read_csv(os.path.join(D, "p5_conclusiones.csv"))
    vals = []
    for col in base.columns:
        for v in base[col].astype(str):
            vals += [t[2] for t in T.extraer(v, col)]
    T._agregar(ref, np.array(vals, dtype=float), "p5_conclusiones.csv")
    return ref


def ref_csv():
    """Referencia {d: {valor: fuente}} con las columnas numericas de los CSV de resultados."""
    ref = {d: {} for d in range(5)}
    bases = []
    for pat in CARPETAS:
        bases += [x for x in glob.glob(os.path.join(R, pat)) if os.path.isdir(x)]
    for base in sorted(set(bases)):
        for dp, _, fs in os.walk(base):
            for fn in sorted(fs):
                if not fn.endswith(".csv") or fn in EXCLUIR:
                    continue
                ruta = os.path.join(dp, fn)
                try:
                    df = pd.read_csv(ruta)
                except Exception:
                    continue
                rel = os.path.relpath(ruta, R).replace("\\", "/")
                for col in df.columns:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        T._agregar(ref, df[col].to_numpy(dtype=float), "%s:%s" % (rel, col))
    return ref


def clasificar(dec, valor, refc, refb, perm):
    """Estado de un numero: en_conclusiones, en_csv, permitido, trivial o no_trazado."""
    d = min(dec, 4)
    clave = round(valor, d)
    if clave in refc[d]:
        return "en_conclusiones"
    if clave in refb[d]:
        return "en_csv"
    if clave in perm:
        return "permitido"
    if dec == 0 and valor == int(valor) and abs(valor) < 10:
        return "trivial"
    return "no_trazado"


def _informe(filas, conteo):
    sin = [x for x in filas if x["estado"] == "no_trazado"]
    md = ["# Sens2 P5 - cifras de los documentos frente a los CSV", "",
          "Numeros con decimales o con `%%` de `%s` y `%s` buscados en todo el texto de `p5_conclusiones.csv`, "
          "en los CSV de `resultados/2026-10-17_sens2_P*` y `resultados/2026-10-18_sens2_*` y en "
          "`p5_trazado_permitidos.csv`." % (NOMBRES[0], NOMBRES[1]), "",
          "- total de numeros: %d" % len(filas)]
    md += ["- %s: %d" % (e, conteo.get(e, 0)) for e in ESTADOS]
    md += ["", "## Lista de no_trazado", "", "| archivo | linea | numero | contexto |", "|---|---:|---|---|"]
    md += ["| %s | %s | %s | %s |" % (x["archivo"], x["linea"], x["numero"], x["contexto"]) for x in sin]
    with open(os.path.join(D, "p5_docs_check.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")


def main():
    refc, refb, perm = ref_conclusiones(), ref_csv(), T.permitidos()
    filas = []
    for nombre in NOMBRES:
        ruta = os.path.join(DOCS, nombre)
        if not os.path.exists(ruta):
            continue
        with open(ruta, encoding="utf-8") as f:
            for i, linea in enumerate(f, start=1):
                txt = linea.rstrip("\n")
                for num, dec, valor, ini, fin in numeros(txt, nombre):
                    filas.append({"archivo": nombre, "linea": i, "numero": num,
                                  "estado": clasificar(dec, valor, refc, refb, perm),
                                  "contexto": T._contexto(txt, ini, fin)})
    pd.DataFrame(filas, columns=list(COLS)).to_csv(os.path.join(D, "p5_docs_check.csv"), index=False,
                                                   encoding="utf-8", lineterminator="\r\n")
    conteo = Counter(x["estado"] for x in filas)
    _informe(filas, conteo)
    sin = [x for x in filas if x["estado"] == "no_trazado"]
    print("numeros totales: %d" % len(filas))
    for e in ESTADOS:
        print("  %-15s %d" % (e, conteo.get(e, 0)))
    print("no_trazado: %d" % len(sin))
    for x in sin:
        print("  %s:%s  %s" % (x["archivo"], x["linea"], x["numero"]))
    return len(sin)


if __name__ == "__main__":
    try:
        n = main()
    except Exception as e:
        print("ERROR: %s" % e)
        raise SystemExit(1)
    raise SystemExit(1 if n else 0)
