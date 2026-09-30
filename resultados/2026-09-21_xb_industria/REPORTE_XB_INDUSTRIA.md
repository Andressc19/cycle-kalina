# Reporte — ¿Converge x_b industrial (0.78–0.85) subiendo P_alta?

Fecha: 2026-09-21 · Rama: `test/teqp-con-validacion` · Motor: **solo `TeqpAdapter`**
(no se usó `AmmoniaWaterAdapter`, nada toca `src/`).

## Resumen ejecutivo

Con `T_fuente=470.0 K` fijo y `x_b` en 0.78–0.85, **sí hay puntos que convergen
subiendo `P_alta` a 6000 kPa**, pero con `P_baja=400` (valor del profesor) todos
son **peores que el caso de `x_b` bajo**: η cae a ~0.022 o se vuelve negativa
(INVIABLE/O3). La clave inesperada es que **`P_baja` es el grado de libertad que
rescata el punto**: elevando `P_baja` a ~900–1000 kPa el ciclo alcanza
η ≈ 0.14–0.16 con Wnet ≈ 180–195 kW (mejor que el 0.115 / 96 kW del caso
KALINA con `x_b` bajo), pero **ningún punto clasifica KALINA** — O2 (riesgo de
cavitación contra el piso de diseño T_amb = 30.4 °C) cierra el margen de
-37 K a ≈ -1.5 K pero **nunca llega a 0**, y O1 (título de turbina < 0.90)
se viola en 0.78/0.82/0.85.

## Datos del barrido

Ventana principal: `P_alta` ∈ [6000, 10000] kPa paso 250 (17 puntos) con
`P_baja=400` fija. Borde de diagnóstico: {5000, 5250, 5500, 5750, 10500} kPa.
Barrido de `P_baja`: {500..1500} paso 100 en el `P_alta` convergente mínimo.

Resto de parámetros (fijos por instrucción del director): `T_sumidero=300.032917 K`,
`m_b=1.0 kg/s`, `eta_t=0.85`, `eta_p=0.75`, `eps_hrvg=0.85`, `eps_reg=0.75`,
`eps_cond=0.80`.

117 puntos registrados en `barrido_xb_industria.csv` (ninguno se ocultó):
45 CORREGIBLE · 43 NO_CONVERGIO · 29 INVIABLE.

## Tabla resumen

### Por x_b — mínimo `P_alta` convergente y mejor punto variando `P_baja`

| x_b | P_alta min convergente (P_baja=400) | Clasificación del mejor punto | Mejor η | Punto (P_alta/P_baja) | Wnet [kW] | T2 [K] | q2 | Margen O2 [K] | Fallas |
|---|---|---|---|---|---|---|---|---|---|
| 0.78 | 6000 kPa | CORREGIBLE | 0.1562 | 6000 / 800 | 191.8 | 457.0 | 0.884 | **-9.94** | O1, O2 |
| 0.80 | 5000 kPa (*) | CORREGIBLE | 0.1400 | 5000 / 900 | 179.9 | 447.1 | 0.903 | **-5.13** | O2 |
| 0.82 | 6000 kPa | CORREGIBLE | 0.1572 | 6000 / 900 | 195.3 | 449.3 | 0.900 | **-5.81** | O1, O2 |
| 0.85 | 6000 kPa | CORREGIBLE | 0.1604 | 6000 / 900 | 194.2 | 443.4 | 0.917 | **-7.01** | O1, O2 |

(*) `x_b=0.80` **no converge en la ventana 6000–10000** (todo
`NO_CONVERGIO`/`PropertyRangeError`); solo converge en el borde 5000–5750 kPa
(con `P_baja=400`: INVIABLE) y 10500 kPa no converge.

Nota de lectura del margen O2: negativo = riesgo de cavitación declarado
(columna O2 se marca si `T9 > T_bubble(P_baja, x_b)` bajo `max(T_sumidero,
30.4 °C)`). Todos los mejores puntos quedan **CORREGIBLE por O2**, ninguno KALINA.

### Con `P_baja=400` fija (valor del profesor) — peor aún

| x_b | Mejor η en P_baja=400 | Clasificación |
|---|---|---|
| 0.78 | 0.0220 (6000 kPa) | CORREGIBLE (O1, O2) |
| 0.80 | — (sin convergencia en la ventana; borde 5000–5750 con η –0.004…–0.013) | INVIABLE |
| 0.82 | -0.0702 (6000 kPa) | INVIABLE (O3) |
| 0.85 | -0.1949 (6000 kPa, solución con N2 roto) | NO_CONVERGIO (N2) |

