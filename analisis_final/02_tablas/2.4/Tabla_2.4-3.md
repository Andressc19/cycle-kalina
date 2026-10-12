# Tabla 2.4-3 · Malla T_sumidero x P_baja por base

**Estudio 2.4** · Sumidero más frío · **Partes:** 2.4a, 2.4b, 2.4c, 2.4d  
**Punto base:** 2.4a a 2.4d = cuatro bases distintas (una por parte)  
**Parte 2.4a (fuente a 403 K):**  
**Datos fijos: T_fuente = 403 K; P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp.**  
**Datos barridos: T_sumidero [278.15–300.03] K (5 valores); P_baja [150–1500] kPa (28 valores); piso de O2 [278.15–300.03] K (5 valores).**  
**Parte 2.4b (fuente a 420 K):**  
**Datos fijos: T_fuente = 420 K; P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp.**  
**Datos barridos: T_sumidero [278.15–300.03] K (5 valores); P_baja [150–1500] kPa (28 valores); piso de O2 [278.15–300.03] K (5 valores).**  
**Parte 2.4c (ε_HRVG = 0.40 (fuente del profesor)):**  
**Datos fijos: T_fuente = 623.15 K; P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.4; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp.**  
**Datos barridos: T_sumidero [278.15–300.03] K (5 valores); P_baja [150–1500] kPa (30 valores); piso de O2 [278.15–300.03] K (5 valores).**  
**Parte 2.4d (datos exactos del profesor):**  
**Datos fijos: T_fuente = 623.15 K; P_alta = 3000 kPa; x_b = 0.5; m_b = 1 kg/s; η_t = 0.85; η_p = 0.75; ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.8; motor de propiedades = teqp.**  
**Datos barridos: T_sumidero [278.15–300.03] K (5 valores); P_baja [150–1500] kPa (10 valores); piso de O2 [278.15–300.03] K (5 valores).**  

| Base | Temperatura del sumidero, T_sumidero [K] | Genuinos | KALINA | Falsos convergidos | P_baja mínima KALINA [kPa] | η mínima KALINA [%] | B verificado en la mínima KALINA | Fuera de rango en la mínima KALINA | η máxima KALINA [%] | P_baja en la η máxima KALINA [kPa] | Bloqueantes (genuinos) | Códigos de bloqueo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | 278.1 | 18 | 11 | 0 | 290.6 | 10.41 | sí | no | 10.41 | 290.6 | CORREGIBLE(7) | O2(7) |
| B1 | 283.1 | 18 | 12 | 0 | 337.5 | 10.03 | sí | no | 10.03 | 337.5 | CORREGIBLE(6) | O2(6) |
| B1 | 288.1 | 18 | 12 | 0 | 393.8 | 9.61 | sí | no | 9.61 | 393.8 | CORREGIBLE(6) | O2(6) |
| B1 | 293.1 | 18 | 15 | 0 | 459.4 | 9.14 | sí | no | 9.14 | 459.4 | CORREGIBLE(2) · INVIABLE(1) | O2(3) · O3(1) |
| B1 | 300.0 | 18 | 9 | 0 | 562.5 | 8.49 | sí | no | 8.49 | 562.5 | CORREGIBLE(8) · INVIABLE(1) | O2(9) · O3(1) |
| B2 | 278.1 | 18 | 12 | 0 | 393.8 | 11.91 | sí | no | 11.91 | 393.8 | CORREGIBLE(6) | O2(6) · O1(1) |
| B2 | 283.1 | 18 | 15 | 0 | 459.4 | 11.28 | sí | no | 11.28 | 459.4 | CORREGIBLE(3) | O2(3) · O1(1) |
| B2 | 288.1 | 18 | 13 | 0 | 534.4 | 10.62 | sí | no | 10.62 | 534.4 | CORREGIBLE(5) | O2(5) · O1(1) |
| B2 | 293.1 | 18 | 12 | 0 | 618.8 | 9.96 | sí | no | 9.96 | 618.8 | CORREGIBLE(6) | O2(6) · O1(1) |
| B2 | 300.0 | 18 | 8 | 0 | 740.6 | 9.11 | sí | no | 9.11 | 740.6 | CORREGIBLE(9) · INVIABLE(1) | O2(10) · O1(1) · O3(1) |
| B3 | 278.1 | 17 | 6 | 0 | 750.0 | 9.69 | sí | sí | 9.69 | 750.0 | CORREGIBLE(11) | O2(11) · O1(1) |
| B3 | 283.1 | 18 | 7 | 0 | 862.5 | 8.89 | sí | sí | 8.89 | 862.5 | CORREGIBLE(11) | O2(11) · O1(2) |
| B3 | 288.1 | 18 | 10 | 0 | 984.4 | 8.11 | sí | sí | 8.11 | 984.4 | CORREGIBLE(8) | O2(8) · O1(2) |
| B3 | 293.1 | 18 | 7 | 0 | 1116 | 7.34 | sí | sí | 7.34 | 1116 | CORREGIBLE(11) | O2(11) · O1(2) |
| B3 | 300.0 | 18 | 4 | 0 | 1312 | 6.30 | sí | sí | 6.30 | 1312 | CORREGIBLE(14) | O2(14) · O1(2) |
| B4 | 278.1 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |
| B4 | 283.1 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |
| B4 | 288.1 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |
| B4 | 293.1 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |
| B4 | 300.0 | 0 | 0 | 0 |  |  |  |  |  |  |  |  |

**Notas:** Filtro: todos los puntos de la malla. n = 20 filas en la tabla. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido. Fuente: resultados/2026-10-06_final_M2S/m2s_resumen.csv.
