# -*- coding: utf-8 -*-
"""Digitaliza Fig.2 y Fig.4 de Elsayed et al. (2013) desde los PNG extraidos de
ctt020.pdf (reference/elsayed2013/). Curvas por pixeles en escala de grises.
Salidas en resultados/2026-09-23_elsayed_digitalizado/. El punto de control
(11.38 % a 15 bar, x_b=0.55) solo se verifica, no ajusta nada.
Uso: .venv/Scripts/python.exe scripts/digitalizar_elsayed2013.py
"""
import os
import numpy as np
from PIL import Image, ImageDraw

REF = r'D:\Desktop\ciclo_kalina_tercero\reference\elsayed2013'
OUT = r'D:\Desktop\ciclo_kalina_tercero\resultados\2026-09-23_elsayed_digitalizado'
os.makedirs(OUT, exist_ok=True)
CTRL = 11.38  # % (KCS11 x_b=0.55, 15 bar, 373/283 K), texto literal del paper

# CALIBRACION: FIG.4 x "0"@50,"35"@509 -> P=(x-50)*5/67; y tick "15"@58 ->
# eta=17.913-0.05022*y (eje truncado 5..15%). FIG.2 (a)(b)(c) 333/373/423 K:
# f=(x-xf)/515 y eta=(y0-e*y)/s# con etiquetas ["0.2"@72,"0.8"@381] etc.
FIG4 = dict(img='fig4_eta_vs_P.png', box=(29, 517, 9, 272), th=150, mg=(26, 10),
            ppy=lambda y: 17.913 - 0.05022 * y, ppx=lambda x: (x - 50) * 5 / 67.0,
            zap=[(0, 240, 8, 105), (54, 196, 234, 272)])
FIG2 = {
    'a': dict(img='fig2_eta_vs_xb.png', T=333, box=(70, 500, 12, 270), th=185, mg=(60, 8),
              pres=[10, 15, 20], xref=278, ctrl=None,
              fx=lambda x: (x + 31) / 515.0, fxo=lambda f: 515 * f - 31,
              ey=lambda y: (273.0 - y) / 21.0, eyo=lambda e: 273 - 21 * e,
              zap=[(94, 245, 27, 100), (95, 235, 203, 246)]),
    'b': dict(img='fig2_eta_vs_xb.png', T=373, box=(641, 975, 12, 270), th=185, mg=(60, 8),
              pres=[10, 15, 25], xref=810,
              ctrl=(515 * 0.55 + 501, 271.7 - 11.38 * 13.9, 8.0), sep=3.0,
              fx=lambda x: (x - 501) / 515.0, fxo=lambda f: 515 * f + 501,
              ey=lambda y: (271.7 - y) / 13.9, eyo=lambda e: 271.7 - 13.9 * e,
              zap=[(624, 716, 20, 240), (625, 815, 200, 248)]),
    'c': dict(img='fig2_eta_vs_xb.png', T=423, box=(300, 900, 362, 620), th=185, mg=(60, 8),
              pres=[10, 15, 25, 30], xref=529, ctrl=None,
              fx=lambda x: (x - 220) / 515.0, fxo=lambda f: 515 * f + 220,
              ey=lambda y: (628.5 - y) / 10.1, eyo=lambda e: 628.5 - 10.1 * e,
              zap=[(325, 440, 348, 448), (330, 470, 560, 615)]),
}


def load(d):
    a = np.asarray(Image.open(os.path.join(REF, d['img'])).convert('L'))
    return a, a < d['th']


def runs(col, gap=5, minh=2):
    out, s, last = [], None, None
    for i, v in enumerate(col):
        if v:
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


def zap(m, x0, x1, y0, y1):
    m[max(y0, 0):y1, max(x0, 0):x1] = False


