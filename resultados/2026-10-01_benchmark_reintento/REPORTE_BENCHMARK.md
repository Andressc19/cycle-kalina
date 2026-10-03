# Cierre del benchmark de tiempos del arranque en frío — informe

**Tarea:** `2026-10-01-benchmark-continuacion` (continúa `2026-10-01-benchmark-cierre-topes`).
**Fecha:** 2026-10-01. **Rama durante toda la corrida:** `feature/rango_motores`. `git status --short src`: vacío al inicio y vacío al final (nada de `src/` se tocó).
**Motor de propiedades:** `TeqpVerificado` en las 253 mediciones nuevas (160 de A2 + 93 de B2).

---

## 1. La pregunta

Cuando el solver arranca en frío (sin temperatura inicial), unas 40 de cada 100 filas
de un barrido no las resuelve. La pregunta es: **¿cuál es la forma más barata de
recuperar esas filas?**

Y una pregunta previa, que es la que originó el error que esta tarea corrige:
**¿basta con poner un tope ("tope 6") al reintento, o hay que dejarlo sin tope?**

---

## 2. Glosario en una línea

| Término | Qué significa aquí |
|---|---|
| **M0** | Modo base: arranque en frío (temperatura inicial `None`) y el bracket original de `src/_cycle_loops.py`, que solo amplía el rango **hacia fuera**. |
| **MA** | Modo "V2 desde el primer intento": arranca en `T_sumidero + 5 K` y usa un *bracket tolerante* que repliega los extremos 5 K **hacia dentro**. Es el modo que produjo la variante V2 de la ablación de tiempos. |
| **MB** | Modo "reintento": corre **M0**; si M0 lanza un error **durante el bracketeo**, repite el intento entero con el bracket tolerante. Si M0 converge, MB es M0 exactamente (mismo resultado, mismo coste). |
| **tope** (`max_repliegues`) | Máximo número de veces que el bracket tolerante repliega un extremo hacia dentro antes de rendirse. `tope 2` = 2 intentos por extremo, el primero incluido. **`None` = sin tope**: repliega hasta agotar el rango físico. |
| **ST** (salida temprana) | Atajo: si el primer intento del extremo alto y el del extremo bajo fallan ambos con "no existe equilibrio bifásico", se rinde sin repliegar. |
| **nF** | Número de evaluaciones del ciclo completo (`evaluar()`) que consumió la medición. Proxy del trabajo real. |
| **fila recuperada** | Fila que el modo resuelve (`convergio = True`), sin importar la clasificación de calidad que salga. |
| **repliegue** | Un paso de 5 K hacia dentro de un extremo del bracket. |
| **CPU s / pared s** | `t_s` es tiempo de CPU de esa fila; el "de pared" es el reloj que ve el usuario (con 6 workers en paralelo, ≈ CPU/6). |
| **KW** | Los 13 números que definen un punto del barrido (presiones, temperaturas, exergy objetivo, tolerancias…). |

---

## 3. Corrección del error de los topes

La tarea anterior **(dio por hecho)** que "tope 6 = el V2 actual". **Es falso.**

`_bracket_tol` de `scripts/sonda_arranque_solver.py` **no tiene tope de intentos**: repliega
5 K por vez mientras quede rango. `benchmark_modos._bracket_tope` (el que se usó para
medir "tope 6") **sí** lleva tope. Por eso "tope 6" no era V2:

- con **tope 6**, MB rescata **11 de las 40** filas que M0 no resuelve;
- **V2** (sin tope) rescata **28**.

Un tope, por pequeño que sea, cambia el resultado. Por eso los topes {2, 3, 6} no
servían para decidir nada, y esta tarea los vuelve a medir con la instrumentación
correcta (`_bracket_sin_tope`, copia fiel de `P._bracket_tol`).

### 3.1 Control de coherencia (el que pedía el director)

> *MB sin tope debe reproducir las 28 filas que rescata V2, con |Δη| < 1e-6.*

Resultado (calculado con el código original `benchmark_cierre_topes.control_v2`, sin tocarlo):

```
CONTROL V2: V2 rescata 28/40, MB sin tope 27/40, comunes 27,
            max|d eta| = 0.000e+00, solo V2 = [('barrido_literatura_kcs11', 20)],
            solo MB = []
```

