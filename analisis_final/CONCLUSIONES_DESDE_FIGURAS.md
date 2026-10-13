# Conclusiones leídas directamente de las figuras

Fecha: 2026-10-12. Alcance: las 30 figuras de `03_figuras/` (PNG), vistas una por una.
Las conclusiones de las fichas salen de las **tablas**; aquí se anota lo que **se ve**: la forma
de las fronteras, dónde se concentran los puntos, qué tan abruptos son los cambios, y qué
cosas la figura no deja ver. Donde una cifra está leída de la gráfica (no de una tabla) se
marca con «≈».

Convenciones (de `a3_comun.py`): verde = KALINA, naranja ▲ = Corregible, dorado ■ = Inviable,
rojo ✕ = No convergió, gris ✕ = Falso convergido. **Marcador hueco = fuera del rango validado
del motor de propiedades** (no es un KALINA confiable).

---

## 1. Lectura figura por figura

### Estudio 1.1 y 2.x — el bloqueo del lado caliente

| Figura | Qué se ve | Conclusión desde la figura |
|---|---|---|
| **2.1-1** (OAT desde el profesor, 10 paneles) | De 132 puntos, 0 llegan a la fila KALINA. Solo dos paneles tienen puntos fuera de «No convergió»: **T_fuente** (Corregible entre ≈400 y 560 K; Inviable en ≈590 K; no converge a 623 K) y **ε_HRVG** (Corregible de 0.75 a 0.82; no converge desde 0.83). Los otros 8 paneles son una línea roja plana. | Hay **dos** palancas que hacen converger el ciclo, no una: bajar T_fuente **o** bajar ε_HRVG. La ficha 2.1 menciona solo la primera. La frontera de ε_HRVG es un escalón (0.82 → 0.83), no una pendiente. |
| **2.2-1** (ruta A, 623 K) | 36 puntos, todos Corregible, en una cuadrícula P_baja 400–2000 × ε_HRVG 0.75–0.81. Ninguno cambia de clase. | Con la fuente a 623 K, **subir P_baja de 400 a 2000 kPa no cambia nada** de la clase: la figura es plana en horizontal. P_baja no es la palanca de este bloqueo. |
| **2.2-2** (ruta B) | La región KALINA es una **cuña**: a 390 K aparece desde P_baja ≈450 kPa; a 403 K desde ≈600; a 420 K desde ≈740; a 434 K desde ≈950 y ya hueca (fuera de rango). A 380 K todo es Falso convergido; por encima de 434 K solo Corregible. | (1) La P_baja mínima **sube casi linealmente con T_fuente** (≈ +500 kPa en 44 K). (2) La ventana de T_fuente es angosta: 390–420 K confiables; 380 K no funciona a ninguna P_baja. (3) A partir de ≈434 K los marcadores son huecos: la zona caliente se sale del rango del motor antes de llegar a 623 K. |
| **2.3-1** (η y ε en [0.40, 0.95], 623 K) | Cuatro de los cinco paneles son una fila roja continua. Solo ε_HRVG tiene Corregibles (0.40–0.82); ε_cond 0.90–0.95 da Falso convergido. | Mover η_t, η_p, ε_reg o ε_cond en todo su rango **no desbloquea** la fuente de 623 K; solo ε_HRVG lo hace, y tampoco llega a KALINA. |
| **2.3-2** (ε_HRVG × ε_cond, P_baja 400) | 48 Corregibles y 12 «No convergió». Los rojos forman un bloque en ε_HRVG 0.7–0.8 con ε_cond bajo (0.40–0.70); hay dos rojos aislados en medio de zona Corregible: (ε_cond 0.80, ε_HRVG 0.50) y (0.95, 0.80). | Alta ε_HRVG con condensador poco efectivo es la combinación que rompe. Los dos rojos aislados no siguen la tendencia: **parecen fallas numéricas del solver**, no física (hipótesis, no probada). |
| **2.3-3** (ε_HRVG × P_baja, 623 K) | Los 19 KALINA aparecen solo con ε_HRVG = 0.40 (P_baja ≥ ≈1320) y 0.50 (P_baja ≥ ≈1740). Entre 400 y 1300 kPa, todo Corregible. | Con la fuente de 623 K la frontera sube de ≈1320 a ≈1740 kPa al pasar de ε_HRVG 0.40 a 0.50: **cada +0.10 de ε_HRVG exige ≈ +400 kPa**. Aviso: la leyenda dibuja «KALINA (n = 19)» sin decir que los 19 son fuera de rango (verificado en `todos_los_puntos.csv`: 19/19). |
| **2.3-4** (T_fuente × ε_cond) | De 21 puntos, 1 KALINA: (403 K, 0.95). Al lado: Corregible a 0.85 y 0.90; Inviable en (420, 0.90); No convergió en (497, 0.90). | El resultado confiable de 2.3 es **un solo punto en una malla de 3 valores de ε_cond**: es una existencia, no una región. Lo amplía la figura 4.2-1. |
| **2.4-1** (sumidero frío) | Tres rectas casi paralelas. P_baja mínima baja al enfriar el sumidero de 300 a 278 K: 563 → 292 kPa (403 K), 740 → 395 (420 K), 1310 → 750 (ε_HRVG 0.40). η máxima sube 8.5 → 10.4 %, 8.1 → 11.9 %, 6.3 → 9.7 %. | (1) El sumidero frío baja la P_baja mínima **43–48 %** en las tres rutas. (2) La ganancia de η es **1.9 a 3.8 pp**, mayor con la fuente más caliente (420 K). (3) Es casi lineal: ≈ −12 kPa por K y ≈ +0.09 pp por K. Aviso: la ruta 2.4c (naranja) es toda fuera de rango según la ficha, pero la figura no la distingue. |

