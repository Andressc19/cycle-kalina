# Plan de mejora de Sensibilidad 2 — objetivo: nota ≥ 4 en cada criterio

**Fecha:** 2026-10-18 · **Rama:** `test/anal_terremoto` · **Punto de partida:** evaluación tipo profesor del 2026-10-18
(informe de un revisor independiente; M2 y U3 comprobados por el director).

| Criterio | Nota hoy | Meta | Cómo se llega (fase) |
|---|---|---|---|
| (a) Rigor estadístico | 2.5 | 4 | F1 |
| (b) Coherencia interna | 2.5 | 4.5 | F0 + F2 |
| (c) Sobre-afirmaciones | 2.5 | 4 | F0 + F2 |
| (d) Cobertura | 3.5 | 4 | F3 (parte con motor) |
| (e) Trazabilidad | 3.0 | 4 | F4 |
| (f) Libro Excel | 3.5 | 4 | F5 |

## 1. Diagnóstico: por qué se pierden los puntos

Cada falla tiene una causa de raíz; arreglar la causa evita que reaparezcan.

| Causa de raíz | Qué produce | Evidencia |
|---|---|---|
| **R1. Cifras y textos escritos a mano en `p5_conclusiones.csv`**; ningún script los genera ni los compara con los CSV | M2 con línea base equivocada (12.4 % del punto M10 en vez de 12.00 % del centro); U3 con el lote de 48 puntos cuando ya hay 96; L7 «0.48» frente a 0.47 | Hallazgos 1, 3, 19, 20 |
| **R2. Los textos no se actualizaron al crecer el trabajo** (U1 pasó de 384 a 808 puntos; el libro de 56 a 76 gráficos) | LEEME «sin corridas nuevas del motor»; `VALIDACION_SENS2.md` con 56 gráficos; informe técnico «70 a 300 °C» | Hallazgos 8, 9, 18 |
| **R3. La confianza no tiene regla** | 20 de 41 conclusiones «Alta»; D1 a D6 «Alta» con fronteras que L9 dice que no se reproducen | Hallazgos 10, 17 |
| **R4. Se confunde «no convergió» con «no existe»** | De 525 NO_CONVERGIO: 191 son falsos convergidos (el balance de energía no cierra), 274 son fallos de bracket o de evaluación, 41 de tiempo y 9 de rango de propiedades. En C4, 37 de 59 puntos del cuartil bajo de T_fuente no convergieron | Hallazgo 6; mensajes de `x1_cargar` |
| **R5. Inferencia estadística mínima**: 3 variables dummy, criterio «algún método supera el máximo», sin corrección por multiplicidad, ocho métodos tratados como independientes | 175 variables marcadas, 38 por un solo método; probabilidad de falso positivo por método ≈ 1/4 | Hallazgos 11, 12 |
| **R6. Comparaciones no pareadas y diseños mezclados** | F6 (+2.47 pp, medianas de regiones distintas) frente a L2 (efecto pareado de 0.64 pp); envolventes de equipos con 2 047 KALINA de barridos, mallas y LHS juntos | Hallazgos 5, 13 |
| **R7. Resolución y censura por diseño** | D1 «550 kPa» es el punto medio entre 500 y 600; D4 da como mínimo físico el límite del LHS; P(KALINA) 0.47 sale de muestrear ε_cond solo hacia abajo | Hallazgos 4, 7, 10 |
| **R8. Falta de datos para dos preguntas** | La curva del ciclo frente a T_fuente (η máx., P_alta y x_b óptimos) y los datos de equipos por potencia (flujo volumétrico, tamaño) no existen | Cobertura (d) |

## 2. Fases

### F0 — Correcciones de texto y cifras (sin motor; ~1 día)

