# Plan del análisis de sensibilidad 2 (sobre los 3 921 puntos de Sensibilidad 1)

**Fecha:** 2026-10-17 · **Rama:** `test/anal_terremoto` · Base: `docs/ETAPA0_INVESTIGACION_SENSIBILIDAD_KALINA.md`.
Sin corridas nuevas del motor: todo se calcula desde los CSV (`scripts/sens1/x1_cargar.py::cargar_todo`).

## Ajustes a la guía del prompt (qué se conserva, qué se cambia)

| Elemento de la guía | Decisión | Motivo |
|---|---|---|
| Morris, Sobol, FAST | **Eliminados** | Exigen diseño propio y salida en todos los puntos; ~31 s/punto y 1/3 sin solución (Etapa 0 §1) |
| El término del prompt para los puntos fuera del rango experimental | **Reemplazado** por dentro/fuera del rango experimental (líquido > 420 K) | Decisión del usuario |
| «no_kalina» | **Se desdobla**: CORREGIBLE, NO_CONVERGIO, INVIABLE | Son causas distintas |
| Índices de sensibilidad | KS/RSA, PAWN, δ de Borgonovo, HSIC, PRCC/SRC, η², regresión logística (la importancia por permutación quedó sin implementar); **parámetro dummy** y bootstrap | Calculables sobre datos existentes; el dummy da el piso de ruido |
| Fase C «distancia a Kalina» | **Se define con los datos**: D, violaciones O1–O5 y vecino KALINA más cercano (variable que cambia y cuánto) | Es la única forma de decir «qué mover» |
| Bloques | Un análisis por centro (C1–C4) **y** consolidado, nunca mezclando datos fijos distintos | Regla del proyecto |
| Elementos añadidos | Interacción (no aditividad) desde las mallas de pares; reglas de la región KALINA (stump/árbol en numpy); requisitos de equipos con percentiles | Responde (3) y (4) del profesor |

## Fases (una por una, OpenCode + verificación mía en cada una)

| Fase | Contenido | Entrega |
|---|---|---|
| P1 | Dataset unificado y Fase A: existencia, fronteras por variable y centro, P(KALINA), reglas de región, zonas grises | `resultados/2026-10-17_sens2_P1/` |
| P2 | Fase C: CORREGIBLE frente a KALINA, distancia a KALINA, sesgo de η, ¿vale rescatar? | `..._P2/` |
| P3 | Fase B: índices globales con dummy y bootstrap sobre η, W_net, P(KALINA); interacciones | `..._P3/` |
| P4 | Equipos: rangos de turbina (ΔP, r_P, Δh, título), regenerador, condensador, por centro y percentiles | `..._P4/` |
| P5 | Informe (5 categorías de conclusiones, ordenadas por impacto y evidencia) y libro `Kalina_anal_sensible_2.xlsx` | `docs/` y `datos/` |

Etiquetas de conclusión: [DISEÑO REAL], [EQUIPOS], [MÁXIMA EFICIENCIA], [FLUCTUACIÓN], [LÍMITES KALINA].