### Estudio 3.x — sensibilidad

| Figura | Qué se ve | Conclusión desde la figura |
|---|---|---|
| **3.1-1** (tornado, Δη) | x_b ≈10.8 pp; P_baja ≈6.8; ε_HRVG ≈6.7; η_t ≈6.3; P_alta ≈5.1; ε_reg ≈5.0; T_fuente ≈3.7; η_p ≈1.4; T_sumidero y ε_cond <1 pp. | El efecto sobre η es **grande para 6 variables y pequeño para 3** (η_p, T_sumidero, ε_cond). Ojo: Δη depende del rango barrido (x_b se barre de 0.3 a 0.9, el más ancho), no solo de la sensibilidad. |
| **3.1-2** (elasticidades) | T_fuente ≈ +10.9; x_b ≈ +3.4; T_sumidero ≈ +1.6; P_alta ≈ −1.2; η_t ≈ +1.1; ε_reg ≈ +0.9; ε_HRVG ≈ +0.65; P_baja ≈ −0.55; ε_cond ≈ −0.4; η_p ≈ +0.15. | La elasticidad de T_fuente es **3 veces** la de la siguiente. Pero es una pendiente local pegada al borde de O2 (ver 3.1-3: T_fuente solo tiene KALINA en ≈400–405 K); no extrapolar. Hay **tres signos negativos** (P_alta, P_baja, ε_cond). |
| **3.1-3** (η vs cada variable, 10 paneles) | η crece **casi lineal** con η_t (3.3 → 9.6 %), ε_HRVG (2.4 → 9 %) y ε_reg (6 → 11 %). Con P_baja cae de ≈10.3 % (340 kPa, Corregible) a 3.5 % (1500). Con P_alta hay un **máximo en ≈2300 kPa** (≈9.2 %) y A* queda del lado descendente. T_sumidero da η creciente al calentar (7.8 → 8.6 %). ε_cond: KALINA solo desde ≈0.78 y η baja ligeramente al subir (8.5 → 7.9 %). | (1) η_t, ε_HRVG y ε_reg son palancas **monótonas y sin saturación visible** hasta 0.95. (2) **P_baja baja ⇒ η sube, pero la zona de η alta es Corregible (O2 falla)**: es la tensión central. (3) Para T_fuente, los puntos más calientes (440–580 K) dan η ≈11–11.6 % pero **no son KALINA**: la ganancia de ≈3 pp se pierde por O2. (4) Con P_baja fija, un sumidero **más frío** baja η un poco: el beneficio de 2.4-1 viene de poder bajar P_baja, no del sumidero en sí. |
| **3.1-4** (margen a O2) | Distancia normalizada al cruce: P_alta ≈0.007, ε_cond ≈0.012, P_baja ≈0.016, x_b ≈0.018, T_sumidero ≈0.022, T_fuente ≈0.024, ε_HRVG ≈0.039, ε_reg ≈0.057, η_t ≈0.34. Línea de corte en 0.06. | A* está a **menos de 1–6 % del rango** de la frontera en 8 variables; solo η_t tiene holgura real (34 %). El ancla es un punto **frágil**: cualquier variación pequeña de casi cualquier dato lo saca de KALINA. |
| **3.2-1** (CDF por variable) | Las curvas KALINA se separan claramente del resto en P_baja (KS 0.44), ε_cond (0.43), T_fuente (0.30); poco en T_sumidero y x_b (0.20) y P_alta (0.15, p = 0.035). En η_t, η_p, ε_HRVG y ε_reg las curvas se **superponen** (KS ≤ 0.11, p > 0.2). | **Qué clase sale** lo deciden P_baja, ε_cond y T_fuente (más baja). Las eficiencias y ε_HRVG/ε_reg **no discriminan** la clase. KALINA favorece fuentes más frías y x_b más baja (≈0.5–0.7). Los «sin resultado» se concentran en T_fuente <410 K y P_alta >4300 kPa. |
| **3.2-2** (plano P_alta × P_baja) | 121 KALINA entre las rectas r_P ≈1.7 y ≈5.3; ninguno bajo ≈550 kPa de P_baja. Los KALINA se apilan contra el techo del gráfico (1400–1500 kPa). | La franja KALINA es una **banda de razón de presiones**, no de presiones absolutas: funciona igual a P_alta 2000 que a 5000. Aviso: el techo visible ≈1460 kPa coincide con el límite del muestreo (1498 kPa); es borde de la caja, no frontera física (la figura 3.3-1 muestra KALINA hasta 2500). |
| **3.2-3** (PRCC de η) | P_baja −0.68; P_alta +0.58; η_t +0.37; T_fuente +0.29; ε_reg +0.27; x_b +0.24; ε_cond +0.08; T_sumidero −0.04; ε_HRVG y η_p ≈0 (barras de error cruzan el 0). | En global, **P_baja y P_alta mandan en η**. ε_HRVG parece irrelevante aquí aunque en 3.1-3 mueve ≈6.7 pp: el LHS la barre solo en 0.60–0.95 y la curva está en la parte plana. **Local y global no coinciden en el signo de P_alta** (−1.2 en 3.1-2; +0.58 aquí): responden preguntas distintas y no se pueden resumir como «P_alta sube/baja η» sin condición. |
| **3.2-4** (histogramas ΔP y r_P) | KALINA cubre ΔP ≈700–3800 kPa sin pico; en r_P tiene su pico en ≈2.5–3 y casi no hay KALINA sobre 6, mientras el resto llega a 14. Los «sin resultado» se acumulan en ΔP ≥3800 y r_P >10. | r_P **discrimina** y ΔP **no**. r_P > 6 prácticamente no produce KALINA; r_P >10 casi no produce resultado. |
| **3.3-1** (KALINA por franja de P_baja 1500–2500) | Barras de 33 a 75 %, sin tendencia: 33, 53, 50, 67, 69, 62, 50, 36, 70, 75. | **No hay techo ni descenso** hasta 2500 kPa. El zigzag (33 → 53 → 50 → 67 …) con ≈15 puntos por franja es **ruido de muestreo**; no se puede afirmar que suba. Aviso: 30 de los 75 KALINA de este caso son fuera de rango y la figura no los separa. |

