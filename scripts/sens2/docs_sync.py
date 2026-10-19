# -*- coding: utf-8 -*-
"""Sens2 - docs_sync: mantiene al dia las cifras globales marcadas en los documentos escritos a mano.

Una cifra marcada se escribe `<!--g:clave-->valor<!--/g-->` (claves de `p5_globales.py`). Sin argumentos reescribe el valor; con `--check` no escribe y
sale con codigo 1 si alguna cifra esta desactualizada o si una clave no existe. Documentos: VALIDACION_SENS2.md y PLAN_SENS2_MEJORA.md.
"""
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
import p5_globales as G  # noqa: E402

DOCS = [os.path.join(RAIZ, "docs", "VALIDACION_SENS2.md"), os.path.join(RAIZ, "docs", "PLAN_SENS2_MEJORA.md")]
PATRON = re.compile(r"<!--g:([a-z0-9_]+)-->(.*?)<!--/g-->")


def revisar(escribir):
    g = G.globales()
    malas, total = [], 0
    for ruta in DOCS:
        with open(ruta, encoding="utf-8", newline="") as fh:
            s = fh.read()

        def cambia(m):
            nonlocal total
            total += 1
            clave = m.group(1)
            if clave not in g:
                malas.append("%s: clave desconocida %s" % (os.path.basename(ruta), clave))
                return m.group(0)
            nuevo = G.valor_texto(clave, g[clave][0])
            if m.group(2) != nuevo:
                malas.append("%s: %s dice %s y el valor actual es %s" % (os.path.basename(ruta), clave, m.group(2), nuevo))
            return "<!--g:%s-->%s<!--/g-->" % (clave, nuevo)

        t = PATRON.sub(cambia, s)
        if escribir and t != s:
            with open(ruta, "w", encoding="utf-8", newline="") as fh:
                fh.write(t)
    return malas, total


def main(argv):
    check = "--check" in argv
    malas, total = revisar(escribir=not check)
    for m in malas:
        print(("DESACTUALIZADA: " if check else "actualizada: ") + m)
    print("docs_sync: %d cifras marcadas, %d %s" % (total, len(malas), "desactualizadas" if check else "actualizadas"))
    return 1 if (check and malas) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
