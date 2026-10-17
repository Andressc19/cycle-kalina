# -*- coding: utf-8 -*-
"""Sens2 - s2_cargar: lee en DataFrames los CSV de P1-P4 y `p5_conclusiones.csv`.

Una funcion por fuente; ninguna cifra del libro se escribe a mano. Todo sale de aqui.
"""
import os

import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P1 = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P1")
P2 = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P2")
P3 = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P3")
P4 = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P4")
P5 = os.path.join(RAIZ, "resultados", "2026-10-17_sens2_P5")


def _csv(directorio, nombre):
    return pd.read_csv(os.path.join(directorio, nombre))


def conclusiones():
    return _csv(P5, "p5_conclusiones.csv")


def dataset():
    return _csv(P1, "p1_dataset.csv")


def existencia_rangos():
    return _csv(P1, "p1_existencia_rangos.csv")


def existencia_prob():
    return _csv(P1, "p1_existencia_prob.csv")


def fronteras():
    return _csv(P1, "p1_fronteras.csv")


def reglas():
    return _csv(P1, "p1_reglas.csv")


def zonas_grises():
    return _csv(P1, "p1_zonas_grises.csv")


def comparacion():
    return _csv(P2, "p2_comparacion.csv")


def distancia_resumen():
    return _csv(P2, "p2_distancia_resumen.csv")


def violaciones():
    return _csv(P2, "p2_violaciones.csv")


def robustez():
    return _csv(P2, "p2_robustez.csv")


def dataset_dedup():
    return _csv(P2, "p2_dataset_dedup.csv")


def distancia():
    return _csv(P2, "p2_distancia.csv")


def cargar_todo():
    """Todos los CSV de esta parte en un diccionario con una clave por fuente."""
    return {
        "conclusiones": conclusiones(),
        "dataset": dataset(),
        "existencia_rangos": existencia_rangos(),
        "existencia_prob": existencia_prob(),
        "fronteras": fronteras(),
        "reglas": reglas(),
        "zonas_grises": zonas_grises(),
        "comparacion": comparacion(),
        "distancia_resumen": distancia_resumen(),
        "violaciones": violaciones(),
        "robustez": robustez(),
        "dataset_dedup": dataset_dedup(),
        "distancia": distancia(),
    }


__all__ = ["conclusiones", "dataset", "existencia_rangos", "existencia_prob", "fronteras",
           "reglas", "zonas_grises", "comparacion", "distancia_resumen", "violaciones",
           "robustez", "dataset_dedup", "distancia", "cargar_todo", "P1", "P2", "P3", "P4", "P5"]