### Estudio 4.x — qué datos del profesor se pueden conservar

| Figura | Qué se ve | Conclusión desde la figura |
|---|---|---|
| **4.1-1** (4.1a, 623 K) | 4 KALINA en 119; 58 «No convergió» repartidos sin estructura. Los 2 confiables están en P_baja ≈1360 y ≈1965 kPa (huecos en ≈1590 y ≈1880). | Con la fuente a 623 K el KALINA solo vive en **P_baja ≥ ≈1360 kPa** (el del profesor es 400). El plano está dominado por rojo: no hay una región, hay cuatro puntos sueltos. |
| **4.1-2** (4.1b, presiones del profesor) | 0 KALINA. Zona fría (<450 K) casi toda Inviable (dorado); zona caliente (>540 K) casi toda No convergió. Los vecinos cercanos a (390–410 K, ε_cond ≥ 0.89) son Corregible/Inviable. | La proyección 2D **oculta** que x_b, η y T_sumidero también eran aleatorios; la franja angosta de 4.2-1 queda sin pisar. Confirma que un LHS de 120 puntos no la encuentra. |
| **4.1-3** (4.1c, presiones y clima) | 0 KALINA; 55 Inviables (46 %), concentrados en T_fuente <460 K. | Mismo patrón que 4.1b: **sin KALINA, pero porque la franja es delgada, no porque no exista** (4.2-1 sí la encuentra). |
| **4.1-4** (4.1d, P_alta y temperaturas) | 6 KALINA, **todos huecos**, con x_b 0.52–0.67 y P_baja ≈950–1960. Para x_b >0.7 hay Corregibles y rojos, ningún KALINA. | Con 623 K y P_alta 3000, solo hay KALINA con **x_b baja y P_baja alta**, y fuera de rango. |
| **4.1-5** (4.1e, fuente y x_b) | 10 KALINA, todos huecos; P_baja ≈650–1810; casi todos sobre 1170 kPa. | Misma lectura: con la fuente de 623 K, **9 de 10 KALINA tienen P_baja >1170 kPa**. |
| **4.2-1** (franja de presiones del profesor) | Tres paneles (sumidero 278, 290, 300 K). A 300 K (su clima): con ε_cond 0.95 hay KALINA de 390 a 410 K; con 0.925, de 390 a ≈397; con 0.90, solo 390–392.5; con 0.875, solo 390; con 0.85, ninguno. A 385 K todo es Falso convergido y a 387.5 K Inviable en los tres paneles. Con sumidero frío (278/290 K) hay KALINA de 390 a ≈407 con ε_cond ≥0.85. | La frontera es una **cuña**: cuanto más caliente la fuente, más efectivo debe ser el condensador. «ε_cond ≥ 0.875» es cierto **solo en el borde izquierdo (390 K)**; para cubrir toda la franja a 300 K hace falta **0.95**, el tope permitido. Por debajo de 390 K no hay KALINA a ningún clima. Aviso: los KALINA se dibujan como cuadrados aunque la leyenda muestra círculo. |
| **4.3-1** (escalera) | KALINA confiables por conjunto conservado: ronda 0: x_b = 15, T_sumidero = 13, P_alta = 12, eficiencias = 11, P_baja = 1, **T_fuente = 0**; ronda 1 (elegido x_b+P_alta) = 7; ronda 2 (+eficiencias) = 7; ronda 3 (+P_baja) = 5. **Todo conjunto que incluye T_fuente da 0.** | Conservar más datos **reduce** los KALINA (15 → 7 → 7 → 5) pero no los elimina. El único dato que da cero es T_fuente. P_baja es el segundo más caro de conservar (1 sola). Aviso: son conteos absolutos con pocos puntos (5–15), sin denominador. |

