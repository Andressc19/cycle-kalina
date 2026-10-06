# Barridos finales — resumen de resultados y conclusiones (6 de octubre de 2026)

**Rama:** `test/barrido_final` · **Libro de datos:** `datos/Excel_final_kalina.xlsx` (27 hojas)
**Protocolo:** `docs/METODOLOGIA_BARRIDOS_FINAL.md` · **Fórmulas:** `docs/MATEMATICA_ITERACIONES_SENSIBILIDAD.md`
**Método de sensibilidad elegido y por qué:** `docs/ESTUDIO_METODOS_SENSIBILIDAD.md`

Todos los cálculos los ejecutó OpenCode a partir de un `TASK_CONTEXT` por fase. Claude los vigiló
en vivo y auditó cada resultado contra los CSV. El motor usado es teqp con la protección A+B, el
bracket tolerante MA y la marca de rango G4-01. Los KALINA se verificaron con el motor riguroso
(verificación B).

---

## 1. Punto de partida: los datos del profesor

| Parámetro | Valor |
|---|---|
| T_fuente / T_sumidero | 623.15 K / 300.03 K (promedio del perfil horario) |
| P_alta / P_baja | 3000 / 400 kPa |
| x_b, m_b | 0.50, 1 kg/s |
| η_t / η_p | 0.85 / 0.75 |
| ε_HRVG / ε_reg / ε_cond | 0.85 / 0.75 / 0.80 |
| Piso de cavitación O2 | 300.03 K (clima del profesor) |

## 2. Qué se ha hecho (≈ 950 combinaciones evaluadas)

| Fase | Pregunta | Qué se varió | Puntos | Resultado |
|---|---|---|---|---|
| **M1** | ¿El código nuevo reproduce lo anterior? | La Fase 1 del profesor: P_alta, x_b y las 24 horas de T_amb | 41 | **41/41 iguales** (todos NO_CONVERGIO) |
| **M2 nivel 1** | ¿Basta UN cambio? | Las 10 variables, una a la vez (ε/η en 0.75–0.85) | 132 | **0 KALINA** |
| **M2 nivel 2** | ¿Bastan DOS cambios? | T_fuente × P_baja; ε_HRVG × P_baja | 180 | **49 KALINA** (T_fuente de 390 a 434 K) |
| **M2R** | Lo mismo, con ε/η en 0.40–0.95 | Las 5 ε/η solas; ε_HRVG × ε_cond; ε_HRVG × P_baja; T_fuente × ε_cond | 225 | **14 KALINA**, incluidos algunos **con la fuente del profesor** |
| **M3** | Sensibilidad alrededor del ancla | Las 10 variables, 15 valores cada una, en torno a 403 K / 564 kPa | 171 | Ranking de variables y fronteras |
| **M2S** | Efecto de un sumidero frío (piso de O2 = clima) | 4 bases × T_sumidero de 5 a 27 °C × P_baja | 320 | **123 KALINA**; η sube 2–3 pp al pasar de 27 a 5 °C |
| **M4** | Mapa global con las 10 variables a la vez | LHS de 300 puntos en una caja de rangos favorables | 300 | **76 KALINA (25 %)**; variables decisivas y rangos favorables |

## 3. Resultados principales

### 3.1 ¿Por qué los datos del profesor no funcionan?
Con una fuente de 623 K, la mezcla sale del HRVG **sobrecalentada**, por encima de la campana
bifásica. Así el separador no tiene líquido y vapor que separar y el ciclo deja de ser un Kalina.
**Ningún cambio de una sola variable lo arregla.**

### 3.2 Las rutas encontradas hacia KALINA (2 cambios respecto al profesor)

| Ruta | Cambios | η | ¿Rango confiable? | Verificado con el motor riguroso |
|---|---|---|---|---|
| **Conservar la fuente de 623 K** | ε_HRVG 0.85 → **0.40** · P_baja 400 → **1318 kPa** | 6.27 % | no (líquido > 420 K) | sí |
| Fuente más fría + P_baja | T_fuente → **390 K** · P_baja → **445 kPa** | 2.45 % | sí | sí |
| Fuente más fría + P_baja | T_fuente → **403 K** · P_baja → **564 kPa** (**ancla A\***) | 8.48 % | sí | sí |
| Fuente más fría + P_baja (la mejor η) | T_fuente → **420 K** · P_baja → **736 kPa** | **9.15 %** | sí | sí |
| Fuente más fría + condensador | T_fuente → **403 K** · ε_cond → **0.95** (P_baja del profesor) | **9.50 %** | sí | sí |

