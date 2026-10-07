# Informe de iteraciones y conclusiones — 7 de octubre de 2026

**Rama:** `test/barrido_final` · **Libro de datos:** `datos/Excel_final_kalina.xlsx` (43 hojas)
**Informe del día anterior:** `docs/INFORME_ITERACIONES_2026-10-06.md` (M1, M2, M2R, M3, M2S y M4 con 300 puntos)
**Motor:** teqp con la protección A+B, el bracket tolerante MA y la marca de rango G4-01. Todos los
KALINA se verificaron con el motor riguroso (verificación B, `B_verificado = True` en el 100 %).
**Ejecución:** OpenCode (corridas 061–063 y 062 para M5), a partir de un `TASK_CONTEXT` por fase.
Claude vigiló cada corrida en vivo (monitor sobre el disco y el log) y auditó los resultados contra
los CSV.

---

## 0. Cambio de prioridad (decisión del usuario, 7 de octubre)

> Lo que se busca ahora, primordialmente, son **los rangos donde hay KALINA**: qué diferencias de
> presión alta y baja aparecen ahí y cuáles son esas presiones. **La eficiencia se mira después**,
> cuando el rango ya esté determinado. También se buscan las combinaciones en las que **algunos
> datos del profesor (temperaturas o presiones) se conservan** y el ciclo sigue siendo Kalina.

Reglas vigentes:
- η y ε en [0.40, 0.95];
- piso de cavitación O2 = T_sumidero (el clima de cada punto);
- punto genuino = KALINA, CORREGIBLE o INVIABLE (los N2 espurios no cuentan).

## 1. Trabajo del día

| Paso | Qué se hizo | Puntos | Resultado | Commit |
|---|---|---|---|---|
| Informe del 6-oct | Guardado en `docs/INFORME_ITERACIONES_2026-10-06.md` | — | — | `a213cac` |
| **M4b** | M4 ampliado de 300 a 500 puntos LHS; análisis centrado en las presiones | +200 (500 en total) | 121 KALINA; ranking convergido | `d82219b` |
| Excel | Hojas de M2S, M4 (500 puntos), ventanas de presión y figuras | — | 43 hojas | `3272e15` |
| **M5** | 5 escenarios que conservan datos del profesor | 600 | KALINA en los 5 escenarios (S2 y S3 en una franja angosta) | `91082fa` |

Acumulado de la campaña: **≈ 2170 combinaciones evaluadas** (≈ 1370 hasta el 6-oct + 800 hoy).

---

## 2. M4b — ventana de presiones de KALINA

### 2.1 Procedimiento
- **Muestreo:** 200 puntos nuevos con `LatinHypercube(d=10, seed=20261007)`, en la misma caja que
  M4: T_fuente 380–500 K, T_sumidero 278.15–303.55 K, P_alta 2000–5000 kPa, P_baja 300–1500 kPa,
  x_b 0.50–0.85, η_t 0.75–0.92, η_p 0.65–0.90, ε_HRVG 0.60–0.95, ε_reg 0.60–0.95 y
  ε_cond 0.70–0.95.
- **Unión con M4:** 300 + 200 = 500 puntos. Cada mitad es un LHS estricto; la unión, no.
- **Análisis repetido sobre los 500:** RSA (KS), PAWN, PRCC, CART y convergencia.
- **Análisis nuevo de presiones:**
  - el plano P_alta–P_baja por clase;
  - los rangos de P_alta, P_baja, dP y rP;
  - la ventana de presiones por franjas de P_alta, T_fuente y T_sumidero;
  - el criterio que se rompe fuera de la ventana de rP.
- **Tiempo:** 3189 s (53 min) con 7 procesos.

### 2.2 Resultados

**Conteos:** 500 puntos.
- KALINA 121 (24 %), CORREGIBLE 308, NO_CONVERGIO 48 e INVIABLE 23.
- Genuinos: 452. Espurios N2: 13.
- Fuera de rango: 222 en total, 38 de ellos KALINA.

**Convergencia del ranking (300 contra 500 puntos):** ρ(KS de KALINA) = **0.93** y ρ(PRCC de η) =
**0.99**. Ambos superan el criterio de 0.9, así que el ranking ya es estable (con 300 puntos era
0.84).

**Qué decide que el ciclo sea KALINA** (RSA; rango = percentiles 5–95 dentro de KALINA):

