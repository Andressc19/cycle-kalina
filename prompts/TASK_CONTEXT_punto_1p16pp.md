---
project: ciclo_kalina_tercero
task_id: 2026-10-13-punto-1p16pp
delegated_to: executor
model: opencode/big-pickle
created: 2026-10-13
---

# TASK_CONTEXT — Diagnóstico del punto del benchmark Elsayed con Δη = +1.16 pp (P_alta = 2300 kPa, x_b = 0.55)

## Task ID

2026-10-13-punto-1p16pp

## Contexto

El benchmark contra Elsayed et al. (2013) / Embaye (23 puntos comparables, |Δη| medio 0.27 pp)
tiene un máximo de 1.16 pp (12.1 %) en la fila 8 de
`resultados/2026-09-24_validacion_tendencias/validacion_tendencias.csv`:

`Fig7_KCS11_0p55, T_fuente=373, P_alta=2300, x_b=0.55, teqp, P_baja=273.545417,
eps_hrvg=0.728142, eps_reg=0.949199, eps_cond=0.928601, eta_modelo=10.7057 %,
eta_paper=9.547 %, delta=+1.1587 pp, q4=0.9501, Wnet=15.98 kW`.

Hay que **explicar el punto con cifras** (o dar los números para excluirlo con un criterio
uniforme). Este TASK_CONTEXT solo MIDE; no decide, no recalibra, no "arregla" nada.

Hipótesis a contrastar (H1 digitalización, H2 sensibilidad, H3 calibración de un paso / cota
q4, H4 ecuación de estado, H5 duplicados del paper). Hipótesis de trabajo de Claude (a
confirmar o refutar con los números): la curva del paper cae a ~0 en ~24.1 bar porque la
mezcla a la salida del HRVG (T2 = T_fuente − 4 K = 369 K, x = 0.55) llega a su punto de
burbuja ("muro de burbuja", fracción de vapor → 0); el modelo tiene ese muro más lejos, y cerca
del muro η es hipersensible a P y a T2.

## Reglas (obligatorias)

- Solo `write`/`edit` para crear archivos; **no inventes helpers**: usa exactamente las
  funciones nombradas abajo (`calibrar_P_baja`, `calibrar_eps`, `resolver_ciclo`,
  `backend.bubble_point`, `backend.fase_de`, `Perturbado`, `PerturbadoReal`).
- **Nunca leer ni escribir fuera de `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barrido-final`**
  (ni temporales). El sandbox aborta toda la ejecución.
- **No modificar** `src/`, `tests/`, `app.py`, `ui_*.py`, ni ningún archivo existente de
  `scripts/` o `resultados/`. Solo crear los archivos de la sección Files.
- Salidas nuevas en `resultados/2026-10-13_punto_1p16pp/`.
- No recortar, redondear ni "arreglar" ε fuera de [0.40, 0.95]: se registran tal cual.
- Todo script: ≤ 250 líneas, reanudable por CSV (clave de fila), excepciones por fila
  registradas en una columna `error` sin abortar. No imprimas trazas largas.
- Motor: `TeqpAdapter(x=0.55)` salvo el paso REAL (`AmmoniaWaterAdapter(x=0.55)`).
- Constantes del benchmark (importar de `scripts/calibracion_elsayed_malla.py`): `T_SUMIDERO`,
  `ETA_T`, `ETA_P`, `M_B`, `PINCH`. T_fuente = 373 K. Usar `sys.path.insert(0, scripts_dir)`
  como hacen `validacion_tendencias_embaye.py` e `incertidumbre_eta_real.py`.

## Paso 1 — `scripts/punto_1p16_datos.py` (sin motor; segundos)

Lee `resultados/2026-09-24_embaye_vectorial/curvas_embaye_fig7.csv` (curva
`KCS11(Con.=0.55)`) y `resultados/2026-09-24_validacion_tendencias/validacion_tendencias.csv`
(filas `motor == teqp` y `convergio == True`). Escribe en la carpeta de salida:

1. `h1_interpolacion.csv`: η_paper(P) para P = 2100, 2200, 2250, 2300, 2350, 2400 kPa con
   interpolación (a) lineal (`np.interp`, la usada por el benchmark), (b) `scipy.interpolate.PchipInterpolator`,
   (c) `scipy.interpolate.CubicSpline`; más la pendiente local dη/dP [pp/bar] de los dos
   vértices que encierran 2300 kPa.
2. `h1_desplazamiento.csv`: para cada punto del modelo de la serie Fig7_0p55 (7 puntos del
   CSV), P_paper en que la curva del paper alcanza ese mismo η_modelo (interpolando P como
   función de η sobre la rama descendente, P > 19.1 bar; vacío si no está en rango) y
   `dP_bar = P_modelo − P_paper`.
