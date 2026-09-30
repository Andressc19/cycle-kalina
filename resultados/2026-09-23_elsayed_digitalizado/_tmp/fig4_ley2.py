# -*- coding: utf-8 -*-
"""Leyenda fig4 multi-umbral."""
import numpy as np
from PIL import Image

g = np.asarray(Image.open(r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013\fig4_eta_vs_P.png').convert('L'))

def art(x0, x1, y0, y1, th, plus=60, label=''):
    print('--- %s x=%d..%d y=%d..%d th=%d ---' % (label, x0, x1, y0, y1, th))
    ruler = ''.join(str((x // 10) % 10) if x % 10 == 0 else ('^' if x % 5 == 0 else '.') for x in range(x0, x1))
    print('     ' + ruler)
    for y in range(y0, y1):
        s = ''
        for x in range(x0, x1):
            v = g[y, x]
            s += '#' if v < th else ('+' if v < th + plus else '.')
        print('%3d|%s|' % (y, s))

# columna izquierda de la caja x=48..130 y=8..80 a th=130 (marcadores claros)
for th in (100, 130, 160):
    art(48, 130, 8, 80, th, 45, 'col-izq')