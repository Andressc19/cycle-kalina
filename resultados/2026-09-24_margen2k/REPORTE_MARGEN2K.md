# Reporte — P_baja por busqueda de raiz, margen O2 = 2 K (30 puntos)

Fecha: 2026-09-24 · Motor: **solo TeqpAdapter** · Tarea 2026-09-24-pbaja-margen-2k (no toca src/ ni archivos existentes). Grid 5x3x2=30; T_sumidero=283.0 K, eta_t=eta_p=0.80, m_b=1.0 kg/s; eps fijos 0.85/0.80/0.85. Margen O2 = T_bur(P,x_b) - T9_amb, T9_amb = re-solucion del condensador a max(T_SUMIDERO,T_AMB_DISENO)=283.15 K (criterio O2 de operativos.py). P* = raiz de margen(P)-2.0: bracket 40 kPa, max 10 pasos en [50, 0.5*P_alta], brentq xtol=0.5 kPa; clasificacion con T_amb_diseno=283.15 K.

## Resumen ejecutivo

**P* encontrada en 22 de 30 puntos**; **KALINA: 22 de 30**. P_baja subio +154.1 kPa de media vs el barrido anterior; eta media perdio 0.98 pp.

## Conteo por clasificacion

| Clasificacion | Puntos |
|---|---|
| KALINA | 22 |
| VALIDO_ADVERTENCIA | 0 |
| CORREGIBLE | 0 |
| DEGENERADO | 0 |
| INVIABLE | 0 |
| NO_CONVERGIO | 8 |
| **Total** | **30** |
| **KALINA** | **22** |
| **P* encontrada** | **22** |

## KALINA ordenados por eta

| x_b | P_alta | T_fuente | P* | T9_amb | T_bur | margen | eta | Wnet [kW] |
|---|---|---|---|---|---|---|---|---|
| 0.65 | 5000.0 | 423.0 | 704.644595 | 302.519768 | 304.519858 | 2.000091 | 0.1215 | 71.8618 |
| 0.6 | 5000.0 | 423.0 | 535.443483 | 298.748452 | 300.748662 | 2.000211 | 0.120151 | 56.7501 |
| 0.7 | 5000.0 | 423.0 | 890.811268 | 306.189002 | 308.189002 | 2.0 | 0.118002 | 83.0583 |
| 0.6 | 4000.0 | 423.0 | 625.242061 | 303.684303 | 305.685165 | 2.000862 | 0.116752 | 72.4283 |
| 0.75 | 5000.0 | 423.0 | 1089.670783 | 309.753425 | 311.751381 | 1.997956 | 0.112369 | 91.0385 |
| 0.8 | 5000.0 | 394.0 | 952.892781 | 302.219162 | 304.219806 | 2.000644 | 0.110591 | 63.8959 |
| 0.65 | 4000.0 | 423.0 | 812.575464 | 307.297599 | 309.298076 | 2.000477 | 0.10981 | 80.0392 |
| 0.75 | 5000.0 | 394.0 | 767.935666 | 297.790861 | 299.792182 | 2.00132 | 0.108587 | 47.9677 |
| 0.7 | 4000.0 | 394.0 | 731.746249 | 299.58423 | 301.585695 | 2.001465 | 0.106949 | 52.9032 |
| 0.6 | 3000.0 | 394.0 | 523.749936 | 298.061583 | 300.061062 | 1.999479 | 0.103716 | 45.9622 |
| 0.65 | 4000.0 | 394.0 | 568.014636 | 295.611143 | 297.614862 | 2.00372 | 0.103673 | 38.583 |
| 0.75 | 4000.0 | 394.0 | 910.07401 | 303.460639 | 305.460995 | 2.000355 | 0.103582 | 63.2644 |
| 0.7 | 4000.0 | 423.0 | 1016.275812 | 310.804472 | 312.805722 | 2.00125 | 0.10153 | 84.3662 |
| 0.65 | 3000.0 | 394.0 | 687.98037 | 301.733597 | 303.73447 | 2.000873 | 0.098609 | 54.5199 |
| 0.8 | 4000.0 | 394.0 | 1101.510788 | 307.244293 | 309.244227 | 1.999934 | 0.097348 | 70.1924 |
| 0.6 | 3000.0 | 423.0 | 752.471907 | 309.841869 | 311.844003 | 2.002134 | 0.096152 | 75.9324 |
| 0.7 | 5000.0 | 394.0 | 600.662419 | 293.279218 | 295.28215 | 2.002932 | 0.091448 | 27.356 |
| 0.7 | 3000.0 | 394.0 | 868.092712 | 305.302016 | 307.302461 | 2.000445 | 0.090552 | 59.413 |
| 0.65 | 3000.0 | 423.0 | 967.9991 | 313.418241 | 315.415517 | 1.997276 | 0.084223 | 74.9734 |
| 0.75 | 3000.0 | 394.0 | 1060.024938 | 308.765931 | 310.768604 | 2.002673 | 0.081356 | 61.2955 |
| 0.6 | 4000.0 | 394.0 | 424.169832 | 291.539189 | 293.678674 | 2.139485 | 0.080412 | 19.5137 |
| 0.65 | 5000.0 | 394.0 | 451.969083 | 288.681285 | 290.685268 | 2.003983 | 0.009114 | 1.3614 |

