# -*- coding: utf-8 -*-
"""Grids numericos de los 5 marcadores de leyenda (c) + leyenda fig4."""
import os
import numpy as np
from PIL import Image

REF = r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013'

def load(name):
    return np.asarray(Image.open(os.path.join(REF, name)).convert('L'))

def grid(g, x0, x1, y0, y1):
    print('--- grid x=%d..%d y=%d..%d ---' % (x0, x1, y0, y1))
    rows = []
    for y in range(y0, y1):
        vals = []
        for x in range(x0, x1):
            v = g[y, x]
            vals.append('%3d' % v)
        rows.append('%3d ' % y + ' '.join(vals))
    print('\n'.join(rows))

g2 = load('fig2_eta_vs_xb.png')

# Filas de leyenda (c) segun analisis previo: 383..391 / 398..406 / 413..421 / 428..436 / 443..451
# Columna de marcadores: x=344..373
for (y0, y1) in [(383, 392), (398, 407), (413, 422), (428, 437), (443, 452)]:
    grid(g2, 340, 395, y0, y1)