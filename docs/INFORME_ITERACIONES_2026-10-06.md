# Informe de iteraciones y conclusiones — campaña final de barridos

**Fecha:** 6 de octubre de 2026 · **Rama:** `test/barrido_final`
**Motor:** teqp con la protección A+B, el bracket tolerante MA y la marca de rango G4-01. Todos los
KALINA se verificaron con el motor riguroso (verificación B).
**Ejecución:** OpenCode, a partir de un `TASK_CONTEXT` por fase. Claude vigiló cada corrida en
vivo y auditó los resultados contra los CSV.

---

## 1. Iteraciones realizadas

| Fase | Pregunta | Qué se varió | Puntos | KALINA | Commit |
|---|---|---|---|---|---|
| M1 | ¿El código nuevo reproduce la Fase 1 del profesor? | P_alta, x_b y las 24 horas de T_amb | 41 | 0 (41/41 iguales a lo anterior) | `1b01096` |
| M2 nivel 1 | ¿Basta UN cambio? | Las 10 variables, una a la vez (ε/η en 0.75–0.85) | 132 | 0 | `02f64b6` |
| M2 nivel 2 | ¿Bastan DOS cambios? | T_fuente × P_baja; ε_HRVG × P_baja | 180 | 49 | `c6fb1e1` |
| M2R | M2 con ε/η en 0.40–0.95 | Las ε/η solas; ε_HRVG × ε_cond; ε_HRVG × P_baja; T_fuente × ε_cond | 225 | 14 | `ef30e9f` |
| M3 | Sensibilidad local alrededor del ancla (403 K / 564 kPa) | Las 10 variables, 15 valores cada una | 171 | 86 (zona del ancla) | `ef30e9f` |
| M2S | Efecto de un sumidero frío (piso de O2 = clima) | 4 bases × T_sumidero de 5 a 27 °C × P_baja | 320 | 123 | `8d88070` |
| M4 | Mapa global con las 10 variables a la vez | LHS de 300 puntos en una caja de rangos favorables | 300 | 76 | `4fd325b` |

En total son **≈ 1370 combinaciones evaluadas**.

## 2. Resultados por fase

### M1 — Reproducibilidad
Los 41 puntos del profesor siguen siendo NO_CONVERGIO. La causa: con una fuente de 623 K la mezcla
sale del HRVG sobrecalentada, así que el separador no tiene líquido y vapor que separar.

### M2 / M2R — Cuánto hay que cambiar el enunciado

| Ruta | Cambios respecto al profesor | η | ¿Rango confiable? |
|---|---|---|---|
| Conservar la fuente de 623 K | ε_HRVG → 0.40 · P_baja → 1318 kPa | 6.3 % | no |
| Fuente más fría + P_baja | T_fuente → 403 K · P_baja → 564 kPa (ancla) | 8.5 % | sí |
| Fuente más fría + P_baja | T_fuente → 420 K · P_baja → 736 kPa | 9.2 % | sí |
| Fuente más fría + condensador | T_fuente → 403 K · ε_cond → 0.95 (P_baja del profesor) | 9.5 % | sí |

Ninguna variable sola basta. Ventana de T_fuente con KALINA (P_alta = 3000 kPa, x_b = 0.50):
**≈ 390–434 K**.

### M3 — Sensibilidad alrededor del ancla
- El ancla está al filo de la cavitación (O2): 7 de 10 variables pierden KALINA con cambios
  pequeños.
- Las mejores palancas de η: ε_reg = 0.95 (10.96 %) y η_t = 0.95 (9.62 %).
- P_baja es la "perilla de seguridad" contra la cavitación.

### M2S — Sumidero frío (P_baja mínima con KALINA → η)

