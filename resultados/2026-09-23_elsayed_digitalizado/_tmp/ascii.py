# -*- coding: utf-8 -*-
"""Dump ASCII de regiones de las figuras para inspeccion visual via texto."""
import os
import numpy as np
from PIL import Image

REF = r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013'

def load(name):
    return np.asarray(Image.open(os.path.join(REF, name)).convert('L'))

def ascii_block(g, x0, x1, y0, y1, bx=4, by=6, th_d=110, th_m=185):
    """cada bloque bx x by px -> char. '#'=oscuro, '+'=medio, '.'=claro"""
    for y in range(y0, min(y1, g.shape[0]), by):
        row = []
        for x in range(x0, min(x1, g.shape[1]), bx):
            b = g[y:y + by, x:x + bx]
            m = b.mean()
            if m < th_d:
                row.append('#')
            elif m < th_m:
                row.append('+')
            else:
                row.append('.')
        print('%4d %s' % (y, ''.join(row)))

g2 = load('fig2_eta_vs_xb.png')
g4 = load('fig4_eta_vs_P.png')

print('############ FIG2 global ############')
ascii_block(g2, 0, 1029, 0, 680, bx=12, by=14)