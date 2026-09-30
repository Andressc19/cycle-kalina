# -*- coding: utf-8 -*-
"""Detecta ejes y ticks de los 3 paneles de fig2 y de fig4."""
import os
import numpy as np
from PIL import Image

REF = r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013'

def load(name):
    return np.asarray(Image.open(os.path.join(REF, name)).convert('L'))

def runs_1d(v, minlen):
    out = []
    cur = 0
    start = 0
    for i, x in enumerate(v):
        if x:
            if cur == 0:
                start = i
            cur += 1
        else:
            if cur >= minlen:
                out.append((start, i - 1))
            cur = 0
    if cur >= minlen:
        out.append((start, len(v) - 1))
    return out

def find_axis_row(g, x0, x1, th=170, minlen=100):
    """fila del eje x: run horizontal largo en el rango x0..x1"""
    best = None
    for y in range(g.shape[0]):
        for (a, b) in runs_1d(g[y, x0:x1] < th, minlen):
            ln = b - a + 1
            if best is None or ln > best[0]:
                best = (ln, y, a + x0, b + x0)
    return best

def find_axis_col(g, y0, y1, th=170, minlen=100):
    best = None
    for x in range(g.shape[1]):
        for (a, b) in runs_1d(g[y0:y1, x] < th, minlen):
            ln = b - a + 1
            if best is None or ln > best[0]:
                best = (ln, x, a + y0, b + y0)
    return best

def find_ticks_x(g, y_axis, x_a, x_b, th=170, probe=5):
    """ticks en eje x: protrusiones verticales debajo de y_axis"""
    ticks = []
    for x in range(x_a, x_b + 1):
        col = g[y_axis + 1:y_axis + 1 + probe, x]
        below = np.sum(col < th)
        col2 = g[y_axis - probe:y_axis, x]
        above = np.sum(col2 < th)
        if below >= 2 or above >= 2:
            ticks.append(x)
    # agrupar consecutivos
    groups = []
    for x in ticks:
        if groups and x - groups[-1][-1] <= 2:
            groups[-1].append(x)
        else:
            groups.append([x])
    return [int(np.mean(g)) for g in groups]

def find_ticks_y(g, x_axis, y_a, y_b, th=170, probe=6):
    """ticks en eje y: protrusiones horizontales a la derecha de x_axis"""
    ticks = []
    for y in range(y_a, y_b + 1):
        rowl = g[y, x_axis + 1:x_axis + 1 + probe]
        right = np.sum(rowl < th)
        rowl2 = g[y, x_axis - probe:x_axis]
        left = np.sum(rowl2 < th)
        if right >= 2 or left >= 2:
            ticks.append(y)
    groups = []
    for y in ticks:
        if groups and y - groups[-1][-1] <= 2:
            groups[-1].append(y)
        else:
            groups.append([y])
    return [int(np.mean(g)) for g in groups]

g2 = load('fig2_eta_vs_xb.png')
g4 = load('fig4_eta_vs_P.png')

print('=== FIG2 ===')
# Panel a: buscar eje x en x 80..500, eje y en y 20..270
for tag, xs, ys in [('a', (80, 500), (20, 270)), ('b', (600, 1030), (20, 270)), ('c', (330, 750), (370, 620))]:
    ax = find_axis_row(g2, xs[0], xs[1])
    ay = find_axis_col(g2, ys[0], ys[1])
    print('panel', tag, 'eje x:', ax, ' e.je y:', ay)
    if ax:
        t = find_ticks_x(g2, ax[1], max(ax[2], xs[0]), min(ax[3], xs[1]))
        print('  ticks x (protuberancia bajo eje):', t)
    if ay:
        t = find_ticks_y(g2, ay[1], max(ay[2], ys[0]), min(ay[3], ys[1]))
        print('  ticks y:', t)

print('=== FIG4 ===')
ax = find_axis_row(g4, 40, 520)
ay = find_axis_col(g4, 0, 340)
print('eje x:', ax, ' eje y:', ay)
if ax:
    print('  ticks x:', find_ticks_x(g4, ax[1], max(ax[2], 40), min(ax[3], 520)))
if ay:
    print('  ticks y:', find_ticks_y(g4, ay[1], max(ay[2], 0), min(ay[3], 340)))