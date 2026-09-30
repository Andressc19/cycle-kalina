---
project: ciclo_kalina_tercero
task_id: 2026-09-23-elsayed-digitalizar-v2
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-23
---

# TASK_CONTEXT — Digitalizar Fig. 2 y Fig. 4 de Elsayed et al. (2013) — v2 (rehacer)

## Task ID

2026-09-23-elsayed-digitalizar-v2

## Por qué se rehace

El intento anterior (`opencode_run_019.log`, `scripts/digitalizar_elsayed2013.py`) fue
**rechazado por Claude en auditoría visual**: curvas mal asignadas (p. ej. Fig. 2c "10 bar,
x=0.45 → 24.9 %" cuando la curva de 10 bar está ≈11 % ahí; Fig. 2a "10 bar en x=0.9–1.0,
η 6.2–6.7 %" cuando esa curva vale ≈3–4 % en ese tramo), curvas truncadas (KCS11 x=0.66 solo
15–20 bar), y el punto de control 11.38 % se usó para *identificar* curvas (circular: así el
control ya no valida nada). Además la ejecución se abortó al intentar editar un archivo en
`C:\cambio\` (fuera del proyecto — prohibido, ver AGENTS.md).

**Sobrescribe** `scripts/digitalizar_elsayed2013.py` y los 5 archivos de
`resultados/2026-09-23_elsayed_digitalizado/` (autorizado). Las imágenes ya extraídas en
`reference/elsayed2013/fig2_eta_vs_xb.png` (1029×680) y `fig4_eta_vs_P.png` (525×339) son
correctas: úsalas, no vuelvas a extraer.

## Leyendas y ejes (leídos por Claude de las imágenes — son la única base para identificar curvas)

Imágenes en escala de grises. Cada curva se distingue por **forma de marcador + relleno**:

**Fig. 2** (eje x: fracción másica NH3, 0.2–1.0, marcas cada 0.2; T_sumidero 283 K)
- Panel (a), arriba-izquierda, T_fuente=333 K, eje y 0–12 (marcas cada 2):
  - 10 bar: círculo **blanco** con línea
  - 15 bar: rombo **blanco** con línea
  - 20 bar: línea **negra** gruesa **sin marcadores**
- Panel (b), arriba-derecha, T_fuente=373 K, eje y 0–18 (marcas cada 2):
  - 10 bar: círculo blanco · 15 bar: rombo **gris** · 25 bar: círculo **gris** ·
    30 bar: rombo blanco · 40 bar: línea negra sin marcadores
- Panel (c), abajo-centro, T_fuente=423 K, eje y 0–25 (marcas cada 5):
  - mismas 5 curvas y mismos estilos que (b)

**Fig. 4** (T_fuente=373 K; eje x: presión de evaporador 0–35 bar, marcas cada 5; eje y 0–20 %,
marcas cada 5)
- KCS11 x=0.66: rombo **blanco**, línea discontinua
- KCS11 x=0.55: rombo **gris**, línea continua (termina con un tramo descendente)
- ORC amoníaco: triángulo **negro** · ORC R134a: triángulo **blanco** (opcionales)

## Objective

Reescribir `scripts/digitalizar_elsayed2013.py` (≤ 350 líneas; PIL + numpy + scipy, ya en
`.venv`):

1. **Calibración de ejes**: localizar las líneas de eje y las marcas (ticks) por píxeles; usar
   **las marcas extremas** de cada eje (p. ej. 0 y 12 en 2a). Constantes de píxel escritas en el
   script con comentario de a qué etiqueta corresponden. Verifica la calibración contra las
   marcas intermedias (error en px, al reporte).
2. **Curvas con marcadores**: detección de marcadores por **plantilla** (correlación, p. ej.
   `scipy.signal.correlate2d` o `scipy.ndimage`), recortando una plantilla de cada estilo
   **de la leyenda** de la propia figura. Clasificar por forma (círculo/rombo/triángulo) y
   nivel de gris del relleno (blanco/gris/negro). Un punto por marcador (centro).
3. **Curvas sin marcadores** (línea negra de 20 bar en 2a, 40 bar en 2b/2c): seguir el trazo
   oscuro grueso columna a columna, muestrear cada 0.02 de fracción másica, **excluyendo** la
   zona de la caja de leyenda y de la caja de texto "Tsource".
4. **Excluir** siempre de la detección: cajas de leyenda, cajas de texto, etiquetas de ejes.
5. Donde marcadores de curvas distintas se solapan y la clasificación sea incierta,
   `metodo=dudoso` (no los omitas ni los reasignes a mano).
6. **Prohibido** usar el punto de control 11.38 % (o cualquier número del texto del paper)
   para identificar, ajustar o desplazar curvas. La identificación sale **solo** del estilo del
   marcador según la leyenda de arriba. El control es solo verificación a posteriori.

## Salidas (sobrescribir)

`resultados/2026-09-23_elsayed_digitalizado/`:
- `elsayed2013_fig2.csv`: `panel, T_fuente_K, P_evap_bar, x_b_masica, eta_pct, metodo`
  (`metodo` ∈ {marcador, trazo, dudoso})
- `elsayed2013_fig4.csv`: `curva, x_b_masica, P_evap_bar, eta_pct, metodo`
- `overlay_fig2.png`, `overlay_fig4.png`: imagen original + puntos digitalizados con color
  distinto por curva y leyenda propia (obligatorios, Claude audita con ellos).
- `REPORTE_DIGITALIZACION.md`: método; calibración (constantes + error en marcas
  intermedias); resolución de 1 px por eje; tabla por curva (n puntos, rango x, rango η,
  η máx y su x); punto de control 11.38 % leído en Fig. 4 (curva x=0.55, interpolado a
  15 bar) y en Fig. 2b (curva 15 bar, interpolado a x=0.55), con diferencia en pp; cita.

## Constraints

- **Nunca leer ni escribir fuera de `D:\Desktop\ciclo_kalina_tercero`** — ni archivos
  temporales: usa una carpeta dentro del proyecto si necesitas scratch
  (`resultados/2026-09-23_elsayed_digitalizado/_tmp/`, bórrala al final). Si lo haces fuera, el
  sandbox aborta toda la ejecución.
- Sin red, sin instalar paquetes (pymupdf ya está; no se necesita aquí).
- No inventar valores: todo η sale de píxeles. Nada de completar, suavizar ni extrapolar.
- No tocar ningún otro archivo del repo.

## Acceptance criteria

1. Las 13 curvas KCS11 de la Fig. 2 (3 en a, 5 en b, 5 en c) y las 2 curvas KCS11 de la
   Fig. 4 tienen puntos, cada una con su P / x asignada por estilo de marcador; cualquier curva
   que no se pueda extraer se declara en UNRESOLVED con la razón.
2. Overlays generados.
3. RESULTS incluye la tabla por curva (n, rango x, rango η, η máx y su x) y el control.

## Verification

`.venv/Scripts/python.exe scripts/digitalizar_elsayed2013.py` corrido; overlays generados;
reporte final en el formato obligatorio de AGENTS.md.
