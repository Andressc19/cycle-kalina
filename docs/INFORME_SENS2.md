# Informe de Sensibilidad 2: análisis de los 3 921 puntos de Sensibilidad 1

> **KALINA existe donde P_baja supera su piso de cavitación y la efectividad del condensador es alta; la η máxima es 14.53 % dentro del rango experimental (14.82 % fuera).** Los óptimos tienden a quedar cerca del piso de P_baja.

Libro asociado: `datos/Kalina_anal_sensible_2.xlsx` (22 hojas, 72 gráficos). Todo número sale de los CSV de `resultados/2026-10-17_sens2_P1..P4`. Rama `test/anal_terremoto`.

## 1. Resumen ejecutivo

- 3663 puntos sin duplicados (de 3 921); 55.9 % son KALINA (total).
- 96.5 % de los CORREGIBLE falla por cavitación (O2) y sobreestiman η en +2.5 puntos.
- Casi la mitad de los CORREGIBLE está a una sola variable de un KALINA; P_baja es la que más rescata.
- Los diseños de mayor η operan con título de salida de turbina de 0.94 (límite 0.90).
- Desde el centro KALINA de cada bloque, C1 y C4 no toleran bajar ε_cond (0.95); P_baja puede bajar hasta 600 kPa (C1) y 800 kPa (C4) (D7, L6).
- Al perturbar las 10 variables a la vez (48 puntos del motor por bloque), con tolerancias nominales seguirían siendo KALINA el 48 % (C1), 98 % (C2), 100 % (C3) y 85 % (C4); con el doble, 17, 90, 65 y 42 %; casi todas las pérdidas son por cavitación (U1, U2).
- El piso de P_baja sube con x_b y la superficie de η apunta hacia el menor P_baja (D8, R1).
- El regenerador pierde peso al subir T_fuente: Q_reg/Q_i de 0.59 (70 °C) a 0.013 (300 °C) y UA de 9.5 a 0.34 kW/K por kg/s (E8).
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

**D7 [DISEÑO REAL, fase A, confianza Alta].** Desde el centro KALINA de cada bloque hay margen amplio en casi todas las variables, pero no en el condensador ni, en C2, en x_b.

- Evidencia: Moviendo una variable cada vez (último nivel KALINA contiguo al centro): C1 baja P_baja hasta 600 kPa (centro 690), ε_cond sin margen (0.95; con 0.90 ya no hay KALINA), T_sumidero sube hasta 283.15 K (centro 278.15), x_b de 0.55 a 0.90, T_fuente de 363.15 a 438.15 K. C4: P_baja hasta 800 kPa, ε_cond sin margen, T_sumidero hasta 290.65 K. C3: P_baja hasta 600 kPa, ε_cond hasta 0.90, T_sumidero hasta 295.65 K. C2: P_baja hasta 400 kPa, ε_cond hasta 0.80, x_b solo de 0.45 a 0.55. El barrido fino de ε_cond sitúa la frontera en ≈ 0.92 (C1) y ≈ 0.906 (C4).
- Implicación: Un diseño en C1 o C4 no tolera perder efectividad del condensador ni subir T_sumidero más de 5 a 8 K; en C2 x_b debe controlarse a ±0.05. La frontera real está entre el último nivel KALINA y el siguiente.
- Fuente: Hoja F1 Margenes de operacion (barridos de una variable, estudios 1 y 10)

**D8 [DISEÑO REAL, fase A, confianza Media].** El piso de P_baja sube con x_b: cuanto más rica la mezcla, más alta debe ser la presión baja.