- Ventana de T_fuente con KALINA (P_alta = 3000 kPa, x_b = 0.50): **≈ 390–434 K**. Por encima de
  ~466 K, la cavitación (O2) ya no se cierra ni con P_baja = 2000 kPa.
- Conservando la fuente de 623 K, **solo se llega a KALINA con un HRVG poco efectivo (0.40–0.50)
  y una P_baja alta (≥ 1318 kPa)**. El costo es una η baja (3–6 %) y estados fuera del rango
  experimental del modelo.
- Ninguna ε ni η sola, ni siquiera en 0.40–0.95, vuelve KALINA al enunciado.

### 3.3 Sensibilidad alrededor del ancla (M3)

| Variable | Sigue KALINA hasta (aprox.) | Qué se rompe | Efecto sobre η |
|---|---|---|---|
| T_fuente | ≤ 410 K | O2 | el más fuerte localmente (elasticidad +10.9) |
| T_sumidero | ≤ 300.5 K | O2 | bajo (+1.6) |
| P_alta | ≥ 2936 kPa | O2 | −1.2 |
| P_baja | ≥ 542 kPa | O2 | −0.6 (la "perilla de seguridad") |
| x_b | 0.47–0.51 | O2 / trabajo negativo | +3.4, pero con un pasillo muy estrecho |
| η_t | ≥ 0.66 | O2 | 0.95 → **η = 9.62 %** |
| η_p | todo el rango 0.40–0.95 | nada | casi irrelevante |
| ε_HRVG | ≤ 0.87 | O2 | +0.6 |
| ε_reg | ≥ 0.72 | O2 | 0.95 → **η = 10.96 %** (la mejor palanca) |
| ε_cond | ≥ 0.79 | O2 | −0.4 |

**Lectura:** el ancla está **al filo de la cavitación (O2)**, el criterio que siempre se rompe
primero. Para ganar η sin perder KALINA, las palancas son el **regenerador (ε_reg)** y la
**turbina (η_t)**. Para ganar margen de seguridad, la palanca es **P_baja**.

### 3.4 Sumidero frío (M2S: el piso de O2 sigue al clima; P_baja mínima con KALINA)

| T_sumidero | B1: fuente 403 K | B2: fuente 420 K | B3: fuente 623 K del profesor, ε_HRVG 0.40 | B4: profesor exacto |
|---|---|---|---|---|
| 5 °C | 291 kPa → **10.4 %** | 394 kPa → **11.9 %** | 750 kPa → 9.7 % ¹ | sin KALINA |
| 10 °C | 338 kPa → 10.0 % | 459 kPa → 11.3 % | 863 kPa → 8.9 % ¹ | sin KALINA |
| 15 °C | 394 kPa → 9.6 % | 534 kPa → 10.6 % | 984 kPa → 8.1 % ¹ | sin KALINA |
| 20 °C | 459 kPa → 9.1 % | 619 kPa → 10.0 % | 1116 kPa → 7.3 % ¹ | sin KALINA |
| 27 °C (profesor) | 563 kPa → 8.5 % | 741 kPa → 9.1 % | 1313 kPa → 6.3 % ¹ | sin KALINA |

¹ Fuera del rango confiable (líquido > 420 K). Todos los puntos de la tabla tienen `B_verificado = True`.
La fila de 27 °C reproduce M2 y M2R con diferencias menores a 6 kPa y a 0.04 pp de η.

- **Un sumidero frío no rescata por sí solo el enunciado del profesor (B4).** El problema está en
  el lado caliente.
- En cualquier base que ya funcione, enfriar el sumidero **baja la P_baja necesaria y sube η**,
  siempre que el criterio de cavitación se evalúe con el clima real. Es la lección de Húsavík.

### 3.5 Mapa global (M4: LHS de 300 puntos, piso de O2 = clima)

**Qué decide que el ciclo sea KALINA** (RSA, KS con p < 0.05), con el rango donde caen los KALINA
(percentiles 5–95):

| Variable | KS | Rango favorable |
|---|---|---|
| P_baja | 0.44 | 690–1460 kPa |
| T_fuente | 0.36 | 383–491 K |
| rP = P_alta/P_baja | 0.35 | 1.7–5.5 |
| ε_cond | 0.35 | 0.76–0.95 |
| dT_fs = T_fuente − T_sumidero | 0.33 | 90–204 K |
| x_b | 0.24 | 0.51–0.80 |

No resultaron decisivas dentro de la caja (p > 0.05): T_sumidero, η_p, P_alta, dP, ε_reg, ε_HRVG
y η_t.

**Qué sube η** (PRCC): P_baja **en contra** (−0.66), P_alta (+0.58), η_t (+0.35), T_fuente
(+0.28), x_b (+0.26) y ε_reg (+0.26).

