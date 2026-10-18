# Sens2 P4 - resumen y preseleccion de equipos

Numeros de `p4_envolventes.csv`, `p4_dependencias.csv`, `p4_restricciones.csv` y `p4_bandas.csv`. Rangos = P5-P95 de KALINA (total).
Cantidades extensivas por kg/s de m_b. Presiones en kPa, T en K, h en kJ/kg.

## Preseleccion por equipo

- **Turbina.** rp 1.698-5.508; dh_turb 65.251-230.431; Wt_mb 10.722-145.931; q4 0.923-0.980; T3 361.230-443.186; T4 296.026-405.135; m_v_mb 0.083-0.887. Lo fija: rp->P_alta, dh_turb->P_baja, Wt_mb->T_fuente, q4->P_alta.
- **Regenerador.** dT_A 24.620-126.411; dT_B 9.652-46.695; pinch_reg 9.652-46.695; LMTD_reg 18.673-73.640; UA_reg 0.759-13.326; qreg_qi 0.031-1.305. Lo fija: pinch_reg->eps_reg, UA_reg->eps_reg, qreg_qi->x_b.
- **Condensador.** Qout_mb 217.985-1561.330; aprox_cond_sal 2.614-23.408; aprox_cond_ent 20.735-115.419. Lo fija: Qout_mb->T_fuente, aprox_cond_sal->eps_cond.
- **HRVG.** Qi_mb 228.783-1695.276; aprox_fuente 2.110-43.980. Lo fija: Qi_mb->T_fuente.
- **Bomba.** Wp_mb 1.418-6.174; Wp_Wt 0.024-0.301; P_alta 1940.000-4500.000; P_baja 563.640-1600.000. Lo fija: Wp_Wt->T_fuente.

## Restriccion activa y regimen de la turbina

- Titulo de turbina (O1): el minimo de q4 en KALINA es 0.9014; en los CORREGIBLE, 6.8 % tiene q4 < 0.90.
- Regenerador: no hay cruces en KALINA (pinch <= 0 en 0.0000 de los puntos); el pinch P5 es 9.652 K.
- Condensador y bomba (O2): 52.6 % de los CORREGIBLE tiene (T9 - T_sumidero) por debajo de la mediana de los KALINA.
- La turbina entrega mas dh_turb y mas eta a rp alto: la banda [6, 10) lidera ambas (regresion dh_turb ~ rp global: pendiente 30.22 kJ/kg por unidad de rp, R2 0.646).

## Limites de este analisis

- Los rangos P5-P95 son la envolvente de un muestreo numerico, no especificaciones de compra: no fijan geometria, caidas de presion, materiales ni margen de diseno.
- `LMTD_reg` y `UA_reg` salen del calor Qreg y de las temperaturas de estado; son por kg/s de m_b y suponen contraflujo puro, sin correccion por configuracion.
- `aprox_cond_sal`, `aprox_cond_ent` y `aprox_fuente` son diferencias de temperatura frente al sumidero o la fuente; no son un pinch de diseno.
- El modelo usa el metodo de efectividad para HRVG, regenerador y condensador; aqui el LMTD se reconstruye a partir de los estados, no sustituye a ese modelo.
- KALINA (total) incluye los puntos fuera del rango experimental (liquido > 420 K); el conjunto dentro del rango se reporta aparte.
- El balance del regenerador se comprueba en el control (e); ninguna cantidad derivada se inventa: todas salen de un archivo.
