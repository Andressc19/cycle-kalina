# Ablación arranque vs. bracket, y de dónde viene el coste

**Tarea:** `2026-10-01-ablacion-arranque-y-tiempos` · **Fecha:** 2026-10-01
**Script:** `scripts/sonda_ablacion_tiempos.py` (187 líneas) · **Datos:** `ablacion_filas.csv` (56 filas × 103 columnas)
**Backend:** `TeqpVerificado` en las cinco variantes + `AmmoniaWaterAdapter` para la verificación B.
**Reproducir:** `.venv\Scripts\python -u scripts\sonda_ablacion_tiempos.py` (6 workers, **2204 s = 36.7 min de reloj de
pared**, muestra completa, sin reducción).

Todas las cifras de este informe se recalcularon desde `ablacion_filas.csv` después de la
corrida, no durante ella. Se comprobó celda a celda: los 6 grupos × 4 variantes de la tabla
de ablación con su suma `rescata + otra = unión`, los dos recuentos por estado de la tabla
de tiempos, la descomposición `Σt_s / ΣnF` de cada variante y de cada grupo, la tabla de
`f2_*` de la clasificación de las 12 no rescatadas, el `max abs(Δη)` de los controles y la
concordancia con el `sonda_filas.csv` previo (estado 56/56, `η` 0.0).

---

## 0. Qué se midió y cómo

**Columnas del CSV.** Para cada variante `v ∈ {V0, V1, V2, VB, V3}` (VC = V1):

| Métrica pedida | Columna en `ablacion_filas.csv` |
|---|---|
| `convergio` | `<v>` (`convergio` / `no_convergio` / `error_backend`), con `<v>_causa` y `<v>_msg` |
| `clasificacion` | `<v>_clas` |
| `eta` | `<v>_eta` (6 decimales) |
| `nF` | `<v>_nF` |
| `iter_lazo_frio_total` | `<v>_iter` |
| `t_s` | `<v>_t_s` |
| `t_por_F` | `<v>_t_por_F` (= `<v>_t_s` / `<v>_nF`) |
| — | `<v>_anom` (0 en toda la corrida), `<v>_Wnet`, `<v>_T1`, `<v>_B_verificado`, `<v>_B_dh4s` |

**Parámetros.** `scripts/sonda_ablacion_tiempos.py` importa `scripts/sonda_arranque_solver.py`
**sin modificarlo** y reutiliza su `muestra()` (las mismas 56 filas), su `Proxy`, sus tablas de
decodificación `PRE`/`COLD`, su `_bracket_tol` (V2) y sus parámetros por fila. Las cinco
variantes se diferencian solo en dos interruptores:

| Variante | `T10_inicial` en la 1.ª evaluación | Extremos del bracket | `F` ante `PropertyRangeError` |
|---|---|---|---|
| **V0** | `None` (frío, arranca en `T1_trial`) | `_bracketear` original (amplía 5 K **hacia fuera**) | propaga la excepción |
| **VC** (= V1) | `T_sumidero + 5 K` (tibio) | `_bracketear` original | propaga la excepción |
| **VB** | `None` (frío) | `_bracket_tol`: repliegue 5 K **hacia dentro** | `None` (`F_seguro`) |
| **V2** | `T_sumidero + 5 K` (tibio) | `_bracket_tol` | `None` (`F_seguro`) |
| **V3** | `T_sumidero + 5 K` (tibio) | `_bracket_bis`: repliegue **por bisección**, ≤ 6 intentos por extremo | `None` (`F_seguro`) |

VC **no es una variante independiente**: es la columna `V1` (sección 3). V0, V1 y V2 **sí se
volvieron a medir aquí**, porque el CSV previo solo traía `nF` e iteraciones del *primer*
fallo de V0, no los totales por variante. La repetición no cambia nada: reproduce el CSV
previo con estado 56/56 y `|Δη| = 0` (§8, punto 3).

**V3, geometría del repliegue.** Extremo `lo = T_sumidero + 1 K`, `hi = T_fuente − 1 K`. Si
`F(lo)` no evalúa, se prueban `lo + d/2^k` con `k = 1…6` (el punto medio es el primer
intento) y `d = hi − lo`; después, para `hi`, `hi − d'/2^k` con `d' = hi − lo_final`, es
decir con `lo_final` (el extremo opuesto ya refinado) como referencia. Con **6 intentos** la
búsqueda alcanza solo `d/64` desde el extremo: **1.4–3.1 K** en los rangos de este estudio.
El paso fijo de 5 K de `_bracket_tol` (V2/VB) llega a **33–39 K**, pero **sin tope de
intentos**: necesita hasta 33–39 evaluaciones por extremo para llegar ahí. Esa asimetría
—misma distancia alcanzable, 6 intentos frente a ~35— es la causa de que V3 pierda 4 filas
(§2.2).

