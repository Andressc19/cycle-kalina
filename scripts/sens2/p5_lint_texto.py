# -*- coding: utf-8 -*-
"""Sens2 - p5_lint_texto: busca palabras fuertes en las conclusiones y en los documentos.

Lee las columnas de texto de `p5_conclusiones.csv` (afirmacion, evidencia, implicacion y
alcance si existe), `docs/INFORME_SENS2.md` y `docs/VALIDACION_SENS2.md`, y escribe una fila
por aparicion de cada palabra fuerte (sin distinguir mayusculas, como palabra completa):
`archivo, id, campo, palabra, contexto` con 60 caracteres a cada lado. Salidas:
`p5_lint_texto.csv` (filas) y `p5_lint_texto.md` (conteo por palabra y por archivo y lista
agrupada por palabra). Es informativo: imprime el resumen y sale con codigo 0.
"""
import os
import re
import sys
from collections import Counter

import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
R = os.path.join(RAIZ, "resultados")
D = os.path.join(R, "2026-10-17_sens2_P5")
DOCS = os.path.join(RAIZ, "docs")
sys.path.insert(0, AQUI)
import p5_trazado as T  # noqa: E402

CONCL = "p5_conclusiones.csv"
NOMBRES = ("INFORME_SENS2.md", "VALIDACION_SENS2.md")
CAMPOS = ("afirmacion", "evidencia", "implicacion", "alcance")
PALABRAS = ("solo", "unico", "unica", "única", "único", "siempre", "nunca", "todos", "todas",
            "ninguno", "ninguna", "demuestra", "prueba que", "garantiza", "confirma",
            "definitivo", "claramente", "evidentemente", "se debe a", "causa")
LADO = 60
ASCII = str.maketrans("áéíóúüñÁÉÍÓÚÑ", "aeiouunAEIOUN")


def _patron(palabra):
    """Expresion regular de una palabra completa (admite varios espacios entre palabras)."""
    cuerpo = r"\s+".join(re.escape(p) for p in palabra.split())
    return re.compile(r"(?<!\w)" + cuerpo + r"(?!\w)", re.IGNORECASE | re.UNICODE)


PATRONES = [(p, _patron(p)) for p in PALABRAS]


def _contexto(texto, ini, fin):
    a, b = max(0, ini - LADO), min(len(texto), fin + LADO)
    return texto[a:b].replace("\r", " ").replace("\n", " ").replace("|", "/")


def _filas_texto(archivo, campo, ident, texto):
    out = []
    for palabra, pat in PATRONES:
        for m in pat.finditer(texto):
            out.append({"archivo": archivo, "id": ident, "campo": campo, "palabra": palabra,
                        "contexto": _contexto(texto, m.start(), m.end())})
    return out


def conclusiones():
    """Una fila por aparicion en las columnas de texto de p5_conclusiones.csv."""
    base = pd.read_csv(os.path.join(D, CONCL))
    campos = [c for c in CAMPOS if c in base.columns]
    filas = []
    for _, r in base.iterrows():
        for campo in campos:
            filas += _filas_texto(CONCL, campo, r["id"], str(r[campo]))
    return filas


def documentos():
    """Una fila por aparicion en los documentos; id = numero de linea, campo vacio."""
    filas = []
    for nombre in NOMBRES:
        ruta = os.path.join(DOCS, nombre)
        if not os.path.exists(ruta):
            continue
        with open(ruta, encoding="utf-8") as f:
            for i, linea in enumerate(f, start=1):
                filas += _filas_texto(nombre, "", i, linea.rstrip("\n"))
    return filas


def _informe(filas):
    pc = Counter(x["palabra"] for x in filas)
    pa = Counter(x["archivo"] for x in filas)
    orden = sorted([(p, pc[p]) for p in PALABRAS], key=lambda t: (-t[1], t[0]))
    md = ["# Sens2 P5 - palabras fuertes en los textos", "",
          "Apariciones de palabras fuertes (sin distinguir mayusculas, como palabra completa) en "
          "`%s`, `%s` y `%s`." % (CONCL, NOMBRES[0], NOMBRES[1]), "",
          "- total de apariciones: %d" % len(filas), "",
          "## Conteo por palabra", "", "| palabra | apariciones |", "|---|---:|"]
    md += ["| %s | %d |" % (p, n) for p, n in orden]
    md += ["", "## Conteo por archivo", "", "| archivo | apariciones |", "|---|---:|"]
    md += ["| %s | %d |" % (a, pa[a]) for a in sorted(pa, key=lambda a: -pa[a])]
    md += ["", "## Lista por palabra", ""]
    for palabra, _ in orden:
        grupo = [x for x in filas if x["palabra"] == palabra]
        md += ["### %s (%d)" % (palabra, len(grupo)), "",
               "| archivo | id | campo | contexto |", "|---|---|---|---|"]
        md += ["| %s | %s | %s | %s |" % (x["archivo"], x["id"], x["campo"], x["contexto"]) for x in grupo]
        md += [""]
    with open(os.path.join(D, "p5_lint_texto.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")


def main():
    filas = conclusiones() + documentos()
    cols = ["archivo", "id", "campo", "palabra", "contexto"]
    pd.DataFrame(filas, columns=cols).to_csv(os.path.join(D, "p5_lint_texto.csv"), index=False,
                                             encoding="utf-8", lineterminator="\r\n")
    _informe(filas)
    pc = Counter(x["palabra"] for x in filas)
    print("apariciones totales: %d" % len(filas))
    for a in (CONCL,) + NOMBRES:
        print("  %-22s %d" % (a, sum(1 for x in filas if x["archivo"] == a)))
    print("top por palabra:")
    for p, n in sorted(pc.items(), key=lambda t: (-t[1], t[0]))[:10]:
        print("  %-14s %d" % (p.translate(ASCII), n))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR: %s" % e)
    raise SystemExit(0)