### Estudios 5.1, 6.1 y 6.2 — optimización, contraste y Húsavík

| Figura | Qué se ve | Conclusión desde la figura |
|---|---|---|
| **5.1-1** (búsqueda de η) | Cinco trayectorias. 5.1d (presiones y clima del profesor) sube de ≈9.5 a 15.6 % y **se aplana** (+0.05 pp en las últimas iteraciones). 5.1a y 5.1b terminan en 15.0 y 15.5 % **todavía subiendo** (≈ +0.4–0.5 pp por paso) cuando se detienen en la iteración 6. 5.1c llega a 12.7 % y 5.1e (fuera de rango) a 11.1 %. Hay puntos evaluados y no aceptados con η hasta ≈17 %. | (1) 5.1d está convergida; 5.1a y 5.1b **no**: sus 15.0 y 15.5 % son cotas inferiores. (2) El 15.6 % es el mejor **aceptado**, no el máximo visto: hay η ≈16–17 % en puntos rechazados, lo que indica que el óptimo está **pegado a la restricción** (KALINA/O2). (3) Cada dato del profesor que se conserva cuesta η: 15.6 → 12.7 → 11.1 %. |
| **6.1-1** (paridad teqp vs motor real) | Cuatro posiciones sobre la recta 1:1, dentro de ±0.7 pp: A* (8.5 %), P03 (≈10.8 %), Húsavík (≈12.7 %) y P08 (≈15.6 %, con 300 s y con 1500 s). Diez puntos cortados por tiempo no aparecen. | Donde el motor real termina, **coincide**. Aviso de lectura: son 5 corridas pero parecen **4 diseños distintos** (P08 aparece dos veces); y los 10 que no terminó no están en la figura, de modo que la comparación cubre solo los casos que el motor real logró resolver. |
| **6.2-1** (malla Húsavík x_b × P_baja) | Para x_b ≤0.475 no hay ciclo (rojos y grises). La P_baja mínima KALINA sube en escalones: 200 (x_b 0.50) → 300 (0.55) → 400 (0.60) → 500 (0.65–0.70) → 600 (0.73–0.76) → 700 (0.79–0.82) → 800 kPa (0.85–0.91). | Es **≈ +150 kPa por cada +0.10 de x_b**, con la resolución de la malla (100 kPa). El borde x_b ≈0.50 es un corte, no una pendiente. Para x_b ≥0.73 la malla empieza en 500 kPa, así que el borde inferior de esa zona no está medido. |
| **6.2-2** (OFAT Húsavík, 10 paneles) | KALINA→Corregible cambia de forma abrupta en T_fuente (≈405 K), T_sumidero (283.15 K), P_alta (≈2800), P_baja (≈650–700), x_b (≈0.85) y ε_cond (solo 0.95 es KALINA). η_t es la palanca más fuerte (10.5 → 13.5 %). Hay dos «No convergió» aislados dentro de curvas lisas (x_b ≈0.625 y ε_cond ≈0.755). | (1) El ciclo de Húsavík vive al filo de O2 en casi todas las variables (como A*). (2) **El corte en T_sumidero = 283.15 K coincide exactamente con el piso de O2 de la corrida**, así que es una condición impuesta, no un hallazgo. (3) ε_cond = 0.95 es el **valor tope** y a la vez el único KALINA: no hay holgura. (4) Los dos rojos aislados se leen como fallas del solver. |