**Contadores.** `nF` = evaluaciones de `F` (una por llamada, incluidas las que `brentq`
repite en los extremos y la evaluación final). `iter` = suma de iteraciones del lazo frío
en todas las evaluaciones, **contadas por la traza del `Proxy`**: 13 llamadas `PRE` + 15 por
iteración + 1 de cierre (`divmod` con resto 0 en las 2509 evaluaciones de `F` de la corrida;
el script cuenta los restos en `<var>_anom` y la corrida salió en **0**). En las evaluaciones
que fallan, la iteración se toma de `decodificar(...)`, igual que en la sonda previa.
`t_por_F = t_s / nF`.

## 1. Conclusión

**El bracket tolerante es el cambio que ayuda. El arranque tibio aporta 2 filas que el
bracket, por sí solo, no recupera — y ni una iteración menos.**

- **VB (solo bracket) rescata 26 de las 40** filas que V0 no resuelve; **VC (solo arranque)
  rescata 3**, de las cuales 2 (`lit_T_from_Ph` f5, f20) no las rescata VB y 1 (f35) sí.
- **V2 = VB + esas 2 filas**: V2 rescata 28 y su conjunto es exactamente `VB ∪ {f5, f20}`
  (verificado fila a fila: `V2 \ VB = {lit_T_from_Ph f5, f20}`, `VB \ V2 = ∅`).
- Ninguna de las cuatro variantes rescata una fila que no rescate alguna de las otras tres
  (`solo_* = 0` en toda la tabla §2): el rescate está **anidado** (VB ⊂ V2, V1 ⊂ V2,
  V3 ⊂ V2). Las "2 filas del arranque" son exclusivas **respecto de VB**, no del conjunto.
- El arranque **no acelera el lazo frío**: en las 16 filas donde V0 y V1 convergen, `nF` es
  idéntico en 16/16 y `iter` solo baja en 2 filas, y en **1 sola iteración**.
- **V3 (bisección) no cumple el objetivo**: rescata 24 frente a 28 de V2 (−4), con `nF` un
  38 % menor. Menos coste, peor cobertura: **el objetivo de esta tarea no se logra con 6
  intentos de bisección**.

## 2. Tabla de ablación (40 filas que V0 no resuelve)

`rescata`: la variante converge. `otra_v`: **no** converge esa variante, pero alguna de las
otras tres sí. `NINGUNA`: no converge ninguna. `unión`: converge alguna de las cuatro
(independiente de la columna en la que se esté mirando).

Comprobación de sumas (`assert`, recalculada del CSV): para cada variante y cada grupo,
`rescata + otra_v = unión`; y `solo_v` (rescata y ninguna otra) = **0 en todas las celdas**,
es decir, ninguna variante rescata algo que las otras tres no cubran.

| Grupo (columna `grupo` del CSV) | Filas | VC | otra_VC | VB | otra_VB | V2 | otra_V2 | V3 | otra_V3 | NINGUNA | unión |
|---|---|---|---|---|---|---|---|---|---|---|---|
| FASE2 `T_from_Ph` (`f2_T_from_Ph`) | 15 | 0 | 11 | 11 | 0 | 11 | 0 | 10 | 1 | 4 | 11 |
| FASE2 `h(P, s, x)` (`f2_h_Ps`) | 5 | 0 | 1 | 1 | 0 | 1 | 0 | 0 | 1 | 4 | 1 |
| Literatura `T_from_Ph` | 13 | 3 | 10 | 11 | 2 | 13 | 0 | 13 | 0 | 0 | 13 |
| Literatura bifásico | 7 | 0 | 3 | 3 | 0 | 3 | 0 | 1 | 2 | 4 | 3 |
| **Total** | **40** | **3** | **25** | **26** | **2** | **28** | **0** | **24** | **4** | **12** | **28** |

**Lectura de la tabla.** `otra_*` no es un logro de la variante: es lo que se le escapa por
poco. `otra_VC = 25` significa que VB (o V2/V3) rescata 25 filas que VC no toca;
`otra_V2 = 0` significa que **V2 no deja nada sin rescatar que alguna otra variante recupere**
(es el conjunto más grande). Los 12 de `NINGUNA` son los mismos para las cuatro variantes y
también los mismos en V0 (§7).

### 2.1. ¿El arranque aporta algo por sí mismo, algo solo en combinación, o nada?

Cruzamiento `VC × VB` sobre las 40 filas (no exhaustivo: hay 2 filas que VB no rescata y
V2/V3 sí):

| | VB converge | VB no converge |
|---|---|---|
| **VC converge** | 1 (`lit_T_from_Ph` f35) | **2** (`lit_T_from_Ph` f5, f20) |
| **VC no converge** | 25 | 12 |

- **Por sí solo: 2 de 40 (5 %).** `lit_T_from_Ph` f5 (η = 0.075082) y f20 (η = 0.064908),
  ambas `CORREGIBLE`. Son filas en las que el bracket original evalúa un extremo que con
  `T10_inicial = T_sumidero + 5 K` sí cae dentro del dominio del backend, y con `None` no.