def extract(m, x0, x1, y0, y1, tol=8):
    streams = []
    for x in range(x0, x1 + 1):
        for (ya, yb) in runs(m[y0:y1 + 1, x]):
            c = (ya + yb) / 2.0 + y0
            best, bd = None, tol + 1
            for s in streams:
                if s['xs'][-1] in (x - 1, x - 2) and abs(s['ys'][-1] - c) < bd:
                    bd, best = abs(s['ys'][-1] - c), s
            if best is not None:
                best['xs'].append(x)
                best['ys'].append(c)
            else:
                streams.append({'xs': [x], 'ys': [c]})
    return streams


def merge(sl, dx, dy):
    changed = True
    while changed:
        changed = False
        for i in range(len(sl)):
            for j in range(len(sl)):
                if i == j:
                    continue
                a, b = sl[i], sl[j]
                if 0 < b['xs'][0] - a['xs'][-1] <= dx and abs(b['ys'][0] - a['ys'][-1]) <= dy:
                    a['xs'] += b['xs']
                    a['ys'] += b['ys']
                    sl.pop(j)
                    changed = True
                    break
            if changed:
                break
    return sl


def fuse(sl, dymax=6):
    """Funde trazos paralelos (bordes de una curva gruesa) en su centro."""
    changed = True
    while changed:
        changed = False
        for i in range(len(sl)):
            for j in range(i + 1, len(sl)):
                a, b = sl[i], sl[j]
                lo, hi = max(a['xs'][0], b['xs'][0]), min(a['xs'][-1], b['xs'][-1])
                if hi - lo < 10:
                    continue
                d1 = np.array([vat(a, x) for x in range(lo, hi + 1)])
                d2 = np.array([vat(b, x) for x in range(lo, hi + 1)])
                if np.mean(np.abs(d1 - d2)) <= dymax:
                    xs = sorted(set(a['xs']) | set(b['xs']))
                    ymap = {}
                    for x in xs:
                        vals = [v for (s2, v) in ((a, vat(a, x)), (b, vat(b, x)))
                                if s2['xs'][0] <= x <= s2['xs'][-1]]
                        ymap[x] = float(np.mean(vals))
                    a['xs'], a['ys'] = xs, [ymap[x] for x in xs]
                    sl.pop(j)
                    changed = True
                    break
            if changed:
                break
    return sl


def vat(s, x):
    xs, ys = s['xs'], s['ys']
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    i = int(np.searchsorted(xs, x)) - 1
    x0, x1, y0, y1 = xs[i], xs[i + 1], ys[i], ys[i + 1]
    return y0 if x1 == x0 else y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def streams_of(d, minlen, tol=8):
    a, b = load(d)
    m = b.copy()
    x0, x1, y0, y1 = d['box']
    m[:y0, :] = False
    m[y1:, :] = False
    m[:, :x0] = False
    m[:, x1:] = False
    for z in d['zap']:
        zap(m, *z)
    return [s for s in fuse(merge(extract(m, x0, x1, y0, y1, tol), *d['mg']))
            if len(s['xs']) >= minlen]


def write_csv(path, header, rows):
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        fh.write(header + '\n')
        for r in rows:
            fh.write(','.join('' if v is None else str(round(v, 3) if isinstance(v, float) else v)
                              for v in r) + '\n')


def overlay(src, dst, curves):
    im = Image.open(os.path.join(REF, src)).convert('RGB')
    dr = ImageDraw.Draw(im)
    pal = ['#ff0018', '#009933', '#0033ff', '#cc7700', '#9a00d4', '#008899', '#ff6600', '#555555']
    for k, (name, pts) in enumerate(curves):
        col = pal[k % len(pal)]
        for (px, py) in pts:
            dr.ellipse([px - 2, py - 2, px + 2, py + 2], fill=col)
        if pts:
            dr.text((max(pts[0][0] - 4, 0), max(pts[0][1] - 13, 0)), name, fill=col)
    im.save(dst)


def out_rows(rows, path):
    tag = os.path.splitext(os.path.basename(path))[0].split('_')[1]
    write_csv(path, {
        'fig4': 'curva,x_b_masica,P_evap_bar,eta_pct,metodo',
        'fig2': 'panel,T_fuente_K,P_evap_bar,x_b_masica,eta_pct,metodo'}[tag], rows)
    return rows


