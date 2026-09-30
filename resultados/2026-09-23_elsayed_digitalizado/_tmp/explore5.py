# -*- coding: utf-8 -*-
"""Exploracion 5: regiones izquierda (eje y) e inferior (eje x) con umbral bajo."""
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

print('== filas 285..339: runs >= 25px ==')
for y in range(285, 339):
    rs = [(a0, b0) for (a0, b0) in runs(dark[y, :]) if b0 - a0 >= 25]
    if rs:
        print(y, rs)

print('\n== columnas 0..60: runs >= 25px ==')
for x in range(0, 61):
    rs = [(a0, b0) for (a0, b0) in runs(dark[:, x]) if b0 - a0 >= 25]
    if rs:
        print(x, rs)