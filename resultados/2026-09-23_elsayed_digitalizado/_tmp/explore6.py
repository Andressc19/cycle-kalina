# -*- coding: utf-8 -*-
"""Exploracion 6: mapa ASCII coarse de la figura."""
import os
import numpy as np
from PIL import Image

REF = r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013\fig4_eta_vs_P.png'
a = np.asarray(Image.open(REF).convert('L'))
H, W = a.shape
dark = a < 150

# mapa coarse: celdas de 6x6 px, densidad oscura
ch, cw = 6, 6
s = ''
for y0 in range(0, H, ch):
    line = ''
    for x0 in range(0, W, cw):
        blk = dark[y0:y0 + ch, x0:x0 + cw]
        f = blk.mean()
        line += '#' if f > 0.5 else ('+' if f > 0.15 else ('.' if f > 0.02 else ' '))
    s += line + '\n'
print(s)
print('leyenda: # dense, + medio, . escaso, espacio limpio')