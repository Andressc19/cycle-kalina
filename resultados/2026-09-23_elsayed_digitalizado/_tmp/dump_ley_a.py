# -*- coding: utf-8 -*-
"""Caja completa de leyendas en ASCII 1x1."""
import os
import numpy as np
from PIL import Image

REF = r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013'

def load(name):
    return np.asarray(Image.open(os.path.join(REF, name)).convert('L'))

def dump(g, x0, x1, y0, y1, th=140, name=''):
    print('--- %s (%d-%d, %d-%d) ---' % (name, x0, x1, y0, y1))
    rows = []
    for y in range(y0, y1):
        row = []
        for x in range(x0, x1):
            v = g[y, x]
            c = '#' if v < th else ('+' if v < th + 40 else '.')
            row.append(c)
        rows.append('%3d|%s|' % (y, ''.join(row)))
    print('\n'.join(rows))

g2 = load('fig2_eta_vs_xb.png')
dump(g2, 92, 290, 205, 254, 150, 'LEYENDA a')