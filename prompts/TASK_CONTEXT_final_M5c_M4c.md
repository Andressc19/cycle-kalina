# TASK_CONTEXT — M5c (malla fina con las presiones del profesor) + M4c (techo de P_baja)

**Fecha:** 2026-10-07 · **Rama:** `test/barrido_final`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barrido-final`.
TODO se crea y se ejecuta aquí.
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`
**Leer antes de empezar:**
- `scripts/barrido_final/comun.py` (`PROFESOR`, `evaluar_punto(..., t_amb_diseno=)`, `COLS`);
- `scripts/barrido_final/m4b_corrida.py` y `m4b_presiones.py` (patrones);
- `resultados/2026-10-07_final_M5/REPORTE_M5.md` §7b;
- `resultados/2026-10-07_final_M4b/REPORTE_M4b.md`.

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`. NUNCA desde la
  terminal.
- PowerShell 5.1: no existen `tee` ni `&&`.
- **La corrida larga se ejecuta EN PRIMER PLANO y se espera a que termine; nada de
  `Start-Process`.** Usa la herramienta bash con el tiempo de espera máximo y vuelve a esperar si
  hace falta. Redirige con `*> archivo`.
- Las verificaciones van en un script escrito con `write`. Cada corrida larga se lanza UNA sola vez.

## Restricciones

- NO modificar `src/`, `comun.py` ni ningún script existente. Cada `.py` debe tener como máximo
  200 líneas. Solo motor teqp. No inventar valores. No hacer commit.
- **Punto genuino:** `clasificacion ∈ {KALINA, CORREGIBLE, INVIABLE}`. Los N2 (`convergio=True` y
  NO_CONVERGIO) son NO genuinos.
- Piso de O2 = T_sumidero en todo punto (`t_amb_diseno=combo["T_sumidero"]`).

## Parte 1 — M5c: delimitar la franja KALINA con las presiones del profesor

**Pregunta.** Con P_alta = 3000 y P_baja = 400 kPa (las presiones del profesor), ¿en qué franja
exacta de T_fuente, ε_cond y T_sumidero el ciclo es KALINA?

- Todo lo demás exactamente como `comun.PROFESOR`: x_b 0.50, η_t 0.85, η_p 0.75, ε_HRVG 0.85 y
  ε_reg 0.75.
- **Malla completa:**
  - `T_fuente ∈ numpy.linspace(385, 410, 11)`;
  - `eps_cond ∈ {0.85, 0.875, 0.90, 0.925, 0.95}`;
  - `T_sumidero ∈ {278.15, 290.65, 300.032917}`.

  Son 11 × 5 × 3 = **165 corridas**.
- **Salidas** en `resultados/2026-10-07_final_M5c/`:
  - `m5c_malla.csv`, escrito con flush;
  - `m5c_frontera.csv`: por (T_sumidero, eps_cond), el rango de T_fuente que es KALINA
    (T_fuente mínima y máxima KALINA, si existe) y el η en cada extremo;
  - `m5c_mapa.png`: un panel por T_sumidero, con eps_cond (x) contra T_fuente (y) y el color de la
    clase.
- **Reporte `REPORTE_M5c.md`:** la franja exacta en una tabla y en palabras, el criterio que
  bloquea a cada lado, y la mejor η dentro de la franja.

## Parte 2 — M4c: ¿dónde está el techo de P_baja?

**Pregunta.** En M4b, el techo de P_baja de los KALINA (~1460–1490 kPa) coincidía con el borde de
la caja (1500 kPa). ¿Hay KALINA por encima de 1500 kPa y hasta dónde?

- **Muestreo:** LHS de **150 puntos**, `LatinHypercube(d=10, seed=20261008)`, en la misma caja de
  `m4_datos.CAJA`, salvo **P_baja ∈ [1500, 2500] kPa**.
- **Restricción:** si P_baja ≥ P_alta − 300, el punto se omite (`omitido=True`), sin evaluarlo.
- **Salidas** en `resultados/2026-10-07_final_M4c/`:
  - `m4c_muestra.csv`, escrito antes de correr;
  - `m4c_lhs.csv`, con flush;
  - `m4c_techo.csv`: por franjas de P_baja de 100 kPa entre 1500 y 2500, `n`, `n_kalina` y
    `%kalina`. **Se suman las franjas de M4b de 1300–1500 kPa** (con los 500 puntos de M4 + M4b)
    para mostrar la continuidad;
  - `m4c_techo_por_palta.csv`: la P_baja máxima KALINA por franja de P_alta (las 6 franjas de M4b)
    con M4 + M4b + M4c juntos;
  - `m4c_techo.png`: el % de KALINA contra P_baja (de 300 a 2500, con todos los puntos).
- **Reporte `REPORTE_M4c.md`:**
  - dónde termina la región KALINA en P_baja y qué criterio la corta (O1 por título bajo, O3 por
    trabajo nulo, etc.);
  - cómo cambia ese techo con P_alta;
  - la ventana completa de P_baja, con su piso y su techo.

## Ejecución

Las dos partes se envían al mismo `ProcessPoolExecutor(max_workers=7)`: 165 + hasta 150 puntos.
Imprimir `[n/N] parte clase t_s`.

## Pasos

1. Crear `m5c_corrida.py` y `m4c_corrida.py`, o bien una corrida conjunta `m5c_m4c_corrida.py`, y
   `m5c_analisis.py` y `m4c_analisis.py`. Todos con como máximo 200 líneas.
2. Humo con `M5C_HUMO=1`: 3 puntos por parte, con salida en `humo/`.
3. Corrida real EN PRIMER PLANO (≈ 1–1.5 h). Después los análisis y los reportes.
4. Verificación (`m5c_m4c_verificar.py`):
   - los conteos;
   - que la malla de M5c esté completa (165 puntos);
   - que la propiedad LHS se cumpla en M4c;
   - que los números de los reportes coincidan con los CSV.

## Formato de salida

El obligatorio de `AGENTS.md`.