- En las **27 filas comunes**, `MB sin tope` da **exactamente** la misma `eta` que V2
  (diferencia 0.000e+00, no "menor que 1e-6": cero). El bracket sin tope es una copia
  fiel del de V2. ✅
- **Falta una fila**: `barrido_literatura_kcs11` #20. **Explicada, no es un fallo de la
  copia del bracket** (ver §5.3): MB ni siquiera intenta el reintento en esa fila, porque
  la regla de MB solo reintenta si el fallo ocurre *durante el bracketeo* y ahí el fallo
  aflora ya en `brentq`. V2, que aplica el arranque en caliente desde el principio, sí
  converge.
- MB **nunca** rescata una fila que V2 no rescata (`solo MB = []`).

---

## 4. Cómo se midió

### 4.1 Qué se reutilizó (no se recalculó)

| Desde | Qué | Cuántas filas |
|---|---|---|
| `benchmark_filas.csv` (etapa A1) | M0 y MB con topes 2, 3, 6 sobre las 40 filas que M0 no resuelve | 280 |
| `benchmark_filas.csv` (etapa A2) | M0 y MB_t6_STno sobre 30 filas "sanas" (las que el barrido original sí resolvió) | 60 |
| `benchmark_minibarrido.csv` | Los 93 puntos del mini-barrido × M0 / MA / MB_t6_STsi | 279 |
| `ablacion_filas.csv` | La ablación de 56 filas; de ella sale el coste de MA (= V2) | 56 |
| Los 7 CSV de `resultados/` | Conteos de filas y `NO_CONVERGIO` de cada barrido histórico | — |

### 4.2 Qué se midió de nuevo

**253 mediciones**, todas con `TeqpVerificado` y la misma instrumentación
(`benchmark_modos.medir`: cronómetro, `nF`, clasificación, y verificación de turbina
`verificar_turbina` + `AmmoniaWaterAdapter` en cuanto sale una fila `KALINA`):

- **A2 — 160 mediciones**: 4 configuraciones nuevas × 40 filas que M0 no resuelve.
  Configuraciones: `MB_t10_STno`, `MB_t15_STno`, `MB_sintope_STno`, `MB_sintope_STsi`.
- **B2 — 93 mediciones**: solo `MB_sintope_STno` sobre los mismos 93 puntos del
  mini-barrido. M0 y MA se copiaron del CSV anterior (columna `origen` los distingue).

### 4.3 Instrumentación por fila

Cada fila del CSV lleva: `convergio`, `causa`, `clasificacion`, `eta`, `T1_sol`, `nF`,
`t_s`, `nF_intento1`, `t_intento1_s` (tiempo del intento fallido), `reintento_usado`,
`punto_cascada` (qué componente lanzó el error), `msg`, `msg_intento1`, `st_disparo`,
`fase_fallo` (`bracket` / `brentq` / `final`), `B_verificado`, `B_dh4s` y los 13 `kw`.

### 4.4 Scripts

| Script | Papel |
|---|---|
| `scripts/benchmark_cierre_modos.py` | Modos y carga de filas. **Corregido** (ver §6). |
| `scripts/benchmark_cierre_a2.py` | **Nuevo.** A2 y B2 incrementales y reanudables. |
| `scripts/benchmark_cierre_informe.py` | **Nuevo.** A3 y A4: solo recalcula cifras desde los CSV. |
| `scripts/benchmark_extrapolacion_cierre.py` | **Nuevo.** Parte C (copia mejorada de `benchmark_extrapolacion.py`). |
| `scripts/benchmark_cierre_topes.py` | Original, **sin tocar**. Se usó su etapa `control`. |

---

## 5. Resultados

### 5.1 A2 + A4 — ¿qué configuración recovers más filas y a qué precio?

Las 40 filas que M0 no resuelve (M0 recupera **0/40**). Cifras recalculadas desde los
CSV; la tabla suma 6 configuraciones × 40 filas = 240 mediciones.