| Sumidero | Fuente 403 K | Fuente 420 K | Fuente 623 K + ε_HRVG 0.40 | Profesor exacto |
|---|---|---|---|---|
| 5 °C | 291 kPa → 10.4 % | 394 kPa → 11.9 % | 750 kPa → 9.7 % ¹ | sin KALINA |
| 10 °C | 338 kPa → 10.0 % | 459 kPa → 11.3 % | 863 kPa → 8.9 % ¹ | sin KALINA |
| 15 °C | 394 kPa → 9.6 % | 534 kPa → 10.6 % | 984 kPa → 8.1 % ¹ | sin KALINA |
| 20 °C | 459 kPa → 9.1 % | 619 kPa → 10.0 % | 1116 kPa → 7.3 % ¹ | sin KALINA |
| 27 °C (profesor) | 563 kPa → 8.5 % | 741 kPa → 9.1 % | 1313 kPa → 6.3 % ¹ | sin KALINA |

¹ Fuera del rango confiable (líquido > 420 K). La fila de 27 °C reproduce M2 y M2R con
diferencias menores a 6 kPa y a 0.04 pp de η.

### M4 — Mapa global (300 puntos, 76 KALINA)

| Variable decisiva (RSA, KS) | KS | Rango donde caen los KALINA (p5–p95) |
|---|---|---|
| P_baja | 0.44 | 690–1460 kPa |
| T_fuente | 0.36 | 383–491 K |
| rP = P_alta/P_baja | 0.35 | 1.7–5.5 |
| ε_cond | 0.35 | 0.76–0.95 |
| dT_fs = T_fuente − T_sumidero | 0.33 | 90–204 K |
| x_b | 0.24 | 0.51–0.80 |

- No resultaron decisivas dentro de la caja: T_sumidero, η_p, P_alta, dP, ε_reg, ε_HRVG y η_t.
- Efecto sobre η (PRCC): P_baja (−0.66), P_alta (+0.58), η_t (+0.35), T_fuente (+0.28),
  x_b (+0.26) y ε_reg (+0.26).
- El mejor KALINA del muestreo: η = 12.3 % (436 K, 279 K, 3482/808 kPa, x_b 0.635).
- Convergencia: el top-5 del ranking es estable, pero el ranking completo no (ρ = 0.84 < 0.9).
  Por eso se decidió ampliar el LHS.

## 3. Conclusiones

1. **El enunciado del profesor no es un Kalina viable tal como está, ni siquiera con un sitio
   frío.** El problema está en el lado caliente: la mezcla sale sobrecalentada.
2. **Queda a dos cambios de serlo:**
   - con su misma fuente, un HRVG de baja efectividad y una P_baja alta;
   - o con una fuente de ~390–434 K y una P_baja de ~450–950 kPa, o un condensador de 0.95.
3. **El criterio que limita es la cavitación de la bomba (O2).** P_baja es la variable que más
   decide si un punto es KALINA.
4. **Región KALINA acotada por M4:** T_fuente ≈ 383–491 K, P_baja ≈ 690–1460 kPa,
   rP ≈ 1.7–5.5, ε_cond ≥ 0.76 y x_b ≈ 0.51–0.80.
5. **Un sitio más frío**, con la cavitación evaluada con ese clima, baja la P_baja necesaria y sube
   η unos 2–3 pp.
6. **Las eficiencias alcanzadas (10–12 %) son coherentes** con Elsayed 2013 (11.4 %) y con Húsavík
   (12.7–13.4 %).

## 4. Lo que no se sabe

- El orden de las variables menos influyentes de M4 no es concluyente (ρ = 0.84).
- Muchos estados con fuente caliente quedan fuera del rango experimental del modelo (líquido >
  420 K).
- Las diferencias de η menores que 0.4–0.7 pp no son concluyentes (incertidumbre de G4-01).

## 5. Qué sigue (definido el 7 de octubre)

1. **Ampliar M4 a 500 puntos**, con foco en las **presiones**: la región KALINA en el plano
   P_alta–P_baja, los diferenciales dP y rP, y la ventana de P_baja por P_alta y por T_fuente.
2. Agregar M2S y M4 al Excel.
3. **M5:** búsqueda de las regiones KALINA **conservando parte de los datos del profesor** (sus
   temperaturas, sus presiones o ambas). La eficiencia se optimiza después, cuando los rangos
   estén definidos.
