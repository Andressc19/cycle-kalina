# -*- coding: utf-8 -*-
"""Localiza clusters de marcador en el cuerpo de fig4 (fuera de la caja de leyenda) y los imprime.
Compara con las plantillas de fig2 (rombo blanco / rombo gris)."""
import numpy as np
from PIL import Image
from scipy import ndimage

# plantillas conocidas de fig2 (registradas en sesion anterior / renders)
g2 = np.asarray(Image.open(r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013\fig2_eta_vs_xb.png').convert('L'))
# rombo gris de fig2b: x=631..640 y=244..253 ; rombo blanco fig2a: x=101..110 y=229..239
for name, x0, x1, y0, y1, th in [('fig2b rombo GRIS leg-b', 631, 641, 244, 254, 170),
                                 ('fig2a rombo BLANCO leg-a', 101, 111, 229, 240, 170)]:
    print('===== %s =====' % name)
    for y in range(y0, y1):
        print('%3d: %s' % (y, ''.join('#' if g2[y, x] < th else ('+' if g2[y, x] < th + 60 else '.') for x in range(x0, x1))))

g = np.asarray(Image.open(r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013\fig4_eta_vs_P.png').convert('L'))

def clusters(x0, x1, y0, y1, th=170, minpx=2, maxpx=60):
    sub = g[y0:y1, x0:x1] < th
    lab, n = ndimage.label(sub)
    out = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if minpx <= len(ys) <= maxpx:
            out.append((x0 + int(xs.min()), y0 + int(ys.min()), lab == i, len(ys)))
    out.sort(key=lambda t: (t[1], t[0]))
    return out

print('\n===== fig4 cuerpo: clusters pequenos (probables marcadores), y=84..288, x=54..520 =====')
for i, (cx, cy, mask, npx) in enumerate(clusters(54, 520, 84, 288, 170, 4, 50)):
    ys, xs = np.where(mask)
    bx0, bx1 = xs.min(), xs.max() + 1
    by0, by1 = ys.min(), ys.max() + 1
    crop = mask[by0:by1, bx0:bx1]
    h, w = crop.shape
    if not (6 <= h <= 14 and 6 <= w <= 14):
        continue
    print('-- [%02d] %dpx x=%d..%d y=%d..%d (%dx%d)' % (i, npx, cx + bx0, cx + bx1 - 1, cy + by0, cy + by1 - 1, w, h))
    for r in range(h):
        print('     %s' % ''.join('#' if crop[r, c] else '.' for c in range(w)))