| Variable | KS | p | Rango KALINA |
|---|---|---|---|
| P_baja | 0.427 | 1e-15 | **683–1461 kPa** |
| ε_cond | 0.426 | 2e-15 | 0.74–0.95 |
| rP = P_alta/P_baja | 0.353 | 1e-10 | **1.69–5.34** |
| T_fuente | 0.287 | 4e-7 | 384–486 K |
| dT_fs = T_fuente − T_sumidero | 0.248 | 2e-5 | 91–199 K |
| T_sumidero | 0.200 | 1e-3 | 279–302 K |
| x_b | 0.193 | 2e-3 | 0.51–0.82 |
| dP = P_alta − P_baja | 0.138 | 0.05 | 968–3718 kPa (no decisivo) |
| P_alta | 0.130 | 0.08 | 2156–4842 kPa (no decisivo) |
| ε_reg, η_p, η_t, ε_HRVG | ≤ 0.12 | > 0.1 | no decisivos dentro de la caja |

**Rangos de presión dentro de KALINA** (121 puntos):

| Variable | mín | p5 | mediana | p95 | máx |
|---|---|---|---|---|---|
| P_alta (kPa) | 2005 | 2156 | 3571 | 4842 | 4961 |
| P_baja (kPa) | 547 | 683 | 1183 | 1461 | 1493 |
| dP (kPa) | 710 | 968 | 2464 | 3718 | 4117 |
| rP (−) | 1.55 | 1.69 | 3.11 | 5.34 | 8.38 |

**Ventana según P_alta:**

| P_alta (kPa) | n | KALINA | % | P_baja KALINA | dP KALINA | rP KALINA |
|---|---|---|---|---|---|---|
| 2000–2500 | 83 | 18 | 21.7 | 913–1459 | 710–1414 | 1.55–2.35 |
| 2500–3000 | 83 | 16 | 19.3 | 683–1441 | 1123–2184 | 1.78–4.20 |
| 3000–3500 | 84 | 21 | 25.0 | 607–1417 | 1869–2673 | 2.32–5.29 |
| **3500–4000** | 83 | 29 | **34.9** | 547–1480 | 2218–3071 | 2.51–6.49 |
| 4000–4500 | 84 | 18 | 21.4 | 634–1493 | 2550–3764 | 2.75–6.93 |
| 4500–5000 | 83 | 19 | 22.9 | 558–1465 | 3208–4117 | 3.21–8.38 |

**Ventana según T_fuente:**

| T_fuente (K) | KALINA | % | P_baja KALINA | dP KALINA | rP KALINA |
|---|---|---|---|---|---|
| 380–400 | 26 | 31.3 | 668–1471 | 903–3540 | 1.69–5.32 |
| **400–420** | 31 | **36.9** | 547–1461 | 710–4117 | 1.55–8.38 |
| 420–440 | 26 | 31.3 | 634–1493 | 1204–3764 | 1.99–6.93 |
| 440–460 | 19 | 22.6 | 607–1490 | 766–3577 | 1.56–5.29 |
| 460–480 | 8 | 9.8 | 688–1459 | 817–2883 | 1.62–5.19 |
| 480–500 | 11 | 13.1 | 769–1452 | 905–3326 | 1.68–4.16 |

**Ventana según T_sumidero:**

| T_sumidero (K) | KALINA | % | P_baja KALINA | rP KALINA |
|---|---|---|---|---|
| **278.15–284.5** (5–11 °C) | 47 | **37.6** | 558–1493 | 1.56–8.38 |
| 284.5–290.85 | 27 | 21.6 | 547–1467 | 1.68–6.49 |
| 290.85–297.2 | 28 | 22.4 | 607–1490 | 1.55–5.32 |
| 297.2–303.55 (clima del profesor) | 19 | 15.2 | 634–1471 | 1.69–6.93 |

**Qué criterio se rompe** en los genuinos que no son KALINA, según dónde cae rP:

| Zona | Criterios (n) |
|---|---|
| rP por debajo de p5 de KALINA | O2 (7) |
| rP dentro de [p5, p95] | O2 (199), O3 (3), O2+O3 (1), S3 (1) |
| rP por encima de p95 de KALINA | O2 (82), O1+O2 (18), O2+O3 (16), O1 (2), O1+O2+O3 (1), O3 (1) |

**Efecto sobre η (PRCC, secundario):** P_baja −0.66, P_alta +0.58, η_t +0.35, T_fuente +0.28,
x_b +0.26 y ε_reg +0.26.

### 2.3 Deducciones
1. **P_baja tiene un piso de ~550–700 kPa que casi no depende de P_alta.** Por debajo, la bomba
   cavita (O2). Con P_alta baja (2000–2500 kPa), el piso sube a ~900 kPa.
2. **El diferencial de presión no está acotado por sí solo:** dP y rP admisibles crecen con P_alta.
   rP pasa de 1.6–2.4 (P_alta 2–2.5 MPa) a 3.2–8.4 (P_alta 4.5–5 MPa).
