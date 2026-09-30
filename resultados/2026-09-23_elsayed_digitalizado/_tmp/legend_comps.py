# -*- coding: utf-8 -*-
"""Candidatos a marcador (bloques compactos ~7..13px) en leyendas de fig2(a,b,c) y fig4."""
import os
import numpy as np
from PIL import Image
from scipy import ndimage

REF = r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013'

def load(name):
    return np.asarray(Image.open(os.path.join(REF, name)).convert('L'))

def comps(g, x0, x1, y0, y1, th):
    sub = g[y0:y1, x0:x1] < th
    lab, n = ndimage.label(sub)
    out = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        h = ys.max() - ys.min() + 1
        w = xs.max() - xs.min() + 1
        out.append((x0 + int(xs.min()), x0 + int(xs.max()), y0 + int(ys.min()), y0 + int(ys.max()), w, h, int(len(ys)), int(w * h)))
    return out

g2 = load('fig2_eta_vs_xb.png')
g4 = load('fig4_eta_vs_P.png')

regions = [
    ('ley a', g2, 92, 290, 204, 256),
    ('ley b', g2, 622, 842, 214, 262),
    ('ley c', g2, 330, 470, 375, 460),
    ('ley f4', g4, 46, 232, 6, 88),
]
for tag, g, x0, x1, y0, y1 in regions:
    print('\n=== %s ===' % tag)
    for c in sorted(comps(g, x0, x1, y0, y1, 200), key=lambda c: (c[3], c[0])):
        w, h, npx = c[4], c[5], c[6]
        # marcador: w~6..14, h~6..14, aspecto 0.6..1.6, npx entre 30% y 95% del area
        aspect = w / h if h else 0
        is_marker = 6 <= w <= 14 and 6 <= h <= 14 and 0.5 <= aspect <= 2.0
        mark = 'MARK' if is_marker else ''
        print('   x=%3d..%3d y=%3d..%3d w=%2d h=%2d npx=%3d area=%3d ar=%.2f %s' % (c[0], c[1], c[2], c[3], w, h, npx, c[7], aspect, mark))