# -*- coding: utf-8 -*-
"""Zoom eje y panel a: x 40..110, y 30..300.  Ademas leyenda panel a y eje x."""
import os
import numpy as np
from PIL import Image

REF = r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013'
TMP = r'D:\Desktop\ciclo_kalina_tercero\resultados\2026-09-23_elsayed_digitalizado\_tmp'

def load(name):
    return np.asarray(Image.open(os.path.join(REF, name)).convert('L'))

def ascii_1x1(g, x0, x1, y0, y1, th_hi=90, th_mid=180):
    out = []
    for y in range(y0, min(y1, g.shape[0])):
        row = []
        for x in range(x0, min(x1, g.shape[1])):
            v = g[y, x]
            row.append('#' if v < th_hi else ('+' if v < th_mid else '.'))
        out.append('%4d %s' % (y, ''.join(row)))
    return '\n'.join(out)

g2 = load('fig2_eta_vs_xb.png')
txt = ascii_1x1(g2, 40, 110, 25, 300)
with open(os.path.join(TMP, 'zoom_ejey_a.txt'), 'w', encoding='utf-8') as f:
    f.write(txt)
print('lines', txt.count(chr(10)) + 1)