3. **Una rP excesiva rompe por expansión:** salida de turbina húmeda (O1) y cavitación (O2).
   Dentro de la ventana de rP, lo que decide es O2, es decir, ε_cond, T_sumidero y P_baja.
4. **La franja más favorable** es P_alta 3500–4000 kPa con T_fuente 400–420 K y un sumidero frío.
5. El techo de P_baja (~1460–1490 kPa) coincide con el borde de la caja (1500 kPa): **no está
   determinado**.

---

## 3. M5 — conservar datos del profesor

### 3.1 Procedimiento
- **Datos del profesor:** T_fuente 623.15 K, T_sumidero 300.032917 K, P_alta 3000 kPa,
  P_baja 400 kPa, x_b 0.50, η_t 0.85, η_p 0.75, ε_HRVG 0.85, ε_reg 0.75 y ε_cond 0.80.
- **5 escenarios:** cada uno fija un subconjunto de esos datos y explora las demás variables con
  un LHS de 120 puntos (`seed = 20261007 + k`). Son 600 corridas con teqp y 7 procesos.
- **Rangos de las variables libres:**
  - P_alta 2000–5000 kPa;
  - P_baja 200–2000 kPa (se amplió porque con 623 K hace falta P_baja alta);
  - T_fuente 380–623.15 K;
  - T_sumidero 278.15–303.55 K;
  - x_b 0.50–0.85;
  - η y ε 0.40–0.95.
- **Restricción:** si P_baja ≥ P_alta − 300 kPa, el punto se omite (2 puntos omitidos).

### 3.2 Resultados

| Escenario | Se conserva del profesor | n | KALINA | Genuinos | N2 | Fuera de rango | Bloqueante |
|---|---|---|---|---|---|---|---|
| **S1** | T_fuente 623.15 + T_sumidero 300.03 | 120 (1 omitido) | **4** | 59 | 2 | 53 | O2 |
| **S2** | P_alta 3000 + P_baja 400 | 120 | 0 en el LHS ¹ | 95 | 2 | 66 | O2 |
| **S3** | P_alta 3000 + P_baja 400 + T_sumidero 300.03 | 120 | 0 en el LHS ¹ | 84 | 6 | 64 | O2 |
| **S4** | P_alta 3000 + T_fuente 623.15 + T_sumidero 300.03 | 120 | **6** | 62 | 2 | 57 | O2 |
| **S5** | T_fuente 623.15 + x_b 0.50 | 120 (1 omitido) | **10** | 82 | 0 | 82 | O2 |

¹ **Nota del director (auditoría).** S2 y S3 **sí son factibles**: M2R ya encontró un KALINA con
exactamente P_alta = 3000, P_baja = 400, T_sumidero = 300.03 y x_b = 0.50, usando
**T_fuente = 403 K y ε_cond = 0.95** (η = 9.50 %, dentro de rango, verificado). Ninguno de los 120
puntos LHS de S3 cayó en esa zona (T_fuente < 420 K con ε_cond > 0.9). Los genuinos más cercanos
del LHS lo confirman:
- S2: D = 0.22 (T_fuente 391 K, T_sumidero 279 K, ε_cond 0.92);
- S3: D = 1.57 (T_fuente 398 K).

**Rangos de las variables libres dentro de KALINA** (percentiles 5–95):

| Escenario | P_alta (kPa) | P_baja (kPa) | rP | dP (kPa) | x_b | ε_HRVG | ε_cond |
|---|---|---|---|---|---|---|---|
| S1 | 2268–4598 | **1394–1953** | 1.37–2.82 | 620–2796 | 0.58–0.81 | **0.47–0.56** | **0.86–0.94** |
| S4 | 3000 (fija) | **993–1928** | 1.56–3.03 | 1072–2007 | 0.52–0.66 | 0.41–0.79 | 0.89–0.94 |
| S5 | 2549–4784 | **889–1772** | 1.84–4.80 | 1163–3433 | 0.50 (fija) | 0.44–0.80 | 0.84–0.94 |
| S2/S3 | 3000/400 (fijas) | — | 7.5 | 2600 | 0.50 | — | **≥ ~0.92** con T_fuente ≈ 390–405 K |

**KALINA más parecido al profesor** en cada escenario:

| Escenario | Valores | η | Rango confiable |
|---|---|---|---|
| S1 | P_alta 3208, P_baja 1966, x_b 0.71, η_t 0.83, η_p 0.87, ε_HRVG 0.47, ε_reg 0.76, ε_cond 0.85 | 4.35 % | **sí** |
| S1 (mayor η) | P_alta 3906, P_baja 1360, x_b 0.83, ε_HRVG 0.50, ε_reg 0.92, ε_cond 0.95 | 9.29 % | sí |
| S4 | P_baja 1105, x_b 0.52, η_t 0.46, ε_HRVG 0.80, ε_reg 0.48, ε_cond 0.94 | 3.74 % | no |
| S4 (mayor η) | P_baja 955, x_b 0.54, ε_HRVG 0.40, ε_cond 0.89 | 6.72 % | no |
| S2/S3 | T_fuente 403, ε_cond 0.95 (resto del profesor), de M2R | 9.50 % | sí |

