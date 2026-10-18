# -*- coding: utf-8 -*-
"""Sens2 - p5_generar: genera `p5_conclusiones.csv` desde `p5_conclusiones_base.csv`.

El archivo base contiene el texto de cada conclusion con marcadores `{{clave}}`, `{{clave|formato}}` o
`{{abs:clave|formato}}`; las claves salen de `p5_hechos.hechos()` (CSV y datos de Sensibilidad 1). Tras rellenar,
aplica la regla de confianza (`p5_confianza.py`) cuando existe `p5_confianza.csv`. Falla si queda un marcador sin
resolver o una clave desconocida. El resto de los documentos leen `p5_conclusiones.csv`, nunca el base.
"""
import csv
import os
import re
import sys

import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
from p5_hechos import hechos  # noqa: E402

D = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P5")
MARCA = re.compile(r"\{\{([^{}]+)\}\}")


def _formato(valor, fmt):
    if fmt == "mil":
        return "{:,.0f}".format(valor).replace(",", " ")
    if fmt:
        return format(valor, fmt)
    return str(valor)


def rellenar(texto, h, desconocidas):
    def sub(m):
        clave, _, fmt = m.group(1).partition("|")
        absoluto = clave.startswith("abs:")
        clave = clave[4:] if absoluto else clave
        if clave not in h:
            desconocidas.append(clave)
            return m.group(0)
        v = h[clave]
        return _formato(abs(v) if absoluto and not isinstance(v, str) else v, fmt)
    return MARCA.sub(sub, texto)


def generar():
    base = pd.read_csv(os.path.join(D, "p5_conclusiones_base.csv"))
    h = hechos()
    desconocidas = []
    for col in ("afirmacion", "evidencia", "implicacion"):
        base[col] = [rellenar(str(t), h, desconocidas) for t in base[col]]
    if desconocidas:
        raise SystemExit("claves desconocidas en las plantillas: %s" % sorted(set(desconocidas)))
    restos = [(r.id, c) for r in base.itertuples() for c in ("afirmacion", "evidencia", "implicacion") if "{{" in str(getattr(r, c))]
    if restos:
        raise SystemExit("marcadores sin resolver: %s" % restos)
    try:
        from p5_confianza import asignar
        base = asignar(base, h)
    except ImportError:
        pass
    base.to_csv(os.path.join(D, "p5_conclusiones.csv"), index=False, quoting=csv.QUOTE_ALL, encoding="utf-8", lineterminator="\r\n")
    return base


if __name__ == "__main__":
    b = generar()
    print("OK: %d conclusiones generadas en %s" % (len(b), os.path.join(D, "p5_conclusiones.csv")))