- Evidencia: Menor P_baja con KALINA en cada columna de x_b de las mallas P_baja×x_b: C1 de 500 kPa (x_b 0.55 a 0.75) a 600, 690 y 800 kPa (x_b 0.82, 0.90 y 0.95); C2 de 400 kPa (0.45 y 0.50) a 563.64, 700 y 900 kPa (0.55, 0.60 y 0.70); C3 de 500 kPa (0.55 a 0.68) a 650, 800 y 950 kPa (0.75, 0.88 y 0.95; sin KALINA en 0.82); C4 de 500 kPa (0.65 y 0.72) a 910 kPa (0.95).
- Implicación: x_b y P_baja no se eligen por separado (coincide con la interacción de F5 de P3): subir x_b para ganar η obliga a subir P_baja y se paga parte de lo ganado. La malla tiene solo 7 niveles de P_baja: el piso real está entre dos niveles. Mecanismo: a P_baja fija la temperatura de burbuja baja al subir x_b (C1 a 690 kPa: 330 K con x_b 0.45, 309 K con 0.60, 296 K con 0.75 y 290 K con 0.90), de modo que m_O2 = T_burbuja − T9 se reduce de 52 K a 0.9 K y hace falta más presión para recuperar el margen.
- Fuente: Hoja F5 Superficies de respuesta (mallas P_baja×x_b, estudios 2 y 11)

**U4 [DISEÑO REAL, fase C, confianza Alta].** La efectividad del condensador es la especificación crítica: debe garantizarse por encima de ≈ 0.92 en Húsavík y de ≈ 0.906 en el bloque frío.

- Evidencia: Frontera del barrido fino de ε_cond: C1 entre 0.917 (sin convergencia) y 0.922 (KALINA con m_O2 0.3 K); C4 entre 0.900 (CORREGIBLE) y 0.906 (KALINA con m_O2 0.3 K); C2 y C3 KALINA en todo el barrido de 0.90 a 0.95. Margen de cavitación con ε_cond = 0.95: 5.5 K (C1), 11.8 K (C2), 14.9 K (C3) y 8.1 K (C4).
- Implicación: Pedir al condensador una efectividad garantizada de al menos 0.93 (C1) o 0.91 (C4) con las demás variables en el centro; un diseño que admita ε_cond menor necesita más P_baja o un sumidero más frío (PRCC de T_sumidero negativo, de P_baja positivo).
- Fuente: Hoja F5 Incertidumbre (barrido fino, u1_scan_eps_cond.csv)

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

**E8 [EQUIPOS, fase B, confianza Media].** El regenerador pierde peso al subir T_fuente: su carga y su conductancia caen mientras el pinch sube.

- Evidencia: Estudio 4 (T_fuente de 70 a 300 °C, mediana de los KALINA por nivel): Q_reg/Q_i de 0.587 a 0.013, UA de 9.53 a 0.34 kW/K por kg/s y pinch de 13.6 a 40.0 K. En los barridos de una variable la carga ya es baja a 150 °C (Q_reg/Q_i 0.121 en C3 y 0.048 en C4) y η se aplana desde ≈150 °C (C3 entre 9.28 y 9.47 %, C4 entre 12.23 y 12.32 %). KALINA aparece entre 90 y 165 °C (C1), 120 y 190 °C (C2), 90 y 290 °C (C3) y 90 y 250 °C (C4). Mecanismo (barrido de T_fuente en C3, KALINA): el lado caliente del regenerador es el líquido pobre del separador, y Q_reg = m_l·(h5 − h6) (0.809 × 281 = 227 kW por kg/s a 90 °C). Al subir T_fuente se vaporiza casi todo el fluido: m_l/m_b cae de 0.81 a 0.006 (0.65 a 0.008 en C4) y Q_reg de 227 a 3 kW por kg/s, aunque la caída de entalpía por kg de líquido sube de 281 a 503 kJ/kg.
- Implicación: Con x_b alto (C1, C3, C4) el regenerador mueve 12 % o menos del calor de entrada desde 150 °C (máximos 0.074, 0.121 y 0.048) y η ya no mejora; con x_b bajo (C2) todavía mueve hasta 0.49 a 150 °C y 0.115 desde 190 °C. En el estudio 4 la mediana es 0.34 a 150 °C, 0.13 a 170 °C y no pasa de 0.04 desde 190 °C. Sugiere dimensionarlo pequeño o evaluar suprimirlo solo con fuentes calientes y x_b alto (no se simuló un ciclo sin regenerador). Entre 70 y 110 °C su carga mediana es de 0.27 a 0.59 del calor de entrada.
- Fuente: Hoja F4 Regenerador vs T_fuente (estudios 1, 4 y 10)

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