## Criterios que bloquean a los no-KALINA

| Bloqueo | Puntos |
|---|---|
| SIN_P* | 8 |
| NO_CONVERGIO | 0 |

## Comparacion 1:1 — barrido_eps_fijos_085 vs margen2k

| x_b | P_alta | T_fuente | P_baja antes | P* ahora | dP [kPa] | margen antes | margen ahora | eta antes | eta ahora | deta [pp] | clasif antes | clasif ahora |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.6 | 3000 | 394 | 511.559 | 523.75 | 12.1907 | 1.41668 | 1.99948 | 0.105004 | 0.103716 | -0.13 | KALINA | KALINA |
| 0.6 | 4000 | 394 | 426.236 | 424.17 | -2.06571 | 2.40795 | 2.13949 | 0.080235 | 0.080412 | +0.02 | KALINA | KALINA |
| 0.6 | 5000 | 394 | 360.842 | 360.842 | 0 | - | - | - | - | - | NO_CONVERGIO | NO_CONVERGIO |
| 0.6 | 3000 | 423 | 601.65 | 752.472 | 150.822 | -0.685663 | 2.00213 | 0.110359 | 0.096152 | -1.42 | CORREGIBLE | KALINA |
| 0.6 | 4000 | 423 | 552.737 | 625.242 | 72.5055 | -0.225627 | 2.00086 | 0.123887 | 0.116752 | -0.71 | CORREGIBLE | KALINA |
| 0.6 | 5000 | 423 | 516.513 | 535.443 | 18.9301 | 1.03799 | 2.00021 | 0.121969 | 0.120151 | -0.18 | KALINA | KALINA |
| 0.65 | 3000 | 394 | 617.141 | 687.98 | 70.8392 | -0.132747 | 2.00087 | 0.105294 | 0.098609 | -0.67 | CORREGIBLE | KALINA |
| 0.65 | 4000 | 394 | 565.081 | 568.015 | 2.93363 | 1.97211 | 2.00372 | 0.103933 | 0.103673 | -0.03 | KALINA | KALINA |
| 0.65 | 5000 | 394 | 449.959 | 451.969 | 2.00965 | 1.99998 | 2.00398 | 0.009185 | 0.009114 | -0.01 | KALINA | KALINA |
| 0.65 | 3000 | 423 | 704.201 | 967.999 | 263.798 | -0.921221 | 1.99728 | 0.105756 | 0.084223 | -2.15 | CORREGIBLE | KALINA |
| 0.65 | 4000 | 423 | 656.956 | 812.575 | 155.619 | -0.503701 | 2.00048 | 0.123154 | 0.10981 | -1.33 | CORREGIBLE | KALINA |
| 0.65 | 5000 | 423 | 622.724 | 704.645 | 81.9209 | -0.184702 | 2.00009 | 0.128589 | 0.1215 | -0.71 | CORREGIBLE | KALINA |
| 0.7 | 3000 | 394 | 708.093 | 868.093 | 160 | -0.35274 | 2.00045 | 0.104061 | 0.090552 | -1.35 | CORREGIBLE | KALINA |
| 0.7 | 4000 | 394 | 675.748 | 731.746 | 55.9986 | -0.029073 | 2.00147 | 0.111606 | 0.106949 | -0.47 | CORREGIBLE | KALINA |
| 0.7 | 5000 | 394 | 598.126 | 600.662 | 2.53649 | 1.99961 | 2.00293 | 0.091635 | 0.091448 | -0.02 | KALINA | KALINA |
| 0.7 | 3000 | 423 | 784.859 | 1184.86 | 400 | -1.02771 | 1.53918 | 0.102702 | - | - | CORREGIBLE | NO_CONVERGIO |
| 0.7 | 4000 | 423 | 743.206 | 1016.28 | 273.07 | -0.668315 | 2.00125 | 0.122436 | 0.10153 | -2.09 | CORREGIBLE | KALINA |
| 0.7 | 5000 | 423 | 713.742 | 890.811 | 177.069 | -0.403447 | 2 | 0.131771 | 0.118002 | -1.38 | CORREGIBLE | KALINA |
| 0.75 | 3000 | 394 | 780.025 | 1060.02 | 280 | -0.45728 | 2.00267 | 0.102879 | 0.081356 | -2.15 | CORREGIBLE | KALINA |
| 0.75 | 4000 | 394 | 754.22 | 910.074 | 155.854 | -0.220636 | 2.00035 | 0.11551 | 0.103582 | -1.19 | CORREGIBLE | KALINA |
| 0.75 | 5000 | 394 | 729.605 | 767.936 | 38.3303 | 0.510381 | 2.00132 | 0.111448 | 0.108587 | -0.29 | KALINA | KALINA |
| 0.75 | 3000 | 423 | 841.813 | 1241.81 | 400 | -0.998526 | -0.216863 | 0.101204 | - | - | CORREGIBLE | NO_CONVERGIO |
| 0.75 | 4000 | 423 | 607.963 | 944.028 | 336.065 | - | -0.424156 | - | - | - | NO_CONVERGIO | NO_CONVERGIO |
| 0.75 | 5000 | 423 | 785.177 | 1089.67 | 304.493 | -0.503035 | 1.99796 | 0.13399 | 0.112369 | -2.16 | CORREGIBLE | KALINA |
| 0.8 | 3000 | 394 | 834.508 | 1234.51 | 400 | -0.461013 | 1.25204 | 0.102078 | - | - | CORREGIBLE | NO_CONVERGIO |
| 0.8 | 4000 | 394 | 816.575 | 1101.51 | 284.936 | -0.297897 | 1.99993 | 0.117475 | 0.097348 | -2.01 | CORREGIBLE | KALINA |
| 0.8 | 5000 | 394 | 798.889 | 952.893 | 154.004 | -0.134735 | 2.00064 | 0.121517 | 0.110591 | -1.09 | CORREGIBLE | KALINA |
| 0.8 | 3000 | 423 | 660.399 | 632.935 | -27.4637 | - | - | - | - | - | NO_CONVERGIO | NO_CONVERGIO |
| 0.8 | 4000 | 423 | 592.935 | 592.935 | 0 | - | - | - | - | - | NO_CONVERGIO | NO_CONVERGIO |
| 0.8 | 5000 | 423 | 838.776 | 1238.78 | 400 | -0.499 | 0.351061 | 0.13599 | - | - | CORREGIBLE | NO_CONVERGIO |

