# TASK_CONTEXT — Sensibilidad 1, Fase B (barridos de 2 variables) + corrección del resumen de la Fase A

**Fecha:** 2026-10-14 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree). TODO se
crea y se ejecuta aquí.
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`
**Base de código a copiar:** `scripts/sens1/faseA_corrida.py` (corrida), `scripts/sens1/faseA_reporte.py`
y `faseA_reporte2.py` (resumen). Datos de entrada: `resultados/2026-10-14_sens1_faseA/faseA_filas.csv`.

## Notas de entorno (OBLIGATORIAS)

- Archivos SOLO con las herramientas `write` y `edit`. NUNCA desde la terminal (nada de `cat <<`,
  here-strings, `Set-Content`, `python -c` que escriba archivos).
- Terminal = Windows PowerShell 5.1, solo para EJECUTAR. Sin `&&` (usa `;`).
- No imprimas caracteres Unicode (η, ε…) en consola: cp1252 falla. Usa solo ASCII en los `print`.
- **La corrida del paso 3 tarda ~90 min. Pasa `timeout=7200000` a la herramienta de shell.** Corre en
  primer plano, no uses `Start-Process`, no la relances si tarda.

## Restricciones

- **NO modificar `src/`, `app.py`, `ui_*.py`, `scripts/barrido_final/comun.py`.**
- Cada `.py`: máximo 200 líneas (divide en dos si hace falta).
- No inventes valores; lo que falte, a UNRESOLVED.
- Cada número del reporte debe salir de un archivo generado en esta tarea.
- `m_b = 1.0` fijo. `t_amb_diseno = T_sumidero` del punto. Motor `teqp`, `extra=True`.
- No sobrescribas `faseA_filas.csv` ni los resúmenes originales de la Fase A.

## Paso 0 — Corregir el resumen de la Fase A

El resumen original no contó el punto base (`variable == "base"`) dentro de cada barrido, de modo que
reportó 2 KALINA en `T_sumidero` de C1 y 0 en `eps_cond` de C1 (los correctos son 3 y 1).

Crea `scripts/sens1/faseA_resumen_corregido.py` (≤200 líneas) que, a partir de `faseA_filas.csv`, para
cada (centro, variable) **añade la fila base de ese centro al conjunto de puntos del barrido** (con su
`valor` = el valor base de esa variable) y vuelve a calcular lo mismo que `faseA_resumen_variables.csv`
(nº por clase, nº KALINA confiables, rango KALINA, rango de η entre KALINA, contiguo sí/no, nº INVIABLE).
Escribe `faseA_resumen_variables_corregido.csv` y `faseA_resumen_corregido.md` en la carpeta de la Fase A.
Verifica y reporta: C1 `T_sumidero` → 3 KALINA, C1 `eps_cond` → 1 KALINA (si salen otros números,
repórtalo tal cual en UNRESOLVED).

## Paso 1 — `scripts/sens1/faseB_corrida.py`

Seis pares de variables, para los dos centros (valores de las demás variables = valores del centro):

| Centro | T_fuente | T_sumidero | P_alta | P_baja | x_b | η_t | η_p | ε_HRVG | ε_reg | ε_cond |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 | 394.15 | 278.15 | 3300 | 690 | 0.82 | 0.85 | 0.80 | 0.85 | 0.75 | 0.95 |
| C2 | 403.0 | 300.15 | 3000 | 563.64 | 0.50 | 0.85 | 0.75 | 0.85 | 0.75 | 0.95 |

| Par | Variable 1 | Variable 2 |
|---|---|---|
| B1 | T_fuente | P_baja |
| B2 | P_baja | x_b |
| B3 | P_alta | P_baja |
| B4 | ε_cond | T_sumidero |
| B5 | ε_reg | η_t |
| B6 | ε_HRVG | T_fuente |

Cada par es una malla 7 × 7 con estos valores (incluyen el del centro, marcado **b**). T_fuente en °C →
sumar 273.15 para K:

| Variable | C1 | C2 |
|---|---|---|
| T_fuente [°C] | 90, 100, 110, 121**b**, 135, 150, 165 | 110, 120, 129.85**b**, 140, 155, 170, 190 |
| T_sumidero [K] | 278.15**b**, 280.65, 283.15, 285.65, 288.15, 293.15, 298.15 | 278.15, 285.15, 290.15, 295.15, 300.15**b**, 302.15, 303.15 |
| P_alta [kPa] | 2000, 2500, 3000, 3300**b**, 3800, 4400, 5000 | 2000, 2500, 3000**b**, 3250, 3500, 3750, 4000 |
| P_baja [kPa] | 500, 600, 690**b**, 800, 950, 1100, 1300 | 400, 450, 500, 563.64**b**, 700, 900, 1200 |
| x_b | 0.55, 0.60, 0.70, 0.75, 0.82**b**, 0.90, 0.95 | 0.35, 0.40, 0.45, 0.50**b**, 0.55, 0.60, 0.70 |
| ε_cond | 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95**b** | igual que C1 |
| η_t, ε_HRVG | 0.50, 0.60, 0.70, 0.80, 0.85**b**, 0.90, 0.95 | igual que C1 |
| ε_reg | 0.50, 0.60, 0.70, 0.75**b**, 0.80, 0.90, 0.95 | igual que C1 |

Total: 49 × 6 × 2 = 588 combinaciones; **elimina duplicados** por (centro, combinación) (el punto base
aparece en las seis mallas: evalúalo una vez y reutilízalo; `variable1/variable2` = `base`).

Copia el patrón de `faseA_corrida.py` (5 procesos, `ProcessPoolExecutor`, escritura incremental con
`flush`). Columnas extra: `id_punto` (`C1-B1-0001`), `centro`, `par` (B1–B6, o `base`), `var1`, `val1`,
`var2`, `val2`. Salidas en `resultados/2026-10-14_sens1_faseB/`: `faseB_filas.csv` y `faseB_log.txt`.

## Paso 2 — `scripts/sens1/faseB_reporte.py` (y `faseB_reporte2.py` si pasa de 200 líneas)

Escribe en `resultados/2026-10-14_sens1_faseB/`:

1. `faseB_mallas.md`: por centro y par, una matriz 7×7 de **clase** (K = KALINA, c = CORREGIBLE,
   n = NO_CONVERGIO, i = INVIABLE; minúscula si es KALINA pero `fuera_rango`) y otra de **η [%]** (solo
   en KALINA), con los ejes rotulados con sus valores. El punto base marcado.
2. `faseB_resumen_pares.csv`: por (centro, par): nº de puntos, nº por clase, nº KALINA confiables,
   % del área KALINA, η mínimo/máximo entre KALINA, el punto KALINA confiable de mayor η (sus 2 valores y
   su η), y la **interacción**: nº de KALINA reales frente al nº esperado si las dos variables actuaran
   por separado (cuántos de los 49 puntos tienen cada una de sus 2 coordenadas en un valor que en la
   Fase A —línea de esa variable, **incluido el punto base**, ya corregido— era KALINA). Si real <
   esperado, "hay interacción" (la combinación se cae antes que cada una por separado).
3. `faseB_resumen.md`: tabla corta con esas cifras por par y centro; para cada par, 1–2 frases con el
   rango conjunto donde sigue habiendo KALINA; y para preselección de equipos, por centro y par, mínimos y
   máximos entre KALINA confiables de `dh_turb`, `Wnet/m_b`, `Qreg/Qi`, `Qout/m_b`, `P_alta/P_baja`.

**Definición de KALINA confiable:** `clasificacion == "KALINA"` y `fuera_rango` falso/vacío y todos los
`eta_*`, `eps_*` en [0.40, 0.95].

## Paso 3 — Ejecutar (desde el directorio de trabajo, en este orden)

```
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\sens1\faseA_resumen_corregido.py
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\sens1\faseB_corrida.py 2>&1 | Tee-Object -FilePath resultados\2026-10-14_sens1_faseB\faseB_log.txt
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\sens1\faseB_reporte.py
```

(Crea la carpeta `resultados\2026-10-14_sens1_faseB` desde el script de corrida. Si hay
`faseB_reporte2.py`, córrelo después.) Si `Tee-Object` no existe, usa `| tee`.

## Paso 4 — Reporte final

Formato obligatorio de `AGENTS.md`. En RESULTS pega: la verificación del Paso 0 (3 y 1), el nº de
puntos y clases por centro y la tabla corta de `faseB_resumen.md`, tal como salieron del archivo.
