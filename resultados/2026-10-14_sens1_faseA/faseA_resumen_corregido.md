# Sensibilidad 1 — Fase A: resumen CORREGIDO (base incluida en cada barrido)

El resumen original (`faseA_resumen_variables.csv`) no contaba dentro de cada barrido el punto base (que la corrida deduplica con `variable="base"`). Aquí se añade la fila base de cada centro al conjunto de puntos de cada variable, con su `valor` = valor base de esa variable, y se recalcula todo. Fuente: `faseA_filas.csv`.

## Centro C1

| variable | n KALINA | KALINA confiables | valores KALINA | η min [%] | η max [%] | INVIABLE | contiguo |
|---|---|---|---|---|---|---|---|
| base | 1 | 1 | — | 11.9998 | 11.9998 | 0 | — |
| T_fuente | 16 | 15 | 363.15–438.15 | 10.2727 | 12.6604 | 0 | sí |
| T_sumidero | 3 | 3 | 278.15–283.15 | 11.9998 | 12.2174 | 0 | sí |
| P_alta | 14 | 14 | 2000–5000 | 8.8975 | 13.1712 | 0 | sí |
| P_baja | 11 | 11 | 600–1500 | 6.3018 | 12.9634 | 0 | sí |
| x_b | 9 | 9 | 0.55–0.9 | 5.8978 | 12.5771 | 1 | sí |
| eta_t | 12 | 12 | 0.4–0.95 | 5.3926 | 13.4636 | 0 | sí |
| eta_p | 12 | 12 | 0.4–0.95 | 11.5389 | 12.0723 | 0 | sí |
| eps_hrvg | 12 | 12 | 0.4–0.95 | 9.4541 | 12.3232 | 0 | sí |
| eps_reg | 12 | 12 | 0.4–0.95 | 11.2541 | 12.4622 | 0 | sí |
| eps_cond | 1 | 1 | 0.95–0.95 | 11.9998 | 11.9998 | 0 | sí |

## Centro C2

| variable | n KALINA | KALINA confiables | valores KALINA | η min [%] | η max [%] | INVIABLE | contiguo |
|---|---|---|---|---|---|---|---|
| base | 1 | 1 | — | 7.9405 | 7.9405 | 0 | — |
| T_fuente | 14 | 8 | 393.15–463.15 | 4.4143 | 11.2394 | 1 | sí |
| T_sumidero | 12 | 12 | 278.15–303.15 | 7.0792 | 8.0726 | 0 | sí |
| P_alta | 8 | 8 | 2000–3750 | 1.8142 | 8.6521 | 0 | sí |
| P_baja | 13 | 13 | 400–1500 | 2.9757 | 9.5108 | 0 | sí |
| x_b | 3 | 3 | 0.45–0.55 | 3.7355 | 9.9385 | 3 | sí |
| eta_t | 12 | 12 | 0.4–0.95 | 3.0881 | 9.0175 | 0 | sí |
| eta_p | 12 | 12 | 0.4–0.95 | 6.8953 | 8.1909 | 0 | sí |
| eps_hrvg | 12 | 12 | 0.4–0.95 | 1.9224 | 8.4929 | 0 | sí |
| eps_reg | 12 | 12 | 0.4–0.95 | 5.2661 | 10.5930 | 0 | sí |
| eps_cond | 4 | 4 | 0.8–0.95 | 7.9405 | 8.4872 | 0 | sí |

## Verificación (esperado)

- **C1 T_sumidero** → n KALINA = **3** (esperado 3)
- **C1 eps_cond** → n KALINA = **1** (esperado 1)