| Configuración | Tope | Recuperadas | CPU total (s) | CPU mediana (s) | CPU máx (s) | nF medio | Filas/1000 s |
|---|---:|---:|---:|---:|---:|---:|---:|
| MB_t2_STno | 2 | 3/40 | 832.41 | 18.58 | 56.15 | 5.40 | 3.60 |
| MB_t3_STno | 3 | 4/40 | 974.32 | 21.22 | 60.32 | 6.58 | 4.11 |
| MB_t6_STno *(reutilizado)* | 6 | 11/40 | 1850.68 | 29.58 | 184.61 | 10.48 | 5.94 |
| MB_t10_STno | 10 | 16/40 | 4503.34 | 81.15 | 540.44 | 14.18 | 3.55 |
| MB_t15_STno | 15 | 25/40 | 6462.60 | 102.45 | 837.91 | 17.85 | 3.87 |
| **MB_sintope_STno** | **sin tope** | **27/40** | **5451.42** | 108.66 | 499.92 | 17.25 | **4.95** |
| MB_sintope_STsi *(sin tope + ST)* | sin tope | 27/40 | 5268.70 | — | — | 17.25 | 5.12 |

**Criterio aplicado (el exacto del director):** entre las configuraciones con ST no, la
de **menor tope que recupera el mismo número de filas que "sin tope"**.

> **Ninguna configuración con tope empata con "sin tope" (27).** El conjunto de candidatas
> queda reducida a un único elemento: `MB_sintope_STno` ella misma (tope 10⁶). La más
> cercana es `MB_t15_STno` con 25/40 (−2).

**Elegida por el criterio: `MB_sintope_STno`.** Aviso al director (la decisión es suya):

- Si la intención del criterio era "la de menor tope **que alcance la misma recuperación
  máxima**", ninguna con tope la alcanza y el criterio no tiene salida útil: habría que
  decir "sin tope" o bajar el tope a la vez que se toca la regla de MB.
- `MB_sintope_STno` es además **la más barata de las que recuperan ≥25 filas**
  (5451 s frente a 6463 s de `t15`), así que es la opción por defecto aunque el criterio
  se lea de otra forma.

**Hallazgo lateral: la salida temprana (ST) está muerta en estas 40 filas.**
`st_disparo` = 0 en las dos configuraciones sin tope. ST sí y ST no dan **resultados
idénticos** (mismas 27 filas, `max|Δη| = 0`, `nF` idénticos); los 183 s de diferencia son
ruido de reloj con 6 workers.

### 5.2 A3 — la "discrepancia" de las filas sanas (explicada)

> *MB_t6_STno "reproduce a M0 en 29/30 filas sanas (1 discrepancia)". Identificar la fila y explicar.*

La discrepancia es **`barrido_literatura_kcs11` #14**, y **no es una discrepancia de
resultado: es un rescate**.

| | M0 | MB_t6_STno |
|---|---|---|
| `convergio` | **False** | **True** |
| `causa` | `PropertyRangeError` | — |
| `clasificacion` | NO_CONVERGIO | CORREGIBLE *(igual que `clasificacion_original`)* |
| `eta` | — | 0.176485 |
| `eta_original` (barrido histórico) | 0.176485 | 0.176485 |
| `T1_sol` | — | 368.5274 K |
| `nF` | 1 | 10 |
| `t_s` | 3.74 s | 41.96 s |
| `punto_cascada` | `valv.T7` | `valv.T7` |

En las **29 filas que M0 resuelve**, MB es **idéntico a M0**: `max|Δη| = 0`,
`max|ΔT1_sol| = 0`, `nF` distintos en **0** filas, `reintento_usado` en **0** filas. Es
justo lo que debe pasar, porque MB corre M0 primero.

En la fila #14, M0 muere en la **primera** evaluación del bracket (`nF = 1`,
`fase_fallo = bracket`) con
`T_from_Ph`: *"equilibrio no resoluble en T=263.16 K, P=2.7355e+05 Pa, x=0"* — un estado
que el motor `teqp` no cubre. El primer intento de MB reproduce ese mismo error
(`msg_intento1` idéntico) y el reintento en caliente **sí converge**, con
`|η(MB) − η_original| = 0.000e+00`. Es decir: MB no se contradice, **hereda el valor del
barrido original con todas las cifras**.

### 5.3 Por qué MB pierde la fila `barrido_literatura_kcs11` #20 (y no es un bug del bracket)

