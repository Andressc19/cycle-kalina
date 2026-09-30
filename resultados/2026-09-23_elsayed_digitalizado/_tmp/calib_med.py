# -*- coding: utf-8 -*-
"""Medicion precisa de centros de etiquetas y calibracion lineal."""
import numpy as np
from PIL import Image
from scipy import ndimage

fig2 = np.asarray(Image.open(r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013\fig2_eta_vs_xb.png').convert('L'))
fig4 = np.asarray(Image.open(r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013\fig4_eta_vs_P.png').convert('L'))

def label_clusters(g, y0, y1, x0, x1, th=185, K=None):
    """Divide la banda en K clusters por separacion minima; devuelve centros x."""
    sub = g[y0:y1, x0:x1] < th
    lab, n = ndimage.label(sub)
    glyphs = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if len(ys) >= 3:
            glyphs.append((x0 + float(xs.mean()), len(ys)))
    glyphs.sort(key=lambda t: t[0])
    if not glyphs:
        return [], glyphs
    # agrupar glifos: separacion entre centros < gap => misma etiqueta
    groups = [[glyphs[0]]]
    for g_ in glyphs[1:]:
        if g_[0] - groups[-1][-1][0] < 16:
            groups[-1].append(g_)
        else:
            groups.append([g_])
    ctr = [float(np.mean([t[0] for t in gr])) for gr in groups]
    return ctr, groups

def report(name, ctr, vals):
    ctr, vals = np.array(ctr), np.array(vals)
    coef = np.polyfit(vals, ctr, 1)
    print('%s: K=%d' % (name, len(ctr)))
    for v, c in zip(vals, ctr):
        print('   %5s -> %8.2f px  (fit %8.2f, err %+6.2f px)' % (v, c, np.polyval(coef, v), c - np.polyval(coef, v)))
    print('   => px = %.5f * val %+.5f' % (coef[0], coef[1]))
    print('   => val = px*%.6f %+.6f' % (1 / coef[0], -coef[1] / coef[0]))
    return coef

# ---- fig2(b) eje x: banda y=283..293
print('=' * 30, 'fig2(b) x', '=' * 30)
ctr, _ = label_clusters(fig2, 283, 294, 610, 1029, 185)
print('centros crudos:', ['%.1f' % c for c in ctr])
# debe ser 5: 0.2,0.4,0.6,0.8,1.0. Si hay mas de 5, relajar a K mas grandes
vals = [0.2, 0.4, 0.6, 0.8, 1.0]
if len(ctr) == 5:
    report('fig2(b) x', ctr, vals)
else:
    # intentar con 5 agrupando manualmente si hay ruido
    print('(!) no son 5; dump glifos:')
    for c, g in _:
        print('   glifo x=%.1f (%d px)' % (c, g))

# ---- fig2(c) eje x: banda y=638..648
print('=' * 30, 'fig2(c) x', '=' * 30)
ctr, _ = label_clusters(fig2, 638, 648, 300, 760, 185)
print('centros crudos:', ['%.1f' % c for c in ctr])
vals = [0.2, 0.4, 0.6, 0.8, 1.0]
if len(ctr) == 5:
    report('fig2(c) x', ctr, vals)
else:
    for c, g in _:
        print('   glifo x=%.1f (%d px)' % (c, g))

# ---- fig4 eje x: banda y=299..311
print('=' * 30, 'fig4 x', '=' * 30)
ctr, _ = label_clusters(fig4, 299, 311, 40, 525, 185)
print('centros crudos:', ['%.1f' % c for c in ctr])
vals = [0, 5, 10, 15, 20, 25, 30, 35]
if len(ctr) == 8:
    report('fig4 x', ctr, vals)
else:
    for c, g in _:
        print('   glifo x=%.1f (%d px)' % (c, g))

# ---- fig4 eje y: banda x=20..60
print('=' * 30, 'fig4 y', '=' * 30)
# bandas de texto a la izquierda
col = (fig4[83:295, 20:60] < 185).sum(axis=1)
bands = []
i = 0
while i < len(col):
    if col[i] >= 2:
        j = i
        while j < len(col) and col[j] >= 2:
            j += 1
        bands.append((83 + i, 83 + j - 1, j - i))
        i = j
    else:
        i += 1
print('bandas posibles:', [(a, b, l) for a, b, l in bands if l <= 14])
# centros de cada banda como etiquetas y
lbl = []
for a, b, l in bands:
    if l <= 11 and l >= 7:
        sub = fig4[a:b + 1, 20:60] < 185
        ys, xs = np.where(sub)
        lbl.append((a + float(ys.mean())))
print('centros y por banda:', ['%.1f' % c for c in lbl])
# esperamos 5: 20,15,10,5,0 (y creciente hacia abajo ~ 0 abajo)
vals = sorted([0, 5, 10, 15, 20], reverse=True)
if len(lbl) == 5:
    report('fig4 y', lbl, vals)