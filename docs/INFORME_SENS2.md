# Informe de Sensibilidad 2: análisis de los 3 921 puntos de Sensibilidad 1

> **KALINA existe donde P_baja supera su piso de cavitación y la efectividad del condensador es alta; la η máxima es 14.53 % dentro del rango experimental (14.82 % fuera).** Los óptimos están pegados a la frontera de existencia.

Libro asociado: `datos/Kalina_anal_sensible_2.xlsx` (18 hojas, 40 gráficos). Todo número sale de los CSV de `resultados/2026-10-17_sens2_P1..P4`. Rama `test/anal_terremoto`.

## 1. Resumen ejecutivo

- 3663 puntos sin duplicados (de 3 921); 55.9 % son KALINA (total).
- 96.5 % de los CORREGIBLE falla por cavitación (O2) y sobreestiman η en +2.5 puntos.
- Casi la mitad de los CORREGIBLE está a una sola variable de un KALINA; P_baja es la que más rescata.
- Los diseños de mayor η operan con título de salida de turbina de 0.94 (límite 0.90).
- La condensación y la cavitación (P_baja, ε_cond, x_b) gobiernan la existencia; η_t, P_alta y T_fuente gobiernan η y potencia.

## 2. Método

Etapa 0 (`docs/ETAPA0_INVESTIGACION_SENSIBILIDAD_KALINA.md`) eligió métodos que se calculan sobre muestreos existentes: RSA/KS, PAWN, δ de Borgonovo, HSIC, PRCC, η², logística, con 3 variables dummy como piso de ruido y bootstrap. Se descartaron Morris, Sobol y FAST (exigen corridas nuevas y salida en todos los puntos). Fase A: existencia y fronteras (P1). Fase C: CORREGIBLE frente a KALINA y distancia (P2). Fase B: índices globales, interacciones y elasticidades (P3). Equipos (P4). Plan en `docs/PLAN_SENS2_ANALISIS.md`.

## 3. Conclusiones por categoría

Cada conclusión indica su fase (A existencia, B interior de KALINA, C comparación), su confianza y su fuente. Orden de categorías por utilidad para el diseño.

### 3.1 DISEÑO REAL (hoja F1 del libro)

**D1 [DISEÑO REAL, fase A, confianza Alta].** P_baja tiene un piso por cavitación (O2): por debajo de él no hay KALINA.

- Evidencia: En los barridos de una variable la frontera está en 550 kPa (C1 y C3), 350 kPa (C2) y 750 kPa (C4). Subir P_baja es el movimiento que más CORREGIBLE rescata: 24 % de los 968 quedan a esa sola variable de un KALINA.
- Implicación: Fijar P_baja por encima del piso de cada bloque con margen.
- Fuente: P1 p1_fronteras.csv; P2 p2_distancia_resumen.md

**D2 [DISEÑO REAL, fase A, confianza Alta].** x_b define una ventana de existencia que cambia con el bloque.

- Evidencia: Frontera de x_b en los barridos de una variable: C1 de 0.525 a 0.925; C2 de 0.425 a 0.575; C3 desde 0.375 y C4 desde 0.625 (sin techo hasta 0.95). En C1 x_b es la variable nº 1 para que haya KALINA (rango medio 1.0).
- Implicación: No existe un x_b único: elegirlo junto con P_baja y la efectividad del condensador (interacción P_baja×x_b, ver F5).
- Fuente: P1 p1_fronteras.csv; P3 p3_ranking.md

**D3 [DISEÑO REAL, fase A, confianza Media].** La temperatura de la fuente tiene un umbral inferior común y un techo que depende del bloque.

- Evidencia: Frontera inferior ≈ 358 K (85 °C) en C1, C3 y C4 y 390.65 K en C2. Techo en los barridos de una variable: 440.65 K (C1), 468.15 K (C2), 568.15 K (C3), 528.15 K (C4).
- Implicación: El techo no es universal: el mismo ciclo admite fuentes más calientes si se reajustan presión y composición. Resolución del barrido: 5 K.
- Fuente: P1 p1_fronteras.csv