| # | Tarea | Resuelve |
|---|---|---|
| 0.1 | M2: usar el centro real (C1-base-0000, KALINA, η 11.9998 %, ε_cond 0.95); ganancia 2.0 pp | R1 |
| 0.2 | U3 y BLUF del informe con el escenario pooled (96 puntos): p_eta_1pp 0.98/0.66/0.95/0.96; η P5 6.27 (C2) y 10.52 (C4) | R1, R2 |
| 0.3 | L7 «0.47»; sacar a un CSV las estadísticas de m_O2 (2.6, 7.0, 13.2 %) | R1 |
| 0.4 | Estabilidad de U1: reformular sin decir «estable»; declarar que con n = 48 el error típico de P es ≈ 0.07–0.10 y que dos lotes que difieren en 0.02 son compatibles pero no prueban estabilidad | (a), (b) |
| 0.5 | P(KALINA) 0.47 en el BLUF: condicionarlo («con ε_cond muestreada de 0.90 a 0.95, el centro es el tope; con ε_cond fija P = 1.00») | R7 |
| 0.6 | D4: decir «mínimo observado en el diseño» (el límite del LHS) y alinear con U4 (ε_cond ≳ 0.92 en C1 y ≳ 0.906 en C4) | R7 |
| 0.7 | F6 y L2: reescribir juntas; la cifra defendible es el efecto pareado (−0.64 pp) y el intervalo por bloque (+1.4 a +3.2); sin «sin centro» | R6 |
| 0.8 | R1 (superficies): quitar «argumento independiente»; indicar que el máximo del ajuste cae en una celda CORREGIBLE y que el R² es en la muestra | R6 |
| 0.9 | L8: «consistente con» y no «respaldados»; añadir que la campaña vieja usa el mismo motor y los mismos centros | R3 |
| 0.10 | LEEME, PLAN, `VALIDACION_SENS2.md` (76 gráficos, 808 puntos, L7–L9, R1–R2) y resumen del informe técnico (umbral por bloque, no «70 a 300 °C») | R2 |
| 0.11 | Sesgo de supervivencia también para la clase (NO_CONVERGIO) en el informe | R4 |

### F1 — Rigor estadístico (sin motor; ~2–3 días)

| # | Tarea | Salida |
|---|---|---|
| 1.1 | **Nulo por permutación** de cada índice y método (≥ 500 barajados de la respuesta) en lugar de 3 dummies; p-valor por variable, bloque y método | `p6_nulo_perm.csv` |
| 1.2 | **Corrección por multiplicidad** (Benjamini–Hochberg, q = 0.05) sobre todas las pruebas; una variable es «distinguible» si pasa BH y la señalan al menos 2 métodos | `p6_indices_fdr.csv`; F1–F3 rehechas |
| 1.3 | **NO_CONVERGIO**: repetir Y1 y P(KALINA) (a) solo con puntos que convergieron, (b) NO_CONVERGIO como cota baja y alta; ver qué conclusiones de D2, D3 y F3 sobreviven | `p6_sens_nc.csv` |
| 1.4 | **Pareado**: vecino KALINA más cercano por bloque y diseño; diferencia de η, W_net/m_b con IC bootstrap; separar LHS de los demás diseños | `p6_pareado.csv` |
| 1.5 | **Envolventes por diseño**: percentiles de equipos solo con LHS, y con ponderación inversa a la densidad de muestreo; declarar las diferencias frente a los 2 047 KALINA mezclados | `p6_equipos_diseno.csv` |
| 1.6 | **Índices comparables entre bloques**: recalcularlos en la caja común (intersección de rangos de los 4 LHS) | `p6_indices_cajacomun.csv` |
| 1.7 | **Frontera con incertidumbre**: regresión logística de la clase frente a cada variable con IC de la posición de la frontera (bootstrap) en lugar del punto medio entre dos puntos | `p6_fronteras_ic.csv` |
| 1.8 | **Superficie de respuesta**: validación cruzada dejando una celda fuera; informar el R² fuera de muestra y si el máximo cae en una celda sin datos | `p6_superficies_cv.csv` |
| 1.9 | **Potencia de U1**: error típico de P por celda y n necesario para ±0.05 y ±0.10 | `p6_potencia_u1.csv` |

