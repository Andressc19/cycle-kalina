# TASK_CONTEXT — M8 (ANECDÓTICO): η y ε fuera de los rangos realistas

**Fecha:** 2026-10-07 · **Rama:** `test/barrido_final` · **Prioridad: baja (curiosidad del usuario)**
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barrido-final`.
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`.
- PowerShell 5.1: no existen `tee` ni `&&`.
- La corrida va EN PRIMER PLANO, sin `Start-Process`, y se lanza UNA sola vez.

## Restricciones

- NO modificar `src/`, `comun.py` ni ningún script existente. Cada `.py` debe tener como máximo
  200 líneas. Solo motor teqp. No hacer commit.
- **Todo el reporte debe dejar claro que es ANECDÓTICO.** Los valores fuera de [0.40, 0.95] **no
  son realistas** para el proyecto: no son recomendaciones ni resultados de diseño.

## Pregunta

¿Cómo se comportan la clase, η y los márgenes si las eficiencias (η_t, η_p) y las efectividades
(ε_HRVG, ε_reg, ε_cond) se llevan **más allá** de lo realista, de 0.20 hasta 0.99?

## Diseño (OAT, una variable a la vez)

- **Puntos base:**
  - B1 = el ancla A\* (`dict(PROFESOR, T_fuente=403.0, P_baja=563.6363636363637)`), con piso de
    O2 = 300.032917;
  - B2 = el óptimo sin restricciones de M7 (de `resultados/2026-10-07_final_M7/m7_optimos.csv`,
    arranque A1). Si M7 no existe, se usa el top 1 de
    `resultados/2026-10-07_final_M4b/m4b_top_kalina.csv`, con piso de O2 = su T_sumidero.
- Para cada base y cada una de las 5 variables: los valores
  `[0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.93, 0.95, 0.97, 0.98, 0.99]`
  (16 valores), con el resto en la base. Son 2 × 5 × 16 = **160 corridas** con
  `ProcessPoolExecutor(max_workers=7)`.
- Cada fila se marca con `realista = (0.40 ≤ valor ≤ 0.95)`.

## Salidas (en `resultados/2026-10-07_final_M8_anecdotico/`)

- `m8_oat.csv`.
- `m8_curvas.png`: 2 × 5 paneles de η contra el valor, con el color de la clase, la franja
  realista sombreada y una línea vertical en el valor de la base.
- `REPORTE_M8.md`, con un encabezado bien visible: "ANECDÓTICO — fuera del rango realista". Por
  variable:
  - qué pasa con η y con la clase al salir del rango, por abajo y por arriba;
  - qué criterio se rompe;
  - si aparece algún comportamiento no monótono o inesperado (por ejemplo, η que baja al subir ε,
    puntos espurios o la falta de convergencia en los extremos).

## Pasos

1. Crear `m8_corrida.py` y `m8_analisis.py`.
2. Humo con `M8_HUMO=1`: 3 puntos.
3. Corrida real, el análisis y el reporte.
4. Verificar los conteos y que los números del reporte coincidan con el CSV.

## Formato de salida

El obligatorio de `AGENTS.md`.
