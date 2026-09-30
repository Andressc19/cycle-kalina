# -*- coding: utf-8 -*-
"""Imprime glifos (comps) como arte ASCII para leer texto de leyendas."""
import os
import numpy as np
from PIL import Image
from scipy import ndimage

REF = r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013'

def load(name):
    return np.asarray(Image.open(os.path.join(REF, name)).convert('L'))

def glyphs(g, x0, x1, y0, y1, th=160):
    sub = g[y0:y1, x0:x1] < th
    lab, n = ndimage.label(sub)
    out = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        out.append((x0 + int(xs.min()), y0 + int(ys.min()), lab == i))
    out.sort()
    return out

def show(comp, x, y, w=16):
    mask = comp[2]
    h, ww = mask.shape
    rows = []
    for r in range(h):
        rows.append(''.join('#' if mask[r, c] else '.' for c in range(ww)))
    return 'x=%d y=%d %dx%d\n%s' % (x, y, ww, h, '\n'.join(rows))

g2 = load('fig2_eta_vs_xb.png')

print('===== LEYENDA b, fila 1 (y=225..239, x=625..840) =====')
for i, comp in enumerate(glyphs(g2, 625, 840, 225, 239, 160)):
    print('-- glyph %d --' % i)
    print(show(comp, comp[0], comp[1]))

print('===== LEYENDA b, fila 2 (y=241..256, x=625..840) =====')
for i, comp in enumerate(glyphs(g2, 625, 840, 241, 256, 160)):
    print('-- glyph %d --' % i)
    print(show(comp, comp[0], comp[1]))