### F2 — Reglas de confianza y generación de conclusiones (sin motor; ~2 días)

| # | Tarea |
|---|---|
| 2.1 | **Regla de confianza escrita y aplicada por código.** Alta: ≥ 2 líneas de evidencia (métodos o campañas distintas), pasa F1 (FDR, NC y pareado) y tiene n ≥ 30 por celda. Media: una línea de evidencia, o depende del diseño o del bloque. Baja: n pequeño, un solo bloque o un resultado que L9 no reproduce |
| 2.2 | **`p5_generar.py`**: cada conclusión es una plantilla con marcadores que se rellenan desde los CSV; así no hay cifras a mano. Los CSV de origen se citan por columna |
| 2.3 | **`p5_cifras_check.py`**: extrae las cifras de cada conclusión y las compara con la fuente (tolerancia por redondeo); falla si una cifra no se encuentra |
| 2.4 | Reasignar la confianza con la regla; rebajar D1 a D6, R1 y L8 si no cumplen |
| 2.5 | Separar «límites del ciclo» de «límites del análisis» con una columna `tipo`; las 5 categorías se mantienen |

### F3 — Cobertura de las preguntas 3 y 4 (parte con motor)

| # | Tarea | ¿Motor? |
|---|---|---|
| 3.1 | **Mapa de existencia en 2 variables**: promover las mallas de F5 a una hoja F1 con leyenda de clases, y añadir los mapas de P_baja × x_b y P_alta × P_baja por bloque | No |
| 3.2 | **Ciclo frente a T_fuente con datos existentes**: η máxima observada, P_alta y x_b del máximo por banda de T_fuente y bloque (estudio 4, LHS y búsquedas) | No |
| 3.3 | **Ciclo frente a T_fuente con optimización local** (T_fuente de 70 a 300 °C cada ~20 °C; 5 variables libres; arranques desde el mejor punto de cada banda): η máx., P_alta, P_baja y x_b óptimos | **Sí (~300 puntos)** |
| 3.4 | **Datos de equipos por potencia**: recalcular estados de ~150 puntos representativos (centros, percentiles de η y r_P) para obtener flujo volumétrico a la salida de la turbina, altura de la bomba, Q y UA de condensador, HRVG y regenerador por kW neto | **Sí (~150 puntos)** |
| 3.5 | **Pisos con resolución de 25 kPa** en los 4 centros (P_baja, 3 niveles de x_b) | **Sí (~100 puntos)** |
| 3.6 | **Reintento de los NO_CONVERGIO** con el modo tolerante ya mergeado (prioridad: estudios 4, 7, 14 y 16, y los falsos convergidos) para separar «no existe» de «no convergió» | **Sí (~320 de 525)** |

### F4 — Trazabilidad (sin motor; ~2 días)

| # | Tarea |
|---|---|
| 4.1 | **`make_sens2.py`**: una orden regenera P1 a P5, U1, R1, R2, el libro y los informes, con las semillas y las versiones registradas |
| 4.2 | **Pruebas** (`tests/test_sens2_*.py`): número de hojas, gráficos y conclusiones; ids únicos; cifras clave contra CSV; libro sin celdas vacías ni solapes |
| 4.3 | **Archivo de supuestos** (`sens2_supuestos.yaml`): tolerancias de U1, umbrales de cercanía (0.15), banda del modelo (±0.7 pp), semillas; cada documento lo cita |
| 4.4 | **Registro de procedencia**: qué se corrió con OpenCode y qué corrió el director (808 puntos de U1: director) |
| 4.5 | Excluir `~$*.xlsx` del control de versiones (`.gitignore`) |

### F5 — Libro Excel (sin motor; ~1–2 días)

