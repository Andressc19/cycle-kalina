# TASK_CONTEXT — A3: figuras Matplotlib de la campaña final (por bloque, en español, con pie)

**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\af-figuras`
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe` (matplotlib 3.11, pandas, numpy, scipy)
**Lee primero:** `docs/METODOLOGIA_ANALISIS_RESULTADOS.md` §3A (reglas de presentación), §4.1–4.3
(estilo, catálogo y código base) y `scripts/analisis_final/nombres.py`, `pies.py`.
**Entrada:** `analisis_final/01_datos/todos_los_puntos.csv`, `analisis_final/00_inventario/condiciones_por_subcaso.csv`
y los CSV de resumen de `resultados/` que se nombran abajo (solo lectura).

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`.
- PowerShell 5.1: no existen `tee`, `tail`, `head` ni `&&`.
- **Cada comando con el PARÁMETRO `timeout` de la herramienta shell = 7200000**, en primer plano.
- No leer nada fuera de `D:\Desktop\ciclo_kalina_tercero`. Escribir SOLO en `scripts/analisis_final/estilo.py`,
  `scripts/analisis_final/a3_*.py` y `analisis_final/03_figuras/`. No tocar `nombres.py` ni `pies.py`
  (solo importarlos). No hacer commit.
- Scripts de 200 líneas como máximo. Backend `matplotlib.use("Agg")`.

## Reglas que valen para TODAS las figuras (no negociables)

1. **Un bloque por figura**: se filtra por `bloque_director` (o `id_subcaso`), nunca se mezclan bloques.
   Excepción: las figuras de síntesis FIG-G01, FIG-G02, FIG-M02S-01 y FIG-M09-01 (cada barra, fila o línea es un caso o una base, rotulado con lo que lo distingue).
   **Barridos de una variable a la vez (OAT: KF-M02-N1, KF-M03, KF-M10-OFAT, KF-M10b-OFAT):** el pie usa `pies.condiciones_texto([...])`, que ya
   devuelve "Punto base (las demás variables quedan fijas en): …". En figuras de un solo panel por variable, pasa `variable_movida=`.
2. **Todo en español**: título, ejes (`nombres.NOMBRE`), leyenda (`nombres.ETIQUETA_CLASE`) con
   `(n = …)` por serie.
3. **Título** en la figura, de 2 líneas: la 1.ª, el texto de la columna "Título" del catálogo (con las
   cifras `{…}` calculadas desde los datos); la 2.ª, más chica, `Bloque <b> · <caso(s)>`.
4. **Recuadro de condiciones** (`estilo.recuadro_condiciones`), con lo fijo esencial del bloque en ≤ 3 líneas
   (sale de `pies.condiciones_texto`, recortado si hace falta).
5. **Pie** con `pies.armar_pie(...)`, guardado como `<ruta>.pie.md`. El argumento `base` es el
   texto de la columna "Punto base" del catálogo.
6. **Forma + color por clase** (`estilo.MARCADOR_CLASE` y `COLOR_CLASE`): KALINA ●, CORREGIBLE ▲,
   INVIABLE ■, NO_CONVERGIO ✕, N2 ✕ gris, OMITIDO no se dibuja (se cuenta en el pie). Los puntos
   fuera de rango van con marcador hueco. Se usa la columna `clase_trazo`.
7. **η** se grafica solo en puntos con `genuino` y `wnet_pos`; los no genuinos se dibujan como ✕ sobre
   el eje x (en y = mínimo del eje). Las barras empiezan en 0. Los paneles que se comparan comparten el eje y.
8. Las variables **fijas** del bloque nunca van en un eje.
9. Salida: `analisis_final/03_figuras/<carpeta>/<ID>_<descriptor>.png` (300 dpi) + `.svg` + `.pie.md`,
   con `<carpeta>` = `G`, `M02`, `M02R`, `M02S`, `M03`, `M04`, `M05`, `M06`, `M07`, `M09`, `M10`.

## `estilo.py`

Implementa exactamente el bloque de código de la metodología §4.3 (`COLOR_CLASE`, `ORDEN_CLASE`,
`MARCADOR_CLASE`, `ETIQUETA_CLASE`, `aplicar_estilo`, `clase_trazo`, `recuadro_condiciones`, `guardar`)
y agrega `COLOR_CLASE["OMITIDO"] = "#BDBDBD"` y `MARCADOR_CLASE["OMITIDO"] = "."`.

## Catálogo

Puntos base (columna "Punto base", texto literal):
- PP: "PP = datos del enunciado del profesor (T_fuente 623.15 K, P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50)"
- AST: "A* = punto del profesor con T_fuente = 403 K y P_baja = 563.64 kPa (KALINA, η = 8.48 %)"
- HUS: "Ancla de Húsavík (Fase 3): P_alta 3300 kPa, P_baja 690 kPa, T_fuente 394.15 K, T_sumidero 278.15 K"
- CAJA: "Sin punto base: muestreo en la caja de rangos indicada en 'Datos barridos'"

| ID | Script | Filtro de datos | Tipo | Ejes | Título (línea 1) | Punto base |
|---|---|---|---|---|---|---|
| FIG-G01 | a3_sintesis.py | todos los casos menos KF-M08 | barras horizontales apiladas por `clase_trazo` | x n puntos, y `id_caso` (orden M01→M10b) | "Resultado de cada barrido: puntos por clase" | — |
| FIG-G02 | a3_sintesis.py | `casos_x_variables.csv` | matriz (imshow) con 3 colores: barrido / fijo = profesor / fijo ≠ profesor, y el valor escrito en la celda | x variable, y `id_subcaso` | "Qué variables se movieron y cuáles quedaron fijas en cada barrido" | — |
| FIG-M09-01 | a3_sintesis.py | `resultados/2026-10-08_final_M9/m9_escalera.csv` | barras agrupadas por ronda: KALINA confiables por conjunto conservado; el elegido de cada ronda resaltado (borde negro) | x conjunto, y KALINA confiables | "Se conservan {n} de los 10 datos de diseño del profesor y sigue habiendo KALINA" ({n} = `n_conservadas` del último elegido) | PP |
| FIG-M02-01 | a3_m02.py | bloque B02 | 10 paneles (uno por `variable`): cada punto en x = `valor`, color/forma por clase, y = 0 (tira) | x la variable con sus unidades | "Con un solo cambio sobre los datos del profesor hay {n_kal} KALINA" | PP |
| FIG-M02-02a / b | a3_m02.py | B03-A y B03-B (una figura cada uno) | dispersión de clases | x P_baja, y `val1` (la variable de `var1`) | A: "Ruta A: conservando la fuente del profesor (623 K), {n_kal} KALINA" · B: "Ruta B: KALINA con T_fuente entre {tmin} y {tmax} K" | PP |
| FIG-M02R-<parte> | a3_m02.py | cada B04-<parte> por separado | si `var2` vacío: como FIG-M02-01; si no: dispersión x = valor de la columna de `var2`, y = valor de la columna de `var1` | — | "M2R, parte {parte}: {n_kal} KALINA con η y ε en [0.40, 0.95]" | PP |
| FIG-M02S-01 | a3_m02.py | **figura de síntesis**: bloques B05-B1, B05-B2 y B05-B3 (cada base es su propio bloque; B4 se nombra en el pie si no tiene KALINA); el pie lista los datos fijos de CADA base por separado | 2 paneles lado a lado, una línea por base: izq. P_baja mínima KALINA vs T_sumidero; der. η máxima KALINA vs T_sumidero | x T_sumidero | "Un sumidero más frío baja la P_baja mínima de KALINA y sube η" | leyenda: B1 "T_fuente = 403 K (A*)", B2 "T_fuente = 420 K", B3 "ε_HRVG = 0.40 (fuente del profesor)" |
| FIG-M03-01 | a3_m03.py | B06, `tipo_punto` = malla, genuino y wnet_pos | tornado: barras horizontales Δη = (máx − mín)·100 por `variable`, ordenadas de mayor a menor | x Δη [pp] | "Cerca de A*, {v1} y {v2} son las que más mueven η en su rango" | AST |
| FIG-M03-02 | a3_m03.py | `resultados/2026-10-06_final_M3/m3_resumen.csv` (`E_eta`) | barras horizontales de E, color por signo, ordenadas por \|E\| | x elasticidad E [–] | "Pegado a A*, {v1} es la variable más sensible (E = {e1:.1f})" | AST |
| FIG-M03-03 | a3_m03.py | B06, malla | 10 paneles 2×5, η vs la variable, color/forma por clase, línea punteada en el valor de A* (`valor_ancla` de m3_resumen) y banda ±0.7 pp alrededor de η(A*) | x la variable, y η [%] | "Eficiencia según cada variable, una a la vez, alrededor de A*" | AST |
| FIG-M03-04 | a3_m03.py | `m3_cruces.csv` (tipo = margen) + `m3_resumen.csv` (a, b, valor_ancla) | puntos: distancia = \|v_cruce − valor_ancla\| / (b − a), una fila por variable, color por criterio, línea vertical en 0.06 | x distancia (fracción del rango), y variable | "A* está a menos del 6 % del rango de la frontera de O2 en {k} de {m} variables" | AST |
| FIG-M04-01 | a3_m04.py | B07, genuinos | 10 paneles: CDF empírica de cada variable para KALINA y para el resto; KS y p (`scipy.stats.ks_2samp`) en la leyenda | x la variable, y probabilidad acumulada | "Qué variables separan a los KALINA del resto (LHS de {n} puntos)" | CAJA |
| FIG-M04-02 | a3_m04.py | B07, todos menos omitidos | dispersión P_alta–P_baja por clase + rectas P_baja = P_alta / r_P con r_P = p5 y p95 de `rP` en los KALINA | x P_alta, y P_baja | "KALINA aparece solo con razón de presiones entre {p5:.1f} y {p95:.1f}" | CAJA |
| FIG-M04-03 | a3_m04.py | `resultados/2026-10-07_final_M4b/m4b_prcc.csv`, fila(s) de `salida` = eta | barras horizontales PRCC con intervalo (ic_lo, ic_hi), color por signo | x PRCC [–] | "Influencia de cada variable sobre η (PRCC, {n} puntos)" | CAJA |
| FIG-M04-04 | a3_m04.py | B07, genuinos | 2 histogramas (ΔP y r_P), KALINA vs resto superpuestos | x ΔP [kPa] / r_P [–] | "Los KALINA se concentran en ΔP {a:.0f}–{b:.0f} kPa y r_P {c:.1f}–{d:.1f}" (p5–p95) | CAJA |
| FIG-M04c-01 | a3_m04.py | B08, evaluados (no omitidos) | barras: % KALINA por franja de P_baja de 100 kPa | x franja de P_baja [kPa], y % KALINA | "Fracción de KALINA al subir P_baja entre 1500 y 2500 kPa" | CAJA |
| FIG-M05-S<k> | a3_m05.py | cada B09-<k> por separado (k = 1…5 es el escenario Sk de REPORTE_M5) | dispersión de clases; x = P_alta si está barrida, si no T_fuente; y = P_baja si está barrida, si no x_b (según `condiciones_por_subcaso.csv`) | — | "Escenario {Sk}: {n_kal} KALINA de {n_eval} puntos evaluados" | PP |
| FIG-M05c-01 | a3_m05.py | B10 | 3 paneles (uno por T_sumidero): mapa de clases con celdas coloreadas | x T_fuente, y ε_cond | "Con las presiones del profesor hay KALINA desde T_fuente ≈ {tmin:.0f} K" (tmin = mínimo T_fuente KALINA) | PP |
| FIG-M06-01 | a3_m07.py | `resultados/2026-10-08_final_M6/m6_comparacion.csv` | paridad η teqp vs η real con la recta 1:1 y la banda ±0.7 pp; los pares sin η real se listan en el pie | x η teqp [%], y η real [%] | "teqp contra el motor real en {n} puntos de control" | — |
| FIG-M07-01 | a3_m07.py | `resultados/2026-10-07_final_M7/m7_trayectorias.csv` | una línea por `arranque`: η vs iteración | x iteración, y η [%] | "La búsqueda llega a η = {max:.1f} % dentro de la región KALINA" | — |
| FIG-M10-01 | a3_m10.py | B14-MALLA (M10 + M10b) | mapa de clases + línea de P_baja mínima KALINA por x_b | x x_b, y P_baja | "Húsavík: P_baja mínima de KALINA según la composición x_b" | HUS |
| FIG-M10-02 | a3_m10.py | B14-OFAT, `variable` y `valor` | paneles por variable, η vs valor, color/forma por clase | — | "Húsavík: eficiencia según cada variable, una a la vez" | HUS |

KF-M08 (anecdótico) y KF-M10-F3 no llevan figura. Si `condiciones_por_subcaso.csv` muestra que un
bloque del catálogo no tiene las condiciones que la figura supone (por ejemplo, que en B14-MALLA M10 y
M10b tengan distinto piso de O2), **no lo mezcles**: haz una figura por subcaso, con el sufijo `a`/`b`,
y anótalo en ASSUMPTIONS.

## Verificación (`a3_verificar.py`)

Para cada figura del catálogo: existen el PNG, el SVG y el `.pie.md`; el pie contiene "Datos fijos",
"Filtro", "n =" y "Fuente". Imprime una tabla ID → OK/FALTA, y para cada figura de dispersión, el n
de puntos dibujados por clase.

## Comandos (cada uno con timeout = 7200000)

```
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\analisis_final\a3_sintesis.py
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\analisis_final\a3_m02.py
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\analisis_final\a3_m03.py
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\analisis_final\a3_m04.py
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\analisis_final\a3_m05.py
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\analisis_final\a3_m07.py
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\analisis_final\a3_m10.py
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\analisis_final\a3_verificar.py
```

## Formato de salida

El obligatorio de `AGENTS.md`. En RESULTS, pega la salida de `a3_verificar.py`.