## Sensibilidad d/dP (regresion lineal sobre las evaluaciones)

| x_b | P_alta | T_fuente | n_evals | dT_bur/dP | dT9_amb/dP | dmargen/dP [K/kPa] |
|---|---|---|---|---|---|---|
| 0.6 | 3000 | 394 | 7 | 0.0585448 | 0.00163491 | 0.0569099 |
| 0.6 | 4000 | 394 | 10 | 0.0720161 | 0.0168963 | 0.0551198 |
| 0.6 | 3000 | 423 | 11 | 0.0487565 | 0.0294987 | 0.0192577 |
| 0.6 | 4000 | 423 | 9 | 0.0541652 | 0.0214576 | 0.0327076 |
| 0.6 | 5000 | 423 | 8 | 0.0582261 | 0.00159695 | 0.0566291 |
| 0.65 | 3000 | 394 | 9 | 0.0493293 | 0.017443 | 0.0318863 |
| 0.65 | 4000 | 394 | 7 | 0.0536445 | 0.00115103 | 0.0524934 |
| 0.65 | 5000 | 394 | 7 | 0.0633133 | 0.000190328 | 0.063123 |
| 0.65 | 3000 | 423 | 14 | 0.0409206 | 0.0290997 | 0.0118209 |
| 0.65 | 4000 | 423 | 11 | 0.0451483 | 0.0278588 | 0.0172895 |
| 0.65 | 5000 | 423 | 11 | 0.0480713 | 0.0157089 | 0.0323624 |
| 0.7 | 3000 | 394 | 9 | 0.0422719 | 0.0269565 | 0.0153154 |
| 0.7 | 4000 | 394 | 9 | 0.045626 | 0.00762859 | 0.0379974 |
| 0.7 | 5000 | 394 | 7 | 0.0507308 | 0.000779469 | 0.0499514 |
| 0.7 | 3000 | 423 | 11 | 0.0361346 | 0.0313125 | 0.00482211 |
| 0.7 | 4000 | 423 | 14 | 0.0388405 | 0.0285608 | 0.0102797 |
| 0.7 | 5000 | 423 | 12 | 0.0414763 | 0.0258552 | 0.0156211 |
| 0.75 | 3000 | 394 | 12 | 0.037126 | 0.0283646 | 0.00876136 |
| 0.75 | 4000 | 394 | 11 | 0.0399493 | 0.0244492 | 0.0155002 |
| 0.75 | 5000 | 394 | 7 | 0.0433412 | 0.00117829 | 0.0421629 |
| 0.75 | 3000 | 423 | 11 | 0.0341183 | 0.0321466 | 0.00197171 |
| 0.75 | 4000 | 423 | 11 | 0.0440763 | 0.0416769 | 0.00239935 |
| 0.75 | 5000 | 423 | 15 | 0.0364708 | 0.0277625 | 0.00870829 |
| 0.8 | 3000 | 394 | 11 | 0.0337925 | 0.0310165 | 0.00277598 |
| 0.8 | 4000 | 394 | 15 | 0.0352001 | 0.0256863 | 0.00951385 |
| 0.8 | 5000 | 394 | 11 | 0.0379093 | 0.0226926 | 0.0152167 |
| 0.8 | 5000 | 423 | 11 | 0.0336878 | 0.0320346 | 0.00165318 |