| # | Tarea |
|---|---|
| 5.1 | Barras de error con el IC de Wilson en los gráficos de P(KALINA) |
| 5.2 | Ejes de las bandas con el valor de la variable (no el número de cuantil) |
| 5.3 | Sustituir el gráfico de «requisitos por equipo» (solo cuenta filas) por histogramas con percentiles |
| 5.4 | LEEME nuevo: qué pregunta responde cada hoja, regla de confianza, límites del análisis y qué es respaldo y qué no |
| 5.5 | Hojas nuevas de F1 a F3 con los resultados de las fases anteriores (nulo por permutación, BH, NC, pareado, fronteras con IC) |

## 3. Orden, esfuerzo y nota esperada

| Etapa | Contenido | Motor | Esfuerzo | Notas que mueve |
|---|---|---|---|---|
| **A** | F0 + F1 + F2 + F4 + F5 + 3.1 + 3.2 | No | 8–10 días de trabajo | (a) 2.5→3.5–4, (b) 2.5→4.5, (c) 2.5→4, (e) 3→4, (f) 3.5→4, (d) 3.5→3.8 |
| **B** | 3.6 + 3.5 (pisos y reintento) | ~420 puntos ≈ 6–8 h de motor | 1–2 días | (a) y (d) refuerzan; cierran la pregunta 6 de la defensa |
| **C** | 3.3 + 3.4 (T_fuente y equipos) | ~450 puntos ≈ 8–11 h de motor | 3–4 días | **(d) 3.8→4**; responde las preguntas 3 y 4 del profesor |

Sin la etapa C, todos los criterios llegan a ≥ 4 salvo cobertura (≈ 3.8). Con A + B + C, todos ≥ 4.

## 4. Condiciones y riesgos

- **Las corridas del motor necesitan autorización expresa** (regla del proyecto). Se ejecutan con OpenCode y un vigilante;
  si OpenCode no arranca o se cuelga, el director las corre y lo declara (así se hizo con los 808 puntos de U1).
- El motor tardó 60–97 s por punto en la última campaña: las horas de arriba son estimaciones, no garantías.
- Las fases F1 pueden **cambiar rankings y conclusiones** (por ejemplo, menos variables «distinguibles» tras BH). Eso es el
  resultado correcto, pero habrá que reescribir las conclusiones afectadas.
- Aunque se cumplan estas fases, el análisis seguirá basado en el motor teqp sin validación experimental propia; se
  declara en el LEEME y en el informe.
- Meta de nota = criterio del evaluador simulado; el resultado real depende del evaluador.

## 5. Criterio de cierre

Se vuelve a pasar la evaluación tipo profesor con un revisor independiente; el plan se da por cumplido cuando ningún
criterio queda por debajo de 4 y no hay hallazgos críticos ni importantes abiertos.

## 6. Revisión del plan tras estudiar la etapa A (2026-10-18)

### 6.1 Qué se hizo y qué se aprendió

| Pieza | Estado | Qué mostró |
|---|---|---|
| **F0** textos y cifras (commits `4ac4e76`, `b7eb5fb`) | Hecha | 14 conclusiones, el BLUF del informe, el LEEME, `VALIDACION_SENS2.md`, el PLAN y el resumen del PDF corregidos; verificador, `rev_final.py` y reconstrucción del libro en verde |
| **F2** generador (`p5_hechos.py`, `p5_generar.py`) | Hecha | `p5_conclusiones_base.csv` lleva marcadores `{{clave\|formato}}` y `p5_conclusiones.csv` se genera desde los CSV. Hoy 21 conclusiones tienen cifras con marcador; las otras 20 siguen con cifras escritas |
| **F2** regla de confianza (`p5_confianza.py`, `p5_evidencia.csv`) | Primera versión sin commit | Aplicada, la regla deja **3 Alta, 37 Media y 1 Baja**. Es demasiado dura: 31 de 41 conclusiones quedan «parcial» en robustez al diseño |
| **F2** comprobación de cifras (`p5_cifras_check.py`) | Sin hacer | Hoy las comprobaciones viven en un script fuera del repositorio (`rev_final.py`, 23 controles) |

Tres hallazgos que cambian el plan:

