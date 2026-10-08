# M6 — verificación con el motor real, margen de subenfriamiento y Excel

## Parte A — teqp vs motor real

| id | origen | clase_teqp | clase_real | coincide | eta_teqp | eta_real | d_eta_pp | ±0.7 pp | m_O2_teqp | m_O2_real |
|---|---|---|---|---|---|---|---|---|---|---|
| P01 | Ancla A* | KALINA | NO_CONVERGIO | False | 0.0848 | n/d | n/d | n/d | 0.311 | n/d |
| P02 | M2, mayor η | KALINA | NO_CONVERGIO | False | 0.0915 | n/d | n/d | n/d | 0.040 | n/d |
| P03 | M5c, presiones del profesor, techo | KALINA | KALINA | True | 0.1081 | 0.1081 | 0.000 | True | 0.357 | 0.359 |
| P04 | M5c, presiones del profesor, ε_cond mínima | KALINA | NO_CONVERGIO | False | 0.0254 | n/d | n/d | n/d | 0.052 | n/d |
| P05 | M7, óptimo A1 | KALINA | NO_CONVERGIO | False | 0.1498 | n/d | n/d | n/d | 0.423 | n/d |
| P06 | M7, óptimo A2 | KALINA | NO_CONVERGIO | False | 0.1548 | n/d | n/d | n/d | 3.811 | n/d |
| P07 | M7, óptimo A3 | KALINA | NO_CONVERGIO | False | 0.1274 | n/d | n/d | n/d | 3.805 | n/d |
| P08 | M7, óptimo A4 | KALINA | KALINA | True | 0.1560 | 0.1560 | 0.000 | True | 0.125 | 0.127 |
| P09 | M7, óptimo A5 | KALINA | NO_CONVERGIO | False | 0.1109 | n/d | n/d | n/d | 5.659 | n/d |
| P10 | M4b, top 1 | KALINA | NO_CONVERGIO | False | 0.1230 | n/d | n/d | n/d | 5.547 | n/d |
| P11 | M4c, mayor P_baja KALINA | KALINA | NO_CONVERGIO | False | 0.0267 | n/d | n/d | n/d | 49.378 | n/d |
| P12 | M2R, fuente del profesor | KALINA | NO_CONVERGIO | False | 0.0627 | n/d | n/d | n/d | 0.242 | n/d |

A: 12 puntos · coincide_clase = 2/12 · dentro_banda (|d_eta_pp| ≤ 0.7 pp) = 2/12 · fuera = 10
A clases teqp: KALINA = 12 · CORREGIBLE = 0 · INVIABLE = 0 · NO_CONVERGIO = 0
A clases real: KALINA = 2 · CORREGIBLE = 0 · INVIABLE = 0 · NO_CONVERGIO = 10
A d_eta_pp (2/12 computables): mín = 0.000 pp · máx = 0.000 pp
A (teqp): fuera_rango = 3/12 · B_verificado = 11/12
A m_O2_teqp: mín = 0.040 K · máx = 49.378 K
A m_O2_real: mín = 0.127 K · máx = 0.359 K

## Parte B1 — piso de O2 = 303.55 K (30.4 °C)

| id | origen | clase | eta | m_O2 |
|---|---|---|---|---|
| P01 | Ancla A* | CORREGIBLE | 0.0848 | -0.499 |
| P02 | M2, mayor η | CORREGIBLE | 0.0915 | -0.575 |
| P03 | M5c, presiones del profesor, techo | CORREGIBLE | 0.1081 | -0.571 |
| P04 | M5c, presiones del profesor, ε_cond mínima | CORREGIBLE | 0.0254 | -0.579 |
| P05 | M7, óptimo A1 | CORREGIBLE | 0.1498 | -1.756 |
| P06 | M7, óptimo A2 | CORREGIBLE | 0.1548 | -3.245 |
| P07 | M7, óptimo A3 | KALINA | 0.1274 | 0.525 |
| P08 | M7, óptimo A4 | CORREGIBLE | 0.1560 | -0.615 |
| P09 | M7, óptimo A5 | KALINA | 0.1109 | 4.829 |
| P10 | M4b, top 1 | CORREGIBLE | 0.1230 | -1.926 |
| P11 | M4c, mayor P_baja KALINA | KALINA | 0.0267 | 32.482 |
| P12 | M2R, fuente del profesor | CORREGIBLE | 0.0627 | -0.578 |

B1: 12 puntos · KALINA = 3 (en A con teqp: 12) · clases distintas entre A(teqp) y B1 = 9
B1: eta mín = 0.0254 · máx = 0.1560 · m_O2 mín = -3.245 K · máx = 32.482 K

## Parte B2 — P_baja mínima para un ΔT_sub dado

