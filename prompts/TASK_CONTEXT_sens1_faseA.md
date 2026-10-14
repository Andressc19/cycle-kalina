# TASK_CONTEXT — Sensibilidad 1, Fase A (barridos univariados, 2 centros)

**Fecha:** 2026-10-14 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree). TODO se
crea y se ejecuta aquí.
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`
**Base de código a copiar:** `scripts/sens1/fase0_corrida.py` y `scripts/sens1/fase0_reporte.py` (ya
funcionan; usa `scripts/barrido_final/comun.py::evaluar_punto(..., extra=True)`).

## Notas de entorno (OBLIGATORIAS)

- Archivos SOLO con las herramientas `write` y `edit`. NUNCA desde la terminal (nada de `cat <<`,
  here-strings, `Set-Content`, `python -c` que escriba archivos).
- Terminal = Windows PowerShell 5.1, solo para EJECUTAR. Sin `tee` (usa `Tee-Object -FilePath`), sin `&&`
  (usa `;`).
- **La corrida del paso 3 tarda ~45–60 min. Pasa `timeout=7200000` a la herramienta de shell.** Corre
  en primer plano, no uses `Start-Process`, no la relances si tarda.

## Objetivo

Barridos de UNA variable a la vez (OFAT) alrededor de 2 centros KALINA, con las 10 variables de diseño
y el rango pedido por el profesor. Se conservan todas las clases (KALINA, CORREGIBLE, NO_CONVERGIO): el
análisis se centra en los KALINA y las demás marcan dónde falla el ciclo.

## Restricciones

- **NO modificar `src/`, `app.py`, `ui_*.py`, ni `scripts/barrido_final/comun.py`.**
- Cada `.py`: máximo 200 líneas (divide en dos archivos si hace falta).
- No inventes valores; lo que falte, a UNRESOLVED.
- Cada número del reporte debe salir de un archivo generado en esta tarea.
- **`m_b` queda FIJO en 1.0** (ya se comprobó que solo escala las potencias).
- **Piso de O2 por punto:** `t_amb_diseno = T_sumidero` de ese punto (el sumidero frío es la temperatura
  ambiente; decisión del usuario, igual que el estudio 2.4 de la campaña anterior).

## Centros (las 10 variables; m_b = 1.0)

| Variable | C1 «frío» (Húsavík) | C2 «cálido» (ancla A\*, clima del profesor) |
|---|---|---|
| T_fuente [K] | 394.15 | 403.0 |
| T_sumidero [K] | 278.15 | 300.15 |
| P_alta [kPa] | 3300 | 3000 |
| P_baja [kPa] | 690 | 563.64 |
| x_b | 0.82 | 0.50 |
| eta_t | 0.85 | 0.85 |
| eta_p | 0.80 | 0.75 |
| eps_hrvg | 0.85 | 0.85 |
| eps_reg | 0.75 | 0.75 |
| eps_cond | 0.95 | 0.95 |

C1 se verificó KALINA en la Fase 0 (punto E95, con piso 283.15). C2 es el ancla A\* de la campaña
anterior, que fue KALINA con T_sumidero 300.03 K; con 300.15 K debería seguir siéndolo, pero es un
punto de partida, **no se asume**: se reporta su clase en el resumen.

## Barridos (se cambia UNA variable, el resto en el valor del centro)

| Variable | Valores | Nº |
|---|---|---|
| T_fuente | en °C: 70, 80, …, 300 (paso 10) **más** 105, 115, 125, 135, 145, 155, 165; convertir a K (+273.15); más el valor base del centro si no está | ≈32 |
| T_sumidero | 278.15, 280.65, …, 303.15 (paso 2.5 K = 5 a 30 °C); más el valor base del centro si no está | 11–12 |
| P_alta | 2000, 2250, …, 5000 kPa | 13 |
| P_baja | 300, 400, …, 1500 kPa; más el valor base del centro si no está | 13–14 |
| x_b | 0.30, 0.35, …, 0.95 | 14 |
| eta_t, eta_p, eps_hrvg, eps_reg, eps_cond | 0.40, 0.45, …, 0.95 (12 valores cada una) | 60 |

Elimina duplicados (por ejemplo el punto base aparece en varios barridos: evalúalo UNA vez por centro y
reutilízalo; márcalo con `variable="base"`). Total esperado ≈ 145 por centro, ≈ 290 en total.

## Paso 1 — `scripts/sens1/faseA_corrida.py`

Copia el patrón de `fase0_corrida.py` (5 procesos, `ProcessPoolExecutor`, `extra=True`, motor `teqp`,
escritura incremental con `flush`). Cada fila lleva además: `id_punto` (`C1-T_fuente-0123` etc.),
`centro` (C1/C2), `variable` (la que se movió, o `base`), `valor`, y `t_amb_diseno = T_sumidero`.
Salidas en `resultados/2026-10-14_sens1_faseA/`:
- `faseA_filas.csv` (todas las columnas de `COLS` + `COLS_EXTRA` + las 4 anteriores),
- `faseA_log.txt`.

Escritura incremental: si el proceso se corta, las filas ya escritas deben quedar en el CSV.

## Paso 2 — `scripts/sens1/faseA_reporte.py` (y `faseA_reporte2.py` si pasa de 200 líneas)

Lee `faseA_filas.csv` y escribe en la misma carpeta:

1. **`faseA_resumen_variables.csv`**: una fila por (centro, variable) con: nº de puntos, nº por clase
   (KALINA / CORREGIBLE / NO_CONVERGIO), nº de **KALINA confiables**, valor mínimo y máximo de la variable
   entre los KALINA, rango de η [%] entre los KALINA, y si el conjunto de valores KALINA es contiguo
   (sí/no).
2. **`faseA_resumen.md`** con:
   - Clase del punto base de C1 y C2.
   - Una tabla por centro: para cada variable, el rango de valores donde hay KALINA, η mínimo y máximo
     allí, y el primer valor (hacia abajo y hacia arriba) donde la clase deja de ser KALINA y a qué clase
     pasa.
   - Un ranking por centro de las variables por **amplitud de η entre sus puntos KALINA** (pp).
   - Para la preselección de equipos, por centro: mínimo/máximo entre los KALINA de `dh_turb` [kJ/kg],
     `Wnet` [kW por kg/s], `Qreg/Qi`, y `m_O2`.
   - Cuenta de puntos genuinos (`convergio=True` y clase ≠ NO_CONVERGIO; los N2 espurios no cuentan).

**Definición de KALINA confiable:** `clasificacion == "KALINA"` y `fuera_rango` falso/vacío y todos los
`eta_*`, `eps_*` en [0.40, 0.95].

## Paso 3 — Ejecutar, en este orden, desde el directorio de trabajo

```
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\sens1\faseA_corrida.py 2>&1 | Tee-Object -FilePath resultados\2026-10-14_sens1_faseA\faseA_log.txt
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\sens1\faseA_reporte.py
```

(Crea la carpeta de resultados desde el script.) Si hay `faseA_reporte2.py`, córrelo después.

## Paso 4 — Reporte final

Formato obligatorio de `AGENTS.md`. En RESULTS pega el número de puntos por centro y clase y la tabla de
rangos KALINA por variable tal como salió de `faseA_resumen.md`.
