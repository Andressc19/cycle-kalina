# -*- coding: utf-8 -*-
"""Panel (b) y (c) completos en render coarse 4x4, y grids de candidatos de leyenda."""
import os
import numpy as np
from PIL import Image

REF = r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013'
TMP = r'D:\Desktop\ciclo_kalina_tercero\resultados\2026-09-23_elsayed_digitalizado\_tmp'

def load(name):
    return np.asarray(Image.open(os.path.join(REF, name)).convert('L'))

def coarse(g, y0, y1, x0, x1, bs=4, th=160):
    out = []
    for y in range(y0, y1, bs):
        row = ''
        for x in range(x0, x1, bs):
            block = g[y:y + bs, x:x + bs]
            frac = np.sum(block < th) / block.size
            row += '.' if frac < 0.05 else ('+' if frac < 0.5 else '#')
        out.append('%4d %s' % (y, row))
    return '\n'.join(out)

def grid(g, y0, y1, x0, x1, label):
    print('--- %s (x=%d..%d, y=%d..%d) ---' % (label, x0, x1, y0, y1))
    hdr = '     ' + ''.join('%3d' % x for x in range(x0, x1))
    print(hdr)
    for y in range(y0, y1):
        row = ''.join('%3d' % g[y, x] for x in range(x0, x1))
        print('%4d %s' % (y, row))

g2 = load('fig2_eta_vs_xb.png')
g4 = load('fig4_eta_vs_P.png')

with open(os.path.join(TMP, 'panel_b_coarse.txt'), 'w', encoding='utf-8') as f:
    f.write(coarse(g2, 0, 350, 560, 1030, 4, 160))
with open(os.path.join(TMP, 'panel_c_coarse.txt'), 'w', encoding='utf-8') as f:
    f.write(coarse(g2, 340, 680, 280, 780, 4, 160))

# grids de leyenda b: zonas col2 (posibles 25/30 bar)
grid(g2, 226, 238, 684, 740, 'ley_b row1 derecho x684..740')
grid(g2, 242, 255, 680, 745, 'ley_b row2 derecho x680..745')
grid(g2, 214, 222, 750, 770, 'ley_b y=215..222 x750..770')