# ETAPA 0 — Investigación bibliográfica de sensibilidad y preselección (KSC-11, NH3-H2O)

**Fecha:** 2026-10-17 · **Rama:** `test/anal_terremoto` · **Ámbito:** solo investigación y redacción.
Complementa (no repite) `docs/ESTUDIO_METODOS_SENSIBILIDAD.md` y `docs/METODOLOGIA_ANALISIS_RESULTADOS.md`.

> **Convención de términos.** No se usa «confiable / no confiable / no citable». Se dice «dentro del rango
> experimental» o «fuera del rango experimental (líquido > 420 K)». Toda cifra lleva su fuente `[n]` de la §7.
> La terminología del modelo (KALINA, O1–O5, D, margen) es la del proyecto y se cita como tal.

---

## 1. Métodos recomendados

La pregunta del proyecto es doble: (a) **¿qué variable decide si un punto es KALINA?** (salida binaria) y
(b) **¿qué variable mueve η y W_net entre los que sí funcionan?** (salida continua). A eso se suma un tercio
de puntos sin solución. Un método global por varianza (Sobol/FAST/Morris) exige una salida definida en **todos**
los puntos y una frontera suave: aquí ninguna de las dos cosas se cumple `[12][14]`. Por eso se recomienda una
**familia de métodos «given-data»** que operan sobre un muestreo ya existente `[9][10]`.

| Método | Qué mide | Requisitos | ¿Sirve con el LHS existente? | Riesgo con puntos sin solución | Fuente |
|---|---|---|---|---|---|
| **RSA / filtrado de Monte Carlo (KS)** | Separa puntos «que cumplen» de «que no» y compara las CDF por variable (estadístico KS) | Muestreo previo + criterio de comportamiento | **Sí** (es su caso de uso) | **Bajo**: los fallos caen en el grupo «no cumple» | `[8][9]` |
| **PAWN** | Distancia KS entre la CDF incondicional y la condicional al fijar una variable | Muestreo previo; sirve con entradas categóricas | **Sí** (given-data) | **Bajo si la salida se define en todos** (margen 0/1) | `[11][12]` |
| **δ de Borgonovo (moment-independent)** | Cambio en **toda** la distribución de la salida al fijar una entrada | Estimador given-data (Plischke-Borgonovo-Smith) | **Sí**, con estimador single-loop | **Bajo** con salida categórica (media de indicadores) | `[13][14]` |
| **HSIC** | Dependencia no lineal X↔Y (norma Hilbert-Schmidt del operador de covarianza) | Matrices de kernel; salida admite clase/indicador | **Sí** (given-data) | **Bajo**: acepta salida discreta con kernel característico | `[15][16]` |
| **PRCC / SRC** | Correlación parcial de rangos (signo e importancia, monótona) | Muestreo LHS; solo puntos con salida | **Sí** (post-proceso) | **Medio**: sesgo de selección si los fallos son informativos | `[17][26]` |
| **η² / correlation ratio (ANOVA post-hoc)** | Fracción de varianza explicada por una entrada | Muestreo previo | **Sí** | **Medio** (solo convergidos) | `[14]` |
| **D-VARS / VARS-TO** | Índices totales «given-data» (Razavi/Sheikholeslami) | Muestreo previo | **Sí** (implementado en `monaco`) | **Bajo** (categoriza entradas) | `[18][19]` |
| **Elasticidad OAT** | Cambio relativo local (Δη/η)/(Δv/v) | Diseño propio (ya existe M3) | No; ya cubierto por M3 OFAT | Bajo (fronteras) | `[1][4]` |
| **Morris (efectos elementales)** | Importancia μ* y no linealidad σ | r(k+1) puntos de trayectoria | **No** (diseño propio) | **Alto**: cada EE exige los dos extremos convergidos | `[2][3]` |
| **Sobol / Saltelli** | Descomposición de Var(y) (S_i, S_Ti) | Matrices A/B (~N(k+2) puntos) | **No** directo | **Alto**: rompe con salidas ausentes | `[5][6]` |
| **FAST / eFAST** | Mismos índices por frecuencias | Muestreo por frecuencias | **No** | **Alto** (igual que Sobol) | `[7]` |
| **DGSM** | Derivadas globales (Sobol total ≥ cte·DGSM) | Derivadas o diferencias finitas | Parcial (dif. local) | Alto si el punto base no converge | `[20]` |
| **Efectos de Shapley** | Reparto de varianza con entradas correlacionadas | Metamodelo o muchas corridas | Parcial (con sustituto) | Medio | `[21]` |
| **Regresión logística** | Signo/tamaño del efecto sobre P(KALINA) | Etiqueta binaria en todos los puntos | **Sí** (ajuste sobre LHS) | **Bajo**: los fallos entran como clase 0 | `[22]` |
| **Importancia por permutación** | Caída de una métrica al permutar una entrada | Un modelo ajustado + el mismo muestreo | **Sí** (con modelo) | **Bajo** | `[23][24]` |
| **Árbol CART (reglas)** | Reglas legibles de la región KALINA | Requiere `scikit-learn` (o stump en numpy) | **Sí** (con modelo) | **Bajo** | `[25]` |
| **GSA de salida Bernoulli** | Sobol de un indicador q=1(falla) | Diseño propio o given-data | Parcial | **Bajo**: la falla es el «evento» | `[27]` |
| **Sobol extremal (MC filtering + sustituto)** | Índices condicionados a la zona extrema de la salida | Puntos + rechazo/sustituto | Parcial | Medio | `[28]` |

