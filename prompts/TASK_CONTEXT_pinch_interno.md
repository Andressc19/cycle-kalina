# TASK_CONTEXT — Corrección 4: pinch interno (regenerador, HRVG, condensador)

**Fecha:** 2026-10-13 · **Rama:** `feature/solucion-4`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barrido-final`
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`. NUNCA desde la
  terminal.
- PowerShell 5.1: no existen `tee` ni `&&`. Se usa `Tee-Object`.
- Toda corrida va EN PRIMER PLANO, con el parámetro `timeout` de la herramienta shell en
  **7200000** ms (por defecto son 120 s y mata la corrida). Se lanza UNA sola vez por paso.
  Nada de `Start-Process`, `taskkill` ni `Stop-Process` por nombre.
- UN comando exacto por paso (los de abajo). No inventes helpers: `comun.py` no tiene helpers de
  CSV; todo el código que necesitas ya está escrito en los tres scripts de abajo.

## Restricciones

- NO modificar `src/`, `app.py`, `ui_*.py`, tests, datos originales ni `scripts/barrido_final/`.
- NO introducir caudales, capacidades caloríficas de gases ni fuente finita.
- NO escribir conclusiones en el reporte; solo ejecutar y mostrar los números. NO hacer commit.
- Los scripts ya existen y NO se editan, salvo para corregir un error de sintaxis o de import
  (repórtalo en `ERRORS`). Si algo exige cambiar la física o la selección de puntos, repórtalo
  en `UNRESOLVED`, no lo arregles.
- No leas ni listes rutas fuera de este directorio.

## Qué hace la sonda (ya implementado)

- `scripts/pinch_interno_muestra.py`: elige los puntos (lee `analisis_final/01_datos/
  todos_los_puntos.csv` y `resultados/2026-09-24_validacion_tendencias/validacion_tendencias.csv`).
  Grupos: `A_estrella`, `opt_5_1`, `franja_4_2`, `final_4_3`, `husavik`, `elsayed` (23 puntos),
  `estratificada` (3.2 y 5.1 por ε_reg × ε_HRVG), `extremos`, `real` (motor real).
- `scripts/pinch_interno.py`: resuelve cada punto con `resolver_ciclo` (teqp, o motor real en el
  grupo `real`) y discretiza: regenerador a contracorriente en 100 tramos, HRVG y condensador en 40.
  Escribe `pinch_puntos.csv` y `perfiles_todos.csv` con flush por punto.
- `scripts/pinch_interno_reporte.py`: `pinch_resumen.csv`, `perfiles_ejemplo.csv`,
  `pinch_regenerador.png`.

## Pasos (en este orden; si un paso falla, DETENTE y reporta)

**Paso 0 — selección (segundos).** Comando exacto:

```
& "D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe" scripts\pinch_interno_muestra.py 2>&1 | Tee-Object -FilePath resultados\2026-10-13_pinch_interno\stdout_muestra.txt
```

Reporta el número de puntos por grupo.

**Paso 1 — humo (3 puntos: A*, un Elsayed y uno estratificado, los tres con teqp).** Comando exacto:

```
$env:PINCH_HUMO = "1"; $env:PINCH_N_WORKERS = "3"; & "D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe" scripts\pinch_interno.py 2>&1 | Tee-Object -FilePath resultados\2026-10-13_pinch_interno\stdout_humo.txt
```

Salida en `resultados/2026-10-13_pinch_interno/humo/`. Comprueba y reporta: que los 3 puntos
tengan `convergio=True`, que `reg_pinch_K` no sea vacío, que `perfiles_todos.csv` tenga 183 filas
por punto, y el `t_s` de cada uno. Si el humo falla, NO sigas con el paso 2.

**Paso 2 — corrida completa (6 procesos, ≈ 1–2 h).** Comando exacto:

```
$env:PINCH_HUMO = "0"; $env:PINCH_N_WORKERS = "6"; & "D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe" scripts\pinch_interno.py 2>&1 | Tee-Object -FilePath resultados\2026-10-13_pinch_interno\stdout_corrida.txt
```

**Paso 3 — resumen, perfiles de ejemplo y figura.** Comando exacto:

```
& "D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe" scripts\pinch_interno_reporte.py 2>&1 | Tee-Object -FilePath resultados\2026-10-13_pinch_interno\stdout_reporte.txt
```

## Qué reportar en RESULTS

- Puntos por grupo (paso 0) y tiempo total del paso 2.
- Del `stdout_reporte.txt`: la tabla completa de `pinch_resumen.csv` (todos, por motor, por
  grupo, por bin de ε_reg y de ε_HRVG), y la línea de ε_reg mínimo con cruce si existe.
- Cuántos puntos quedaron `NO_CONVERGIO` o `NO_EVALUADO` y el motivo (`mensaje`) más frecuente.
- Para los 4 puntos del grupo `real`: pinch del regenerador y diferencia frente a su par teqp
  (mismo `tag` sin el sufijo `_real`).

## Formato de salida

El obligatorio de `AGENTS.md`.
