# -*- coding: utf-8 -*-
"""Leyenda de fig4: arte ASCII."""
import numpy as np
from PIL import Image

g = np.asarray(Image.open(r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013\fig4_eta_vs_P.png').convert('L'))

def art(x0, x1, y0, y1, th=170):
    print('--- x=%d..%d y=%d..%d th=%d ---' % (x0, x1, y0, y1, th))
    ruler = ''.join(str((x // 10) % 10) if x % 10 == 0 else ('^' if x % 5 == 0 else '.') for x in range(x0, x1))
    print('     ' + ruler)
    for y in range(y0, y1):
        s = ''
        for x in range(x0, x1):
            v = g[y, x]
            s += '#' if v < th else ('+' if v < th + 60 else '.')
        print('%3d|%s|' % (y, s))

art(48, 225, 8, 90, 170)