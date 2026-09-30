# -*- coding: utf-8 -*-
"""Componentes conexos en areas de datos de cada panel."""
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
        out.append((x0 + int(xs.min()), x0 + int(xs.max()), y0 + int(ys.min()), y0 + int(ys.max()), w, h, len(ys)))
    return out

g2 = load('fig2_eta_vs_xb.png')
g4 = load('fig4_eta_vs_P.png')

# Distribution de grises en area de datos de panel a (entre cajas)
area_a = g2[100:200, 100:480]
h, e = np.histogram(area_a, bins=8, range=(0, 256))
print('FIG2 panel a data area (100..480,100..200) hist:', list(zip(e.tolist(), h.tolist())))

# Panel b data area (x 700..1020, y 40..250)
area_b = g2[40:250, 700:1020]
h, e = np.histogram(area_b, bins=8, range=(0, 256))
print('FIG2 panel b data area hist:', list(zip(e.tolist(), h.tolist())))

print('\n-- FIG2: componentes (th=170) panel a data region x 95..490 y 25..250, tam>=3px --')
for c in sorted(comps(g2, 95, 490, 25, 250, 170), key=lambda c: (c[3], c[0])):
    if c[6] >= 3:
        print('  comp x=%3d..%3d y=%3d..%3d w=%2d h=%2d npx=%3d' % c)

print('\n-- FIG2: componentes (th=170) panel b region x 615..1025 y 25..250 --')
for c in sorted(comps(g2, 615, 1025, 25, 250, 170), key=lambda c: (c[3], c[0])):
    if c[6] >= 3:
        print('  comp x=%3d..%3d y=%3d..%3d w=%2d h=%2d npx=%3d' % c)