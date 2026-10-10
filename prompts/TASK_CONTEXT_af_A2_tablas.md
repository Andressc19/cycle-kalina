# TASK_CONTEXT — A2: tablas de presentación y libro `Excel_kalina_final_final_final.xlsx` con hoja Tablero

**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\af-tablas`
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe` (pandas, openpyxl 3.1.5)
**Lee primero:** `docs/METODOLOGIA_ANALISIS_RESULTADOS.md` §3A.5, §4B.3, §6 (6.1, 6.2, 6.3) y
`scripts/analisis_final/nombres.py`, `pies.py`.
**Entrada:** `analisis_final/01_datos/todos_los_puntos.csv`, `analisis_final/00_inventario/*.csv`,
`analisis_final/03_figuras/**` (PNG + `.pie.md`; **pueden no existir todavía**: los genera otro agente en paralelo) y los CSV de resumen de `resultados/`
que se nombran abajo (solo lectura).

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`.
- PowerShell 5.1: no existen `tee`, `tail`, `head` ni `&&`.
- **Cada comando con el PARÁMETRO `timeout` de la herramienta shell = 7200000**, en primer plano.
- No leer nada fuera de `D:\Desktop\ciclo_kalina_tercero`. Escribir SOLO en `scripts/analisis_final/a2_*.py`,
  `analisis_final/02_tablas/` y `datos/Excel_kalina_final_final_final.xlsx`. **No abrir para escribir
  ni modificar `datos/Excel_final_kalina.xlsx`.** No tocar `nombres.py` ni `pies.py`. No hacer commit.
- Scripts `.py` de 200 líneas como máximo.

## Parte 1 — Tablas (`a2_tablas_*.py` → `analisis_final/02_tablas/<carpeta>/TAB-*.csv` + `.md`)

Cada tabla se guarda como CSV (columnas ya en español) y como Markdown con tres partes (§3A.5):
**encabezado** (ID, título, caso y bloque, punto base, "Datos fijos: …" de `pies.condiciones_texto`),
**cuerpo**, **notas** (filtro, n, † = fuera de rango, ‡ = N2, fuente).

Formato numérico (§6.1): η en % con 2 decimales; presiones sin decimales (1 decimal si < 1000);
temperaturas con 1 decimal; x_b, ε, η_t, η_p con 3; índices (KS, PRCC, E, p) con 3.

### Juego mínimo por caso (para cada `id_caso` menos KF-M08)
- `TAB-<Mnn>-00` condiciones: filas de `condiciones_por_subcaso.csv` del caso, con las columnas
  Subcaso, Variable (`nombres.NOMBRE`), Estado (Fija/Barrida), Valor o rango, n valores, ¿Igual al profesor?, Unidad.
- `TAB-<Mnn>-01` conteo por clase: filas de `conteo_por_subcaso.csv` del caso, con las columnas
  Subcaso, Corridas, Genuinas, KALINA, KALINA confiables, Corregibles, Inviables, No convergió, N2, Omitidas, Fuera de rango.

`<Mnn>` = `M01, M02-N1, M02-N2, M02R, M02S, M03, M04, M04b, M04c, M05, M05c, M06, M07, M09, M10, M10b`.

### Resultado principal (`TAB-<Mnn>-02`): renombrar y formatear el resumen que ya existe

| ID | Fuente (en `resultados/`) |
|---|---|
| TAB-M01-02 | 2026-10-06_final_M1/m1_comparacion.csv |
| TAB-M02-N1-02 | 2026-10-06_final_M2/m2n1_resumen.csv |
| TAB-M02-N2-02 | 2026-10-06_final_M2/m2n2_resumen.csv |
| TAB-M02R-02 | 2026-10-06_final_M2R/m2r_resumen.csv |
| TAB-M02S-02 | 2026-10-06_final_M2S/m2s_resumen.csv |
| TAB-M03-02 | ver abajo (se calcula) |
| TAB-M04-02 / -03 / -04 | 2026-10-07_final_M4b/m4b_rsa.csv / m4b_prcc.csv / m4b_rangos_presiones.csv |
| TAB-M04-05 / -06 / -07 | 2026-10-07_final_M4b/m4b_ventana_por_palta.csv / _por_tfuente.csv / _por_tsumidero.csv |
| TAB-M04c-02 | 2026-10-07_final_M4c/m4c_techo.csv y m4c_techo_por_palta.csv (2 tablas: -02 y -03) |
| TAB-M05-02 / -03 | 2026-10-07_final_M5/m5_resumen.csv / m5_rangos.csv |
| TAB-M05c-02 | 2026-10-07_final_M5c/m5c_frontera.csv |
| TAB-M06-02 / -03 | 2026-10-08_final_M6/m6_comparacion.csv / m6_subenfriamiento.csv |
| TAB-M07-02 | 2026-10-07_final_M7/m7_optimos.csv |
| TAB-M09-02 / -03 | 2026-10-08_final_M9/m9_escalera.csv / m9_motor_real.csv |
| TAB-M10-02 / -03 | 2026-10-09_final_M10_husavik/m10_catalogo.csv / m10_ofat_rangos.csv |
| TAB-M10b-02 | se calcula: por x_b de KF-M10b-MALLA, P_baja mínima KALINA, η en ese punto y criterio que más bloquea a los no KALINA |

Renombrado de columnas: usa `nombres.NOMBRE` cuando la columna esté ahí. Para las demás, propón un
nombre en español y **anótalo** en `analisis_final/02_tablas/traducciones_columnas.csv`
(`tabla, columna_original, nombre_propuesto, unidad`), para que el director lo revise. No borres columnas.

**TAB-M03-02 (ranking local)**, desde la tabla canónica (bloque B06) y `m3_resumen.csv` / `m3_cruces.csv`:
columnas Variable, Rango [a, b], Valor en A*, Elasticidad E en A* (`E_eta`), Δη [pp] (malla, genuinos
con W_net > 0: (máx − mín) × 100), η máx. KALINA [%] y su valor, Zona KALINA (`kalina_desde`–`kalina_hasta`),
Criterios que bloquean (`criterios_bloqueantes`), Distancia a la frontera de O2 (fracción del rango:
|v_cruce − valor_ancla| / (b − a), tomando de `m3_cruces.csv` las filas con `criterio` = m_O2).
Orden: |E| de mayor a menor.

### Síntesis (`analisis_final/02_tablas/G/`)
- `TAB-G01`: una fila por caso con ID, nombre, familia, bloque(s), punto base, diseño, corridas,
  genuinas, KALINA, KALINA confiables, N2 y criterio que más bloquea. Los nombres, familias y diseños
  se copian de la tabla §2.1 de la metodología. El criterio dominante es el código O1/O2/O3/O5 más
  frecuente en `codigos_falla` de los genuinos no KALINA.
- `TAB-G02`: `casos_x_variables.csv` con encabezados en español.
- `TAB-G03`: rangos KALINA comparados: p5, mediana y p95 de P_alta, P_baja, dP, rP, T_fuente y x_b,
  sobre los KALINA confiables de B07, cada B09-<k> (k = 1…5 = escenarios S1…S5), B10, el B13 del conjunto elegido en la ronda 3
  de M9 (`m9_escalera.csv`, `elegido`) y B14-MALLA. Una fila por (caso, variable), con la columna
  "Datos fijos" (de `pies.condiciones_texto`).
- `TAB-G04`: los 11 datos del profesor. Columnas: dato, valor, conservado en el conjunto máximo de M9
  (sí/no: en el `conservados` elegido de la última ronda; códigos EF = las 5 eficiencias/efectividades,
  PA = P_alta, PB = P_baja, TF = T_fuente, TS = T_sumidero, XB = x_b).
- `TAB-G05`: por caso, n y % de genuinos no KALINA que violan O1, O2, O3 y O5 (columnas `viol_O*`).

## Parte 2 — Libro (`a2_excel_*.py` → `datos/Excel_kalina_final_final_final.xlsx`)

Hojas en este orden (§6.3), todo en español:
1. `LEEME`: para qué es el libro, cómo leer las hojas, el `nombres.GLOSARIO` completo y la leyenda
   de colores de clase.
2. `Tablero` (ver Parte 3).
3. `Indice`: una fila por hoja con hipervínculo interno, caso, bloque y qué muestra.
4. `Punto_profesor`: los 11 datos del profesor y los de A* (T_fuente 403 K, P_baja 563.64 kPa, resto igual).
5. `G01_resumen_casos` … `G05_bloqueos`.
6. Por caso, en orden: `<Mnn>_00_condiciones`, `<Mnn>_01_conteo`, `<Mnn>_02_…`, y `<Mnn>_figuras`
   con los PNG de `03_figuras/<carpeta>/` insertados. **Si la carpeta de figuras no existe, la hoja
   `<Mnn>_figuras` se crea con el texto "Figuras pendientes: se insertan al volver a correr a2_excel_libro.py"**;
   el script debe poder correrse de nuevo más tarde y entonces insertar los PNG (`openpyxl.drawing.image.Image`, ancho ~16 cm),
   cada uno con su pie (`.pie.md`) en las celdas de abajo.
7. `X_M08_anecdotico`: conteo de KF-M08 y una franja roja arriba: "ANECDÓTICO — fuera del rango realista".
8. `Datos` (tabla canónica como Tabla de Excel con filtros), `Condiciones`, `Bloques`, `Aux_tablero` (oculta).

Formato de cada hoja `<Mnn>_*`: filas 1–6 con el encabezado (título; caso y bloque; punto base; datos
fijos; filtro; fuente); la tabla empieza en la fila 8 con encabezado en negrita y autofiltro; las
notas van al final. Celdas de clase coloreadas: KALINA C6EFCE, CORREGIBLE FFD9A0, NO_CONVERGIO F8B4B4,
INVIABLE FFF2A8, N2 D9D9D9. Ancho de columnas ajustado; paneles inmovilizados bajo el encabezado.
Nombres de hoja ≤ 31 caracteres.

## Parte 3 — Hoja `Tablero` (solo fórmulas clásicas: INDEX/MATCH; sin FILTRAR, sin macros)

- `B2`: lista desplegable (validación de datos) con los `bloque_director` de `Bloques` (menos BX). Si el bloque es OAT (`es_oat`), la tabla de condiciones muestra `valor_base` con el título "Punto base (las demás quedan fijas aquí)".
- **KPIs** (B4:G5): Corridas, Genuinas, KALINA, KALINA confiables, η máx. KALINA [%], Criterio que más bloquea.
  Se precalculan por bloque en `Aux_tablero` (una columna por bloque) y se leen con
  `=INDEX(Aux_tablero!<fila>, MATCH($B$2, Aux_tablero!$1:$1, 0))`.
- **Condiciones** (B8:E21): las 13 variables con Estado y Valor/rango del bloque elegido; precalculadas
  en `Aux_tablero` (bloques de 13 filas por bloque, una columna por bloque) y leídas con INDEX/MATCH.
- **Pie del bloque** (B23): `pies.condiciones_texto` del bloque, precalculado y leído con INDEX/MATCH.
- **Gráfico 1** (barras): n por clase del bloque elegido (rango auxiliar en `Tablero` con INDEX/MATCH).
- **Gráfico 2** (barras): n de genuinos no KALINA que violan O1, O2, O3 y O5.
- **Gráfico 3** (dispersión): las 2 variables principales del bloque. Son las 2 primeras barridas en
  este orden de prioridad: P_alta, P_baja, T_fuente, x_b, T_sumidero, eps_cond, eps_hrvg, eps_reg,
  eta_t, eta_p. En `Aux_tablero` van, por bloque, 8 columnas (x e y de KALINA, Corregible, Inviable y
  No convergió+N2), de 900 filas como máximo. Las celdas vacías llevan `=NA()`, para que Excel no las
  dibuje. En `Tablero`, un rango de 900 × 8 las lee con
  `=IFERROR(INDEX(Aux_tablero!<col>, ROW()-k), NA())`, eligiendo la columna con MATCH sobre el
  encabezado `"<bloque>|<serie>"`. Los títulos de los ejes del gráfico salen de celdas con
  `nombres.NOMBRE` de las 2 variables (también INDEX/MATCH). Una serie por clase, con su color
  (2E7D32, EF8A17, C9A227, C62828) y marcador (círculo, triángulo, cuadrado, x).
- Si un bloque tiene más de 900 puntos en alguna clase, se toman los primeros 900 y se anota en el pie.

## Verificación (`a2_verificar.py`)

1. Imprime la lista de hojas del libro nuevo y su número.
2. Para 5 hojas `<Mnn>_01_conteo` elegidas al azar (semilla 1): los conteos coinciden con `conteo_por_subcaso.csv`.
3. Ninguna hoja `<Mnn>_*` tiene filas de más de un bloque, salvo las `_00_condiciones` y `_01_conteo` que
   lista subcasos del mismo caso (imprime los bloques que aparecen por hoja).
4. Calcula el hash SHA-256 de `datos/Excel_final_kalina.xlsx` al empezar y al terminar `a2_excel_*.py`,
   y comprueba que no cambió.
5. La hoja `Tablero` existe; la validación de B2 tiene la lista; hay 3 gráficos.

## Comandos (cada uno con timeout = 7200000)

```
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\analisis_final\a2_tablas_casos.py
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\analisis_final\a2_tablas_sintesis.py
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\analisis_final\a2_excel_libro.py
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\analisis_final\a2_verificar.py
```

(Si un script supera 200 líneas, pártelo en `a2_excel_hojas.py`, `a2_excel_tablero.py`, etc., y que
`a2_excel_libro.py` los llame.)

## Formato de salida

El obligatorio de `AGENTS.md`. En RESULTS, pega la salida de `a2_verificar.py`.
