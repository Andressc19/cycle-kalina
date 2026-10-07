# TASK_CONTEXT — Campaña final, M4b: ampliar M4 a 500 puntos con foco en las PRESIONES de la región KALINA

**Fecha:** 2026-10-07 · **Rama:** `test/barrido_final` (commit base: HEAD actual)
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barrido-final`.
TODO se crea y se ejecuta aquí.
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`
**Leer antes de empezar:**
- `prompts/TASK_CONTEXT_final_M4.md` (la caja, las definiciones y el análisis);
- `scripts/barrido_final/m4_datos.py`, `m4_corrida.py`, `m4_analisis.py`, `m4_rsa.py`,
  `m4_pawn_prcc.py`, `m4_arbol.py` y `m4_figuras.py`;
- `resultados/2026-10-06_final_M4/REPORTE_M4.md` §14.

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`. NUNCA desde la
  terminal (nada de heredocs, `Set-Content` ni `python -c` que escriba archivos).
- PowerShell 5.1: no existen `tee` ni `&&`.
- **La corrida larga se ejecuta EN PRIMER PLANO y se espera a que termine.** Nada de
  `Start-Process` ni de desacoplarla: en la corrida 058 eso mató el proceso al cerrar la sesión.
  Usa la herramienta bash con el tiempo de espera máximo y vuelve a esperar si hace falta.
  Redirige con `*> archivo`.
- Las verificaciones van en un script escrito con `write`. Lanza la corrida larga UNA sola vez.

## Restricciones

- NO modificar `src/`, `comun.py`, ningún `m4_*.py` existente ni los resultados de
  `resultados/2026-10-06_final_M4/`. Para reutilizar código, impórtalo; si un módulo tiene una ruta
  fija (`OUT`), crea un módulo nuevo que reciba la ruta como parámetro.
- Cada `.py` debe tener como máximo 200 líneas (incluido el verificador). No inventar valores.
  No hacer commit.

## Por qué

Con 300 puntos, el ranking KS completo no convergió (ρ = 0.84 < 0.9). Además, **la prioridad del
usuario cambió**: lo primero son los **rangos donde hay KALINA**, en particular **las presiones
alta y baja y sus diferencias** (dP = P_alta − P_baja y rP = P_alta/P_baja). La eficiencia es
secundaria.

## Diseño

1. **200 puntos nuevos** con `scipy.stats.qmc.LatinHypercube(d=10, seed=20261007)` escalados a la
   **misma caja** `m4_datos.CAJA`, con `id_muestra` de 300 a 499. Mismo motor y misma evaluación
   que M4: `evaluar_punto(..., motor="teqp", t_amb_diseno=T_sumidero)` y
   `ProcessPoolExecutor(max_workers=7)`.
   Salidas en `resultados/2026-10-07_final_M4b/`: `m4b_muestra.csv` (escrito ANTES de correr) y
   `m4b_lhs.csv` (con flush por fila). Imprimir `[n/200] clase t_s`.
2. **Unión de 500 puntos** = `resultados/2026-10-06_final_M4/m4_lhs.csv` (300) + `m4b_lhs.csv`
   (200). En el reporte hay que declarar que la unión de dos LHS no es un LHS estricto de 500, pero
   que cada mitad sí lo es.
3. **Repetir el análisis de M4 sobre los 500 puntos** (RSA con sus 4 separaciones, PAWN, PRCC,
   CART, convergencia y top), con las mismas fórmulas y parámetros, escribiendo en la carpeta de
   M4b. **Convergencia:** se comparan los rankings con 300 y con 500 puntos mediante el ρ de
   Spearman, con el criterio ρ ≥ 0.9.
4. **Análisis de PRESIONES (lo nuevo y prioritario)**, sobre los 500 puntos (`m4b_presiones.py`):
   - (a) `m4b_plano_presiones.png`: dispersión de P_baja (x) contra P_alta (y). Cada punto lleva
     el color de su clase (KALINA verde, CORREGIBLE naranja, INVIABLE amarillo y no genuino gris),
     con líneas de rP constante en 2, 3, 4 y 5.
   - (b) `m4b_rangos_presiones.csv`: para P_alta, P_baja, dP y rP, el mínimo, p5, mediana, p95 y
     máximo **dentro de KALINA**, con los mismos estadísticos para los no KALINA genuinos y el KS
     con su valor p.
   - (c) `m4b_ventana_por_palta.csv`: se divide P_alta en 6 franjas iguales entre 2000 y 5000 kPa.
     Por franja: `n`, `n_kalina`, `%kalina`, P_baja mín/máx de los KALINA, dP mín/máx y rP mín/máx
     de los KALINA.
   - (d) `m4b_ventana_por_tfuente.csv`: lo mismo, con T_fuente en 6 franjas entre 380 y 500 K.
     Por franja: `n_kalina`, `%kalina` y los rangos de P_baja, dP y rP de los KALINA.
   - (e) `m4b_ventana_por_tsumidero.csv`: lo mismo, con T_sumidero en 4 franjas entre 278.15 y
     303.55 K.
   - (f) `m4b_hist_dP_rP.png`: histogramas de dP y de rP, KALINA contra no KALINA.
   - (g) **Qué criterio rompe fuera de la ventana:** entre los genuinos no KALINA, el conteo de
     `codigos_falla` según si rP < p5 de KALINA, rP > p95 de KALINA o rP está dentro.
     Salida: `m4b_bloqueo_por_rP.csv`.

## Reporte `REPORTE_M4b.md` (lenguaje llano; la PRIORIDAD va primero)

1. La pregunta.
2. Qué se hizo.
3. Conteos (300 + 200 = 500 puntos, KALINA, genuinos, N2 y fuera de rango).
4. **La ventana de presiones de KALINA**: la tabla (b) y la figura (a).
5. **Cómo cambia la ventana** de P_baja, dP y rP según P_alta, T_fuente y T_sumidero (tablas c, d
   y e, explicadas en palabras).
6. Qué criterio se rompe fuera de la ventana (tabla g).
7. RSA de las 10 variables más las derivadas (los rangos favorables con 500 puntos), comparado
   con los 300.
8. La convergencia (ρ entre 300 y 500, contra el criterio de 0.9).
9. PRCC y PAWN sobre η (secundario).
10. Las reglas de CART.
11. El top-10 KALINA (secundario).
12. Los tiempos.
13. La conclusión: **los rangos recomendados de P_alta, P_baja, dP y rP para KALINA.**
14. Lo que no se sabe.
15. Qué sigue.

## Pasos

1. Crear `m4b_corrida.py`, `m4b_analisis.py` (que reutiliza las funciones de los `m4_*.py` con
   la ruta como parámetro), `m4b_presiones.py` y `m4b_reporte.py`, todos con como máximo 200 líneas.
2. Humo con `M4B_HUMO=1`: N = 4, con salida en `.../2026-10-07_final_M4b/humo/`.
3. Corrida real de 200 puntos EN PRIMER PLANO (≈ 1.5–2 h). Después el análisis y el reporte.
4. Verificación (`m4b_verificar.py`, ≤ 200 líneas):
   - que la muestra y las corridas coincidan;
   - que se cumpla la propiedad LHS de los 200;
   - que haya 500 filas en la unión;
   - que 2 valores de la tabla (b) recalculados a mano coincidan;
   - que los números del reporte coincidan con los CSV.

## Formato de salida

El obligatorio de `AGENTS.md`.