**Recomendación de diseño (no repite el estudio previo, lo refuerza):** sobre los datos ya existentes (3 921
puntos en total; el LHS propiamente dicho es de 500 puntos en 9 variables) se puede calcular **sin nuevas corridas**: RSA/KS `[8]`, PAWN `[11]`, δ de Borgonovo `[13]`, HSIC `[15]`,
PRCC/SRC `[17]`, η² `[14]`, D-VARS `[18]`, regresión logística `[22]`, importancia por permutación `[23]` y
CART `[25]`. Los que **exigen diseño propio** (Morris, Sobol, FAST, DGSM, Shapley) quedan descartados por coste
(~31 s/punto) y por el hueco de los NO_CONVERGIO `[12][14]`.

**Puntos que el estudio previo no cubría y aquí se añaden:** (i) el **δ de Borgonovo** y **HSIC** como medidas
de dependencia que no suponen monotonía `[13][15]`; (ii) el tratamiento de la salida **Bernoulli** con Sobol
del indicador de falla `[27]`; (iii) el **estimador single-loop «given-data»** que permite varianza y densidad
sobre un mismo muestreo `[9][14]`; (iv) el uso de un **parámetro «dummy»** como piso de ruido de los índices `[29]`.

---

## 2. Hallazgos Kalina (variables de mayor impacto, valores de referencia con fuente)

### 2.1 Variables de mayor impacto (consenso bibliográfico)

| Hallazgo | Evidencia | Fuente |
|---|---|---|
| **Composición a la entrada de turbina (x_b) y temperatura del separador** son las variables clave | Identificadas por Marston (1990) y Nag & Gupta (1998); confirmado en revisiones y estudios de optimización | `[30][31][32]` |
| **x_b y presión de entrada de turbina** gobiernan η y W_net en KCS-11 | Estudio paramétrico que cruza x_b con P_evap | `[33][34]` |
| **Efecto de T_fuente es el más fuerte, seguido de T_sumidero** en un split-cycle | ±50 K de fuente ≈ ±40 % de potencia; ±15 K de agua fría ≈ ±7 % | `[30]` |
| **La eficiencia exergética del condensador cae al subir la temperatura del agua de enfriamiento**; agua más fría permite menor P_cond y más x_b | Análisis exergético del ciclo | `[35][30]` |
| **El recuperador añade eficiencia** (precalienta el fluido al evaporador) | KCS-11 y KCS-34 se diseñan con recuperadores | `[31][36]` |
| **Rango de x_b para operación estable: 0.55–0.9** | Curvas η vs x_b a varias P y T | `[33]` (Papers/ctt020.pdf) |

### 2.2 Valores de referencia de eficiencia y óptimos

