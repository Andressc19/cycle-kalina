# Estudio de métodos de análisis de sensibilidad — selección para el ciclo KCS-11

**Fecha:** 2026-10-05 · **Rama:** `test/barrido_final` · **Alimenta a:** `docs/METODOLOGIA_BARRIDOS_FINAL.md` (M3–M4)

## 1. La pregunta que debe responder el análisis

El objetivo de la campaña no es explicar la varianza de η, sino **llegar a KALINA, o quedar lo más
cerca posible, dentro de las restricciones del proyecto** (ε ∈ [0.75, 0.85], η_t/η_p realistas,
piso de O2 = 300.03 K). Por eso el análisis de sensibilidad tiene que responder tres preguntas
concretas:

1. **¿Qué variables deciden si un punto es KALINA o no?** Es una pregunta de factibilidad, y la
   salida es binaria.
2. **¿Hacia dónde hay que mover cada variable?** Hace falta el signo del efecto y el rango favorable.
3. **Entre los puntos que sí funcionan, ¿qué variables mueven η y W_net?** Aquí la salida es continua.

## 2. Rasgos del modelo que condicionan la elección

| Rasgo | Consecuencia para el método |
|---|---|
| ~31 s por punto (teqp + A+B), con ejecución secuencial | El presupuesto realista es de **100–400 puntos** por fase. Cualquier método que pida miles queda fuera |
| Hay **puntos que no convergen** (NO_CONVERGIO) y regiones INVIABLES | En esos puntos no existen η ni márgenes. Los métodos que exigen una salida en todos los puntos (Sobol, FAST, Morris) pierden información |
| La salida principal es **categórica** (KALINA / CORREGIBLE / INVIABLE / NO_CONVERGIO) y tiene fronteras bruscas | Las varianzas y derivadas de la clase no tienen sentido; se necesitan métodos para salidas binarias o basados en distribuciones |
| Detrás de la clase hay **márgenes continuos**: O1 → q4 − 0.90; O2 → T_burbuja(P_baja) − T9; O5 → q2 ∈ (0.001, 0.999); O3 → W_net > 0 | Sobre estos márgenes sí se pueden aplicar métodos continuos, y miden directamente qué tan cerca está un punto de ser KALINA |
| k ≈ 10 variables | Con tan pocas variables no hace falta un cribado previo pensado para decenas o cientos de factores |
| Hay interacciones fuertes ya conocidas (x_b con P_alta; P_baja con ε_cond en O2; T_fuente con la campana) | Un método solo local (OAT) no basta: Saltelli et al. (2019) muestran que el OAT por sí solo subestima las interacciones y no explora el espacio |

## 3. Métodos revisados

### 3.1 Locales

**OAT o derivadas locales (una variable a la vez).** Se mueve una variable con el resto fijo y se
calcula la elasticidad E = (Δη/η)/(Δv/v).
- Costo: n·k puntos; con 15 por variable, 150 puntos.
- A favor: es fácil de leer, coincide con la práctica de la literatura de ciclos Kalina (Elsayed
  2013 y Nguyen 2014 hacen estudios paramétricos de este tipo) y ubica dónde cada variable cruza
  una frontera de clase.
- En contra: solo vale alrededor del punto base, no ve interacciones y cubre una fracción mínima
  del espacio (Saltelli et al., 2019).
- **Veredicto: necesario pero no suficiente.** Se mantiene porque tú lo pediste (15 variaciones) y
  porque marca dónde están las fronteras.

### 3.2 Cribado (screening)

