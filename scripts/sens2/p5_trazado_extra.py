# -*- coding: utf-8 -*-
"""Sens2 - p5_trazado_extra: poder del trazado y cobertura de marcadores.

Dos comprobaciones que amplian p5_trazado.py:
- poder(): control negativo. Genera n numeros inventados con dos decimales (uniforme en [0.01, 99.99],
  semilla fija) y mide que porcentaje saldria "trazado" con la misma referencia y la misma regla de
  p5_trazado.py. Reutiliza clasificar() y referencia() de ese modulo; no reescribe la logica.
- cobertura_marcadores(): en p5_conclusiones_base.csv cuenta, por conclusion, cuantos numeros van
  dentro de marcadores {{...}} y cuantos fuera.
anexo() es un orquestador minimo que llama a las dos y anade el resultado a p5_trazado.md.
"""
import os
import re
import sys

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
if AQUI not in sys.path:
    sys.path.insert(0, AQUI)

MARCA = re.compile(r"\{\{.*?\}\}")


def poder(trazado_fn_o_conjunto=None, semilla=20261018, n=300, permitidos=None):
    """Porcentaje de numeros inventados (2 decimales, [0.01, 99.99]) que saldrian trazados.

    El primer argumento puede ser una funcion marcar(dec, valor) -> estado o el conjunto de referencia
    de p5_trazado.referencia(); si es None se calcula el de p5_trazado. La regla es la de p5_trazado.
    """
    import p5_trazado as T
    if callable(trazado_fn_o_conjunto):
        marcar = trazado_fn_o_conjunto
    else:
        ref = T.referencia() if trazado_fn_o_conjunto is None else trazado_fn_o_conjunto
        perm = T.permitidos() if permitidos is None else permitidos
        marcar = lambda dec, val: T.clasificar(dec, val, ref, perm)[0]     # noqa: E731
    rng = np.random.default_rng(semilla)
    valores = np.round(rng.uniform(0.01, 99.99, n), 2)
    estados = [marcar(2, float(v)) for v in valores]
    return 100.0 * sum(e == "si" for e in estados) / float(len(estados))


def cobertura_marcadores():
    """Tabla (id, dentro, fuera): marcadores {{...}} y numeros sueltos por conclusion."""
    import p5_trazado as T
    base = pd.read_csv(os.path.join(T.D, "p5_conclusiones_base.csv"))
    filas = []
    for r in base.itertuples():
        dentro, fuera = 0, 0
        for campo in T.CAMPOS:
            texto = str(getattr(r, campo))
            tramos = [(m.start(), m.end()) for m in MARCA.finditer(texto)]
            dentro += len(tramos)
            for m in T.PATRON.finditer(texto):
                if not any(a <= m.start() < b for a, b in tramos):
                    fuera += 1
        filas.append((r.id, dentro, fuera))
    return pd.DataFrame(filas, columns=["id", "dentro", "fuera"])


def anexo(trazado_ref, trazado_perm, ruta_md=None):
    """Calcula poder y cobertura y los anade al final de p5_trazado.md."""
    import p5_trazado as T
    ruta = ruta_md or os.path.join(T.D, "p5_trazado.md")
    pct = poder(trazado_ref, permitidos=trazado_perm)
    cob = cobertura_marcadores()
    dentro, fuera = int(cob["dentro"].sum()), int(cob["fuera"].sum())
    with open(ruta, "a", encoding="utf-8") as f:
        f.write("\n## Poder del control negativo\n\n")
        f.write("una cifra inventada con dos decimales se habría trazado en el %.1f %% de los casos.\n\n" % pct)
        f.write("## Cobertura de marcadores\n\n")
        f.write("- numeros dentro de marcadores: %d\n" % dentro)
        f.write("- numeros fuera de marcadores: %d\n\n" % fuera)
        f.write("### 10 conclusiones con mas numeros fuera de marcadores\n\n")
        f.write("| id | dentro | fuera |\n|---|---|---|\n")
        for r in cob.sort_values(["fuera", "id"], ascending=[False, True]).head(10).itertuples():
            f.write("| %s | %d | %d |\n" % (r.id, r.dentro, r.fuera))
    print("poder (cifra inventada trazada): %.1f %%" % pct)
    print("numeros dentro de marcadores: %d" % dentro)
    print("numeros fuera de marcadores: %d" % fuera)
    return pct, cob