| Configuración / caso | Condición | Resultado | Fuente |
|---|---|---|---|
| **KCS-11** (baja temperatura) | P_evap 10–50 bar; T_fuente 333–473 K; T_sumidero 283 K; x_b óptimo 0.55 | Hasta **+40 %** vs ORC-amoníaco y **+20 %** vs R134a | `[33]` |
| **KCS-11, Jailolo (geotermia)** | x_b 0.85; P_turbina 29 bar; fuente 179 °C; salmuera 76.3 kg/s | **η_net 11.7 %**, **3.3 MW** | `[36]` |
| **KCS-11 (barrido de x_b)** | Ídem, por fracción másica | 70 % → 7.5 % @29 bar; 75 % → 8.9 % @31 bar; 80 % → 10.3 % @32 bar; 85 % → 11.7 % @29 bar | `[36]` |
| **Kalina básico (óptimo de x_b)** | P_evap 1000–7000 kPa; T_evap 100–150 °C | Con P ≤ 3000 kPa **existe x_b óptimo**; con P > 4000 kPa **no hay pico** (η crece monótona con x_b y T) | `[37]` |
| **KCS-34 con 2.º separador** | P_evap 3 MPa | η_térmica máxima 12.04 / 12.65 / **11.76 %** (A/B/C); exergía 59.56 / **62.59** / 58.16 % | `[38]` |
| **KCS-11 con eyector / KCS-34 con eyector** | T_geotermia 443.15 K; x_b 0.6; η_t 85 %; η_p 75 % | η_térmica 13.78 % (KCS-11) y **16.55 %** (KCS-34); exergía 49.85 % y 57.56 % | `[39]` |
| **KCS-11 modificado (SSE, sin válvula)** | P_evap 3.0 MPa; x_b 0.75 | η_exergía **56.59 %** | `[40]` |
| **KCS-34 (Húsavík)** | Geotermia 121 °C; mezcla ~82 % amoníaco | 2 MW nominales; **> 1 600 kW** sostenidos | `[31][41]` |
| **KCS-34 (optimización)** | — | Máx. eficiencia y potencia a **x_b 0.78** | `[42]` |
| **Split-cycle (Nguyen et al.)** | T_fuente 346 °C; T_agua 25 °C | x_b 0.75–0.8 **exige 125–130 bar**; alternativa x_b 0.6–0.7 con P_baja baja | `[30]` |
| **Cota baja de generación** | Ciclo Kalina | Temperatura mínima de generación ≈ **53 °C** (enfriamiento con agua) | `[43]` |
| **Kalina «de dos presiones» / ciclos interactuantes** | La variante descrita por Kalina (IGW2003) se interpreta como **dos ciclos acoplados** mediante un separador adicional (S3) a **presión intermedia** | Niveles: P_alta, P_intermedia (S3) y P_baja | `[68]` |
| **KC1 / KC2 / KC3 (multietapa)** | KC3 opera a **16 500 kPa (~2 400 psi)** frente a ~10 000 kPa de KC0–KC2; la eficiencia sube con la presión y el nº de etapas | `[31]` |
| **Diseño nominal de KCS-11** | Concebido para recursos **≥ 375 °F (~190 °C)**; su uso a 60–200 °C es una **aplicación** posterior, no el diseño original | `[68]` |

**Nota de rango.** Los valores con T_fuente > 420 K (p. ej. split-cycle a 346 °C) describen comportamiento de
mezcla **fuera del rango experimental (líquido > 420 K)** del modelo Tillner-Roth & Friend `[44]`; se usan solo
como tendencia, nunca como magnitud de validación.

---

## 3. Plantilla de informe técnico de sensibilidad (índice propuesto)

Basada en la regla «confesar en presencia de la sensibilidad» (explicar la búsqueda de especificaciones para que
el lector juzgue) `[45][46]` y en la estructura de bloques del proyecto (`METODOLOGIA_ANALISIS_RESULTADOS.md`).

1. **Resumen ejecutivo (BLUF):** pregunta respondida, hallazgo principal, cifra que lo sostiene, criterio que manda.
2. **Objetivo y preguntas:** fijar el marco de sensibilidad — priorización de factores, análisis de tendencia,
   cuantificación de interacciones `[47]`.
3. **Modelo y datos:** entradas y rangos; salidas (clase + η/W_net/márgenes); diseño del muestreo (OFAT, mallas,
   LHS con semilla); nº de puntos; motor y su coste.
4. **Definición de rango experimental y tratamiento de no convergencia:** qué es «dentro/fuera del rango
   experimental (líquido > 420 K)»; cómo entran los NO_CONVERGIO.
5. **Métodos aplicados y justificación:** tabla método → qué mide → por qué se eligió → qué se descartó y por qué `[12]`.
6. **Resultados globales:** tabla de índices (RSA/KS, PAWN, δ, PRCC, HSIC), CDF condicionales, tornado, con
   intervalos de confianza por bootstrap y **parámetro dummy** como piso de ruido `[29]`.
7. **Resultados por bloque de comparabilidad:** un bloque = mismas variables fijas (regla del proyecto).
8. **Región factible y distancia a la factibilidad:** reglas (árbol) de la zona KALINA y distribución de D.
9. **Hallazgos de diseño:** preselección de turbina, regenerador y condensador (§5).
10. **Limitaciones y supuestos:** sustitutos, sesgo de selección, banda de incertidumbre de η.
11. **Conclusiones y recomendaciones:** una frase por pregunta + cifra + confianza + próximo paso.
12. **Anexos:** fuentes numeradas, glosario, tablas y **reproducibilidad** (semilla, versiones, CSVs) `[45][46]`.

**Reglas de tabla y figura (heredadas del proyecto):** cada tabla lleva encabezado (caso, bloque, datos fijos),
cuerpo con unidades y notas con fuente; cada figura es de un solo bloque; el color no va solo (forma + color).

