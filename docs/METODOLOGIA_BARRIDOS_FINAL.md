# Metodología de barridos y análisis de sensibilidad — campaña final

**Fecha:** 2026-10-05 · **Rama:** `test/barrido_final` · **Estado:** diseño, sin ejecutar.
**Libro de datos:** `datos/Excel_final_kalina.xlsx` (nuevo; el consolidado anterior no se toca).
**Elección del método de sensibilidad:** `docs/ESTUDIO_METODOS_SENSIBILIDAD.md`.
**Fórmulas de cada paso (bisección, OAT, LHS, RSA, PAWN, PRCC, CART, búsqueda dirigida):**
`docs/MATEMATICA_ITERACIONES_SENSIBILIDAD.md`.

**Objetivo de la campaña:** que los barridos lleguen a KALINA o, si dentro de las restricciones no
es posible, al punto más cercano según el índice de cercanía D (estudio, §6). Siempre se indica qué
criterio sigue bloqueando.

Este documento es el protocolo de la campaña. Cada fase tiene una pregunta, un diseño, un criterio de
aceptación y un entregable. Ninguna fase arranca sin la autorización explícita del usuario. Cada
corrida se ejecuta con OpenCode a partir de su `TASK_CONTEXT`, y Claude verifica el resultado antes
de pasar a la fase siguiente.

---

## 0. Decisiones del usuario (2026-10-05)

| Tema | Decisión |
|---|---|
| Reproducibilidad (M1) | Solo se vuelve a correr la **Fase 1 del profesor** (41 puntos) y se compara con la corrida del 2026-09-19 |
| Datos del profesor que se pueden mover (M2) | **Todos**: T_fuente, P_alta, x_b, P_baja, η_t, η_p (las ε solo dentro de [0.75, 0.85]) |
| Piso de cavitación O2 (`T_amb_diseno`) | **300.032917 K** (promedio del perfil horario del enunciado) |
| η_t / η_p | Base 0.85 / 0.75 del profesor; en el barrido se mueven solo dentro de rangos realistas para turbinas y bombas de este tipo de ciclo, con fuente citada en M5 |
| Efectividades | ε_HRVG, ε_reg y ε_cond siempre en [0.75, 0.85]; O2 se cierra con P_baja, nunca subiendo ε |

## 1. Configuración congelada (M0)

Todas las fases usan la misma configuración. Si algo cambia a mitad de la campaña, se reinicia desde M1.

- **Código:** el commit de `master` vigente al arrancar M1 (se anota su hash en la hoja `M0_protocolo`).
- **Motor:** `TeqpVerificado` (protección A) + `verificar_turbina` sobre los KALINA (B) +
  `bracket_tolerante=True` (MA) + marca de rango `motor_rango="teqp"` (IAPWS G4-01 §6).
- **Clasificación:** los 17 criterios vigentes (KALINA / CORREGIBLE / INVIABLE / NO_CONVERGIO) más
  la marca `fuera_rango` como un eje aparte.
- **Base de cálculo:** m_b = 1 kg/s, T0 = 300.032917 K y P0 = 101.325 kPa.
- **Punto del profesor (PP):** P_alta = 3000 kPa, P_baja = 400 kPa, x_b = 0.50, T_fuente = 623.15 K,
  T_sumidero = 300.032917 K, ε = 0.85 / 0.75 / 0.80, η_t = 0.85, η_p = 0.75.
- **Registro:** cada punto guarda en su fila todas las entradas (también las constantes), la clase,
  η, W_net, los márgenes de O1 y O2, el mensaje del clasificador con su sugerencia y las columnas A_* / B_*.

## 2. Fases

### M1 — Reproducibilidad del caso del profesor

- **Pregunta:** ¿el código actualizado (con MA, A+B y la marca de rango) da lo mismo que la corrida
  del 2026-09-19?
- **Diseño:** se repiten exactamente los 41 puntos: el punto base, 9 de P_alta (2000–4000 kPa), 7 de
  x_b (0.40–0.70) y 24 de T_sumidero tomados del perfil horario (`tamb_profesor.csv`).
- **Hipótesis H1:** se vuelven a obtener 41/41 NO_CONVERGIO, con el mismo mecanismo (estado 2 fuera
  de la campana).
- **Criterio de aceptación:** cada punto tiene la misma clase que antes. Si alguno cambia, la
  diferencia se explica antes de seguir: puede ser un efecto de MA o un error.
- **Entregable:** las hojas `M1_profesor_*` y una tabla antes/después.

### M2 — Distancia a Kalina desde el punto del profesor

