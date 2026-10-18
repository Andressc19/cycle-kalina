# TASK_CONTEXT — Sensibilidad 1, Ronda 1 de nuevos barridos (N1, N3, N4)

**Fecha:** 2026-10-14 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree). TODO se
crea y se ejecuta aquí.
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe` (scipy 1.18 con `scipy.stats.qmc`,
numpy, pandas; **no** trae scikit-learn).
**Código a copiar (no reinventar):** `scripts/sens1/faseC_reanuda.py` — corredor con **un proceso por punto,
5 simultáneos y tope duro de 600 s** (si vence: `terminate()` y fila `NO_CONVERGIO` con
`mensaje="tiempo_agotado_600s"`), escritura incremental en modo `a`, y `scripts/sens1/faseC_corrida.py`
(muestreo LHS y redondeo). Usa `scripts/barrido_final/comun.py::evaluar_punto(..., extra=True)`.

## Notas de entorno (OBLIGATORIAS)

- Archivos SOLO con las herramientas `write` y `edit`. NUNCA desde la terminal (nada de `cat <<`,
  here-strings, `Set-Content`, `python -c` que escriba archivos).
- Terminal = Windows PowerShell 5.1, solo para EJECUTAR. Sin `&&` (usa `;`).
- No imprimas Unicode (η, ε…) en consola: solo ASCII.
- **Cada corrida larga se lanza con `timeout=7200000` en la herramienta de shell, en primer plano, sin
  `Start-Process`.** La shell corta a las 2 h: por eso la corrida se hace **por barrido** (paso 2) y el script
  es **reanudable** (salta los `id_punto` ya escritos). Si una invocación se corta, relanza el MISMO comando.

## Restricciones

- **NO modificar `src/`, `app.py`, `ui_*.py`, `scripts/barrido_final/comun.py`.**
- Cada `.py`: máximo 200 líneas (divide en `ronda1_puntos.py`, `ronda1_corrida.py`, `ronda1_reporte.py`,
  `ronda1_reporte2.py`).
- No inventes valores; lo que falte, a UNRESOLVED. Cada número del reporte sale de un archivo generado.
- No toques archivos de las Fases 0, A, B y C.
- **Reglas del usuario, válidas en todo:** T_fuente 70–300 °C (343.15–573.15 K); eficiencias y
  efectividades 0.40–0.95 con paso 0.05; T_sumidero 5–30 °C (278.15–303.15 K); `m_b = 1.0`;
  `t_amb_diseno = T_sumidero` del punto; motor `teqp`; `extra=True`. Se conservan todas las clases.

## Configuración nominal (salvo lo que cada barrido mueva)

`eta_t=0.85, eta_p=0.80, eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.95, m_b=1.0`.

| Centro | T_fuente [K] | T_sumidero [K] | P_alta | P_baja | x_b | eta_p |
|---|---|---|---|---|---|---|
| C1 | 394.15 | 278.15 | 3300 | 690 | 0.82 | 0.80 |
| C2 | 403.0 | 300.15 | 3000 | 563.64 | 0.50 | 0.75 |

## Paso 1 — `scripts/sens1/ronda1_puntos.py` y `ronda1_corrida.py`

Generan los puntos de tres barridos (cada punto lleva `id_punto`, `barrido` ∈ {N1, N3, N4}, `centro`
y el `combo` de las 10 variables + `m_b`). **Elimina duplicados por combinación** dentro de cada barrido.

### N1 — Ventana de presiones por temperatura de fuente (máx. 390 puntos)

13 niveles de T_fuente en °C: 70, 90, 110, 130, 150, 170, 190, 210, 230, 250, 270, 290, 300
(sumar 273.15 para K). Por nivel `i` (0..12), un LHS `scipy.stats.qmc.LatinHypercube(d=4,
seed=20261015+i)` de **30 puntos** sobre estas 4 variables (resto = configuración nominal, `eta_p=0.80`):

| Variable | Rango | Redondeo |
|---|---|---|
| P_alta [kPa] | 1000–5000 | 10 kPa |
| P_baja [kPa] | 150–2000 | 10 kPa |
| x_b | 0.30–0.95 | 0.01 |
| T_sumidero [K] | 278.15–303.15 | 0.5 K |

**Descarta** (no resamplees) los puntos con `P_alta < 1.3 × P_baja` y repórtalo (cuántos por nivel).
`id_punto = N1-T{°C:03d}-{nn:02d}`; `centro = "NA"`.

### N4 — Presión alta baja × composición (98 puntos)

Para cada centro (C1 y C2, con su configuración completa de la tabla): malla 7 × 7 de
`P_alta ∈ {1000, 1250, 1500, 1750, 2000, 2500, 3000}` × `x_b ∈ {0.40, 0.50, 0.60, 0.70, 0.80, 0.90,
0.95}`; resto en el valor del centro. `id_punto = N4-{centro}-{nnnn}`.

### N3 — Compensación del condensador (192 puntos)

Configuración de **C1** (T_fuente 394.15, P_alta 3300, x_b 0.82, eta_t 0.85, eta_p 0.80, eps_hrvg 0.85,
eps_reg 0.75). Malla:

- `eps_cond ∈ {0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95}` (8)
- `P_baja ∈ {400, 500, 600, 700, 800, 1000, 1250, 1500}` (8)
- `T_sumidero ∈ {283.15, 293.15, 303.15}` (10, 20 y 30 °C) (3)

`id_punto = N3-{nnnn}`; `centro = "C1"`.

### Corredor

Mismo patrón que `faseC_reanuda.py` (un proceso por punto, 5 simultáneos, tope duro de 600 s,
modo `a`, `flush` por fila, encabezado fijo). Acepta un argumento de línea de comandos: `N1`, `N3`, `N4`
o `all`; **salta** los `id_punto` ya presentes en el CSV. Salidas en
`resultados/2026-10-14_sens1_ronda1/`: `ronda1_filas.csv` (columnas de `COLS` + `COLS_EXTRA` +
`id_punto`, `barrido`, `centro`) y `ronda1_log_<barrido>.txt`. El script de puntos escribe además
`ronda1_diseno.csv` con todos los puntos planeados (para verificar el conteo).

## Paso 2 — Ejecutar (en este orden; cada comando en primer plano con `timeout=7200000`)

```
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\sens1\ronda1_corrida.py N4
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\sens1\ronda1_corrida.py N3
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\sens1\ronda1_corrida.py N1
```

(Redirige la salida a `ronda1_log_<barrido>.txt` con `2>&1 | Tee-Object -FilePath ...`.) N4 + N3 son 290
puntos (~1 h); N1 son ≤ 390 (~1.5 h). Antes de correr, verifica el conteo de `ronda1_diseno.csv`
(N1 ≤ 390, N4 = 98, N3 = 192) y repórtalo.

## Paso 3 — Reporte (`ronda1_reporte.py`, `ronda1_reporte2.py`)

**KALINA confiable:** clase KALINA, `fuera_rango` falso/vacío y todo `eta_*`/`eps_*` en [0.40, 0.95].
**KALINA fuera de rango:** clase KALINA con `fuera_rango` verdadero (se reporta APARTE, nunca se suma a
los confiables). Un punto genuino es `convergio=True` y clase ≠ NO_CONVERGIO.

Escribe en `resultados/2026-10-14_sens1_ronda1/`:

1. `ronda1_resumen_barridos.csv`: por barrido (y por centro), nº de puntos, nº por clase, KALINA
   confiables, KALINA fuera de rango, η mín/mediana/máx entre confiables.
2. **N1** `ronda1_N1_por_temperatura.csv`: por nivel de T_fuente: puntos, KALINA confiables, KALINA fuera
   de rango, y entre los KALINA (confiables o no) mín/p10/mediana/p90/máx de P_alta, P_baja, x_b y
   T_sumidero, η máxima y el punto que la logra (sus 4 valores).
3. **N3** `ronda1_N3_frontera.csv`: por (T_sumidero, eps_cond) la **P_baja mínima** con KALINA y su η, o
   "ninguna". Más `ronda1_N3_mallas.md`: matriz 8×8 de clases (K/c/n/i; minúscula si fuera de rango) por
   cada T_sumidero.
4. **N4** `ronda1_N4_mallas.md`: matriz 7×7 de clase y de η [%] por centro.
5. `ronda1_equipos.csv`: por barrido, mín/mediana/máx entre KALINA confiables de `dh_turb`,
   `Wnet/m_b`, `Qi/m_b`, `Qreg/Qi`, `Qout/m_b`, `P_alta/P_baja`.
6. `ronda1_resumen.md`: tablas anteriores en lenguaje llano y una conclusión por barrido: ventana de
   presiones por temperatura de fuente (N1); menor ε_cond que sirve en cada clima y a qué P_baja (N3);
   dónde hay KALINA con P_alta ≤ 2000 kPa (N4). Incluye cuántos puntos agotaron el tope de 600 s y dónde.

## Paso 4 — Reporte final

Formato obligatorio de `AGENTS.md`. En RESULTS: conteo de puntos planeados vs. evaluados por barrido,
clases, KALINA confiables y fuera de rango por barrido, nº de descartados en N1, nº con tiempo agotado,
y las tablas de N1 (por temperatura) y N3 (frontera), tal como salieron de los archivos.
