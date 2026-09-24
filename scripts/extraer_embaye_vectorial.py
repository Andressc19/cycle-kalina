# -*- coding: utf-8 -*-
"""Extraccion vectorial de las curvas de Embaye et al. (KCS11, PDF vectorial).
Pag 4: Figs 2-5 (eta vs x_NH3, 0.2-1.0; T_sum 283 K); pag 5: Fig 7 (eta vs P_evap 0-35 bar).
Todo dato sale de get_drawings()/get_text(); el control 11.38 % (KCS11 0.55 @15 bar) NO
calibra ni identifica, solo se verifica.
Uso: .venv/Scripts/python.exe scripts/extraer_embaye_vectorial.py"""
import os, csv
import numpy as np
import pymupdf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

PDF = r'D:\Desktop\ciclo_kalina_tercero\PERFORMANCEOFKALINACYCLESYSTEM11KCS11USINGLOWTEMPERATUREHEATSOURCES.pdf'
OUT = r'D:\Desktop\ciclo_kalina_tercero\resultados\2026-09-24_embaye_vectorial'
CTRL = 11.38
GRAY = (0.5253909826278687,) * 3
BLK, RED, GRN, BLU = (0, 0, 0), (1, 0, 0), (0, 0.689453, 0.313721), (0, 0, 1)
P4 = {'Fig2': (128.2, 130.6, 282.8, 224.2), 'Fig3': (333.0, 130.6, 487.0, 224.0),
      'Fig4': (128.2, 319.4, 282.6, 412.8), 'Fig5': (333.3, 319.4, 486.9, 413.0)}
PEV = {'Fig2': 10, 'Fig3': 15, 'Fig4': 23.5, 'Fig5': 32}
TCOL = {'Fig2': {BLU: 333, RED: 373, GRN: 423}, 'Fig3': {BLU: 333, RED: 373, GRN: 423},
        'Fig4': {RED: 373, GRN: 423, BLK: 463}, 'Fig5': {RED: 373, GRN: 423, BLK: 463}}
FIG7 = (222.0, 341.0, 426.5, 465.5)
C66, C55 = 'KCS11(Con.=0.66)', 'KCS11(Con.=0.55)'
ONH3, OR134 = 'ORC(Ammonia)', 'ORC(R134a)'
CC = {C66: '#1f77b4', C55: '#d62728', ONH3: '#2ca02c', OR134: '#ff7f0e', BLU: '#1f77b4',
      RED: '#d62728', GRN: '#2ca02c', BLK: '#000000'}
os.makedirs(OUT, exist_ok=True)

def inside(b, r):
    x0, y0, x1, y1 = (b.x0, b.y0, b.x1, b.y1) if hasattr(b, 'x0') else b
    return x0 >= r[0] and y0 >= r[1] and x1 <= r[2] and y1 <= r[3]

def chain_pts(d):
    """Puntos sobre la curva de un trazo (extremos 'l', fin de 'c'), sin duplicados
    consecutivos; los controles de la bezier no estan en la curva."""
    p = []
    for it in d['items']:
        if it[0] == 'l':
            qs = (it[1], it[2])
        elif it[0] == 'c':
            qs = (it[3],)
        else:
            continue
        for q in qs:
            q = tuple(q)
            if not p or p[-1] != q:
                p.append(q)
    return p

