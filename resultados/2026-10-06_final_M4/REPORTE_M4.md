# REPORTE M4 — sensibilidad global con LHS (10 variables a la vez)
## 1. La pregunta
Moviendo **las 10 variables a la vez** dentro de un rango favorable y realista: **¿qué variables deciden que el ciclo sea KALINA?, ¿en qué rango hay que ponerlas? y ¿qué combinaciones dan KALINA con mayor η?**
## 2. Qué se hizo, en simple
- **Muestreo.** 300 puntos con muestreo latino hipercubico (LHS, semilla 20261006): cada rango se divide en 300 franjas y cae exactamente un punto en cada franja de cada variable, así ninguna zona de la caja queda sin explorar. La muestra quedó en `m4_muestra.csv` ANTES de correr.
- **Corrida.** Los 300 puntos se resolvieron con el motor `teqp` y 5 procesos, con el piso de O2 de cada punto igual a su propia `T_sumidero`. Todo quedó en `m4_lhs.csv`.
- **Punto bueno (genuino).** Solo cuentan KALINA, CORREGIBLE e INVIABLE. Una fila que el solver cerró pero que el clasificador marca NO_CONVERGIO es un punto fijo espurio (N2) y es NO genuina en todo.
- **Análisis.** RSA (KS, valor p, IC95 % por bootstrap de 1000 remuestreos y rango favorable = percentiles 5–95) con cuatro separaciones; PAWN con 10 franjas; PRCC con rangos, residuos y prueba t; un árbol CART; la convergencia del ranking con los primeros 150 puntos; y el top-10.
## 3. Cuántos KALINA salieron
De **300** puntos: **76 KALINA**. Conteos por clase: CORREGIBLE = 181, KALINA = 76, NO_CONVERGIO = 34, INVIABLE = 9.
Puntos genuinos: 266. Espurios N2 (`convergio=True` y NO_CONVERGIO): 7. Fuera del rango confiable del motor de propiedades: 128.
## 4. Qué variables deciden KALINA y su rango favorable
Separación **KALINA vs el resto** (B = los 76 KALINA; B̄ = los 224 demás), ordenada por KS. El rango favorable es donde viven los KALINA (percentiles 5–95 dentro de B):

| variable | KS | IC95 % | valor p | rango favorable (p5–p95) | n_B | n_B̄ |
|---|---|---|---|---|---|---|
| P_baja | 0.436 | [0.356, 0.544] | 3.043e-10 | [689.621, 1459.7] | 76 | 224 |
| T_fuente | 0.355 | [0.272, 0.466] | 6.751e-07 | [382.81, 491.196] | 76 | 224 |
| rP | 0.354 | [0.283, 0.456] | 7.467e-07 | [1.67965, 5.45895] | 76 | 224 |
| eps_cond | 0.349 | [0.293, 0.488] | 1.19e-06 | [0.755767, 0.945828] | 76 | 224 |
| dT_fs | 0.329 | [0.252, 0.449] | 5.725e-06 | [89.8394, 204.032] | 76 | 224 |
| x_b | 0.236 | [0.166, 0.373] | 0.002883 | [0.513677, 0.799026] | 76 | 224 |
| T_sumidero | 0.163 | [0.105, 0.305] | 0.08735 | [279.041, 302.446] | 76 | 224 |
| eta_p | 0.163 | [0.095, 0.293] | 0.08735 | [0.661562, 0.887276] | 76 | 224 |
| P_alta | 0.148 | [0.095, 0.276] | 0.1489 | [2151.1, 4895.2] | 76 | 224 |
| dP | 0.140 | [0.120, 0.252] | 0.1963 | [904.309, 3742.45] | 76 | 224 |
| eps_reg | 0.130 | [0.085, 0.264] | 0.2671 | [0.62379, 0.933707] | 76 | 224 |
| eps_hrvg | 0.090 | [0.074, 0.252] | 0.7105 | [0.615698, 0.926253] | 76 | 224 |
| eta_t | 0.085 | [0.074, 0.221] | 0.7738 | [0.760173, 0.907765] | 76 | 224 |

