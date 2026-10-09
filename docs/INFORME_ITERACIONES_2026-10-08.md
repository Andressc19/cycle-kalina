# Informe de iteraciones y conclusiones — 7 (noche) y 8 de octubre de 2026

**Rama:** `test/barrido_final` · **Informes previos:** `docs/INFORME_ITERACIONES_2026-10-06.md` y
`docs/INFORME_ITERACIONES_2026-10-07.md`.
**Motor:** solo teqp, con la protección A+B, MA y la marca de rango. Los KALINA se verificaron con
el motor riguroso (B).
**Ejecución:** OpenCode (corridas 064–069). Claude vigiló en vivo y auditó contra los CSV.
**Incidente:** el 7-oct por la noche se cayó internet a mitad de M7. M7 se **retomó** el 8-oct
desde donde quedó: los scripts ya estaban escritos y faltaban el verificador, la prueba de humo y
la corrida. No se perdió ningún resultado guardado.

## 1. Trabajo realizado

| Paso | Qué | Puntos | Commit |
|---|---|---|---|
| Excel M5 | Hojas de M5 (49 hojas) | — | `9f04ed5` |
| **M5c** | Malla fina con las presiones del profesor (3000/400 kPa) | 165 | `9aa8657` |
| **M4c** | Techo de P_baja (de 1500 a 2500 kPa) | 150 | `9aa8657` |
| **M7** | Optimización de η (búsqueda por patrones, 5 arranques) | ≈ 600 evaluaciones | `84dde45` |
| **M8** | ANECDÓTICO: η y ε de 0.20 a 0.99 | 160 | `0c01a19` |
| Excel | Hojas de M5c, M4c, M7 y M8 | — | (en curso al redactar) |

Acumulado de la campaña: **≈ 3250 evaluaciones**.

## 2. M5c — franja KALINA con las presiones del profesor

**Procedimiento.**
- Se fijan P_alta = 3000 kPa, P_baja = 400 kPa, x_b = 0.50, η_t = 0.85, η_p = 0.75,
  ε_HRVG = 0.85 y ε_reg = 0.75.
- Malla completa: T_fuente 385–410 K (11 valores) × ε_cond {0.85, 0.875, 0.90, 0.925, 0.95} ×
  T_sumidero {278.15, 290.65, 300.03} K.
- Piso de O2 = T_sumidero.

**Resultados:** 104 de 165 puntos son KALINA.

| T_sumidero | ε_cond | T_fuente con KALINA | η máx. |
|---|---|---|---|
| 278.15 K (5 °C) | 0.85 | 390–407.5 K | 9.8 % |
| 278.15 K | 0.875–0.95 | 390 → ≥ 410 K | 9.8–10.1 % |
| 290.65 K (17.5 °C) | 0.85 | 390–407.5 K | 10.4 % |
| 290.65 K | 0.875–0.95 | 390 → ≥ 410 K | 10.4–10.7 % |
| 300.03 K (profesor) | 0.85 | — | — |
| 300.03 K | 0.875 | 390 K | 2.5 % |
| 300.03 K | 0.90 | 390–392.5 K | 5.0 % |
| 300.03 K | 0.925 | 390–397.5 K | 7.9 % |
| 300.03 K | 0.95 | 390 → ≥ 410 K | **10.8 %** |

**Deducciones.**
1. **El borde inferior está en ≈ 390 K.** Por debajo, el ciclo no da trabajo (O3) o aparecen
   puntos fijos espurios (N2).
2. **Con el clima del profesor, el borde superior lo fija O2**, y sube cuanto mejor es el
   condensador.
3. **Con un sumidero frío, la malla no alcanza el techo** (≥ 410 K).
4. **Con las presiones del profesor y su clima hace falta ε_cond ≥ 0.875.** Para un rango útil,
   0.925–0.95.

## 3. M4c — techo de P_baja

**Procedimiento.**
- LHS de 150 puntos (`seed = 20261008`) en la caja de M4, con P_baja entre 1500 y 2500 kPa.
- Se omite el punto si P_baja ≥ P_alta − 300 (15 omitidos).
- Piso de O2 = T_sumidero.

**Resultados:** 75 KALINA, 43 CORREGIBLE (todos por O2), 2 INVIABLE y 15 NO_CONVERGIO.

| P_baja (kPa) | % KALINA |
|---|---|
| 1300–1400 (M4 + M4b) | 35.7 % |
| 1400–1500 (M4 + M4b) | 50.0 % |
| 1500–1600 | 33.3 % |
| 1600–1700 | 53.3 % |
| 1700–1800 | 50.0 % |
| 1800–1900 | 66.7 % |
| 1900–2000 | 69.2 % |
| 2000–2100 | 61.5 % |
| 2100–2200 | 50.0 % |
| 2200–2300 | 35.7 % |
| 2300–2400 | 70.0 % |
| 2400–2500 | 75.0 % |