def centerline(d):
    """Linea central de un contorno CERRADO (banda): emparejamiento simetrico de la
    polilinea; si el trazo es una polilinea abierta se usa tal cual."""
    p = chain_pts(d)
    p0, p1 = p[0], p[-1]
    if (p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2 > 2.0:
        return p
    n = len(p) // 2
    return [((p[i][0] + p[-1 - i][0]) / 2, (p[i][1] + p[-1 - i][1]) / 2) for i in range(n)]

def dash_centers(d, gap=4.5):
    """Centroide de cada trazo de una linea discontinua: cada trazo es un contorno
    cerrado y los consecutivos quedan separados por un salto > gap pt (internos <= 4)."""
    p = chain_pts(d)
    chunks, cur = [], [p[0]]
    for i in range(1, len(p)):
        if (p[i][0] - p[i - 1][0]) ** 2 + (p[i][1] - p[i - 1][1]) ** 2 > gap ** 2:
            chunks.append(np.array(cur).mean(axis=0))
            cur = [p[i]]
        else:
            cur.append(p[i])
    chunks.append(np.array(cur).mean(axis=0))
    return [tuple(np.round(np.asarray(c), 3)) for c in chunks]

def calibrate(region, draws, spans):
    """Ajuste lineal pdf->dato con las marcas EXTREMAS de cada eje (de las etiquetas
    de ticks), error maximo contra todas las etiquetas intermedias."""
    R = (region[0] - 4, region[1] - 4, region[2] + 4, region[3] + 4)
    cands = [d for d in draws if d['fill'] == GRAY and inside(d['rect'], R)]
    xax = max((d for d in cands if d['rect'].height < 3 and d['rect'].width > 50),
              key=lambda d: len(d['items']))
    yax = max((d for d in cands if d['rect'].width < 3 and d['rect'].height > 50),
              key=lambda d: len(d['items']))
    cal, msg = {}, []
    for key, axd, vert in (('x', xax, False), ('y', yax, True)):
        ax = axd['rect']
        pair = []
        for w in spans:
            b = w['bbox']
            try:
                v = float(w['text'].strip())
            except ValueError:
                continue
            if not 0 <= v <= 40:
                continue
            cy = (b[1] + b[3]) / 2
            if vert and ax.x0 - 14 < b[0] and b[2] < ax.x0 + 6 and cy <= xax['rect'].y0 + 4 and ax.y0 - 25 <= cy <= ax.y1 + 25:
                pair.append((cy, v))
            elif not vert and ax.y0 + 3 < b[1] < ax.y0 + 16 and ax.x0 - 30 <= (b[0] + b[2]) / 2 <= ax.x1 + 30:
                pair.append(((b[0] + b[2]) / 2, v))
        pair.sort(key=lambda p: p[0])
        xs = [p[0] for p in pair]
        vs = [p[1] for p in pair]
        a = (vs[-1] - vs[0]) / (xs[-1] - xs[0])
        b0 = vs[0] - a * xs[0]
        assert max(abs(b0 + a * x - v) for x, v in pair) < 0.6, 'etiqueta no alineada eje %s' % key
        cal[key] = dict(a=a, b=b0, err=float(max(abs(b0 + a * x - v) for x, v in pair)))
        msg.append('  %s: %d etiquetas, max err %.4g' % (key, len(pair), cal[key]['err']))
    return cal, '\n'.join(msg)

def inv(cal, key, v):
    return cal[key]['a'] * v + cal[key]['b']

def series_p4(region, draws, colmap):
    ser = {}
    for d in draws:
        b, f, n = d['rect'], d['fill'], len(d['items'])
        if f is None:
            continue
        f = tuple(round(c, 6) for c in f)
        if not inside(b, region) or n < 40 or f not in colmap:
            continue
        ser[f] = centerline(d)
    return ser

def dist2(polys, pt):
    return min(np.min(np.sum((np.array(p) - pt) ** 2, axis=1)) for p in polys)

def eta_at(pts, x):
    xs = [p[0] for p in pts]
    i = int(np.clip(np.searchsorted(xs, x), 1, len(pts) - 1))
    p0, p1 = pts[i - 1], pts[i]
    return p0[1] if p0[0] == p1[0] else p0[1] + (x - p0[0]) * (p1[1] - p0[1]) / (p1[0] - p0[0])

def dump(name, fields, conv=None):
    with open(os.path.join(OUT, name), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            if fields[0] in r:
                w.writerow(conv(r) if conv else r)

def audit(page, over, fname, title):
    pix = page.get_pixmap(dpi=150)
    img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
    fig, ax = plt.subplots(figsize=(8.2, 10.8))
    ax.imshow(img)
    s = 150 / 72
    for cal, serie in over:
        for nm, (pts, col) in serie.items():
            ax.plot([inv(cal, 'x', x) * s for x, y in pts], [inv(cal, 'y', y) * s for x, y in pts], '.', ms=2.4, color=col)
    ax.set_title(title)
    ax.axis('off')
    fig.savefig(os.path.join(OUT, fname), dpi=120)
    plt.close(fig)

doc = pymupdf.open(PDF)
p4, p5 = doc[3], doc[4]
d4, d5 = p4.get_drawings(), p5.get_drawings()
sp4 = [w for b in p4.get_text('dict')['blocks'] if 'lines' in b for l in b['lines'] for w in l['spans']]
sp5 = [w for b in p5.get_text('dict')['blocks'] if 'lines' in b for l in b['lines'] for w in l['spans']]
rows, report = [], []

for fig, reg in P4.items():
    if not any(str(PEV[fig]) in w['text'] for w in sp4 if inside(w['bbox'], reg)):
        report.append('ADVERTENCIA: Fig %s sin anotacion Evaporator Pressure' % fig)
    cal, msg = calibrate(reg, d4, sp4)
    report.append('## %s (P_evap=%g bar, eje y 0-%d)' % (fig, PEV[fig], 18 if fig != 'Fig2' else 16))
    report.append(msg)
    for col, Tf in TCOL[fig].items():
        cl = series_p4(reg, d4, {col: Tf})[col]
        pts = sorted(set((round(inv(cal, 'x', x), 6), round(inv(cal, 'y', y), 6)) for x, y in cl))
        rows += [dict(figura=fig, P_evap_bar=PEV[fig], T_fuente_K=Tf, x_b_masica=p[0], eta_pct=p[1])
                 for p in pts]
        ym = max(pts, key=lambda p: p[1])
        report.append('  - T=%g K: n=%d, x [%.3f, %.3f], eta [%.3f, %.3f] %% (max en x=%.3f)'
                      % (Tf, len(pts), pts[0][0], pts[-1][0], min(y for _, y in pts), ym[1], ym[0]))

report.append('## Fig7 (eta vs P_evap 0-35 bar, eje y 0-20, T_fuente 373 K)')
cal7, msg7 = calibrate(FIG7, d5, sp5)
report.append(msg7)
dr = [d for d in d5 if d['fill'] == BLK and inside(d['rect'], FIG7)]
dash = [d for d in dr if 100 <= len(d['items']) <= 250 and d['rect'].width > 60 and d['rect'].height < 55]
band = [d for d in dr if 25 <= len(d['items']) <= 80 and d['rect'].width > 100 and d['rect'].height > 30]
mark = [d for d in dr if 10 <= len(d['items']) <= 25 and 3 < d['rect'].width < 7 and d['rect'].x0 > 250]
assert len(dash) == len(band) == 2, 'Fig7 dash=%d band=%d' % (len(dash), len(band))
# mas items = KCS11 0.66 (sigue subiendo tras ~20 bar, valores tipo R134a); 0.55 cae
d66, d55 = sorted(dash, key=lambda d: len(d['items']), reverse=True)
bR134, bNH3 = sorted(band, key=lambda d: d['rect'].y0)
s7, nmark, maxsep, polys = {}, {}, {}, []
for name, line in ((C66, d66), (C55, d55), (OR134, bR134), (ONH3, bNH3)):
    cl = dash_centers(line) if line in (d66, d55) else centerline(line)
    pts = sorted(set((round(inv(cal7, 'x', x), 6), round(inv(cal7, 'y', y), 6)) for x, y in cl))
    s7[name] = pts
    xb = {'KCS11(Con.=0.66)': 0.66, 'KCS11(Con.=0.55)': 0.55}.get(name, np.nan)
    rows += [dict(curva=name, x_b_masica=xb, P_evap_bar=p[0], eta_pct=p[1]) for p in pts]
    ym = max(pts, key=lambda p: p[1])
    nmark[name], maxsep[name], polys = 0, 0.0, polys + [cl]
    report.append('  - %s: n=%d, P [%.3f, %.3f], eta [%.3f, %.3f] %% (max en %.3f bar)'
                  % (name, len(pts), pts[0][0], pts[-1][0], min(y for _, y in pts), ym[1], ym[0]))
for m in mark:  # marcadores: solo corroboracion (conteo y separacion)
    c = np.array(chain_pts(m)).mean(axis=0)
    i = int(np.argmin([dist2([p], c) for p in polys]))
    name = (C66, C55, OR134, ONH3)[i]
    nmark[name] += 1
    maxsep[name] = max(maxsep[name], float(np.sqrt(dist2([polys[i]], c))))
report += ['    marcadores: %d, max sep %.4g pt' % (nmark[n], maxsep[n]) for n in s7 if nmark[n]]

e55, eO1, eO2 = eta_at(s7[C55], 15.0), eta_at(s7[ONH3], 15.0), eta_at(s7[OR134], 15.0)
report.append('## Controles (informativos)\n  - KCS11 Con.=0.55 a 15 bar: extraido %.3f %%, texto del '
              'paper 11.38 %% (dif %.3f pp)' % (e55, e55 - CTRL))
if eO1:
    report.append('  - ORC(Ammonia) a 15 bar: extraido %.3f %% (texto ~7 %%)' % eO1)
if eO2:
    report.append('  - ORC(R134a) a 15 bar: extraido %.3f %% (texto ~9.2 %%)' % eO2)

dump('curvas_embaye_eta_vs_xb.csv', ['figura', 'P_evap_bar', 'T_fuente_K', 'x_b_masica', 'eta_pct'])
dump('curvas_embaye_fig7.csv', ['curva', 'x_b_masica', 'P_evap_bar', 'eta_pct'],
     lambda r: dict(r, x_b_masica='' if np.isnan(r['x_b_masica']) else r['x_b_masica']))

over4 = []
for fig, reg in P4.items():
    cal, _ = calibrate(reg, d4, sp4)
    over4.append((cal, {'%s %gK' % (fig, Tf): ([(inv(cal, 'x', x), inv(cal, 'y', y)) for x, y in
                                                series_p4(reg, d4, {col: Tf})[col]], CC[col])
                        for col, Tf in TCOL[fig].items()}))
audit(p4, over4, 'auditoria_pag4.png', 'Pag 4 - puntos extraidos sobre el PDF')
audit(p5, [(cal7, {k: (v, CC[k]) for k, v in s7.items()})], 'auditoria_pag5.png', 'Pag 5 Fig7 - puntos extraidos sobre el PDF')

report.insert(0, '# Reporte de extraccion vectorial - Embaye et al. (KCS11)\n\n' +
    'Metodo: curvas como bandas de relleno (trazo) en get_drawings(); linea central por ' +
    'emparejamiento simetrico de cada contorno cerrado (en discontinuas: centroide de cada trazo). ' +
    'Calibracion pdf->dato con las marcas EXTREMAS de las etiquetas de ticks de cada eje, error max ' +
    'contra las etiquetas intermedias (reportado). Series por leyenda: Figs 2-3 azul/rojo/verde = ' +
    '333/373/423 K; Figs 4-5 rojo/verde/negro = 373/423/463 K (463 K es banda negra; cajas de ' +
    'leyenda/anotaciones <=20 items se excluyen, bandas de datos >=40). Fig 7: rombos grises (n=3) ' +
    'de la cola de KCS11 0.55 son duplicados sombra de los negros y se excluyen; los marcadores ' +
    'solo corroboran (conteo y separacion).\n')
with open(os.path.join(OUT, 'REPORTE_EXTRACCION.md'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(report) + '\n\nCita: Embaye, M., AL-Dadah, R., Mahmoud, S., Elsayed, A., '
            '& Rezk, A., "Performance of Kalina Cycle System 11 (KCS11) using low temperature '
            'heat sources", University of Birmingham (version de congreso; modelo de Elsayed et '
            'al. 2013, IJLCT 8(suppl_1) i69-i78).\n')
print('\n'.join(report))
print('Control KCS11 0.55 @15 bar = %.3f %% (esperado 11.38)' % e55)
print('Salidas en', OUT)