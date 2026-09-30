# -*- coding: utf-8 -*-
"""Exploracion 3: region inferior (eje x) y region izquierda (eje y)."""
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

print('== filas 300..338: runs oscuros largos (>=80px) ==')
for y in range(300, 339):
    rs = [(a0, b0) for (a0, b0) in runs(dark[y, :]) if b0 - a0 >= 80]
    if rs:
        print(y, rs)

print('\n== columnas 0..30 y 500..524: runs verticales largos (>=150px) ==')
for x in list(range(0, 32)) + list(range(495, W)):
    rs = [(a0, b0) for (a0, b0) in runs(dark[:, x]) if b0 - a0 >= 150]
    if rs:
        print(x, rs)