**Reglas del árbol** (exactitud del 76 % con validación cruzada). Las más claras:
- con P_baja > 881 kPa, ε_cond > 0.90 y η_t ≤ 0.88 → KALINA en el 100 % de los casos;
- con P_baja ≤ 881 kPa, solo ε_cond > 0.94 da KALINA de forma fiable.

**El mejor KALINA del muestreo:** η = **12.3 %**, con T_fuente 436 K, T_sumidero 279 K, P_alta 3482
kPa, P_baja 808 kPa, x_b 0.635, η_t 0.92, η_p 0.75, ε_HRVG 0.68, ε_reg 0.94 y ε_cond 0.84.

**Convergencia:** el ranking del primer lugar (P_baja) y del top-5 es estable. Las posiciones bajas
no son concluyentes (ρ = 0.84 < 0.9).

## 4. Conclusiones actuales

1. **El enunciado del profesor no es un Kalina viable tal como está.** La fuente de 623 K es
   demasiado caliente para un KCS-11 a 3 MPa con ε_HRVG = 0.85.
2. **Queda a dos cambios de serlo:**
   - con su misma fuente: un HRVG de baja efectividad y una P_baja alta (η ≈ 6 %);
   - o con una fuente de ~400–420 K y una P_baja de ~550–750 kPa, o un condensador de 0.95
     (η ≈ 8.5–9.5 %).
3. **El criterio que limita es la cavitación de la bomba (O2)**, en todas las fases.
4. Alrededor del punto funcional, **ε_reg y η_t son las mejores palancas de eficiencia**: hasta
   ~11 % con ε_reg = 0.95.
5. **Un sitio más frío mejora cualquier diseño que ya funcione:** a 5 °C, η llega a 10.4–11.9 % con
   las fuentes de 403–420 K. Sin embargo, el enfriamiento no rescata por sí solo el enunciado del
   profesor.
6. **El mapa global (M4)** confirma que lo que más decide la factibilidad es **P_baja**, seguida de
   T_fuente, la razón de presiones, ε_cond y el salto de temperatura entre fuente y sumidero.
   El rango favorable es: T_fuente ≈ 383–491 K, P_baja ≈ 690–1460 kPa, rP ≈ 1.7–5.5,
   ε_cond ≥ 0.76 y x_b ≈ 0.51–0.80.
7. Con los rangos de la literatura (Elsayed, Húsavík) **se alcanza η ≈ 12 %**. Ese valor es
   coherente con Elsayed (11.4 % a 373 K) y con Húsavík (12.7–13.4 %).

## 5. Lo que falta o no se sabe

- **Convergencia de M4:** el orden de las variables menos influyentes no es concluyente
  (ρ = 0.84). Para afinarlo haría falta ampliar el LHS (por ejemplo, a 500 puntos).
- **M5 (búsqueda dirigida) y M6 (verificación final con el motor riguroso)** están pendientes.
- **Rango confiable:** 128 de los 300 puntos de M4 y todos los KALINA que conservan la fuente de
  623 K tienen líquido > 420 K, sin respaldo experimental en G4-01.
- **Incertidumbre:** las diferencias de η menores que 0.4–0.7 pp no son concluyentes (incertidumbre
  del modelo G4-01). Los estados con líquido > 420 K son extrapolación del modelo.
- **No probado todavía:** combinaciones con x_b > 0.55 y P_alta de 4000–5000 kPa partiendo del
  enunciado del profesor (M4 las cubre).

## 6. Dónde está cada cosa

| Fase | Reporte | Commit |
|---|---|---|
| M0–M1 | `resultados/2026-10-06_final_M1/REPORTE_M1.md` | `1b01096` |
| M2 nivel 1 | `resultados/2026-10-06_final_M2/REPORTE_M2_N1.md` (ver §9, nota del director) | `02f64b6` |
| M2 nivel 2 | `resultados/2026-10-06_final_M2/REPORTE_M2_N2.md` | `c6fb1e1` |
| M3 y M2R | `resultados/2026-10-06_final_M3/REPORTE_M3.md` (ver §11) · `resultados/2026-10-06_final_M2R/REPORTE_M2R.md` | `ef30e9f` |
| Excel (27 hojas, sin M2S ni M4 aún) | `datos/Excel_final_kalina.xlsx` | `6dfc433` |
| M2S | `resultados/2026-10-06_final_M2S/REPORTE_M2S.md` | `8d88070` |
| M4 | `resultados/2026-10-06_final_M4/REPORTE_M4.md` (ver §14, nota del director) | (este commit) |
