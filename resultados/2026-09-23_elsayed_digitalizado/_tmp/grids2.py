# -*- coding: utf-8 -*-
"""Grids numericos: marcadores de leyenda (c) y leyenda fig4."""
import os
import numpy as np
from PIL import Image

REF = r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013'
TMP = r'D:\Desktop\ciclo_kalina_tercero\resultados\2026-09-23_elsayed_digitalizado\_tmp'

def load(name):
    return np.asarray(Image.open(os.path.join(REF, name)).convert('L'))

def grid_txt(g, y0, y1, x0, x1):
    hdr = '     ' + ''.join('%3d' % x for x in range(x0, x1))
    lines = [hdr]
    for y in range(y0, y1):
        lines.append('%4d %s' % (y, ''.join('%3d' % g[y, x] for x in range(x0, x1))))
    return '\n'.join(lines)

g2 = load('fig2_eta_vs_xb.png')
g4 = load('fig4_eta_vs_P.png')

parts = [
    ('ley_c_marker_col.txt', g2, 380, 456, 338, 378),
    ('ley_c_ent2.txt', g2, 396, 408, 338, 395),
    ('ley_c_ent5.txt', g2, 441, 453, 338, 395),
]
for name, g, y0, y1, x0, x1 in parts:
    txt = grid_txt(g, y0, y1, x0, x1)
    with open(os.path.join(TMP, name), 'w', encoding='utf-8') as f:
        f.write(txt)
print('ok')