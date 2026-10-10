# TASK_CONTEXT — A4: validación cruzada de las cifras de los reportes contra la tabla canónica

**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\af-validacion`
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`
**Entrada:** `analisis_final/01_datos/todos_los_puntos.csv` (columnas en `docs/METODOLOGIA_ANALISIS_RESULTADOS.md`
§2.3 y en `prompts/TASK_CONTEXT_af_A1_datos.md` §2) y `analisis_final/00_inventario/*.csv`.

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`.
- PowerShell 5.1: no existen `tee`, `tail`, `head` ni `&&`.
- **Cada comando con el PARÁMETRO `timeout` de la herramienta shell = 7200000**, en primer plano.
- No leer nada fuera de `D:\Desktop\ciclo_kalina_tercero`. No modificar nada fuera de
  `scripts/analisis_final/a4_*.py` y `analisis_final/05_validacion/`. No hacer commit.
- Scripts de 200 líneas como máximo. Percentiles con `numpy.percentile` (método lineal, el de defecto).

## Objetivo

Recalcular desde la tabla canónica cada cifra que la metodología (§3.2) y los reportes dan por buena,
y marcarla ✔ (coincide) o ✘ (no coincide), con el valor esperado, el valor recalculado y el filtro
usado. **No corrijas nada; solo mide y reporta.**

Definiciones (literal): genuino, es_N2, kalina_confiable, omitido, wnet_pos ya vienen como columnas.
Tolerancias: conteos exactos; η ±0.0005 (en tanto por uno); presiones ±1 kPa; temperaturas ±0.5 K;
r_P ±0.01.

## Checks (`a4_checks.py`, una función por caso; `a4_validar.py` los corre todos)

| ID | Caso / filtro | Cifra esperada |
|---|---|---|
| V01 | KF-M01, todas las filas | 42 filas; las 42 NO_CONVERGIO o N2 (ninguna genuina) |
| V02 | KF-M02-N1 (malla + bisección) | 0 KALINA |
| V03 | KF-M02-N2-A | 0 KALINA |
| V04 | KF-M02-N2-B | KALINA en T_fuente ∈ {390, 403, 420, 434} K y en ningún otro valor de T_fuente; la menor P_baja KALINA es 445.455 kPa con η = 0.0245 (en T_fuente 390) |
| V05 | KF-M02-N2-B, KALINA | n KALINA = 59 (filas); n KALINA fuera de rango = 11 |
| V06 | KF-M02R | n KALINA = 14 (filas) y fuera de rango = 13 |
| V07 | KF-M02S | n KALINA únicos por (base, T_sumidero, P_baja) = 123; la base B4 tiene 0 KALINA |
| V08 | KF-M02S, por base B1/B2/B3 | η máxima KALINA y P_baja mínima KALINA en T_sumidero 278.15 y 300.032917: B1 (0.1041; 290.625) / (0.0849; 562.5); B2 (0.1191; 393.75) / (0.0911; 740.625); B3 (0.0969; 750) / (0.0630; 1312.5). Si el reporte usó otra definición (por ejemplo, η en la P_baja mínima), dilo |
| V09 | KF-M03 | 171 filas; 148 genuinas; 86 KALINA; 8 fuera de rango |
| V10 | KF-M03, `tipo_punto` = malla, genuinas con wnet_pos | Δη (pp) por `variable` = (máx − mín) × 100: x_b 10.78; P_baja 6.80; eps_hrvg 6.69; eta_t 6.32; P_alta 5.14; eps_reg 4.99; T_fuente 3.67; eta_p 1.38; T_sumidero 0.85; eps_cond 0.82 (±0.02 pp) |
| V11 | KF-M03, KALINA de la malla | η máxima KALINA por variable: eps_reg 0.1096 en 0.95; eta_t 0.0962 en 0.95 |
| V12 | KF-M04 + KF-M04b | 500 filas; 121 KALINA; 222 fuera de rango |
| V13 | KF-M04 + KF-M04b, KALINA | p5–p95: P_alta [2155.69, 4841.78]; P_baja [683.165, 1460.71]; dP [968.027, 3717.63]; rP [1.68614, 5.33942] |
| V14 | KF-M04c | 150 filas; 15 omitidas; 135 evaluadas |
| V15 | KF-M05 (subcasos KF-M05-1 … KF-M05-5 = escenarios S1…S5) | 600 filas; 2 omitidas; KALINA por escenario: 1 → 4, 2 → 0, 3 → 0, 4 → 6, 5 → 10; fuera de rango 322 de 598 evaluadas |
| V16 | KF-M05c | 165 filas; 104 KALINA |
| V17 | KF-M07, KALINA, por arranque | η máxima: A1 0.1498; A2 0.1548; A3 0.1274; A4 0.1560; A5 0.1109 |
| V18 | KF-M09, por subcaso | Recontar n filas, genuinas, KALINA y KALINA confiables por (ronda, conservados) y compararlo con `resultados/2026-10-08_final_M9/m9_escalera.csv` (columnas n_eval, n_genuinos, n_kalina, n_kalina_confiable), fila por fila |
| V19 | KF-M09-R3 con conservados XB+PA+EF+PB | 5 KALINA, 5 confiables; T_fuente de los KALINA en [391, 409] K y T_sumidero en [280, 293] K (redondeado al entero) |
| V20 | KF-M09, conservados que incluyen TF | 0 KALINA confiables en todas las rondas |
| V21 | KF-M10-F3 | 97 filas; 97 KALINA |
| V22 | KF-M10-MALLA + KF-M10b-MALLA | P_baja mínima KALINA por x_b: comparar con REPORTE_M10 y REPORTE_M10b; en x_b ≤ 0.475 no hay ningún punto genuino con W_net > 0; el primer x_b con KALINA es 0.55 y su P_baja mínima KALINA es 300 kPa |
| V23 | Todos | N2 por caso (tabla, solo información) |

Si una columna necesaria no existe o un subcaso no aparece con el nombre esperado, el check queda
"NO EVALUABLE" con el motivo. No adivines.

## Salidas

- `analisis_final/05_validacion/validacion_A4.csv`: `id_check, caso, filtro, cifra, esperado, recalculado, resultado (✔/✘/NO EVALUABLE), nota`.
- `analisis_final/05_validacion/checks_A4.md`: la misma tabla en Markdown, más un resumen (n ✔, n ✘, n no evaluables).

## Comando (timeout = 7200000)

```
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\analisis_final\a4_validar.py
```

## Formato de salida

El obligatorio de `AGENTS.md`. En RESULTS, pega el resumen y la lista de ✘ y NO EVALUABLE.
