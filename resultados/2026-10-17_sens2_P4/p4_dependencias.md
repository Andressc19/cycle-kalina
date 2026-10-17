# Sens2 P4 - Paso 2: que variable fija cada requisito

Spearman (rho, p) de cada cantidad de equipo con las 10 entradas, por
centro, sobre KALINA (total) de los estudios LHS 3 y 14 (entradas
variando a la vez). Las 3 asociaciones mas fuertes por cantidad:
|rho| mayor, con su signo. `eta_p` es constante en el LHS: sale sin
varianza (n y rho = .).

## C1 Husavik

| cantidad | 1a variable (rho, p) | 2a variable (rho, p) | 3a variable (rho, p) |
|---|---|---|---|
| rp | P_alta (+0.699, 1.3e-18) / P_baja (-0.646, 2.8e-15) / T_fuente (+0.179, 0.053) |
| dh_turb | P_baja (-0.611, 2.1e-13) / eta_t (+0.586, 3e-12) / P_alta (+0.429, 1.2e-06) |
| Wt_mb | T_fuente (+0.580, 5.8e-12) / eps_cond (+0.402, 6.4e-06) / eta_t (+0.334, 0.00022) |
| q4 | P_alta (-0.656, 7.8e-16) / eta_t (-0.493, 1.5e-08) / P_baja (+0.317, 0.00047) |
| UA_reg | eps_reg (+0.788, 3e-26) / eps_cond (-0.400, 7.3e-06) / x_b (-0.342, 0.00015) |
| pinch_reg | eps_reg (-0.920, 6.9e-49) / T_fuente (+0.344, 0.00014) / eps_cond (+0.270, 0.0031) |
| qreg_qi | x_b (-0.490, 1.7e-08) / eps_reg (+0.467, 9.9e-08) / eps_cond (-0.359, 6.4e-05) |
| Qout_mb | T_fuente (+0.548, 1.3e-10) / eps_cond (+0.433, 1e-06) / eps_hrvg (+0.375, 2.9e-05) |
| aprox_cond_sal | eps_cond (-0.597, 9.2e-13) / P_baja (+0.313, 0.00055) / T_fuente (+0.236, 0.01) |
| Qi_mb | T_fuente (+0.562, 3.5e-11) / eps_cond (+0.436, 7.8e-07) / eps_hrvg (+0.372, 3.3e-05) |
| Wp_Wt | P_alta (+0.438, 7.1e-07) / T_fuente (-0.417, 2.7e-06) / eta_t (-0.385, 1.7e-05) |

## C2 ancla A*

| cantidad | 1a variable (rho, p) | 2a variable (rho, p) | 3a variable (rho, p) |
|---|---|---|---|
| rp | P_baja (-0.770, 5.8e-27) / P_alta (+0.545, 1.7e-11) / eps_cond (+0.239, 0.0059) |
| dh_turb | P_baja (-0.660, 1.1e-17) / eta_t (+0.656, 1.7e-17) / P_alta (+0.381, 7e-06) |
| Wt_mb | T_fuente (+0.664, 5.7e-18) / eps_cond (+0.397, 2.7e-06) / eta_t (+0.303, 0.00043) |
| q4 | eta_t (-0.721, 2.8e-22) / P_baja (+0.498, 1.5e-09) / P_alta (-0.433, 2.5e-07) |
| UA_reg | eps_reg (+0.877, 7e-43) / T_fuente (-0.343, 6.1e-05) / eps_cond (-0.244, 0.0049) |
| pinch_reg | eps_reg (-0.946, 9e-65) / eps_cond (+0.281, 0.0012) / T_fuente (+0.255, 0.0032) |
| qreg_qi | T_fuente (-0.500, 1.2e-09) / eps_reg (+0.485, 4.4e-09) / x_b (-0.286, 0.00091) |
| Qout_mb | T_fuente (+0.687, 1.2e-19) / eps_cond (+0.421, 5.4e-07) / eps_reg (-0.297, 0.00057) |
| aprox_cond_sal | eps_cond (-0.689, 9e-20) / T_fuente (+0.232, 0.0076) / P_baja (+0.227, 0.0091) |
| Qi_mb | T_fuente (+0.691, 6.8e-20) / eps_cond (+0.431, 2.8e-07) / eps_hrvg (+0.288, 0.00084) |
| Wp_Wt | T_fuente (-0.533, 5.6e-11) / eta_t (-0.323, 0.00017) / eps_cond (-0.301, 0.00048) |

## C3 caliente 150 C