**M5 [MÁXIMA EFICIENCIA, fase C, confianza Media].** Los diseños de mayor η tienden a quedar cerca del piso de P_baja; la cercanía a la frontera es real pero depende del diseño de muestreo.

- Evidencia: η baja al subir P_baja (PRCC −0.63 en C1) y P_baja tiene piso por cavitación (D1). Con todos los puntos, el 10 % de mayor η está a 0.14 de la frontera frente a 0.37 en el resto (KS 0.357), con 73 de 205 a una variable (casi siempre P_baja); pero esa diferencia mezcla mallas y barridos que ponen puntos junto a la frontera. Solo con el muestreo LHS la diferencia es significativa en C1 (0.62 frente a 0.75, p = 0.016) y no en C2 (0.79 frente a 0.83, p = 0.63), C3 (0.82 frente a 0.90, p = 0.09) ni C4 (0.83 frente a 0.82, p = 0.48).
- Implicación: Un óptimo real debe llevar margen en P_baja y ε_cond. La afirmación general sobre todo el espacio queda como tendencia dependiente del diseño, no como resultado demostrado.
- Fuente: P2 p2_robustez.md; revisión final (LHS solo, recalculado)

**R1 [MÁXIMA EFICIENCIA, fase B, confianza Media].** La superficie de η ajustada solo con celdas KALINA apunta siempre hacia el menor P_baja: el óptimo con restricciones queda en el piso de cavitación.

- Evidencia: Ajuste cuadrático sobre las 8 mallas (P_baja×x_b y P_alta×P_baja; R² de 0.96 a 1.00): el máximo del ajuste cae en el menor P_baja de la malla (400 a 500 kPa) en las 8; en 7 esa celda es CORREGIBLE (no KALINA) y en C2 (P_alta×P_baja) es KALINA. Por ejemplo C1: 15.1 % a 500 kPa, mientras el mejor KALINA de la malla es 13.3 %.
- Implicación: η crece al bajar P_baja hasta chocar con la restricción de cavitación (O2): refuerza M5 con un argumento independiente del muestreo. El máximo del polinomio fuera de las celdas KALINA indica dirección, no un diseño factible.
- Fuente: Hoja F5 Superficies de respuesta (mallas de los estudios 2 y 11)

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

- Evidencia: Rango medio en Y1: C1 x_b 1.0, P_baja 2.6, ε_cond 2.8; C2 ε_cond 1.6, P_baja 1.8, x_b 2.6; C3 P_baja 1.0; C4 T_fuente 1.0, P_baja 2.0. Signos: P_baja y ε_cond favorecen; x_b alto perjudica en C1 y C2. Criterio de ruido: al menos un método supera el máximo de las 3 variables dummy (criterio laxo); las variables citadas lo superan en 3 a 8 métodos (en C4 P_baja solo en 3 de 8).
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

**U3 [FLUCTUACIÓN, fase C, confianza Media].** Al perturbar las variables, la eficiencia de los puntos KALINA se mantiene cerca de la del centro; lo que se pierde es la clase, no la eficiencia.

- Evidencia: Escenario A, fracción de KALINA con |η − η del centro| ≤ 1 pp: 1.00 en C1, 0.94 en C3, 0.98 en C4 y 0.64 en C2. η P5–P95: C1 11.2 a 13.0 % (centro 12.0), C3 8.8 a 10.4 % (9.45), C4 10.7 a 12.1 % (11.15), C2 5.8 a 9.1 % (7.94). En B la dispersión crece (C2 de 2.6 a 10.6 %). La banda del modelo de propiedades (±0.7 pp) se suma de forma determinista a P5 y P95.
- Implicación: El riesgo de diseño es salir de KALINA por cavitación (U1, U2), no perder eficiencia; C2 es el bloque con η más dispersa. Con 48 puntos por celda los percentiles P5 y P95 son aproximados.
- Fuente: Hoja F5 Incertidumbre; u1_resumen.csv

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