| id | ΔT_sub | alcanzable | P_baja_orig | P_baja_req | ΔP_baja | eta_orig | eta_req | d_eta_pp | rP_req | m_O1_req | iter | nota |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P01 | 2.0 | True | 563.6 | 597.4 | 33.8 | 0.0848 | 0.0819 | -0.288 | 5.021 | 0.0360 | 8 | n/d |
| P01 | 5.0 | True | 563.6 | 650.6 | 86.9 | 0.0848 | 0.0777 | -0.713 | 4.611 | 0.0382 | 8 | n/d |
| P02 | 2.0 | True | 736.4 | 782.1 | 45.7 | 0.0915 | 0.0877 | -0.376 | 3.836 | 0.0374 | 8 | n/d |
| P02 | 5.0 | True | 736.4 | 852.7 | 116.3 | 0.0915 | 0.0823 | -0.918 | 3.518 | 0.0404 | 8 | n/d |
| P03 | 2.0 | True | 400.0 | 424.6 | 24.6 | 0.1081 | 0.1051 | -0.301 | 7.065 | 0.0239 | 9 | n/d |
| P03 | 5.0 | True | 400.0 | 468.4 | 68.4 | 0.1081 | 0.1001 | -0.799 | 6.405 | 0.0264 | 9 | n/d |
| P05 | 2.0 | True | 808.3 | 1251.1 | 442.7 | 0.1498 | 0.1131 | -3.670 | 3.502 | 0.0316 | 9 | hueco NO_CONVERGIO en 1231.3 kPa, 1244.5 kPa, 1247.8 kPa |
| P05 | 5.0 | True | 808.3 | 1251.1 | 442.7 | 0.1498 | 0.1131 | -3.670 | 3.502 | 0.0316 | 9 | hueco NO_CONVERGIO en 1231.3 kPa, 1244.5 kPa, 1247.8 kPa |
| P06 | 2.0 | True | 393.8 | 393.8 | 0.0 | 0.1548 | 0.1548 | 0.000 | 7.619 | 0.0047 | 0 | n/d |
| P06 | 5.0 | True | 393.8 | 413.0 | 19.2 | 0.1548 | 0.1515 | -0.332 | 7.264 | 0.0062 | 9 | n/d |
| P07 | 2.0 | True | 1359.6 | 1359.6 | 0.0 | 0.1274 | 0.1274 | 0.000 | 3.678 | 0.0307 | 0 | n/d |
| P07 | 5.0 | True | 1359.6 | 1408.6 | 49.0 | 0.1274 | 0.1241 | -0.329 | 3.550 | 0.0318 | 8 | n/d |
| P08 | 2.0 | True | 400.0 | 427.3 | 27.3 | 0.1560 | 0.1513 | -0.472 | 7.020 | 0.0079 | 9 | n/d |
| P08 | 5.0 | True | 400.0 | 471.1 | 71.1 | 0.1560 | 0.1443 | -1.174 | 6.368 | 0.0110 | 9 | n/d |
| P09 | 2.0 | True | 1022.3 | 1022.3 | 0.0 | 0.1109 | 0.1109 | 0.000 | 4.704 | 0.0006 | 0 | n/d |
| P09 | 5.0 | True | 1022.3 | 1022.3 | 0.0 | 0.1109 | 0.1109 | 0.000 | 4.704 | 0.0006 | 0 | n/d |

B2: 16 casos (8 puntos × ΔT_sub ∈ {2.0, 5.0} K) · alcanzables = 16 · no alcanzables = 0 · con nota = 2
B2 alcanzables: ΔP_baja mín = 0.0 kPa · máx = 442.7 kPa · d_eta_pp mín = -3.670 pp · máx = 0.000 pp · iteraciones máx = 9 · evaluaciones = 131

## Lo que no se sabe

- 10 de 12 puntos no tienen η_real: el motor real agotó los 300 s (NO_CONVERGIO); la banda ±0.7 pp solo se comprueba en 2/12.
- los 16 de 16 casos B2 son alcanzables: no se sabe si existe un P_baja_req menor fuera del [lo, hi] bisecado.
- 2 casos con nota (hueco NO_CONVERGIO): no se sabe si el predicado es monótono en todo el intervalo.
- B1 cambia la clase de 9 de 12 puntos frente a la Parte A: no se sabe si ese piso cambiaría las otras fases.
- El motor real no corre la verificación B: B_verificado solo existe para teqp, no se sabe qué diría el motor real.

> Todas las cifras de este reporte salen de los CSV de esta carpeta y se recalculan con `scripts/barrido_final/m6_verificar.py`.

## Nota del director (Claude, auditoría 2026-10-08)

- **Los NO_CONVERGIO del motor real se deben al límite de tiempo, no a la física.** Los 10 casos se
  cortaron en el límite de 300 s (`mensaje` = "presupuesto de tiempo agotado"). Los 2 puntos que sí
  terminaron (P03 y P08) coinciden con teqp en la clase y en η (|Δη| ≤ 0.0003 pp) y en m_O2
  (≤ 0.002 K). M9 vuelve a correr 3 puntos con 1500 s.
- **B2 de P05 (óptimo A1) no es confiable.** Para los dos objetivos (2 K y 5 K) da la MISMA P_baja
  (1251 kPa) y una caída de η de −3.7 pp. Además hay un hueco NO_CONVERGIO entre 1231 y 1248 kPa:
  el predicado no es monótono y la bisección saltó. En los otros 7 puntos el costo es coherente:
  - **2 K de subenfriamiento:** +25–46 kPa de P_baja y −0.3 a −0.5 pp de η;
  - **5 K:** +19–116 kPa y −0.3 a −1.2 pp.
- **Lectura para el informe.** El criterio O2 del código exige subenfriamiento ≥ 0 K al piso, sin un
  margen propio. Con las presiones del profesor (P03, P08), exigir 2 K cuesta ~25 kPa de P_baja
  (400 → ~425 kPa) y ≤ 0.5 pp de η. Es una corrección barata: no cambia ningún rango KALINA de forma
  material.
- **B1 (piso de 30.4 °C):** 9 de 12 pasan a CORREGIBLE con un déficit de 0.5–3.2 K. Eso equivale a lo
  anterior: subir el piso 3.5 K se come un margen que hoy es casi nulo.
