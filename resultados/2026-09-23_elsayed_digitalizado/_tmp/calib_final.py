# -*- coding: utf-8 -*-
"""Calibracion definitiva por etiquetas de tick.
Metodo: detectar banda de texto del eje, agrupar glifos en K clusters (K = n labels),
centroide por cluster, ajuste lineal con 1os y ultimos, verificar intermedios (error px).
"""
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
            bands.append((y0 + i, y0 + j))
            i = j
        else:
            i += 1
    return bands

def glyphs(g, y0, y1, x0, x1, th=175, mindark=2):
    sub = g[y0:y1, x0:x1] < th
    lab, n = ndimage.label(sub)
    out = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if len(ys) < mindark:
            continue
        out.append((x0 + float(xs.mean()), xs.size, y0 + float(ys.mean())))
    out.sort(key=lambda t: t[0])
    return out

def cluster_k(centers, K, gap=14):
    """Agrupar centros 1D en K clusters (kmeans unidimensional sencillo)."""
    centers = sorted(centers)
    # kmeans++
    np.random.seed(0)
    c = [centers[len(centers) * i // K] for i in range(K)]  # semilla uniforme
    for _ in range(60):
        groups = [[] for _ in range(K)]
        for p in centers:
            k = min(range(K), key=lambda i: abs(p - c[i]))
            groups[k].append(p)
        for i in range(K):
            if groups[i]:
                c[i] = float(np.mean(groups[i]))
    # reordenar
    order = sorted(range(K), key=lambda i: c[i])
    c = [c[i] for i in order]
    groups = [[] for _ in range(K)]
    for p in centers:
        k = min(range(K), key=lambda i: abs(p - c[i]))
        groups[k].append(p)
    return c, groups

def calibrate(g, x0, x1, y0, y1, K, th=175, axis='x', minbandh=9):
    best = None
    for b in text_bands(g, x0, x1, y0, y1, th, 2):
        if b[1] - b[0] > 14 or b[1] - b[0] < minbandh:
            continue
        gl = glyphs(g, b[0], b[1], x0, x1, th)
        if len(gl) < K:
            continue
        c, groups = cluster_k([t[0] for t in gl], K)
        # validar: cada cluster debe tener >=1 glifo y separaciones ~constantes
        if any(len(g_) == 0 for g_ in groups):  # no puede pasar, but safe
            continue
        seps = np.diff(c)
        good = np.all(seps > 0) and (np.max(seps) - np.min(seps)) <= 6
        if good:
            best = (b, c, len(gl), seps)
            break
    return best

print('=== fig2(b) EJE X: 5 etiquetas (0.2..1.0), banda y=250..330 ===')
r = calibrate(fig2, 613, 1024, 250, 330, 5, 175)
if r:
    b, c, ngl, seps = r
    print(' banda y=%d..%d, glifos=%d' % (b[0], b[1], ngl))
    print(' centros: %s' % ['%.1f' % x for x in c])
    print(' separaciones: %s' % ['%.1f' % x for x in seps])
    # ajuste lineal val=(0.2..1.0): slope px/val
    vals = np.array([0.2, 0.4, 0.6, 0.8, 1.0])
    coef = np.polyfit(vals, c, 1)
    for v, x in zip(vals, c):
        print('   %s -> x=%.1f (fit %.1f, err %+.1f px)' % (v, x, np.polyval(coef, v), x - np.polyval(coef, v)))
    print('   coef: x = %.4f + %.4f*val' % (coef[1], coef[0]))

print('\n=== fig2(c) EJE X: 5 etiquetas (0.2..1.0), banda y=625..665 ===')
r = calibrate(fig2, 333, 744, 625, 665, 5, 175)
if r:
    b, c, ngl, seps = r
    print(' banda y=%d..%d, glifos=%d' % (b[0], b[1], ngl))
    print(' centros: %s' % ['%.1f' % x for x in c])
    vals = np.array([0.2, 0.4, 0.6, 0.8, 1.0])
    coef = np.polyfit(vals, c, 1)
    for v, x in zip(vals, c):
        print('   %s -> x=%.1f (err %+.1f px)' % (v, x, x - np.polyval(coef, v)))
    print('   coef: x = %.4f + %.4f*val' % (coef[1], coef[0]))

print('\n=== fig2(b) EJE Y: 10 etiquetas (0..18 pares), x=590..646 ===')
r = calibrate(fig2, 588, 648, 95, 262, 10, 175, 'y')
if r:
    b, c, ngl, seps = r
    print(' banda y=%d..%d, glifos=%d' % (b[0], b[1], ngl))
    print(' centros (y): %s' % ['%.1f' % x for x in c])
    print(' separaciones: %s' % ['%.1f' % x for x in seps])
    vals = np.array([0, 2, 4, 6, 8, 10, 12, 14, 16, 18])
    coef = np.polyfit(vals, c, 1)
    for v, x in zip(vals, c):
        print('   %2d -> y=%.1f (err %+.1f px)' % (v, x, x - np.polyval(coef, v)))
    print('   coef: y = %.4f + %.4f*val' % (coef[1], coef[0]))

print('\n=== fig2(c) EJE Y: 6 etiquetas (0,5,10,15,20,25), x=300..350 ===')
r = calibrate(fig2, 300, 352, 378, 640, 6, 175, 'y')
if r:
    b, c, ngl, seps = r
    print(' banda y=%d..%d, glifos=%d' % (b[0], b[1], ngl))
    print(' centros (y): %s' % ['%.1f' % x for x in c])
    vals = np.array([0, 5, 10, 15, 20, 25])
    coef = np.polyfit(vals, c, 1)
    for v, x in zip(vals, c):
        print('   %2d -> y=%.1f (err %+.1f px)' % (v, x, x - np.polyval(coef, v)))
    print('   coef: y = %.4f + %.4f*val' % (coef[1], coef[0]))
else:
    print('  (no encontrado K=6)')

print('\n=== fig4 EJE X: 8 etiquetas (0..35 cada 5), y=285..325 ===')
r = calibrate(fig4, 45, 522, 285, 325, 8, 175)
if r:
    b, c, ngl, seps = r
    print(' banda y=%d..%d, glifos=%d' % (b[0], b[1], ngl))
    print(' centros: %s' % ['%.1f' % x for x in c])
    print(' separaciones: %s' % ['%.1f' % x for x in seps])
    vals = np.array([0, 5, 10, 15, 20, 25, 30, 35])
    coef = np.polyfit(vals, c, 1)
    for v, x in zip(vals, c):
        print('   %2d -> x=%.1f (err %+.1f px)' % (v, x, x - np.polyval(coef, v)))
    print('   coef: x = %.4f + %.4f*val' % (coef[1], coef[0]))

print('\n=== fig4 EJE Y: 5 etiquetas (0,5,10,15,20), x=24..58 ===')
r = calibrate(fig4, 24, 58, 83, 295, 5, 175, 'y')
if r:
    b, c, ngl, seps = r
    print(' banda y=%d..%d, glifos=%d' % (b[0], b[1], ngl))
    print(' centros (y): %s' % ['%.1f' % x for x in c])
    vals = np.array([0, 5, 10, 15, 20])
    coef = np.polyfit(vals, c, 1)
    for v, x in zip(vals, c):
        print('   %2d -> y=%.1f (err %+.1f px)' % (v, x, x - np.polyval(coef, v)))
    print('   coef: y = %.4f + %.4f*val' % (coef[1], coef[0]))
else:
    print('  (no encontrado K=5)')