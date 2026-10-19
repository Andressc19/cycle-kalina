# TASK_CONTEXT — Sensibilidad 2, B3: corrida del motor (pisos de P_baja a 25 kPa y reintento de NO_CONVERGIO)

**Fecha:** 2026-10-18 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree).
**Intérprete (ruta relativa):** `..\..\..\.venv\Scripts\python.exe`.
**Autorización:** el usuario autorizó expresamente estas corridas del motor (el «motor» es el programa que calcula el ciclo; cada punto es un
cálculo completo del ciclo). Tu rol es SOLO ejecutar los dos comandos de abajo y reportar; no edites ningún archivo ni analices resultados.

## Notas de entorno (OBLIGATORIAS)

- **NUNCA uses `cd`, `cd /d` ni rutas absolutas en la terminal; no leas fuera de este directorio.** PowerShell 5.1, sin `&&`. No hagas `git add/commit/stash/checkout/reset`.
- No edites ni crees archivos; los comandos ya escriben en `resultados/2026-10-18_sens2_B/s2b_filas.csv` (escritura incremental; **relanzar el mismo comando reanuda**).
- Cada comando puede tardar mucho. Usa `timeout=1800000` (30 min) en la herramienta de terminal; si el comando se corta por el tiempo, **relánzalo igual** (retoma donde quedó) hasta que
  imprima la línea `fin [...]`. Si un comando falla 3 veces seguidas con el mismo error, para y repórtalo en `ERRORS`.
- No ejecutes otros procesos del motor en paralelo (el director ya usa 5 procesos de cálculo por comando).

## Comandos (en este orden)

1. Pisos de P_baja (49 puntos, presupuesto normal):

```
..\..\..\.venv\Scripts\python.exe scripts\sens2\s2b_corrida.py PISOS
```

2. Reintento de NO_CONVERGIO con presupuesto mayor (90 puntos):

```
$env:S2B_PRESUPUESTO = "900"; $env:S2B_LIMITE = "1100"; ..\..\..\.venv\Scripts\python.exe scripts\sens2\s2b_corrida.py REINT0
```

Cuando ambos impriman `fin [...]`, ejecuta este conteo (solo lectura) y pégalo en `RESULTS`:

```
..\..\..\.venv\Scripts\python.exe -c "import pandas as pd; d=pd.read_csv('resultados/2026-10-18_sens2_B/s2b_filas.csv'); print(d.groupby(['barrido','clasificacion']).size())"
```

## Aceptación

`s2b_filas.csv` con 49 filas de PISOS y 90 de REINT0 (139 en total, ids únicos). Reporta en RESULTS el conteo por barrido y clasificación y cuántos puntos agotaron el tiempo
(`mensaje` que empiece por `tiempo_agotado`). Formato de salida de `AGENTS.md`.