- **Solo en combinación: 1 de 40.** f35, que el bracket tolerante ya rescata sin warm start.
- **Nada: en las otras 37** el warm start no cambia nada.

**Conclusión explícita:** el arranque aporta **2 filas por sí solo (5 % de la muestra)**, y
nada en combinación — porque V2 = VB + esas 2, sin sinergia ninguna: **V2 = VB ∪ {f5, f20}**
(comprobado: `VB \ V2 = ∅`). El bracket tolerante hace **26 de las 28** filas que rescata V2
(93 %), 25 de ellas sin ninguna ayuda del warm start.

### 2.2. Por qué V3 pierde 4 filas frente a V2/VB

Las 4 son `lit_bifasico` f25, f40, `f2_T_from_Ph` f1251 y `f2_h_Ps` f1411. En las cuatro, V3
agota los 6 intentos de bisección (o encuentra extremo sin cambio de signo) con `nF` = 3–9
frente a 14–35 de V2:

| Fila | Rango de T1 del bracket (`[Ts+1, Tf−1]`) | Alcanza V3 en 6 intentos | Alcanza V2 con su paso de 5 K (sin tope de intentos) | `nF` V2 → V3 | Causa en V3 |
|---|---|---|---|---|---|
| `lit_bifasico` f25 | [284.0, 462.0] K (d = 178.0) | `d/64` = 2.78 K | 178 K en ≤ 35 intentos | 22 → 9 | `NoBracket`: `extremo_hi` sin evaluar |
| `lit_bifasico` f40 | [284.0, 462.0] K (d = 178.0) | `d/64` = 2.78 K | 178 K en ≤ 35 intentos | 23 → 9 | `NoBracket`: `extremo_hi` sin evaluar |
| `f2_T_from_Ph` f1251 | [301.0, 469.0] K (d = 168.0) | `d/64` = 2.62 K | 168 K en ≤ 33 intentos | 14 → 3 | `NoBracket`: sin cambio de signo |
| `f2_h_Ps` f1411 | [301.0, 499.0] K (d = 198.0) | `d/64` = 3.09 K | 198 K en ≤ 39 intentos | 35 → 9 | `NoBracket`: `extremo_hi` sin evaluar |

La geometría lo explica sin más: 6 intentos de bisección barren solo `d/64`, el **1.6 %**
del rango; el paso fijo de 5 K de `_bracket_tol` recorre hasta el rango entero, pero
necesita **33–39 intentos** por extremo. V3 no gasta 5–7 veces más `F` que V2 en esas filas
al contrario: gasta 3–9 frente a 14–35, y aun así pierde las 4, porque **se rinde antes de
llegar al punto evaluable**. A cambio, V3 no pierde ninguna fila que V2 no tenga en común:
`V2 ∩ V3 = 24`, `V3 \ V2 = ∅` (dentro de las 40). Es decir, **V3 es un subconjunto estricto
de V2** (pierde 4, no gana ninguna).

## 3. Tiempos: media, mediana y p90 por variante (56 filas, misma carga)

Las cinco variantes se ejecutaron **secuencialmente dentro de la misma tarea de worker**, así
que los `t_s` son comparables entre variantes. `t_por_F` se calculó en el script con el `t_s`
sin redondear (el CSV guarda `t_s` con 1 decimal y `t_por_F` con 3, así que al recalcular
`t_s / nF` desde el CSV aparecen diferencias de hasta 0.05 s, que son solo de redondeo).

| Variante | `t_s` media | `t_s` med | `t_s` p90 | `nF` media | `nF` med | `nF` p90 | `iter` media | `iter` med | `iter` p90 | `t_por_F` media | `t_por_F` med | `t_por_F` p90 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V0 | 20.40 | 9.85 | 56.70 | 4.07 | 2.0 | 9.0 | 10.09 | 4.5 | 25.5 | 4.216 | 4.372 | 7.244 |
| VC (=V1) | 21.27 | 9.90 | 55.85 | 4.39 | 2.0 | 9.0 | 10.73 | 5.0 | 25.5 | 4.134 | 4.367 | 6.933 |
| V2 | 73.25 | 56.40 | 106.25 | 13.96 | 13.5 | 22.0 | 23.61 | 24.0 | 31.0 | 5.260 | 4.325 | 7.225 |
| VB | 70.56 | 55.25 | 113.00 | 13.79 | 13.5 | 21.5 | 23.39 | 24.0 | 31.0 | 5.131 | 4.359 | 7.246 |
| V3 | 42.26 | 41.60 | 61.80 | 8.59 | 9.0 | 10.0 | 18.34 | 20.0 | 26.5 | 4.976 | 4.633 | 6.866 |

### 3.1. Por estado (convergidas / no convergidas)

