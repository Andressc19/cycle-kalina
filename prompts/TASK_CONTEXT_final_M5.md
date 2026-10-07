# TASK_CONTEXT — Campaña final, M5: regiones KALINA conservando datos del profesor

**Fecha:** 2026-10-07 · **Rama:** `test/barrido_final`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barrido-final`.
TODO se crea y se ejecuta aquí.
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`
**Leer antes de empezar:**
- `scripts/barrido_final/comun.py` (`PROFESOR`, `evaluar_punto(..., t_amb_diseno=)`, `COLS`);
- `scripts/barrido_final/m4_datos.py`, `m4_rsa.py` y `m4b_presiones.py` (reutilizar sus funciones
  de RSA y de ventanas de presión importándolas, sin modificarlas);
- `resultados/2026-10-07_final_M4b/REPORTE_M4b.md`.

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`. NUNCA desde la
  terminal.
- PowerShell 5.1: no existen `tee` ni `&&`.
- **La corrida larga se ejecuta EN PRIMER PLANO y se espera a que termine. Nada de
  `Start-Process`.** Usa la herramienta bash con el tiempo de espera máximo y vuelve a esperar si
  hace falta. Redirige con `*> archivo`.
- Las verificaciones van en un script escrito con `write`. Lanza la corrida larga UNA sola vez.

## Restricciones

- NO modificar `src/`, `comun.py` ni ningún script existente. Cada `.py` debe tener como máximo
  200 líneas. No inventar valores. No hacer commit. Se usa SOLO el motor teqp:
  `motor="teqp"`.

## Pregunta (prioridad del usuario, 2026-10-07)

**¿Qué datos del profesor se pueden conservar tal cual y aun así obtener un ciclo KALINA? Para
cada conjunto conservado, ¿en qué rangos tienen que estar las demás variables, en especial las
presiones y sus diferencias?** La eficiencia es secundaria: se reporta, pero no se optimiza.

## Escenarios (cada uno fija un subconjunto de los datos del profesor)

Datos del profesor (`comun.PROFESOR`): T_fuente = 623.15 K, T_sumidero = 300.032917 K,
P_alta = 3000 kPa, P_baja = 400 kPa, x_b = 0.50, η_t = 0.85, η_p = 0.75, ε_HRVG = 0.85,
ε_reg = 0.75, ε_cond = 0.80.

| Escenario | Se conservan del profesor | Variables libres |
|---|---|---|
| **S1 — sus temperaturas** | T_fuente = 623.15, T_sumidero = 300.032917 | P_alta, P_baja, x_b, η_t, η_p, ε_HRVG, ε_reg, ε_cond |
| **S2 — sus presiones** | P_alta = 3000, P_baja = 400 | T_fuente, T_sumidero, x_b, η_t, η_p, ε_HRVG, ε_reg, ε_cond |
| **S3 — sus presiones y su clima** | P_alta = 3000, P_baja = 400, T_sumidero = 300.032917 | T_fuente, x_b, η_t, η_p, ε_HRVG, ε_reg, ε_cond |
| **S4 — su P_alta y sus temperaturas** | P_alta = 3000, T_fuente = 623.15, T_sumidero = 300.032917 | P_baja, x_b, η_t, η_p, ε_HRVG, ε_reg, ε_cond |
| **S5 — su fuente y su composición** | T_fuente = 623.15, x_b = 0.50 | T_sumidero, P_alta, P_baja, η_t, η_p, ε_HRVG, ε_reg, ε_cond |

**Rangos de las variables libres** (fijados por el director):

| Variable | Rango | Motivo |
|---|---|---|
| P_alta | [2000, 5000] kPa | caja de M4 |
| P_baja | [200, 2000] kPa | más amplio que M4: con 623 K hace falta P_baja alta (M2R: ≥ 1318) |
| T_fuente | [380, 623.15] K | hasta el valor del profesor |
| T_sumidero | [278.15, 303.55] K | caja de M4 |
| x_b | [0.50, 0.85] | caja de M4 |
| η_t, η_p, ε_HRVG, ε_reg, ε_cond | [0.40, 0.95] | rango permitido por el usuario |

Piso de O2 = T_sumidero en todos los casos (`t_amb_diseno=combo["T_sumidero"]`).
Restricción física: si P_baja ≥ P_alta − 300, el punto no se evalúa; se marca `omitido=True` con
el motivo "P_baja demasiado cerca de P_alta".

**Punto genuino:** `clasificacion ∈ {KALINA, CORREGIBLE, INVIABLE}`. Una fila con
`convergio=True` y NO_CONVERGIO es espuria (N2) y es NO genuina en todo.

## Diseño

- Por escenario: **LHS de 120 puntos** sobre sus variables libres, con
  `scipy.stats.qmc.LatinHypercube(d=n_libres, seed=20261007 + k)`, donde k = 1…5 es el número del
  escenario. Son 600 corridas en `ProcessPoolExecutor(max_workers=7)`, todas enviadas al mismo pool.
- Las muestras se guardan en `m5_muestra.csv` ANTES de correr. Las filas se escriben con flush en
  `resultados/2026-10-07_final_M5/m5_lhs.csv`, con las columnas `escenario, id, omitido` más las de
  `COLS`. Imprimir `[n/600] Sk clase t_s`.

## Análisis por escenario (`m5_analisis.py`)

1. Conteos: n, KALINA, genuinos, N2, omitidos y fuera de rango.
2. **¿Es posible?**
   - Si n_KALINA = 0, el escenario es **no factible en la caja**. Se reporta cuál es el criterio
     bloqueante dominante entre los genuinos y el punto genuino de menor D (con sus valores).
   - Si n_KALINA > 0, se sigue con los puntos 3 a 6.
3. **Rangos KALINA** de cada variable libre: mín, p5, mediana, p95 y máx dentro de KALINA. También
   los de dP y rP cuando las presiones no están fijas. Si n_KALINA ≥ 10, KS (RSA) KALINA contra no
   KALINA.
4. **Ventana de presiones:** para S1, S2 y S5, la figura de P_baja contra P_alta por clase (en S2
   las presiones están fijas: se grafica T_fuente contra x_b). Para S4, P_baja contra x_b.
5. **KALINA más parecido al profesor:** el de menor `d = Σ |v − v_prof|/(b − a)` sobre las
   variables libres, con todos sus valores, su η, `fuera_rango` y `B_verificado`.
6. Secundario: el KALINA de mayor η.

Salidas: `m5_resumen.csv` (una fila por escenario), `m5_rangos.csv`, `m5_cercano_profesor.csv` y
una figura por escenario, `m5_S{k}.png`.

## Reporte `REPORTE_M5.md` (lenguaje llano)

1. La pregunta.
2. Qué se hizo.
3. **Tabla principal:** escenario | qué se conserva | ¿hay KALINA? | cuántos | rangos clave de lo
   que se mueve | KALINA más parecido al profesor | η de ese punto.
4. Una sección por escenario, con sus rangos, su figura y el criterio que bloquea.
5. Los tiempos.
6. **Conclusión, con la forma:** "De los datos del profesor se pueden conservar … siempre que …".
7. Lo que no se sabe:
   - 120 puntos por escenario es una exploración, no un mapa fino;
   - los puntos fuera de rango.
8. Qué sigue.

## Pasos

1. Crear `m5_corrida.py`, `m5_analisis.py` y `m5_reporte.py`, todos con como máximo 200 líneas.
2. Humo con `M5_HUMO=1`: 2 puntos por escenario, con salida en `.../2026-10-07_final_M5/humo/`.
3. Corrida real EN PRIMER PLANO (≈ 2–3 h). Después el análisis y el reporte.
4. Verificación (`m5_verificar.py`, ≤ 200 líneas):
   - que la muestra y las corridas coincidan;
   - que cada escenario respete exactamente los valores del profesor que conserva;
   - que se cumpla la propiedad LHS;
   - que los números del reporte coincidan con los CSV.

## Formato de salida

El obligatorio de `AGENTS.md`.
