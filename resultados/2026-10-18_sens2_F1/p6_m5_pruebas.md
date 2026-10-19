# Sens2 F1 - M5 con dos pruebas (KS y Mann-Whitney)

Distancia L1 normalizada a la frontera no-KALINA del 10 % de KALINA de mayor eta frente al resto, por bloque, solo con las filas LHS (estudios 3 y 14).
`completo` normaliza con los limites del conjunto completo (la del libro); `lhs`, con los de las propias filas LHS. Bonferroni por 4 bloques (tope 1).

| normalizacion | bloque | n top | n resto | mediana top | mediana resto | p (KS) | p (KS, Bonf) | p (MW) | p (MW, Bonf) |
|---|---|---|---|---|---|---|---|---|---|
| completo | C1 Husavik | 12 | 106 | 0.62 | 0.75 | 0.016 | 0.064 | 0.044 | 0.175 |
| completo | C2 ancla A* | 14 | 117 | 0.79 | 0.83 | 0.633 | 1.000 | 0.500 | 1.000 |
| completo | C3 caliente 150 C | 13 | 108 | 0.82 | 0.90 | 0.092 | 0.366 | 0.029 | 0.114 |
| completo | C4 frio 110 C | 14 | 123 | 0.83 | 0.81 | 0.478 | 1.000 | 0.626 | 1.000 |
| lhs | C1 Husavik | 12 | 106 | 0.94 | 1.11 | 0.086 | 0.343 | 0.049 | 0.194 |
| lhs | C2 ancla A* | 14 | 117 | 1.09 | 1.19 | 0.454 | 1.000 | 0.331 | 1.000 |
| lhs | C3 caliente 150 C | 13 | 108 | 1.07 | 1.30 | 0.003 | 0.010 | 0.003 | 0.012 |
| lhs | C4 frio 110 C | 14 | 123 | 1.26 | 1.19 | 0.770 | 1.000 | 0.497 | 1.000 |

De las 8 combinaciones (2 normalizaciones x 4 bloques), sale p < 0.05 en 2 con KS y en 4 con Mann-Whitney.
Con Bonferroni (x4) sigue saliendo p < 0.05 en 1 con KS y en 1 con Mann-Whitney.
Control: la mayor diferencia de p_ks frente a p6_m5_lhs.csv es 9.02e-17 (tolerancia 1e-9).