---

## 4. Tratamiento de no convergencia y «distancia a KALINA»

### 4.1 Cómo entran los puntos sin solución

- **Grupo de comportamiento:** en RSA/filtrado de Monte Carlo, un punto que no converge simplemente cae en el
  grupo «no cumple» y **no se descarta**; eso evita el sesgo de analizar solo los convergentes `[8][9]`.
- **Salida definida en todos los puntos:** en lugar de η (que no existe en los fallos), se usa una **magnitud
  continua de violación** (los márgenes O1–O5 del proyecto) o un **indicador 0/1**; así PAWN, δ, HSIC y Sobol
  Bernoulli se calculan sin huecos `[11][13][15][27]`.
- **Piso de ruido:** incluir un factor dummy y comprobar que los índices de las variables reales lo superan `[29]`.
- **Registro explícito del fallo:** `monaco` marca los casos fallidos como incompletos y permite repetirlos sin
  recalcular todo; es el patrón a imitar en el motor (guardar «no convergió», no borrar la fila) `[18]`.
- **Robustez numérica del ciclo:** la biblioteca ThermoCycle (Modelica) documenta que la simulación de ciclos
  termodinámicos falla sobre todo en inicialización e integración con EOS complejas, y mitiga con estrategias de
  robustez por componente — referencia de prácticas, no de valores `[48]`.

### 4.2 Distancia a la factibilidad

- El proyecto ya define **D** (suma de violaciones normalizadas por tolerancias τ) en `MATEMATICA_ITERACIONES_SENSIBILIDAD.md`.
- La literatura de optimización respalda esa forma: las penalizaciones **basadas en distancia a la factibilidad**
  superan a las basadas solo en el número de restricciones violadas `[49][50]`.
- **Normalización por tolerancia:** la práctica ε-normalizada (dividir cada violación por un ε_i y quedarse con la
  parte positiva) es exactamente la construida con τ; el objetivo es `γ_i ≤ 1` para todas las restricciones `[51]`.
- **Violación de restricción puntual:** MATLAB define `infeasibility(constr, pt)` como el valor numérico de la
  violación en un punto (0 = factible) — útil como semántica de D `[52]`.
- **Conjunto mínimamente infactible (IIS):** cuando un punto no converge, identificar el **subconjunto mínimo de
  restricciones** que lo hacen infactible (`Chinneck`) da la explicación («falla solo O2») en vez de un código opaco `[53]`.
- **Proyección a la región factible:** además del escalar D, se puede reportar la **dirección de menor corrección**
  (qué variable mover y cuánto) resolviendo un problema de mínima distancia a la frontera; en la práctica basta la
  proyección normalizada `Violación_i / τ_i` sobre la restricción activa `[49][51]`.
- **Reporte:** D siempre con el vector completo de violaciones (no ocultar tras un escalar), como ya exige el proyecto.

---

## 5. Criterios de preselección de equipos (valores de referencia con fuente)

### 5.1 Turbina / expansor

| Criterio | Valor de referencia | Fuente |
|---|---|---|
| Tipo según relación de expansión (EPR) | **Radial-inflow (RIT) recomendada para EPR < 10**; axial para caudal alto y EPR bajo; axial de impulsos factible en pequeña escala si EPR alto y caudal bajo | `[54]` |
| EPR típicos de turbinas pequeñas | **1.997–7.95** en la mayoría de las turbinas ORC revisadas | `[54]` |
| Eficiencia isentrópica de RIT | **65–85 %**; se reporta hasta **85 %** alcanzable | `[54][55]` |
| Velocidad específica óptima (RIT) | **0.4–0.8** | `[54]` (citando a Uusitalo et al.) |
| Turbina radial-outflow (ROT) | 10–400 kW; 7 200–42 700 rpm; **68.7–85 %** | `[54][56]` |
| **Título de salida de turbina ≥ 0.90** | Restricción estándar para no dañar álabes; usada como cota de P_baja en varios estudios | `[33][57]` |
| η_t de referencia en los casos | 80 % (Jailolo, Elsayed), 82 % (solar KC-12), 85 % (configuraciones KCS-11/34 con eyector); η_p 65–75 % | `[33][36][39][57]` |
| Relación volumétrica | RIT maneja alto **volumetric flow ratio** en una sola etapa | `[55]` |

### 5.2 Regenerador (recuperador)

| Criterio | Valor de referencia | Fuente |
|---|---|---|
| Modelo | Método de **efectividad** o **LMTD / pinch point**; ambos usados en la literatura | `[35]` |
| Pinch del regenerador | **4 K** (Elsayed); **5 K** en recuperadores (Nguyen); 10 °C en un caso de 120 °C de fuente | `[30][33][35]` |
| Función | Precalienta el fluido de alta presión hacia el evaporador; sube η | `[31][36]` |
| Intercambio | Cerrar con ε (método del proyecto) o con pinch; documentar cuál para no mezclar | `[33]` |