**D4 [DISEÑO REAL, fase A, confianza Alta].** El condensador es la restricción que manda: hay una efectividad mínima por bloque.

- Evidencia: ε_cond mínima con KALINA: 0.80 (C1), 0.65 (C2), 0.85 (C3), 0.85 (C4). Frontera en barridos de una variable: 0.775 (C2) y 0.875 (C3). En C1 y C2 ε_cond es de las 3 variables que deciden la existencia.
- Implicación: Dimensionar el condensador para ε ≥ 0.85 salvo que x_b sea bajo (≤ 0.55) y el clima frío; con 0.95 no hay problema de existencia.
- Fuente: P1 p1_existencia_rangos.csv; P3 p3_ranking.md

**D5 [DISEÑO REAL, fase A, confianza Media].** El sumidero frío tiene un techo de temperatura en tres de los cuatro bloques.

- Evidencia: KALINA deja de existir al subir T_sumidero por encima de 284.4 K (C1), 296.9 K (C3) y 291.9 K (C4). En C2 (centro a 300.15 K) no hay cambio en el barrido.
- Implicación: El diseño de Húsavík (278 K) no se traslada a climas cálidos sin subir P_baja y la efectividad del condensador.
- Fuente: P1 p1_fronteras.csv

**D6 [DISEÑO REAL, fase A, confianza Media].** P_alta rara vez limita la existencia, salvo en C2 y C4.

- Evidencia: En los barridos de una variable: C1 y C3 sin cambio de clase; C2 pierde KALINA por encima de 3875 kPa; C4 tiene una ventana sin KALINA entre 1625 y 1875 kPa.
- Implicación: Elegir P_alta por eficiencia (M2) y no por existencia, comprobando el título de salida (E3).
- Fuente: P1 p1_fronteras.csv

### 3.2 EQUIPOS (hoja F4 del libro)

**E1 [EQUIPOS, fase B, confianza Alta].** La turbina debe cubrir relaciones de presión de 1.7 a 5.5 (P5–P95) y caídas de entalpía de 65 a 230 kJ/kg.

- Evidencia: KALINA (total), n = 2047: r_P mediana 3.47; Δh mediana 152.7 kJ/kg; Wt 10.7 a 145.9 kW por kg/s de m_b; T de entrada 361 a 443 K. El 10 % de mayor η: r_P 4.26 a 7.25 y Δh 172 a 249 kJ/kg.
- Implicación: Preseleccionar una turbina radial de una etapa para r_P hasta ~7 (la literatura da radial para EPR < 10). Los diseños de máxima η piden la parte alta del rango.
- Fuente: P4 p4_envolventes.csv; Etapa 0 §5.1

**E2 [EQUIPOS, fase B, confianza Alta].** El Δh de la turbina crece con la relación de presiones, y la η también.

- Evidencia: Regresión Δh sobre r_P: pendiente 30.2 kJ/kg por unidad de r_P, R² 0.65 (n = 507 en el muestreo LHS). Por bandas de r_P: Δh mediana 46 kJ/kg en [1, 1.5) y 236 kJ/kg en [6, 10); η mediana 2.5 % y 10.2 %.
- Implicación: No conviene operar a r_P bajo; el límite superior lo pone el título de salida (E3) y la existencia (D1).
- Fuente: P4 p4_dependencias.csv; p4_bandas.csv

**E3 [EQUIPOS, fase B, confianza Alta].** Los diseños de mayor η operan cerca del límite de humedad de la turbina.

- Evidencia: Título de salida q4 en KALINA: mínimo 0.9014 (límite O1: 0.90). En el 10 % de mayor η: mediana 0.9355 y P5 0.9101, frente a 0.950 de todo KALINA. q4 baja con P_alta (Spearman −0.66 en C1) y con η_t (−0.72 en C2).
- Implicación: Prever protección contra erosión en las últimas etapas o recalentamiento si se sube P_alta; el margen real al límite es ≤ 0.01 en los óptimos.
- Fuente: P4 p4_envolventes.csv; p4_dependencias.csv

**E4 [EQUIPOS, fase B, confianza Media].** El regenerador necesita un acercamiento mínimo de 9.7 K (P5) y una conductancia de 0.76 a 13.3 kW/K por kg/s.