- **Pregunta:** ¿cuál es el cambio mínimo sobre los datos del profesor que convierte el punto en KALINA?
- **Hipótesis H2:** el bloqueo está en el lado caliente (T2 queda por encima del rocío). Solo las
  variables que mueven T2 o el rocío (T_fuente, P_alta, x_b, ε_HRVG) pueden destrabarlo. Las demás
  (P_baja, η_t, η_p) intervienen después, para cerrar O1 y O2.
- **Diseño por niveles (conservar la mayor cantidad posible de datos del profesor):**
  - Nivel 1: se cambia **una sola** variable.
  - Nivel 2: se cambian pares, solo si el nivel 1 no alcanza.
  - Nivel 3: tríos, solo si el nivel 2 no alcanza.

  La búsqueda se detiene en el primer nivel que da KALINA y se reportan **todas** las soluciones
  de ese nivel. Dentro de cada nivel se prueban primero las variables de diseño (P_alta, P_baja,
  x_b, η_t, η_p) y después las del sitio (T_fuente, T_sumidero). En cada paso:
  1. **Búsqueda 1D por variable** desde PP, con el resto fijo. Primero se localiza la frontera
     NO_CONVERGIO → convergente por bisección y luego la frontera → KALINA.
     - T_fuente: 623.15 K hacia abajo, hasta 380 K.
     - P_alta: 3000 kPa hacia arriba, hasta 10 000 kPa (por encima, `fuera_rango`).
     - x_b: 0.50 en ambos sentidos, 0.30–0.85.
     - ε_HRVG: solo 0.75–0.85, para mostrar que dentro del rango realista no alcanza.
  2. **Combinaciones de 2 variables** entre las que sí destraban, en una malla gruesa de 7×7: por
     ejemplo T_fuente×P_alta y T_fuente×x_b.
  3. **Cierre de O1/O2** sobre los convergentes, con P_baja (y luego η_t/η_p dentro de su rango
     realista). Se aprovecha la sugerencia que devuelve el clasificador en cada punto CORREGIBLE.
- **Métrica de distancia:** el cambio relativo de cada variable, normalizado por su rango realista:
  d = Σ |Δv| / (v_max − v_min). El **ancla A\*** es el punto KALINA con la menor d.
- **Criterio de aceptación:** existe al menos un punto KALINA, y el ancla A\* está confirmada con el
  motor real (`AmmoniaWaterAdapter`).
- **Entregable:** las hojas `M2_*`, una tabla de "cambio mínimo por variable" y la definición de A\*.
- **Valor académico:** cuantifica cuánto hay que alejarse del enunciado para que un KCS-11 a ~3 MPa
  funcione con esa fuente. Contrasta con Nguyen 2014, donde con fuentes de ~350 °C las presiones de
  entrada a turbina son de 100 bar o más.

### M3 — Sensibilidad local alrededor de A\* (OFAT, 15 puntos por variable)

- **Pregunta:** ¿qué variables influyen más en η, en W_net y en la clase?
- **Diseño:** 15 puntos equiespaciados por variable dentro de su rango realista, con el resto en A\*.
  Variables: T_fuente, T_sumidero, P_alta, P_baja, x_b, ε_HRVG, ε_reg, ε_cond, η_t y η_p.
  Son unos 150 puntos.
- **Salidas por punto:** la clase, η, W_net, los márgenes de O1/O2/O5 y el índice de cercanía D.
- **Indicadores:** elasticidad local E = (Δη/η)/(Δv/v) en A\*, la variación total de η en el rango,
  el **valor donde la variable cruza cada frontera de clase** y la pendiente de cada margen.
- **Limitación declarada:** es un análisis local y no capta interacciones (Saltelli et al., 2019);
  por eso M4 es obligatorio.
- **Criterio de aceptación:** un ranking de variables, con las diferencias menores a la banda de
  incertidumbre (±0.4–0.7 pp) marcadas como no concluyentes.
- **Entregable:** las hojas `M3_OFAT_<variable>` y un gráfico tornado.

### M4 — Sensibilidad global orientada a KALINA (LHS + RSA)

Se descartó Morris: pierde los efectos que caen en puntos NO_CONVERGIO y no indica qué valores
llevan a KALINA. La justificación completa está en el estudio, §3.2.

- **Pregunta:** ¿qué variables deciden que un punto sea KALINA, en qué rango y con qué interacciones?
- **Diseño:** un solo muestreo LHS de ~250 puntos (semilla fija) dentro de la caja de rangos
  realistas definida al terminar M2. Se analiza de cuatro maneras:
  1. **RSA / filtrado Monte Carlo (principal):** KALINA frente a no-KALINA, y por separado cada
     criterio bloqueante (O1, O2, O5, convergencia). Estadístico KS con su valor p y las CDF de cada grupo.
  2. **PAWN** sobre η (solo los convergidos) y sobre el índice de cercanía D.
  3. **PRCC** sobre η y sobre cada margen, para conocer el signo de cada efecto.
  4. **CART** (opcional, requiere `scikit-learn`) para obtener reglas de la región KALINA.
