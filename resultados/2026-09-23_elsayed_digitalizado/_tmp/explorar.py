# -*- coding: utf-8 -*-
"""Exploracion de pixeles de fig2_eta_vs_xb.png y fig4_eta_vs_P.png
para calibrar ejes y localizar paneles/leyendas/cajas de texto."""
import os
import numpy as np
from PIL import Image

REF = r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013'

def analyze(name):
    im = Image.open(os.path.join(REF, name))
    a = np.asarray(im)
    print('=' * 70)
    print(name, 'size', im.size, 'mode', im.mode, 'arr', a.shape, a.dtype)
    g = a if a.ndim == 2 else a.mean(axis=2)
    print('gray min/max/mean', g.min(), g.max(), round(float(g.mean()), 1))
    # histograma de niveles de gris mas comunes
    hist, edges = np.histogram(g, bins=16, range=(0, 256))
    for h, e in zip(hist, edges):
        print('  g[%3d..%3d): %6d px' % (e, e + 16, h))
    return g

g2 = analyze('fig2_eta_vs_xb.png')
g4 = analyze('fig4_eta_vs_P.png')

def column_profile(g, y_mid):
    """perfil de oscuridad por columna en la fila y_mid (busca bordes de paneles)"""
    row = g[y_mid]
    dark = row < 128
    # transiciones
    tr = np.diff(dark.astype(int))
    starts = np.where(tr == 1)[0] + 1
    ends = np.where(tr == -1)[0]
    print('  fila', y_mid, ': segmentos oscuros', list(zip(starts.tolist(), ends.tolist()))[:40])

print('\n-- FIG2 perfiles de fila (buscar cajas de panel) --')
for y in range(0, g2.shape[0], 40):
    column_profile(g2, y)

print('\n-- FIG4 perfiles de fila --')
for y in range(0, g4.shape[0], 30):
    column_profile(g4, y)