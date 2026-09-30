# -*- coding: utf-8 -*-
"""Glifos de leyenda (a) para comparar '10 bar' / '15 bar'."""
import os
import numpy as np
from PIL import Image
from scipy import ndimage

REF = r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013'

def load(name):
    return np.asarray(Image.open(os.path.join(REF, name)).convert('L'))

def glyphs(g, x0, x1, y0, y1, th=160, minpx=2):
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
    return '\n'.join(''.join('#' if crop[r, c] else '.' for c in range(crop.shape[1])) for r in range(crop.shape[0]))

g2 = load('fig2_eta_vs_xb.png')

print('===== LEY a, texto fila1 (y=210..226, x=95..300) — "10 bar" =====')
for label, x0, x1, y0, y1 in [
    ('LEY a fila1', 95, 300, 210, 226),
    ('LEY a fila2', 95, 300, 226, 242),
]:
    print('\n-- %s --' % label)
    gs = glyphs(g2, x0, x1, y0, y1, 160)
    for i, c in enumerate(gs):
        print('-- [%02d] x=%d y=%d --' % (i, c[0], c[1]))
        print(show(c))