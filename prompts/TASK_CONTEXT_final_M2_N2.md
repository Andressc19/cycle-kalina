# TASK_CONTEXT — Campaña final, M2 nivel 2: ¿con DOS cambios al enunciado del profesor aparece KALINA?

**Fecha:** 2026-10-06 · **Rama:** `test/barrido_final` (commit base `02f64b6`)
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barrido-final`.
TODO se crea y se ejecuta aquí.
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`
**Leer antes de empezar:**
- `resultados/2026-10-06_final_M2/REPORTE_M2_N1.md`, **sobre todo §9 (nota del director)**;
- `scripts/barrido_final/comun.py` (reutilizar `evaluar_punto`, `PROFESOR` y `COLS`);
- `scripts/barrido_final/m2_nivel1.py` (patrón de pool, CSV con flush y rondas de bisección);
- `scripts/barrido_final/excel_m2.py`.

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`. NUNCA desde la
  terminal: nada de heredocs, here-strings, `Set-Content` ni `python -c` que escriba archivos.
- La terminal es PowerShell 5.1. No existen `tee` ni `&&`: usa `Tee-Object` y `;`.
- Las verificaciones van en un script escrito con `write`; no uses `python -c` de varias líneas.
- Lanza la corrida larga UNA sola vez y espera a que termine.

## Restricciones

- NO modificar `src/`, `app.py`, `ui_*.py`, `scripts/formatear_excel_barridos.py`,
  `m1_reproducir_f1.py`, `m2_nivel1.py` ni `comun.py`.
- Cada `.py` debe tener como máximo 200 líneas.
- No inventar valores. Todos los rangos y reglas están aquí; lo que falte va a UNRESOLVED.
- Nunca reportar una ejecución que no ocurrió. No hacer commit.

## Definiciones clave (leerlas con cuidado: el nivel 1 se equivocó aquí)

- **Punto genuino:** `clasificacion ∈ {KALINA, CORREGIBLE, INVIABLE}`. Una fila con
  `convergio=True` pero `clasificacion == "NO_CONVERGIO"` es un **punto fijo espurio (N2)** y se
  trata como NO convergido en TODO: conteos, fronteras y conclusiones.
- **Los criterios bloqueantes** se cuentan SOLO sobre los puntos genuinos que no son KALINA.

## Diseño

El primer cambio destraba el lado caliente (lo que mostró el nivel 1). El segundo cambio es
**P_baja**, que según la regla del proyecto es la variable con la que se cierra O2 (nunca subiendo
las ε). Todas las demás variables quedan como en `PROFESOR`.

| Ruta | Variable 1 (valores fijos) | Variable 2 | Qué conserva del profesor |
|---|---|---|---|
| A — solo diseño | `eps_hrvg` ∈ {0.75, 0.78, 0.81} | P_baja | Toda la fuente y el sitio (T_fuente = 623.15 K) |
| B — sitio + diseño | `T_fuente` ∈ {380, 390, 403, 420, 434, 466, 497, 529, 560} K | P_baja | Todo, salvo la fuente |

**Fase A — malla.** Para cada valor de la variable 1 se usa
`P_baja ∈ numpy.linspace(400, 2000, 12)`. Son (3 + 9) × 12 = **144 corridas** con
`evaluar_punto(combo, motor="teqp", tag=...)`, en `ProcessPoolExecutor(max_workers=6)`.
- Las filas se escriben con flush en `resultados/2026-10-06_final_M2/m2n2_malla.csv`, con las
  columnas `fase, ruta, var1, val1, P_baja_val` más las de `COLS`.
- Después de cada fila se imprime `[n/144] ruta var1=val1 P_baja=... clase t_s`.

**Fase B — bisección sobre P_baja.** Para cada fila (ruta, val1), los 12 puntos se ordenan por
P_baja y se detecta cada par de vecinos donde cambia:
- (i) `es_kalina` (frontera "KALINA"), o
- (ii) `m_O2 >= 0`, solo cuando **ambos** vecinos son genuinos (frontera "O2").

Se bisecta con tolerancia de 10 kPa, como máximo 8 iteraciones, en rondas paralelas.
Para decidir de qué lado cae el punto medio en una frontera "O2":
- si el punto medio no es genuino, se trata como el lado "NO cumple";
- ese caso se registra en una columna `nota` con el texto "punto medio no genuino".

Cada evaluación se escribe con flush en `m2n2_biseccion.csv`.

## Salidas (en `resultados/2026-10-06_final_M2/`)

- **`m2n2_fronteras.csv`**: `ruta, var1, val1, frontera, P_baja_si, P_baja_no, ancho_final,
  iteraciones, clase_si, eta_si, D_si, fuera_rango_si, codigos_falla_si`.
- **`m2n2_kalina.csv`**: todas las filas KALINA (malla + bisección), con
  `d = |val1 − val1_prof|/(b1 − a1) + |P_baja − 400|/(1500 − 150)`.
  Rangos: eps_hrvg [0.75, 0.85] y T_fuente [340, 623.15], los mismos del nivel 1. Para P_baja
  se usa la escala del nivel 1, [150, 1500], **aunque aquí la malla llegue a 2000**; anotarlo en
  el reporte.
  Columnas: `ruta, var1, val1, P_baja, eta, Wnet, m_O1, m_O2, d, fuera_rango, detalle_rango,
  B_verificado`.
- **`m2n2_resumen.csv`**, una fila por (ruta, val1):
  - `n_genuinos`, `n_kalina` y `n_espurios_N2`;
  - `P_baja_min_kalina`, con su `eta` y su `fuera_rango`;
  - `P_baja_min_O2`, la menor P_baja con `m_O2 >= 0` entre los genuinos;
  - `mejor_D`, con su `P_baja`;
  - los bloqueantes genuinos más frecuentes.
- **`REPORTE_M2_N2.md`**, en lenguaje llano:
  1. La pregunta.
  2. Qué se hizo.
  3. Una tabla por ruta (una fila por val1: ¿hay KALINA?, la menor P_baja KALINA, η en ese punto,
     si está fuera de rango y qué bloquea si no hay KALINA).
  4. **El KALINA de menor d de cada ruta y el de mayor η de cada ruta.**
  5. Tiempos.
  6. Conclusión con la forma: "Con dos cambios sí/no se alcanza KALINA. Ruta A (conservando la
     fuente del profesor): … Ruta B: …".
  7. Lo que no se sabe. Debe incluir:
     - qué KALINA están fuera del rango confiable (T > 420 K de líquido);
     - que los puntos de bisección pueden caer en zonas espurias;
     - la resolución de la malla.
  8. Qué sigue (lo decide el director).
- **`scripts/barrido_final/excel_m2.py`** (EDITAR): añadir las hojas `M2_N2_malla`,
  `M2_N2_biseccion`, `M2_N2_fronteras`, `M2_N2_kalina` y `M2_N2_resumen`, junto con sus filas en
  `Resumen`. Si se vuelve a ejecutar, el resultado tiene que ser el mismo.

## Pasos

1. Crear `scripts/barrido_final/m2_nivel2.py`. Si hace falta para respetar las 200 líneas,
   separarlo en `m2_nivel2.py` (corrida) y `m2_nivel2_reporte.py` (resúmenes y reporte).
2. Humo con `M2_HUMO=1`: 1 valor por ruta × 2 valores de P_baja, sin bisección, con salida en
   `resultados/2026-10-06_final_M2/humo_n2/`.
3. Corrida real:
   `python scripts/barrido_final/m2_nivel2.py 2>&1 | Tee-Object -FilePath resultados/2026-10-06_final_M2/stdout_n2.txt`.
   Duración esperada: 60–100 min.
4. `python scripts/barrido_final/excel_final.py; python scripts/barrido_final/excel_m2.py`.
5. Verificar con un script de comprobación (como `comprobar_m2.py`; se puede crear
   `comprobar_m2n2.py`): conteos de los CSV, hojas del xlsx y que los números del reporte
   coinciden con los CSV.

## Formato de salida

El obligatorio de `AGENTS.md`. En RESULTS van la tabla resumen de las dos rutas y las rutas de los
archivos generados.