- rP de los KALINA de M4c: 1.16–3.04.
- η de los KALINA: mínima 0.27 %, mediana 4.35 %, máxima 8.35 %.
- 30 de los 75 están fuera de rango. 74 de 75 tienen B verificado; el de P_baja = 2494.5 kPa
  falló por 2.02 kJ/kg, contra un umbral de 2.0.

**Deducciones.**
1. **No hay techo de clasificación hasta 2500 kPa.**
2. **El techo de P_baja es estructural (rP > ~1.2) y de eficiencia**, no de cavitación.
3. **Ventana completa de P_baja:** piso de ≈ 550 kPa (O2) y techo práctico fijado por rP y η.

## 4. M7 — optimización de η

**Método.** Búsqueda por patrones sobre las variables libres normalizadas:
- paso inicial del 10 % del rango, que se divide a la mitad cuando ningún vecino mejora;
- objetivo lexicográfico: primero D (llegar a KALINA) y después −η;
- como máximo 120 evaluaciones por arranque;
- caja: T_fuente 380–500 K, T_sumidero 278–303.5 K, P_alta 2000–5000 kPa,
  P_baja 300–2500 kPa, x_b 0.50–0.85, η y ε 0.40–0.95.

**Resultados:**

| Arranque | Se conserva del profesor | η inicial → óptima | Óptimo | Márgenes (O1 / O2 / O5) | Rango confiable |
|---|---|---|---|---|---|
| A1 | nada | 12.30 → **14.98 %** | T_f 436, T_s 279.1, P_alta 4382, P_baja 808, x_b 0.705, η_t 0.95, η_p 0.75, ε_HRVG 0.68, ε_reg 0.94, ε_cond 0.84 | 0.018 / 0.42 K / 0.478 | sí |
| A2 | nada (parte de M2S B2; el óptimo se quedó en P_alta 3000, P_baja 394 y 5 °C) | 11.91 → **15.48 %** | T_f 420, η_t 0.95, ε_reg 0.95 (resto de la base) | 0.005 / 3.81 K / 0.253 | sí |
| A3 | T_fuente 623.15 + T_sumidero 300.03 | 9.29 → **12.74 %** | P_alta 5000, P_baja 1360, x_b 0.85, η_t 0.95, η_p 0.84, ε_HRVG 0.50, ε_reg 0.92, ε_cond 0.95 | 0.031 / 3.81 K / 0.264 | sí |
| A4 | P_alta 3000 + P_baja 400 + T_sumidero 300.03 | 9.50 → **15.60 %** | T_f 415, η_t 0.95, η_p 0.81, ε_HRVG 0.95, ε_reg 0.95, ε_cond 0.95 (x_b 0.50) | 0.006 / 0.12 K / 0.246 | sí |
| A5 | T_fuente 623.15 + x_b 0.50 | 8.46 → **11.09 %** | T_s 302.6, P_alta 4808, P_baja 1022, η_t 0.92, η_p 0.58, ε_HRVG 0.46, ε_reg 0.69, ε_cond 0.88 | 0.001 / 5.66 K / 0.488 | **no** |

Todos los óptimos tienen `B_verificado = True`.

**Deducciones.**
1. **η máx. ≈ 15–15.6 % dentro de los límites del proyecto.** Se alcanza incluso **conservando
   las presiones y el clima del profesor** (A4), si la fuente es de ~415 K.
2. **Con las temperaturas del profesor (623 K) el máximo es ≈ 12.7 %**, con P_alta y x_b altos y
   ε_HRVG ≈ 0.5.
3. **El optimizador empuja η_t, ε_reg y ε_cond al tope (0.95)**, y P_alta y x_b a sus bordes.
   El óptimo real podría estar fuera de la caja. **Son máximos acotados, no diseños robustos.**
4. **Varios óptimos quedan al filo de O1/O2** (A4: 0.12 K de O2 y 0.006 de título; A1: 0.42 K;
   A5: 0.001 de título). Para un diseño real conviene retroceder, subiendo P_baja.

## 5. M8 — ANECDÓTICO: η y ε de 0.20 a 0.99

> No son resultados de diseño: los valores fuera de [0.40, 0.95] no son realistas.

**Procedimiento.** OAT de 16 valores por variable (de 0.20 a 0.99) sobre:
- B1 = el ancla (403 K / 564 kPa, clima del profesor);
- B2 = el óptimo A1 de M7.

Son 160 puntos.

**Clase a lo largo del barrido** (de 0.20 a 0.99; K = KALINA, c = CORREGIBLE, i = INVIABLE,
x = no converge o espurio):

