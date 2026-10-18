# -*- coding: utf-8 -*-
"""Sens2 A5 - pruebas de cifras y conclusiones (solo lectura).

Comprueba que `p5_conclusiones.csv` no deja marcadores, que la confianza toma solo los tres valores
de la regla, que los ids son unicos y coinciden con `p5_evidencia.csv`, que cuatro cifras clave de
`p5_hechos.hechos()` valen lo esperado y que `p5_generar.rellenar` reproduce exactamente los textos.
"""
import os
import sys

import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens2"))
from p5_generar import rellenar  # noqa: E402
from p5_hechos import hechos  # noqa: E402

P5 = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P5")
CONCLUSIONES = os.path.join(P5, "p5_conclusiones.csv")
BASE = os.path.join(P5, "p5_conclusiones_base.csv")
EVIDENCIA = os.path.join(P5, "p5_evidencia.csv")
TEXTOS = ("afirmacion", "evidencia", "implicacion")
CLAVE = {"u1p.C1.p_kalina": (0.469, 0.001), "mo2.todos.p3": (7.0, 0.1),
         "l8.n": (213.0, 0.0), "r2.agr.evaluaciones_ventanas_una_vez": (665.0, 0.0)}


def test_sin_marcadores():
    c = pd.read_csv(CONCLUSIONES)
    for col in TEXTOS:
        assert not c[col].astype(str).str.contains(r"\{\{", regex=True).any(), col


def test_confianza_valores():
    c = pd.read_csv(CONCLUSIONES)
    assert set(c["confianza"].dropna()) <= {"Alta", "Media", "Baja", "No aplica"}


def test_ids_unicos_y_evidencia():
    c = pd.read_csv(CONCLUSIONES)
    e = pd.read_csv(EVIDENCIA)
    assert c["id"].is_unique
    assert set(c["id"].astype(str)) == set(e["id"].astype(str))


def test_cifras_clave():
    h = hechos()
    for clave, (esperado, tol) in CLAVE.items():
        assert clave in h, clave
        assert abs(float(h[clave]) - esperado) <= tol, (clave, h[clave])


def test_rellenar_reproduce():
    base = pd.read_csv(BASE)
    c = pd.read_csv(CONCLUSIONES)
    h = hechos()
    faltan = []
    for col in TEXTOS:
        assert [rellenar(str(t), h, faltan) for t in base[col]] == list(c[col].astype(str)), col
    assert not faltan
