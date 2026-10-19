# -*- coding: utf-8 -*-
"""Sens2 - s2_construir: ensambla `Kalina_anal_sensible_2.xlsx` con las hojas de la parte 1 y,
si existen, las de la parte 2 (`s2_f3.py` y `s2_f4.py`)."""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))

from openpyxl import Workbook  # noqa: E402
from x5_graficos import dibujar_todos  # noqa: E402
from s2_cargar import cargar_todo  # noqa: E402
from s2_leeme import hoja_leeme  # noqa: E402
from s2_conclusion import hoja_conclusion  # noqa: E402
from s2_f1 import hoja_f1_existencia, hoja_f1_reglas  # noqa: E402
from s2_f1c import hoja_f1_margenes  # noqa: E402
from s2_f2 import hoja_f2_comparacion, hoja_f2_distancia  # noqa: E402
from s2_datos import HOJAS_DATOS  # noqa: E402

SALIDA = os.path.join(RAIZ, "datos", "Kalina_anal_sensible_2.xlsx")

HOJAS = [hoja_conclusion, hoja_f1_existencia, hoja_f1_reglas, hoja_f1_margenes, hoja_f2_comparacion,
         hoja_f2_distancia]


def _opcionales():
    """Hojas de la parte 2, si sus modulos ya estan en disco."""
    hojas = []
    for mod, attr in (("s2_f3", "HOJAS_F3"), ("s2_fb", "HOJAS_FB"), ("s2_f4", "HOJAS_F4"), ("s2_f4t", "HOJAS_F4T"), ("s2_f4k", "HOJAS_F4K"),
                      ("s2_f5", "HOJAS_F5"), ("s2_f5u", "HOJAS_F5U"), ("s2_f6", "HOJAS_F6"), ("s2_f7", "HOJAS_F7"),
                      ("s2_f7c", "HOJAS_F7C"), ("s2_conf", "HOJAS_CONF")):
        try:
            hojas += list(getattr(__import__(mod), attr, []))
        except ImportError:
            pass
    return hojas


def construir():
    datos = cargar_todo()
    wb = Workbook()
    wb.remove(wb.active)
    hoja_leeme(wb, datos)
    for fn in HOJAS + _opcionales() + list(HOJAS_DATOS):
        fn(wb, datos)
    n = dibujar_todos(wb)
    nombres = wb.sheetnames
    if nombres[0] != "LEEME":
        idx = nombres.index("LEEME")
        nombres.insert(0, nombres.pop(idx))
        wb._sheets = [wb[s] for s in nombres]
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    wb.save(SALIDA)
    print("OK: guardado", SALIDA, "- graficos dibujados:", n)


if __name__ == "__main__":
    construir()
