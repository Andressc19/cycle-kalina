# -*- coding: utf-8 -*-
"""Busca lineas de eje: runs horizontales/verticales largos con g<200."""
import os
import numpy as np
from PIL import Image

REF = r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013'

def load(name):
    return np.asarray(Image.open(os.path.join(REF, name)).convert('L'))

def max_run_row(row, th):
    d = row < th
    best = 0; bestx = (0, 0); cur = 0; start = 0
    for i, v in enumerate(d):
        if v:
            if cur == 0:
                start = i
            cur += 1
            if cur > best:
                best = cur
                bestx = (start, i)
        else:
            cur = 0
    return best, bestx

for name in ['fig2_eta_vs_xb.png', 'fig4_eta_vs_P.png']:
    g = load(name)
    print('==== %s  (%dx%d) ====' % (name, g.shape[1], g.shape[0]))
    print('-- mayor run horizontal (g<200) por fila, filtro run>=80 --')
    for y in range(g.shape[0]):
        b, (a, c) = max_run_row(g[y], 200)
        if b >= 80:
            print('  y=%3d run=%3d x=%3d..%3d' % (y, b, a, c))
    # verticales: transponer y repetir
    print('-- mayor run vertical (g<200) por columna, filtro run>=80 --')
    for x in range(g.shape[1]):
        b, (a, c) = max_run_row(g[:, x], 200)
        if b >= 80:
            print('  x=%3d run=%3d y=%3d..%3d' % (x, b, a, c))