# TASK_CONTEXT — Campaña final, M2 nivel 1: ¿con UN solo cambio al enunciado del profesor aparece KALINA?

**Fecha:** 2026-10-06 · **Rama:** `test/barrido_final` (commit base `1b01096`)
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barrido-final`.
TODO se crea y se ejecuta aquí.
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`
**Leer antes de empezar:** `docs/METODOLOGIA_BARRIDOS_FINAL.md` (M2),
`docs/MATEMATICA_ITERACIONES_SENSIBILIDAD.md` (§2 y §4) y `scripts/barrido_final/comun.py`, que ya
existe, está probado y hay que reutilizarlo.

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`. NUNCA desde la
  terminal: nada de heredocs, here-strings, `Set-Content` ni `python -c` que escriba archivos.
- La terminal es Windows PowerShell 5.1. No existen `tee` ni `&&`: usa `Tee-Object` y `;`.
- Para verificaciones rápidas con Python, escribe un script en `scripts/barrido_final/` con `write`
  y ejecútalo; no uses `python -c` de varias líneas, porque PowerShell rompe las comillas.
- Lanza la corrida larga UNA sola vez y espera a que termine. No la repitas salvo que haya fallado.

## Restricciones

- NO modificar `src/`, `app.py`, `ui_*.py`, `scripts/formatear_excel_barridos.py` ni
  `scripts/barrido_final/m1_reproducir_f1.py`.
- Cada `.py` debe tener como máximo 200 líneas.
- No inventar valores, rangos ni fórmulas: todos están aquí. Lo que falte va a UNRESOLVED.
- Nunca reportar una ejecución que no ocurrió. Cada número tiene que salir de un archivo generado.
- No hacer commit.

## Qué es "nivel 1"

Desde el punto del profesor (`comun.PROFESOR`) se cambia **una sola variable** a la vez; las otras
10 quedan exactamente como dio el profesor. El objetivo es encontrar, para cada variable, si existe
un valor dentro de su rango con el que el punto **converge** y con el que es **KALINA**, y ubicar
esas fronteras con precisión.

## Rangos (fijados por el director; no cambiarlos)

| Variable | Tipo | Rango [a, b] | Tolerancia de bisección |
|---|---|---|---|
| P_alta (kPa) | diseño | [1000, 10000] | 10 |
| P_baja (kPa) | diseño | [150, 1500] | 10 |
| x_b (−) | diseño | [0.30, 0.90] | 0.005 |
| eta_t (−) | diseño | [0.75, 0.90] | 0.005 |
| eta_p (−) | diseño | [0.65, 0.85] | 0.005 |
| eps_hrvg (−) | diseño | [0.75, 0.85] | 0.005 |
| eps_reg (−) | diseño | [0.75, 0.85] | 0.005 |
| eps_cond (−) | diseño | [0.75, 0.85] | 0.005 |
| T_fuente (K) | sitio | [340, 623.15] | 0.5 |
| T_sumidero (K) | sitio | [283.15, 303.55] | 0.5 |

`m_b` no se barre: es la base de cálculo.

## Archivos a crear o modificar

### 1. `scripts/barrido_final/comun.py` (EDITAR, cambio mínimo)

Añadir la columna `codigos_falla` a `COLS`. En la rama donde converge, rellenarla con los códigos
de `val.fallas` unidos por coma (por ejemplo `"O2,O1"`), o `""` si es KALINA. No cambiar nada más.
Añadir un test en `test_comun.py` que lo cubra con un `evaluar_ciclo` simulado mediante monkeypatch.

### 2. `scripts/barrido_final/m2_nivel1.py` (NUEVO)

**Fase A — malla gruesa.** Para cada una de las 10 variables, 10 valores equiespaciados
`numpy.linspace(a, b, 10)`. Cada valor reemplaza a la variable en `PROFESOR`. Son 100 corridas con
`evaluar_punto(combo, motor="teqp", tag=f"{var}={valor:g}")`, en `ProcessPoolExecutor(max_workers=6)`.
- Cada fila se escribe con flush en `resultados/2026-10-06_final_M2/m2n1_malla.csv`, con las
  columnas `fase="malla"`, `variable` y `valor`, más todas las de `comun.COLS`.
- Después de cada fila se imprime `[n/100] var=valor clase t_s`.

**Fase B — bisección de fronteras.** Para cada variable, se ordenan sus 10 puntos por valor y se
detecta cada par de vecinos (v_j, v_{j+1}) donde cambia:
- (i) `convergio` (frontera "convergencia"), o
- (ii) `clasificacion == "KALINA"` (frontera "KALINA").

Cada frontera se refina por bisección:
- Se evalúa `v_m = (lo + hi)/2` y se reemplaza el extremo del mismo lado (mismo valor del criterio
  de esa frontera).
- Se para cuando `hi − lo < tol` o tras 10 iteraciones.
- Todas las fronteras activas avanzan **en paralelo por rondas**: en cada ronda se envían al pool
  todos los puntos medios pendientes.
- Cada evaluación se escribe con flush en `m2n1_biseccion.csv`, con las columnas `fase="biseccion"`,
  `variable`, `frontera`, `iteracion` y `valor`, más las de `COLS`. Se imprime
  `[ronda k] var frontera lo..hi`.

**Resultado de fronteras** (`m2n1_fronteras.csv`): una fila por frontera con
`variable, tipo (diseño/sitio), frontera, lado_si (valor del extremo que SÍ cumple), lado_no,
ancho_final, iteraciones, clase_lado_si, D_lado_si, codigos_falla_lado_si`.

**Resumen por variable** (`m2n1_resumen.csv`), una fila por cada una de las 10 variables:
- `n_converge`, `n_kalina`, `n_corregible`, `n_inviable` y `n_no_convergio` (contando malla y bisección);
- `valor_conv_mas_cercano_prof`: el valor convergido más cercano al del profesor;
- `valor_kalina_mas_cercano_prof`: el valor KALINA más cercano al del profesor;
- `d_normalizada = |v − v_prof|/(b − a)` del valor KALINA más cercano, o vacío si no hay ninguno;
- `D_minimo` y su valor;
- `criterios_bloqueantes_frecuentes`: los códigos más frecuentes en `codigos_falla` de los
  convergidos que no son KALINA.

### 3. `REPORTE_M2_N1.md` (lo genera el script, en lenguaje llano)

Secciones:
1. La pregunta.
2. Qué se hizo: la malla y la bisección, explicadas en simple.
3. Tabla por variable, primero las de diseño y luego las de sitio:
   `¿converge en algún valor? | ¿KALINA en algún valor? | valor KALINA más cercano al profesor y su
   d | mejor D | criterio que más bloquea`.
4. Las fronteras encontradas, con su precisión.
5. Tiempos.
6. Conclusión literal, con la forma: "Con un solo cambio sí/no se alcanza KALINA; las variables que
   lo logran son … y el cambio mínimo es …". Si ninguna lo logra: "ninguna variable sola lo logra;
   las que al menos hacen converger el ciclo son …, y el criterio que queda bloqueando es …".
7. Lo que no se sabe (por ejemplo, la resolución de la malla y los posibles huecos entre puntos de
   la malla).
8. Qué sigue: el nivel 2 lo decide el director; no proponer pares concretos como si fueran resultados.

Además, marcar con una nota los valores de `x_b` menores que 0.55 que resulten convergidos o KALINA:
el proyecto los considera "x_b bajo, no preferido". Se reportan igual, sin ocultarlos.

### 4. `scripts/barrido_final/excel_m2.py` (NUEVO)

Abre `datos/Excel_final_kalina.xlsx`, ya creado por `excel_final.py`. Crea o reemplaza las hojas
`M2_N1_malla`, `M2_N1_biseccion`, `M2_N1_fronteras` y `M2_N1_resumen`, reutilizando
`escribir_tabla` de `excel_final.py` por importación, con el mismo formato y descripción. También
añade o actualiza las filas de esas hojas en `Resumen`. Si se vuelve a ejecutar, el resultado tiene
que ser el mismo. Unidades nuevas: `valor` (según la variable, o "(−)"), `ancho_final`, `lado_si`,
`lado_no` y `d_normalizada (−)`.

## Pasos

1. Editar `comun.py` y `test_comun.py`. Correr
   `python -m pytest scripts/barrido_final/test_comun.py -q`: todo debe pasar.
2. Crear `m2_nivel1.py` y `excel_m2.py`.
3. Humo: correr el script con la variable de entorno `M2_HUMO=1`, que limita la malla a 2
   variables × 2 valores, sin bisección, y escribe en `resultados/2026-10-06_final_M2/humo/`.
   Comprobar que la salida es coherente.
4. Corrida real:
   `python scripts/barrido_final/m2_nivel1.py 2>&1 | Tee-Object -FilePath resultados/2026-10-06_final_M2/stdout.txt`.
   Duración esperada: 30–60 min.
5. `python scripts/barrido_final/excel_final.py; python scripts/barrido_final/excel_m2.py`.
6. Verificar con un script de comprobación (escrito con `write`): el número de filas de cada CSV,
   las hojas del xlsx y que cada número del reporte coincide con los CSV.

## Formato de salida

El obligatorio de `AGENTS.md`. En RESULTS va la tabla resumen por variable (las 10 filas) y las
rutas de los archivos generados.