- Evidencia: Contraflujo, estados 5→6 y 10→1: pinch mediana 25.0 K (P5–P95 9.65–46.7); LMTD mediana 37.7 K; UA mediana 4.29 kW/K por kg/s (3.14 en el 10 % de mayor η); Q_reg/Q_i mediana 0.21 (0.03 a 1.31). Sin cruces en ningún KALINA. ε_reg fija el pinch (Spearman −0.92 en C1) y el UA (+0.79).
- Implicación: Para los diseños óptimos, UA mediana 3.1 y P95 7.6 kW/K por kg/s; es una cota de preselección, no un diseño.
- Fuente: P4 p4_envolventes.csv; p4_resumen.md

**E5 [EQUIPOS, fase B, confianza Media].** El condensador debe evacuar de 218 a 1561 kW por kg/s de m_b con un acercamiento de 2.6 a 23.4 K en la salida.

- Evidencia: Mediana: 721 kW por kg/s y 9.2 K. En el 10 % de mayor η: 542 a 1275 kW por kg/s. La carga la fija T_fuente (Spearman +0.55 en C1, +0.69 en C2); el acercamiento lo fija ε_cond (−0.60 y −0.69).
- Implicación: Elegir el condensador por carga (T_fuente) y por acercamiento (ε_cond); el acercamiento no es un pinch de diseño.
- Fuente: P4 p4_envolventes.csv; p4_dependencias.csv

**E6 [EQUIPOS, fase B, confianza Media].** El HRVG debe aportar de 229 a 1695 kW por kg/s de m_b.

- Evidencia: Mediana 790 kW por kg/s; T_fuente − T3 de 2.1 a 44.0 K. La carga la fija T_fuente (Spearman +0.56 en C1, +0.69 en C2).
- Implicación: El tamaño del intercambiador de calor de la fuente escala con T_fuente y con m_b.
- Fuente: P4 p4_envolventes.csv

**E7 [EQUIPOS, fase B, confianza Media].** La bomba consume entre 2.4 % y 30 % del trabajo de la turbina, pero solo 2.7 a 7.8 % en los diseños óptimos.

- Evidencia: W_p/W_t mediana 6.0 %; 10 % de mayor η: 2.7 a 7.8 %. P_alta de 1940 a 4500 kPa (P5–P95).
- Implicación: Bomba de presión media; la cavitación (O2) manda sobre el consumo (D1).
- Fuente: P4 p4_envolventes.csv

### 3.3 MÁXIMA EFICIENCIA (hoja F2 y F4 del libro)

**M1 [MÁXIMA EFICIENCIA, fase B, confianza Alta].** La η máxima es 14.82 % con la fuente a 170 °C, fuera del rango experimental; dentro del rango es 14.53 %.

- Evidencia: 14.82 %: fuente 443.15 K, P_alta 4550 kPa, P_baja 610 kPa, x_b 0.73 (N1-T170-14). 14.53 %: fuente 423.15 K, P_alta 6000 kPa, P_baja 650 kPa, x_b 0.75, η_t 0.85, ε_reg 0.75, ε_cond 0.95 (N10-C3-0016). Mediana de η en KALINA 7.7 %; P90 11.5 %.
- Implicación: Para una fuente de 150 °C el objetivo es ≈ 14.5 % con P_alta alta (≥ 5000 kPa); la cifra de 14.8 % necesita 170 °C.
- Fuente: P2 p2_robustez.md; p2_dataset_dedup.csv

**M2 [MÁXIMA EFICIENCIA, fase B, confianza Alta].** Para Húsavík el mejor KALINA llega a 14.0 % subiendo P_alta a 5000 kPa y bajando P_baja a 600 kPa.

- Evidencia: C1-B3-0127: 394.15 K, P_alta 5000, P_baja 600, x_b 0.82, η_t 0.85, ε_reg 0.75, ε_cond 0.95: η 14.01 %, dentro del rango experimental. El punto base (P_alta 3300, P_baja 690) es CORREGIBLE con η 12.4 %.
- Implicación: Con la misma fuente de 121 °C, ganar ≈ 1.6 puntos exige más presión y quedar cerca del piso de P_baja.
- Fuente: P2 p2_robustez.md; p1 dataset

