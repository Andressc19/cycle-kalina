# -*- coding: utf-8 -*-
"""Componentes exactos (< th) de los glifos grandes de la caja de fig4 (x=55..100)."""
import numpy as np
from PIL import Image
from scipy import ndimage

g = np.asarray(Image.open(r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013\fig4_eta_vs_P.png').convert('L'))

for th in (150, 110):
    print('\n===== threshold <%d =====' % th)
    for label, y0, y1 in [('linea 1', 10, 27), ('linea 2', 28, 45), ('linea 3', 46, 63), ('linea 4', 64, 82)]:
        sub = g[y0:y1, 54:100] < th
        lab, n = ndimage.label(sub)
        print('-- %s (y=%d..%d): %d componentes' % (label, y0, y1, n))
        for i in range(1, n + 1):
            ys, xs = np.where(lab == i)
            if len(ys) < 3:
                print('   [%02d] %d px  x=%d..%d y=%d..%d  (ruido)' % (i, len(ys), 54 + xs.min(), 54 + xs.max(), y0 + ys.min(), y0 + ys.max()))
                continue
            x0, x1 = 54 + xs.min(), 54 + xs.max() + 1
            yy0, yy1 = y0 + ys.min(), y0 + ys.max() + 1
            crop = lab[ys.min():ys.max() + 1, xs.min():xs.max() + 1] > 0
            print('   [%02d] %d px  x=%d..%d y=%d..%d' % (i, len(ys), x0, x1 - 1, yy0, yy1 - 1))
            for r in range(crop.shape[0]):
                print('        %s' % ''.join('#' if crop[r, c] else '.' for c in range(crop.shape[1])))