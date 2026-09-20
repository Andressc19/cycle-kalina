# Resumen cruzado — Fase 1 / Fase 2 / Fase 3

**Tarea:** consolidación final (tabla D) · **Fecha:** 2026-09-20 ·
**Rama:** `fix/temperatura-ambiente`

| Fase | Caso | T_fuente | Clasificación | η | Lección aprendida |
|---|---|---|---|---|---|
| **1** | Datos exactos del profesor | 623.15 K (350 °C) | **NO_CONVERGIO** (41/41 puntos) | — | `T_fuente` alto rompe la campana bifásica NH3-H2O a `P_alta` razonable: el estado 2 del HRVG queda fuera del dominio del separador en todo el rango pedido por el enunciado (P_alta 2-4 MPa, x_b 0.4-0.7, T_amb real de 24 h). Ningún ajuste de esas 3 variables lo arregla — la causa es estructural, no paramétrica. |
| **2** | Base libre (mismo profesor, T_fuente corregido a 470 K) | 470.0 K | **KALINA** | 0.1243 | Bajar `T_fuente` a 470 K (documentado en `CONTEXT.md`) resuelve el problema de Fase 1. Con eso resuelto, el bloqueo pasa a ser el criterio O2 (cavitación) y luego O1 (calidad de turbina, frontera real más cercana del ancla, margen +0.0013 — al filo). `eps_cond` es la variable más influyente: por debajo de ~0.93 todo el plano `P_baja×eps_cond` cae a CORREGIBLE. |
| **3** | Caso real Húsavík (geotérmico, Islandia) | 394.15 K (121 °C) | **KALINA** | 0.1273 | Ancla directamente en un caso real publicado. El piso de diseño de O2 (`T_amb_diseno`) heredado del clima tropical del profesor (30.4 °C) era físicamente incorrecto para Islandia; corregirlo a 283.15 K (10 °C, realista) bajó el `P_baja` necesario de 1200 a 690 kPa y subió η de 0.088 a 0.127 (+44 %). La frontera O2 quedó confirmada 1:1 con el motor real (10/10 spot-checks). |

## Hallazgos transversales

- **El motor rápido (`TeqpAdapter`) es confiable lejos de fronteras**, pero cerca de un borde de clasificación puede discrepar del motor real (`AmmoniaWaterAdapter`) — se documentó explícitamente en Fase 2 (x_b=0.39: KALINA en Teqp, NO_CONVERGIO en el motor real, reproducido 2 veces) y NO en Fase 3 (10/10 coincidieron). La estrategia de "Teqp para el grueso + motor real para los puntos cerca del borde" es la que permitió detectar esa discrepancia sin pagar el costo de correr todo con el motor lento.
- **Ningún candidato final tuvo que forzar variables a los extremos de `CAMPOS_CICLO`** (a diferencia de intentos anteriores con `eps_cond=0.99` o `P_alta` cerca del techo de 20 MPa) — las bases de Fase 2 y Fase 3 usan valores dentro de rangos de ingeniería razonables.
- **El criterio de diseño configurable (`T_amb_diseno`)**, añadido en esta misma rama, fue la corrección que desbloqueó Fase 3: confirma que el piso de cavitación debe reflejar el clima real del caso, no un valor heredado de otro contexto.

## Archivos fuente de esta tabla

- Fase 1: `resultados/barridos_2026-09-19/fase1_profesor/CONSTANCIA_PROFESOR.md`
- Fase 2: `resultados/barridos_2026-09-19/fase2_libre/resumen_fase2.json`,
  `BASE_LIBRE_v2.md`, `spotcheck_motor_real_fase2.json`
- Fase 3: `resultados/barridos_2026-09-19/fase3_real/resumen_fase3.json`,
  `CASO_HUSAVIK_v2.md`
