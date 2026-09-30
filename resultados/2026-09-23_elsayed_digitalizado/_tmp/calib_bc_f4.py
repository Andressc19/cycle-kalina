# -*- coding: utf-8 -*-
"""Calibracion final: posiciones exactas de etiquetas de tick para paneles (b),(c) de fig2 y fig4.
Ejes x: fig2b (5 etiquetas, 0.2..1.0), fig2c (5 etiquetas, 0.2..1.0), fig4 (8 etiquetas, 0..35 bar).
Ejes y: fig2b (10 etiquetas, 0..18), fig2c (6 etiquetas, 0..25), fig4 (5 etiquetas, 0..20)."""
import numpy as np
from PIL import Image
from scipy import ndimage

fig2 = np.asarray(Image.open(r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013\fig2_eta_vs_xb.png').convert('L'))
fig4 = np.asarray(Image.open(r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013\fig4_eta_vs_P.png').convert('L'))

def rowspan(g, y0, y1, x0, x1, th=190, mindark=1):
    """Componentes conexos en una franja: devuelve [(cx_centroide)] ordenados por x."""
    sub = g[y0:y1, x0:x1] < th
    lab, n = ndimage.label(sub)
    out = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if len(ys) >= mindark:
            w = xs.max() - xs.min() + 1
            h = ys.max() - ys.min() + 1
            if w > 30 or h > 14:  # descartar trazos largos (ejes)
                continue
            out.append((x0 + float(xs.mean()), y0 + float(ys.min()), w, h, len(ys)))
    return sorted(out)

print('=== fig2 PANEL (b): etiquetas eje x (buscar 5 grupos en y~265..285, x=620..1040) ===')
for y0 in range(255, 300):
    r = rowspan(fig2, y0, y0 + 12, 620, 1040, 170, 4)
    if len(r) == 5:
        print('y0=%d: %s' % (y0, ['cx=%5.1f w=%2d h=%2d px=%d' % t[:5] for t in r]))
        break

print('\n=== fig2 PANEL (b): etiquetas eje y (10 numeros 0..18, x~600..640) ===')
for y in range(90, 270):
    r = rowspan(fig2, y, y + 11, 588, 644, 170, 3)
    for t in r:
        if t[0] in [x for x, *_ in [(f[0]) for f in found]]:
            continue
    for t in r:
        already = any(abs(f[0] - t[0]) < 3 for f in found)
        if not already and not any(abs(f[1] - t[1]) < 8 for f in found):
            found.append(t)
# agrupar por centroide x del tick label y ordenar por y
print('componentes unicos x~590..644:')
for t in sorted(found, key=lambda t: t[1]):
    print('   y=%4.1f..%4.1f cx=%5.1f w=%2d h=%2d px=%d' % (t[1], t[1] + t[3], t[0], t[2], t[3], t[4]))

print('\n=== fig2 PANEL (c): etiquetas eje x (5 grupos, x=300..760) ===')
for y0 in range(620, 700):
    r = rowspan(fig2, y0, y0 + 12, 300, 760, 170, 4)
    if len(r) == 5:
        print('y0=%d: %s' % (y0, ['cx=%5.1f w=%2d h=%2d px=%d' % t[:5] for t in r]))
        break

print('\n=== fig2 PANEL (c): etiquetas eje y (0..25, 6 numeros, x=300..348) ===')
sub = fig2[376:640, 300:350]
# buscar filas oscuras
rowsim = (sub < 170).sum(axis=1)
print('columnas oscuras por fila (th=170), x=300..350:')
bands = []
inband = False
for i, s in enumerate(rowsim):
    if s > 3 and not inband:
        inband = True
        ystart = i
    elif s <= 3 and inband:
        inband = False
        bands.append((376 + ystart, 376 + i))
if inband:
    bands.append((376 + ystart, 376 + len(rowsim)))
print('   bandas:', bands)

print('\n=== fig4: etiquetas eje x (0..35 bar, 8 numeros, y>293, imagen 525px) ===')
for y0 in range(294, 335):
    r = rowspan(fig4, y0, y0 + 12, 40, 525, 170, 4)
    if len(r) >= 7:
        print('y0=%d (%d labels): %s' % (y0, len(r), ['cx=%5.1f w=%2d h=%2d px=%d' % t[:5] for t in r]))
        break

print('\n=== fig4: etiquetas eje y (0..20, 5 numeros, x=30..52, y=83..295) ===')
sub = fig4[83:295, 24:52]
rowsim = (sub < 170).sum(axis=1)
bands = []
inband = False
for i, s in enumerate(rowsim):
    if s > 2 and not inband:
        inband = True
        ystart = i
    elif s <= 2 and inband:
        inband = False
        bands.append((83 + ystart, 83 + i))
if inband:
    bands.append((83 + ystart, 83 + len(rowsim)))
print('   bandas texto eje y:', bands)