| Base | Variable | Secuencia | η KALINA |
|---|---|---|---|
| B1 | η_t | ccccccc**KKKKKKKKK** (KALINA desde 0.70) | 6.8–10.1 % |
| B1 | η_p | c**KKKKKKKKKKKKKKK** (desde 0.25) | 5.9–8.8 % |
| B1 | ε_HRVG | xxi**KKKKKKK**cccccc (0.35–0.85) | 0.7–8.5 % |
| B1 | ε_reg | cccccccc**KKKKKKKK** (desde 0.80) | 9.0–**11.6 %** |
| B1 | ε_cond | iiiicccc**KKKKKKKK** (desde 0.80) | 7.8–8.5 % |
| B2 | η_t | ccccccccxx**KKKKKK** (desde 0.93) | 14.2–15.6 % |
| B2 | η_p | KKKKKxxKKKKKKKKK | 12.8–15.2 % |
| B2 | ε_HRVG | **KKKKKKK**ccccccccc (hasta 0.70) | 10.4–14.7 % |
| B2 | ε_reg | ccccccccccKxxKKK (desde ~0.90) | 14.8–15.2 % |
| B2 | ε_cond | iicccccccxKKKKKK (desde 0.90) | 13.9–14.5 % |

**Lectura anecdótica.**
- Subir ε_reg y η_t por encima de 0.95 seguiría subiendo η (en B1, ε_reg = 0.99 da 11.6 %), pero
  son valores irreales.
- Un ε_HRVG demasiado alto saca al ciclo de KALINA: sobrecalienta la salida del HRVG o rompe O2.
- El óptimo B2 está apoyado en los bordes de η_t, ε_reg y ε_cond, con puntos espurios cerca.

## 5b. M6 — verificación con el motor real y margen de subenfriamiento (O2)

**Procedimiento:**

- Se tomaron 12 puntos finales: el ancla, M2, M5c, los 5 óptimos de M7, M4b, M4c y M2R.
- Cada uno se evaluó con teqp y con el motor real. Además, con teqp:
  - con el piso de 30.4 °C que trae el código por defecto;
  - con una bisección de P_baja para tener 2 K y 5 K de subenfriamiento.

**Resultados:**

- **teqp coincide con el motor real.** Con 300 s, el motor real solo terminó 2 de los 12 puntos; los
  otros 10 se cortaron por el límite de tiempo, no por la física. En M9, con 1500 s, convergieron
  el ancla, A4 y Húsavík. Los 5 puntos convergidos son todos KALINA en los dos motores, con
  |Δη| ≤ 0.003 pp.
- **O2 no tiene margen propio de subenfriamiento.** El código exige T9 ≤ T_burbuja al piso, es
  decir, ≥ 0 K. Varios puntos quedan con 0.04–0.4 K. Con el piso de 30.4 °C, 9 de 12 pasan a
  CORREGIBLE.
- **El costo de un margen real es bajo:**

  | Margen | P_baja adicional | Pérdida de η |
  |---|---|---|
  | 2 K | +25–46 kPa | −0.3 a −0.5 pp |
  | 5 K | +19–116 kPa | −0.3 a −1.2 pp |

  Con las presiones del profesor, 2 K de margen piden 400 → ~425 kPa. Esto no cambia de forma
  material ningún rango KALINA. La bisección del óptimo A1 no es confiable, porque tiene un hueco
  NO_CONVERGIO.

## 5c. M9 — escalera de conservación de los datos del profesor + Húsavík

**Pregunta (planteada por el usuario):** si se conserva solo un grupo de los datos del profesor y
se libera el resto, ¿hay KALINA? ¿Y si se van sumando grupos?

**Procedimiento:**

- 6 grupos: T_fuente, las η/ε, P_alta, P_baja, T_sumidero y x_b.
- Paso 1: 100 puntos LHS por grupo conservado.
- Paso 2: al grupo con más KALINA confiables (dentro de rango y verificados con B) se le suma cada
  uno de los demás, con 30 puntos por conjunto.
- Tope de ~4 h para el paso 1 y la ronda 1. El 9 de octubre se completaron las rondas 2 y 3, también
  con 30 puntos por conjunto: la escalera tiene 4 rondas y 18 conjuntos.

**Resultados:**

| Se conserva | KALINA | Confiables |
|---|---|---|
| x_b = 0.50 | 29/100 | **15** |
| T_sumidero = 300 K | 17/100 | 13 |
| P_alta = 3000 kPa | 19/100 | 12 |
| las η/ε (0.85/0.75/0.85/0.75/0.80) | 13/100 | 11 |
| P_baja = 400 kPa | 1/100 | 1 |
| T_fuente = 623 K | 7/100 | **0** |
| x_b + P_alta | 11/30 | 7 |
| x_b + las η/ε (6 de 11 datos) | 11/30 | 6 |
| x_b + T_sumidero | 9/30 | 5 |
| x_b + P_baja | 4/30 | 3 |
| x_b + T_fuente | 2/30 | 0 |
| x_b + P_alta + las η/ε (7 datos) | 13/30 | 7 |
| x_b + P_alta + T_sumidero | 8/30 | 6 |
| x_b + P_alta + P_baja | 2/30 | 2 |
| x_b + P_alta + T_fuente | 3/30 | 0 |
| **x_b + P_alta + η/ε + P_baja (8 de 10 datos)** | **5/30** | **5** |
| x_b + P_alta + η/ε + T_sumidero (8 de 10) | 6/30 | 4 |
| x_b + P_alta + η/ε + T_fuente (8 de 10) | 0/30 (30 NO_CONVERGIO) | 0 |

