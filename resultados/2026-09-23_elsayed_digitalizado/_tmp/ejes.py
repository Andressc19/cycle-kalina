# -*- coding: utf-8 -*-
"""Localizacion fina de ejes, ticks y cajas en ambas figuras."""
import os
import numpy as np
from PIL import Image
from scipy import ndimage

REF = r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013'

def load(name):
    a = np.asarray(Image.open(os.path.join(REF, name)).convert('L'))
    return a

def long_runs(g):
    """para cada fila, longitud del run oscuro mas largo continuo (g<140)"""
    dark = g < 140
    n = dark.shape[1]
    # runs por fila vectorizados
    rows = []
    for y in range(dark.shape[0]):
        d = dark[y]
        # mayor run
        best = cur = 0
        for v in d:
            if v:
                cur += 1
                if cur > best:
                    best = cur
            else:
                cur = 0
        rows.append(best)
    return np.array(rows)

def long_vruns(g):
    dark = g < 140
    cols = []
    for x in range(dark.shape[1]):
        best = cur = 0
        for v in dark[:, x]:
            if v:
                cur += 1
                if cur > best:
                    best = cur
            else:
                cur = 0
        cols.append(best)
    return np.array(cols)

g2 = load('fig2_eta_vs_xb.png')
g4 = load('fig4_eta_vs_P.png')

print('--- FIG2: filas con run oscuro largo (>=40 px) ---')
h2 = long_runs(g2)
for y in np.where(h2 >= 40)[0]:
    print('  y=%3d  run=%d' % (y, h2[y]))

print('--- FIG2: columnas con run vertical largo (>=25 px) ---')
v2 = long_vruns(g2)
for x in np.where(v2 >= 25)[0]:
    print('  x=%3d  run=%d' % (x, v2[x]))

print('--- FIG4: filas con run oscuro largo (>=40 px) ---')
h4 = long_runs(g4)
for y in np.where(h4 >= 40)[0]:
    print('  y=%3d  run=%d' % (y, h4[y]))

print('--- FIG4: columnas con run vertical largo (>=25 px) ---')
v4 = long_vruns(g4)
for x in np.where(v4 >= 25)[0]:
    print('  x=%3d  run=%d' % (x, v4[x]))