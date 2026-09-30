# -*- coding: utf-8 -*-
"""Coordenadas exactas de lines largas (runs >= 40px, g<170)."""
import os
import numpy as np
from PIL import Image

REF = r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013'

def load(name):
    return np.asarray(Image.open(os.path.join(REF, name)).convert('L'))

def find_runs_1d(v, minlen):
    runs = []
    cur = 0
    start = 0
    for i, x in enumerate(v):
        if x:
            if cur == 0:
                start = i
            cur += 1
        else:
            if cur >= minlen:
                runs.append((start, i - 1))
            cur = 0
    if cur >= minlen:
        runs.append((start, len(v) - 1))
    return runs

for name in ['fig2_eta_vs_xb.png', 'fig4_eta_vs_P.png']:
    g = load(name)
    dark = g < 170
    print('==== %s ====' % name)
    print('-- filas: runs horizontales >=40px --')
    for y in range(dark.shape[0]):
        for (a, b) in find_runs_1d(dark[y], 40):
            print('  y=%3d x=%3d..%3d  len=%d' % (y, a, b, b - a + 1))
    print('-- columnas: runs verticales >=40px --')
    for x in range(dark.shape[1]):
        for (a, b) in find_runs_1d(dark[:, x], 40):
            print('  x=%3d y=%3d..%3d  len=%d' % (x, a, b, b - a + 1))