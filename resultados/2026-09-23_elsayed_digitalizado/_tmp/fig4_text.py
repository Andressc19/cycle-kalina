# -*- coding: utf-8 -*-
"""Glifos del texto de la caja superior de fig4 (x=100..235), por linea."""
import numpy as np
from PIL import Image
from scipy import ndimage

g = np.asarray(Image.open(r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013\fig4_eta_vs_P.png').convert('L'))

def glyphs(x0, x1, y0, y1, th=180, minpx=2):
    sub = g[y0:y1, x0:x1] < th
    lab, n = ndimage.label(sub)
    out = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if len(ys) < minpx:
            continue
        out.append((x0 + int(xs.min()), y0 + int(ys.min()), lab == i))
    out.sort(key=lambda t: (t[1], t[0]))
    return out

def show(comp):
    mask = comp[2]
    ys, xs = np.where(mask)
    y0, y1 = ys.min(), ys.max() + 1
    x0, x1 = xs.min(), xs.max() + 1
    crop = mask[y0:y1, x0:x1]
    return '%dx%d %s' % (crop.shape[1], crop.shape[0], '\n'.join(
        ''.join('#' if crop[r, c] else '.' for c in range(crop.shape[1])) for r in range(crop.shape[0])))

for label, y0, y1 in [('linea 1', 12, 26), ('linea 2', 30, 44), ('linea 3', 48, 61), ('linea 4', 66, 79)]:
    print('\n===== %s =====' % label)
    for i, c in enumerate(glyphs(100, 240, y0, y1, 185, 3)):
        print('-- [%02d] x=%d y=%d %s' % (i, c[0], c[1], show(c)))