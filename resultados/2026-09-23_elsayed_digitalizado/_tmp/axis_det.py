# -*- coding: utf-8 -*-
"""Filas 248..296 de panel a con regla de x (cada 10px)."""
import os
import numpy as np
from PIL import Image

REF = r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013'
TMP = r'D:\Desktop\ciclo_kalina_tercero\resultados\2026-09-23_elsayed_digitalizado\_tmp'

def load(name):
    return np.asarray(Image.open(os.path.join(REF, name)).convert('L'))

g2 = load('fig2_eta_vs_xb.png')

def render(g, y0, y1, x0, x1, th=200):
    ruler = '      '
    for x in range(x0, x1):
        if x % 10 == 0:
            ruler += str((x // 10) % 10)
        else:
            ruler += '.'
    out = [ruler]
    for y in range(y0, y1):
        row = ''.join('#' if g[y, x] < 90 else ('+' if g[y, x] < 200 else '.') for x in range(x0, x1))
        out.append('%4d %s' % (y, row))
    return '\n'.join(out)

txt = render(g2, 248, 297, 80, 500)
with open(os.path.join(TMP, 'axis_a_det.txt'), 'w', encoding='utf-8') as f:
    f.write(txt)
print('lines', txt.count(chr(10)) + 1)