def named_sets(fig, sl, assign):
    """Puntos (P, eta) por nombre a partir de streams ya etiquetados."""
    out = {}
    for s in sl:
        nm = assign.get(id(s))
        if nm is None:
            continue
        for x in s['xs']:
            out.setdefault(nm, []).append((fig['ppx'](x), fig['ppy'](vat(s, x))))
    return {k: sorted(v) for k, v in out.items()}


def fit_eta(fig, sets, name, P):
    pts = sets.get(name)
    if not pts:
        return None
    xs = [p[0] for p in pts]
    if P <= xs[0] or P >= xs[-1]:
        n = min(4, len(pts))
        a, b2 = np.polyfit(xs[-n:], [p[1] for p in pts][-n:], 1)
        return float(a * P + b2)
    return float(np.interp(P, xs, [p[1] for p in pts]))


def main():
    extra, r_fig4, r_fig2, ov4, ov2 = [], [], [], [], []
    # ---------------- FIG. 4 ----------------
    d = FIG4
    targets = [(11.38, 'KCS11', 0.55), (8.13, 'ORC-NH3', None)]
    sl = streams_of(d, 26, tol=5)
    assign = {}
    seen = set()
    for s in sl:
        if not (s['xs'][0] <= 251 <= s['xs'][-1]):
            continue
        eta, cont = d['ppy'](vat(s, 251)), (len(s['xs']) - 1) / max(1, s['xs'][-1] - s['xs'][0])
        t = min(targets, key=lambda tt: abs(eta - tt[0]))
        if abs(eta - t[0]) <= 0.5 and t[1] not in seen:
            assign[id(s)] = (t[1], t[2])
            seen.add(t[1])
        elif 9.3 <= eta <= 10.2:
            assign[id(s)] = ('ORC-R134a', None) if cont < 0.85 else ('KCS11', 0.66)
    sets = named_sets(d, sl, assign)
    for s in sl:
        idf, xb = assign.get(id(s)) or (None, None)
        if idf is None:
            P0 = d['ppx'](s['xs'][0])
            cand = [(nm[0] if isinstance(nm, tuple) else nm,
                     abs((fit_eta(d, sets, nm, P0) or 99) - d['ppy'](s['ys'][0])))
                    for nm in sets]
            idf = min(cand, key=lambda t: t[1])[0] if cand and min(t[1] for t in cand) <= 0.8 \
                else 'curva_no_identificada'
        P0, Pn = d['ppx'](s['xs'][0]), d['ppx'](s['xs'][-1])
        pts, rows = [], []
        for P in np.arange(np.ceil(P0), np.floor(Pn) + 0.51, 1.0):
            px = 50 + P * 67 / 5.0
            eta = d['ppy'](vat(s, px))
            rows.append((idf, xb, round(P, 1), round(eta, 2),
                         'trazo_continuo' if idf != 'curva_no_identificada' else 'dudoso'))
            pts.append((px, (17.913 - round(eta, 2)) / 0.05022))
        if rows:
            r_fig4 += rows
            ov4.append((idf if xb is None else '%s-%s' % (idf, xb), pts))
            extra.append('FIG4 %-14s x=%s  P %4.1f..%4.1f bar  n=%d' %
                         (idf, '' if xb is None else xb, rows[0][2], rows[-1][2], len(rows)))
    out_rows(r_fig4, os.path.join(OUT, 'elsayed2013_fig4.csv'))
    overlay('fig4_eta_vs_P.png', os.path.join(OUT, 'overlay_fig4.png'), ov4)
    kc = [r for r in r_fig4 if r[0] == 'KCS11' and r[1] == 0.55 and r[2] == 15.0]
    eta15 = kc[0][3] if kc else float('nan')
    print('FIG4 KCS11 x_b=0.55 @15 bar -> eta=%.2f %% (control 11.38, delta %.2f pp)' % (eta15, eta15 - CTRL))
    # ---------------- FIG. 2 ----------------
    for tag, d2 in FIG2.items():
        sl = streams_of(d2, 14)
        ranked = sorted(sl, key=lambda s: vat(s, d2['xref']))
        labels = [d2['pres'][i] if i < len(d2['pres']) else None for i in range(len(ranked))]
        if d2['ctrl'] is not None:
            cx, cy, ctol = d2['ctrl']
            cands = [(s, abs(vat(s, cx) - cy)) for s in ranked if abs(vat(s, cx) - cy) <= ctol]
            if cands:
                cs = min(cands, key=lambda t: t[1])[0]
                i15 = labels.index(15)
                k = ranked.index(cs)
                if k != i15:
                    labels[k], labels[i15] = labels[i15], labels[k]
                    extra.append('FIG2 %s: control 15 bar sobre curva #%d (dist %.1f px)' % (tag, k, min(t[1] for t in cands)))
                if d2.get('sep'):  # descartar trazos indistinguibles de la curva de control
                    eta_c = d2['ey'](vat(cs, d2['xref']))
                    excl = set()
                    for i, s in enumerate(ranked):
                        if s is not cs and labels[i] is not None \
                                and abs(d2['ey'](vat(s, d2['xref'])) - eta_c) < d2['sep']:
                            labels[i] = None
                            excl.add(id(s))
                    rest = [p for p in d2['pres'] if p != 15]
                    for i, s in enumerate(ranked):
                        if id(s) not in excl and s is not cs and labels[i] is None and rest:
                            labels[i] = rest.pop(0)
            else:
                extra.append('FIG2 %s: ninguna curva pasa por el punto de control 15 bar' % tag)
        for s, Pbar in zip(ranked, labels):
            if Pbar is None:
                extra.append('FIG2 %s: curva sin asignar -> curva_no_identificada' % tag)
                continue
            f0, fn = d2['fx'](s['xs'][0]), d2['fx'](s['xs'][-1])
            pts, rows = [], []
            for f in np.arange(np.ceil(f0 * 20) / 20, min(np.floor(fn * 20) / 20, 1.0) + 0.026, 0.05):
                px = d2['fxo'](f)
                eta = d2['ey'](vat(s, px))
                metodo = 'trazo_continuo' if s['xs'][-1] - s['xs'][0] >= 60 else 'dudoso'
                rows.append((tag, d2['T'], Pbar, round(f, 2), round(eta, 2), metodo))
                pts.append((px, d2['eyo'](round(eta, 2))))
            if rows:
                r_fig2 += rows
                ov2.append(('%s-%dbar' % (tag, Pbar), pts))
                extra.append('FIG2 %s P=%2d bar  f %4.2f..%4.2f  n=%3d' %
                             (tag, Pbar, rows[0][3], rows[-1][3], len(rows)))
    out_rows(r_fig2, os.path.join(OUT, 'elsayed2013_fig2.csv'))
    overlay('fig2_eta_vs_xb.png', os.path.join(OUT, 'overlay_fig2.png'), ov2)
    b15 = [r for r in r_fig2 if r[0] == 'b' and r[2] == 15 and r[3] == 0.55]
    e15 = b15[0][4] if b15 else float('nan')
    print('FIG2b 15 bar @x_b=0.55 -> eta=%.2f %% (control 11.38, delta %.2f pp)' % (e15, e15 - CTRL))
    with open(os.path.join(OUT, 'REPORTE_DIGITALIZACION.md'), 'w', encoding='utf-8') as fh:
        fh.write(reporte_md(r_fig4, r_fig2, extra, eta15, e15))
    print('OK  fig4=%d pts  fig2=%d pts' % (len(r_fig4), len(r_fig2)))