3. `h5_duplicados.csv`: η_paper del mismo estado (x_b=0.55, 1500 kPa) leído de la serie Fig7
   (11.4317) y de la Fig3 (11.3942) y del texto del paper (11.38); diferencias en pp.
4. `estadistica_con_sin.csv`: sobre los 23 puntos comparables (teqp, convergen,
   `titulo_salida_turbina` ≠ vacío y ≥ 0.90, `eta_paper_pct` ≠ vacío), filas con columnas
   `criterio, n, delta_medio_pp, absdelta_medio_pp, absdelta_max_pp, mediana_absrel_pct`:
   - `todos` (23);
   - `sin_punto_2300` (22);
   - `Wnet>=20kW` ; `Wnet>=25kW` ; `eps_hrvg>=0.80` ; `eps_hrvg>=0.85` (cada uno aplicado a los 23
     de forma uniforme; indicar en `n` cuántos quedan y listar en `excluidos` las claves
     `serie|P|x_b|T`).
5b. En `estadistica_con_sin.csv` añadir la fila `sin_punto_2300_por_decision` (= la de `sin_punto_2300`, etiquetada como exclusión por decisión del usuario, causa abierta, NO por criterio objetivo).
5. `diagnostico_23.csv`: los 23 puntos con `serie,T_fuente_K,P_alta_kPa,x_b,eps_hrvg,Wnet_kW,
   q4,delta_pp,delta_rel_pct` ordenados por `eps_hrvg` ascendente (para ver si Δ positivo se
   concentra en ε_HRVG bajo).

Comando exacto (timeout de la shell: 600000 ms):
`.venv/Scripts/python.exe scripts/punto_1p16_datos.py`

## Paso 2 — `scripts/punto_1p16_marcadores.py` (PDF vectorial; ~1 min)

Es una **copia** de `scripts/extraer_embaye_vectorial.py` con SOLO estos cambios:
- `PDF = r'D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barrido-final\Papers\PERFORMANCEOFKALINACYCLESYSTEM11KCS11USINGLOWTEMPERATUREHEATSOURCES.pdf'`
- el directorio `OUT` pasa a `resultados/2026-10-13_punto_1p16pp/_extraccion_marcadores`
  (el script original NO se toca y sus CSV/PNG originales NO se sobrescriben);
- en el bucle `for m in mark:` además de lo que ya hace, guardar para cada marcador el centro
  `c` convertido a datos con `inv(cal7,'x',c[0])` y `inv(cal7,'y',c[1])`, el nombre de curva
  `name` y `sep_pt` (la separación ya calculada), y al final volcar
  `resultados/2026-10-13_punto_1p16pp/h1_marcadores_fig7.csv` con columnas
  `curva,P_bar,eta_pct,sep_pt`.
Si el script copiado falla por algo distinto de la ruta/OUT, NO lo repares: repórtalo en
`UNRESOLVED` con el traceback corto. (Si no existe `pymupdf` en `.venv`, repórtalo.)

Comando exacto (timeout de la shell: 600000 ms):
`.venv/Scripts/python.exe scripts/punto_1p16_marcadores.py`

## Paso 3 — DIFERIDO POR EL USUARIO: NO EJECUTAR NI CREAR ESTE SCRIPT EN ESTA CORRIDA

(El usuario decidió excluir el punto por ahora y retomar el diagnóstico después de la entrega. Se conserva la especificación para esa fase.)

### `scripts/punto_1p16_motor.py` (teqp; ~40 min; timeout 3600000 ms)

Argumento `teqp` (este paso) o `real` (paso 4). Funciones: reutilizar `calibrar_P_baja` y
`calibrar_eps` (import de `calibracion_elsayed_malla`), `resolver_ciclo` (de
`src.cycle_solver`), `Perturbado` (import `incertidumbre_eta as I`, `I.Perturbado`,
`I.CASOS`, `I.COMUN`). Cada fila de cada CSV con `error` (vacío si OK).

**B1 — muro de burbuja** → `muro_burbuja.csv`: con `backend = TeqpAdapter(x=0.55)`,
`P_muro(dT)` = raíz en P (brentq, bracket [500, 6000] kPa) de
`backend.bubble_point(P, 0.55) - (373.0 - dT)` para `dT = 2, 3, 4, 5, 6` K. Columnas
`dT_K, T2_K, P_muro_kPa`. (dT=4 es el caso del benchmark.)

