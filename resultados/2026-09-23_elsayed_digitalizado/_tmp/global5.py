# -*- coding: utf-8 -*-
"""Vista global completa 5x5 px/char."""
import os
import numpy as np
from PIL import Image

REF = r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013'
TMP = r'D:\Desktop\ciclo_kalina_tercero\resultados\2026-09-23_elsayed_digitalizado\_tmp'

def load(name):
    return np.asarray(Image.open(os.path.join(REF, name)).convert('L'))

def ascii_region(g, x0, x1, y0, y1, bx, by, th_hi=90, th_mid=180, th_lo=235):
    out = []
    for y in range(y0, min(y1, g.shape[0]), by):
        row = []
        for x in range(x0, min(x1, g.shape[1]), bx):
            m = g[y:y + by, x:x + bx].mean()
            if m < th_hi:
                row.append('#')
            elif m < th_mid:
                row.append('+')
            elif m < th_lo:
                row.append('-')
            else:
                row.append('.')
        out.append('%4d %s' % (y, ''.join(row)))
    return '\n'.join(out)

g2 = load('fig2_eta_vs_xb.png')
txt = ascii_region(g2, 0, 1029, 0, 680, 5, 5)
with open(os.path.join(TMP, 'fig2_global5.txt'), 'w', encoding='utf-8') as f:
    f.write(txt)
print('lines', txt.count(chr(10)) + 1)