**M3 [MÁXIMA EFICIENCIA, fase B, confianza Alta].** Mejores equipos dan 13.95 % en Húsavík sin cambiar las presiones.

- Evidencia: C1-B5-0228: η_t 0.95 y ε_reg 0.95 con P_alta 3300 y P_baja 690: η 13.95 %, W_net 124.9 kW por kg/s.
- Implicación: η_t y ε_reg son las palancas de equipo; η_t es la variable con mayor efecto sobre η en C1 y C2 (F1).
- Fuente: P2 p2_robustez.md; P3 p3_ranking.md

**M4 [MÁXIMA EFICIENCIA, fase B, confianza Media].** Los otros dos bloques llegan a 13.2 % (C4) y 12.4 % dentro del rango (C2).

- Evidencia: C4: N7B-C4-B1-045 con fuente 423.15 K, P_alta 3880, P_baja 800, x_b 0.88: 13.23 %. C2: C2-LHS-0005 con 436.5 K, P_alta 3090, P_baja 660, x_b 0.47, η_t 0.95: 12.37 % (13.12 % fuera del rango).
- Implicación: El bloque con x_b bajo (C2) rinde menos que los de x_b alto, con presiones menores.
- Fuente: P2 p2_robustez.md

**M5 [MÁXIMA EFICIENCIA, fase C, confianza Alta].** Los óptimos están pegados a la frontera de KALINA, no en zona segura.

- Evidencia: Distancia L1 normalizada al punto no-KALINA más cercano: mediana 0.138 en el 10 % de mayor η frente a 0.368 en el resto (KS 0.357, p ≈ 1e-21). De 205 puntos, 73 están a una sola variable de la frontera, casi siempre P_baja.
- Implicación: Un óptimo real debe llevar margen en P_baja y en ε_cond; operar en el máximo es operar sobre el piso de cavitación.
- Fuente: P2 p2_robustez.md

### 3.4 FLUCTUACIÓN (hoja F3 del libro)

**F1 [FLUCTUACIÓN, fase B, confianza Alta].** Sobre η, manda η_t en C1 y C2, y manda P_alta con x_b en C3 y C4.

- Evidencia: Rango medio entre 8 métodos (1 = mayor): C1 η_t 1.2; C2 η_t 1.3; C3 P_alta 2.0 y x_b 2.2; C4 P_alta 1.8 y x_b 2.7. PRCC de η_t en C1 +0.74; P_baja −0.63. Las variables citadas son distinguibles del ruido de las 3 variables dummy.
- Implicación: Con fuente fría y x_b alto la presión es la palanca; con x_b bajo, la calidad de la turbina.
- Fuente: P3 p3_ranking.md; p3_indices.csv

**F2 [FLUCTUACIÓN, fase B, confianza Alta].** La potencia específica la mueve T_fuente en C1, C2 y C3, y x_b en C4.

- Evidencia: W_net por kg/s de m_b: T_fuente rango medio 1.0 (C1, C2) y 1.8 (C3); x_b 1.3 (C4). Le siguen η_t y ε_HRVG.
- Implicación: Para potencia, subir la fuente; para eficiencia, la presión y la calidad de la turbina.
- Fuente: P3 p3_ranking.md

**F3 [FLUCTUACIÓN, fase B, confianza Alta].** Para que exista KALINA deciden x_b, P_baja y ε_cond (T_fuente en C4).

- Evidencia: Rango medio en Y1: C1 x_b 1.0, P_baja 2.6, ε_cond 2.8; C2 ε_cond 1.6, P_baja 1.8, x_b 2.6; C3 P_baja 1.0; C4 T_fuente 1.0, P_baja 2.0. Signos: P_baja y ε_cond favorecen; x_b alto perjudica en C1 y C2.
- Implicación: Las tres variables del lado frío del ciclo (condensación y cavitación) gobiernan la existencia.
- Fuente: P3 p3_ranking.md

**F4 [FLUCTUACIÓN, fase B, confianza Media].** η responde casi proporcionalmente a η_t y es sensible a P_baja y T_fuente en el punto base.

