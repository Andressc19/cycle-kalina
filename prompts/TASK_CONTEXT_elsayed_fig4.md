---
project: ciclo_kalina_tercero
task_id: 2026-09-23-elsayed-fig4
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-23
---

# TASK_CONTEXT — Digitalizar SOLO la Fig. 4 de Elsayed et al. (2013)

## Task ID

2026-09-23-elsayed-fig4

## Contexto

Dos intentos previos de digitalizar Fig. 2 + Fig. 4 juntas fallaron: el primero fue rechazado
en auditoría (curvas mal asignadas, control 11.38 % usado de forma circular) y el segundo
(`opencode_run_020.log`) se cortó sin terminar. Se reduce el alcance a **una sola figura, la
más limpia**. Método y reglas generales: `TASK_CONTEXT_elsayed_digitalizar.md` (v2) — léelo,
pero **ignora todo lo de la Fig. 2** y usa los nombres de archivo de ESTA tarea.

Imagen (ya extraída, correcta): `reference/elsayed2013/fig4_eta_vs_P.png` (525×339 px,
escala de grises).

## La figura (leída por Claude)

- T_fuente=373 K, T_sumidero=283 K. Eje x: "Evaporator Pressure [Bars]", 0–35, marcas cada 5.
  Eje y: "Thermal Efficiency [%]", 0–20, marcas cada 5.
- Leyenda arriba-izquierda (4 entradas):
  - KCS11(Con.=0.66): rombo **blanco**, línea discontinua
  - KCS11(Con.=0.55): rombo **gris**, línea continua (tramo final descendente, más espaciado)
  - ORC(Ammonia): triángulo **negro**
  - ORC(R134a): triángulo **blanco**
- Caja de texto "Tsource=373 K" abajo-izquierda: exclúyela.

## Objective

1. Crear `scripts/digitalizar_elsayed2013_fig4.py` (**nuevo**, ≤ 200 líneas; no reutilices ni
   edites `scripts/digitalizar_elsayed2013.py`). PIL + numpy + scipy.
2. Calibración: localizar por píxeles las marcas 0 y 35 del eje x y 0 y 20 del eje y (constantes
   en el script con comentario); verificar contra las marcas intermedias (5, 10, …) y reportar
   el error en px.
3. Detección de marcadores por plantilla recortada **de la leyenda** (correlación normalizada),
   clasificación por forma (rombo/triángulo) y relleno (blanco/gris/negro). Un punto por
   marcador (centro). Excluir las cajas de leyenda y de texto. Marcadores solapados de dos
   curvas con clasificación incierta → `metodo=dudoso`.
4. **Obligatorias**: las dos curvas KCS11. ORC: inclúyelas si salen con el mismo método sin
   esfuerzo extra (útiles como control de la calibración), si no, omítelas y dilo.
5. **Prohibido** usar 11.38 % u otro número del texto del paper para identificar/ajustar
   curvas. La identificación sale solo del estilo del marcador.

## Salidas (en `resultados/2026-09-23_elsayed_digitalizado/`)

- `fig4_v3.csv`: `curva, x_b_masica, P_evap_bar, eta_pct, metodo` (un registro por marcador)
- `overlay_fig4_v3.png`: imagen original ampliada ×2 + puntos detectados, color por curva,
  con leyenda propia.
- `REPORTE_FIG4_v3.md`: calibración (constantes + error en marcas intermedias), resolución de
  1 px en bar y en %, tabla por curva (n marcadores, rango P, rango η, η máx y P del máximo),
  control a posteriori: η interpolado linealmente de la curva x=0.55 a 15 bar vs 11.38 % del
  texto (diferencia en pp), y cita del paper.

No sobrescribas ni borres los archivos antiguos de esa carpeta (quedan como historial del
intento rechazado). Borra solo `_tmp/` si lo usas.

## Constraints

- **Nunca leer ni escribir fuera de `D:\Desktop\ciclo_kalina_tercero`**, ni temporales (usa
  `resultados/2026-09-23_elsayed_digitalizado/_tmp/`). Hacerlo aborta toda la ejecución.
- Sin red, sin instalar paquetes. No tocar ningún otro archivo del repo.
- Todo η sale de píxeles; nada de completar, suavizar ni extrapolar.
- Trabaja por pasos cortos y verifica cada uno; si algo no sale, repórtalo en UNRESOLVED en vez
  de iterar indefinidamente.

## Acceptance criteria

1. Las dos curvas KCS11 con puntos asignados por estilo de marcador.
2. Overlay y reporte generados.
3. RESULTS: tabla por curva y el control a posteriori.

## Verification

`.venv/Scripts/python.exe scripts/digitalizar_elsayed2013_fig4.py` corrido; salida en el
formato obligatorio de AGENTS.md.