Todos los KALINA de M5 tienen `B_verificado = True`. Fuera de rango: S1 2 de 4, S4 6 de 6 y S5 10 de 10.

### 3.3 Deducciones
1. **Con la fuente del profesor (623 K) es necesario:**
   - un HRVG poco efectivo (ε_HRVG ≈ 0.4–0.6), para que la mezcla no salga sobrecalentada;
   - una P_baja alta (≈ 900–1950 kPa), contra la cavitación;
   - un condensador efectivo (ε_cond ≥ 0.84).

   La razón de presiones queda baja: rP ≈ 1.4–3 cuando además se conserva el clima.
2. **Con las presiones del profesor (3000/400 kPa) es necesario** bajar la fuente a ~390–405 K y
   usar un condensador muy efectivo (≥ 0.92). Su rP es de 7.5, que solo funciona por esa
   combinación.
3. **El criterio que bloquea es siempre O2** (cavitación de la bomba).

---

## 4. Conclusiones del día

1. **Ventana de presiones de KALINA** (mapa global):
   - **P_baja ≈ 550–1460 kPa**, con un piso de ~550–700 kPa por cavitación;
   - **rP ≈ 1.7–5.3**, que crece con P_alta;
   - **dP ≈ 970–3700 kPa**;
   - franja óptima en cantidad de KALINA: **P_alta 3500–4000 kPa**.
2. **Lo que acota el diseño es P_baja, no el diferencial.** dP y rP admisibles dependen de P_alta.
3. **Más frío es mejor:** un sumidero de 5–11 °C duplica la fracción de KALINA respecto al clima
   del profesor (38 % contra 15 %).
4. **Del enunciado del profesor se puede conservar:**
   - sus **temperaturas**, con ε_HRVG ≈ 0.5, P_baja ≈ 1400–1950 kPa y ε_cond ≥ 0.86 (η 4–9 %);
   - su **fuente y su composición**, con P_baja ≈ 900–1770 kPa (η de hasta 6.7 %, fuera de rango);
   - su **P_alta y sus temperaturas**, con P_baja ≈ 1000–1930 kPa;
   - **sus presiones**, solo si T_fuente ≈ 390–405 K y ε_cond ≥ 0.92 (η ≈ 9.5 %).
5. **No se puede conservar todo a la vez:** el punto exacto del profesor no es KALINA en ningún
   escenario ni clima (M1, M2S).

## 5. Lo que no se sabe

- La franja KALINA con las presiones del profesor está identificada, pero no delimitada con
  precisión.
- El techo de P_baja de la ventana global no está determinado (coincide con el borde de la caja,
  1500 kPa).
- Muchos KALINA que conservan la fuente de 623 K están fuera del rango experimental del modelo
  (líquido > 420 K).
- 120 puntos por escenario es una exploración, no un mapa fino.

## 6. Qué sigue

1. Malla fina dirigida sobre las presiones del profesor: T_fuente 385–410 K × ε_cond 0.85–0.95 ×
   T_sumidero (≈ 100 puntos).
2. Extender P_baja por encima de 1500 kPa en la caja global, para fijar el techo de la ventana.
3. Agregar M5 al Excel.
4. Optimizar η dentro de los rangos ya fijados (M5b).
5. M6: verificación final con el motor riguroso completo.

## 7. Archivos

| Fase | Reporte | Datos |
|---|---|---|
| M4b | `resultados/2026-10-07_final_M4b/REPORTE_M4b.md` | `m4b_lhs.csv`, `m4b_rangos_presiones.csv`, `m4b_ventana_por_*.csv`, `m4b_bloqueo_por_rP.csv`, figuras `m4b_plano_presiones.png` y `m4b_hist_dP_rP.png` |
| M5 | `resultados/2026-10-07_final_M5/REPORTE_M5.md` (ver §7b, nota del director) | `m5_lhs.csv`, `m5_resumen.csv`, `m5_rangos.csv`, `m5_cercano_profesor.csv`, figuras `m5_S1–S5.png` |
| Excel | `datos/Excel_final_kalina.xlsx` | hojas `M2S_*` y `M4_*` (500 puntos, ventanas de presión, figuras) |
| Protocolo | `prompts/TASK_CONTEXT_final_M4b.md`, `TASK_CONTEXT_final_M5.md` y `TASK_CONTEXT_final_excel_M2S_M4.md` | — |
