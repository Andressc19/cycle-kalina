# -*- coding: utf-8 -*-
"""Calibracion final de ejes fig2 (b)/(c) y fig4."""
import numpy as np
from PIL import Image
from scipy import ndimage

fig2 = np.asarray(Image.open(r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013\fig2_eta_vs_xb.png').convert('L'))
fig4 = np.asarray(Image.open(r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013\fig4_eta_vs_P.png').convert('L'))

def comps(g, y0, y1, x0, x1, th=170, mindark=3):
    sub = g[y0:y1, x0:x1] < th
    lab, n = ndimage.label(sub)
    out = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if len(ys) < mindark:
            continue
        w = xs.max() - xs.min() + 1
        h = ys.max() - ys.min() + 1
        if w > 34 or h > 15:
            continue
        out.append((x0 + float(xs.mean()), y0 + float(ys.mean()), w, h, len(ys)))
    out.sort(key=lambda t: t[0])
    return out

def xlabels(g, x0, x1, ylo, yhi, th=170, expect=None):
    for y0 in range(ylo, yhi):
        r = comps(g, y0, y0 + 13, x0, x1, th)
        if expect and len(r) == expect:
            print('  fila y0=%d: %s' % (y0, ['cx=%5.1f w=%2d' % (t[0], t[2]) for t in r]))
            return r
        if not expect and len(r) >= 4:
            print('  fila y0=%d (%d): %s' % (y0, len(r), ['cx=%5.1f w=%2d' % (t[0], t[2]) for t in r]))
            return r
    return None

print('=== fig2 PANEL (b) etiquetas eje x (0.2..1.0, esperar 5) ===')
xlabels(fig2, 620, 1040, 262, 290, 170, 5)

print('=== fig2 PANEL (c) etiquetas eje x (0.2..1.0, esperar 5) ===')
xlabels(fig2, 300, 760, 626, 660, 170, 5)

print('=== fig4 etiquetas eje x (0..35, esperar 8) ===')
xlabels(fig4, 40, 525, 294, 330, 170, 8)

def ylabels(g, x0, x1, ylo, yhi, th=170, minrowpop=3):
    """bandas de texto del eje y: detectar filas oscuras y agrupar."""
    col = (g[ylo:yhi, x0:x1] < th).sum(axis=1)
    bands = []
    i = 0
    while i < len(col):
        if col[i] >= minrowpop:
            j = i
            while j < len(col) and col[j] >= minrowpop:
                j += 1
            bands.append((ylo + i, ylo + j - 1))
            i = j
        else:
            i += 1
    return bands

print('=== fig2 PANEL (b) etiquetas eje y: bandas (x=588..644) ===')
print(yLabels if False else ylabels(fig2, 588, 644, 95, 262, 170, 2))

print('=== fig2 PANEL (c) etiquetas eje y: bandas (x=300..350) ===')
print(ylabels(fig2, 300, 350, 378, 640, 170, 2))

print('=== fig4 etiquetas eje y: bandas (x=24..52) ===')
print(ylabels(fig4, 24, 52, 84, 295, 170, 2))