### Síntesis

| Figura | Qué se ve | Conclusión desde la figura |
|---|---|---|
| **S-1** (puntos por clase y estudio) | Total ≈4560 puntos: 1662 KALINA, 1701 Corregible, 344 Inviable, 718 No convergió, 135 Falso convergido. 1.1 es 100 % rojo; 2.1 no tiene KALINA; 4.1 tiene la mayor proporción de rojo e inviable y menos de 5 % KALINA; 5.1 es ≈75 % KALINA. | La proporción de KALINA **no es comparable entre estudios**: 5.1 es un optimizador y 6.x opera junto a un KALINA conocido, mientras que 4.1 es exploración a ciegas. No debe leerse como «qué tan fácil es KALINA». Sí muestra que los rojos se acumulan en 1.1, 2.1 y 4.1, es decir, donde se conserva la fuente de 623 K. |
| **S-2** (matriz de variables) | m_b es gris en **todas** las filas; T_amb_diseño aparece en blanco en los primeros estudios; los bloques finales (M10) fijan 7–8 variables en valores de Húsavík y barren solo P_baja y x_b. | **m_b nunca se movió**: ninguna conclusión cubre el flujo másico. La cobertura de las 10 variables es desigual: las primeras corridas barren pocas y las últimas una por una. Aviso: las filas usan los códigos antiguos KF-Mxx, no la nomenclatura «estudio 1.1–6.2». |

---

## 2. Conclusiones transversales que solo se ven al mirar las figuras

