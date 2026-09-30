# -*- coding: utf-8 -*-
"""Grids numericos de grises en marcadores candidatos de leyendas."""
import os
import numpy as np
from PIL import Image

REF = r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013'

def load(name):
    return np.asarray(Image.open(os.path.join(REF, name)).convert('L'))

def grid(g, y0, y1, x0, x1, label):
    print('--- %s (x=%d..%d, y=%d..%d) ---' % (label, x0, x1, y0, y1))
    hdr = '     ' + ''.join('%3d' % x for x in range(x0, x1))
    print(hdr)
    for y in range(y0, y1):
        row = ''.join('%3d' % g[y, x] for x in range(x0, x1))
        print('%4d %s' % (y, row))

g2 = load('fig2_eta_vs_xb.png')
g4 = load('fig4_eta_vs_P.png')

# leyenda a: circulo blanco (10 bar) y rombo blanco (15 bar)
grid(g2, 212, 223, 98, 110, 'ley_a marker1 (circle 10bar)')
grid(g2, 228, 240, 98, 112, 'ley_a marker2 (diamond 15bar)')
# leyenda b: entrada 1 y 2 (x=630..640)
grid(g2, 226, 238, 628, 644, 'ley_b marker1 row1 y227..236')
grid(g2, 242, 254, 628, 644, 'ley_b marker2 row2 y243..253')
grid(g2, 214, 220, 750, 768, 'ley_b arriba de caja y215..219')
# lo que sigue al primer marcador de ley_b (para entender layout)
grid(g2, 226, 238, 645, 736, 'ley_b row1 texto x645..736')