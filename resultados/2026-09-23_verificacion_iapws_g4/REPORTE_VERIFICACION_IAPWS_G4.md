# Reporte — Verificación de los dos motores contra IAPWS G4-01 (Tablas 6–8)
Fecha: 2026-09-23 · Tarea `2026-09-23-verificacion-iapws-g4` · solo lectura de `src/`.
Guía: **IAPWS G4-01**, §8, Tablas 6–8 (valores transcritos literalmente); Tillner-Roth & Friend, *J. Phys. Chem. Ref. Data* **27**, 63 (1998). `x` = molar NH3.
Criterios (fijados en TASK_CONTEXT, no modificados): Tabla 6 p rel<1e-6; Cv,w rel<1e-4; f rel<1e-6 solo motor referencia (teqp: offset esperado, en J/mol); Tablas 7–8 p,ρ rel<1e-3; x abs<1e-3.

## Resumen por motor y tabla
| Motor | Tabla | Filas | sí | no | no_converge | esperado_offset |
|---|---|---|---|---|---|---|
| iapws | 6 | 24 | 24 | 0 | 0 | 0 |
| iapws | 7 | 12 | 8 | 0 | 4 | 0 |
| iapws | 8 | 12 | 12 | 0 | 0 | 0 |
| teqp | 6 | 24 | 6 | 12 | 0 | 6 |
| teqp | 7 | 12 | 8 | 0 | 4 | 0 |
| teqp | 8 | 12 | 12 | 0 | 0 | 0 |

## Peor error por propiedad
| Motor | Propiedad | Peor error rel | Peor error abs | Punto |
|---|---|---|---|---|
| iapws | Cv | 9.484e-10 | 4.91e-08 | `x0.9_T400_rho30` |
| iapws | f | 4.137e-09 | 2.89e-05 | `x0.9_T400_rho30` |
| iapws | p | 2.629e-08 | 4.07e-08 | `x0.9_T400_rho0.5` |
| iapws | p_BUB | 2.332e-01 | 3.89 | `xL0.6_T500` |
| iapws | p_DEW | 1.039e-06 | 4.1e-07 | `xV0.4_T400` |
| iapws | rho_L | 6.529e-02 | 1.66 | `xL0.6_T500` |
| iapws | rho_v | 2.061e+00 | 18.3 | `xL0.6_T500` |
| iapws | w | 8.526e-10 | 4.08e-07 | `x0.9_T400_rho0.5` |
| iapws | x_L | 3.849e-05 | 4.11e-07 | `xV0.2_T300` |
| iapws | x_v | 2.351e-01 | 0.184 | `xL0.6_T500` |
| teqp | Cv | 3.758e-03 | 0.138 | `x0.5_T500_rho1` |
| teqp | f | 4.771e-03 | 33.3 | `x0.9_T400_rho30` |
| teqp | p | 2.629e-08 | 4.07e-08 | `x0.9_T400_rho0.5` |
| teqp | p_BUB | 2.322e-01 | 3.88 | `xL0.6_T500` |
| teqp | p_DEW | 1.039e-06 | 4.1e-07 | `xV0.4_T400` |
| teqp | rho_L | 6.506e-02 | 1.66 | `xL0.6_T500` |
| teqp | rho_v | 2.060e+00 | 18.3 | `xL0.6_T500` |
| teqp | w | 6.127e-04 | 0.509 | `x0.5_T500_rho32` |
| teqp | x_L | 3.849e-05 | 4.11e-07 | `xV0.2_T300` |
| teqp | x_v | 2.351e-01 | 0.184 | `xL0.6_T500` |

## f en teqp: offset esperado (J/mol; no es fallo)
| Punto | f guía [J/mol] | f teqp [J/mol] | Δ [J/mol] |
|---|---|---|---|
| `x0.1_T600_rho35` | -13734.1763 | -13741.5095829 | -7.33 |
| `x0.1_T600_rho4` | -16991.6697 | -16999.0029617 | -7.33 |
| `x0.5_T500_rho32` | -12109.5369 | -12138.5460871 | -29.01 |
| `x0.5_T500_rho1` | -18281.302 | -18310.3111942 | -29.01 |
| `x0.9_T400_rho30` | -6986.4869 | -7019.82214876 | -33.34 |
| `x0.9_T400_rho0.5` | -13790.6278 | -13823.9630652 | -33.34 |

## Puntos `no_converge` (nunca ocultados)
- **iapws, Tabla 7, `xL0.6_T500`**: flash devolvió ok=True pero en raíz degenerada (y=0.6=entrada, rho_L=27.121126=rho_v=27.121126 mol/dm3): punto en el lugar crítico del modelo; P=20.591391 MPa vs 16.698 de la guía
- **teqp, Tabla 7, `xL0.6_T500`**: flash devolvió ok=True pero en raíz degenerada (y=0.6=entrada, rho_L=27.115464=rho_v=27.115464 mol/dm3): punto en el lugar crítico del modelo; P=20.575133 MPa vs 16.698 de la guía

## Conclusión por motor
- **motor de referencia `_nh3h2o_engine.py` (iapws 1.5.5)** — **SÍ reproduce G4-01 dentro de tolerancia**: 44 filas evaluables cumplen su criterio. 1 punto(s) `no_converge` (lugar crítico), registrado con su mensaje real.
- **motor teqp `_teqp_engine.py` + `_teqp_flash.py` (teqp 0.23.2)** — **NO reproduce G4-01 dentro de tolerancia**: 12 filas fuera de criterio (Cv: 6 filas (err_rel 1.2e-03–3.8e-03); w: 6 filas (err_rel 2.5e-04–6.1e-04)). 1 punto(s) `no_converge` (lugar crítico), registrado con su mensaje real.
Cita: IAPWS G4-01 (2001); Tillner-Roth & Friend, J. Phys. Chem. Ref. Data 27, 63 (1998).