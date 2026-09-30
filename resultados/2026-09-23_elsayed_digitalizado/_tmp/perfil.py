# -*- coding: utf-8 -*-
"""Perfil de pixeles MUY oscuros (g<100) para localizar ejes/curvas/etiquetas."""
import os
import numpy as np
from PIL import Image

REF = r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013'

def load(name):
    return np.asarray(Image.open(os.path.join(REF, name)).convert('L'))

g2 = load('fig2_eta_vs_xb.png')
d2 = g2 < 100
nrow = d2.sum(axis=1)
ncol = d2.sum(axis=0)

print('--- FIG2 filas con >=5 px oscuros (g<100) ---')
for y in np.where(nrow >= 5)[0]:
    xs = np.where(d2[y])[0]
    print('  y=%3d count=%3d x:[%3d..%3d] gaps>12: %s' % (y, nrow[y], xs[0], xs[-1],
          [int(a) for a in np.where(np.diff(xs) > 12)[0] + 1][:12]))

print('--- FIG2 columnas con >=5 px oscuros ---')
for x in np.where(ncol >= 5)[0]:
    ys = np.where(d2[:, x])[0]
    print('  x=%3d count=%3d y:[%3d..%3d] gaps>12: %s' % (x, ncol[x], ys[0], ys[-1],
          [int(a) for a in np.where(np.diff(ys) > 12)[0] + 1][:12]))