**Aviso:** estos grupos quedaron con menos de 20 puntos y NO se amplió el muestreo por cuenta propia (el director decide):
- `cumple_O1/T_fuente: n_B=254, n_Bbar=12`
- `cumple_O1/T_sumidero: n_B=254, n_Bbar=12`
- `cumple_O1/P_alta: n_B=254, n_Bbar=12`
- `cumple_O1/P_baja: n_B=254, n_Bbar=12`
- `cumple_O1/x_b: n_B=254, n_Bbar=12`
- `cumple_O1/eta_t: n_B=254, n_Bbar=12`
- `cumple_O1/eta_p: n_B=254, n_Bbar=12`
- `cumple_O1/eps_hrvg: n_B=254, n_Bbar=12`
- `cumple_O1/eps_reg: n_B=254, n_Bbar=12`
- `cumple_O1/eps_cond: n_B=254, n_Bbar=12`
- `cumple_O1/dP: n_B=254, n_Bbar=12`
- `cumple_O1/rP: n_B=254, n_Bbar=12`
- `cumple_O1/dT_fs: n_B=254, n_Bbar=12`
### 4.1 Las otras separaciones (misma caja)
**Genuino vs no genuino:**

| variable | KS | IC95 % | valor p | rango favorable (p5–p95) | n_B | n_B̄ |
|---|---|---|---|---|---|---|
| dP | 0.355 | [0.216, 0.534] | 0.0006608 | [1039.97, 4055.19] | 266 | 34 |
| P_alta | 0.347 | [0.207, 0.546] | 0.0009727 | [2148.02, 4831.79] | 266 | 34 |
| T_fuente | 0.265 | [0.209, 0.446] | 0.02305 | [386.4, 492.364] | 266 | 34 |
| dT_fs | 0.241 | [0.196, 0.442] | 0.05034 | [93.4421, 206.42] | 266 | 34 |
| eta_t | 0.205 | [0.125, 0.396] | 0.1363 | [0.759704, 0.909921] | 266 | 34 |
| eps_hrvg | 0.203 | [0.119, 0.379] | 0.1434 | [0.6199, 0.93063] | 266 | 34 |
| eps_reg | 0.198 | [0.148, 0.336] | 0.1621 | [0.616278, 0.932478] | 266 | 34 |
| rP | 0.188 | [0.143, 0.387] | 0.2072 | [1.81857, 9.27693] | 266 | 34 |
| x_b | 0.161 | [0.134, 0.366] | 0.3752 | [0.519737, 0.829068] | 266 | 34 |
| eps_cond | 0.156 | [0.115, 0.314] | 0.4122 | [0.712997, 0.93821] | 266 | 34 |
| eta_p | 0.118 | [0.100, 0.317] | 0.7465 | [0.663262, 0.886811] | 266 | 34 |
| P_baja | 0.110 | [0.109, 0.295] | 0.8171 | [366.899, 1444.46] | 266 | 34 |
| T_sumidero | 0.081 | [0.107, 0.302] | 0.9789 | [279.553, 302.391] | 266 | 34 |

**Cumple O2 vs no (entre genuinos):**

| variable | KS | IC95 % | valor p | rango favorable (p5–p95) | n_B | n_B̄ |
|---|---|---|---|---|---|---|
| P_baja | 0.432 | [0.368, 0.556] | 6.962e-10 | [690.913, 1459.5] | 79 | 187 |
| eps_cond | 0.375 | [0.314, 0.504] | 1.758e-07 | [0.758635, 0.945797] | 79 | 187 |
| T_fuente | 0.369 | [0.286, 0.495] | 2.943e-07 | [382.889, 490.946] | 79 | 187 |
| dT_fs | 0.347 | [0.261, 0.468] | 1.856e-06 | [90.5573, 203.344] | 79 | 187 |
| rP | 0.316 | [0.256, 0.451] | 2.027e-05 | [1.68136, 5.90012] | 79 | 187 |
| x_b | 0.257 | [0.197, 0.398] | 0.0009761 | [0.513962, 0.798264] | 79 | 187 |
| T_sumidero | 0.173 | [0.101, 0.317] | 0.06189 | [279.065, 302.373] | 79 | 187 |
| eta_p | 0.168 | [0.098, 0.293] | 0.07662 | [0.662482, 0.887048] | 79 | 187 |
| P_alta | 0.165 | [0.100, 0.307] | 0.08358 | [2153.47, 4892.53] | 79 | 187 |
| dP | 0.129 | [0.104, 0.236] | 0.2821 | [904.571, 3765] | 79 | 187 |
| eps_hrvg | 0.118 | [0.079, 0.259] | 0.3879 | [0.616615, 0.925518] | 79 | 187 |
| eps_reg | 0.116 | [0.082, 0.232] | 0.4101 | [0.62116, 0.933344] | 79 | 187 |
| eta_t | 0.059 | [0.077, 0.226] | 0.9813 | [0.76019, 0.90981] | 79 | 187 |

