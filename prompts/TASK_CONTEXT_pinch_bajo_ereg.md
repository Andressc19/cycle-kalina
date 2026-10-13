# TASK_CONTEXT — Corrección 4, ronda corta con ε_reg < 0.60

**Fecha:** 2026-10-13 · **Rama:** `feature/solucion-4`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barrido-final`
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y modifican SOLO con las herramientas `write` y `edit`.
- PowerShell 5.1: no existen `tee` ni `&&`. Se usa `Tee-Object`.
- La corrida va EN PRIMER PLANO, con el parámetro `timeout` de la herramienta shell en
  **7200000** ms, y se lanza UNA sola vez. Nada de `Start-Process`.
- UN comando exacto. No inventes helpers.

## Restricciones

- NO modificar `src/`, `app.py`, `ui_*.py`, tests, datos ni ningún script existente.
- NO leer ni listar rutas fuera de este directorio. NO hacer commit.
- Sin caudales ni fuente finita.

## Paso único

`scripts/pinch_interno_bajo_ereg.py` toma 5 puntos base ya medidos y cambia SOLO ε_reg a 0.40 y
0.55 (10 puntos, teqp). Comando exacto:

```
& "D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe" scripts\pinch_interno_bajo_ereg.py 2>&1 | Tee-Object -FilePath resultados\2026-10-13_pinch_interno\stdout_bajo_ereg.txt
```

Salida en `resultados/2026-10-13_pinch_interno/bajo_ereg/`. Si falla por sintaxis o import,
corrige solo eso y repórtalo en `ERRORS`.

## Qué reportar en RESULTS

La tabla completa de las líneas `[n/10]` (tag, ε_reg, clase, pinch, pos_f, T1, T_bub, t_s) y el
número de puntos `CRUCE`, `SIN_CRUCE_ESTRECHO` y `SIN_CRUCE_AMPLIO`. No escribas conclusiones.

## Formato de salida

El obligatorio de `AGENTS.md`.