- Evidencia: Solo se usó el motor teqp, sin validación experimental propia del ciclo; el lugar crítico de la mezcla no se vigila; m_b no se barrió (escala las potencias); hay 7 puntos atípicos señalados en el libro 1 (Δh de turbina anormalmente bajo) y no se descartan; el diseño mezcla barridos de una variable, mallas y LHS, por lo que las probabilidades por nivel dependen del diseño; los p-valores e intervalos sobre todos los puntos suponen independencia que los barridos y mallas no cumplen, y la versión sobre el muestreo LHS (+3.1 puntos de η, IC [+2.46, +3.65]) es la más defendible. La propagación de incertidumbre (U1 a U3) usa tolerancias supuestas (uniformes, 48 puntos por celda, entradas independientes) y no se estableció la estabilidad del muestreo; la banda del modelo de propiedades se suma de forma determinista y no se muestreó; la importancia por permutación no se implementó; la «confianza» de cada conclusión es la robustez dentro del modelo teqp, no una validación física.
- Implicación: Validar con el motor real los 7 atípicos y los óptimos de M1 a M4 antes de citarlos como cifras de diseño.
- Fuente: Excel 1 LEEME; P1 p1_existencia.md

**L6 [LÍMITES KALINA, fase C, confianza Media].** Cuantas más variables se mueven a la vez desde el centro, menor es la fracción de puntos KALINA, y el condensador es el par que más la reduce.

- Evidencia: Fracción de KALINA (C1, C2, C3, C4): moviendo 1 variable 67, 70, 84 y 71 %; 2 variables 66, 63, 71 y 57 %; 7 a 9 variables 47, 52, 51 y 59 %. En las mallas de pares la de ε_cond×T_sumidero deja KALINA solo el 6 % (C1), 67 % (C2), 16 % (C3) y 10 % (C4); la de ε_reg×η_t es 100 % KALINA en C1 y C2.
- Implicación: Los diseños tienen pasos de tamaño distinto (una variable recorre todo su rango, el LHS recorre las nueve), así que la lectura es exploratoria. Mover el condensador junto con T_sumidero es el cambio de dos variables más peligroso.
- Fuente: Hoja F1 Margenes de operacion (secciones 2 y 3)

**U1 [LÍMITES KALINA, fase C, confianza Media].** Al perturbar las 10 variables con tolerancias nominales, lo único que saca a un centro de KALINA es una efectividad del condensador por debajo de ≈ 0.92 (C1) o ≈ 0.906 (C4); el resto de tolerancias no lo hace.

