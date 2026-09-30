# -*- coding: utf-8 -*-
"""Exploracion 7: ticks eje x (segmentos verticales cortos cerca de la base) y eje y."""
import os
import numpy as np
from PIL import Image

REF = r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013\fig4_eta_vs_P.png'
a = np.asarray(Image.open(REF).convert('L'))
H, W = a.shape
dark = a < 128

def runs(v, gap=2, minh=2):
    out, s, last = [], None, None
    for i, val in enumerate(v):
        if val:
            if s is None:
                s = i
            last = i
        elif s is not None and i - last > gap:
            if last - s + 1 >= minh:
                out.append((s, last))
            s = last = None
    if s is not None and last - s + 1 >= minh:
        out.append((s, last))
    return out

# Buscar en filas 250..300 segmentos verticales: por cada columna, runs de 3..12 px
print('== posibles ticks x: columnas con run vertical de 3..12px en filas 245..300 ==')
for x in range(30, W - 10):
    rs = [(a0, b0) for (a0, b0) in runs(dark[:, x]) if a0 >= 245 and b0 <= 302 and (b0 - a0) in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)]
    for (a0, b0) in rs:
        print(x, 'y=%d..%d h=%d' % (a0, b0, b0 - a0 + 1))