En la ablación, esa fila la rescata **V2** (`nF` 9, `η` 0.064908) pero **no** la variante
VB (solo bracket, sin arranque en caliente: `PuntoNoEvaluable`). Es una de las 2 filas
(`f5`, `f20`) que **solo** el arranque en caliente salva.

En MB, esa fila queda así:

```
causa = PropertyRangeError · nF = 4 · fase_fallo = brentq
reintento_usado = False · nF_intento1 = 0 · t_intento1_s = 0.0
```

`reintento_usado = False` significa que `_correr` nunca llegó a probar el reintento. La regla de MB es
`if c["fase"] != "bracket": raise` — solo reintenta si el fallo aflora durante el
bracketeo. Aquí el error aflora ya en `brentq`, así que MB se rinde. V2 no tiene esa
condición: entra directamente con `T10 = T_sumidero + 5 K`, toda la cascada es otra, y el
punto problemático sí se evalúa.

**Consecuencia de fondo:** la regla "MB reintenta solo si falla en el *bracketeo*" tiene
un punto ciego. Ese mismo punto ciego reaparece en el mini-barrido (§5.4:
`barrido_literatura_kcs11` #28, la única de las 75 sanas que MA resuelve y MB no).

### 5.4 B2 — los 93 puntos del mini-barrido

| Modo | Origen | Resuelve | NO_CONVERGIO | CPU total (s) | CPU mediana (s) | **Pared (s)** |
|---|---|---:|---:|---:|---:|---:|
| M0 | reutilizado | 73/93 | 20 | 3873.72 | 38.10 | **658** |
| MA (= V2) | reutilizado | 81/93 | 12 | 4343.21 | 40.80 | **740** |
| MB_t6_STsi *(descartado)* | reutilizado | 80/93 | 13 | 4391.77 | — | 746 |
| **MB_sintope_STno** | **medido aquí** | **84/93** | **9** | 7598.65 | 69.86 | **1281** |

> **De dónde sale cada fila (importante al comparar ficheros).**
> `benchmark_minibarrido_mb_corregido.csv` contiene **solo 3 modos** (M0, MA, MB_sintope_STno
> = 3 × 93 = 279 filas). La fila `MB_t6_STsi` **no está en ese CSV**: son sus números del
> fichero anterior `benchmark_minibarrido.csv` (279 filas, también en este mismo directorio),
> y su tiempo de pared (746 s) del `progreso.log` de aquella corrida. Se incluye aquí solo
> como referencia del modo que A4 descartó.
> Los tiempos de pared de M0 (658 s) y MA (740 s) son los de aquella corrida
> (`progreso.log`: "PARTE B M0: fin — 93 filas en 658 s", "PARTE B MA: … 740 s"); solo el
> de MB_sintope_STno (1281 s) es de esta corrida.

**MB corregido es el que más resuelve (84/93) y el que más cuesta (1.95× la CPU de MA,
1.73× su pared).** Los tiempos de pared de M0 y MA son los de la corrida original
(`progreso.log`: 658 s y 740 s); el de MB es de esta corrida.

**Fracción de puntos `NO_CONVERGIO` original: 57/279 = 20.4 %** (19 de los 93 puntos ya
venían marcados `NO_CONVERGIO` en su barrido histórico: 60 CORREGIBLE, 14 KALINA,
19 NO_CONVERGIO). Los tres modos de este cuadro resuelven entre el 78 % y el 90 %.

Por grupo (agrupando `ctl_*` dentro de `sana`, ver §8):

| Grupo | Puntos | M0 | MA | MB_sintope_STno |
|---|---:|---:|---:|---:|
| sana (+ ctl) | 75 | 73 | 75 | 74 |
| lit_T_from_Ph | 6 | 0 | 4 | **6** |
| lit_bifasico | 3 | 0 | 0 | **1** |
| f2_T_from_Ph | 7 | 0 | 2 | **3** |
| f2_h_Ps | 2 | 0 | 0 | 0 |
| **Total** | **93** | **73** | **81** | **84** |

- MB resuelve **11** filas que M0 no, y **4** que MA no. **Ninguna** que M0 resuelva y MB
  no (`[]`): MB contiene a M0, como debe ser.
- El único punto donde MB pierde contra MA es `barrido_literatura_kcs11` #28, **el mismo
  punto ciego de §5.3** (`fase_fallo = brentq`, `reintento_usado = False`).
- `f2_h_Ps` (2 puntos) no lo resuelve **ningún** modo.

**Verificación de turbina.** Las 14 filas `KALINA` del mini-barrido llevan
`B_verificado` calculado (`verificar_turbina` + `AmmoniaWaterAdapter`): 13 `True` y
**1 `False`** —`busqueda_libre_v2` #944, con `B_dh4s = −2.2284 kJ/kg`. **Los tres modos
dan exactamente el mismo resultado ahí** (`η = 0.011784`, `T1_sol = 366.7 K`,
`B_verificado = False`) y coincide con `eta_original`, así que es una propiedad del punto
de diseño, no un artefacto del modo. En A2 **no salió ninguna fila KALINA** (91 CORREGIBLE,
69 NO_CONVERGIO), luego no hay nada que verificar con motor real en esa parte.

### 5.5 Parte C — cuánto costaría cada modo en cada barrido histórico

Costes por tipo de fila, **todos medidos** (no inventados):

| Coste | Valor | De dónde sale |
|---|---:|---|
| Fila sana en M0 (y en MB: corre M0 primero) | 45.72 s | 29 de las 30 filas sanas que M0 resuelve |
| Fila sana en MA (= V2) | 46.31 s | Ablación, las 16 filas que V0 resuelve |
| Fila que **no** se resuelve, en M0 | 7.84 s | Las 40 filas de A1 |
| Fila que **no** se resuelve, en MB_sintope_STno | 170.00 s | Las 13 de las 40 que MB sigue sin resolver |
| Fila que **no** se resuelve, en MA (= V2) | 84.03 s | Ablación, las 40 que V0 no resuelve |

Modelo aplicado (explícito en el CSV): con `s` filas convergentes y `f` filas
`NO_CONVERGIO` según el propio CSV del barrido,
`t_M0 = s·45.72 + f·7.84`, `t_MB = s·45.72 + f·170.00`, `t_MA = s·46.31 + f·84.03`.

**Tiempo de pared extrapolado (min, 6 workers):**

| Barrido | Filas | NO_CONVERGIO | M0 | MA (= V2) | MB (sintope) | Tiempo real conocido |
|---|---:|---:|---:|---:|---:|---|
| busqueda_libre_v2 | 1591 | 302 | 170.3 | 236.3 | 306.3 | sin dato registrado |
| ronda6_diagnostico | 646 | 206 | 60.4 | 104.7 | 153.2 | sin dato registrado |
| ronda5_diagnostico | 148 | 81 | 10.3 | 27.5 | 46.8 | sin dato registrado |
| barrido_xb_industria | 117 | 43 | 10.3 | 19.6 | 29.7 | **≈ 65 min** (≈ 10.8 min de la extrapolación M0) |
| barrido_literatura_kcs11 | 60 | 28 | 4.7 | 10.6 | 17.3 | sin dato registrado |
| barrido_margen2k | 30 | 8 | 3.0 | 4.7 | 6.6 | **8369 s** (extrapolación M0: 3.0 min) |
| barrido_pinch6_realista | 30 | 7 | 3.1 | 4.6 | 6.2 | **1797 s** (extrapolación M0: 3.1 min) |

**Medido vs extrapolado, sin mezcla:** los conteos de filas y `NO_CONVERGIO` son
**medidos** (propio CSV de cada barrido); los costes por tipo de fila son **medidos**
(muestra de 40 + 30 filas y ablación de 56); **el tiempo de cada barrido con estos modos
es extrapolación** — ninguno de los 7 barridos se ejecutó con MB. En
`extrapolacion_barridos.csv` cada fila lleva `origen_coste_sana`, `origen_coste_falla` y
`filas_y_no_convergio` para que no se puedan confundir.

Los tres barridos con tiempo real conocido **discrepan fuerte de la extrapolación**:
`margen2k` tardó 8369 s de verdad contra 3.0 min extrapolados con M0 (46×), y
`pinch6_realista` 1797 s contra 3.1 min (19×). O los tiempos reales incluyen trabajo que
no es resolver filas (malla completa, E/S de disco, evaluations, etc.), o el coste por fila de la muestra no
representa a esos barridos. `xb_industria` sí coincide en orden de magnitud (≈ 65 min
real vs 10.3 min extrapolados con M0, 6×). La extrapolación **no** debe usarse como
presupuesto.

---

## 6. El incidente: qué pasó y qué se hizo

1. **La corrida anterior fue cortada** por el límite de tiempo del comando del agente, a
   mitad de A2. Los 6 procesos de Python de A2 quedaron **huérfanos** y siguieron
   escribiendo en `resultados/2026-10-01_benchmark_reintento/`.
2. **A2 falló y no dejó datos.** A las 18:12 los huérfanos terminaron con
   **`RecursionError`** y **`benchmark_filas_topes.csv` no existía**: se perdieron ~35 min
   de CPU de 6 workers. Causa: en `benchmark_cierre_modos.py`, `medir()` parchea
   `BM.cfg_nombre = cfg_nombre` (los parches se aplican **dentro de cada worker**, porque
   en Windows el `spawn` no los hereda), pero `cfg_nombre` llamaba a `BM.cfg_nombre(...)`:
   desde el parche, la función se llamaba a sí misma. El piloto previo no lo detectó
   porque no pasó por el camino con el parche dentro de un worker.
3. **El arreglo** (mínimo, en `scripts/benchmark_cierre_modos.py`): guardar
   `_CFG_NOMBRE_ORIG = BM.cfg_nombre` **antes** del parche y llamar a esa referencia, igual
   que ya se hacía con `_BRACKET_TOPE = BM._bracket_tope`. Se buscó una segunda referencia
   circular análoga en `benchmark_cierre_topes.py`: **no la hay** (su `cfg_nombre` es el
   nombre importado del módulo de modos, y nunca parchea `BM`).
4. **Humo por el camino real**: antes de lanzar nada, 2 filas × 4 configuraciones = 8
   mediciones con el mismo `pool`/`medir`/parche y **dentro de un worker de
   `ProcessPoolExecutor`**. Resultado: **8 filas, 0 excepciones**, 640 s.
5. **A2 incremental y reanudable**: cada fila se añade al CSV con `flush`+`fsync` en el
   momento en que termina, y se anota una línea en `progreso_cierre.log`. Si el CSV ya
   tiene esa `(config, csv_origen, fila_csv)`, se omite. Una excepción en una fila se
   escribe **como una fila más** (`convergio=False`, `causa`, `msg`) y no aborta nada.
6. **El CSV de 160 filas quedó verificado**: 160 filas, **160 claves únicas**
   (`config|csv_origen|fila_csv`), **40 columnas** exactamente como
   `benchmark_filas.csv`, **0 filas con `RecursionError`**, 0 excepciones de worker.
   Los conteos por configuración cuadran (40 cada una) y suman 240 en la tabla de A4.
7. **Un defecto encontrado y corregido sobre la marcha**: el encabezado del CSV lo fijaba
   la primera fila, y como esa fila no era KALINA no traía `B_verificado`/`B_dh4s` —las
   columnas se habrían perdido en las filas KALINA. El esquema se fijó a las 40 columnas
   de `benchmark_filas.csv` y el CSV existente se normalizó (solo añadiendo las dos
   columnas vacías; 8 filas del humo, todas `NO_CONVERGIO`, ninguna KALINA, luego no se
   perdió ningún dato).

---

## 7. Tiempos

| Fase | Mediciones | Pared (s) | Pared (min) |
|---|---:|---:|---:|
| Humo (2 filas × 4 configs) | 8 | 640 | 10.7 |
| A2 (las 152 restantes) | 152 | 3268 | 54.5 |
| B2 (93 puntos, MB corregido) | 93 | 1281 | 21.4 |
| **Total de cómputo** | **253** | **5189** | **86.5** |
| Control V2 + A3 + A4 + Parte C | — | < 10 | < 0.2 |

**No hubo que reducir ninguna parte**: 86.5 min de reloj de pared quedan por debajo del
~100 min del enunciado. Todas las corridas largas se lanzaron desacopladas
(`nohup`) y se siguieron con consultas cortas; el progreso se puede seguir en vivo en
`resultados/2026-10-01_benchmark_reintento/progreso_cierre.log`.

**CPU consumida** (suma de `t_s` de las filas medidas): A2 **21.7 ks** en 3908 s de pared
(humo + A2) = **5.55×**; B2 **7.6 ks** en 1281 s = **5.93×**; total **29.3 ks** en
5189 s = **5.64×**. Los 6 workers están casi saturados: el límite ya no es paralelismo
sino el número de filas caras (la más cara de A2, `barrido_literatura_kcs11` #49 en
`MB_t15_STno`, se tardó **837.91 s** de CPU ella sola y por sí sola fija elMakespan del
lote). Subir workers más allá de 6 no acortaría esto de forma apreciable.

---

## 8. Conclusión

1. **El error de los topes era real y grave**: "tope 6" no era V2. Con la corrección,
   el tope sí importa y mucho: 3, 4, 11, 16, 25 y 27 filas recuperadas para topes
   2, 3, 6, 10, 15 y sin tope. **Cuanto más alto el tope, más filas, más CPU.**
2. **Sin tope es lo que hay que usar** para no dejar filas en la mesa: recupera 27/40 de
   las que M0 no resuelve, y en las 27 comunes reproduce V2 con `Δη = 0` exactos.
3. **Recuperar filas cuesta tiempo, y bastante**: una fila que MB no resuelve cuesta
   **170 s** de CPU frente a los **7.8 s** que cuesta cuando M0 se rinde pronto. MB es
   ~1.7× más lento que MA en el mini-barrido a cambio de **3 filas más** (84 vs 81 de 93).
   Si el objetivo es terminar el barrido rápido y se puede perder 3 de 93 puntos,
   **MA gana**; si el objetivo es no dejar nada sin clasificar, **MB gana**.
4. **La salida temprana (ST) no hace nada aquí**: 0 disparos en 160 mediciones, resultados
   idénticos. Es código inerte en el rango de barridos medido.
5. **Hay un punto ciego conocido en la regla de MB**: reintenta solo si el fallo aflora en
   el bracketeo. Las filas que fallan en `brentq` nunca se reintentan (2 casos medidos:
   `barrido_literatura_kcs11` #20 y #28). Es la causa de que MB recupere 27 y no 28.

---

## 9. Lo que no sabemos

- **Por qué exactamente brentq falla en `barrido_literatura_kcs11` #20** y #28: se sabe
  que el error aflora en `brentq` (`fase_fallo`), con 4 evaluaciones, y que con arranque en
  caliente desde el principio sí converge; **no** se instrumentó qué punto interior de
  `brentq` lo lanza ni si es el extremo ya reevaluado. Es una inferencia a partir de
  `fase_fallo`, no una medición.
- **Qué ingrediente de V2 salva esa fila**: la ablazión demuestra que el bracket solo (VB)
  no la salva y que el arranque en caliente sí, pero **esa fila concreta no estaba en la
  muestra de la ablación** (`ctl_literatura` = filas 0, 17, 31, 45, 59), así que no se
  aisló con medición propia.
- **Si los tiempos son comparables entre corridas.** `MB_sintope_STsi` y
  `MB_sintope_STno` dan resultados **idénticos** y aun así sus totales de CPU difieren un
  3.5 % (5268.70 vs 5451.42 s). Con 6 workers sobre una máquina compartida, diferencias
  menores del ~5 % en `t_total_s` **no son significativas**. Por eso el desempate por
  "menor tiempo total" de A4 es frágil (aunque aquí no decidía nada: solo había una
  candidata).
- **Si la extrapolación de la Parte C sirve de presupuesto.** Los tres barridos con tiempo
  real conocido la contradicen por factores de 6 a 46 (§5.5).
- **Qué pasa en barridos más grandes.** La muestra de A2 son 40 filas y la de B2, 93. Las
  filas caras (`lit_bifasico`, hasta 838 s de CPU) pueden dominar cualquier barrido real.
- **Si el comportamiento depende de la máquina.** Todo se midió en una sola máquina, con 6
  workers, en una sola corrida por configuración.

---

## 10. Qué sigue

1. **Decidir qué hacer con la regla de MB** (§8.5): hoy tiene un punto ciego en `brentq`.
   Cambiarlo es tocar `src/`, luego **queda a decisión del director**. Con los datos de
   aquí: relaxing la condición de reintento subiría 27→28 en A2 y 84→85 en B2, a costa de
   más CPU en las filas que hoy se rinden pronto.
2. **Decidir MB vs MA** con el criterio de negocio, no con el de recuperación: MB gana
   3 filas de 93 y cuesta 1.7× más (§8.3).
3. **Revisar si ST se queda o se va.** 0 disparos en 160 mediciones: o se quita, o se
   documenta que solo aplica a rangos fuera de lo medido.
4. **Si el tiempo importa, atacar las filas caras, no los workers** (§7): los 6 workers
   ya rinden al 5.6×, así que la palanca es reducir el coste de las filas que se rinden
   tardíamente (hasta 838 s de CPU cada una), no añadir procesos.
5. **Arreglar la etiqueta `grupo`** en `benchmark_minibarrido_mb_corregido.csv` (§11): las
   filas reutilizadas traen `sana` donde las nuevas traen `ctl_literatura` /
   `ctl_KALINA_f2`, así que la comparación por grupo no es directa sin plegar.
6. **Antes de usar la Parte C como presupuesto**, calibrar `t_s` por fila contra un
   barrido real completo (por ejemplo `barrido_margen2k`, donde se conocen los 8369 s).

---

## 11. Defectos de datos encontrados (no corregidos en la evidencia)

| # | Qué | Dónde | Efecto |
|---|---|---|---|
| 1 | La columna `grupo` no es comparable entre filas reutilizadas y nuevas: `benchmark_minibarrido.csv` solo usa 5 etiquetas (`sana`, `lit_*`, `f2_*`) mientras las filas medidas por `P.muestra()` usan `ctl_literatura` / `ctl_KALINA_f2`. | `benchmark_minibarrido_mb_corregido.csv` | Las tablas por grupo hay que plegar `ctl_*` dentro de `sana` (75 puntos). Los 7 puntos afectados se identificaron y son consistentes en las dos etiquetas. |
| 2 | `progreso_cierre.log` mezcla tres scripting distintos (corrida huérfana de 17:42, esta de 18:17 en adelante) sin separador de intento más que la línea `===`. | `progreso_cierre.log` | Cosmético; las líneas llevan etiqueta (`A2`, `A2humo`, `B2`). |
| 3 | `benchmark_cierre_topes.py::pool` sigue sin ser incremental (acumula en memoria y escribe al final). No se usó en esta tarea para medir. | `scripts/benchmark_cierre_topes.py` | Si alguien lo vuelve a usar para A2, pierde el trabajo ante un fallo. La versión incremental es `benchmark_cierre_a2.py`. |

---

## 12. Ficheros

**Nuevos, en `resultados/2026-10-01_benchmark_reintento/`:**

| Fichero | Contenido |
|---|---|
| `benchmark_filas_topes.csv` | **160 filas** (40 × 4 configuraciones), 40 columnas. A2. |
| `benchmark_minibarrido_mb_corregido.csv` | **279 filas** (93 × M0/MA reutilizados + 93 × MB medido), 41 columnas (añade `origen`). B2. |
| `extrapolacion_barridos.csv` | **21 filas** (7 barridos × 3 modos), 18 columnas. Parte C. |
| `REPORTE_BENCHMARK.md` | Este informe. |
| `progreso_cierre.log` | Una línea por fila terminada, con `flush`. |
| `stdout_cierre_a2_humo.txt`, `stdout_cierre_a2.txt`, `stdout_cierre_b2.txt` | Salida de las tres corridas. |

**Scripts nuevos:** `scripts/benchmark_cierre_a2.py`, `scripts/benchmark_cierre_informe.py`,
`scripts/benchmark_extrapolacion_cierre.py`.

**Modificado:** `scripts/benchmark_cierre_modos.py` (solo el arreglo de la referencia
circular y su comentario).

**Sin tocar:** `src/`, `tests/`, `benchmark_filas.csv`, `benchmark_minibarrido.csv`,
`benchmark_cierre_topes.py`, `benchmark_modos.py`, `benchmark_extrapolacion.py`,
`sonda_arranque_solver.py`, `ablacion_filas.csv` y los CSV de los barridos.
