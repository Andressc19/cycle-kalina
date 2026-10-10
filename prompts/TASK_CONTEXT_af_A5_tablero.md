# TASK_CONTEXT — A5: tablero HTML interactivo `tablero_kalina.html`

**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\af-tablero`
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`
**Lee primero:** `docs/METODOLOGIA_ANALISIS_RESULTADOS.md` §3A (reglas: no mezclar bloques, condiciones
visibles) y §4B.2 (diseño del tablero), y `scripts/analisis_final/nombres.py`.
**Entrada:** `analisis_final/01_datos/todos_los_puntos.csv`, `analisis_final/00_inventario/*.csv` y
`analisis_final/05_validacion/validacion_A4.csv` (si existe).

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`.
- PowerShell 5.1: no existen `tee`, `tail`, `head` ni `&&`.
- **Cada comando con el PARÁMETRO `timeout` de la herramienta shell = 7200000**, en primer plano.
- No leer nada fuera de `D:\Desktop\ciclo_kalina_tercero`. No descargar nada de internet. Escribir
  SOLO en `scripts/analisis_final/a5_*` y `analisis_final/06_tablero/`. No hacer commit.
- `.py` de 200 líneas como máximo; los archivos de plantilla (`a5_plantilla.html`, `a5_estilos.css`,
  `a5_app.js`) de 300 líneas como máximo cada uno. El `.py` los une en un solo HTML.

## Construcción

`a5_tablero.py`:
1. Lee la tabla canónica y deja **solo** estas columnas: `id_punto, id_caso, id_subcaso, bloque_director,
   tipo_punto, clase_trazo, genuino, kalina_confiable, fuera_rango, omitido, wnet_pos, T_fuente,
   T_sumidero, P_alta, P_baja, x_b, eta_t, eta_p, eps_hrvg, eps_reg, eps_cond, T_amb_diseno, eta_pct,
   Wnet, dP, rP, D, viol_O1, viol_O2, viol_O3, viol_O5`. Redondea a 5 cifras significativas.
   **Excluye KF-M08.**
2. Arma objetos JSON: `PUNTOS` (lista de filas, con las claves cortas tal cual), `CONDICIONES` (de
   `condiciones_por_subcaso.csv`), `BLOQUES` (de `bloques.csv`), `CASOS` (de `casos.csv`), `NOMBRE`,
   `ETIQUETA_CLASE` y `GLOSARIO` (de `nombres.py`), `COLOR_CLASE` = {KALINA #2E7D32, CORREGIBLE
   #EF8A17, INVIABLE #C9A227, NO_CONVERGIO #C62828, N2 #9E9E9E} y `FORMA_CLASE` = {KALINA circle,
   CORREGIBLE triangle, INVIABLE rect, NO_CONVERGIO crossRot, N2 crossRot}.
3. Inserta el CSS, los JSON (`<script>const DATOS = {...};</script>`) y el JS en la plantilla, y
   escribe `analisis_final/06_tablero/tablero_kalina.html`.

Chart.js se carga desde el CDN, exactamente con esta línea:
`<script src="https://cdn.jsdelivr.net/npm/chart.js@4.5.1" integrity="sha384-jb8JQMbMoBUzgWatfe6COACi2ljcDdZQ2OxczGA3bGNeWe+6DChMTBJemed7ZnvJ" crossorigin="anonymous"></script>`

## Diseño (HTML + CSS + JS sin frameworks, todo en español)

Encabezado oscuro con el título "Ciclo Kalina KCS-11 — resultados de la campaña final de barridos" y
tres pestañas (botones que muestran u ocultan secciones):

**Pestaña 1 — Resumen de la campaña**
- Tarjetas KPI calculadas en JS: corridas totales, % de puntos genuinos, KALINA confiables, número de casos.
- Barras horizontales apiladas: n por `clase_trazo` en cada `id_caso` (orden M01 → M10b).
- Tabla "Qué se fijó en cada barrido": una fila por `id_subcaso`, una columna por variable, y en cada
  celda "barrida", "= profesor" o el valor fijo (de `CONDICIONES`), con color de fondo por estado.

**Pestaña 2 — Explorador por bloque** (la principal)
- Filtros en fila: **Bloque** (select, de `BLOQUES`) → **Subcaso** (select con "Todos los del bloque"
  y los `id_subcaso` de ese bloque) → casillas por clase → casilla "Solo KALINA confiables" →
  casilla "Solo con W_net > 0".
- **Selectores de eje X e Y: ofrecen SOLO las variables con `estado = barrido` en el bloque elegido**
  (según `CONDICIONES`), más las derivadas `dP`, `rP` y `eta_pct`. Por defecto X = la primera barrida
  y Y = `eta_pct` si hay genuinos; si no, la segunda barrida. Los nombres se muestran con `NOMBRE`.
- Panel **"Condiciones de este bloque"**, siempre visible y al lado de los filtros: tabla de las
  variables fijas con su valor y unidad, con las que difieren del profesor resaltadas, y debajo la
  lista de las barridas con su rango. Si el bloque es inconsistente según `BLOQUES` (`consistente` = no),
  aparece un aviso amarillo con las diferencias. En bloques OAT (`es_oat` = sí) el panel se titula "Punto base: las demás variables
  quedan fijas en estos valores mientras se mueve una" y muestra `valor_base`; además, el selector de eje X filtra los puntos a
  `variable` == la variable elegida (así cada curva mueve una sola variable).
- Tarjetas KPI del filtro actual: corridas, genuinas, KALINA, KALINA confiables, η máx. KALINA [%] y
  criterio que más bloquea (el `viol_O*` más frecuente entre los genuinos no KALINA).
- Gráfico de dispersión (Chart.js `scatter`): una serie por clase, con su color y su forma
  (`pointStyle`); los fuera de rango con relleno transparente. El tooltip muestra `id_punto`, la clase, X, Y y η.
  `eta_pct` solo se dibuja en puntos con `genuino` y `wnet_pos`.
- Barras de bloqueo: n de genuinos no KALINA con `viol_O1`, `viol_O2`, `viol_O3` y `viol_O5` verdaderos.
- Texto de pie automático bajo el gráfico, armado igual que `pies.armar_pie` (caso, bloque, datos
  fijos, datos barridos, filtros activos, n y fuente "todos_los_puntos.csv").
- Tabla de puntos del filtro: columnas id_punto, clase, las variables barridas, η [%], W_net, ΔP, r_P
  y fuera de rango; ordenable al hacer clic en el encabezado; paginada de 50 en 50; botón "Descargar CSV"
  que exporta las filas filtradas (Blob + enlace de descarga).

**Pestaña 3 — Metodología y glosario**
- `GLOSARIO` completo como lista de definiciones.
- Tabla de casos (de `CASOS`) con n por clase.
- Un párrafo fijo: "Solo se comparan puntos de un mismo bloque: un bloque reúne puntos con las mismas
  variables fijas en los mismos valores. Las diferencias de η menores que 0.7 puntos porcentuales no
  son concluyentes (banda de incertidumbre del modelo de propiedades)."

Estilo: siguiendo la skill de dashboards. Fondo claro, tarjetas blancas con sombra suave, letra del
sistema y cuadrícula responsiva (en pantallas angostas, una columna). Incluye `@media print`. Sin
animaciones al filtrar (`chart.update('none')`). Ningún texto en inglés visible.

## Verificación (`a5_verificar.py`)

1. El HTML existe; imprime su tamaño en MB (debe ser < 15 MB).
2. Extrae el JSON embebido y comprueba que: n puntos == filas de la tabla canónica sin KF-M08;
   ninguna fila de `PUNTOS` tiene `bloque_director` vacío.
3. Para 3 bloques (B06, B07, B10), recalcula en Python los KPIs (corridas, genuinas, KALINA, KALINA
   confiables) y los imprime, para que el director los compare con lo que muestra el navegador.
4. Busca en el HTML palabras en inglés de interfaz ("Filter", "Download", "Show", "Page") e imprime
   las que encuentre.

## Comandos (cada uno con timeout = 7200000)

```
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\analisis_final\a5_tablero.py
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\analisis_final\a5_verificar.py
```

## Formato de salida

El obligatorio de `AGENTS.md`. En RESULTS, pega la salida de `a5_verificar.py`.
