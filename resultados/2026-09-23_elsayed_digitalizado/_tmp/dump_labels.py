# -*- coding: utf-8 -*-
"""Dumps ASCII con regla de coordenadas para las zonas de etiquetas de ejes."""
import numpy as np
from PIL import Image

fig2 = np.asarray(Image.open(r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013\fig2_eta_vs_xb.png').convert('L'))
fig4 = np.asarray(Image.open(r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013\fig4_eta_vs_P.png').convert('L'))

def ruler(x0, x1):
    s = []
    scale = 5
    for x in range(x0, x1):
        if x % 10 == 0:
            s.append(str((x // 10) % 10))
        elif x % 5 == 0:
            s.append('^')
        else:
            s.append(' ')
    return ''.join(s)

def dump(g, x0, x1, y0, y1, th=185, step=1):
    print('x %d..%d, y %d..%d' % (x0, x1, y0, y1))
    print('    ' + ruler(x0, x1))
    for y in range(y0, y1):
        s = ''
        for x in range(x0, x1):
            v = g[y, x]
            s += '#' if v < th else ('+' if v < th + 50 else '.')
        print('%4d|%s|' % (y, s))
    print()

# fig2(b) etiquetas x: banda y=284..293 detectada
#dump(fig2, 610, 1030, 280, 296, 185, 1)
# Ajustar: buscar filas con texto en x amplio
print('########## fig2(b) etiquetas x (candidata y=284..293) ##########')
dump(fig2, 610, 1029, 283, 295, 185)

print('########## fig2(b) etiquetas x (intento y=260..275) ##########')
dump(fig2, 610, 1029, 258, 276, 185)

print('########## fig2(c) etiquetas x (y=638..647) ##########')
dump(fig2, 300, 760, 634, 650, 185)

print('########## fig4 etiquetas x (y=286..312) ##########')
dump(fig4, 40, 522, 284, 312, 185)