1. **La regla v1 confunde «depende del diseño» con «el enunciado ya acota su alcance».** D2 a D7 son fronteras medidas moviendo una variable con las demás en el centro; el texto ya lo dice. Marcarlas «parcial» les impide llegar a Alta, aunque sean exactas en su rebanada. Solución (regla v2): `robusto_diseno` pasa a `si` / `acotado` (el enunciado limita su alcance a la rebanada donde se midió) / `parcial` (se enuncia en general pero depende del diseño) / `no`. `acotado` cuenta como válido para Alta.
2. **La mayor parte de lo pendiente se resuelve con tres cálculos de F1**: 15 conclusiones esperan la prueba de NO_CONVERGIO, 14 esperan un intervalo o una corrección por multiplicidad y 1 espera el emparejado. Hasta que F1 no exista, casi todo queda en Media por construcción, no por mala calidad.
3. **NO_CONVERGIO no se resuelve del todo sin el motor.** En el muestreo LHS solo se puede acotar (extremos pesimista y optimista). En los estudios 4, 7 y 16 (35 % a 38 % de NO_CONVERGIO) y en el cuartil bajo de T_fuente de C3 y C4, la única forma de separar «no existe» de «no convergió» es reintentar esos puntos (etapa B). Con la etapa A, `robusto_nc` queda `si`, `no` o «acotado por cotas»; nunca «resuelto».

### 6.2 Plan de acción revisado (etapa A, en este orden)

| Paso | Contenido | Entregable | Depende de | Notas que mueve |
|---|---|---|---|---|
| **A1** | Cerrar F2: regla v2 (`acotado`), `p5_cifras_check.py` en el repositorio (portar los 23 controles de `rev_final.py` y cubrir las conclusiones nuevas), mover a `p5_hechos.py` las cifras literales de las conclusiones sin marcador que F1 vaya a tocar, y las del informe y el PDF | `p5_confianza.py` v2, `p5_cifras_check.py` | F0 | (b), (c), (e) |
| **A2** | **F1 núcleo.** (1.1, 1.2) nulo por permutación (≥ 500 barajados) con corrección de Benjamini–Hochberg por respuesta, incluyendo la caja común de rangos (1.6) como opción. (1.3) NO_CONVERGIO: Y1 con NC como 0, sin NC y como KALINA; tabla de la fracción de NC por estudio y bloque. (1.4) pareado por bloque, diseño y tipo de violación. (1.5) envolventes de equipos solo con LHS y con peso inverso a la densidad de muestreo. (1.9) potencia de U1 | `p6_nulo_perm.csv`, `p6_indices_fdr.csv`, `p6_sens_nc.csv`, `p6_nc_fraccion.csv`, `p6_pareado.csv`, `p6_equipos_diseno.csv`, `p6_potencia_u1.csv` | A1 | (a) |
| **A3** | **F1 secundario.** (1.7) frontera con intervalo (regresión logística de las 9 variables en el LHS, posición de la frontera con las demás en el centro, IC por bootstrap; se informa el AUC y se descarta si es < 0.8). (1.8) validación cruzada de las superficies (una celda fuera) | `p6_fronteras_ic.csv`, `p6_superficies_cv.csv` | A2 | (a) |
| **A4** | **Reescribir las conclusiones afectadas** con lo que salga de A2 y A3 (F1 a F3, L3, E1 a E7, D1, D3, D8, R1, L6), actualizar `p5_evidencia.csv` desde los CSV (cada campo con su fuente) y regenerar. Si la corrección por multiplicidad quita variables «distinguibles», se escribe lo que quede | `p5_conclusiones_base.csv` v2 | A2, A3 | (a), (b), (c) |
| **A5** | **F4**: `make_sens2.py` (una orden regenera P1 a P5, U1 a R2, F1, el libro y los informes), pruebas `tests/test_sens2_*.py`, `sens2_supuestos.yaml`, registro de procedencia, `p6_mO2_estadisticas.csv`, `.gitignore` para `~$*.xlsx` | script, pruebas, YAML | A4 | (e) |
| **A6** | **F5**: barras de error con el IC de Wilson, ejes con el valor de la variable, histograma en lugar del gráfico de «requisitos por equipo», hojas nuevas con los resultados de F1 (nulo y BH, NO_CONVERGIO, pareado, fronteras con IC) y una hoja de «Cómo leer la confianza», LEEME nuevo | libro de 24 a 26 hojas | A4 | (f), (d) |
| **A7** | Verificación: verificador del libro, `p5_cifras_check.py`, pruebas, auditoría en Excel real; **evaluación tipo profesor por un revisor independiente** | informe del revisor | A5, A6 | todos |

