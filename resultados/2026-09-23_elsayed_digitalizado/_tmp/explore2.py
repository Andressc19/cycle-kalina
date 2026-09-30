# -*- coding: utf-8 -*-
"""Exploracion 2: bordes exactos del plot, ticks de ambos ejes.""" 
import os
import numpy as np
from PIL import Image

REF = r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013\fig4_eta_vs_P.png'
a = np.asarray(Image.open(REF).convert('L'))
H, W = a.shape
dark = a < 128

# --- borde horizontal (filas): columna con muchos px oscuros de corrido ---
def runs(v, gap=2, minh=3):
    out, s, last = [], None, None
    for i, val in enumerate(v):
        if val:
            if s is None:
                s = i
            last = i
        elif s is not None and i - last > gap:
            if last - s + 1 >= minh:
                out.append((s, last))
            s = last = None
    if s is not None and last - s + 1 >= minh:
        out.append((s, last))
    return out

# filas que son "lintas full-width": >= 400 px oscuros
full_rows = [y for y in range(H) if dark[y].sum() >= 400]
print('full-width rows:', full_rows)

# columnas full-height: >= 250 px oscuros
full_cols = [x for x in range(W) if dark[:, x].sum() >= 250]
print('full-height cols:', full_cols)

# --- ticks eje x: en la banda de filas justo arriba de la linea inferior ---
# buscar en filas desde bottom-8 hasta bottom-1 ... primero localizar linea inferior exacta
bottom_cands = []
for y in range(H - 1, 0, -1):
    r = runs(dark[y, :])
    longest = max((b - a for a, b in r), default=0)
    if longest > 400:
        bottom_cands.append((y, longest, len(r)))
print('\nfilas candidatas a linea x-axis (desde abajo):')
for c in bottom_cands[:12]:
    print(c)