- Evidencia: Elasticidades locales: η_t 1.03 a 1.15 en los cuatro bloques; P_baja −0.60 a −0.79; T_fuente 1.02 (C1), 1.28 (C4), 0.25 (C3). En C2 T_fuente da 13.2 porque el punto base está sobre una rampa de la frontera: no usar como valor de diseño.
- Implicación: Un punto de η_t equivale a un punto porcentual relativo de η; subir P_baja 100 kPa (≈ 14 % en C1) baja η ≈ 9 % en términos relativos.
- Fuente: P3 p3_elasticidad.md

**F5 [FLUCTUACIÓN, fase B, confianza Media].** P_baja×x_b y ε_cond×T_sumidero interactúan sobre la existencia; sobre η la interacción es débil o moderada.

- Evidencia: 1 − R² del modelo aditivo sobre el indicador KALINA: B2 0.26 a 0.52 y B4 0.33 a 0.52 (C1 a C4). Sobre η: entre 0.00 y 0.18 en casi todos los pares (aditivos, < 0.05, en B1, B3 y B5 salvo B1 y B3 en C2 con 0.08 y 0.05); fuertes solo B6 en C1 (0.28) y B4 en C4 (0.28).
- Implicación: Para η dentro de la región KALINA, ajustar variable por variable es una buena primera aproximación; para la frontera no: x_b y P_baja se eligen juntos.
- Fuente: P3 p3_interaccion.md

**F6 [FLUCTUACIÓN, fase C, confianza Alta].** Los CORREGIBLE sobreestiman la eficiencia y la potencia de los KALINA.

- Evidencia: η mediana 10.2 % frente a 7.7 % (+2.47 puntos, IC 95 % [+2.18, +2.70]); W_net por kg/s 82.7 frente a 57.9 (+24.8, IC [+19.0, +29.7]). En el muestreo LHS: +3.1 puntos y +40.9 kW por kg/s.
- Implicación: Un CORREGIBLE parece mejor porque incumple cavitación; no sirve como estimador del desempeño real.
- Fuente: P2 p2_comparacion.md

### 3.5 LÍMITES KALINA (hoja F1 y F2 del libro)

**L1 [LÍMITES KALINA, fase A, confianza Alta].** El 96 % de los CORREGIBLE falla por cavitación (O2) y el 4 % por título de salida (O1).

- Evidencia: Entre 968 CORREGIBLE con vecino KALINA: violación dominante O2 96 %, O1 4 %; D mediana 1.17 (P90 10.1). 255 puntos son zona gris (D ≤ 0.278), 249 de ellos por O2.
- Implicación: La frontera práctica de Kalina en este modelo es el piso de P_baja: es la que hay que explorar con mayor resolución.
- Fuente: P1 p1_zonas_grises.csv; P2 p2_violaciones.md

**L2 [LÍMITES KALINA, fase C, confianza Alta].** Rescatar un CORREGIBLE es posible con un solo cambio en casi la mitad de los casos, y cuesta eficiencia.

- Evidencia: 49 % de los 968 CORREGIBLE está a una sola variable de un KALINA (P_baja sube 24 %, ε_cond sube 16 %, x_b baja 3 %, T_fuente baja 3 %). Distancia L1 mediana 0.365; mediana de 2 variables distintas. La η del vecino KALINA es menor en 0.64 puntos (IC [−0.79, −0.30]).
- Implicación: Vale rescatar: el costo es pequeño frente a la sobreestimación (F6). D predice solo débilmente la distancia (Spearman +0.30).
- Fuente: P2 p2_distancia_resumen.md

**L3 [LÍMITES KALINA, fase A, confianza Alta].** Ninguna regla simple separa KALINA de no-KALINA: la región es multivariable.

- Evidencia: En el muestreo LHS el mejor corte único tiene ganancia de Gini ≤ 0.072 (C1: x_b ≤ 0.785). Solo hay reglas puras para no-KALINA: C1 x_b > 0.785 y ε_cond ≤ 0.875 (n = 51, 6 % KALINA); C4 T_fuente ≤ 366.25 K y P_alta > 2800 kPa (n = 32, 3 % KALINA).
- Implicación: Para declarar zonas seguras hay que combinar al menos 2 a 3 variables; los umbrales de D1 a D6 valen cada uno con las demás variables en el centro del bloque.
- Fuente: P1 p1_reglas.md

