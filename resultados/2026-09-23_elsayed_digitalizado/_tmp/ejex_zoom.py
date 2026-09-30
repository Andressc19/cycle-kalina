# -*- coding: utf-8 -*-
"""Franjas de ejes x de los tres paneles a 1x1."""
import os
import numpy as np
from PIL import Image

REF = r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013'
TMP = r'D:\Desktop\ciclo_kalina_tercero\resultados\2026-09-23_elsayed_digitalizado\_tmp'

def load(name):
    return np.asarray(Image.open(os.path.join(REF, name)).convert('L'))

def ascii_rows(g, y0, y1, x0=0, x1=None, th_hi=110, th_mid=200):
    x1 = min(x1 or g.shape[1], g.shape[1])
    out = []
    for y in range(y0, min(y1, g.shape[0])):
        row = []
        for x in range(x0, x1):
            v = g[y, x]
            row.append('#' if v < th_hi else ('+' if v < th_mid else '.'))
        out.append('%4d %s' % (y, ''.join(row)))
    return '\n'.join(out)

g2 = load('fig2_eta_vs_xb.png')
# eje x panel a: x 80..510, y 240..300
txt = ascii_rows(g2, 240, 300, 80, 510)
with open(os.path.join(TMP, 'ejex_a_largo.txt'), 'w', encoding='utf-8') as f:
    f.write(txt)
print('a lines', txt.count(chr(10)) + 1)
# eje x panel b: x 610..1030, y 240..300
txt = ascii_rows(g2, 240, 300, 610, 1030)
with open(os.path.join(TMP, 'ejex_b_largo.txt'), 'w', encoding='utf-8') as f:
    f.write(txt)
print('b lines', txt.count(chr(10)) + 1)
# eje x panel c: x 330..750, y 600..680
txt = ascii_rows(g2, 600, 680, 330, 750)
with open(os.path.join(TMP, 'ejex_c_largo.txt'), 'w', encoding='utf-8') as f:
    f.write(txt)
print('c lines', txt.count(chr(10)) + 1)