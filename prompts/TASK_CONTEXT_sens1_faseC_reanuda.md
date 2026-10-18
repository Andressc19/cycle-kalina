# TASK_CONTEXT — Sensibilidad 1, Fase C: REANUDAR con tope duro por punto

**Fecha:** 2026-10-14 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree). TODO se
crea y se ejecuta aquí.
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`
**Contexto:** la corrida de `scripts/sens1/faseC_corrida.py` (TASK_CONTEXT_sens1_faseC.md) se atascó: tras
124 puntos evaluados (todos del centro C1), los 5 procesos quedaron más de 15 min dentro de puntos que no
cierran (el tope de `PRESUPUESTO_S=300` no cubre todos los lazos internos). El usuario autorizó
detenerlos. Los 124 puntos están en `resultados/2026-10-14_sens1_faseC/faseC_filas.csv` (copia de seguridad:
`faseC_filas_parte1.csv`). **No se pierden: se reanuda.**

## Notas de entorno (OBLIGATORIAS)

- Archivos SOLO con las herramientas `write` y `edit`. NUNCA desde la terminal (nada de `cat <<`,
  here-strings, `Set-Content`, `python -c` que escriba archivos).
- Terminal = Windows PowerShell 5.1, solo para EJECUTAR. Sin `&&` (usa `;`).
- No imprimas Unicode (η, ε…) en consola: solo ASCII en los `print`.
- **La corrida tarda ~1.5–2 h. Pasa `timeout=7200000` a la herramienta de shell.** En primer plano, sin
  `Start-Process`; no la relances si tarda.

## Restricciones

- **NO modificar `src/`, `app.py`, `ui_*.py`, `scripts/barrido_final/comun.py`.**
- NO borrar ni reescribir las 124 filas existentes de `faseC_filas.csv`: solo se **añaden** filas
  nuevas al final (modo `a`). No toques `faseC_filas_parte1.csv`.
- Cada `.py`: máximo 200 líneas.
- No inventes valores; lo que falte, a UNRESOLVED. Cada número del reporte sale de un archivo generado.

## Paso 1 — Crear `scripts/sens1/faseC_reanuda.py`

1. **Reproduce exactamente la misma muestra LHS** de `faseC_corrida.py` (misma semilla 20261014, mismas
   cajas, mismo redondeo, mismos `id_punto`). Importa la función de muestreo de `faseC_corrida.py` si
   está expuesta (sin ejecutar `main`); si no, copia su lógica **sin cambiarla**.
2. **Verificación de consistencia (obligatoria):** compara los 124 `id_punto` ya presentes en
   `faseC_filas.csv` con la muestra regenerada: sus valores de las 9 variables deben coincidir. Si algún
   id difiere, DETENTE y repórtalo en UNRESOLVED sin correr nada.
3. **Salta** todos los `id_punto` ya presentes y evalúa solo los faltantes (≈376: los que quedaron de C1 y
   los 250 de C2).
4. **Tope duro por punto: 600 s.** NO uses `ProcessPoolExecutor` (no puede matar un worker atascado).
   Usa `multiprocessing.Process` (contexto `spawn`) con una cola o tubería, **5 procesos simultáneos**:
   cada punto va en su propio proceso, que llama a `evaluar_punto(combo, motor="teqp", tag=id,
   t_amb_diseno=combo["T_sumidero"], extra=True)` y devuelve la fila. El proceso padre espera cada
   punto con un plazo de 600 s; si vence, **termina el proceso (`terminate()` y `join`)** y registra la
   fila con `convergio=False`, `clasificacion="NO_CONVERGIO"`, `mensaje="tiempo_agotado_600s"`,
   `t_s=600`, y las 9 variables del punto (el resto de columnas vacías). El padre lanza el siguiente
   punto en cuanto se libera una ranura.
5. Escritura **incremental** en `faseC_filas.csv` (modo `a`, mismas columnas y orden que el archivo
   existente; **lee su encabezado** y úsalo), con `flush` en cada fila. `id_punto`, `centro` y
   `tipo="lhs"` como antes.
6. Imprime (solo ASCII) `[n/total] id clase t_s` por punto y, al final, cuántos agotaron el tiempo.
   El log va a `resultados/2026-10-14_sens1_faseC/faseC_log_reanuda.txt`.

## Paso 2 — Ejecutar

```
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\sens1\faseC_reanuda.py 2>&1 | Tee-Object -FilePath resultados\2026-10-14_sens1_faseC\faseC_log_reanuda.txt
```

(Si falla `Tee-Object`, usa `| tee`.)

## Paso 3 — Reporte del análisis

Cuando la corrida termine con 500 puntos en `faseC_filas.csv` (o menos si hay duplicados tras el
redondeo; cuéntalo), ejecuta los **Pasos 3, 4 y 5 de `prompts/TASK_CONTEXT_sens1_faseC.md`** tal como
están escritos (scripts `faseC_reporte.py` / `faseC_reporte2.py`: ventanas, KS, PRCC, top10, equipos,
resumen). Los puntos con `tiempo_agotado_600s` son NO_CONVERGIO y NO cuentan como puntos genuinos.
Añade al resumen una línea con cuántos puntos agotaron el tiempo, de qué centro y en qué zona
(mín/máx de cada variable entre ellos).

## Paso 4 — Reporte final

Formato obligatorio de `AGENTS.md`. En RESULTS: nº de ids saltados, nº evaluados, nº con tiempo agotado,
nº de puntos y clases por centro, y las cifras que pide el Paso 5 del TASK_CONTEXT original.
