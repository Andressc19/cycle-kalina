# REPORTE_DIGITALIZACION — Fig. 2 y Fig. 4 de Elsayed et al. (2013)

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
anclas del texto del paper (11.38 % KCS11 x_b=0.55; 8.13 % ORC-NH3 = 11.38/1.4) y, para
la banda media, por continuidad del trazo: discontinua -> ORC-R134a (9.48 % = 11.38/1.2),
solida -> KCS11 x_b=0.66; tramos sin x=251 por prolongacion por ajuste lineal (<=0.8 pp).
FIG.2: orden de eficiencia en x_r=0.6 (panel b: punto de control, minima distancia a
(x=784.4 px, y=113.5 px) -> 15 bar).

## Calibracion de ejes (constantes del script) y resolucion (1 px)
- FIG.4 x: P=(x-50)*5/67 ("0"@50,"35"@509) -> 1 px = 0.0746 bar.
- FIG.4 y: eta=17.913-0.05022*y ("15"@y=58; eje truncado 5..15 %) -> 1 px = 0.0502 %.
- FIG.2 (a): f=(x+31)/515; eta=(273-y)/21 ("12"@21,"4"@189) -> 1 px = 0.00194 frac; 0.0476 %.
- FIG.2 (b): f=(x-501)/515; eta=(271.7-y)/13.9 ("18"@21.5,"10"@132.5) -> 1 px = 0.00194 frac; 0.0719 %.
- FIG.2 (c): f=(x-220)/515; eta=(628.5-y)/10.1 ("25"@376,"10"@527.5) -> 1 px = 0.00194 frac; 0.0990 %.

## Punto de control (KCS11 x_b=0.55, 15 bar, 373/283 K -> 11.38 %)
- Leido en FIG.4: eta=11.38 % (delta 0.00 pp).
- Leido en FIG.2b: eta=11.38 % (delta 0.00 pp).

## Curvas extraidas (puntos por curva y notas)
- FIG.4: 57 registros: {'KCS11': 25, 'ORC-NH3': 20, 'ORC-R134a': 12}
- FIG.2: 48 registros: {'a': 9, 'b': 25, 'c': 14}
- FIG4 KCS11          x=0.55  P 10.0..28.0 bar  n=19
- FIG4 ORC-NH3        x=  P 11.0..30.0 bar  n=20
- FIG4 ORC-R134a      x=  P 12.0..15.0 bar  n=4
- FIG4 KCS11          x=0.66  P 15.0..20.0 bar  n=6
- FIG4 ORC-R134a      x=  P 22.0..29.0 bar  n=8
- FIG2 a P=10 bar  f 0.90..1.00  n=  3
- FIG2 a P=15 bar  f 0.75..0.85  n=  3
- FIG2 a P=20 bar  f 0.60..0.70  n=  3
- FIG2 a: curva sin asignar -> curva_no_identificada
- FIG2 a: curva sin asignar -> curva_no_identificada
- FIG2 a: curva sin asignar -> curva_no_identificada
- FIG2 b: control 15 bar sobre curva #2 (dist 0.1 px)
- FIG2 b: curva sin asignar -> curva_no_identificada
- FIG2 b: curva sin asignar -> curva_no_identificada
- FIG2 b P=15 bar  f 0.45..0.90  n= 10
- FIG2 b P=10 bar  f 0.50..0.90  n=  9
- FIG2 b P=25 bar  f 0.65..0.90  n=  6
- FIG2 b: curva sin asignar -> curva_no_identificada
- FIG2 b: curva sin asignar -> curva_no_identificada
- FIG2 b: curva sin asignar -> curva_no_identificada
- FIG2 b: curva sin asignar -> curva_no_identificada
- FIG2 b: curva sin asignar -> curva_no_identificada
- FIG2 b: curva sin asignar -> curva_no_identificada
- FIG2 c P=10 bar  f 0.45..0.45  n=  1
- FIG2 c P=15 bar  f 0.25..0.45  n=  5
- FIG2 c P=25 bar  f 0.50..0.50  n=  1
- FIG2 c P=30 bar  f 0.60..0.90  n=  7
- FIG2 c: curva sin asignar -> curva_no_identificada
- FIG2 c: curva sin asignar -> curva_no_identificada
- FIG2 c: curva sin asignar -> curva_no_identificada
- FIG2 c: curva sin asignar -> curva_no_identificada
- FIG2 c: curva sin asignar -> curva_no_identificada
- FIG2 c: curva sin asignar -> curva_no_identificada
- FIG2 c: curva sin asignar -> curva_no_identificada
- FIG2 c: curva sin asignar -> curva_no_identificada

## Archivos generados
`elsayed2013_fig2.csv`, `elsayed2013_fig4.csv`, `overlay_fig2.png`, `overlay_fig4.png`,
`REPORTE_DIGITALIZACION.md` (este archivo), en `resultados/2026-09-23_elsayed_digitalizado/`.

## Referencia
Elsayed, A., Embaye, M., AL-Dadah, R., Mahmoud, S., & Rezk, A. (2013). Thermodynamic
performance of Kalina cycle system 11 (KCS11): feasibility of using alternative
zeotropic mixtures. International Journal of Low-Carbon Technologies, 8(suppl_1),
i69-i78. https://doi.org/10.1093/ijlct/ctt020
