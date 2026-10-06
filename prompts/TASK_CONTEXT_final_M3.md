# TASK_CONTEXT — Campaña final, M3: sensibilidad local (una variable a la vez) alrededor del ancla A\*

**Fecha:** 2026-10-06 · **Rama:** `test/barrido_final` (commit base `c6fb1e1`)
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barrido-final`.
TODO se crea y se ejecuta aquí.
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe` (incluye matplotlib)
**Leer antes de empezar:**
- `docs/MATEMATICA_ITERACIONES_SENSIBILIDAD.md` §5 (fórmulas de esta fase);
- `scripts/barrido_final/comun.py` (reutilizar `evaluar_punto`, `PROFESOR` y `COLS`);
- `scripts/barrido_final/m2_nivel2.py` (patrón de pool y CSV con flush).

**OJO:** en paralelo corre OTRA tarea de OpenCode (M2R) en este mismo worktree. No toques sus
archivos (`m2r_*.py`, `resultados/2026-10-06_final_M2R/`) ni el Excel.

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`. NUNCA desde la
  terminal: nada de heredocs, here-strings, `Set-Content` ni `python -c` que escriba archivos.
- La terminal es PowerShell 5.1. No existen `tee` ni `&&`: usa `Tee-Object` y `;`.
- Las verificaciones van en un script escrito con `write`; no uses `python -c` de varias líneas.
- Lanza la corrida larga UNA sola vez y espera a que termine.

## Restricciones

- NO modificar `src/`, `app.py`, `ui_*.py`, ningún script existente de `scripts/barrido_final/`
  ni `datos/Excel_final_kalina.xlsx` (el Excel se consolida aparte).
- Cada `.py` debe tener como máximo 200 líneas.
- No inventar valores. Lo que falte va a UNRESOLVED.
- Nunca reportar una ejecución que no ocurrió. No hacer commit.

## Definiciones

- **Ancla A\***: `dict(PROFESOR, T_fuente=403.0, P_baja=563.6363636363637)`. En la corrida de
  M2 nivel 2 dio KALINA, η = 0.08482, m_O2 = +0.311 K, `B_verificado=True` y dentro de rango.
- **Punto genuino:** `clasificacion ∈ {KALINA, CORREGIBLE, INVIABLE}`. Una fila con
  `convergio=True` y `clasificacion == "NO_CONVERGIO"` es un punto fijo espurio (N2) y se trata
  como NO genuino en TODO.

## Rangos (fijados por el director; actualizados el 2026-10-06)

| Variable | Rango [a, b] |
|---|---|
| T_fuente (K) | [340, 623.15] |
| T_sumidero (K) | [283.15, 303.55] |
| P_alta (kPa) | [1000, 10000] |
| P_baja (kPa) | [150, 1500] |
| x_b (−) | [0.30, 0.90] |
| eta_t, eta_p, eps_hrvg, eps_reg, eps_cond (−) | **[0.40, 0.95]** (rango permitido por el usuario) |

## Diseño (MATEMATICA §5)

- **Punto A\***: 1 corrida.
- **Malla OAT:** para cada una de las 10 variables, 15 valores
  `v_j = a + (j − 1)(b − a)/14` (j = 1…15). La variable toma cada valor y las demás quedan en A\*.
- **Vecinos para la elasticidad:** para cada variable, `A*_i ± h` con `h = 0.01·(b − a)`.
  Son 2 corridas por variable.

Total: 1 + 10 × 17 = **171 corridas**, con `evaluar_punto(combo, motor="teqp", tag=...)` y
`ProcessPoolExecutor(max_workers=5)`. Cada fila se escribe con flush en
`resultados/2026-10-06_final_M3/m3_ofat.csv`, con las columnas `tipo_punto (ancla/malla/vecino),
variable, valor` más las de `COLS`. Después de cada fila se imprime `[n/171] var=valor clase t_s`.

## Cálculos (solo con puntos genuinos)

Por variable i:

1. **Elasticidad de η en A\*:** `E_i = [η(v+h) − η(v−h)]/(2h) · v_i/η(A*)`. Se calcula solo si
   los dos vecinos y A\* son genuinos; si no, va vacía con el motivo.
2. **Efecto en el rango:** `Δη_i = max η − min η` sobre los puntos genuinos de la malla.
   También se reportan `n_genuinos`, `n_kalina` y el valor de la variable con el que se obtiene
   el máximo η KALINA.
3. **Cruces de frontera** (`m3_cruces.csv`). Para cada par de puntos consecutivos de la malla
   (ordenados por valor) en el que ambos son genuinos, y para cada margen m ∈ {m_O1, m_O2, m_O5}
   que cambie de signo, se interpola linealmente:
   `v* = v_j − m_j·(v_{j+1} − v_j)/(m_{j+1} − m_j)`.
   Además, cada cambio de clase entre puntos consecutivos se registra con su par (v_j, v_{j+1})
   y las dos clases, aunque alguno no sea genuino.
   Columnas: `variable, tipo (margen/clase), criterio, v_j, v_j1, v_cruce, clase_j, clase_j1`.
4. **Rango KALINA continuo alrededor de A\*:** el intervalo de valores consecutivos de la malla,
   alrededor del valor de A\* (incluyendo A\* y sus vecinos), donde la clase es KALINA.
   Se reportan `kalina_desde` y `kalina_hasta`, que son los puntos extremos de la malla.

Todo esto va en `m3_resumen.csv`, con una fila por variable: `variable, valor_ancla, a, b,
E_eta, motivo_E, delta_eta, eta_min, eta_max, n_genuinos, n_kalina, valor_eta_max_kalina,
kalina_desde, kalina_hasta, criterios_bloqueantes (fuera de la zona KALINA, solo genuinos)`.

## Figuras (en `resultados/2026-10-06_final_M3/`, con matplotlib y backend Agg)

- `m3_tornado.png`: barras horizontales de `Δη_i`, ordenadas de mayor a menor.
- `m3_elasticidad.png`: barras de `E_i`.
- `m3_curvas.png`: 10 subgráficos, uno por variable, de η vs el valor de la variable. Cada punto
  lleva el color de su clase (KALINA verde, CORREGIBLE naranja, INVIABLE amarillo y no genuino
  rojo/gris) y una línea vertical marca el valor de A\*.

## Reporte `REPORTE_M3.md` (lenguaje llano)

1. La pregunta.
2. Qué se hizo, explicado en simple.
3. Una tabla por variable: E, Δη, el rango KALINA alrededor del ancla y el criterio que se rompe
   primero al salir de ese rango, de cada lado.
4. Un ranking de influencia sobre η (por |E| y por Δη, que pueden no coincidir: explicarlo).
5. Las fronteras más cercanas al ancla, con su valor interpolado, para indicar qué tan "al filo"
   está A\*.
6. Las figuras.
7. Los tiempos.
8. La conclusión.
9. Lo que no se sabe:
   - OAT no ve interacciones;
   - las diferencias de η menores que 0.4–0.7 pp no son concluyentes;
   - los puntos fuera de rango confiable.
10. Qué sigue (M4, lo decide el director).

## Pasos

1. Crear `scripts/barrido_final/m3_ofat.py` (corrida) y `scripts/barrido_final/m3_analisis.py`
   (resumen, cruces, figuras y reporte; se puede volver a ejecutar sobre el CSV sin recalcular).
2. Humo con `M3_HUMO=1`: A\* + 1 variable × 3 valores, con salida en `.../2026-10-06_final_M3/humo/`.
3. Corrida real:
   `python scripts/barrido_final/m3_ofat.py 2>&1 | Tee-Object -FilePath resultados/2026-10-06_final_M3/stdout.txt`,
   y después `python scripts/barrido_final/m3_analisis.py`.
4. Verificar con un script escrito con `write`: las filas del CSV (171), que E y Δη se recalculan
   igual a mano para 2 variables, y que las figuras existen.

## Formato de salida

El obligatorio de `AGENTS.md`. En RESULTS va la tabla resumen por variable (10 filas).
