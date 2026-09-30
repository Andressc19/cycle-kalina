# -*- coding: utf-8 -*-
"""Render 1x1 de las cajas de leyenda de fig2 (a,b,c) y fig4."""
import os
import numpy as np
from PIL import Image

REF = r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013'
TMP = r'D:\Desktop\ciclo_kalina_tercero\resultados\2026-09-23_elsayed_digitalizado\_tmp'

def load(name):
    return np.asarray(Image.open(os.path.join(REF, name)).convert('L'))

def render(g, y0, y1, x0, x1, th_dark=90, th_mid=200):
    ruler = '      '
    for x in range(x0, x1):
        if x % 5 == 0:
            ruler += str((x // 10) % 10)
        else:
            ruler += '.'
    out = [ruler]
    for y in range(y0, y1):
        row = ''.join('#' if g[y, x] < th_dark else ('+' if g[y, x] < th_mid else '.') for x in range(x0, x1))
        out.append('%4d %s' % (y, row))
    return '\n'.join(out)

g2 = load('fig2_eta_vs_xb.png')
g4 = load('fig4_eta_vs_P.png')

jobs = [
    ('ley_a.txt', g2, 203, 258, 90, 300),
    ('ley_b.txt', g2, 215, 262, 615, 845),
    ('ley_c.txt', g2, 375, 458, 330, 470),
    ('ley_f4.txt', g4, 5, 90, 45, 230),
]
for name, g, y0, y1, x0, x1 in jobs:
    txt = render(g, y0, y1, x0, x1)
    with open(os.path.join(TMP, name), 'w', encoding='utf-8') as f:
        f.write(txt)
    print(name, 'ok lines=%d' % (txt.count(chr(10)) + 1))