**Final de la escalera:** se conservan **8 de los 10 datos de diseño del profesor**: sus 2
presiones, x_b y las 5 η/ε. Hay que mover solo T_fuente (**391–409 K**) y T_sumidero (**280–293 K**).
Los 5 KALINA son confiables, con η de hasta 10.6 % y ≥ 2 K de subenfriamiento.

Con su clima (300 K) en lugar de P_baja también hay KALINA: T_fuente 392–417 K y P_baja 587–1660 kPa.
Su fuente de 623 K bloquea siempre: es el mismo modo de fallo que el punto original.

Rangos con x_b + P_alta: P_baja 545–1850 kPa, rP 1.6–5.5, T_fuente 391–483 K.

**Húsavík:** con su piso de diseño (10 °C), la P_baja mínima KALINA es **690 kPa, exactamente su
valor real**; η = 12.7 %. El motor real lo confirma (KALINA, Δη −0.002 pp).

**Deducción:** la planta real cae justo en el borde de cavitación de nuestra ventana KALINA. Eso
respalda tanto el criterio O2 como el mapa.

## 6. Conclusiones (acumuladas)

1. **Región KALINA:**
   - P_baja ≈ 550 kPa (piso por O2) hasta un techo práctico fijado por rP ≳ 1.2 y por η;
   - rP ≈ 1.7–5.3 en el mapa global, creciente con P_alta;
   - T_fuente ≈ 384–486 K;
   - ε_cond ≥ 0.74;
   - x_b ≈ 0.51–0.82;
   - un sumidero frío amplía la región.
2. **Datos del profesor que se pueden conservar:**
   - **sus presiones (3000/400 kPa)**, con T_fuente ≈ 390–410 K o más y ε_cond ≥ 0.875 (con su
     clima, ≥ 0.925 para un rango útil);
   - **sus temperaturas**, con ε_HRVG ≈ 0.5, P_baja alta y ε_cond alto;
   - **su fuente y su x_b**, con P_baja de ~900–1800 kPa (fuera de rango).
   - **Escalera M9 completa:**
     - sus 2 presiones, x_b y las η/ε (8 de 10 datos) son compatibles con KALINA si
       T_fuente ≈ 391–409 K y T_sumidero ≤ ~293 K;
     - con su clima de 300 K hace falta, además, ε_cond ≥ 0.875 (M5c).
   - **Consolidado M2 + M5c + M9:**
     - se pueden conservar **9 de sus 11 datos**: todo salvo T_fuente y P_baja (M2), o todo salvo
       T_fuente y ε_cond (M5c);
     - el único dato que **no se sostiene con confianza** es **T_fuente = 623 K**: sus KALINA
       quedan todos fuera del rango confiable;
     - P_baja = 400 kPa es el segundo más restrictivo;
     - x_b, P_alta, T_sumidero y las η/ε se conservan sin problema.
3. **Eficiencia máxima dentro de los límites del proyecto: ≈ 15–15.6 %.** Conservando las
   temperaturas del profesor: ≈ 12.7 %.
4. **El criterio limitante en todo el estudio es O2** (cavitación); con rP alta también O1.
   Conviene reportar los rangos con ~2 K de subenfriamiento: P_baja_min sube unos 25–45 kPa.
5. **Validación externa:** Húsavík cae en el borde de la ventana KALINA con su P_baja real, y teqp
   coincide con el motor riguroso en los 5 puntos convergidos.

## 7. Lo que no se sabe

- El techo de T_fuente con las presiones del profesor y un sumidero frío (≥ 410 K, fuera de la
  malla).
- Los óptimos de M7 son locales y están en los bordes de la caja.
- Hay muchos estados con fuente caliente fuera del rango experimental del modelo.
- Las diferencias de η menores que 0.4–0.7 pp no son concluyentes.

## 8. Archivos

`resultados/2026-10-07_final_M5c/`, `..._M4c/`, `..._M7/`, `..._M8_anecdotico/`,
`resultados/2026-10-08_final_M6/` y `..._M9/` (CSV, PNG y `REPORTE_*.md`). Excel:
`datos/Excel_final_kalina.xlsx` (72 hojas). Protocolos en `prompts/TASK_CONTEXT_final_*.md`.