**Cumple O1 vs no (entre genuinos):**

| variable | KS | IC95 % | valor p | rango favorable (p5–p95) | n_B | n_B̄ |
|---|---|---|---|---|---|---|
| rP | 0.850 | [0.815, 0.973] | 1.22e-09 | [1.80862, 8.66825] | 254 | 12 |
| dP | 0.740 | [0.701, 0.953] | 6.673e-07 | [1022.78, 3802.27] | 254 | 12 |
| P_baja | 0.732 | [0.646, 0.882] | 1.046e-06 | [371.521, 1446.82] | 254 | 12 |
| P_alta | 0.624 | [0.481, 0.858] | 8.241e-05 | [2143.42, 4746.2] | 254 | 12 |
| T_fuente | 0.396 | [0.255, 0.591] | 0.03912 | [386.752, 492.734] | 254 | 12 |
| dT_fs | 0.345 | [0.211, 0.551] | 0.1008 | [92.9947, 207.081] | 254 | 12 |
| T_sumidero | 0.314 | [0.228, 0.516] | 0.1683 | [279.525, 302.431] | 254 | 12 |
| eta_t | 0.309 | [0.240, 0.595] | 0.1804 | [0.759275, 0.908633] | 254 | 12 |
| eps_cond | 0.228 | [0.161, 0.534] | 0.5142 | [0.712281, 0.937892] | 254 | 12 |
| x_b | 0.205 | [0.185, 0.530] | 0.6442 | [0.522745, 0.829648] | 254 | 12 |
| eps_reg | 0.180 | [0.169, 0.488] | 0.7911 | [0.615641, 0.933308] | 254 | 12 |
| eps_hrvg | 0.169 | [0.165, 0.463] | 0.8426 | [0.61904, 0.931097] | 254 | 12 |
| eta_p | 0.131 | [0.157, 0.457] | 0.9739 | [0.664355, 0.887341] | 254 | 12 |
## 5. Qué variables mueven η y en qué sentido
**PAWN** (sobre η de los genuinos con W_net > 0 y sobre D de los genuinos; cuanto más alto el índice, más cambia la distribución al fijar la variable):

| variable | PAWN η (mediana) | PAWN η (máx) | PAWN D (mediana) | PAWN D (máx) |
|---|---|---|---|---|
| P_baja | 0.301 | 0.480 | 0.292 | 0.601 |
| P_alta | 0.222 | 0.430 | 0.153 | 0.255 |
| eta_p | 0.209 | 0.270 | 0.150 | 0.224 |
| eps_reg | 0.194 | 0.260 | 0.148 | 0.304 |
| T_fuente | 0.173 | 0.333 | 0.251 | 0.509 |
| x_b | 0.172 | 0.225 | 0.167 | 0.265 |
| eta_t | 0.172 | 0.371 | 0.139 | 0.192 |
| T_sumidero | 0.170 | 0.274 | 0.143 | 0.224 |
| eps_hrvg | 0.151 | 0.312 | 0.168 | 0.343 |
| eps_cond | 0.146 | 0.189 | 0.258 | 0.539 |

Las tres con más peso sobre η por PAWN: P_baja (0.301), P_alta (0.222), eta_p (0.209).

**PRCC** (negativo = subir la variable baja η; el IC95 % que no cruza al cero indica que el efecto se distingue del ruido):

| variable | PRCC η | IC95 % (η) | valor p (η) | PRCC m_O1 | PRCC m_O2 | PRCC m_O5 |
|---|---|---|---|---|---|---|
| P_baja | -0.661 | [-0.755, -0.567] | 1.312e-32 | 0.921 | 0.794 | 0.049 |
| P_alta | 0.578 | [0.476, 0.681] | 1.223e-23 | -0.886 | 0.343 | 0.091 |
| eta_t | 0.350 | [0.233, 0.468] | 1.36e-08 | -0.574 | 0.011 | -0.039 |
| T_fuente | 0.280 | [0.160, 0.401] | 7.042e-06 | -0.778 | -0.717 | -0.359 |
| x_b | 0.262 | [0.142, 0.383] | 2.738e-05 | 0.153 | -0.520 | -0.055 |
| eps_reg | 0.256 | [0.135, 0.378] | 4.218e-05 | -0.199 | -0.053 | 0.143 |
| eps_cond | 0.108 | [-0.016, 0.233] | 0.08862 | 0.045 | 0.763 | 0.050 |
| T_sumidero | -0.053 | [-0.178, 0.072] | 0.4031 | -0.129 | -0.572 | 0.033 |
| eps_hrvg | -0.038 | [-0.164, 0.087] | 0.5471 | -0.325 | -0.244 | -0.337 |
| eta_p | 0.006 | [-0.119, 0.132] | 0.9188 | -0.033 | 0.035 | -0.175 |