- Evidencia: Escenario A (96 puntos del motor por bloque en dos lotes independientes de 48, LHS de las 10 variables; T_fuente ±5 K, T_sumidero ±3 K, P_alta y P_baja ±5 %, x_b ±0.02, η_t, η_p, ε_HRVG, ε_reg y ε_cond ±0.05, esta última recortada a [0.90, 0.95] por el tope): P(KALINA) 0.47 en C1 [0.37, 0.57], 0.99 en C2 [0.94, 1.00], 1.00 en C3 [0.96, 1.00] y 0.85 en C4 [0.77, 0.91]; los dos lotes coinciden (diferencias de 0.00 a 0.02, |z| ≤ 1.0), así que P(KALINA) es estable con 48 puntos por celda. Escenario C (igual, pero con ε_cond fija en 0.95): P(KALINA) = 1.00 en los cuatro bloques (48 de 48, IC [0.93, 1.00]) y PRCC de ε_cond = 1.00. Barrido fino de ε_cond (10 niveles de 0.90 a 0.95, resto en el centro): C1 es KALINA desde ε_cond 0.922 (CORREGIBLE con m_O2 −0.1 K en 0.911), C4 desde 0.906 (m_O2 −0.0 K en 0.900), y C2 y C3 lo son en todo el barrido. m_O2 con ε_cond = 0.95: 5.5 K (C1), 11.8 K (C2), 14.9 K (C3) y 8.1 K (C4); cada −0.01 de ε_cond resta ≈ 1.1 K en C1 y ≈ 1.8 K en C4. De los 66 puntos que pierden la clase en A, 64 son CORREGIBLE por cavitación (O2) y 2 no convergen.
- Implicación: Las pérdidas del escenario A no son dispersión general sino una sola variable: la tolerancia que se pueda garantizar en el condensador. Con ε_cond en 0.95 los cuatro centros toleran las demás perturbaciones; el margen de ε_cond antes de salir de KALINA es 0.028 en C1, 0.044 en C4 y ≥ 0.05 en C2 y C3. Las tolerancias son supuestos de escenario (uniformes; incertidumbre estándar ±a/√3), no mediciones.
- Fuente: Hoja F5 Incertidumbre; resultados/2026-10-17_sens2_U1

**U2 [LÍMITES KALINA, fase C, confianza Media].** Con el doble de tolerancia solo C2 y C3 conservan la clase en la mayoría de los casos; C1 y C4 caen a 17 y 42 %.

- Evidencia: Escenario B (tolerancias ×2): P(KALINA) 0.17 en C1 [0.09, 0.30], 0.90 en C2 [0.78, 0.95], 0.65 en C3 [0.50, 0.77] y 0.42 en C4 [0.29, 0.56]. De 90 puntos que pierden la clase, 86 son CORREGIBLE por cavitación (O2). PRCC: C3 ε_cond +0.83 y T_sumidero −0.47; C4 ε_cond +0.79, T_sumidero −0.66 y x_b −0.47. En B ε_cond se muestrea en [0.85, 0.95], también de forma unilateral (media 0.90), de modo que la pérdida de clase vuelve a estar dominada por el condensador.
- Implicación: La robustez ordena a los bloques distinto según la tolerancia (A: C3 > C2 > C4 > C1; B: C2 > C3 > C4 > C1). El condensador y el sumidero son las variables que deciden en C1, C3 y C4.
- Fuente: Hoja F5 Incertidumbre; resultados/2026-10-17_sens2_U1

**L7 [LÍMITES KALINA, fase A, confianza Media].** La clase KALINA exige m_O2 ≥ 0, es decir, cero margen de cavitación; exigir 3 K de margen reduce mucho la existencia, sobre todo en Húsavík y en el bloque frío.

- Evidencia: El criterio O2 es m_O2 = T_burbuja(P_baja, x_b) − T9 ≥ 0 (la tolerancia de 1 K solo normaliza el índice D). Entre los 2243 KALINA de todos los estudios de Sensibilidad 1 (con duplicados), 2.6 % tienen m_O2 < 1 K, 7.0 % < 3 K y 13.2 % < 5 K (4.0, 10.0 y 20.9 % en C1). En la propagación de incertidumbre con tolerancias nominales (96 puntos por bloque), exigir m_O2 ≥ 3 K baja P(KALINA) de 0.47 a 0.15 en C1, de 0.85 a 0.57 en C4, de 1.00 a 0.93 en C3 y de 0.99 a 0.99 en C2. Con ε_cond fija en 0.95 y exigiendo m_O2 ≥ 3 K, P(KALINA) es 0.79 en C1 y 1.00 en C2, C3 y C4: la pérdida de región por exigir margen se concentra en Húsavík.
- Implicación: La región KALINA y los pisos de P_baja de D1 valen para margen cero; un diseño real con margen de NPSH tendría pisos más altos y menos región. El resultado de Húsavík (P = 0.48) depende de aceptar margen cero.
- Fuente: Revisión final (recalculado desde x1_cargar: m_O2 de cada punto y u1_filas.csv)

