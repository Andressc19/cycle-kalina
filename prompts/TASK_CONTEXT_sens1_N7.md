# TASK_CONTEXT — Sensibilidad 1, N7: una variable y pares alrededor de 2 centros NUEVOS (C3 caliente, C4 frío)

**Fecha:** 2026-10-15 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree). TODO se
crea y se ejecuta aquí.
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe` (numpy, pandas, scipy).
**Código a copiar (no reinventar):** `scripts/sens1/ronda2_corrida.py` (un proceso por punto, 5
simultáneos, tope duro de 600 s, reanudable por barrido, escritura incremental en modo `a`) y
`scripts/sens1/ronda2_reporte.py` / `ronda2_reporte2.py` (formato de reporte). Usa
`scripts/barrido_final/comun.py::evaluar_punto(..., extra=True)`.

## Notas de entorno (OBLIGATORIAS)

- Archivos SOLO con las herramientas `write` y `edit`. NUNCA desde la terminal (nada de `cat <<`,
  here-strings, `Set-Content`, `python -c` que escriba archivos).
- Terminal = Windows PowerShell 5.1, solo para EJECUTAR. Sin `&&` (usa `;`).
- No imprimas Unicode (η, ε…) en consola: solo ASCII.
- **Cada corrida larga con `timeout=7200000` en la herramienta de shell, en primer plano, sin
  `Start-Process`.** La corrida es **por barrido** y reanudable: si una invocación se corta, relanza el
  MISMO comando.
- **NO ejecutes `pytest` ni toda la suite.**

## Restricciones

- **NO modificar `src/`, `app.py`, `ui_*.py`, `scripts/barrido_final/comun.py`.**
- Cada `.py`: máximo 200 líneas (divide en `n7_puntos.py`, `n7_corrida.py`, `n7_reporte.py`,
  `n7_reporte2.py`).
- No inventes valores; lo que falte, a UNRESOLVED. Cada número del reporte sale de un archivo generado.
- No toques archivos de fases y rondas anteriores.
- **Reglas del usuario:** T_fuente 70–300 °C (343.15–573.15 K); eficiencias y efectividades 0.40–0.95
  con paso 0.05; T_sumidero 5–30 °C (278.15–303.15 K); `m_b = 1.0`; `t_amb_diseno = T_sumidero` del punto;
  motor `teqp`; `extra=True`. Se conservan todas las clases.

## Por qué existe

La Ronda 1 encontró KALINA confiables a fuente caliente (150 °C) y fuente fría (110 °C) con presiones y
x_b distintos de los centros C1/C2. Aquí se repite el análisis de la Fase A (una variable) y de la Fase B
(pares) alrededor de dos puntos KALINA confiables nuevos, sacados tal cual de `ronda1_filas.csv`.

## Centros (valores EXACTOS del punto de origen; `eta_p = 0.80`, `m_b = 1.0`)

| Centro | Origen | T_fuente [K] | T_sumidero [K] | P_alta | P_baja | x_b | η_t | ε_HRVG | ε_reg | ε_cond |
|---|---|---|---|---|---|---|---|---|---|---|
| C3 caliente (150 °C) | `N1-T150-19` | 423.15 | 280.5 | 3150 | 950 | 0.75 | 0.85 | 0.85 | 0.75 | 0.95 |
| C4 frío (110 °C) | `N1-T110-06` | 383.15 | 282.5 | 3880 | 910 | 0.88 | 0.85 | 0.85 | 0.75 | 0.95 |

Primero **lee esas dos filas de `resultados/2026-10-14_sens1_ronda1/ronda1_filas.csv`** y verifica que sus
variables coinciden con la tabla y que son KALINA sin `fuera_rango`; repórtalo (clase, η, `m_O2`). Si la
fila difiere de la tabla, usa los valores de la FILA y dilo en ASSUMPTIONS. El punto base de cada centro
se re-evalúa una vez (`variable = "base"`).

## Paso 1 — `n7_puntos.py` y `n7_corrida.py`

Cada punto lleva `id_punto`, `barrido` ∈ {N7A, N7B}, `centro` (C3/C4), `variable` (o `par`), y el `combo`
de las 10 variables + `m_b`. Elimina duplicados por (centro, combinación).

### N7A — una variable a la vez (por centro, el resto en el valor del centro)

| Variable | Valores |
|---|---|
| T_fuente | en °C: 70, 80, …, 300 (paso 10) más el base del centro |
| T_sumidero | 278.15, 280.65, …, 303.15 (paso 2.5 K) más el base del centro |
| P_alta [kPa] | 1000, 1250, …, 5000 (paso 250) |
| P_baja [kPa] | 200, 300, …, 2000 (paso 100) más el base del centro |
| x_b | 0.30, 0.35, …, 0.95 |
| η_t, η_p, ε_HRVG, ε_reg, ε_cond | 0.40, 0.45, …, 0.95 (12 valores cada una) |

`m_b` queda fijo en 1.0. Esperado ≈ 150 puntos por centro (≈ 300 en total).

### N7B — mallas de 2 variables 7 × 7 (4 pares por centro)

Los valores incluyen el del centro (**b**); resto en el valor del centro.

| Par | Variables |
|---|---|
| B1 | T_fuente × P_baja |
| B2 | P_baja × x_b |
| B3 | P_alta × P_baja |
| B4 | ε_cond × T_sumidero |

| Variable | C3 caliente | C4 frío |
|---|---|---|
| T_fuente [°C] | 110, 130, 140, 150**b**, 160, 180, 200 | 80, 90, 100, 110**b**, 120, 135, 150 |
| P_baja [kPa] | 500, 650, 800, 950**b**, 1100, 1300, 1600 | 500, 650, 800, 910**b**, 1050, 1250, 1500 |
| x_b | 0.55, 0.62, 0.68, 0.75**b**, 0.82, 0.88, 0.95 | 0.65, 0.72, 0.78, 0.83, 0.88**b**, 0.92, 0.95 |
| P_alta [kPa] | 2000, 2500, 3150**b**, 3500, 4000, 4500, 5000 | 2500, 3000, 3400, 3880**b**, 4300, 4600, 5000 |
| ε_cond | 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95**b** | igual que C3 |
| T_sumidero [K] | 278.15, 280.5**b**, 283.15, 288.15, 293.15, 298.15, 303.15 | 278.15, 282.5**b**, 285.65, 288.15, 293.15, 298.15, 303.15 |

Total: 49 × 4 × 2 = 392 combinaciones (≈ 370 únicas). Descarta (no resamplees) combinaciones con
`P_alta < 1.3 × P_baja` y repórtalo.

### Corredor

Argumento `N7A`, `N7B` o `all`; salta los `id_punto` ya escritos; un proceso por punto, 5 simultáneos,
tope duro de 600 s (fila `NO_CONVERGIO` con `mensaje="tiempo_agotado_600s"`), modo `a`, `flush` por fila.
Salidas en `resultados/2026-10-15_sens1_N7/`: `n7_filas.csv`, `n7_log_<barrido>.txt`, `n7_diseno.csv` y
`n7_descartes.csv`.

## Paso 2 — Ejecutar (cada comando en primer plano con `timeout=7200000`)

```
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\sens1\n7_corrida.py N7A
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\sens1\n7_corrida.py N7B
```

(Redirige a `n7_log_<barrido>.txt` con `2>&1 | Tee-Object -FilePath ...`.) Antes de correr, verifica el
conteo de `n7_diseno.csv` y repórtalo. Estimo ~2–2.5 h en total.

## Paso 3 — Reporte (`n7_reporte.py`, `n7_reporte2.py`)

**KALINA confiable:** clase KALINA, `fuera_rango` falso/vacío y todo `eta_*`/`eps_*` en [0.40, 0.95].
**KALINA fuera de rango:** KALINA con `fuera_rango` verdadero (siempre aparte). Un punto genuino es
`convergio=True` y clase ≠ NO_CONVERGIO. **El punto base se incluye dentro de cada barrido de su variable**
(error ya cometido en la Fase A: el resumen original no lo contaba).

Escribe en `resultados/2026-10-15_sens1_N7/`:

1. `n7_resumen_variables.csv`: por (centro, variable): nº de puntos, nº por clase, KALINA confiables, KALINA
   fuera de rango, valor mín y máx entre los KALINA, rango de η entre KALINA confiables y si el conjunto
   de valores KALINA es contiguo.
2. `n7_resumen_pares.csv` y `n7_mallas.md`: por (centro, par) matriz 7 × 7 de clases (K/c/n/i; minúscula
   si fuera de rango) y de η [%], nº de KALINA, % de área y el KALINA confiable de mayor η.
3. `n7_equipos.csv`: por centro, mín/mediana/máx entre KALINA confiables de `dh_turb`, `Wnet/m_b`,
   `Qi/m_b`, `Qreg/Qi`, `Qout/m_b`, `P_alta/P_baja`.
4. `n7_resumen.md`: tablas en lenguaje llano; ranking de variables por amplitud de η entre KALINA por
   centro; comparación con C1 y C2 (lee `resultados/2026-10-14_sens1_faseA/faseA_resumen_variables_corregido.csv`).

## Paso 4 — Reporte final

Formato obligatorio de `AGENTS.md`. En RESULTS: verificación de los centros, conteos planeados vs.
evaluados, clases, KALINA confiables y fuera de rango por centro y barrido, nº con tiempo agotado, y la
tabla de ventanas por variable de C3 y C4, tal como salió de los archivos.