### 5.3 Condensador

| Criterio | Valor de referencia | Fuente |
|---|---|---|
| Modelo | Energía o **LMTD**; ε-NTU como alternativa equivalente | `[35][58]` |
| Approach / pinch | **4.5 K** en el condensador y 5 K de subenfriamiento (Nguyen/Nigro); TTD 7 °C en calentadores cerrados | `[30][59]` |
| Comportamiento zeotrópico | Condensación a temperatura variable (glide); se ajusta cambiando x_b y presión | `[60][31]` |
| Carga y tamaño (micro-canal) | Condensador micro-canal dimensionado para un Kalina de 1 kWe con LMTD; el tamaño es sensible al modelo de transferencia | `[61]` |
| Agua de enfriamiento | T_agua baja → menor P_cond y mayor x_b admisible; subir T_agua baja la η exergética | `[30][35]` |

### 5.4 Bomba / cavitación (criterio O2 del proyecto)

| Criterio | Valor de referencia | Fuente |
|---|---|---|
| Margen NPSH recomendado | **NPSHA/NPSHR ≈ 1.1–2.5** (Hydraulic Institute); margen típico ≈ 1.5 m; 10 % mínimo y 100 % en aplicaciones críticas | `[62][63]` |
| NPSH = presión de succión − presión de vapor | `NPSH = Ps − Pvap` | `[62][63]` |
| Amoníaco (alta P de vapor) | Requiere mantenerse presurizado o subenfriado; existen bombas de amoníaco con NPSHR ≈ 0 (toleran líquido saturado sin subenfriamiento) | `[64]` |

> Nota: en los papeles Kalina el criterio O2 se maneja como **subenfriamiento en la bomba** y en la práctica como
> cota de P_baja; su vínculo con NPSH es el de la tabla y el modelo del proyecto (`T_burbuja(P_baja) − T9`).

---

## 6. Capacidades necesarias (librerías / herramientas)

**Ya disponibles** (según `requirements.txt` y los docs del proyecto): `numpy`, `scipy`, `pandas`, `matplotlib`.

| Capacidad | Se puede con lo que hay | Requiere nueva librería | Nota |
|---|---|---|---|
| LHS y QMC | `scipy.stats.qmc.LatinHypercube` | — | Ya usado en M4/M5 |
| KS / PRCC / bootstrap | `scipy.stats.ks_2samp`, `spearmanr`, `bootstrap`, `rankdata` | — | RSA y PRCC sin dependencias nuevas |
| PAWN | Ordenar + `ks_2samp` / `scipy.stats.ecdf` | — | Implementable en numpy/scipy |
| η² / correlation ratio | `numpy` (grupos por cuantiles) | — | Post-proceso del LHS |
| **δ de Borgonovo (given-data)** | Histogramas/KDE + numpy | — | No hay función estándar en scipy; implementar el estimador single-loop `[13][14]` |
| **HSIC** | Matrices de kernel con `numpy` | — | Sin equivalente en scipy; Gretton et al. `[15]`; alternativa R `sensitivity` |
| Regresión logística | `scipy.optimize.minimize` / IRLS con numpy | — | No necesita `scikit-learn` `[22]` |
| Importancia por permutación | Reimplementar con numpy sobre el modelo/salida | — | `sklearn.inspection.permutation_importance` existe `[23]` pero **no es necesario** |
| **Árbol CART** | — | **Sí, `scikit-learn`** (o stump de un corte en numpy) | Único método que hoy pide `scikit-learn` `[25]` |
| Sobol / Saltelli | `scipy.stats.sobol_indices` (SciPy ≥ 1.11) | — | **Exige diseño tipo Saltelli**, no aplica al LHS existente `[5][65]` |
| Morris / DGSM | — | `SALib` (opcional) | Solo si se añade diseño propio `[66]` |
| D-VARS given-data | — | `monaco` (opcional) | Implementa D-VARS sobre datos existentes `[18]` |

**Conclusión de §6:** todo lo recomendado (§1) es calculable con `numpy/scipy/pandas` **salvo CART**, que requiere
`scikit-learn` o una versión mínima de un solo corte. No se necesita `SALib` ni `monaco` para el plan de la §1;
se listan solo como opción si en el futuro se añadiera un diseño Morris/DGSM/VARS propio.

---

## 7. Fuentes

Se marca con **⚠** la que no pudo abrirse completo (solo título/abstract en la búsqueda).

