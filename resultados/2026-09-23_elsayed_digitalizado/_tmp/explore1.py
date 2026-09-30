# -*- coding: utf-8 -*-
"""Exploracion 1: estructura general de fig4_eta_vs_P.png (ejes, ticks, leyenda)."""
import os
import numpy as np
from PIL import Image

REF = r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013\fig4_eta_vs_P.png'
a = np.asarray(Image.open(REF).convert('L'))
H, W = a.shape
print('size', W, H, 'dtype', a.dtype, 'min/max', a.min(), a.max())

dark = a < 128
# Perfil de filas y columnas: cuantas columnas oscuras hay por fila / filas oscuras por columna
rowdark = dark.sum(axis=1)
coldark = dark.sum(axis=0)
print('\n== filas con mas de 15 px oscuros (posibles lineas horizontales) ==')
for y in range(H):
    if rowdark[y] > 15:
        print(y, rowdark[y])
print('\n== columnas con mas de 15 px oscuros (posibles lineas verticales) ==')
for x in range(W):
    if coldark[x] > 15:
        print(x, coldark[x])