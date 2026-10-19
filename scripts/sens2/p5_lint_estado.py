# -*- coding: utf-8 -*-
"""Sens2 - p5_lint_estado: frases de estado caducas en documentos y conclusiones.

Lee `docs/INFORME_SENS2.md`, `docs/VALIDACION_SENS2.md`, `docs/PLAN_SENS2_MEJORA.md` y las
columnas de texto (`afirmacion`, `evidencia`, `implicacion`) de `p5_conclusiones.csv`. En el
plan se ignora la seccion historica entre los encabezados `## 6.` y `## 7.`. Busca, sin
distinguir mayusculas, las frases de estado pedidas y escribe una fila por aparicion:
`archivo, linea, id, campo, frase, contexto, tema, resultado_existente`, con `tema` tomado de
la primera palabra clave del contexto y `resultado_existente = si` cuando el CSV del tema ya
existe. Salidas: `p5_lint_estado.csv` y `p5_lint_estado.md`. Es informativo: sale con 0.
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
F1 = os.path.join(R, "2026-10-18_sens2_F1")
DOCS = os.path.join(RAIZ, "docs")
sys.path.insert(0, AQUI)

CONCL = "p5_conclusiones.csv"
PLAN = "PLAN_SENS2_MEJORA.md"
NOMBRES = ("INFORME_SENS2.md", "VALIDACION_SENS2.md", PLAN)
CAMPOS = ("afirmacion", "evidencia", "implicacion")
FRASES = ("queda pendiente", "quedan pendientes", "siguen abiertos", "sigue abierto",
          "pendiente de", "no se corrió", "no se corrio", "sin hacer", "por hacer",
          "etapa C", "requiere el motor", "requieren el motor", "necesita el motor",
          "falta el motor", "aún no", "todavía no", "sin commit",
          "con el motor)", "hasta reintentar", "falta la evaluación", "faltan flujo", "reintentar con el modo", "calcular el ciclo frente",
          "refinar p_baja", "se obtendrían", "se obtendria", "no hay optimizador", "sin optimizador", "un optimizador")
TEMAS = ("reintent", "piso", "densidad", "caudal", "bomba", "simétric", "simetric",
         "T_fuente", "optimiz", "NO_CONVERGIO")
CSV_TEMA = {"reintent": "p6_reintento_nc.csv", "NO_CONVERGIO": "p6_reintento_nc.csv",
            "piso": "p6_pisos25.csv", "densidad": "p6_dens.csv", "caudal": "p6_dens.csv",
            "bomba": "p6_dens.csv", "simétric": "p6_sim.csv", "simetric": "p6_sim.csv",
            "T_fuente": "p6_opt_T.csv", "optimiz": "p6_opt_T.csv"}
COLS = ("archivo", "linea", "id", "campo", "frase", "contexto", "tema", "resultado_existente")
LADO = 80


def _patron(frase):
    """Expresion regular de la frase completa (varios espacios admitidos, sin mayusculas)."""
    cuerpo = r"\s+".join(re.escape(p) for p in frase.split())
    return re.compile(r"(?<!\w)" + cuerpo + r"(?!\w)", re.IGNORECASE | re.UNICODE)


PATRONES = [(f, _patron(f)) for f in FRASES]


def _contexto(texto, ini, fin):
    a, b = max(0, ini - LADO), min(len(texto), fin + LADO)
    return texto[a:b].replace("\r", " ").replace("\n", " ").replace("|", "/")


def _ascii(texto):
    return texto.encode("ascii", "replace").decode("ascii")


def _tema(ctx):
    """Primera palabra clave (en el orden de TEMAS) que aparece en el contexto."""
    bajo = ctx.lower()
    for t in TEMAS:
        if t.lower() in bajo:
            return t
    return ""


def _resultado(tema):
    if not tema:
        return "-"
    ruta = os.path.join(F1, CSV_TEMA[tema])
    return "si" if os.path.exists(ruta) else "no"


def _filas(archivo, linea, ident, campo, texto):
    out = []
    for frase, pat in PATRONES:
        for m in pat.finditer(texto):
            ctx = _contexto(texto, m.start(), m.end())
            tema = _tema(ctx)
            out.append({"archivo": archivo, "linea": linea, "id": ident, "campo": campo,
                        "frase": frase, "contexto": ctx, "tema": tema,
                        "resultado_existente": _resultado(tema)})
    return out


def documentos():
    """Apariciones en los tres documentos; en el plan se salta de `## 6.` a `## 7.`."""
    filas = []
    for nombre in NOMBRES:
        ruta = os.path.join(DOCS, nombre)
        if not os.path.exists(ruta):
            continue
        saltar = False
        with open(ruta, encoding="utf-8") as f:
            for i, linea in enumerate(f, start=1):
                txt = linea.rstrip("\n")
                if nombre == PLAN:
                    if txt.startswith("## 6."):
                        saltar = True
                    elif txt.startswith("## 7."):
                        saltar = False
                    if saltar:
                        continue
                filas += _filas(nombre, i, "", "", txt)
    return filas


def conclusiones():
    """Apariciones en las columnas de texto de p5_conclusiones.csv (id + campo)."""
    base = pd.read_csv(os.path.join(D, CONCL))
    filas = []
    for _, r in base.iterrows():
        for campo in CAMPOS:
            if campo in base.columns:
                filas += _filas(CONCL, "", str(r["id"]), campo, str(r[campo]))
    return filas


def _informe(filas):
    pf = Counter(x["frase"] for x in filas)
    pa = Counter(x["archivo"] for x in filas)
    sospechosas = [x for x in filas if x["resultado_existente"] == "si"]
    md = ["# Sens2 P5 - frases de estado caducas", "",
          "Apariciones (sin distinguir mayusculas) de las frases de estado pedidas en "
          "`%s`, `%s`, `%s` y en las columnas de texto de `%s`. En el plan se omite la seccion "
          "entre `## 6.` y `## 7.`. Una aparicion con `resultado_existente = si` es sospechosa "
          "de estar caduca." % (NOMBRES[0], NOMBRES[1], NOMBRES[2], CONCL), "",
          "- total de apariciones: %d" % len(filas),
          "- sospechosas (resultado_existente = si): %d" % len(sospechosas), "",
          "## Conteo por frase", "", "| frase | apariciones |", "|---|---:|"]
    md += ["| %s | %d |" % (f, pf.get(f, 0)) for f in FRASES]
    md += ["", "## Conteo por archivo", "", "| archivo | apariciones |", "|---|---:|"]
    md += ["| %s | %d |" % (a, pa.get(a, 0)) for a in (CONCL,) + NOMBRES]
    md += ["", "## Sospechosas de estar caducas", "",
           "| archivo | linea/id | campo | frase | tema | contexto |",
           "|---|---|---|---|---|---|"]
    for x in sospechosas:
        ref = x["linea"] if x["linea"] != "" else x["id"]
        md.append("| %s | %s | %s | %s | %s | %s |" % (x["archivo"], ref, x["campo"],
                                                       x["frase"], x["tema"], x["contexto"]))
    with open(os.path.join(D, "p5_lint_estado.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")


def main():
    filas = documentos() + conclusiones()
    pd.DataFrame(filas, columns=list(COLS)).to_csv(
        os.path.join(D, "p5_lint_estado.csv"), index=False, encoding="utf-8",
        lineterminator="\r\n")
    _informe(filas)
    pf = Counter(x["frase"] for x in filas)
    pa = Counter(x["archivo"] for x in filas)
    print("apariciones totales: %d" % len(filas))
    print("por archivo:")
    for a in (CONCL,) + NOMBRES:
        print("  %-22s %d" % (a, pa.get(a, 0)))
    print("por frase (todas las frases buscadas):")
    for f in FRASES:
        print("  %-22s %d" % (_ascii(f), pf.get(f, 0)))
    sosp = [x for x in filas if x["resultado_existente"] == "si"]
    print("sospechosas (resultado_existente = si): %d" % len(sosp))
    for x in sosp:
        ref = x["linea"] if x["linea"] != "" else "%s:%s" % (x["id"], x["campo"])
        frase = _ascii(x["frase"])
        tema = _ascii(x["tema"])
        ctx = _ascii(x["contexto"])
        print("  %s | %s | %s | %s | %s" % (x["archivo"], ref, frase, tema, ctx))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR: %s" % _ascii(str(e)))
    raise SystemExit(0)