| Variante | Estado | n | `t_s` media | `t_s` med | `t_s` p90 | `nF` media | `nF` med | `iter` media | `iter` med | `t_por_F` media | `t_por_F` p90 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| V0 | converge | 16 | 49.68 | 48.95 | 67.60 | 9.12 | 9.0 | 23.75 | 23.5 | 5.45 | 7.51 |
| V0 | NO converge | 40 | 8.69 | 8.70 | 19.88 | 2.05 | 2.0 | 4.62 | 4.0 | 3.72 | 6.02 |
| VC | converge | 19 | 46.59 | 43.20 | 62.34 | 9.11 | 9.0 | 23.00 | 21.0 | 5.12 | 6.93 |
| VC | NO converge | 37 | 8.26 | 8.30 | 16.50 | 1.97 | 2.0 | 4.43 | 4.0 | 3.63 | 6.46 |
| V2 | converge | 44 | 60.30 | 58.20 | 89.92 | 14.05 | 12.0 | 25.91 | 26.0 | 4.53 | 6.49 |
| V2 | NO converge | 12 | 120.75 | 52.10 | 289.79 | 13.67 | 16.5 | 15.17 | 16.0 | 7.92 | 15.25 |
| VB | converge | 42 | 61.41 | 57.40 | 92.41 | 14.26 | 12.5 | 26.31 | 26.0 | 4.53 | 6.53 |
| VB | NO converge | 14 | 97.99 | 42.15 | 257.25 | 12.36 | 14.5 | 14.64 | 15.5 | 6.95 | 13.54 |
| V3 | converge | 40 | 49.08 | 45.80 | 64.79 | 9.68 | 10.0 | 22.35 | 21.0 | 5.06 | 6.81 |
| V3 | NO converge | 16 | 25.20 | 24.95 | 36.80 | 5.88 | 6.0 | 8.31 | 6.0 | 4.77 | 6.64 |

### 3.2. ¿De dónde viene el sobrecoste de V2?

**De más evaluaciones de `F`, no de iteraciones ni de evaluaciones caras** — con una
excepción importante en las filas bifásicas.

Descomposición `t_s = nF × coste_por_evaluación` con coste agregado `Σt_s / ΣnF` sobre las
56 filas (el CSV guarda `t_s` redondeado a 0.1 s y `t_por_F` a 3 decimales, así que la
columna `t_por_F` no se puede recalcular exactamente desde `t_s`; las sumas y medianas de
esta sección salen de los valores tal como están guardados):

| Variante | Σ`t_s` (s) | Σ`nF` | coste agregado por eval (s) | `t_s` vs V0 | `nF` vs V0 | coste/eval vs V0 | reparto del sobrecoste |
|---|---|---|---|---|---|---|---|
| V0 | 1142.4 | 228 | 5.01 | 1.00× | 1.00× | 1.00× | — |
| VC | 1190.9 | 246 | 4.84 | 1.04× | 1.08× | 0.97× | ruido |
| **V2** | 4102.0 | 782 | 5.25 | **3.59×** | **3.43×** | 1.05× | **94 % `nF`, 6 % coste/eval** |
| VB | 3951.1 | 772 | 5.12 | 3.46× | 3.39× | 1.02× | 97 % `nF`, 3 % coste/eval |
| V3 | 2366.4 | 481 | 4.92 | 2.07× | 2.11× | 0.98× | 104 % `nF`, −4 % coste/eval |

El reparto no sale de multiplicar los dos factores (eso daría 3.43 × 1.05 = 3.59 con un
reparto logarítmico, no lineal), sino de una descomposición **aditiva** del sobrecoste
`ΔΣt_s` sobre las 56 filas: se calcula qué parte del sobrecoste explican las `ΔnF`
evaluaciones adicionales **al coste medio de V0** (5.011 s/eval), y el resto es lo que sube
el coste por evaluación. Para V2: `ΔΣt_s` = 2959.6 s, `ΔΣnF` = 554 → 2775.8 s (93.8 %) por
más evaluaciones, y 183.8 s (6.2 %) por evaluaciones más caras.

- **Más evaluaciones de `F`: sí, es la causa.** `nF` multiplica por 3.43 (mediana 2 → 13.5;
  p90 9 → 22). Cada extremo del bracket que no evalúa se reintenta, y cada reintento es una
  cascada completa.
- **Más iteraciones por evaluación: no.** `iter/nF` **cae** al usar el bracket tolerante
  (V0 2.48, VC 2.44, VB 1.70, V2 1.69, V3 2.14): las evaluaciones de sondeo mueren pronto
  (muchas en la fase `PRE`, con 0 iteraciones), así que el número de iteraciones **totales**
sube mucho menos que `nF` (565 → 1322, 2.34×) y `iter` por fila convergida se queda
   prácticamente igual (mediana 23.5 → 26).
