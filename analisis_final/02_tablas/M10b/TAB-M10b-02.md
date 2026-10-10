# TAB-M10b-02 · Frontera KALINA al variar x_b (Húsavík, x_b bajo)

**Caso(s):** KF-M10b · **Bloque(s):** B14-OFATb, B14-MALLA  
**Punto base:** Húsavík con x_b bajo  
**Datos fijos: T_fuente = 394.15 K; T_sumidero = 278.15 K; P_alta = 3300 kPa; m_b = 1 kg/s; eta_t = 0.9; eta_p = 0.8; eps_hrvg = 0.85; eps_reg = 0.75; eps_cond = 0.95; T_amb_diseno = 283.15 K; motor = teqp.**  
**Datos barridos: P_baja [200–700] kPa (6 valores); x_b [0.3–0.7] (17 valores).**  

| x_b | P_baja mínima KALINA [kPa] | η en ese punto [%] | Criterio que más bloquea |
|---|---|---|---|
| 0.300 |  |  |  |
| 0.350 |  |  |  |
| 0.400 |  |  | O3 |
| 0.450 |  |  | O3 |
| 0.500 | 200.0 | 1.23 |  |
| 0.550 | 300.0 | 9.56 | O2 |
| 0.600 | 400.0 | 11.64 | O2 |
| 0.650 | 500.0 | 12.17 | O2 |
| 0.700 | 500.0 | 13.31 | O2 |

**Notas:** Filtro: todos los puntos de KF-M10b-MALLA. n = 9. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido (N2). Fuente: canónico (KF-M10b-MALLA). Una fila por valor de x_b; el criterio cuenta solo O1/O2/O3/O5.