## Comparación contra el hallazgo previo (`x_b` bajo)

Referencia previa documentada: `x_b≈0.28–0.29`, `P_alta=3000`, `P_baja=400`
→ **KALINA, η ≈ 0.115, Wnet ≈ 96 kW** (motor real). Verificación puntual con
`TeqpAdapter` en esta tarea: `x_b=0.29` → CORREGIBLE (solo O2), **η=0.1181**,
Wnet=96.4 kW, margen O2 = -0.20 K (consistencia del pipeline).

Camino `x_b` industrial probado aquí:

- **Con `P_baja=400`, `x_b` alto es decididamente PEOR**: η ≤ 0.022 o negativa.
  La composición industrial NO recupera el punto de operación del profesor en
  esa presión de baja, ni siquiera subiendo `P_alta` a 6000–10000 kPa.
- **La combinación `x_b` alto + `P_alta` ≈ 6000 + `P_baja` ≈ 900 da mejor η
  (0.140–0.160 vs 0.115) y ~2× Wnet (180–195 kW vs 96 kW)**, pero sacrifica
  KALINA: nunca cierra O2 (el margen mejora de -37 K a ≈ -1.5…-5 K pero no
  llega a 0) y, en 0.78/0.82/0.85, viola también O1.

## Hallazgos inesperados

1. **`P_baja` es el grado de libertad que rescata el punto, no `P_alta`.** η
   sube bruscamente al crecer `P_baja` de 400 a ~900 (0.022 → 0.156 en x_b=0.78;
   de negativo → 0.14 en x_b=0.80) y luego cae. El óptimo de η está en
   `P_baja≈900–1000`, muy por encima de los 400 del profesor.
2. **El margen O2 mejora monótonamente con `P_baja` pero NO se cierra ni a
   1500 kPa** (mínimos |margen| ≈ 1.5–2.7 K). Respuesta a la pregunta de la
   tarea: en composición alta el cierre de O2 con `P_baja` es parcial, igual que
   en el caso `x_b=0.50` ya diagnosticado (que tampoco cerraba a 1500). Faltaría
   el escalón de diseño (subenfriamiento extra del condensador), que está fuera
   de alcance (eps_cond fijo por orden del director).
3. **`x_b=0.80` presenta un hoyo de convergencia**: ventana 6000–10000 kPa toda
   NO_CONVERGIO (`PropertyRangeError` del motor teqp en `T_from_Ph`/`h(P,s,x)`),
   con banda convergente solo a 5000–5750 e infeasible a 10500+. No es monotónico
   en `P_alta` — sensibilidad del dominio del motor/campana.
4. **El solver a veces "converge" a soluciones no físicas cerca de la campana**
   (ej.: x_b=0.85, 6000/400 → η=-0.195, q2=1.0, N2 abierto, C1/C3 rotos).
   El criterio N2 las marca NO_CONVERGIO y no se ocultan, pero conviene anotarlo
   como robustez numérica pendiente (el punto se resuelve, no es que brentq
   falle).
5. Cota de Carnot del punto: η_Carnot = 1 - T_sumidero/T_fuente = 0.3616; los
   mejores puntos alcanzan ~0.44 × Carnot.

## Metodología y límites

- Únicamente `TeqpAdapter` — motor experimental/expeditivo del repo
  (validado <0.5 % en h/s contra el motor real, pero es el camino rápido, no la
  verificación final). Tiempo por punto 0.1–100 s; corrida total ≈ 65 min en 4
  tandas (script con reanudación por CSV, sin tocar `src/`).
- Todo punto probado —converja o no— está en el CSV con
  `detalle_error` cuando aplica (`PropertyRangeError` con mensaje del motor tal
  cual). Sin reintentos con otro motor (norma de la tarea).
- Los valores reportados son del motor teqp; antes de cualquier decisión de
  diseño conviene verificar los ~5 mejores puntos con `AmmoniaWaterAdapter`
  (≈9 min/punto) — fuera del alcance de esta tarea (prohibido usarlo aquí).

## Entregables

- `barrido_xb_industria.csv` — 117 puntos, columnas: x_b, P_alta, P_baja,
  etiqueta_punto, convergio, clasificacion, eta, Wnet, fallas, detalle_error,
  T2, q2, O2_margen_K.
- Este reporte.