Las de mayor |PRCC| sobre η: P_baja (-0.661), P_alta (0.578), eta_t (0.350).
## 6. Las reglas del árbol, en palabras
Clasificador CART (`max_depth=4`, `min_samples_leaf=5`, `random_state=0`) sobre las 10 variables, KALINA vs no KALINA. exactitud CV (5 particiones): media = 0.7600 · por particion = [0.75, 0.7, 0.75, 0.8167, 0.7833].
- si P_baja <= 881.1 y eps_cond <= 0.9392 y eps_hrvg <= 0.6242 y x_b <= 0.678 → **KALINA** (n = 5, 60.0 % KALINA)
- si P_baja <= 881.1 y eps_cond <= 0.9392 y eps_hrvg <= 0.6242 y x_b > 0.678 → **no KALINA** (n = 6, 0.0 % KALINA)
- si P_baja <= 881.1 y eps_cond <= 0.9392 y eps_hrvg > 0.6242 y T_sumidero <= 281.6 → **no KALINA** (n = 18, 16.7 % KALINA)
- si P_baja <= 881.1 y eps_cond <= 0.9392 y eps_hrvg > 0.6242 y T_sumidero > 281.6 → **no KALINA** (n = 110, 0.9 % KALINA)
- si P_baja <= 881.1 y eps_cond > 0.9392 → **KALINA** (n = 6, 83.3 % KALINA)
- si P_baja > 881.1 y eps_cond <= 0.9029 y x_b <= 0.5858 y eta_p <= 0.7193 → **no KALINA** (n = 9, 33.3 % KALINA)
- si P_baja > 881.1 y eps_cond <= 0.9029 y x_b <= 0.5858 y eta_p > 0.7193 → **KALINA** (n = 22, 81.8 % KALINA)
- si P_baja > 881.1 y eps_cond <= 0.9029 y x_b > 0.5858 y T_fuente <= 400.8 → **KALINA** (n = 14, 64.3 % KALINA)
- si P_baja > 881.1 y eps_cond <= 0.9029 y x_b > 0.5858 y T_fuente > 400.8 → **no KALINA** (n = 80, 10.0 % KALINA)
- si P_baja > 881.1 y eps_cond > 0.9029 y eta_t <= 0.8826 y eps_reg <= 0.9163 → **KALINA** (n = 20, 100.0 % KALINA)
- si P_baja > 881.1 y eps_cond > 0.9029 y eta_t <= 0.8826 y eps_reg > 0.9163 → **KALINA** (n = 5, 80.0 % KALINA)
- si P_baja > 881.1 y eps_cond > 0.9029 y eta_t > 0.8826 → **no KALINA** (n = 5, 40.0 % KALINA)
## 7. Los diferenciales recomendados dentro de KALINA
Las tres variables derivadas, con su KS en la separación KALINA y su rango favorable (percentiles 5–95 dentro de los KALINA): dP: KS 0.140 y rango favorable [904.309, 3742.45], rP: KS 0.354 y rango favorable [1.67965, 5.45895], dT_fs: KS 0.329 y rango favorable [89.8394, 204.032].
## 8. Los 10 mejores KALINA
Los 10 KALINA de mayor η de la corrida:

