# TASK_CONTEXT — M9, rondas 2 y 3 de la escalera (complemento de `TASK_CONTEXT_final_M9.md` y `..._ronda1.md`)

**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barrido-final`
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`.
- PowerShell 5.1: no existen `tee` ni `&&`.
- La corrida va EN PRIMER PLANO, con el parámetro `timeout` de la herramienta shell en 7200000 ms, y
  se lanza UNA sola vez. Nada de `Start-Process`, `taskkill` ni `Stop-Process` por nombre.

## Restricciones

- NO modificar `src/` ni `comun.py`. Puedes editar `m9_*.py` y `excel_m9.py`, siempre con un máximo
  de 200 líneas cada uno. No hacer commit.
- NO repetir las rondas 0 ni 1: sus filas ya están en `m9_paso1.csv`, `m9_paso2.csv` (ronda=1) y
  `m9_escalera.csv`. Se reutiliza la reanudación de `m9_paso2.py`, como parámetros/entorno
  (`M9_P2_N`, `M9_P2_RONDAS`, `M9_P2_SIN_CORTE` o los que correspondan).

## Tarea

1. **Ronda 2.** S = {XB, PA} (el elegido de la ronda 1). Conjuntos `XB+PA+EF`, `XB+PA+PB`,
   `XB+PA+TS` y `XB+PA+TF`, cada uno con un LHS de **30 puntos**:
   - misma caja, misma regla de omitidos, piso O2 = T_sumidero del punto y pool de 7;
   - semillas: siguiendo el índice correlativo del paso 2 (sin repetir los de la ronda 1);
   - sin corte de tiempo;
   - filas con `ronda=2` en `m9_paso2.csv`; la ronda 2 se agrega a `m9_escalera.csv` con el mismo
     ranking (confiables → KALINA → D_min).
2. **Ronda 3, solo si el elegido de la ronda 2 tiene ≥ 1 KALINA.** S = el elegido de la ronda 2;
   cada grupo restante se suma con 30 puntos (`ronda=3`). Con S de 4 grupos se termina: el
   conjunto de 6 grupos es el punto del profesor, que ya se sabe NO_CONVERGIO (M1).
3. **Búsqueda dirigida** (regla del TASK_CONTEXT original: paso 0.15 → 0.02, máximo 40
   evaluaciones, se detiene en D = 0) para los conjuntos de la ÚLTIMA ronda corrida que tengan 0
   KALINA, como mucho 2 (los de menor D_min). Salida: `m9_busqueda.csv`.
4. **Volver a ejecutar** `m9_analisis.py`, `m9_figuras.py` y `m9_verificar.py`. En `REPORTE_M9.md`:
   - la escalera completa;
   - el conjunto máximo, contando **grupos y número de variables** conservadas;
   - qué grupo bloquea y con qué criterio;
   - si alguna ronda queda sin explorar, decirlo explícitamente.

   **CONSERVA la sección "Nota del director" que ya está al final de `REPORTE_M9.md`**: si el
   reporte se regenera, vuelve a añadirla al final, sin modificarla.
5. **Excel.** Ejecuta en orden `excel_final.py`, `excel_m2.py`, `excel_m3_m2r.py`, `excel_m2s_m4.py`,
   `excel_m5.py`, `excel_m5c_m7_m8.py`, `excel_m6.py`, `excel_m9.py` y `verificar_excel_m9.py`.

## Formato de salida

El obligatorio de `AGENTS.md`.