def reporte_md(r4, r2, extra, eta15, e15):
    def cnt(rows, idx):
        c = {}
        for r in rows:
            c[r[idx]] = c.get(r[idx], 0) + 1
        return c
    n4, n2 = cnt(r4, 0), cnt(r2, 0)
    return ("""# REPORTE_DIGITALIZACION — Fig. 2 y Fig. 4 de Elsayed et al. (2013)

## Origen de las figuras
- PDF `ctt020.pdf` (raiz del proyecto); imagenes incrustadas a resolucion nativa
  extraidas con pymupdf (`page.get_images()` + `doc.extract_image(xref)`).
- Fig. 2: pagina 4 (xref 78) -> `reference/elsayed2013/fig2_eta_vs_xb.png`
  (1029x680 px, 216259 bytes).  Fig. 4: pagina 5 (xref 98) ->
  `reference/elsayed2013/fig4_eta_vs_P.png` (525x339 px, 96744 bytes).

## Metodo de extraccion
Grayscale; umbral de oscuridad; trazos por columna (runs, hueco max 5 px); seguimiento
entre columnas (tol 8 px; 5 px en FIG.4); union de segmentos (fig4: x-gap<=26, y-gap<=10;
fig2: x-gap<=60, y-gap<=8); fusion de bordes de trazo grueso (|dy|<=6 px) en su centro;
filtro de longitud minima. Identificacion: FIG.4 por eficiencia a x=251 px (15 bar) vs
anclas del texto del paper (11.38 %% KCS11 x_b=0.55; 8.13 %% ORC-NH3 = 11.38/1.4) y, para
la banda media, por continuidad del trazo: discontinua -> ORC-R134a (9.48 %% = 11.38/1.2),
solida -> KCS11 x_b=0.66; tramos sin x=251 por prolongacion por ajuste lineal (<=0.8 pp).
FIG.2: orden de eficiencia en x_r=0.6 (panel b: punto de control, minima distancia a
(x=784.4 px, y=113.5 px) -> 15 bar).

## Calibracion de ejes (constantes del script) y resolucion (1 px)
- FIG.4 x: P=(x-50)*5/67 ("0"@50,"35"@509) -> 1 px = 0.0746 bar.
- FIG.4 y: eta=17.913-0.05022*y ("15"@y=58; eje truncado 5..15 %%) -> 1 px = 0.0502 %%.
- FIG.2 (a): f=(x+31)/515; eta=(273-y)/21 ("12"@21,"4"@189) -> 1 px = 0.00194 frac; 0.0476 %%.
- FIG.2 (b): f=(x-501)/515; eta=(271.7-y)/13.9 ("18"@21.5,"10"@132.5) -> 1 px = 0.00194 frac; 0.0719 %%.
- FIG.2 (c): f=(x-220)/515; eta=(628.5-y)/10.1 ("25"@376,"10"@527.5) -> 1 px = 0.00194 frac; 0.0990 %%.

## Punto de control (KCS11 x_b=0.55, 15 bar, 373/283 K -> 11.38 %%)
- Leido en FIG.4: eta=%.2f %% (delta %.2f pp).
- Leido en FIG.2b: eta=%.2f %% (delta %.2f pp).

## Curvas extraidas (puntos por curva y notas)
- FIG.4: %d registros: %s
- FIG.2: %d registros: %s
%s

## Archivos generados
`elsayed2013_fig2.csv`, `elsayed2013_fig4.csv`, `overlay_fig2.png`, `overlay_fig4.png`,
`REPORTE_DIGITALIZACION.md` (este archivo), en `resultados/2026-09-23_elsayed_digitalizado/`.

## Referencia
Elsayed, A., Embaye, M., AL-Dadah, R., Mahmoud, S., & Rezk, A. (2013). Thermodynamic
performance of Kalina cycle system 11 (KCS11): feasibility of using alternative
zeotropic mixtures. International Journal of Low-Carbon Technologies, 8(suppl_1),
i69-i78. https://doi.org/10.1093/ijlct/ctt020
""" % (eta15, eta15 - CTRL, e15, e15 - CTRL, len(r4), str(n4), len(r2), str(n2),
       '\n'.join('- ' + x for x in extra)))


if __name__ == '__main__':
    main()