**B2 — curva fina del modelo** → `curva_fina.csv`: para P_alta (kPa) en
`2100, 2250, 2280, 2300, 2320, 2350, 2400, 2450, 2500, 2600` (2300 = reproducción del
benchmark: debe dar 10.7057 %): `P_baja = calibrar_P_baja(b, 0.55, P)`;
`cal = calibrar_eps(b, x_b=0.55, P_alta=P, P_baja=P_baja, T_fuente=373.0)`; registrar
`P_alta_kPa, P_baja_kPa, eps_hrvg, eps_reg, eps_cond, eta_pct, Wnet_kW, Qi_kW`(r["Qi"]),
`T2_K`(r["estados"]["e2"].T), `q2`(`b.fase_de(P, e2.T, e2.x)[1]`, vacío si falla),
`m3`(e3.m), `x3`(e3.x), `q4`(`b.fase_de(P_baja, e4.T, e4.x)[1]`), `error`.
Los puntos más allá del muro pueden fallar: se registran con su error (es un dato).

**B3 — sensibilidad a ε_HRVG y a P en 2300 kPa** → `sensibilidad_2300.csv`: con ε_reg,
ε_cond y P_baja de la fila 2300 de B2:
 (i) ε_HRVG = ε* + d, d ∈ {−0.05, −0.02, −0.01, +0.01, +0.02, +0.05} (P=2300 fija);
 (ii) P_alta ∈ {2280, 2320} con **las ε de 2300 fijas** (sin recalibrar);
 con `resolver_ciclo(backend, P_alta=..., P_baja=..., T_fuente=373.0, T_sumidero=T_SUMIDERO,
 x_b=0.55, m_b=M_B, eta_t=ETA_T, eta_p=ETA_P, eps_hrvg=..., eps_reg=..., eps_cond=...)`.
 Registrar `caso, eps_hrvg, P_alta_kPa, eta_pct, Wnet_kW, T2_K, error`. (La sensibilidad con
 recalibración ya sale de B2 en 2280/2320.)

**B4 — banda de propiedades en 2300 kPa** → `banda_2300.csv`: replicar
`incertidumbre_eta.py` (mismo `Perturbado`, mismos 7 `CASOS`: base, xL±, yV±, hE±) con el punto
`dict(P_alta=2300.0, P_baja=<B2>, T_fuente=373.0, x_b=0.55, eps_hrvg=<B2>, eps_reg=<B2>,
eps_cond=<B2>)` y `**I.COMUN`. Registrar `caso, eta_pct, Wnet_kW, error` y al final
las semibandas por grupo (|Δη| máximo de ± en pp) y el RSS, igual que `banda.csv` original.
Los casos que den `PropertyRangeError` quedan con su error (se repiten en el paso 4).

Comando exacto (timeout 3600000 ms; si se corta, relanzar el mismo comando: continúa):
`.venv/Scripts/python.exe scripts/punto_1p16_motor.py teqp`

## Paso 4 — DIFERIDO: NO EJECUTAR (motor real, 1–3 h)

Mismo script, argumento `real`: `AmmoniaWaterAdapter(x=0.55)` (de
`src.properties.ammonia_water_adapter`):
- `real_2300.csv`: calibración + solución a P_alta = 2300 kPa (mismas columnas que B2);
- para cada caso de `banda_2300.csv` con error, repetirlo con `PerturbadoReal` (import
  `incertidumbre_eta_real as R`, `R.PerturbadoReal`) → `banda_2300_real.csv`; incluir también
  el caso `base` con el motor real para medir la diferencia con el mismo motor.
Un punto a la vez, escribiendo a CSV tras cada uno. Si el motor real no converge, registrar.

Comando exacto (timeout 10800000 ms; reanudable):
`.venv/Scripts/python.exe scripts/punto_1p16_motor.py real`

## Files

Crear (esta corrida: solo pasos 1 y 2): `scripts/punto_1p16_datos.py`, `scripts/punto_1p16_marcadores.py`, y los CSV de `resultados/2026-10-13_punto_1p16pp/` indicados.
NO crear el reporte `.md` (lo redacta Claude).

## Acceptance criteria

1. Los 5 CSV del paso 1 existen y `todos` reproduce n=23, Δ medio −0.0615, |Δ| medio 0.2749,
   |Δ| máx 1.1587.
2. `h1_marcadores_fig7.csv` existe con los marcadores de ambas curvas KCS11.
(Criterios 3–5, de los pasos 3 y 4, quedan diferidos.)

## Verification

Salida final en el formato obligatorio de AGENTS.md. En `RESULTS`, imprimir: η_paper(2300) por
cada interpolación; P_muro por dT; la tabla `curva_fina` (P, η, Wnet, q2); la tabla de
`sensibilidad_2300`; las semibandas; y la fila `todos`/`sin_punto_2300` de la estadística.