- **Evaluaciones individualmente más caras: casi no, salvo en `lit_bifasico`.** El coste
  agregado por evaluación varía entre 4.84 y 5.25 s (≤ 5 %), pero **por grupo** sí hay una
  cola pesada:

| Grupo | `Σt_s` V0 → V2 (s) | `ΣnF` V0 → V2 | coste agregado/eval V0 → V2 (s) | cuota del sobrecoste de V2 (2959.6 s) |
|---|---|---|---|---|
| FASE2 `T_from_Ph` | 183.7 → 1008.6 | 39 → 216 | 4.71 → 4.67 | 27.9 % |
| FASE2 `h(P, s, x)` | 33.6 → 301.8 | 7 → 93 | 4.80 → 3.25 | 9.1 % |
| Literatura `T_from_Ph` | 479.4 → 1096.1 | 81 → 242 | 5.92 → 4.53 | 20.8 % |
| **Literatura bifásico** | **19.9 → 1300.7** | **10 → 140** | **1.99 → 9.29** | **43.3 %** |
| `ctl_KALINA_f2` | 259.2 → 237.7 | 48 → 48 | 5.40 → 4.95 | −0.7 % |
| `ctl_literatura` | 166.6 → 157.1 | 43 → 43 | 3.87 → 3.65 | −0.3 % |
| **Total** | **1142.4 → 4102.0** | **228 → 782** | **5.01 → 5.25** | **100 %** |

  Las 7 filas `lit_bifasico` aportan el **43 % del sobrecoste total de V2 con solo el 12.5 %
  de las filas**. En ellas el coste por evaluación se multiplica por 4.7 (1.99 → 9.29 s).
  Causa medida (micro-sonda puntual sobre `lit_bifasico` f49, `P_alta = 5000 kPa`,
  `x_b = 0.70`; 19 evaluaciones de V2, 354 llamadas a propiedades): las 19 evaluaciones
  mueren en `sep.ELV = equilibrio_liquido_vapor`, y el tiempo se lo llevan dos llamadas
  lentísimas de teqp a 5 MPa — **`h(P, s, x)` ≈ 12 s por llamada** (16 llamadas, 191.8 s de
  los 278.9 s totales) y `sep.ELV` ≈ 6 s por llamada (41 llamadas, 252.5 s) — frente a
  ~150 ms de media por etiqueta en las filas sanas; `T_from_Ph` sube de ~140 ms a ~920 ms.
  Es decir: en esas filas hay evaluaciones *más caras*, y ahí está el 43 % del gasto. La
  lentitud viene de que el backend está en la frontera de la campana binaria, no del número
  de iteraciones. (Esta micro-sonda es una medición aparte, no sale del CSV; ver §8.7.)

**Respuesta:** el sobrecoste de V2 es sobre todo **más evaluaciones de `F` (94 %)**; el
contribuyente secundario es un grupo de filas donde **cada evaluación individual cuesta
varias veces más** (`h(P, s, x)` ≈ 12 s, `sep.ELV` ≈ 6 s). Las iteraciones por evaluación no
son la causa: bajan de 2.48 a 1.69.

## 4. Efecto del arranque en iteraciones (16 filas donde V0 y VC convergen)

| Métrica | V0 mediana | VC mediana | Δ mediana | Δ mínimo | Δ máximo | Pares idénticos |
|---|---|---|---|---|---|---|
| `nF` | 9.00 | 9.00 | +0.00 | 0 | 0 | **16/16** |
| `iter` | 23.50 | 23.50 | +0.00 | −1 | 0 | 14/16 (2 con −1) |
| `t_s` | 48.95 | 46.15 | **−1.90** | −7.9 | +2.5 | 0/16 |
| `t_por_F` | 4.96 | 4.75 | −0.19 | −0.9 | +0.3 | 0/16 |

**¿El arranque físico acelera? No apreciablemente.** `nF` es idéntico en las 16 filas: el
warm start cambia el punto de partida del lazo interior pero **no reduce el número de
evaluaciones de `F`** (el lazo exterior ya evalúa los mismos puntos). `iter` baja en
**1 iteración** en 2 de 16 filas y en ninguna sube. La mejora de `t_s` (−1.9 s de mediana,
VC más rápido en 14 de 16) es del orden del ruido entre repeticiones: no la acompaña ninguna
reducción de `nF` ni de `iter` que la justifique, así que **no debe atribuirse al arranque**.

En las filas donde las variantes coinciden en converger, el resultado físico es el mismo:
`|Δη|` máximo = **0.0** para V0/VC (16 pares), VB/V0 (16), V2/VC (19), V3/VC (19) y V2/VB
(42). Hay **una sola fila** en toda la corrida donde el par difiere: `lit_T_from_Ph` f3, entre
V3 y cada una de VB y V2, con `|Δη| = 1e-6` y `|ΔT1| = 1e-4` — exactamente **una unidad del
último decimal** con que el CSV guarda `η` (6 decimales) y `T1` (4 decimales), es decir, la
misma raíz redondeada a distinta precisión. Ninguna variante cambia el resultado físico donde
ambas convergen: el warm start y el bracket deciden *si* se converge, nunca *a qué*.

