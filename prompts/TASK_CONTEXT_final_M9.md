# TASK_CONTEXT — M9: escalera de conservación de los datos del profesor + Húsavík + Excel

**Fecha:** 2026-10-08 · **Rama:** `test/barrido_final`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barrido-final`
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`. NUNCA desde la
  terminal (nada de `Set-Content`, `Out-File`, here-strings ni `Add-Content`).
- PowerShell 5.1: no existen `tee` ni `&&`.
- Las corridas largas van EN PRIMER PLANO, sin `Start-Process` ni jobs. Cada corrida se lanza UNA
  sola vez. Si tarda, espera: no la relances.
- Cada corrida escribe sus filas en el CSV a medida que terminan (append + flush). Si se corta, al
  relanzarla se saltan los `id` que ya existen en el CSV (reanudación).

## Restricciones

- NO modificar `src/`, `comun.py` ni ningún script existente. Cada `.py` nuevo debe tener como
  máximo 200 líneas: si hace falta, varios scripts.
- Cada evaluación usa `comun.evaluar_punto(combo, motor=..., tag=..., t_amb_diseno=...)`. El motor
  principal es `motor="teqp"`. `ProcessPoolExecutor(max_workers=7)`. No hacer commit. No inventar
  datos.
- **Punto genuino** = clase KALINA, CORREGIBLE o INVIABLE. `convergio=True` con clase
  NO_CONVERGIO es un punto espurio (N2) y NO cuenta como genuino.
- **KALINA confiable** = KALINA, `fuera_rango == False` y `B_verificado == True`. Todo conteo y
  todo rango se reporta DOS veces: para todos los KALINA y para los KALINA confiables.

## La pregunta

¿Qué datos del profesor se pueden conservar tal cual y aun así obtener un ciclo KALINA? ¿Cuál es el
**conjunto máximo** de sus datos compatible con KALINA? Y, para cada conjunto conservado, ¿en qué
rangos quedan las demás variables, en especial P_alta, P_baja, dP = P_alta − P_baja y
rP = P_alta/P_baja? La eficiencia es SECUNDARIA: se reporta, pero no se optimiza.

## Grupos de datos del profesor (valores de `comun.PROFESOR`)

| Grupo | Variables conservadas |
|---|---|
| `TF` | T_fuente = 623.15 |
| `EF` | eta_t = 0.85, eta_p = 0.75, eps_hrvg = 0.85, eps_reg = 0.75, eps_cond = 0.80 |
| `PA` | P_alta = 3000 |
| `PB` | P_baja = 400 |
| `TS` | T_sumidero = 300.032917 |
| `XB` | x_b = 0.50 |

## Presupuesto de tiempo (OBLIGATORIO): 4 h de pared como máximo, todo incluido

- Referencia: con teqp, ~50–90 s por punto con 7 procesos, es decir, ~10 s efectivos por punto.
- El total planificado es de ~1 150 corridas teqp, unas 3.2 h.
- Se anota la hora de inicio en `m9_tiempos.csv`. Si al ir a empezar una ronda del paso 2 ya pasaron
  **3 h 15 min** desde el inicio del paso 0, esa ronda NO se lanza: se pasa al paso 4 y el reporte
  lo dice ("escalera cortada por tiempo en la ronda N").

## Caja de las variables libres (acotada con lo aprendido en M2–M5c)

- P_alta: 2000–5000 kPa.
- P_baja: 300–2000 kPa. Ningún KALINA previo quedó por debajo de 445 kPa con un clima de 27 °C ni
  por debajo de ~290 kPa con 5 °C.
- T_fuente: 380–520 K cuando T_fuente es libre. En M4b ningún KALINA pasó de ~491 K. Las
  fuentes calientes, con ε_HRVG bajo, ya las cubre el escenario `C_TF`.
- T_sumidero: 278.15–303.55 K.
- x_b: 0.50–0.85; eta_t, eta_p, eps_hrvg, eps_reg y eps_cond: 0.40–0.95.
- m_b = 1.0.
- Piso de O2: `t_amb_diseno = combo["T_sumidero"]`, la del propio punto.
- Si `P_baja ≥ P_alta − 300`, el punto no se evalúa: `omitido=True`, con el motivo en `mensaje`.
- Muestreo: `scipy.stats.qmc.LatinHypercube(d=n_libres, seed=...)`, escalado a la caja. La muestra
  se guarda en un CSV ANTES de correr.

## Paso 0 — Húsavík (solo teqp)

Punto base, tomado de `resultados/barridos_2026-09-19/fase3_real/CASO_HUSAVIK_v2.md` §1.0:
P_alta 3300, P_baja 690, x_b 0.82, T_fuente 394.15, T_sumidero 278.15, eta_t 0.90, eta_p 0.80,
eps_hrvg 0.85, eps_reg 0.75, eps_cond 0.95, m_b 1.0.

