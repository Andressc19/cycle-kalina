# TASK_CONTEXT — M10: Húsavík revisitado (re-corrida de la Fase 3 + barridos que faltaban) + Excel

**Fecha:** 2026-10-09 · **Rama:** `test/barrido_final`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barrido-final`
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`

## Notas de entorno (OBLIGATORIAS: lecciones de las corridas 071–075)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`. Nunca desde la
  terminal.
- PowerShell 5.1: no existen `tee`, `tail` ni `&&`.
- **Toda corrida larga se lanza con el PARÁMETRO `timeout` de la herramienta shell = 7200000.** Con el
  valor por defecto (120000 ms), la corrida muere. Va en primer plano y UNA sola vez. Nada de
  `Start-Process`, `taskkill` ni `Stop-Process` por nombre.
- `comun.py` exporta SOLO `PROFESOR`, `T_AMB_DISENO`, `TAU`, `PRESUPUESTO_S`, `VARS`, `COLS`,
  `margenes`, `indice_D` y `evaluar_punto`. No inventes otras funciones.
- **Plantilla obligatoria:** `scripts/barrido_final/m5_corrida.py` (muestra → `ProcessPoolExecutor(7)`
  → `as_completed` → `csv.DictWriter` con flush por fila). El `combo` lleva solo las 11 variables y
  `t_amb_diseno` va como argumento aparte de `evaluar_punto`. Cada corrida es reanudable: salta los
  `id` que ya estén en el CSV.

## Restricciones

- NO modificar `src/`, `comun.py` ni scripts existentes. Cada `.py` nuevo debe tener como máximo 200
  líneas. Solo motor teqp. No hacer commit. No inventar datos.
- **Punto genuino** = KALINA, CORREGIBLE o INVIABLE (`convergio=True` con NO_CONVERGIO es N2, no
  genuino). **KALINA confiable** = KALINA + `fuera_rango == False` + `B_verificado == True`.

## Contexto

En septiembre, antes del PR del bracket tolerante (MA) y de la protección A+B de teqp, la Fase 3
estudió la planta de Húsavík con el `TeqpAdapter` viejo. Sus resultados están en
`resultados/barridos_2026-09-19/fase3_real/`.

**Ancla de Húsavík** (`CASO_HUSAVIK_v2.md` §1.0):

```
P_alta 3300, P_baja 690, x_b 0.82, T_fuente 394.15, T_sumidero 278.15, eta_t 0.90,
eta_p 0.80, eps_hrvg 0.85, eps_reg 0.75, eps_cond 0.95, m_b 1.0
piso O2 = 283.15 K
```

## Parte A — re-correr los KALINA de la Fase 3 con el motor actual

**Familias de la Fase 3 (catálogo):**

| Familia | Archivo(s) | Variables movidas | Piso O2 original | KALINA en sept. |
|---|---|---|---|---|
| F3-A búsqueda v1 | `busqueda_husavik.csv` | P_alta, P_baja, x_b, η_t, ε_reg, ε_cond | **303.55** (default de entonces) | 14 / 69 |
| F3-B búsqueda v2 | `busqueda_husavik_v2.csv` | P_baja, ε_reg, ε_cond | 283.15 | 27 / 40 |
| F3-C mapa 2D | `mapa_2d_pbaja_epsreg.csv` | P_baja × ε_reg | 283.15 | 24 / 36 |
| F3-D OFAT 7 pts sobre el ancla de 690 | `sensibilidad_P_baja.csv`, `_eps_cond`, `_eps_reg`, `_eta_t`, `_x_b` | una variable por archivo | 283.15 | 4, 3, 7, 7, 5 |
| F3-E OFAT 4 pts sobre la base v1 de 1200 | `sensibilidad_palta.csv`, `_pbaja`, `_xb` (archivos con BOM: usar `encoding="utf-8-sig"`) | una variable por archivo | **303.55** | 2, 2, 2 |

**Qué se corre:**

- Cada fila con `clasificacion == "KALINA"` de esos archivos se vuelve a evaluar con
  `evaluar_punto(combo, motor="teqp", t_amb_diseno=<piso original de su familia>)`.
- El `combo` son las 11 variables tal cual vienen en la fila.
- Son ~96 corridas.

**Salida:** `m10_recorrida_fase3.csv`. Tiene las columnas de `comun.COLS` más `familia`,
`archivo_origen`, `fila_origen`, `clase_sept`, `eta_sept`, `coincide_clase` y
`d_eta_pp = 100·(eta_ahora − eta_sept)`.