## 5. Controles (10 filas) y verificación B

Las 10 filas de control reproducen la clasificación y `η` del CSV original en **las cinco**
variantes:

| Grupo control | n | `clasificacion_original` | V0 / VC / V2 / VB / V3 | `max abs(Δη)` (5 variantes) |
|---|---|---|---|---|
| `ctl_KALINA_f2` | 5 | `KALINA` | `KALINA` ×5 | 4.67e-07 |
| `ctl_literatura` | 5 | `CORREGIBLE` | `CORREGIBLE` ×5 | 0.00e+00 |

`|Δη| < 1e-4` en las 10 filas y en las 5 variantes → **sin regresión**. El `4.67e-07` es
redondeo: `eta_original` viene del CSV previo con toda la coma flotante y `<v>_eta` se guarda
a 6 decimales, así que la diferencia solo puede ser el redondeo del CSV (≤ 5e-07). En
`ctl_literatura` la diferencia es exactamente 0.

**Verificación B (`verificar_turbina` + `AmmoniaWaterAdapter`), solo sobre las 5 filas
`KALINA`** (las únicas que salen `KALINA` en toda la muestra): `verificado = True` en las
cinco variantes, con `Δh4s` entre −1.1441 y −1.2495 kJ/kg, idéntico entre variantes
(es el mismo punto físico). Coherente con que esas 5 filas llevan `eta_t = 0.85`, y con que A
ya sustituye el `h4s` de teqp (`CONTEXT.md`, protección A+B).

**Las filas `CORREGIBLE` rescatadas NO se verifican con el motor real**, por requisito de
`CONTEXT.md` (B se aplica solo a `KALINA`). De las 28 filas rescatadas por V2, **27 salen
`CORREGIBLE` y 1 `NO_CONVERGIO`** (la única fila de la muestra que el backend clasifica así:
`lit_T_from_Ph` f3, `η` = −0.4496, `Wnet` = −30.82 kJ/kg — un punto de trabajo con trabajo
neto negativo, no un fallo numérico). VB: 25 `CORREGIBLE` + 1 `NO_CONVERGIO`. V3: 23
`CORREGIBLE` + 1 `NO_CONVERGIO`. Es decir, **de todo el rescate de esta tarea, ninguna fila
nueva se verificó con el motor real**: solo las 5 `KALINA` de control, que ya convergían con
V0.

## 6. Costo/beneficio (filas rescatadas por cada 1000 s de cómputo)

Sobre las 40 filas que V0 no resuelve (`Σt_s` de esas 40):

| Variante | Rescata | `Σt_s` (s) | absolutas (filas/1000 s) | base incremental | filas/1000 s adicionales |
|---|---|---|---|---|---|
| V0 | 0/40 | 348 | 0.00 | — | — |
| VC | 3/40 | 431 | 6.96 | vs V0: +3 filas por +83 s | 35.97 |
| **VB** | **26/40** | 3211 | 8.10 | vs V0: +26 filas por +2864 s | 9.08 |
| **V2** | **28/40** | 3361 | 8.33 | vs V0: +28 filas por +3013 s | 9.29 |
| **V3** | **24/40** | 1638 | **14.66** | vs V0: +24 filas por +1290 s | **18.60** |
| V3 (misma fila) | 24/40 | 1638 | 14.66 | vs VC: +21 filas por +1207 s | 17.40 |

Sobre las 56 filas completas: V0 14.01, VC 15.95, V2 10.73, VB 10.63, **V3 16.90** filas/1000 s.

**Ranking costo/beneficio incremental: VC (36) > V3 (19) > V2 (9.3) ≈ VB (9.1) filas por
1000 s.** El warm start es lo más rentable *por segundo invertido* porque casi no cuesta
nada, pero solo recupera 3 filas; el bracket tolerante recupera 26–28 por el triple de
tiempo. **Si el criterio es número de filas recuperadas, V2 (28) gana; si es filas por
segundo, gana V3 (24 por la mitad de tiempo), pero V3 es un subconjunto estricto de V2 y
pierde 4 filas.**

## 7. Filas no rescatadas por ninguna variante (12) — solo clasificación

Las 12 son las mismas para V0, VC, VB, V2 y V3 (`V2` y `V3` fallan en exactamente las
mismas 12). La causa se toma de **V2**, la variante más tolerante; los mensajes de V3 se dan
aparte donde difieren:

