# -*- coding: utf-8 -*-
"""Exploracion 4: buscar linea inferior del plot y eje y exacto."""
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

print('== filas 270..300: todos los runs >= 40px ==')
for y in range(270, 301):
    rs = [(a0, b0) for (a0, b0) in runs(dark[y, :]) if b0 - a0 >= 40]
    if rs:
        print(y, rs)

print('\n== columnas 0..25: todos los runs >= 30px ==')
for x in range(0, 26):
    rs = [(a0, b0) for (a0, b0) in runs(dark[:, x]) if b0 - a0 >= 30]
    if rs:
        print(x, rs)

print('\n== fila 8 (top box): posiciones de transiciones oscuras ==')
seg = list(runs(dark[8, :]))
print(seg[:5], '...', seg[-5:], 'n=', len(seg))