### 6.3 Nota esperada tras la etapa A (estimación, no garantía)

| Criterio | Hoy | Tras la etapa A | Qué falta para 4 o más |
|---|---|---|---|
| (a) Rigor | 2.5 | 3.5 a 4 | Reintentar NO_CONVERGIO (etapa B) para cerrar el sesgo de existencia |
| (b) Coherencia | 2.5 | 4 a 4.5 | Nada, si `p5_cifras_check.py` cubre todas las conclusiones |
| (c) Sobre-afirmaciones | 2.5 | 4 | Nada; la regla v2 con `acotado` debe dar una distribución creíble (no 3 Alta de 41) |
| (d) Cobertura | 3.5 | 3.8 | Ciclo frente a T_fuente optimizado y equipos por potencia (etapa C) |
| (e) Trazabilidad | 3.0 | 4 | Nada |
| (f) Libro | 3.5 | 4 | Nada |

### 6.4 Riesgos y decisiones abiertas

- **La corrección por multiplicidad puede reducir los resultados.** Si F1, F2 y F3 pierden variables, hay que reescribir esas conclusiones; es el resultado correcto, pero cambia el mensaje del libro.
- **Definir «líneas de evidencia independientes» es un juicio.** La regla las cuenta por familia de método (correlación, dependencia, derivada local, campaña distinta), no por número de métodos; el criterio queda escrito en `p5_confianza.py` y en el libro.
- **Reglas y umbrales (n ≥ 30, 500 barajados, q = 0.05, AUC ≥ 0.8) son decisiones mías**, declaradas en `sens2_supuestos.yaml`.
- **Regla de trabajo:** no se lanzan corridas del motor sin autorización expresa; A2 y A3 son solo cálculo sobre datos existentes.

## 7. Etapa B ejecutada (2026-10-18 y 2026-10-19)

Con autorización expresa del usuario se corrieron 828 puntos del motor (más los 808 de U1). OpenCode (DeepSeek, una pestaña, con vigilante) corrió pisos, reintento, densidades y la optimización por T_fuente; el director corrió ε_cond simétrico y terminó la optimización tras tres caídas del script (error de rango de propiedades sin capturar y un archivo sin cabecera). Entregables: `s2b_puntos*.py`, `s2b_corrida*.py`, `s2b_dens.py`, `s2b_opt_T.py`, `p6_pisos25.py`, `p6_reintento_nc.py`, `p6_dens.py`, `p6_sim.py`, `p6_opt_T.py`; hojas F3 Pisos 25 kPa y reintento, F4 Caudales y bomba, F4 Optimo vs T_fuente y F5 Incertidumbre simetrica; conclusiones D9, L10, E10, U5 y M7.

Resultados: el piso de P_baja de la malla sobrestimaba hasta 125 kPa; reintentar con 3 veces el presupuesto no recupera ningún NO_CONVERGIO (0 de 88); por kW neto la turbina maneja 0.25 a 1.69 L/s a la entrada y la bomba 102 a 503 m; P(KALINA) depende del centro de ε_cond (C1 0.25 con centro 0.90 frente a 0.48 con 0.95); la η máxima encontrada por búsqueda local llega a 16.8 % a 160 °C y no sigue subiendo después.

Sigue fuera de alcance: un método de resolución distinto para los NO_CONVERGIO, el NPSH real y la validación experimental propia del ciclo. Falta la evaluación independiente posterior a la etapa B.