**L4 [LÍMITES KALINA, fase A, confianza Alta].** El 15 % de los KALINA está fuera del rango experimental (líquido > 420 K) y el máximo global es uno de ellos.

- Evidencia: Entre los 2047 KALINA (total) con η: 15 % fuera. El máximo global (14.82 %) está fuera; el máximo dentro del rango es 14.53 %. La marca empieza hacia una fuente de 150 °C.
- Implicación: Citar siempre el máximo dentro del rango; los puntos fuera son resultados normales del modelo y se muestran aparte.
- Fuente: P2 p2_dataset_dedup.csv; docs/rangos_motor.md

**L5 [LÍMITES KALINA, fase A, confianza Alta].** Quedan límites del análisis que ningún barrido cierra.

- Evidencia: Solo se usó el motor teqp, sin validación experimental propia del ciclo; el lugar crítico de la mezcla no se vigila; m_b no se barrió (escala las potencias); hay 7 puntos atípicos señalados en el libro 1 (Δh de turbina anormalmente bajo) y no se descartan; el diseño mezcla barridos de una variable, mallas y LHS, por lo que las probabilidades por nivel dependen del diseño.
- Implicación: Validar con el motor real los 7 atípicos y los óptimos de M1 a M4 antes de citarlos como cifras de diseño.
- Fuente: Excel 1 LEEME; P1 p1_existencia.md

## 4. CORREGIBLE frente a KALINA

Ver F6 (sobreestimación de +2.47 puntos de η y +24.8 kW por kg/s), L1 (96 % por O2) y L2 (rescate). Los CORREGIBLE aportan información sobre la frontera, no sobre el desempeño: su η es optimista porque incumplen la cavitación.

## 5. Recomendaciones para la próxima campaña

1. Refinar P_baja cerca de su piso (paso de 25 kPa en C1 y C3, 550 kPa; C2 350 kPa; C4 750 kPa): es la frontera que más puntos separa.
2. Barrer T_fuente con paso de 2.5 K en los techos de cada bloque (440.65, 468.15, 568.15 y 528.15 K).
3. Repetir las mallas B2 (P_baja x x_b) y B4 (ε_cond x T_sumidero) con más niveles en C3 y C4, donde la no aditividad de la existencia es alta.
4. Validar con el motor real los 7 atípicos y los óptimos M1 a M4 antes de citarlos como cifras de diseño.
5. Barrer m_b (1, 5, 10, 15, 20) solo si el profesor pide dimensionar por caudal.

## 6. Limitaciones y supuestos

- Solo motor teqp, sin validación experimental propia del ciclo; el lugar crítico no se vigila.
- El 15 % de los KALINA está fuera del rango experimental (líquido > 420 K); se muestran siempre aparte.
- Los diseños mezclan barridos de una variable, mallas y LHS: las probabilidades por nivel dependen del diseño; los índices globales se calcularon solo sobre el LHS de cada bloque.
- η, W_net y los márgenes existen solo en puntos convergidos: las comparaciones de η entre clases condicionan en haber convergido (sesgo de supervivencia a vigilar).
- m_b no se barrió; las potencias son por kg/s de m_b (el estudio 0 usa m_b distinto de 1).
- Las elasticidades salen de solo dos estudios (1 y 10); la de T_fuente en C2 (13.2) está sobre una rampa.
- Los índices de D en C4 (n = 28) son indicativos.
- LMTD y UA del regenerador se reconstruyen de los estados (contraflujo puro); el modelo usa efectividad.
- 7 puntos atípicos del libro 1 no se descartan ni se validaron con el motor real.

*Revisión con la lista de `validate-data` (plugin `data` de Anthropic): duplicados, denominadores, cifras recalculadas de forma independiente, sesgo de selección y gráficos revisados en Excel real. Estado: compartir con los caveats de la sección 6.*
