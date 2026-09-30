# -*- coding: utf-8 -*-
"""Zoom fino de la barra vertical y areas clave."""
import os
import numpy as np
from PIL import Image

REF = r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013'
TMP = r'D:\Desktop\ciclo_kalina_tercero\resultados\2026-09-23_elsayed_digitalizado\_tmp'

def load(name):
    return np.asarray(Image.open(os.path.join(REF, name)).convert('L'))

def ascii_1x1(g, x0, x1, y0, y1, th_hi=90, th_mid=180):
    out = []
    for y in range(y0, min(y1, g.shape[0])):
        row = []
        for x in range(x0, min(x1, g.shape[1])):
            v = g[y, x]
            row.append('#' if v < th_hi else ('+' if v < th_mid else '.'))
        out.append('%4d %s' % (y, ''.join(row)))
    return '\n'.join(out)

g2 = load('fig2_eta_vs_xb.png')

# 1. barra vertical x 20..70, y 30..230
txt = ascii_1x1(g2, 20, 70, 30, 230)
with open(os.path.join(TMP, 'zoom_barra.txt'), 'w', encoding='utf-8') as f:
    f.write(txt)
print('barra lines', txt.count(chr(10)) + 1)

# 2. zona leyenda panel a: x 90..260, y 20..120
txt = ascii_1x1(g2, 90, 260, 20, 120)
with open(os.path.join(TMP, 'zoom_leyenda_a.txt'), 'w', encoding='utf-8') as f:
    f.write(txt)
print('leyenda_a lines', txt.count(chr(10)) + 1)

# 3. eje x central de panel a: x 100..500, y 255..295
txt = ascii_1x1(g2, 100, 500, 255, 295)
with open(os.path.join(TMP, 'zoom_ejex_a.txt'), 'w', encoding='utf-8') as f:
    f.write(txt)
print('ejex_a lines', txt.count(chr(10)) + 1)

# 4. esquina superior izquierda completa con titulo claro: x 0..120, y 0..50
txt = ascii_1x1(g2, 0, 120, 0, 50)
with open(os.path.join(TMP, 'zoom_esquina.txt'), 'w', encoding='utf-8') as f:
    f.write(txt)
print('esquina lines', txt.count(chr(10)) + 1)