1. **La frontera KALINA es nítida, no gradual.** En 2.1-1, 2.2-2, 3.1-3, 4.2-1, 6.2-1 y 6.2-2 se pasa de verde a naranja en un paso de la malla. Es lo esperable de un criterio de umbral (O2), y significa que **un punto verde no da aviso de que está a un paso del borde** (3.1-4: 8 de 9 variables a menos de 6 %).
2. **La frontera se mueve de forma ordenada con tres variables**: sube con T_fuente (2.2-2, ≈ +500 kPa en 44 K), baja con un sumidero frío (2.4-1, −43 a −48 %) y sube con x_b (6.2-1, ≈ +150 kPa por +0.10). Son tres curvas casi rectas; sirven para interpolar, no solo para describir.
3. **Hay un compromiso central: P_baja baja ⇒ η sube, pero O2 lo prohíbe.** Es visible en 3.1-3 (η de 10.3 a 3.5 % al subir P_baja) y en 6.2-2 (≈ −0.8 pp por cada +100 kPa). Eso explica por qué los óptimos de 5.1-1 quedan pegados a la restricción, y por qué 2 K de margen cuestan menos de 0.5 pp (≈25–46 kPa × 0.5–0.9 pp/100 kPa ≈ 0.2–0.4 pp).
4. **El punto del profesor falla por el lado caliente y la figura lo muestra de cuatro formas**: 2.1-1 (T_fuente, ε_HRVG), 2.2-1 (P_baja no ayuda), 2.3-1 (las eficiencias no ayudan) y 4.3-1 (todo conjunto con T_fuente da 0).
5. **La franja que permite conservar las presiones del profesor es delgada** (4.2-1): 390–410 K y un condensador muy efectivo. Los muestreos aleatorios (4.1b, 4.1c) no la encuentran; solo la malla dirigida.
6. **Con 623 K, los KALINA aparecen en otra región del espacio**: P_baja >≈1000 kPa y x_b baja (4.1-1, 4.1-4, 4.1-5), casi todos fuera de rango. Es otra «familia» de diseños, no una variante del profesor.
7. **El número que decide la clase es r_P, no ΔP** (3.2-4): el KALINA vive en 1.7–5.3 y por encima de ≈6 casi no hay.
8. **Las eficiencias de equipo suben η de forma lineal y sin costo en clase** (3.1-3, 6.2-2): η_t, ε_HRVG y ε_reg hasta 0.95 no sacan al ciclo de KALINA. Son las palancas «seguras» para η.

---

## 3. Avisos sobre las propias figuras

**Estado (2026-10-12):** los avisos 1–4 y el 6 de la tabla quedaron corregidos en las figuras
(Matplotlib y gráficos nativos del Excel); el 5 está explicado en la ficha 3.1; el 7 (códigos KF-Mxx en S-2)
sigue sin cambio. Además, la corrida de corrección confirmó que en 6.1-1 son 5 corridas sobre 4 diseños y
mostró que en 2.3-3 también las 43 CORREGIBLE son fuera de rango.

| # | Figura | Observación | Efecto |
|---|---|---|---|
| 1 | 2.3-3, 2.4-1, 3.3-1 | Mezclan KALINA fuera de rango con confiables sin decirlo en la leyenda (2.3c: 19/19 fuera de rango; 3.3: 30/75). | Un lector puede tomar como diseño válido un punto que la ficha declara no confiable. |
| 2 | 4.2-1 | KALINA dibujado como cuadrado; la leyenda muestra círculo. | Confusión de lectura (también con el cuadrado dorado «Inviable»). |
| 3 | 3.2-2 y 3.2-1 | El techo de P_baja de los KALINA (≈1460 kPa) es el borde del muestreo (1498). | La «ventana 683–1461 kPa» del reporte (§4, conclusión 4) puede leerse como límite físico; 3.3-1 muestra KALINA hasta 2500. Conviene anotar «dentro de la caja muestreada». |
| 4 | 5.1-1 | 5.1a y 5.1b se detienen mientras suben. | Sus 15.0 y 15.5 % son cotas inferiores; el 15.6 % de 5.1d sí está convergido. |
| 5 | 3.1-2 vs 3.2-3 | P_alta tiene signo opuesto (local −1.2, global +0.58). | Debe explicarse en la ficha (3.1-3 muestra un máximo en ≈2300 kPa). |
| 6 | 2.1-1 vs ficha 2.1 | La ficha nombra solo T_fuente; la figura muestra también ε_HRVG ≤0.82. | Omisión menor en la conclusión 2 de la ficha 2.1. |
| 7 | S-2 | Usa códigos KF-Mxx en vez de «estudio 1.1–6.2». | Inconsistencia con el resto tras el refactor del 2026-10-12. |

## 4. Lo que las figuras no permiten concluir

- **Causas físicas.** Las figuras muestran *qué* pasa, no *por qué* (por ejemplo, por qué η cae al calentar la fuente a P_baja fija, o por qué ε_cond más alta baja η).
- **Fallas numéricas vs. físicas.** Los rojos aislados (2.3-2, 6.2-2) son sospechosos de solver, pero sin reintento no hay prueba.
- **El borde superior de T_fuente** en 4.2-1 (la malla termina en 410 K) y el borde inferior de P_baja para x_b ≥0.73 en 6.2-1.
- **Efectos de m_b** (S-2: nunca se movió).
- **Diferencias menores que ≈0.7 pp** entre puntos (banda de 6.1-1).
