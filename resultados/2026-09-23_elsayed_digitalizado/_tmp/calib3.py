# -*- coding: utf-8 -*-
"""Escaneo empirico de bandas de texto de ejes para calibracion."""
import numpy as np
from PIL import Image
from scipy import ndimage

fig2 = np.asarray(Image.open(r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013\fig2_eta_vs_xb.png').convert('L'))
fig4 = np.asarray(Image.open(r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013\fig4_eta_vs_P.png').convert('L'))

def text_bands(g, x0, x1, y0, y1, th=175, minpop=2):
    col = (g[y0:y1, x0:x1] < th).sum(axis=1)
    bands = []
    i = 0
    while i < len(col):
        if col[i] >= minpop:
            j = i
            while j < len(col) and col[j] >= minpop:
                j += 1
            bands.append((y0 + i, y0 + j - 1))
            i = j
        else:
            i += 1
    return bands

def comps_in_band(g, y0, y1, x0, x1, th=175, mindark=3, maxw=36, maxh=16):
    sub = g[y0:y1, x0:x1] < th
    lab, n = ndimage.label(sub)
    out = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if len(ys) < mindark:
            continue
        w = xs.max() - xs.min() + 1
        h = ys.max() - ys.min() + 1
        if w <= maxw and h <= maxh:
            out.append((x0 + float(xs.mean()), y0 + float(ys.mean()), w, h))
    out.sort(key=lambda t: t[0])
    return out

# fig2 (b): etiquetas x deberian estar bajo el panel (x=613..1024). Buscar bandas en y=240..330
print('=== fig2(b): bandas de texto x=613..1024, y=240..340 ===')
for b in text_bands(fig2, 613, 1024, 240, 340, 175, 2):
    if b[1] - b[0] > 16:
        continue
    cs = comps_in_band(fig2, b[0], b[1] + 1, 613, 1024, 175)
    if len(cs) >= 4:
        print('  banda y=%d..%d: %s' % (b[0], b[1], ['cx=%5.1f w=%2d' % (c[0], c[2]) for c in cs]))

# fig2 (b): etiquetas y a la izquierda (x=588..644); bandas previas raras, buscar en x=590..646
print('=== fig2(b): bandas de texto eje y x=590..646, y=90..262 ===')
for b in text_bands(fig2, 590, 646, 90, 262, 175, 2):
    if b[1] - b[0] > 16:
        continue
    cs = comps_in_band(fig2, b[0], b[1] + 1, 590, 646, 175)
    print('  banda y=%d..%d: %s' % (b[0], b[1], ['cx=%5.1f w=%2d' % (c[0], c[2]) for c in cs]))

# fig2 (c): etiquetas x bajo panel (x=333..744), buscar y=625..680
print('=== fig2(c): bandas de texto x=333..744, y=625..685 ===')
for b in text_bands(fig2, 333, 744, 625, 685, 175, 2):
    if b[1] - b[0] > 16:
        continue
    cs = comps_in_band(fig2, b[0], b[1] + 1, 333, 744, 175)
    if len(cs) >= 4:
        print('  banda y=%d..%d: %s' % (b[0], b[1], ['cx=%5.1f w=%2d' % (c[0], c[2]) for c in cs]))

# fig2 (c): etiquetas y a la izquierda (x=300..350)
print('=== fig2(c): bandas de texto eje y x=300..350, y=378..640 ===')
for b in text_bands(fig2, 300, 350, 378, 640, 175, 2):
    if b[1] - b[0] > 16:
        continue
    cs = comps_in_band(fig2, b[0], b[1] + 1, 300, 350, 175)
    print('  banda y=%d..%d: %s' % (b[0], b[1], ['cx=%5.1f w=%2d' % (c[0], c[2]) for c in cs]))

# fig4: etiquetas x bajo el grafico (x=50..517), buscar y=290..340
print('=== fig4: bandas de texto x=50..517, y=288..345 ===')
for b in text_bands(fig4, 50, 517, 288, 345, 175, 2):
    if b[1] - b[0] > 16:
        continue
    cs = comps_in_band(fig4, b[0], b[1] + 1, 50, 517, 175)
    if len(cs) >= 5:
        print('  banda y=%d..%d: %s' % (b[0], b[1], ['cx=%5.1f w=%2d' % (c[0], c[2]) for c in cs]))

# fig4: etiquetas y (x=24..52)
print('=== fig4: bandas de texto eje y x=24..52, y=83..295 ===')
for b in text_bands(fig4, 24, 52, 83, 295, 175, 2):
    if b[1] - b[0] > 16:
        continue
    cs = comps_in_band(fig4, b[0], b[1] + 1, 24, 52, 175)
    print('  banda y=%d..%d: %s' % (b[0], b[1], ['cx=%5.1f w=%2d' % (c[0], c[2]) for c in cs]))