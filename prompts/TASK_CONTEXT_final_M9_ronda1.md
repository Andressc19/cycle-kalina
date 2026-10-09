# TASK_CONTEXT — M9, ronda 1 de la escalera (complemento de `TASK_CONTEXT_final_M9.md`)

**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barrido-final`
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`.
- PowerShell 5.1: no existen `tee` ni `&&`.
- La corrida va EN PRIMER PLANO, con el parámetro `timeout` de la herramienta shell en 7200000 ms, y
  se lanza UNA sola vez. Nada de `Start-Process`, `taskkill` ni `Stop-Process` por nombre.

## Restricciones

- NO modificar `src/` ni `comun.py`. Puedes editar los scripts `m9_*.py` y `excel_m9.py` (los
  escribió la corrida anterior), siempre con un máximo de 200 líneas cada uno. No hacer commit.

## Contexto

En la corrida 072, el paso 1 terminó con este resultado (`m9_escalera.csv`, ronda 0): el elegido
es **XB** (15 KALINA confiables). El paso 2 se saltó por el corte de 3 h 15 min. El director decidió
correr AHORA la ronda 1, con menos puntos.

## Tarea

1. **Ronda 1 del paso 2.** S = {XB}. Conjuntos `XB∪TF`, `XB∪EF`, `XB∪PA`, `XB∪PB` y `XB∪TS`, cada
   uno con un LHS de **30 puntos**:
   - misma caja que en el paso 1, misma regla `P_baja ≥ P_alta − 300` → omitido, piso O2 =
     T_sumidero del punto y pool de 7;
   - semillas como dice `TASK_CONTEXT_final_M9.md`;
   - en esta corrida NO se aplica el corte de tiempo, y NO se corre la ronda 2.

   Las filas van a `resultados/2026-10-08_final_M9/m9_paso2.csv` (con `ronda=1`) y la ronda 1 se
   agrega a `m9_escalera.csv`, marcando `elegido` según el ranking del TASK_CONTEXT original.
2. **Búsqueda dirigida** (la misma regla del TASK_CONTEXT original, 40 evaluaciones como máximo)
   solo para los conjuntos de la ronda 1 que tengan 0 KALINA, como mucho 2 conjuntos (los de menor
   D_min). Salida en `m9_busqueda.csv`.
3. **Volver a ejecutar** `m9_analisis.py`, `m9_figuras.py` y `m9_verificar.py`, para que el reporte,
   los rangos y las figuras incluyan la ronda 1. En `REPORTE_M9.md` debe decir:
   - que la escalera llegó a 2 grupos conservados;
   - que la ronda 2 "no se exploró por presupuesto de tiempo" (NO "sin KALINA");
   - que la ronda 1 tiene 30 puntos por conjunto, así que es una exploración y no un mapa fino.
4. **Corregir `excel_m9.py`.** Hoy falla en `_fila_resumen` con `camp` = None (`TypeError:
   'NoneType' object is not subscriptable`, línea 79): no todas las hojas tienen columna de clases;
   para esas, la fila de `Resumen` se escribe sin conteos. Después ejecuta en orden `excel_final.py`,
   `excel_m2.py`, `excel_m3_m2r.py`, `excel_m2s_m4.py`, `excel_m5.py`, `excel_m5c_m7_m8.py`,
   `excel_m6.py`, `excel_m9.py` y `verificar_excel_m9.py`.

## Formato de salida

El obligatorio de `AGENTS.md`.
