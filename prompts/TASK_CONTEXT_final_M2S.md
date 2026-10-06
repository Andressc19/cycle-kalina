# TASK_CONTEXT — Campaña final, M2S: efecto de un sumidero frío (con P_baja libre y el piso de O2 = clima)

**Fecha:** 2026-10-06 · **Rama:** `test/barrido_final` (commit base `6dfc433`)
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barrido-final`.
TODO se crea y se ejecuta aquí.
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`
**Leer antes de empezar:**
- `scripts/barrido_final/comun.py` y `test_comun.py`;
- `scripts/barrido_final/m2_nivel2.py` (patrón de malla y bisección sobre P_baja);
- `resultados/barridos_2026-09-19/fase3_real/CASO_HUSAVIK_v2.md` §1, solo como contexto de por qué
  importa el piso de O2.

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`. NUNCA desde la
  terminal (nada de heredocs, here-strings, `Set-Content` ni `python -c` que escriba archivos).
- PowerShell 5.1: no existen `tee` ni `&&`. Para la corrida larga usa
  `Start-Process -RedirectStandardOutput ... -RedirectStandardError ...`, como en M2R, o `Tee-Object`.
- Las verificaciones van en un script escrito con `write`. Lanza la corrida larga UNA sola vez.

## Restricciones

- NO modificar `src/`, `app.py`, `ui_*.py` ni ningún script de `scripts/barrido_final/`, salvo
  `comun.py` y `test_comun.py` y solo como se indica en el paso 1. No tocar el Excel.
- Cada `.py` debe tener como máximo 200 líneas. No inventar valores. No hacer commit.
- **Otra tarea (M4) se lanzará en paralelo cuando termines el paso 1.** Después del paso 1 no
  vuelvas a tocar `comun.py`.

## Paso 1 — `comun.py`: piso de O2 por punto (cambio mínimo, retrocompatible)

- `evaluar_punto(combo, *, motor="teqp", tag=None, t_amb_diseno=None)`:
  - si `t_amb_diseno is None`, se usa `T_AMB_DISENO` (comportamiento actual, sin cambios);
  - si no, ese valor se pasa a `evaluar_ciclo(..., T_amb_diseno=...)` **y** a `margenes`.
- `margenes(backend, resultado, combo, t_amb_diseno=None)`: usa
  `max(T_sumidero, t_amb_diseno o T_AMB_DISENO)`.
- La fila guarda el piso usado en una columna nueva `T_amb_diseno`, que se añade a `COLS`.
- **El archivo debe seguir teniendo como máximo 200 líneas.**
- Tests en `test_comun.py` (también ≤ 200 líneas; si no cabe, crear `test_comun_piso.py`):
  1. el default no cambia;
  2. con `t_amb_diseno=283.15` y `T_sumidero=278.15`, `margenes` usa 283.15;
  3. con `T_sumidero` mayor que el piso, usa `T_sumidero`.
- Correr pytest sobre los tests de `scripts/barrido_final/`: todo en verde. **Imprimir la línea
  `PASO1_OK` en la terminal** cuando termine; el director la vigila para lanzar M4.

## Pregunta de M2S

Si el sitio es más frío y el criterio de cavitación se evalúa con **ese** clima
(piso de O2 = T_sumidero), ¿cuánto baja la P_baja necesaria para KALINA, y cuánto sube η?

## Diseño

**Bases**, con todo lo demás como `comun.PROFESOR`:

| Base | Cambios respecto al profesor |
|---|---|
| B1 | T_fuente = 403.0 (el ancla de M3) |
| B2 | T_fuente = 420.0 (el KALINA de mayor η en M2) |
| B3 | eps_hrvg = 0.40 (conserva la fuente de 623.15 K; ruta de M2R) |
| B4 | ninguno (el profesor exacto: ¿el sumidero frío solo basta?) |

- `T_sumidero ∈ {278.15, 283.15, 288.15, 293.15, 300.032917}`, siempre con
  `t_amb_diseno = T_sumidero` (el piso de O2 sigue al clima).
- `P_baja ∈ numpy.linspace(150, 1500, 10)`.
- **Malla:** 4 × 5 × 10 = **200 corridas**, en `ProcessPoolExecutor(max_workers=5)`. Cada fila se
  escribe con flush en `resultados/2026-10-06_final_M2S/m2s_malla.csv`, con las columnas
  `base, T_sumidero_val, P_baja_val` más las de `COLS`.
- **Bisección:** para cada (base, T_sumidero), sobre P_baja (tolerancia 10 kPa, como máximo 7
  iteraciones, en rondas paralelas), en cada par de vecinos donde cambie "es KALINA", o donde
  cambie `m_O2 >= 0` con ambos genuinos. Va en `m2s_biseccion.csv`.
- **Punto genuino:** `clasificacion ∈ {KALINA, CORREGIBLE, INVIABLE}`. Una fila con
  `convergio=True` y `NO_CONVERGIO` es espuria (N2) y se trata como NO genuina en todo.

## Salidas (en `resultados/2026-10-06_final_M2S/`)

- **`m2s_resumen.csv`**, por (base, T_sumidero):
  - `n_genuinos`, `n_kalina` y `n_N2`;
  - `P_baja_min_kalina` con su η, su `B_verificado` y su `fuera_rango`;
  - el η máximo entre los KALINA y su P_baja;
  - los bloqueantes genuinos.
- **`m2s_kalina.csv`**: los KALINA sin duplicados.
- **Figura `m2s_pbaja_eta.png`**, una curva por base:
  - η en la P_baja mínima KALINA vs T_sumidero;
  - en un segundo panel, la P_baja mínima vs T_sumidero.
- **`REPORTE_M2S.md`** en lenguaje llano:
  1. La pregunta.
  2. Qué se hizo.
  3. La tabla por base (filas: T_sumidero; columnas: la P_baja mínima KALINA y su η).
  4. Respuesta explícita: **¿el sumidero frío solo (B4) vuelve KALINA al profesor?**
  5. Cuánto sube η por cada 5 K de sumidero más frío, en cada base.
  6. Comparación con Húsavík (sumidero de 5 °C, piso de 10 °C, P_baja de 670–690 kPa, η de
     12.7–13.4 %; es otro ciclo: x_b = 0.82 y P_alta = 3300 kPa, así que la comparación es de
     tendencia, no de valor).
  7. Tiempos.
  8. Conclusión.
  9. Lo que no se sabe (fuera de rango, puntos de 278 K cerca del límite del motor).
  10. Qué sigue.

## Pasos

1. Paso 1 (`comun.py`, los tests y `PASO1_OK`).
2. Crear `scripts/barrido_final/m2s_corrida.py` y `m2s_reporte.py`.
3. Humo con `M2S_HUMO=1`: 1 base × 2 T_sumidero × 2 P_baja, con salida en `.../humo/`.
4. Corrida real y después el reporte.
5. Verificación con un script escrito con `write`: los conteos, que no haya duplicados y que los
   números del reporte coincidan con los CSV.

## Formato de salida

El obligatorio de `AGENTS.md`.
