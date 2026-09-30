# PRESCAN eps_hrvg — Fase 2 (tarea 2026-09-20-fase2-prescan-eps-hrvg)

**Fecha:** 2026-09-20 · **Rama:** `fix/temperatura-ambiente` (worktree
`barridos-tercero-f7448d`)

Pre-escaneo de `eps_hrvg` sobre el candidato v2 (400/0.40/0.95, resto defaults,
`T_amb_diseno=303.55`) con TeqpAdapter: 6 puntos en 0.70–0.95 paso 0.05
(`prescan_eps_hrvg.csv`, esquema `tabla_barrido` + q2/T2 + trío O2).

| eps_hrvg | clasif. | η | q2 | T2 [K] | margen S5 (470−T2) |
|---|---|---|---|---|---|
| 0.70 | KALINA | 0.121758 | 0.454 | 456.29 | +13.71 |
| 0.75 | KALINA | 0.122737 | 0.492 | 458.97 | +11.03 |
| 0.80 | KALINA | 0.123570 | 0.530 | 461.48 | +8.52 |
| 0.85 | KALINA | 0.124289 | 0.569 | 463.83 | +6.17 |
| 0.90 | KALINA | 0.124917 | 0.608 | 466.02 | +3.98 |
| 0.95 | KALINA | 0.125473 | 0.649 | 468.07 | +1.93 |

**Qué se encontró:** los 6 puntos clasifican KALINA — ninguna frontera se cruza
en 0.70–0.95, la respuesta es monótona y suave (η +3.05 % rel. en el rango).
Las fronteras de O5 (q2∈(1e-3, 1−1e-3)) no están a la vista: la superior
(q2>0.999 → DEGENERADO) cae en ≈1.4, fuera de `CAMPOS_CICLO`; la inferior
(q2<1e-3 → INVIABLE) en ≈0.12, lejos del candidato. La única frontera cercana
es S5 (T2 > T_fuente=470 → INVIABLE): el margen colapsa de +13.71 K a +1.93 K
y la extrapolación lineal de T2 da el cruce en eps_hrvg ≈ 0.99 — justo el tope
0.99 de `CAMPOS_CICLO`.

**Rango final recomendado (tabla de sensibilidad, BASE_LIBRE_v2 §3):
`eps_hrvg: 0.80 – 0.99`, centro 0.85.** El 0.80–0.90 original era INADECUADO:
todo KALINA sin acercarse a ningún borde (a 0.90, margen S5 aún +3.98 K). La
corrección extiende el tope a 0.99 para bracketing de la frontera S5 real en el
entorno del candidato; el piso 0.80 se conserva (sin fronteras debajo en un
entorno razonable y la curva es suave). Dejó constancia: η(0.85)=0.124289 teqp
concuerda con el motor real (0.124296).