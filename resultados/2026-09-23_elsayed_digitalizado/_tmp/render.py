# -*- coding: utf-8 -*-
"""Render ASCII fino por region -> archivos txt para inspeccion."""
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
regions = [
    ('fig2_top_left', g2, 20, 560, 0, 320, 3, 4),
    ('fig2_top_right', g2, 560, 1029, 0, 320, 3, 4),
    ('fig2_bottom', g2, 240, 820, 320, 680, 3, 4),
]
for name, g, x0, x1, y0, y1, bx, by in regions:
    txt = ascii_region(g, x0, x1, y0, y1, bx, by)
    with open(os.path.join(TMP, name + '.txt'), 'w', encoding='utf-8') as fh:
        fh.write(txt)
    print('wrote', name, 'lines=', txt.count(chr(10)) + 1)