| Grupo | Fila CSV | `nF` V2 / V3 | Causa en V2 | Detalle |
|---|---|---|---|---|
| `lit_bifasico` | 4, 19, 34, 49 | 19 / 7 | `NoBracket` sin extremo evaluable | `sep.ELV` no resuelve en **ninguna** composición a `P_alta = 5000 kPa`, `T ≈ 360.16–360.34 K`: «no existe equilibrio bifásico para ninguna composición (T fuera de la campana binaria a esa P)». En V3 el mensaje es `extremo_lo sin evaluar en 6 intentos (T = 285.375 K)`: mismo problema, otra profundidad de sondeo. |
| `f2_T_from_Ph` | 8 | 5 / 5 | `PuntoNoEvaluable` | punto interior de `brentq` no evaluable (`T = 370.8961 K`, idéntico en V3); en V0 el fallo es en `valv.T7` tras 5 evaluaciones de `F` |
| `f2_T_from_Ph` | 853 | 14 / 6 | `PuntoNoEvaluable` | interior no evaluable (`T = 348.58 K` en V2, `348.45 K` en V3); en V0, `h = 69842.5` fuera de dominio a `P = 2.5e6 Pa`, `x = 0.8088` |
| `f2_T_from_Ph` | 997 | 5 / 5 | `PuntoNoEvaluable` | interior no evaluable (`T = 346.9964 K`, idéntico en V3); en V0, `h = −2.35e7` fuera de dominio a `P = 3.6e6 Pa`, `x = 0.8570` |
| `f2_T_from_Ph` | 1505 | 6 / 6 | `PuntoNoEvaluable` | interior no evaluable (`T = 351.8451 K`, idéntico en V3); en V0, `h = −5.83e8` fuera de dominio a `P = 4e6 Pa`, `x = 0.7604` |
| `f2_h_Ps` | 379 | 3 / 3 | `PuntoNoEvaluable` | interior no evaluable (`T = 301.0329 K`, idéntico en V3); en V0, `h(P, s, x)` con equilibrio no resoluble en `T = 345.03 K`, `P = 3e6 Pa`, `x = 0.5140` |
| `f2_h_Ps` | 865 | 18 / 4 | `NoBracket` sin cambio de signo | `F < 0` en todo el rango: V2 `f_lo = −6.624`, `f_hi = −93.837` en [371, 459] K; V3 `f_lo = −20.521`, `f_hi = −62.359` en [385, 427] K |
| `f2_h_Ps` | 1178 | 15 / 3 | `NoBracket` sin cambio de signo | V2 `f_lo = −5.307`, `f_hi = −78.018` en [366, 439] K; V3 `f_lo = −9.262`, `f_hi = −78.018` en [370, 439] K |
| `f2_h_Ps` | 1293 | 22 / 4 | `NoBracket` sin cambio de signo | V2 `f_lo = −5.114`, `f_hi = −72.602` en [361, 429] K; V3 `f_lo = −29.0`, `f_hi = −70.637` en [385, 427] K |

Los rangos de los tres `NoBracket` por signo **difieren entre V2 y V3** porque `_bracket_tol`
camina 5 K hacia dentro sin tope y `_bracket_bis` barre solo `d/64`: V2 evalúa un tramo
distinto del que V3 alcanza a sondear. En las tres, `F` es negativo en **todo** el tramo que
cada una evaluó, y ninguna de las dos estrategias lo cambia.

Clasificación (sin proponer estrategia, como pide el enunciado):

- **`sep.ELV` sin equilibrio (4 filas, `lit_bifasico` 4/19/34/49):** **sin solución en el
  rango físico de T1 con ese backend.** No es un problema de búsqueda: el estado 2 queda
  fuera de la campana binaria a 5 MPa para cualquier composición. Recuperable solo
  cambiando el problema (presión, `T_fuente`), no la estrategia de bracket.
- **`F` sin cambio de signo en todo el rango (3 filas, `f2_h_Ps` 865/1178/1293):** el
  criterio `F = T1_nuevo − T1` no se anula en (T_sumidero, T_fuente) → **sin solución de
  este criterio** en ese punto de operación, con `F < 0` en todo el rango que cada estrategia
evaluó. Clasificado como no recuperable por ninguna estrategia de bracket; no se ha
   evaluado si otro criterio daría solución.
- **`PuntoNoEvaluable` en `brentq` (5 filas: `f2_T_from_Ph` 8/853/997/1505, `f2_h_Ps` 379):**
  los dos extremos del bracket SÍ evalúan y hay cambio de signo, pero un punto interior que
  `brentq` decide sondear cae en un hueco del dominio del backend (`brentq` no admite
  `None`). Son las únicas 5 de las 12 **potencialmente recuperables con otra estrategia**
  (p. ej. tratar el hueco interior), pero **no se propone ninguna aquí**: es una decisión del
director y no estaba en el enunciado. Nota: en V3 estas 5 tienen `nF` = 3–6, de las más
   bajas del conjunto de las 12, porque los extremos sí evalúan y `brentq` falla de
   inmediato; la bisección no llega a activarse.

## 8. Contexto de la corrida (desviaciones y supuestos)

