# TASK_CONTEXT — Sensibilidad 2, U1: propagación de incertidumbre (384 puntos del motor)

**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree).
**Intérprete (ruta relativa):** `..\..\..\.venv\Scripts\python.exe`

## Notas de entorno (OBLIGATORIAS)

- **NUNCA uses `cd`, `cd /d` ni rutas absolutas en la terminal; no leas fuera de este directorio.**
- PowerShell 5.1, sin `&&` (usa `;`). Solo ASCII en los `print`. **NO ejecutes `pytest`.** No crees ni edites
  archivos: esta tarea solo ejecuta dos comandos ya escritos por el director.
- La corrida es larga: usa `timeout=7200000` en la herramienta de shell, en primer plano, sin `Start-Process`.
  Si la invocación se corta, relanza el MISMO comando (el corredor salta los puntos ya escritos y reanuda).

## Qué ejecutar (en este orden, uno por uno)

```
..\..\..\.venv\Scripts\python.exe scripts\sens2\u1_corrida.py U1A
..\..\..\.venv\Scripts\python.exe scripts\sens2\u1_corrida.py U1B
```

Cada uno evalúa 192 puntos con el motor (un proceso por punto, 5 simultáneos, tope duro de 600 s por punto) y
escribe en `resultados/2026-10-17_sens2_U1/u1_filas.csv`. No modifiques ningún archivo. Si un comando termina
antes de procesar los 192 puntos (por corte), relánzalo hasta que imprima «fin [U1A]» o «fin [U1B]».

## Reporte (formato de `AGENTS.md`)

En RESULTS: la última línea «fin [...]» de cada comando (nº de puntos nuevos, tiempo y cuántos agotaron 600 s) y
el número de filas de `u1_filas.csv`. No inventes números: copia la salida.
