# TASK_CONTEXT — Sensibilidad 2, B4: corrida del motor (densidades de 150 puntos y eta máxima frente a T_fuente)

**Fecha:** 2026-10-18 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree).
**Intérprete:** `..\..\..\.venv\Scripts\python.exe` (en PowerShell; en bash usa `../../../.venv/Scripts/python.exe`).
**Autorización:** el usuario autorizó expresamente estas corridas del motor (el «motor» es el programa que calcula el ciclo; cada punto es un cálculo completo del ciclo).
Tu rol es SOLO ejecutar los comandos de abajo y reportar; no edites ningún archivo ni analices resultados.

## Notas de entorno (OBLIGATORIAS)

- **NUNCA uses `cd`, `cd /d` ni rutas absolutas; no leas fuera de este directorio.** No hagas `git add/commit/stash/checkout/reset`.
- No edites ni crees archivos; los comandos escriben en `resultados/2026-10-18_sens2_B/` (escritura incremental; **relanzar el mismo comando reanuda**).
- Cada comando puede tardar mucho. Usa `timeout=1800000` (30 min); si el comando se corta por el tiempo, **relánzalo igual** hasta que imprima la línea `fin [...]`.
  Si un comando falla 3 veces seguidas con el mismo error, para y repórtalo en `ERRORS`.
- Lanza los comandos de uno en uno (nunca en paralelo): cada uno ya usa 5 procesos de cálculo.

## Comandos (en este orden)

1. Densidades (150 puntos):

```
../../../.venv/Scripts/python.exe scripts/sens2/s2b_corrida_dens.py DENS
```

2. Eta máxima frente a T_fuente (12 bandas, hasta 30 evaluaciones por banda):

```
../../../.venv/Scripts/python.exe scripts/sens2/s2b_opt_T.py 5
```

Al terminar ambos, ejecuta este conteo (solo lectura) y pégalo en `RESULTS`:

```
../../../.venv/Scripts/python.exe -c "import pandas as pd, glob; d=pd.read_csv('resultados/2026-10-18_sens2_B/s2b_dens_filas.csv'); print(d.clasificacion.value_counts()); print(d[['V3_m3s','V4_m3s','H_bomba_m']].describe()); o=pd.concat([pd.read_csv(f) for f in glob.glob('resultados/2026-10-18_sens2_B/s2b_opt_*.csv')]); print(o.groupby('banda').agg(n=('id_punto','size'), kalina=('clasificacion', lambda s: (s=='KALINA').sum()), eta_max=('eta','max')))"
```

## Aceptación

`s2b_dens_filas.csv` con 150 filas (ids únicos) y `s2b_opt_*.csv` con 12 archivos. Reporta los conteos del comando de arriba y cuántos puntos agotaron el tiempo
(`mensaje` que empiece por `tiempo_agotado`). Formato de salida de `AGENTS.md`.
