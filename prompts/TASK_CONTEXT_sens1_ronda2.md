# TASK_CONTEXT — Sensibilidad 1, Ronda 2 de nuevos barridos (N2, N5, N6)

**Fecha:** 2026-10-15 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree). TODO se
crea y se ejecuta aquí.
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe` (scipy 1.18 con `scipy.stats.qmc`,
numpy, pandas; **no** trae scikit-learn).
**Código a copiar (no reinventar):** `scripts/sens1/ronda1_puntos.py`, `ronda1_corrida.py`,
`ronda1_reporte.py`, `ronda1_reporte2.py` (ya funcionan: un proceso por punto, 5 simultáneos, tope duro de
600 s, reanudable por barrido, escritura incremental en modo `a`). Copia cada uno a `ronda2_*.py` y adapta.
Usa `scripts/barrido_final/comun.py::evaluar_punto(..., extra=True)`.

## Notas de entorno (OBLIGATORIAS)

- Archivos SOLO con las herramientas `write` y `edit`. NUNCA desde la terminal (nada de `cat <<`,
  here-strings, `Set-Content`, `python -c` que escriba archivos).
- Terminal = Windows PowerShell 5.1, solo para EJECUTAR. Sin `&&` (usa `;`).
- No imprimas Unicode (η, ε…) en consola: solo ASCII.
- **Cada corrida larga con `timeout=7200000` en la herramienta de shell, en primer plano, sin
  `Start-Process`.** La corrida es **por barrido** y reanudable: si una invocación se corta, relanza el
  MISMO comando.
- **NO ejecutes `pytest` ni toda la suite del proyecto:** no es parte de esta tarea y tarda más de 5 min.

## Restricciones

- **NO modificar `src/`, `app.py`, `ui_*.py`, `scripts/barrido_final/comun.py`.**
- Cada `.py`: máximo 200 líneas.
- No inventes valores; lo que falte, a UNRESOLVED. Cada número del reporte sale de un archivo generado.
- No toques archivos de las Fases 0, A, B, C ni de la Ronda 1.
- **Reglas del usuario, válidas en todo:** T_fuente 70–300 °C (343.15–573.15 K); eficiencias y
  efectividades 0.40–0.95 con paso 0.05; T_sumidero 5–30 °C (278.15–303.15 K); `m_b = 1.0`;
  `t_amb_diseno = T_sumidero` del punto; motor `teqp`; `extra=True`. Se conservan todas las clases.

## Configuración nominal

`eta_t=0.85, eta_p=0.80, eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.95, m_b=1.0` salvo lo que cada barrido
mueva.

| Centro | T_fuente [K] | T_sumidero [K] | P_alta | P_baja | x_b | eta_p |
|---|---|---|---|---|---|---|
| C1 | 394.15 | 278.15 | 3300 | 690 | 0.82 | 0.80 |
| C2 | 403.0 | 300.15 | 3000 | 563.64 | 0.50 | 0.75 |

## Qué aprendió la Ronda 1 (para diseñar esta)

- Hay KALINA desde 70 °C (2 puntos, P_alta 1630–2200, P_baja 770–840, x_b 0.70–0.75), con P_baja
  de 400–1900 kPa a 90–150 °C; por encima de ~170 °C casi todo KALINA queda fuera de rango del motor.
- Con ε_cond < 0.85 no hay KALINA en ningún clima: `eps_cond = 0.95` queda como nominal; solo se baja
  en el barrido N6 junto con otras (no se repite N3).

## Paso 1 — `ronda2_puntos.py` y `ronda2_corrida.py`

Generan los puntos de tres barridos (cada punto lleva `id_punto`, `barrido` ∈ {N2, N5, N6}, `centro` y el
`combo` de las 10 variables + `m_b`). **Elimina duplicados por combinación** dentro de cada barrido.

### N2 — Esquina de fuente fría con presiones bajas (máx. 150 puntos)

Un LHS `scipy.stats.qmc.LatinHypercube(d=5, seed=20261016)` de **150 puntos** sobre estas 5 variables
(resto = configuración nominal, `eta_p=0.80`):

| Variable | Rango | Redondeo |
|---|---|---|
| T_fuente [K] | 343.15–403.15 (70–130 °C) | 0.5 K |
| P_alta [kPa] | 800–3000 | 10 kPa |
| P_baja [kPa] | 100–900 | 10 kPa |
| x_b | 0.30–0.80 | 0.01 |
| T_sumidero [K] | 278.15–303.15 | 0.5 K |

**Descarta** (no resamplees) los puntos con `P_alta < 1.3 × P_baja` y repórtalo.
`id_punto = N2-{nnn:03d}`; `centro = "NA"`.

### N5 — Mapa fuente × clima × P_baja (360 puntos)

Configuración nominal con `P_alta = 3000`, `x_b = 0.70`, `eta_p = 0.80`. Malla completa:

- `T_fuente` en °C: 90, 110, 130, 150, 170, 200 (sumar 273.15 para K) (6)
- `T_sumidero` en °C: 5, 10, 15, 20, 25, 30 (sumar 273.15) (6)
- `P_baja` [kPa]: 300, 400, 500, 600, 700, 800, 900, 1000, 1250, 1500 (10)

`id_punto = N5-T{°C:03d}-S{°C:02d}-{nn:02d}`; `centro = "NA"`.

### N6 — Equipos de baja efectividad con condensador al máximo (54 puntos)

Para cada centro (C1 y C2, con su configuración completa de la tabla; `eps_cond = 0.95`): malla 3 × 3 × 3
de `eta_t ∈ {0.40, 0.55, 0.70}` × `eps_hrvg ∈ {0.40, 0.55, 0.70}` × `eps_reg ∈ {0.40, 0.55, 0.70}`.
`id_punto = N6-{centro}-{nn:02d}`.

### Corredor

Mismo patrón que `ronda1_corrida.py`: argumento `N2`, `N5`, `N6` o `all`; salta los `id_punto` ya
escritos; un proceso por punto, 5 simultáneos, tope duro de 600 s, modo `a`, `flush` por fila, encabezado
fijo. Salidas en `resultados/2026-10-15_sens1_ronda2/`: `ronda2_filas.csv`, `ronda2_log_<barrido>.txt`,
`ronda2_diseno.csv` (todos los puntos planeados) y `ronda2_descartes.csv`.

## Paso 2 — Ejecutar (en este orden, cada comando en primer plano con `timeout=7200000`)

```
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\sens1\ronda2_corrida.py N6
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\sens1\ronda2_corrida.py N2
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\sens1\ronda2_corrida.py N5
```

(Redirige a `ronda2_log_<barrido>.txt` con `2>&1 | Tee-Object -FilePath ...`.) Antes de correr, verifica el
conteo de `ronda2_diseno.csv` (N2 ≤ 150, N5 = 360, N6 = 54) y repórtalo. Estimo ~2–2.5 h en total.

## Paso 3 — Reporte (`ronda2_reporte.py`, `ronda2_reporte2.py`)

**KALINA confiable:** clase KALINA, `fuera_rango` falso/vacío y todo `eta_*`/`eps_*` en [0.40, 0.95].
**KALINA fuera de rango:** clase KALINA con `fuera_rango` verdadero (se reporta APARTE). Un punto genuino es
`convergio=True` y clase ≠ NO_CONVERGIO.

Escribe en `resultados/2026-10-15_sens1_ronda2/`:

1. `ronda2_resumen_barridos.csv`: por barrido (y por centro en N6), nº de puntos, nº por clase, KALINA
   confiables, KALINA fuera de rango, η mín/mediana/máx entre confiables.
2. **N2** `ronda2_N2_ventanas.csv`: entre los KALINA (confiables y no) mín/p10/mediana/p90/máx de
   T_fuente, P_alta, P_baja, x_b y T_sumidero, y los 5 KALINA de mayor η con sus 5 variables.
3. **N5** `ronda2_N5_frontera.csv`: por (T_fuente, T_sumidero): la **P_baja mínima** con KALINA, la
   η máxima entre sus KALINA y la P_baja que la logra, y si es confiable; "ninguna" si no hay.
   Más `ronda2_N5_mallas.md`: matriz de clases (K/c/n/i; minúscula si fuera de rango) de T_sumidero × P_baja
   por cada T_fuente.
4. **N6** `ronda2_N6_cubos.md`: por centro, las 27 combinaciones con clase y η [%]; y una frase con la
   combinación de menor efectividad que sigue siendo KALINA confiable.
5. `ronda2_equipos.csv`: por barrido, mín/mediana/máx entre KALINA confiables de `dh_turb`, `Wnet/m_b`,
   `Qi/m_b`, `Qreg/Qi`, `Qout/m_b`, `P_alta/P_baja`.
6. `ronda2_resumen.md`: tablas anteriores en lenguaje llano y una conclusión por barrido: dónde hay KALINA
   a 70–130 °C con presiones bajas (N2); P_baja mínima y η máxima por fuente y clima (N5); cuán baratos
   pueden ser turbina, HRVG y regenerador (N6). Incluye cuántos puntos agotaron el tope y dónde.

## Paso 4 — Reporte final

Formato obligatorio de `AGENTS.md`. En RESULTS: conteo de puntos planeados vs. evaluados por barrido,
clases, KALINA confiables y fuera de rango por barrido, nº de descartados en N2, nº con tiempo agotado y
las tablas de N5 (frontera) y N6 (mejor combinación barata), tal como salieron de los archivos.