## 4. CORREGIBLE frente a KALINA

Ver F6 (sobreestimación de +2.47 puntos de η y +24.8 kW por kg/s), L1 (96 % por O2) y L2 (rescate). Los CORREGIBLE aportan información sobre la frontera, no sobre el desempeño: su η es optimista porque incumplen la cavitación.

## 5. Recomendaciones para la próxima campaña

1. Refinar P_baja cerca de su piso (paso de 25 kPa en C1 y C3, 550 kPa; C2 350 kPa; C4 750 kPa): es la frontera que más puntos separa.
2. Barrer T_fuente con paso de 2.5 K en los techos de cada bloque (440.65, 468.15, 568.15 y 528.15 K).
3. Repetir las mallas B2 (P_baja x x_b) y B4 (ε_cond x T_sumidero) con más niveles en C3 y C4, donde la no aditividad de la existencia es alta.
4. Validar con el motor real los 7 atípicos y los óptimos M1 a M4 antes de citarlos como cifras de diseño.
5. Repetir la propagación con más puntos por celda (≥ 200) y comprobar la estabilidad de P(KALINA), con tolerancias medidas o acordadas con el profesor, y muestrear la banda del modelo de propiedades en vez de sumarla.
6. Barrer m_b (1, 5, 10, 15, 20) solo si el profesor pide dimensionar por caudal.

## 6. Limitaciones y supuestos

- Solo motor teqp, sin validación experimental propia del ciclo; el lugar crítico no se vigila.
- El 15 % de los KALINA está fuera del rango experimental (líquido > 420 K); se muestran siempre aparte.
- Los diseños mezclan barridos de una variable, mallas y LHS: las probabilidades por nivel dependen del diseño; los índices globales se calcularon solo sobre el LHS de cada bloque.
- η, W_net y los márgenes existen solo en puntos convergidos: las comparaciones de η entre clases condicionan en haber convergido (sesgo de supervivencia a vigilar).
- m_b no se barrió; las potencias son por kg/s de m_b (el estudio 0 usa m_b distinto de 1).
- Las elasticidades salen de solo dos estudios (1 y 10); la de T_fuente en C2 (13.2) está sobre una rampa.
- Los p-valores y los IC de la comparación sobre todos los puntos suponen independencia que los barridos y las mallas no cumplen; la versión sobre LHS (η +3.1 puntos, IC [+2.46, +3.65]) es la más defendible.
- Los índices de D en C4 (n = 28) son indicativos.
- LMTD y UA del regenerador se reconstruyen de los estados (contraflujo puro); el modelo usa efectividad.
- 7 puntos atípicos del libro 1 no se descartan ni se validaron con el motor real.
- El criterio «distinguible del ruido» es laxo (algún método supera el máximo de 3 variables dummy); la conclusión M5 (óptimos cerca de la frontera) no se sostiene con el LHS solo, salvo en C1.
- La propagación de incertidumbre usa tolerancias supuestas (uniformes, ±a/√3 de incertidumbre estándar), 48 puntos por escenario y bloque (IC de Wilson) y entradas independientes; no se estableció la estabilidad del muestreo (JCGM 101) y la banda del modelo de propiedades (±0.7 pp) se suma de forma determinista. La importancia por permutación no se implementó.
- La cavitación (O2) exige m_O2 = T_burbuja − T9 ≥ 0 (margen cero, no un cálculo de NPSH; ver L7); la «confianza» de cada conclusión es robustez dentro del modelo teqp, no validación física.

*Revisión con la lista de `validate-data` (plugin `data` de Anthropic): duplicados, denominadores, cifras recalculadas de forma independiente, sesgo de selección y gráficos revisados en Excel real. Estado: compartir con los caveats de la sección 6.*