**Morris, efectos elementales** (Morris, 1991; Campolongo et al., 2007). Se construyen r
trayectorias por una malla de p niveles. En cada paso cambia una sola variable, en una cantidad Δ,
y se registra el efecto elemental EE_i = [y(x + Δe_i) − y(x)]/Δ. Con las r trayectorias se obtiene,
para cada variable, μ\* = media de |EE_i| (su importancia global) y σ = desviación de EE_i (su no
linealidad o interacción con otras).
- Costo: r(k+1) puntos; con r = 10 y k = 10, 110 puntos.
- A favor: es barato, sirve como método global y es estándar.
- En contra, en nuestro caso:
  1. Cada efecto elemental necesita **los dos extremos convergidos**. Si una fracción p de los
     puntos no converge, se pierde ~1 − (1 − p)² de los efectos: con p = 0.3, la mitad.
  2. La clase es discontinua, así que un EE de la clase no significa nada. Solo serviría sobre
     η o sobre los márgenes, y justo ahí aparecen los huecos del punto 1.
  3. Está pensado para cribar muchos factores (decenas o cientos). Con 10 aporta poco frente a un
     muestreo LHS del mismo tamaño, que además puede reutilizarse para varios análisis.
  4. Da un ranking, pero **no dice qué valores llevan a KALINA**, que es nuestro objetivo.
- **Veredicto: lo descarto como método principal.** En la propuesta anterior lo había elegido sin
  haber hecho este estudio.

### 3.3 Basados en varianza