- Malla de P_baja: 500 a 1000 kPa en pasos de 50 kPa (11 valores, con el resto en la base).
- Cada valor se evalúa con dos pisos: `t_amb_diseno = 283.15` (el del caso) y `278.15` (el criterio
  de esta campaña, piso = T_sumidero). Son 22 corridas.
- **El paso 0 y el paso 3 (motor real) van juntos en un mismo pool de 7 procesos**, para que los 3
  puntos lentos del motor real corran mientras se hace Húsavík. Duración estimada: ~25–30 min.
- Salida: `m9_husavik.csv`. Se reporta la P_baja mínima KALINA con cada piso y la η en 690 kPa.

## Paso 1 — conservar UN solo grupo (6 escenarios × 100 = 600 corridas, ~1 h 40 min)

- Escenarios `C_TF`, `C_EF`, `C_PA`, `C_PB`, `C_TS` y `C_XB`.
- En cada uno se fija el grupo y el resto queda libre en la caja. LHS de 100 puntos con
  `seed = 20261008 + k` (k = 1…6, en ese orden).
- Todo va en un solo pool. Salidas: `m9_paso1_muestra.csv` y `m9_paso1.csv` (columnas
  `escenario, conservados, id, omitido` + `comun.COLS`).

## Paso 2 — sumar grupos de a uno (selección hacia adelante)

1. **Ranking de un conjunto:** primero por el número de KALINA confiables; si empatan, por el número
   total de KALINA; y si vuelven a empatar, por la menor D mínima entre los genuinos.
2. **Ronda 1:** el mejor escenario del paso 1 es el conjunto S. Para cada grupo g que no esté en S,
   se corre el escenario `S∪g` con un LHS de **50 puntos** (`seed = 20261108 + índice correlativo
   de escenario del paso 2`).
3. **Rondas siguientes:** S pasa a ser el mejor `S∪g` de la ronda, con el mismo ranking, y se repite
   con 50 puntos por conjunto. Se termina con la primera de estas condiciones:
   - ningún `S∪g` de la ronda tiene KALINA;
   - S ya contiene 4 grupos (máximo 3 rondas: 5 + 4 + 3 conjuntos × 50 = 600 corridas como tope,
     pero lo habitual es cortar antes);
   - se cumple el tope de tiempo de 3 h 15 min.

   Las rondas que se corten se reportan como "no exploradas", NO como "sin KALINA".
4. **Búsqueda dirigida cuando un conjunto da 0 KALINA:** el LHS puede fallar en franjas angostas
   (lección de M5 → M5c). Para cada `S∪g` de la ÚLTIMA ronda con 0 KALINA:
   - se arranca desde su genuino de menor D;
   - se hace una búsqueda por patrones que minimiza SOLO D, sobre las variables libres
     normalizadas a [0, 1];
   - paso inicial 0.15 (pasos grandes), que se divide a la mitad cuando ningún vecino ±paso mejora;
     paso mínimo 0.02; máximo **40 evaluaciones** por conjunto y como mucho 2 conjuntos (los 2 de
     menor D_min);
   - se detiene apenas encuentra D = 0 (KALINA).

   Lee `scripts/barrido_final/m7_optimizar.py` y reutiliza `_a_u`, `_de_u` y `_candidatos` si
   sirven, sin modificar ese archivo.
5. Salidas: `m9_paso2.csv` (todas las corridas del paso 2, con `ronda`), `m9_busqueda.csv` y
   `m9_escalera.csv`. Este último tiene una fila por conjunto evaluado con estas columnas:
   ronda, conservados, n_conservadas (número de variables), n_eval, n_genuinos, n_kalina,
   n_kalina_confiable, D_min, criterio_mas_roto, elegido (bool) y kalina_por_busqueda (bool).

## Paso 3 — motor real, solo 3 puntos de control

- Puntos:
  - el ancla A\* (`dict(PROFESOR, T_fuente=403.0, P_baja=563.6363636363637)`, piso 300.032917);
  - el óptimo A4 de `resultados/2026-10-07_final_M7/m7_optimos.csv` (piso = su T_sumidero);
  - la base de Húsavík (piso 283.15).
- Con `motor="real"` y un límite de tiempo de **1500 s**. En M6, con 300 s el motor real casi nunca
  alcanza a converger. El límite se cambia SIN modificar `comun.py`.
- Se corre en el MISMO pool que el paso 0, al inicio (ver paso 0). Se usa una función envoltorio de nivel de módulo en el script nuevo. Antes de llamar a
  `evaluar_punto`, hace `comun.PRESUPUESTO_S = 1500` si `motor == "real"` y `= 300` si no. Así teqp
  conserva sus 300 s.
- Salida: `m9_motor_real.csv`, con la comparación contra la fila teqp del mismo punto: clase de cada
  motor, η de cada motor y `d_eta_pp` (teqp: tómala del paso 0 para Húsavík, de
  `resultados/2026-10-08_final_M6/m6_verificacion.csv` para A\* y A4).

## Paso 4 — análisis y reporte

En `resultados/2026-10-08_final_M9/`:

