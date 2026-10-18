# -*- coding: utf-8 -*-
"""Sens2 A5 - pruebas del contraste R1 (solo lectura).

Comprueba que la cascada de filtros no crece en `n_unicos`, que ningun punto del libro viejo de
`r1_puntos.csv` comparte clave de 10 variables con `dataset_dedup()` y que la distancia al centro
es no negativa y coherente con la marca `cerca`.
"""
import os
import sys

import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens2"))
from r1_filtro import CERCANO, clave10  # noqa: E402
from s2_cargar import dataset_dedup  # noqa: E402

R1 = os.path.join(RAIZ, "resultados", "2026-10-18_sens2_R1")


def test_cascada_monotona():
    c = pd.read_csv(os.path.join(R1, "r1_cascada.csv"))
    n = c["n_unicos"].to_numpy(float)
    assert (n[1:] <= n[:-1]).all(), "n_unicos no es monotona no creciente"


def test_puntos_fuera_de_dataset_dedup():
    p = pd.read_csv(os.path.join(R1, "r1_puntos.csv"))
    assert set(clave10(p)).isdisjoint(set(clave10(dataset_dedup())))


def test_distancia_y_cerca():
    p = pd.read_csv(os.path.join(R1, "r1_puntos.csv"))
    assert (p["dist"] >= 0).all()
    assert (p["cerca"].astype(bool) == (p["dist"] <= CERCANO)).all()