- **Robustez:** bootstrap con 1 000 remuestreos y prueba de convergencia (los índices con 150 y con
  250 puntos). Si el ranking cambia, se amplía el muestreo. Si aparecen pares con interacción
  fuerte, se hacen mallas 2D (7×7) dirigidas sobre esos pares.
- **Criterio de aceptación:** un ranking estable de variables por su efecto sobre la factibilidad,
  con el rango favorable de cada una.
- **Entregable:** las hojas `M4_LHS`, `M4_RSA`, `M4_PAWN_PRCC` (y `M4_malla_<par>` si hacen falta),
  con sus figuras de CDF y tornado.

### M5 — Ventana de diseño: diferenciales recomendados

- **Pregunta:** ¿qué diferenciales de presión y de temperatura conviene usar en este ciclo?
- **Magnitudes:** ΔP = P_alta − P_baja y la razón de presiones P_alta/P_baja; ΔT_fuente−sumidero;
  el margen de subenfriamiento de O2 (T_burbuja(P_baja) − T9); el título de salida de turbina (O1);
  y T_fuente − T2 (approach del HRVG).
- **Diseño:** se reutilizan todos los puntos de M2–M4 y se trazan sobre esas magnitudes. Además se
  hace una **búsqueda dirigida** (capa 3 del estudio): con los rangos favorables del RSA, se refinan
  los mejores puntos minimizando D y, entre los KALINA, maximizando η. La región KALINA se delimita
  y se resume en rangos. Si no existe ningún KALINA dentro de las restricciones, se reporta el punto
  con la menor D y el criterio que lo bloquea.
- **Contraste con la literatura** (todos los PDF están en `Papers/`):
  - Elsayed et al. 2013 / Embaye: P 10–40 bar, x_b 0.55–0.9, η_t = η_p = 0.80, pinch 4 K, título de
    salida de turbina ≥ 0.90.
  - Nguyen et al. 2014: ΔT de recuperadores 5 K, ΔT de condensador 4.5 K, η_bomba 0.70; con fuentes
    calientes, P alta y x alto o P baja y x bajo.
  - Nemati et al. 2017: estados a 5000 kPa.
  - Caso Húsavík (Fase 3).
- **Criterio de aceptación:** cada rango recomendado tiene dos respaldos: el resultado del modelo y
  una fuente. Si una de las dos no lo respalda, se dice explícitamente.
- **Entregable:** la hoja `M5_ventana` y una tabla de recomendaciones con su fuente.

### M6 — Verificación y síntesis

- Confirmar con el motor real los puntos KALINA que quedan a menos de 1 K (o de 0.005 de título)
  de una frontera, más A\* y el mejor punto de M5.
- Aplicar la banda de incertidumbre de η (±0.4–0.7 pp, por G4-01) a todas las comparaciones.
- Escribir el reporte final en lenguaje llano: la pregunta, el método, la tabla, la conclusión, lo
  que no se sabe y lo que sigue.

## 3. Libro `datos/Excel_final_kalina.xlsx`

- Hojas por fase con prefijo (`M0_`, `M1_`, …, `M6_`) y una hoja `Resumen` con el conteo por clase
  de cada fase.
- Se aplica el formato acordado: unidades en los títulos, colores por clase, filtros y una
  descripción al final de cada tabla. Se genera con un consolidador nuevo que reutiliza
  `scripts/formatear_excel_barridos.py`.
- Los CSV de origen van en `resultados/2026-10-XX_final_M<n>/`; el Excel nunca se edita a mano.

## 4. Costo estimado (~31 s/punto con teqp + A+B)

| Fase | Puntos | Tiempo aprox. |
|---|---|---|
| M1 | 41 | 25 min |
| M2 | ~150 | 1 h 20 min |
| M3 | ~150 | 1 h 20 min |
| M4 | ~250 (+ mallas 2D si hacen falta) | 2 h 10 min – 3 h |
| M5 | 0–100 | 0–1 h |
| M6 | ~10 con el motor real | ~1 h |

## 5. Reglas que se mantienen

- Todo el código nuevo va en `scripts/`; `src/` no se toca. Si una fase necesitara cambiar el
  motor, se para y se consulta, y el cambio se hace en una rama aparte.
- Ningún punto se oculta: los NO_CONVERGIO y los `fuera_rango` se reportan igual que el resto.
- Lo que no esté en `CONTEXT.md`, en este protocolo o en los `TASK_CONTEXT` de cada fase se reporta
  como no resuelto; no se inventa.