- `m9_rangos.csv`: por escenario con KALINA, para cada variable libre más dP y rP, el mín, p5,
  mediana, p95 y máx dentro de los KALINA y dentro de los KALINA confiables, más el KS (RSA) contra
  los no KALINA genuinos cuando hay ≥ 10 KALINA.
- `m9_escalera.png`: diagrama de la escalera, con cada conjunto como nodo con su n_KALINA y
  n_KALINA confiable, y el camino elegido resaltado.
- `m9_plano_presiones.png`: plano P_alta–P_baja con:
  - los KALINA de `resultados/2026-10-07_final_M4b/m4b_lhs.csv` en gris;
  - los KALINA de M9, coloreados por escenario;
  - el punto del profesor (3000/400) marcado con una X;
  - Húsavík (3300/690) marcado con una estrella.
- `REPORTE_M9.md`, en lenguaje llano:
  - la pregunta;
  - qué se hizo;
  - la tabla de la escalera;
  - el **conjunto máximo de datos del profesor compatible con KALINA**, con los rangos de lo que
    queda libre;
  - qué grupo bloquea y con qué criterio;
  - Húsavík: si cae dentro de la ventana KALINA y con qué P_baja mínima;
  - los 3 puntos del motor real;
  - lo que no se sabe.

  Las cifras salen todas de los CSV. Cada KALINA fuera de rango se nombra como tal ("fuera del rango
  confiable del motor").
- `m9_verificar.py`: recalcula desde los CSV las cifras del reporte e imprime OK o FALLA por cada
  una.

## Paso 5 — Excel

1. `scripts/barrido_final/excel_m9.py`, con el patrón de `excel_m5c_m7_m8.py` (léelo: reutiliza
   `excel_final.escribir_tabla`, es idempotente y añade o actualiza sus filas en `Resumen`). Hojas:
   `M9_husavik`, `M9_paso1`, `M9_paso2`, `M9_busqueda`, `M9_escalera`, `M9_rangos`,
   `M9_motor_real` y `M9_figuras` (las 2 imágenes).
2. Ejecuta en orden `excel_final.py`, `excel_m2.py`, `excel_m3_m2r.py`, `excel_m2s_m4.py`,
   `excel_m5.py`, `excel_m5c_m7_m8.py`, `excel_m6.py` (si existe) y `excel_m9.py`.
3. Verifica con un script hecho con `write`:
   - que las hojas M9 existen con el número de filas de su CSV;
   - que todas las hojas anteriores siguen presentes;
   - que `Resumen` tiene las filas de M9.

## Pasos

1. Crear los scripts. Humo con `M9_HUMO=1`: 2 puntos por escenario del paso 1 y 2 de Húsavík, en
   `resultados/2026-10-08_final_M9/humo/`.
2. Corrida: paso 0 → paso 1 → paso 2 (ronda por ronda) → paso 3 → paso 4 → paso 5.

## Formato de salida

El obligatorio de `AGENTS.md`.

## LECCIONES DE LA CORRIDA ANTERIOR (071, abortada por el director) — OBLIGATORIAS

La corrida 071 se detuvo porque:

1. Inventó funciones que NO existen en `comun.py` (`_inicializar_csv`, `_fila_desde_res`,
   `_append_csv`, `_fila_omitido`, `COLS_MUESTRA`).
2. Corría en serie, sin pool.
3. Pasaba `t_amb_diseno` dentro de `combo`.
4. Lanzó la corrida con el timeout por defecto de 120 s de la herramienta shell, y la corrida murió.
5. Ejecutó `taskkill /IM python.exe /F`, que está PROHIBIDO porque puede matar procesos ajenos.

Por eso, ahora:

- `comun.py` exporta SOLO `PROFESOR`, `T_AMB_DISENO`, `TAU`, `PRESUPUESTO_S`, `VARS`, `COLS`,
  `margenes`, `indice_D` y `evaluar_punto`. No uses nada más de `comun`.
- **Plantilla obligatoria:** `scripts/barrido_final/m5_corrida.py`. Léelo entero y copia su
  estructura: muestra LHS → `ProcessPoolExecutor(max_workers=7)` + `as_completed` → `csv.DictWriter`
  con flush por fila. El `combo` lleva solo las 11 variables (las de `PROFESOR`) y `t_amb_diseno` va
  como argumento aparte de `evaluar_punto`.
- Los archivos `scripts/barrido_final/m9_corrida.py`, `m9_humo.py` y `m9_main.py` que dejó la 071
  están mal. SOBRESCRÍBELOS con `write`, o reemplázalos por scripts nuevos.
- **Cada comando de corrida larga se lanza con el parámetro `timeout` de la herramienta shell en
  14400000 ms (4 h).** Nunca con el valor por defecto.
- Nunca `taskkill /IM python.exe`, ni `Stop-Process` por nombre.
- La carpeta `resultados/2026-10-08_final_M9/` está vacía salvo `humo/`. El reloj de 4 h arranca de
  nuevo con el paso 0.