## Parte B — barridos que faltaron en la Fase 3 (sobre el ancla de Húsavík, piso 283.15)

**B1, OFAT de 15 puntos por variable** (`numpy.linspace`, el resto en el ancla): 150 corridas.

| Variable | Rango | Por qué |
|---|---|---|
| T_fuente | 380–430 K | En sept. no se movió. Salmuera de ~121 °C |
| T_sumidero | 273.15–293.15 K | En sept. no se movió. Clima de 0 a 20 °C; el piso queda en max(T_sumidero, 283.15) |
| P_alta | 2500–4000 kPa | En sept., solo 4 puntos |
| P_baja | 500–1200 kPa | En sept., 7 puntos |
| **x_b** | **0.60–0.95** | **En sept., solo 0.78–0.86: amplía la concentración de amoníaco** |
| eta_t | 0.75–0.95 | |
| eta_p | 0.60–0.90 | En sept. no se movió |
| eps_hrvg | 0.60–0.95 | En sept. no se movió |
| eps_reg | 0.40–0.95 | |
| eps_cond | 0.70–0.95 | |

**B2, malla 2D x_b × P_baja:**

- x_b en {0.70, 0.73, 0.76, 0.79, 0.82, 0.85, 0.88, 0.91};
- P_baja en {500, 600, 700, 800, 900, 1000, 1100, 1200};
- son 64 corridas: la concentración variable cambia el punto de burbuja y, con él, la P_baja
  mínima de O2.

**Salidas:** `m10_ofat.csv` (con `variable`, `valor`) y `m10_malla_xb_pbaja.csv`.

Todo lo de A y B va en UN solo pool de 7 procesos. Se escriben todas las muestras ANTES de correr.
Humo con `M10_HUMO=1`: 2 puntos por parte, en `.../humo/`.

## Parte C — análisis, reporte y Excel

Todo en `resultados/2026-10-09_final_M10_husavik/`:

1. `m10_catalogo.csv`: una fila por familia, F3-A…F3-E y además B1-<variable> y B2. Columnas:
   - familia, origen (sept / nuevo), variables_movidas, piso_O2, n;
   - KALINA_sept, KALINA_ahora, confiables_ahora;
   - coincide (n de filas con la misma clase) y d_eta_pp medio y máximo en valor absoluto.
2. `m10_ofat_rangos.csv`: por variable de B1, el rango de valores donde el punto es KALINA (mín y máx
   KALINA), el criterio que lo rompe a cada lado y η mín y máx dentro de KALINA.
3. `m10_xb_pbaja.png`: mapa de clase de B2 con la isolínea de η. `m10_ofat.png`: 2 × 5 paneles de η
   contra el valor, coloreados por clase, con una línea vertical en el valor del ancla.
4. `REPORTE_M10.md`, en lenguaje llano:
   - la pregunta;
   - la tabla del catálogo;
   - cuántos KALINA de septiembre se confirman, cuáles cambian de clase y por qué (criterio, A/B o
     MA);
   - la tabla de rangos de B1, con la de **x_b** destacada;
   - lo que muestra B2: la P_baja mínima KALINA para cada x_b;
   - lo que no se sabe.
   Las cifras salen todas de los CSV.
5. `m10_verificar.py`: recalcula las cifras del reporte e imprime OK o FALLA.
6. `scripts/barrido_final/excel_m10.py`, con el patrón de `excel_m9.py`, idempotente, con
   `_fila_resumen` tolerante a hojas sin columna de clases. Hojas: `M10_catalogo`,
   `M10_recorrida_F3`, `M10_ofat`, `M10_ofat_rangos`, `M10_xb_pbaja` y `M10_figuras`.
7. Ejecuta en orden, cada uno con timeout=7200000: `excel_final.py`, `excel_m2.py`, `excel_m3_m2r.py`,
   `excel_m2s_m4.py`, `excel_m5.py`, `excel_m5c_m7_m8.py`, `excel_m6.py`, `excel_m9.py` y
   `excel_m10.py`. Después, un verificador hecho con `write`:
   - que las hojas M10 tengan las filas de su CSV;
   - que todas las hojas anteriores sigan presentes;
   - que `Resumen` tenga las filas de M10.

## Formato de salida

El obligatorio de `AGENTS.md`.
