---
project: ciclo_kalina_tercero
task_id: 2026-09-24-embaye-extraccion-vectorial
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-24
---

# TASK_CONTEXT — Extraer los datos EXACTOS de las curvas vectoriales de Embaye et al.

## Task ID

2026-09-24-embaye-extraccion-vectorial

## Contexto

Para la validación académica del modelo KCS11 se van a comparar **tendencias** contra el
modelo publicado por el grupo de Birmingham (Elsayed et al. 2013 / Embaye et al., mismo modelo
EES con propiedades Ibrahim-Klein, pinch 4 K). Los intentos de digitalizar imágenes de
`ctt020.pdf` fallaron. El PDF

  `PERFORMANCEOFKALINACYCLESYSTEM11KCS11USINGLOWTEMPERATUREHEATSOURCES.pdf` (raíz del proyecto)

tiene las figuras como **gráficos vectoriales** (Claude lo verificó: página 4 → 76 dibujos /
1579 elementos de trazado, página 5 → 345 / 4530, 0 imágenes). Por tanto los datos se pueden
leer **exactos** de las coordenadas del PDF, sin procesar píxeles. `pymupdf` ya está instalado
en `.venv` (`import pymupdf`).

Esta tarea SOLO extrae datos. **No se corre el ciclo.**

## Figuras (según el texto del paper; los números de página son de pymupdf, base 1)

Página 4 (las 4 figuras η vs fracción másica NH3, eje x 0.2–1.0, T_sumidero 283 K):
- Fig. 2 — P_evap = 10 bar; series: Tsource = 333 K, 373 K, 423 K; eje y 0–16
- Fig. 3 — P_evap = 15 bar; series: 333, 373, 423 K; eje y 0–18
- Fig. 4 — P_evap = 23.5 bar; series: 373, 423, 463 K; eje y 0–18
- Fig. 5 — P_evap = 32 bar; series: 373, 423, 463 K; eje y 0–18

Página 5:
- Fig. 6a/6b — ORC (NO se necesitan; ignóralas)
- Fig. 7 — η vs presión de evaporador (0–35 bar), eje y 0–20, T_fuente 373 K; series:
  KCS11(Con.=0.66), KCS11(Con.=0.55), ORC(Ammonia), ORC(R134a). **Obligatorias las 2 KCS11**;
  ORC opcionales.

## Objective

Crear `scripts/extraer_embaye_vectorial.py` (≤ 250 líneas), que:

1. **Calibración de ejes por figura** usando el propio PDF: posición (bbox) de las etiquetas de
   ticks (`page.get_text("dict")`) y/o las líneas de eje/rejilla de `page.get_drawings()`.
   Transformación lineal coordenada-PDF → dato con las marcas extremas; comprobar contra las
   marcas intermedias y reportar el error máximo (en unidades del eje).
2. **Asignación de cada figura a su región** de la página (bbox), usando las leyendas/títulos
   de texto ("Evaporator Pressure=10 bar", etc.) para saber qué región es qué figura.
3. **Identificación de series por la LEYENDA**: cada entrada de leyenda ("Tsource=333 K", …)
   tiene al lado una muestra de línea/marcador; su **color de trazo/relleno, ancho y tipo de
   marcador** define la serie. Asigna cada trazado de datos a la serie cuyo estilo coincida.
   Si dos series tienen estilo idéntico y no se pueden distinguir, NO adivines: repórtalo en
   UNRESOLVED.
4. **Datos**: de cada polilínea/serie, extraer los vértices (y/o centros de marcadores) y
   convertirlos a (x, η). Excluir ejes, rejilla, cajas de leyenda y muestras de leyenda.
5. **Control a posteriori** (NO usarlo para calibrar ni identificar): en Fig. 7, curva
   KCS11 Con.=0.55, η interpolado linealmente a 15 bar; el texto del paper dice **11.38 %**.
   Reportar diferencia en pp. (Otros controles del texto, también solo informativos: en Fig. 7
   a 15 bar ORC amoníaco ≈ 7 %, ORC R134a ≈ 9.2 %.)
6. **Figura de auditoría**: renderizar las páginas 4 y 5 (`page.get_pixmap(dpi=150)`) y dibujar
   encima (matplotlib) los puntos extraídos, re-proyectados a coordenadas de página, con un
   color por serie y leyenda. Si la extracción es correcta, los puntos caen exactamente sobre
   las curvas del PDF.

## Salidas (en `resultados/2026-09-24_embaye_vectorial/`)

- `curvas_embaye_eta_vs_xb.csv`: `figura, P_evap_bar, T_fuente_K, x_b_masica, eta_pct`
- `curvas_embaye_fig7.csv`: `curva, x_b_masica, P_evap_bar, eta_pct`
- `auditoria_pag4.png`, `auditoria_pag5.png`
- `REPORTE_EXTRACCION.md`: método, calibración por figura (constantes + error en marcas
  intermedias), tabla por serie (n puntos, rango x, rango η, η máx y su x), resultado de los
  controles, cita del paper (Embaye, M., AL-Dadah, R., Mahmoud, S., Elsayed, A., & Rezk, A.,
  "Performance of Kalina Cycle System 11 (KCS11) using low temperature heat sources",
  University of Birmingham — anota que es la versión de congreso del modelo de Elsayed et al.
  2013, IJLCT 8(suppl_1) i69–i78).

## Files

Crear solo el script y la carpeta de resultados. **No modificar ningún archivo existente** ni el
PDF.

## Constraints

- **Nunca leer ni escribir fuera de `D:\Desktop\ciclo_kalina_tercero`** (ni temporales). Si lo
  haces, el sandbox aborta la ejecución completa sin reporte.
- Sin red; sin instalar nada (pymupdf, matplotlib, numpy ya están en `.venv`).
- Todo valor sale de coordenadas del PDF: nada de completar, suavizar ni extrapolar.
- Trabaja por pasos cortos y verifica cada uno. Primero explora la estructura de
  `get_drawings()` de la página 4 con un volcado pequeño (colores, anchos, número de items por
  dibujo) antes de escribir el extractor; no vuelques miles de líneas al log.
- Si algo no sale en un tiempo razonable, termina con STATUS partial y lo que tengas; no
  iteres indefinidamente.

## Acceptance criteria

1. 12 series η vs x_b (4 figuras × 3 T_fuente) + 2 series KCS11 de Fig. 7, cada una asignada
   por estilo de leyenda (o declarada en UNRESOLVED).
2. Figuras de auditoría y reporte generados.
3. RESULTS: tabla por serie y el control 11.38 %.

## Verification

`.venv/Scripts/python.exe scripts/extraer_embaye_vectorial.py` corrido; salida final en el
formato obligatorio de AGENTS.md.
