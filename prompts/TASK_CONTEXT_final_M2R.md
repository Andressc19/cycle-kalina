# TASK_CONTEXT — Campaña final, M2R: repetir M2 con eficiencias y efectividades en [0.40, 0.95]

**Fecha:** 2026-10-06 · **Rama:** `test/barrido_final` (commit base `c6fb1e1`)
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barrido-final`.
TODO se crea y se ejecuta aquí.
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`
**Leer antes de empezar:**
- `resultados/2026-10-06_final_M2/REPORTE_M2_N1.md` (§9) y `REPORTE_M2_N2.md`;
- `scripts/barrido_final/comun.py`;
- `scripts/barrido_final/m2_nivel1.py` y `m2_nivel2.py` (patrón de malla y bisección).

**OJO:** en paralelo corre OTRA tarea de OpenCode (M3) en este mismo worktree. No toques sus
archivos (`m3_*.py`, `resultados/2026-10-06_final_M3/`) ni el Excel.

## Por qué

M2 limitó η_t, η_p, ε_HRVG, ε_reg y ε_cond a [0.75, 0.85]. El usuario aclaró que el rango
permitido es **[0.40, 0.95]**. Hay que repetir lo que ese límite pudo haber condicionado. En
particular, la pregunta clave es: **¿se puede llegar a KALINA conservando la fuente
(T_fuente = 623.15 K) y el sitio (T_sumidero) del profesor, cambiando solo variables de diseño?**

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`. NUNCA desde la
  terminal: nada de heredocs, here-strings, `Set-Content` ni `python -c` que escriba archivos.
- La terminal es PowerShell 5.1. No existen `tee` ni `&&`: usa `Tee-Object` y `;`.
- Las verificaciones van en un script escrito con `write`; no uses `python -c` de varias líneas.
- Lanza la corrida larga UNA sola vez y espera a que termine.

## Restricciones

- NO modificar `src/`, `app.py`, `ui_*.py`, ningún script existente de `scripts/barrido_final/`
  ni `datos/Excel_final_kalina.xlsx`.
- Cada `.py` debe tener como máximo 200 líneas.
- No inventar valores. Lo que falte va a UNRESOLVED.
- Nunca reportar una ejecución que no ocurrió. No hacer commit.

## Definiciones

- **Punto genuino:** `clasificacion ∈ {KALINA, CORREGIBLE, INVIABLE}`. Una fila con
  `convergio=True` y `clasificacion == "NO_CONVERGIO"` es un punto fijo espurio (N2) y se trata
  como NO genuino en TODO: conteos, fronteras y conclusiones. **Las fronteras de "convergencia"
  se definen con "es genuino", NO con la bandera `convergio`.**
- Todo lo que no se indique queda exactamente como en `comun.PROFESOR`.

## Parte 1 — nivel 1 repetido para las 5 variables de rendimiento

- `eps_hrvg`, `eps_reg`, `eps_cond`, `eta_t` y `eta_p`, cada una con
  `numpy.linspace(0.40, 0.95, 12)` y el resto en `PROFESOR`: 60 corridas.
- Bisección (tolerancia 0.005, como máximo 8 iteraciones, en rondas paralelas) en cada par de
  vecinos donde cambie "es genuino" o "es KALINA".
- Salidas: `m2r_n1_malla.csv` y `m2r_n1_biseccion.csv`.

## Parte 2 — nivel 2 conservando fuente y sitio del profesor (T_fuente = 623.15 K)

El nivel 1 mostró que el lado caliente solo se destraba con `eps_hrvg` bajo (ε_HRVG ≤ 0.817 sí
convergía) y que lo que queda bloqueando es O2, que mejora con ε_cond o con P_baja. Por eso:

- **2a — (eps_hrvg, eps_cond):** `eps_hrvg ∈ {0.40, 0.50, 0.60, 0.70, 0.80}` ×
  `eps_cond ∈ numpy.linspace(0.40, 0.95, 12)`, con P_baja = 400 del profesor: 60 corridas.
- **2b — (eps_hrvg, P_baja):** `eps_hrvg ∈ {0.40, 0.50, 0.60, 0.70}` ×
  `P_baja ∈ numpy.linspace(400, 2000, 12)`: 48 corridas. Los valores de 0.75–0.81 ya están en M2.
- Bisección sobre la segunda variable (eps_cond con tolerancia 0.005; P_baja con 10 kPa; como
  máximo 8 iteraciones) donde cambie "es KALINA", o donde cambie `m_O2 >= 0` con ambos vecinos
  genuinos.

## Parte 3 — nivel 2 alternativo: (T_fuente, eps_cond) con P_baja del profesor

`T_fuente ∈ {403, 420, 434, 466, 497, 529, 560}` × `eps_cond ∈ {0.85, 0.90, 0.95}`, con
P_baja = 400: 21 corridas, sin bisección. Pregunta: ¿puede ε_cond sustituir a P_baja como
segundo cambio?

## Ejecución

`ProcessPoolExecutor(max_workers=5)`. Las tres partes se envían juntas al mismo pool para
aprovecharlo; la bisección va después. Cada CSV de malla se escribe con flush, con las columnas
`parte, var1, val1, var2, val2` más las de `COLS`. Después de cada fila se imprime
`[n/N] parte var1=val1 var2=val2 clase t_s`. Todo va en `resultados/2026-10-06_final_M2R/`.

## Salidas

- `m2r_*_malla.csv` y `m2r_*_biseccion.csv` por parte, y `m2r_fronteras.csv`.
- `m2r_kalina.csv` con TODOS los KALINA **sin duplicados** (clave: los valores de las 11
  variables). Columnas: `parte, var1, val1, var2, val2, eta, Wnet, m_O1, m_O2, fuera_rango,
  B_verificado`, más `n_cambios` (cuántas variables difieren de `PROFESOR`) y
  `d = Σ |v − v_prof|/(b − a)`, con los rangos de `TASK_CONTEXT_final_M3.md` (ε/η en [0.40, 0.95]).
- `m2r_resumen.csv`: por parte y por valor de var1, `n_genuinos`, `n_kalina`, `n_N2`, el KALINA
  de menor d y el de mayor η, y los bloqueantes genuinos más frecuentes.
- `REPORTE_M2R.md` en lenguaje llano:
  1. La pregunta.
  2. Qué cambió respecto a M2.
  3. Parte 1: tabla por variable.
  4. Parte 2: **respuesta directa a si se llega a KALINA conservando la fuente del profesor**,
     con la tabla.
  5. Parte 3.
  6. Comparación con M2: ¿hay un KALINA con menos cambios o con menor d que el de M2
     (T_fuente = 390 K / P_baja = 445 kPa, d ≈ 0.857 con la escala vieja; recalcularlo con la
     escala nueva para compararlo)?
  7. Tiempos.
  8. Conclusión.
  9. Lo que no se sabe (incluyendo los fuera de rango).
  10. Qué sigue.

## Pasos

1. Crear `scripts/barrido_final/m2r_corrida.py` y `scripts/barrido_final/m2r_reporte.py`.
2. Humo con `M2R_HUMO=1`: 1 punto por parte, sin bisección, con salida en `.../humo/`.
3. Corrida real con `Tee-Object` hacia `resultados/2026-10-06_final_M2R/stdout.txt`; después el
   reporte.
4. Verificar con un script escrito con `write`: los conteos, que no haya duplicados en
   `m2r_kalina.csv` y que los números del reporte coincidan con los CSV.

## Formato de salida

El obligatorio de `AGENTS.md`.
