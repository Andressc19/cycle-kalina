# TASK_CONTEXT — A5b: correcciones al tablero HTML (revisión del director en el navegador)

**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\af-tablero`
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`
**Contexto:** continuación de `prompts/TASK_CONTEXT_af_A5_tablero.md` (léelo). Los archivos
`scripts/analisis_final/a5_*` ya existen.

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`.
- PowerShell 5.1: no existen `tee`, `tail`, `head` ni `&&`. Cada comando con el PARÁMETRO `timeout` de la
  herramienta shell = 7200000, en primer plano.
- No leer nada fuera de `D:\Desktop\ciclo_kalina_tercero`. No descargar nada. Modificar SOLO
  `scripts/analisis_final/a5_*` y regenerar `analisis_final/06_tablero/tablero_kalina.html`. No hacer commit.
- Límites de líneas: `.py` ≤ 200; `.js`, `.css` y `.html` ≤ 300 cada uno. Si `a5_app.js` se pasa,
  pártelo en `a5_app.js` + `a5_graficos.js` (el `.py` los une en orden).

## Correcciones

### C1 — CRÍTICA: los gráficos del Explorador no se ven
En la pestaña "Explorador por bloque", los canvas `graf-disp` y `graf-bloq` miden 0 × 0 px, aunque su
contenedor `.lienzo.alto` mide 420 px. Causa probable: los gráficos se crean mientras la sección está
oculta y no se redimensionan al mostrarla. Solución:
- Al cambiar de pestaña, después de mostrar la sección, llama a `chart.resize()` en todos los
  gráficos de esa sección, dentro de un `requestAnimationFrame`.
- Además, si un gráfico se crea con la sección oculta, créalo recién la primera vez que se muestra.
- El canvas debe ocupar el contenedor (`width: 100%`, `height: 100%`), con `responsive: true` y
  `maintainAspectRatio: false`.

### C2 — El selector de bloque dice qué es cada bloque
Hoy solo muestra el código (`B07`). Que cada opción diga
`<bloque> · <id_caso(s)> · <descripción corta>`, por ejemplo
`B07 · KF-M04 + KF-M04b · muestreo LHS de 500 puntos`. Usa este diccionario literal de
descripciones por prefijo (en `a5_tablero.py`, constante `DESCRIPCION_BLOQUE`):

| Prefijo | Descripción |
|---|---|
| B01 | reproducción del caso del profesor |
| B02 | un solo cambio sobre el profesor |
| B03-A | dos cambios, ruta A: ε_HRVG y P_baja |
| B03-B | dos cambios, ruta B: T_fuente y P_baja |
| B04 | η y ε en [0.40, 0.95], parte {sufijo} |
| B05 | sumidero frío, base {sufijo} |
| B06 | sensibilidad local alrededor de A* |
| B07 | muestreo LHS de 500 puntos |
| B08 | LHS con P_baja de 1500 a 2500 kPa |
| B09 | conservando datos del profesor, escenario S{sufijo} |
| B10 | presiones del profesor: franja T_fuente × ε_cond |
| B11 | búsqueda de η máxima, arranque {sufijo} |
| B12 | puntos de control (verificación) |
| B13 | escalera de conservación: {sufijo} |
| B14-F3 | Húsavík: re-evaluación de la Fase 3 |
| B14-MALLA | Húsavík: malla x_b × P_baja |
| B14-OFAT | Húsavík: una variable a la vez |
| B14-OFATb | Húsavík: x_b bajo (0.30–0.70) |

### C3 — El panel de condiciones nombra el punto base
Encima de la tabla de condiciones, agrega una línea "Punto base: …" con este texto literal según el bloque:
- B01, B02, B03-*, B04-*: "PP = datos del enunciado del profesor"
- B05-B1: "PP con T_fuente = 403 K (la fuente de A*)"; B05-B2: "PP con T_fuente = 420 K";
  B05-B3: "PP con ε_HRVG = 0.40"; B05-B4: "PP exacto"
- B06: "A* = punto del profesor con T_fuente = 403 K y P_baja = 563.64 kPa (KALINA, η = 8.48 %)"
- B14-*: "Ancla de Húsavík: P_alta 3300 kPa, P_baja 690 kPa, T_fuente 394.15 K, T_sumidero 278.15 K"
- Los demás: "Sin punto base: las variables barridas se sortean dentro de su rango"
Además, las celdas de valor que difieren del profesor van en **negrita** y con un "*" visible al lado
del número. Hoy el asterisco no se ve.

### C4 — KPIs claros en bloques de una variable a la vez
En bloques OAT (`es_oat`), las tarjetas KPI se calculan solo con los puntos de la variable del eje X.
Agrega bajo las tarjetas el texto: "Cifras de los puntos donde se mueve <nombre de la variable X>;
las demás variables están en el punto base."

### C5 — Tabla "Qué se fijó en cada barrido" (pestaña Resumen)
- En las filas de subcasos OAT (`es_oat` = sí), en vez de "barrida" en cada columna, escribe
  "una a la vez" con un color propio, y agrega al nombre del subcaso " (una variable a la vez)".
- Cuando `T_amb_diseno` no tenga dato (M1–M3), escribe "300,03 K (por protocolo)".
  **Fuente:** el piso de O2 de M1–M3 fue 300.032917 K, según `docs/METODOLOGIA_BARRIDOS_FINAL.md` §0.

### C6 — Accesibilidad
Las dos casillas "Solo KALINA confiables" y "Solo con W_net > 0" tienen que tener su `<label for=…>`
asociado (hoy el lector de pantalla las lee como "on").

## Verificación (`a5_verificar.py`, ampliado)

Además de lo que ya verifica:
- Comprueba con una expresión regular que exista en el JS una llamada a `resize()` dentro del manejador de cambio de pestaña.
- Imprime 5 opciones del selector de bloque, tal como quedan en el HTML.
- Comprueba que `DESCRIPCION_BLOQUE` cubre todos los `bloque_director` (ninguno sin descripción).

## Comandos (cada uno con timeout = 7200000)

```
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\analisis_final\a5_tablero.py
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\analisis_final\a5_verificar.py
```

## Formato de salida

El obligatorio de `AGENTS.md`.