1. **V0/V1/V2 se re-midieron** (lo permite el enunciado) porque el CSV previo no traía `nF`
   ni iteraciones por variante. La corrida de referencia **reproduce el CSV previo
   exactamente**: estado (`convergio`/`no_convergio`/`error_backend`) en **56/56** filas
   para las tres variantes; clasificación en **16/16, 19/19 y 44/44** (las filas en las que
   el CSV previo trae `*_clas`, es decir, las que convergieron); y `η` con
   `max |Δη| = 0.0` en las 79 comparaciones con `η` disponible. (En las filas que no
   convergieron, el CSV previo deja `*_clas` vacío y este CSV lo deja vacío también: por eso
   la comparación de clasificación se hace solo donde hay dato, no sobre las 56.)
2. **Los tiempos absolutos de esta corrida son menores que los del CSV previo** (V0 1142 s
   vs 1910 s; V2 4102 s vs 6856 s) por menor saturación de la máquina (6 workers sobre 16
   núcleos lógicos, 5 variantes por tarea). Como las 5 variantes se midieron en la **misma
   carga y en la misma tarea de worker**, las comparaciones relativas (V2/V0 = 3.59×,
   V3/V2 = 0.58×) son las válidas; los valores absolutos de esta tabla no son comparables
   con los del `REPORTE_ARRANQUE_SOLVER.md`.
3. **VC sí se recalculó, y no hacía falta hacerlo.** El enunciado pedía no recalcular VC y
   tomar sus columnas del CSV previo; como las 5 variantes se corren en la misma tarea de
   worker (para que los tiempos sean comparables), V1 se midió también. **El resultado es
   idéntico al del CSV previo** (estado 56/56, `max |Δη| = 0.0`), así que la repetición no
   cambia ninguna conclusión: VC = la columna `V1` de este CSV. La equivalencia
   `V2 = VB ∪ {f5, f20}` se verificó fila a fila contra este CSV.
4. **`PuntoNoEvaluable` conserva el precedente de la sonda previa** (brentq no admite
   `None`): es una excepción propia del script de diagnóstico, no de `src/`.
5. **V3 no memoriza resultados de `F`.** El extremo que se refina por bisección puede
   coincidir con un punto ya evaluado (p. ej. `lo + d/2 == hi − d/2`); se cuenta como
   evaluación nueva. Con memoización el `nF` de V3 bajaría algo más, pero eso sería otra
   variante, no la especificada.
6. **`brentq` reevalúa los dos extremos** del bracket que `_bracket_tol` / `_bracket_bis`
   ya habían evaluado: 2 evaluaciones extra por variante, idénticas en V2, VB y V3 (V0/V1
   también, por `_bracketear`). No afecta a la comparación relativa.
7. Las cifras de la micro-sonda de §3.2 (coste por etiqueta de llamada) vienen de una
   medición puntual de 2 filas, **no del CSV**; están etiquetadas como tales.

## 9. Conclusión operativa

1. **Qué cambio ayuda: el bracket tolerante.** Solo él recupera 26 de las 28 filas de V2; el
   warm start aporta 2 filas que el bracket no recupera (5 % de la muestra) y no ahorra ni
   una iteración. Si se quisiera actuar sobre `src/`, la palanca es hacer tolerante la
   evaluación de `F(lo)`/`F(hi)` en `_bracketear` (37 de los 40 fallos de V0 están en un
   extremo — 25 `extremo_hi` + 12 `extremo_lo` — y solo 3 en `interior_brentq`),
   **no** ajustar `T10_inicial`.
2. **De dónde viene el coste: de `nF` (94 %).** V2 multiplica las evaluaciones de `F` por
   3.43 y las iteraciones por evaluación **bajan**. El agravante secundario es el grupo
   `lit_bifasico`: 7 filas (12.5 % de la muestra) aportan el 43 % del sobrecoste porque ahí
   el backend está en la frontera de la campana binaria a 5 MPa y cada evaluación paga
   `h(P, s, x)` ≈ 12 s y `sep.ELV` ≈ 6 s en vez de ~150 ms.
3. **V3 no cumple el objetivo de esta tarea.** Con 6 intentos de bisección rescata 24 frente
   a 28 de V2 con un 38 % menos de `nF`: es más barato y estrictamente peor (subconjunto
   estricto de V2, sin ganar ninguna fila). Si se quisiera igualar la cobertura con menos
   evaluaciones, habría que subir el número de intentos o cambiar la secuencia de sondeo —
   **decisión del director, no se propone aquí**.
4. **Ninguna fila rescatada se verificó con el motor real**: las 27 `CORREGIBLE` de V2 (y 25
   de VB, 23 de V3) quedan sin verificar por requisito de `CONTEXT.md`; solo las 5 `KALINA`
   de control, que ya convergían con V0.

**No se ha modificado `src/`.** La decisión de qué llevar a `src/` es del director.