**Índices de Sobol** (Sobol', 2001; estimador de Saltelli et al., 2010). Descomponen Var(y) en
índices de primer orden S_i y totales S_Ti.
- Costo: N(k + 2) puntos; con N = 512 y k = 10, unos 6 100 puntos, es decir **~53 h**.
- En contra: exige una salida en **todos** los puntos (los NO_CONVERGIO rompen el estimador), supone
  una salida continua y su costo es prohibitivo.
- **Veredicto: descartado.**

**FAST / eFAST** (Saltelli et al., 1999). Estima los mismos índices con un muestreo por frecuencias.
- Costo: ~1 000–2 000 puntos.
- En contra: tiene los mismos problemas que Sobol con los fallos y con la salida categórica.
- **Veredicto: descartado.**

**Metamodelo + Sobol** (polinomios de caos o procesos gaussianos; Sudret, 2008). Se ajusta un
sustituto barato con 100–300 puntos y sobre él se calcula Sobol.
- En contra: los sustitutos suaves se ajustan mal a fronteras de fase y a regiones sin solución.
- **Veredicto: no ahora.** Solo podría servir para η *dentro* de la región KALINA, como trabajo futuro.

### 3.4 Regresión y correlación sobre un muestreo

**SRC / PRCC** (coeficientes de correlación parcial de rangos; Marino et al., 2008). Se hace un
muestreo LHS (McKay et al., 1979) y se calcula la correlación parcial de rangos entre cada entrada
y la salida, descontando el efecto de las demás.
- Costo: ~100–300 puntos.
- A favor: da el **signo** del efecto (subir o bajar), funciona con relaciones monótonas no
  lineales y puede calcularse solo con los puntos que convergieron.
- En contra: falla si la relación no es monótona.
- **Veredicto: lo adopto como complemento** sobre η y sobre los márgenes.

### 3.5 Basados en distribuciones (moment-independent)

**PAWN** (Pianosi y Wagener, 2015). Compara la distribución acumulada de la salida sin condicionar
con la que resulta al fijar una variable, mediante la distancia de Kolmogorov–Smirnov.
- Costo: funciona con un muestreo ya hecho (versión *given-data*).
- A favor: no supone linealidad ni continuidad y tolera discontinuidades.
- **Veredicto: lo adopto** para η y para el índice de cercanía.

**Análisis regional de sensibilidad (RSA) o filtrado Monte Carlo** (Spear y Hornberger, 1980;
Hornberger y Spear, 1981; Pianosi et al., 2016). Se separa la muestra en puntos que **cumplen** el
comportamiento buscado (KALINA) y puntos que **no** lo cumplen. Para cada variable se comparan sus
distribuciones en los dos grupos con la prueba de KS: si son distintas, esa variable decide la
factibilidad, y la forma de las curvas muestra **qué rango la favorece**.
- Costo: funciona sobre el mismo LHS.
- A favor: está hecho para salidas binarias. **Los NO_CONVERGIO no estorban**, porque simplemente
  caen en el grupo de "no cumple". Responde de forma directa las preguntas 1 y 2 de la §1. Además
  se puede repetir criterio por criterio (¿qué causa O1?, ¿qué causa O2?, ¿qué impide converger?).
- **Veredicto: es el método principal.**

### 3.6 Reglas de clasificación (complemento interpretativo)

**Árbol de decisión CART** (Breiman et al., 1984). Con el mismo LHS se ajusta un árbol que predice
la clase. El resultado son reglas legibles, del tipo "KALINA si P_baja > X y x_b ∈ [a, b]". Es una
manera transparente de describir la región factible y de sugerir hacia dónde mover el diseño.
Necesita `scikit-learn`, que hoy no está instalado.

## 4. Comparación resumida

| Método | Puntos | ¿Tolera fallos? | ¿Sirve con salida categórica? | ¿Dice cómo llegar a KALINA? | Decisión |
|---|---|---|---|---|---|
| OAT 15×k | 150 | Sí | Ubica fronteras | Localmente | **Sí (M3)** |
| Morris | 110–220 | No | No | No | Descartado |
| Sobol | ~6 000 | No | No | No | Descartado |
| eFAST | ~1 500 | No | No | No | Descartado |
| Metamodelo + Sobol | 100–300 | Mal | No | No | Futuro (solo dentro de KALINA) |
| PRCC | LHS compartido | Sí (con los convergidos) | Sobre los márgenes | El signo | **Sí (M4)** |
| PAWN | LHS compartido | Sí | Sí | Parcialmente | **Sí (M4)** |
| **RSA / MC filtering** | LHS compartido | **Sí** | **Sí, es su caso de uso** | **Sí, con el rango favorable** | **Principal (M4)** |
| CART | LHS compartido | Sí | Sí | Sí, con reglas | Opcional (requiere scikit-learn) |

## 5. Método elegido: diseño en tres capas sobre un solo muestreo

**Capa 1 — Local (M3): OAT con 15 puntos por variable** alrededor del ancla A\* obtenida en M2.
- Salidas: la clase, η, W_net y los márgenes de O1, O2 y O5.
- Indicadores: la elasticidad en A\*, el rango de η y el **valor donde la variable cruza cada
  frontera de clase**.

**Capa 2 — Global (M4): un LHS de ~250 puntos** dentro de la caja de rangos realistas (definida
tras M2). Cuesta ~2.2 h. Ese mismo muestreo se analiza de cuatro formas:
1. **RSA (principal):** separa KALINA de no-KALINA y repite la separación por cada criterio
   bloqueante (O1, O2, O5 y convergencia). Para cada variable calcula el estadístico KS y su valor
   p, y traza las CDF de los dos grupos.
2. **PAWN** sobre η (solo los convergidos) y sobre el índice de cercanía D (§6).
3. **PRCC** sobre η y sobre cada margen, para conocer el signo de cada efecto.
4. **CART** (opcional) para obtener reglas de la región KALINA.

**Robustez:** intervalos de confianza por bootstrap (1 000 remuestreos) para KS, PAWN y PRCC, y
una prueba de convergencia que repite los índices con 150 y con 250 puntos. Si el ranking cambia
entre ambas, el muestreo se amplía.

**Capa 3 — Dirigida (M5): búsqueda hacia KALINA.** Partiendo de las reglas y de los rangos que dio
RSA, se refinan los mejores puntos minimizando D y, después, maximizando η entre los KALINA. Si no
existe ningún KALINA dentro de las restricciones, se reporta el punto con la menor D y cuál
criterio sigue bloqueando.

## 6. Índice de cercanía a KALINA (D)

Sirve para que "lo más cercano posible" sea una magnitud medible y no una apreciación. Para cada
punto convergido se calcula:

```
D = v_O1/τ_O1 + v_O2/τ_O2 + v_O5/τ_O5 + v_O3/τ_O3
  v_O1 = max(0, 0.90 − q4)                     [título]
  v_O2 = max(0, T9 − T_burbuja(P_baja, x_b))   [K, a T_amb_diseno = 300.03 K]
  v_O5 = distancia de q2 al intervalo (0.001, 0.999)
  v_O3 = max(0, −W_net)                        [kW]
```

D = 0 cuando se cumplen todos los criterios operativos. Los NO_CONVERGIO no tienen D, pero sí
entran en el RSA.

**Tolerancias aprobadas por el usuario (2026-10-05):** τ_O1 = 0.01 de título, τ_O2 = 1 K,
τ_O5 = 0.01 y τ_O3 = 1 kW. D siempre se reporta junto con el vector completo de violaciones, para
que la elección de τ no oculte cuál criterio falla. El cálculo detallado está en
`docs/MATEMATICA_ITERACIONES_SENSIBILIDAD.md`.

## 7. Implementación

- **Dependencias:** con `scipy` (`stats.qmc.LatinHypercube`, `stats.ks_2samp`, `stats.spearmanr`) y
  `numpy` alcanza para LHS, RSA, PAWN y PRCC. CART usa `scikit-learn` 1.9.1, instalado con permiso
  del usuario el 2026-10-05 y fijado en `requirements.txt`. `SALib` no se usa.
- **Márgenes:** se calculan en `scripts/` a partir del resultado del solver, con `backend.fase_de`
  y `backend.bubble_point`, igual que lo hace `operativos.py`. **No se toca `src/`.**
- **Muestreo reproducible:** LHS con una semilla fija que queda anotada en `M0_protocolo`.

## Referencias

- Breiman, L., Friedman, J. H., Olshen, R. A., & Stone, C. J. (1984). *Classification and regression trees*. Wadsworth.
- Campolongo, F., Cariboni, J., & Saltelli, A. (2007). An effective screening design for sensitivity analysis of large models. *Environmental Modelling & Software, 22*(10), 1509–1518.
- Hornberger, G. M., & Spear, R. C. (1981). An approach to the preliminary analysis of environmental systems. *Journal of Environmental Management, 12*(1), 7–18.
- Marino, S., Hogue, I. B., Ray, C. J., & Kirschner, D. E. (2008). A methodology for performing global uncertainty and sensitivity analysis in systems biology. *Journal of Theoretical Biology, 254*(1), 178–196.
- McKay, M. D., Beckman, R. J., & Conover, W. J. (1979). A comparison of three methods for selecting values of input variables in the analysis of output from a computer code. *Technometrics, 21*(2), 239–245.
- Morris, M. D. (1991). Factorial sampling plans for preliminary computational experiments. *Technometrics, 33*(2), 161–174.
- Pianosi, F., & Wagener, T. (2015). A simple and efficient method for global sensitivity analysis based on cumulative distribution functions. *Environmental Modelling & Software, 67*, 1–11.
- Pianosi, F., Beven, K., Freer, J., Hall, J. W., Rougier, J., Stephenson, D. B., & Wagener, T. (2016). Sensitivity analysis of environmental models: A systematic review with practical workflow. *Environmental Modelling & Software, 79*, 214–232.
- Saltelli, A., Tarantola, S., & Chan, K. P.-S. (1999). A quantitative model-independent method for global sensitivity analysis of model output. *Technometrics, 41*(1), 39–56.
- Saltelli, A., Annoni, P., Azzini, I., Campolongo, F., Ratto, M., & Tarantola, S. (2010). Variance based sensitivity analysis of model output. Design and estimator for the total sensitivity index. *Computer Physics Communications, 181*(2), 259–270.
- Saltelli, A., Aleksankina, K., Becker, W., Fennell, P., Ferretti, F., Holst, N., Li, S., & Wu, Q. (2019). Why so many published sensitivity analyses are false: A systematic review of sensitivity analysis practices. *Environmental Modelling & Software, 114*, 29–39.
- Sobol', I. M. (2001). Global sensitivity indices for nonlinear mathematical models and their Monte Carlo estimates. *Mathematics and Computers in Simulation, 55*(1–3), 271–280.
- Spear, R. C., & Hornberger, G. M. (1980). Eutrophication in Peel Inlet—II. Identification of critical uncertainties via generalized sensitivity analysis. *Water Research, 14*(1), 43–49.
- Sudret, B. (2008). Global sensitivity analysis using polynomial chaos expansions. *Reliability Engineering & System Safety, 93*(7), 964–979.