| cantidad | 1a variable (rho, p) | 2a variable (rho, p) | 3a variable (rho, p) |
|---|---|---|---|
| rp | P_alta (+0.661, 1.6e-16) / P_baja (-0.604, 2.2e-13) / eta_t (-0.139, 0.13) |
| dh_turb | P_alta (+0.600, 3.7e-13) / P_baja (-0.469, 5.7e-08) / eta_t (+0.302, 0.00078) |
| Wt_mb | T_fuente (+0.525, 6.6e-10) / x_b (+0.479, 2.6e-08) / eps_hrvg (+0.381, 1.6e-05) |
| q4 | P_alta (-0.749, 5.5e-23) / eta_t (-0.348, 9.2e-05) / T_fuente (-0.300, 0.00082) |
| UA_reg | eps_reg (+0.644, 1.7e-15) / x_b (-0.418, 1.8e-06) / T_fuente (-0.392, 8.7e-06) |
| pinch_reg | eps_reg (-0.862, 6.9e-37) / T_fuente (+0.399, 6e-06) / x_b (-0.213, 0.019) |
| qreg_qi | x_b (-0.585, 1.8e-12) / T_fuente (-0.356, 6.1e-05) / P_baja (-0.292, 0.0011) |
| Qout_mb | T_fuente (+0.623, 2.2e-14) / eps_hrvg (+0.447, 2.7e-07) / x_b (+0.329, 0.00023) |
| aprox_cond_sal | eps_cond (-0.477, 3.1e-08) / T_fuente (+0.403, 4.6e-06) / x_b (+0.290, 0.0013) |
| Qi_mb | T_fuente (+0.622, 2.6e-14) / eps_hrvg (+0.452, 1.9e-07) / x_b (+0.340, 0.00014) |
| Wp_Wt | T_fuente (-0.491, 1.1e-08) / eps_hrvg (-0.454, 1.7e-07) / P_alta (+0.352, 7.6e-05) |

## C4 frio 110 C

| cantidad | 1a variable (rho, p) | 2a variable (rho, p) | 3a variable (rho, p) |
|---|---|---|---|
| rp | P_alta (+0.767, 8e-28) / P_baja (-0.517, 1e-10) / eta_t (-0.131, 0.13) |
| dh_turb | P_alta (+0.699, 2e-21) / P_baja (-0.382, 4.2e-06) / eta_t (+0.312, 0.00021) |
| Wt_mb | x_b (+0.571, 3.2e-13) / T_fuente (+0.501, 4.7e-10) / eps_hrvg (+0.373, 7.1e-06) |
| q4 | P_alta (-0.834, 1.1e-36) / eta_t (-0.280, 0.00091) / T_fuente (-0.193, 0.023) |
| UA_reg | eps_reg (+0.615, 1.2e-15) / x_b (-0.493, 9.2e-10) / T_fuente (-0.389, 2.7e-06) |
| pinch_reg | eps_reg (-0.907, 1.3e-52) / T_fuente (+0.279, 0.00095) / P_alta (+0.192, 0.025) |
| qreg_qi | x_b (-0.622, 5.3e-16) / T_fuente (-0.364, 1.2e-05) / eps_hrvg (-0.327, 9.7e-05) |
| Qout_mb | T_fuente (+0.557, 1.6e-12) / x_b (+0.478, 3.5e-09) / eps_hrvg (+0.457, 1.9e-08) |
| aprox_cond_sal | eps_cond (-0.511, 1.7e-10) / x_b (+0.388, 2.8e-06) / T_fuente (+0.315, 0.00017) |
| Qi_mb | T_fuente (+0.561, 1e-12) / x_b (+0.490, 1.2e-09) / eps_hrvg (+0.465, 1e-08) |
| Wp_Wt | P_alta (+0.486, 1.7e-09) / T_fuente (-0.431, 1.5e-07) / eps_hrvg (-0.426, 2.1e-07) |

## Regresion de dh_turb sobre rp (minimos cuadrados)

| centro | n | pendiente | intercepto | R2 |
|---|---|---|---|---|
| C1 Husavik | 118 | 23.7064 | 44.7062 | 0.518 |
| C2 ancla A* | 131 | 28.8453 | 42.8718 | 0.584 |
| C3 caliente 150 C | 121 | 30.5121 | 21.2574 | 0.677 |
| C4 frio 110 C | 137 | 31.3947 | 11.5871 | 0.694 |
| todos | 507 | 30.2218 | 23.8179 | 0.646 |

Lectura: rho > 0 = al subir la entrada sube la cantidad; los p-valores
son indicativos (n y diseno del LHS, no muestreo aleatorio puro).