1. Saltelli, A., Aleksankina, K., et al. (2019). *Why so many published sensitivity analyses are false*. EMS 114, 29–39. https://arxiv.org/pdf/1711.11359
2. Morris, M. D. (1991). *Factorial sampling plans for preliminary computational experiments*. Technometrics 33(2). (referencia clásica; ver `[3]`)
3. Campolongo, F., Cariboni, J., Saltelli, A. (2007). *An effective screening design…* EMS 22(10). (referencia clásica)
4. Saltelli, A. (2016). *Sensitivity analysis: Scope and limitations* (lesson). https://www.andreasaltelli.eu/file/repository/Saltelli_Lesson_Sens_Analysis_1.pdf
5. Sobol', I. M. (2001). *Global sensitivity indices for nonlinear mathematical models*. Math. Comp. Sim. 55, 271–280. http://www.andreasaltelli.eu/file/repository/Sobol_2001.pdf
6. Saltelli, A., Annoni, P., et al. (2010). *Variance based sensitivity analysis of model output…* CPC 181(2), 259–270. https://cran.r-project.org/web/packages/sensobol/readme/README.html
7. Saltelli, A., Tarantola, S., Chan, K. P.-S. (1999). *A quantitative model-independent method…* Technometrics 41(1). (referencia clásica)
8. Spear, R. C., Hornberger, G. M. (1980). *Eutrophication in Peel Inlet—II…* Water Research 14(1), 43–49. https://www.ecmwf.int/sites/default/files/elibrary/2004/14102-issues-uncertainty-estimation-hydrologic-modeling-use-ensemble-approaches.pdf
9. van Griensven, A., et al. (2006). *A global sensitivity analysis tool…* J. Hydrology. https://ssl.tamu.edu/media/11571/ann-globalsensitivity-j.hydrology-2006.pdf
10. Plischke, E., Borgonovo, E., Smith, C. L. (2013). *Global sensitivity measures from given data*. EJOR 226(3), 536–550. https://ideas.repec.org/a/eee/ejores/v226y2013i3p536-550.html
11. Pianosi, F., Wagener, T. (2015). *A simple and efficient method for GSA based on CDFs (PAWN)*. EMS 67, 1–11. https://www.sciencedirect.com/science/article/pii/S1364815215000237 **⚠**
12. Pianosi, F., et al. (2016). *Sensitivity analysis of environmental models…* EMS 79, 214–232. https://pmc.ncbi.nlm.nih.gov/articles/PMC6812336
13. Borgonovo, E. (2007). *A new uncertainty importance measure*. RESS 92(6), 771–784. https://didattica.unibocconi.it/mypage/upload/49434_20120425_044522_MOMENT_INDEP_UNCERT_IMP_2.PDF
14. Borgonovo, E., Hazen, G. B., Plischke, E. (2016). *A Common Rationale for GSA and Their Estimation*. Risk Analysis 36(10), 1871–1895. https://www-10b015.pages.gwdg.de/papers/CommonRationale_ESREL2013.pdf
15. Gretton, A., Bousquet, O., Smola, A., Schölkopf, B. (2005). *Measuring statistical dependence with Hilbert-Schmidt norms*. ALT 2005. https://link.springer.com/chapter/10.1007/11564089_7 **⚠**
16. *R: Sensitivity Indices based on the HSIC (`sensiHSIC`)*, paquete `sensitivity`. https://search.r-project.org/CRAN/refmans/sensitivity/help/sensiHSIC.html
17. Marino, S., et al. (2008). *A methodology for performing global uncertainty and sensitivity analysis…* JTB 254(1), 178–196. (referencia clásica)
18. Shambaugh (2022). *Monaco: A Monte Carlo Library for UA/SA*. SciPy Proceedings. https://proceedings.scipy.org/articles/majora-212e5952-024
19. Razavi, S., Gupta, H. V. (2016) / Sheikholeslami & Razavi (2020). *VARS-TO / D-VARS*. (citados en `[18]`)
20. Kucherenko, S., et al. (2016). *Quantile based global sensitivity measures*. arXiv. https://arxiv.org/pdf/1608.02221
21. *Efectos de Shapley* (revisión y comparación). https://arxiv.org/html/2506.11471
22. *Logistic regression from scratch (NumPy)* — implementación de referencia. https://github.com/asteriscuz/logistic-regression-scratch
23. scikit-learn. *Permutation feature importance*. https://scikit-learn.org/stable/modules/permutation_importance.html
24. Hooker, G., Mentch, L. (2019). *Please Stop Permuting Features*. arXiv. https://arxiv.org/pdf/1905.03151v1
25. scikit-learn. `sklearn.inspection.permutation_importance` (y modelos de árbol). https://scikit-learn.org/1.1/modules/generated/sklearn.inspection.permutation_importance.html
26. Saltelli, A., Marivoet, J. / Hora & Helton (2003) (PRCC, monótono) — citados en `[13]`.
27. *Global Sensitivity Analysis* (nota de clase; §6.8: salida Bernoulli q=1(G(x))). https://simcenter.designsafe-ci.org/media/filer_public/eb/a1/eba14491-7342-48ee-a444-14feb6ff8312/3sensitivity_lecture_note.pdf
28. Wong, C. Y., Seshadri, P., Parks, G. (2019/2020). *Extremum Sensitivity Analysis with Polynomial Monte Carlo Filtering*. arXiv. https://arxiv.org/abs/1907.08113v3
29. Puy, A., et al. *sensobol* (parámetro dummy / piso de ruido). https://cran.r-project.org/web/packages/sensobol/readme/README.html
30. Nguyen, T.-V., Knudsen, T., Larsen, U., Haglind, F. (2014). *Thermodynamic evaluation of the Kalina split-cycle concepts*. Energy 71. https://backend.orbit.dtu.dk/ws/portalfiles/portal/93006213/Thermodynamic_evaluation_postprint.pdf (y `Papers/Thermodynamic_evaluation_postprint.pdf`)
31. Dubey, A. M., Sharma, M. (2021). *High-efficiency thermodynamic cycles for Kalina power generation systems: A comprehensive review*. IOP Conf. Ser. 1168, 012030. https://iopscience.iop.org/article/10.1088/1757-899X/1168/1/012030/pdf
32. *A review of research on the Kalina cycle* (2012). Renewable and Sustainable Energy Reviews. https://doi.org/10.1016/j.rser.2012.05.040 **⚠**
33. Elsayed, A., et al. (2013). *Thermodynamic performance of Kalina cycle system 11 (KCS11)*. IJLCT 8(suppl.1), i69. https://academic.oup.com/ijlct/article/8/suppl_1/i69/770890 (y `Papers/ctt020.pdf`)
34. Hettiarachchi, H. M. D., et al. (2007). *The Performance of KCS-11 With Low-Temperature Heat Sources*. ASME JERT 129(3), 243. https://asmedigitalcollection.asme.org/energyresources/article/129/3/243/447549 **⚠**
35. *Kalina Cycle — an overview*. ScienceDirect Topics. https://www.sciencedirect.com/topics/engineering/kalina-cycle
36. *Thermodynamics Analysis of KCS-11 for Jailolo Geothermal Field* (2020/2021). WGC. http://www.geothermal-energy.org/pdf/IGAstandard/WGC/2020/26043.pdf
37. *Performance analysis and optimum ammonia-water concentration of basic Kalina cycle* (2025). Results in Engineering 26, 104887. https://www.sciencedirect.com/science/article/pii/S2590123025009636 **⚠**
38. *Optimization of the KCS34 based on the addition of a second vapor-liquid separator* (2025). Energy. https://www.sciencedirect.com/science/article/pii/S0360544225028944 **⚠**
39. *Comparative Analysis of Kalina Cycle Configurations…* (2025). IJCCE 44(5). https://www.ijcce.ac.ir/article_722352_8694e1fe0f1f49dd595b1daea22525d2.pdf
40. *Performance Improvement of KCS-34…* (2021). Frontiers in Energy Research. https://www.frontiersin.org/journals/energy-research/articles/10.3389/fenrg.2021.741704/full
41. *Notes from the North: … 2 MW Kalina Cycle Geothermal Power Plant in Húsavík* (2002). GRC. https://www.oh.is/static/files/Skyrslur_og_greinar/Enskar/Notes_from_the_North.pdf
42. Nasruddin, et al. (2009). *Energy and exergy analysis of KCS34…* J. Mech. Sci. Tech. https://link.springer.com/article/10.1007/s12206-009-0617-8 **⚠**
43. Yanagisawa, et al. (2012). *Starting Field Test of Kalina System using Hot Spring Fluid in Japan*. Stanford. https://pangea.stanford.edu/ERE/pdf/IGAstandard/SGW/2012/Yanagisawa.pdf
44. IAPWS G4-01 (2001) / Tillner-Roth & Friend (1998) — rango de validez (documento local `reference/IAPWS_G4-01_nh3h2o.pdf`; ver también `CONTEXT.md`).
45. Saltelli, A., Annoni, P. (2010). *How to avoid a perfunctory sensitivity analysis*. EMS 25, 1508–1517. (citado en `[4]`)
46. Saltelli, A., et al. (2008). *Global Sensitivity Analysis. The Primer*. Wiley. https://www.andreasaltelli.eu/file/repository/A_Saltelli_..._Global_Sensitivity_Analysis_The_Primer_Wiley_Interscience_2008_.pdf
47. JRC (2020). *Uncertainty and Sensitivity Analysis for policy decision making*. https://publications.jrc.ec.europa.eu/repository/bitstream/JRC122132/kj-na-30432-en-n.pdf
48. Desideri, A., et al. (2014). *ThermoCycle: A Modelica library for the simulation of thermodynamic systems*. https://ep.liu.se/ecp/096/072/ecp14096072.pdf
49. Coit, D. W., Smith, A. E. (1998). *Adaptive penalty methods for genetic optimization of constrained combinatorial problems*. https://www.eng.auburn.edu/~smithae/files/orsa.pdf
50. Richardson, J. T., et al. (1989) (penalización basada en distancia a la factibilidad) — citado en `[49][51]`.
51. Collange, G., et al. (2010). *Multidisciplinary Optimization…* (valores de restricción ε-normalizados). http://www.cmap.polytechnique.fr/~nikolaus.hansen/collange2010Chap12.pdf
52. MATLAB. *infeasibility — Constraint violation at a point*. https://www.mathworks.com/help/optim/ug/optim.problemdef.optimizationconstraint.infeasibility.html
53. Chinneck, J. (2008). *Irreducible Infeasible Sets (IIS)* — citado en https://pmc.ncbi.nlm.nih.gov/articles/PMC10495685
54. *A Review on the Preliminary Design of Axial and Radial Turbines for Small-Scale ORC* (2023). Energies 16(8), 3423. https://www.mdpi.com/1996-1073/16/8/3423
55. *Design Method and Performance Prediction for Radial-Inflow Turbines of High-Temperature Mini-ORC* (2019). ASME JGT. https://asmedigitalcollection.asme.org/gasturbinespower/article/141/9/091021/955379 **⚠**
56. Capata, R., Pantano, F. (2020). *Expander design procedures and selection criterion for small rated ORC*. Energy Sci. Eng. https://scijournals.onlinelibrary.wiley.com/doi/10.1002/ese3.710
57. Jeannot, et al. (2021). *Thermodynamic Evaluation of a Solar Based Kalina Cycle*. IEOM. (documento local `Papers/evalaucion_termica_solar.pdf`; calidad mínima de turbina 0.90, η_t 82 %)
58. *LMTD vs. ε–NTU Method for Heat Exchanger Analysis*. https://cfdland.com/lmtd-vs-%CE%B5-ntu-method-for-heat-exchanger-analysis-comprehensive-guide
59. Nigro (2022). *Performance comparison between Kalina Cycle and ORC for waste heat recovery*. PoliMi. https://www.politesi.polimi.it/retrieve/ba56b848-7e0c-4f1d-ad97-dfea6d099036/2022_12_Nigro.pdf
60. *Why Kalina (Ammonia-Water) cycle rather than steam Rankine…* (2022). Energy Conv. Manag. https://www.sciencedirect.com/science/article/pii/S0196890422005350 **⚠**
61. Fronk, B. M. *Evaluation of heat and mass transfer models for sizing low-temperature Kalina cycle microchannel condensers*. ASME JERT (año no confirmado). https://ir.library.oregonstate.edu/downloads/tm70n254s
62. Henshaw, T. *Understanding NPSH & Cavitation*. Pumps & Systems (2018). https://www.pumpsandsystems.com/wp-content/uploads/sites/default/files/NPSH%20ebook-2018.pdf
63. Wassgren, C. *Pumps – Net Positive Suction Head* (notas ME30800, Purdue). https://engineering.purdue.edu/~wassgren/teaching/ME30800/NotesAndReading/Pumps_NPSH_LectureNotes.pdf
64. Creare. *Two-phase pumped ammonia loop — pump with NPSHR ≈ 0*. https://ttu-ir.tdl.org/server/api/core/bitstreams/5cce0c52-d4ca-4828-ab8a-9861f803e69c/content
65. SciPy 1.11.0 Release Notes — `scipy.stats.sobol_indices`. https://docs.scipy.org/doc/scipy-1.13.0/release/1.11.0-notes.html
66. SALib (Python) — Morris, DGSM, Sobol. https://salib.readthedocs.io/ **⚠ (no abierto en esta búsqueda; documentación de conocimiento general, marcar para verificación)**
67. *Notes on the vapor-liquid equilibrium / separador* — `Papers/resumen_utilidad_papers_kalina.md` (resumen local de los PDFs del proyecto).
68. Kalina, A. I., et al. (2003). *New Binary Geothermal Power System*. Stanford IGW2003, W00024. https://pangea.stanford.edu/ERE/pdf/IGAstandard/Russia/IGW2003/W00024.PDF
