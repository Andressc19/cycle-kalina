# TASK_CONTEXT — A1: tabla canónica de puntos, condiciones por subcaso y glosario

**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\af-datos`
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe` (pandas 3, numpy, openpyxl ya instalados)
**Contexto (léelo):** `docs/METODOLOGIA_ANALISIS_RESULTADOS.md` §1, §2.3, §3A.1, §3A.2, §3A.6 y §4B.4.

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`. Nunca desde PowerShell.
- PowerShell 5.1: no existen `tee`, `tail`, `head` ni `&&`.
- **Cada comando con el PARÁMETRO `timeout` de la herramienta shell = 7200000**, en primer plano.
  Nada de `Start-Process`.
- No leer nada fuera de `D:\Desktop\ciclo_kalina_tercero`. No tocar `src/`, `resultados/`, `datos/`,
  `app.py` ni `scripts/barrido_final/`. No hacer commit.
- Scripts NUEVOS en `scripts/analisis_final/`, de **200 líneas como máximo** cada uno.
- Leer los CSV con `pandas.read_csv` (algunos campos `mensaje` tienen saltos de línea entre comillas;
  pandas los maneja; **no** cuentes filas con `wc -l`). `comun.py` NO tiene helpers de CSV: no lo importes.
- No inventes columnas, valores ni definiciones: todo lo que necesitas está aquí.

## Objetivo

Juntar en UNA tabla todos los puntos evaluados de la campaña final (M1–M10b), identificar cada punto
por caso, subcaso y bloque, y detectar **desde los datos** qué variables quedaron fijas (y en qué valor)
y cuáles se barrieron en cada subcaso.

## 1. Fuentes (`scripts/analisis_final/a1_fuentes.py`)

Una lista `FUENTES` con un dict por archivo: `archivo` (ruta relativa al directorio de trabajo),
`id_caso`, `tipo_punto` (fijo, o el nombre de la columna de donde sale) y la regla de subcaso.
Raíz de todas las rutas: `resultados/`. Solo estos archivos (los demás son resúmenes y NO entran):

| archivo | id_caso | id_subcaso | tipo_punto | bloque_director |
|---|---|---|---|---|
| 2026-10-06_final_M1/m1_filas.csv | KF-M01 | `KF-M01-<grupo>` | `malla` | B01 |
| 2026-10-06_final_M2/m2n1_malla.csv | KF-M02-N1 | `KF-M02-N1` | `malla` | B02 |
| 2026-10-06_final_M2/m2n1_biseccion.csv | KF-M02-N1 | `KF-M02-N1` | `biseccion` | B02 |
| 2026-10-06_final_M2/m2n2_malla.csv | KF-M02-N2 | `KF-M02-N2-<ruta>` | `malla` | B03-<ruta> |
| 2026-10-06_final_M2/m2n2_biseccion.csv | KF-M02-N2 | `KF-M02-N2-<ruta>` | `biseccion` | B03-<ruta> |
| 2026-10-06_final_M2R/m2r_n1_malla.csv | KF-M02R | `KF-M02R-<parte>` | `malla` | B04-<parte> |
| 2026-10-06_final_M2R/m2r_n1_biseccion.csv | KF-M02R | `KF-M02R-<parte>` | `biseccion` | B04-<parte> |
| 2026-10-06_final_M2R/m2r_n2a_malla.csv | KF-M02R | `KF-M02R-<parte>` | `malla` | B04-<parte> |
| 2026-10-06_final_M2R/m2r_n2a_biseccion.csv | KF-M02R | `KF-M02R-<parte>` | `biseccion` | B04-<parte> (0 filas: válido) |
| 2026-10-06_final_M2R/m2r_n2b_malla.csv | KF-M02R | `KF-M02R-<parte>` | `malla` | B04-<parte> |
| 2026-10-06_final_M2R/m2r_n2b_biseccion.csv | KF-M02R | `KF-M02R-<parte>` | `biseccion` | B04-<parte> |
| 2026-10-06_final_M2R/m2r_n3_malla.csv | KF-M02R | `KF-M02R-<parte>` | `malla` | B04-<parte> |
| 2026-10-06_final_M2S/m2s_malla.csv | KF-M02S | `KF-M02S-<base>` | `malla` | B05 |
| 2026-10-06_final_M2S/m2s_biseccion.csv | KF-M02S | `KF-M02S-<base>` | `biseccion` | B05 |
| 2026-10-06_final_M3/m3_ofat.csv | KF-M03 | `KF-M03` | columna `tipo_punto` | B06 |
| 2026-10-06_final_M4/m4_lhs.csv | KF-M04 | `KF-M04` | `lhs` | B07 |
| 2026-10-07_final_M4b/m4b_lhs.csv | KF-M04b | `KF-M04b` | `lhs` | B07 |
| 2026-10-07_final_M4c/m4c_lhs.csv | KF-M04c | `KF-M04c` | `lhs` | B08 |
| 2026-10-07_final_M5/m5_lhs.csv | KF-M05 | `KF-M05-<escenario>` | `lhs` | B09-<escenario> |
| 2026-10-07_final_M5c/m5c_malla.csv | KF-M05c | `KF-M05c` | `malla` | B10 |
| 2026-10-07_final_M7/m7_evaluaciones.csv | KF-M07 | `KF-M07-<arranque>` | `busqueda` | B11-<arranque> |
| 2026-10-07_final_M8_anecdotico/m8_oat.csv | KF-M08 | `KF-M08` | `oat` | BX |
| 2026-10-08_final_M6/m6_verificacion.csv | KF-M06 | `KF-M06-VER` | `control` | B12 |
| 2026-10-08_final_M6/m6_piso_30_4C.csv | KF-M06 | `KF-M06-PISO` | `control` | B12 |
| 2026-10-08_final_M6/m6_subenfriamiento_evals.csv | KF-M06 | `KF-M06-SUB` | `busqueda` | B12 |
| 2026-10-08_final_M9/m9_paso1.csv | KF-M09 | `KF-M09-R0-<conservados>` | `lhs` | B13-<conservados> |
| 2026-10-08_final_M9/m9_paso2.csv | KF-M09 | `KF-M09-R<ronda>-<conservados>` | `lhs` | B13-<conservados> |
| 2026-10-08_final_M9/m9_husavik.csv | KF-M09 | `KF-M09-HUS` | `control` | B13-HUS |
| 2026-10-08_final_M9/m9_motor_real_raw.csv | KF-M09 | `KF-M09-REAL` | `control` | B12 |
| 2026-10-09_final_M10_husavik/m10_recorrida_fase3.csv | KF-M10 | `KF-M10-F3` | `control` | B14-F3 |
| 2026-10-09_final_M10_husavik/m10_ofat.csv | KF-M10 | `KF-M10-OFAT` | `oat` | B14-OFAT |
| 2026-10-09_final_M10_husavik/m10_malla_xb_pbaja.csv | KF-M10 | `KF-M10-MALLA` | `malla` | B14-MALLA |
| 2026-10-09_final_M10b_xb_bajo/m10b_ofat_xb.csv | KF-M10b | `KF-M10b-OFAT` | `oat` | B14-OFATb |
| 2026-10-09_final_M10b_xb_bajo/m10b_malla_xb_pbaja.csv | KF-M10b | `KF-M10b-MALLA` | `malla` | B14-MALLA |

`<columna>` = el valor de esa columna en la fila, sin espacios (reemplaza espacios y `+` por `_` solo
en el ID; conserva el valor original en su columna). Si una columna indicada no existe en el archivo,
**detente y repórtalo** en UNRESOLVED (no inventes).

## 2. Tabla canónica (`a1_cargar.py` → `analisis_final/01_datos/todos_los_puntos.csv`)

Una fila por fila de cada archivo de la lista (no deduplicar). Columnas, en este orden:

1. `id_punto` = `<id_subcaso>-<nnnn>` (contador de 4 dígitos por subcaso, en el orden de lectura),
   `id_caso`, `id_subcaso`, `bloque_director`, `tipo_punto`, `origen_csv`, `fila_origen` (índice 0-based
   en el CSV de origen).
2. Entradas: `T_fuente, T_sumidero, P_alta, P_baja, x_b, m_b, eta_t, eta_p, eps_hrvg, eps_reg, eps_cond, T_amb_diseno, motor`.
3. Salidas: `convergio, clasificacion, codigos_falla, eta, Wnet, m_O1, m_O2, m_O3, m_O5, D, viol_O1, viol_O2, viol_O3, viol_O5, fuera_rango, B_verificado, t_s, mensaje`.
4. Columnas propias del archivo que identifican el subcaso o el punto (`grupo, ruta, var1, val1, var2, val2, parte, base, escenario, conservados, ronda, arranque, iteracion, variable, valor, id, id_muestra, realista, familia, piso, origen`) si existen; vacías si no.
5. Calculadas:
   - `genuino` = `clasificacion` ∈ {KALINA, CORREGIBLE, INVIABLE}
   - `es_N2` = `convergio` es verdadero **y** `clasificacion` == NO_CONVERGIO
   - `kalina_confiable` = `clasificacion` == KALINA **y** `fuera_rango` no es verdadero
   - `omitido` = la columna `omitido` del archivo si existe (verdadero/falso); si no, falso
   - `wnet_pos` = `Wnet` > 0 (falso si vacío)
   - `eta_pct` = `eta` × 100
   - `dP` = `P_alta − P_baja`; `rP` = `P_alta / P_baja`; `dT_fs` = `T_fuente − T_sumidero`
   - `clase_trazo` = "N2" si `es_N2`, "OMITIDO" si `omitido`, si no `clasificacion`

Columnas que un archivo no tenga quedan vacías: **nunca** se rellenan con un valor supuesto. Si un
archivo no tiene `T_amb_diseno`, queda vacía (no pongas 300.032917).

## 3. Condiciones por subcaso (`a1_condiciones.py`)

Para cada `id_subcaso` y cada una de las 13 entradas del punto 2.2:
- se cuentan los valores distintos no vacíos, redondeando a 6 cifras significativas;
- si hay 1 → `estado = fijo`, `valor_fijo`;
- si hay más de 1 → `estado = barrido`, `min`, `max`, `n_valores`;
- si todo está vacío → `estado = sin_dato`;
- `igual_al_profesor` (sí/no, solo si es fijo), comparando con el punto del profesor:
  `T_fuente 623.15, T_sumidero 300.032917, P_alta 3000, P_baja 400, x_b 0.50, m_b 1.0, eta_t 0.85,
  eta_p 0.75, eps_hrvg 0.85, eps_reg 0.75, eps_cond 0.80, T_amb_diseno 300.032917` (tolerancia relativa 1e-6);
- `unidad`: K para temperaturas, kPa para presiones, kg/s para m_b, – para el resto.

Salidas en `analisis_final/00_inventario/`:
- `condiciones_por_subcaso.csv`: columnas `id_caso, id_subcaso, bloque_director, variable, estado, valor_fijo, min, max, n_valores, igual_al_profesor, unidad`.
- `bloques.csv`: una fila por `bloque_director`, con sus subcasos, n de puntos y una **firma**: el
  texto ordenado de las variables fijas y sus valores, más la lista de las barridas.
  La columna `consistente` vale "sí" si **todos** los subcasos del bloque tienen la misma firma. Si no,
  la columna `diferencias` dice qué variable difiere y entre qué subcasos. Esto NO se corrige: se reporta.
- `casos.csv`: una fila por `id_caso` con n puntos, genuinos, KALINA, KALINA confiables, CORREGIBLE,
  INVIABLE, NO_CONVERGIO (sin N2), N2, omitidos y fuera de rango.
- `conteo_por_subcaso.csv`: lo mismo por `id_subcaso`.
- `casos_x_variables.csv`: matriz `id_subcaso` × 13 variables, con la celda en `=PP`,
  `fijo:<valor>`, `barrido:[min, max]` o vacía.

## 4. Nombres y glosario (`scripts/analisis_final/nombres.py`)

- `NOMBRE`: dict columna → nombre de presentación en español, **literal**:
  `T_fuente`: "Temperatura de la fuente, T_fuente [K]"; `T_sumidero`: "Temperatura del sumidero, T_sumidero [K]";
  `P_alta`: "Presión de alta, P_alta [kPa]"; `P_baja`: "Presión de baja, P_baja [kPa]";
  `x_b`: "Fracción de amoníaco de la mezcla base, x_b [–]"; `m_b`: "Flujo másico base, m_b [kg/s]";
  `eta_t`: "Eficiencia isentrópica de la turbina, η_t [–]"; `eta_p`: "Eficiencia isentrópica de la bomba, η_p [–]";
  `eps_hrvg`: "Efectividad del generador de vapor, ε_HRVG [–]"; `eps_reg`: "Efectividad del regenerador, ε_reg [–]";
  `eps_cond`: "Efectividad del condensador, ε_cond [–]"; `T_amb_diseno`: "Piso de O2 (T de diseño de la bomba) [K]";
  `eta_pct`: "Eficiencia térmica del ciclo, η [%]"; `Wnet`: "Trabajo neto, W_net [kW] (m_b = 1 kg/s)";
  `dP`: "Diferencia de presiones, ΔP [kPa]"; `rP`: "Razón de presiones, r_P [–]";
  `dT_fs`: "Diferencia de temperatura fuente–sumidero [K]"; `clasificacion`: "Clase del ciclo"; `D`: "Índice de cercanía D [–]".
- `ETIQUETA_CLASE`: KALINA → "KALINA", CORREGIBLE → "Corregible", INVIABLE → "Inviable",
  NO_CONVERGIO → "No convergió", N2 → "Falso convergido (N2)", OMITIDO → "Omitido (no evaluado)".
- `GLOSARIO`: dict término → definición, **literal**:
  - "PP (punto del profesor)": "Los datos del enunciado: P_alta 3000 kPa, P_baja 400 kPa, x_b 0.50, T_fuente 623.15 K, T_sumidero 300.03 K, η_t 0.85, η_p 0.75, ε_HRVG 0.85, ε_reg 0.75, ε_cond 0.80. Con ellos el ciclo no converge."
  - "A* (punto ancla)": "El punto del profesor con solo dos cambios: T_fuente = 403 K y P_baja = 563.64 kPa. Es KALINA con η = 8.48 %. Se eligió en M2 como el cambio intermedio que vuelve funcional el ciclo, y M3 estudia la sensibilidad a su alrededor."
  - "Punto genuino": "Punto cuya clase es KALINA, CORREGIBLE o INVIABLE: el modelo lo resolvió de verdad."
  - "N2 (falso convergido)": "El solver dice que convergió, pero el clasificador lo marca NO_CONVERGIO: es una solución espuria y no cuenta como convergido."
  - "KALINA confiable": "Punto KALINA dentro del rango validado del modelo de propiedades (IAPWS G4-01)."
  - "Fuera de rango": "Punto con estados fuera del rango validado del modelo de propiedades (por ejemplo, líquido por encima de 420 K); su η se toma con cautela."
  - "O1": "Criterio de título (calidad del vapor) a la salida de la turbina."
  - "O2": "Criterio de cavitación: el líquido debe llegar subenfriado a la bomba."
  - "O3": "Criterio de trabajo neto: el ciclo debe producir trabajo (W_net > 0)."
  - "O5": "Criterio del separador: debe recibir una mezcla de dos fases."
  - "Piso de O2": "Temperatura con la que se evalúa la cavitación. 300.03 K fija en M1–M3; desde M2S es igual a la T_sumidero de cada punto."
  - "Banda de η": "Incertidumbre del modelo de propiedades: ±0.4–0.7 puntos porcentuales; diferencias menores no son concluyentes."
  - "Bloque": "Conjunto de puntos con las mismas variables fijas y los mismos valores; solo se comparan puntos de un mismo bloque."

## 5. Pies de figura (`scripts/analisis_final/pies.py`)

Función `condiciones_texto(id_subcasos: list[str]) -> str`, que lee `condiciones_por_subcaso.csv` y
devuelve dos líneas:
- `"Datos fijos: <var> = <valor> <unidad>; ..."`, solo las variables fijas con el mismo valor en
  todos los subcasos dados;
- `"Datos barridos: <var> [min–max] <unidad> (n valores); ..."`.

Usa los nombres cortos (`T_fuente`, `P_baja`…) y los valores con 4 cifras significativas.

Función `armar_pie(id_fig, titulo, id_subcasos, bloque, filtro, n, fuente, marcas="", base="")` ->
str, con el formato:
```
Figura <id_fig>. <titulo>.
Caso(s): <id_subcasos unidos por coma> (bloque <bloque>).<si base: " Punto base: " + base>
<condiciones_texto(...)>
Filtro: <filtro>.<si marcas: " Marcas: " + marcas>
n = <n>. Fuente: <fuente>.
```

## 6. Esquema estrella para Power BI (`a1_estrella.py` → `analisis_final/07_powerbi/`)

- `hechos_puntos.csv`: la tabla canónica completa.
- `dim_caso.csv`: `casos.csv` más `bloque_director`.
- `dim_condiciones.csv`: copia de `condiciones_por_subcaso.csv`.
- `dim_variable.csv`: `variable, nombre_presentacion, unidad` (de `NOMBRE`).
- `dim_clase.csv`: `clase, etiqueta, color, orden`. Colores: KALINA #2E7D32, CORREGIBLE #EF8A17,
  INVIABLE #C9A227, NO_CONVERGIO #C62828, N2 #9E9E9E, OMITIDO #BDBDBD; orden en ese mismo orden.

## 7. Verificación (`a1_verificar.py` → imprime y escribe `analisis_final/05_validacion/checks_A1.md`)

Para cada check, imprime `OK` o `FALLA` con la cifra:
1. Para cada archivo de FUENTES: n filas leídas con pandas == n filas con ese `origen_csv` en la tabla canónica.
2. Ninguna fila con `id_caso`, `id_subcaso` o `bloque_director` vacíos.
3. `id_punto` único.
4. Conteo por `id_caso` y clase (tabla Markdown).
5. Lista de bloques con `consistente = no` y sus diferencias (no es FALLA: es INFORMACIÓN).
6. Conteo de N2 por caso.

## Comandos a ejecutar (en este orden, cada uno con timeout = 7200000, desde el directorio de trabajo)

```
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\analisis_final\a1_cargar.py
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\analisis_final\a1_condiciones.py
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\analisis_final\a1_estrella.py
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\analisis_final\a1_verificar.py
```

Las carpetas de salida se crean con `os.makedirs(..., exist_ok=True)` dentro de los scripts.

## Formato de salida

El obligatorio de `AGENTS.md` (STATUS / SUMMARY / FILES_CHANGED / TESTS / RESULTS / ERRORS /
ASSUMPTIONS / UNRESOLVED / RECOMMENDATIONS). En RESULTS pega la salida completa de `a1_verificar.py`.