## Hallazgos

1. **P* encontrada en 22 de 30 puntos**; KALINA = 22 de 30.
2. **P_baja extra vs barrido anterior**: promedio +154.1 kPa en 30 pares; eta perdida media 0.98 pp en 22 pares.
3. **O2 ya no bloquea por construccion** (margen 2 K => T9_amb = T_bur - 2 < T_bur). Sensibilidad: ver tabla dmargen/dP.
4. `clasificacion=NO_CONVERGIO` agrupa P* encontrada con ciclo final no convergido; `SIN_P*` separa los que nunca alcanzaron margen 2 K.
5. **Conformidad de aceptacion |margen-2|<0.1 K: 21 de 22 puntos con P***. Excepcion unica: (0.6, 4000, 394) da margen 2.1395 - la funcion margen(P) es DISCONTINUA ahi (rama alterna del solver: eta 0.034 <-> 0.080, T9_amb salta 0.41 K en 0.5 kPa); sus evaluaciones muestran margenes 1.71/2.14/2.16 sin ningun P en [1.9, 2.1], asi que 2.1395 es lo mas cercano alcanzable en la vecindad (ver evaluaciones_margen.csv).
6. Motivos de los 8 puntos SIN P*: 3 por `PropertyRangeError` de teqp (dominio roto: (0.6,5000,394) h fuera de dominio; (0.8,3000,423) y (0.8,4000,423) equilibrio no resoluble) y 5 con margen max < 2 K ((0.7,3000,423), (0.75,3000,423), (0.75,4000,423), (0.8,3000,394), (0.8,5000,423): dmargen/dP ~ 0.002-0.005 K/kPa segun tabla de sensibilidad - el margen se satura sin alcanzar 2 K en [50, 0.5*P_alta]).

## Metodologia y limites

- P_a = P_baja final del mismo punto en barrido_eps_fijos_085.csv; si fue NO_CONVERGIO o sin P_baja: calibrar_P_baja(pinch=6.0). - Cada evaluacion de margen(P) resuelve el ciclo completo con P_baja=P y re-resuelve solo el condensador (O2); todas van a evaluaciones_margen.csv. - Captura de CicloNoConvergeError/PropertyRangeError/ValueError/RuntimeError/NotImplementedError por evaluacion; si el bracket no se cierra o una evaluacion falla, el punto se registra con pbaja_encontrada=False y el motivo, sin descartarlo. Reanudable por CSV (clave x_b/P_alta/T_fuente).

## Entregables

- barrido_margen2k.csv (30 filas), evaluaciones_margen.csv (todas las evaluaciones de margen(P)), run.log y este reporte.
