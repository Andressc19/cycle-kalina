# Sens2 etapa B - P(KALINA) con eps_cond simetrico

SIM centra eps_cond en 0.90 y lo perturba +-0.05 (uniforme); las otras nueve variables igual que en U1A. U1A centra eps_cond en el tope 0.95 y solo puede bajar. Los NO_CONVERGIO cuentan como no KALINA. Intervalo de Wilson de 95 %.

| centro | escenario | n | KALINA | P(KALINA) | IC 95 % | CORREGIBLE | INVIABLE | NO_CONVERGIO |
|---|---|---|---|---|---|---|---|---|
| C1 | SIM (eps_cond 0.90 +-0.05) | 48 | 12 | 0.25 | 0.15 a 0.39 | 36 | 0 | 0 |
| C1 | U1A (eps_cond 0.95 solo hacia abajo) | 48 | 23 | 0.48 | 0.34 a 0.62 | 25 | 0 | 0 |
| C2 | SIM (eps_cond 0.90 +-0.05) | 48 | 47 | 0.98 | 0.89 a 1.00 | 0 | 1 | 0 |
| C2 | U1A (eps_cond 0.95 solo hacia abajo) | 48 | 47 | 0.98 | 0.89 a 1.00 | 0 | 0 | 1 |
| C3 | SIM (eps_cond 0.90 +-0.05) | 48 | 30 | 0.62 | 0.48 a 0.75 | 18 | 0 | 0 |
| C3 | U1A (eps_cond 0.95 solo hacia abajo) | 48 | 48 | 1.00 | 0.93 a 1.00 | 0 | 0 | 0 |
| C4 | SIM (eps_cond 0.90 +-0.05) | 48 | 24 | 0.50 | 0.36 a 0.64 | 23 | 0 | 1 |
| C4 | U1A (eps_cond 0.95 solo hacia abajo) | 48 | 41 | 0.85 | 0.73 a 0.93 | 7 | 0 | 0 |