| # | id | η | W_net (kW) | D | T_fuente | T_sumidero | P_alta | P_baja | x_b | eta_t | eta_p | eps_hrvg | eps_reg | eps_cond |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 286.0 | 0.1230 | 91.42 | 0.00 | 436.097 | 279.098 | 3481.82 | 808.34 | 0.634749 | 0.918483 | 0.746081 | 0.677731 | 0.94153 | 0.841826 |
| 2 | 20.0 | 0.1091 | 57.84 | 0.00 | 414.265 | 287.822 | 4841.78 | 1106.65 | 0.676679 | 0.826498 | 0.818212 | 0.869164 | 0.90437 | 0.794862 |
| 3 | 149.0 | 0.1085 | 80.10 | 0.00 | 428.033 | 296.004 | 4127.89 | 882.806 | 0.671542 | 0.771052 | 0.807274 | 0.788939 | 0.912477 | 0.931908 |
| 4 | 153.0 | 0.1077 | 85.08 | 0.00 | 441.069 | 292.126 | 3213.43 | 607.329 | 0.53951 | 0.816012 | 0.663761 | 0.756381 | 0.840128 | 0.945982 |
| 5 | 213.0 | 0.1064 | 47.00 | 0.00 | 402.978 | 281.559 | 4312.31 | 691.773 | 0.650244 | 0.7954 | 0.886896 | 0.859285 | 0.787737 | 0.798693 |
| 6 | 76.0 | 0.1061 | 152.51 | 0.00 | 490.779 | 287.893 | 4594.56 | 1315.79 | 0.820547 | 0.852919 | 0.730311 | 0.802814 | 0.926377 | 0.930827 |
| 7 | 15.0 | 0.1054 | 26.53 | 0.00 | 384.399 | 291.539 | 3558.44 | 668.347 | 0.675123 | 0.86271 | 0.755245 | 0.623233 | 0.913052 | 0.866496 |
| 8 | 257.0 | 0.1025 | 91.39 | 0.00 | 421.452 | 279.365 | 2761.69 | 709.67 | 0.735446 | 0.854067 | 0.824452 | 0.651982 | 0.685112 | 0.941753 |
| 9 | 291.0 | 0.1015 | 71.06 | 0.00 | 437.984 | 283.738 | 3396.52 | 775.802 | 0.626187 | 0.801803 | 0.891814 | 0.600039 | 0.880646 | 0.925209 |
| 10 | 157.0 | 0.0995 | 128.94 | 0.00 | 475.008 | 283.528 | 3942.23 | 1239.94 | 0.82444 | 0.859118 | 0.666887 | 0.738725 | 0.811315 | 0.920168 |
## 9. La convergencia
ρ de Spearman entre el ranking con los primeros 150 puntos y el de los 300: **KS (KALINA) = 0.8407** y **PRCC(η) = 0.9515**. Variables que cambian 2 o más posiciones: KS T_sumidero (9 → 7), KS eta_p (13 → 8), KS eps_reg (7 → 11), KS eps_cond (2 → 4), KS rP (5 → 3), PRCC T_sumidero (10 → 8).
## 10. Los tiempos
La corrida completa (300 corridas) tardó 9374 s (156 min). Por punto (`t_s`): mínimo 29.8 s, mediana 142.1 s, máximo 354.1 s, media 153.7 s (300 puntos).
## 11. La conclusión
El RSA de §4 dice qué variables separan KALINA del resto y en qué rango viven los KALINA; PAWN y PRCC de §5 dicen qué variables mueven η y en qué sentido; el árbol de §6 da reglas sí/no que se leen directo; y §7 da los diferenciales (dP, rP, dT_fs) recomendados dentro de KALINA. No se propone ningún valor nuevo: las tablas son insumos para que el director decida.
## 12. Lo que no se sabe
- Las diferencias de η menores que 0.4–0.7 pp no son concluyentes: es la banda de incertidumbre del modelo de propiedades (G4-01).
- Hay puntos fuera de rango (motor de propiedades sin respaldo experimental): 128 de 300. Sus η hay que tomarlas con pinzas.
- Esto es una **caja favorable**, no todo el espacio: fuera de los rangos de `TASK_CONTEXT final_M4` no se dijo nada.
## 13. Qué sigue
M5 (búsqueda dirigida hacia KALINA con las variables que señala el RSA). El orden concreto lo decide el director.

## 14. Nota del director (Claude, auditoría 2026-10-06)

- **Convergencia por debajo del criterio del protocolo.** MATEMATICA §6.6 fija ρ ≥ 0.9 entre los
  rankings con 150 y con 300 puntos. PRCC(η) cumple (0.95); el ranking KS de KALINA **no** cumple
  (0.84). Lo estable es: P_baja es la 1.ª variable en ambos rankings, y T_fuente, rP, ε_cond y
  dT_fs están en el top-5 en ambos. Las posiciones intermedias e inferiores (T_sumidero, η_p,
  ε_reg) se mueven 2–5 puestos: su orden relativo **no** es concluyente. Para cerrarlo haría falta
  ampliar el LHS (por ejemplo, a 500 puntos); queda como decisión pendiente.
- **Rango confiable:** 128 de 300 puntos (y 19 de los 76 KALINA) tienen líquido > 420 K (G4-01 sin
  respaldo experimental). Todos los KALINA tienen `B_verificado = True`.
- **Límite de líneas:** `m4_verificar.py` tiene 232 líneas (> 200). Es el verificador, no afecta
  los resultados; se deja anotado.

