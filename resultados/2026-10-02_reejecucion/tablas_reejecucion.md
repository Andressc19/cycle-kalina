## Resultado por barrido de origen

```
                           puntos  recuperados  KALINA  CORREGIBLE  INVIABLE  NO_CONV_tras_clasificar  siguen_sin_converger  %_recuperado
origen                                                                                                                                   
b0_scan_cementera             352          278       0         264         0                       14                    74          79.0
busqueda_libre_v2             302          247       6         238         3                        0                    55          81.8
barrido_xb_industria           43            6       0           1         4                        1                    37          14.0
barrido_literatura_kcs11       28           23       0          21         0                        2                     5          82.1
eta_vs_Tambiente_profesor      23            0       0           0         0                        0                    23           0.0
eta_vs_Palta_profesor           9            0       0           0         0                        0                     9           0.0
barrido_margen2k                8            8       3           4         0                        1                     0         100.0
barrido_pinch6_realista         7            6       0           5         0                        1                     1          85.7
eta_vs_xb_profesor              6            0       0           0         0                        0                     6           0.0
exploracion_tfuente_bajo        5            2       0           2         0                        0                     3          40.0
busqueda_husavik                4            4       0           4         0                        0                     0         100.0
frontera_tfuente_teqp           3            3       0           2         0                        1                     0         100.0
barrido_eps_fijos_085           2            1       0           1         0                        0                     1          50.0
busqueda_libre                  1            1       0           1         0                        0                     0         100.0
busqueda_husavik_v2             1            0       0           0         0                        0                     1           0.0
sensibilidad_P_baja             1            0       0           0         0                        0                     1           0.0
sensibilidad_eps_hrvg           1            1       0           1         0                        0                     0         100.0
TOTAL                         796          580       9         544         7                       20                   216          72.9
```

## Causa de los que siguen sin converger

```
                             filas
causa                             
sin cambio de signo             78
punto interior no evaluable     67
sin extremos evaluables         61
otro                             6
presupuesto agotado              4
```

## Cruce con la comprobación O5

```
conv                       converge ahora  sigue sin converger  total
veredicto                                                            
DENTRO_DE_CAMPANA_POSIBLE             278                   33    311
LIQUIDA_DEMOSTRADA                      0                    4      4
SOBRECALENTADA_DEMOSTRADA               1                   36     37
total                                 279                   73    352
```

## Tiempos por fila

```
                                      n  media_s  mediana_s  p90_s   max_s
todas                             796.0    123.0      113.9  187.6  1533.8
recuperadas                       580.0    130.6      118.2  195.9   292.5
sin converger                     216.0    102.8       81.6  146.4  1533.8
cortadas por presupuesto (300 s)    4.0      NaN        NaN    NaN     NaN
```

## Verificación con el motor real

```
                                                                   clave                                                                                 csv_origenes      motivo  eta_teqp     clas_teqp  eta_real     clas_real  d_eta_rel  misma_clas  verificada     t_s  msg
0                3000|1234.51|394|283|0.8|1|0.8|0.8|0.85|0.8|0.85|283.15                                                     2026-09-24_margen2k/barrido_margen2k.csv      KALINA  0.073416        KALINA  0.073408        KALINA   0.000107        True        True   539.7  NaN
1                5000|1238.78|423|283|0.8|1|0.8|0.8|0.85|0.8|0.85|283.15                                                     2026-09-24_margen2k/barrido_margen2k.csv      KALINA  0.109215        KALINA  0.109207        KALINA   0.000072        True        True   561.1  NaN
2                3000|1184.86|423|283|0.7|1|0.8|0.8|0.85|0.8|0.85|283.15                                                     2026-09-24_margen2k/barrido_margen2k.csv      KALINA  0.073381        KALINA  0.073381        KALINA   0.000007        True        True   594.7  NaN
3               3000|273.545|373|283|0.55|1|0.8|0.8|0.85|0.75|0.8|303.55                                     2026-09-22_literatura_kcs11/barrido_literatura_kcs11.csv    falla N2 -0.449588  NO_CONVERGIO -0.449634  NO_CONVERGIO   0.000103        True        True   809.4  NaN
4                5000|360.842|394|283|0.6|1|0.8|0.8|0.85|0.8|0.85|283.15  2026-09-24_margen2k/barrido_margen2k.csv;2026-09-23_eps_fijos_085/barrido_eps_fijos_085.csv  eta minima -0.815171  NO_CONVERGIO -0.815194  NO_CONVERGIO   0.000028        True        True   878.1  NaN
5  3000|398.119|463|283|0.65|1|0.8|0.8|0.993292|0.957123|0.988621|303.55                                     2026-09-22_literatura_kcs11/barrido_literatura_kcs11.csv    falla N2  0.130276  NO_CONVERGIO  0.130288  NO_CONVERGIO   0.000096        True        True   396.1  NaN
6               1500|273.545|340|283|0.55|1|0.8|0.8|0.85|0.75|0.8|283.15                                        2026-09-22_frontera_tfuente/frontera_tfuente_teqp.csv    falla N2 -0.477527  NO_CONVERGIO -0.478560  NO_CONVERGIO   0.002162        True        True   711.7  NaN
7        6000|380.465|583.15|300.033|0.5|1|0.85|0.75|0.9|0.75|0.8|303.55                                                    barridos_2026-09-19/b0_scan_cementera.csv  eta maxima  0.253860  NO_CONVERGIO  0.256615  NO_CONVERGIO   0.010854        True       False  1320.0  NaN
8                5000|360.842|394|283|0.6|1|0.8|0.8|0.85|0.75|0.8|283.15                                       2026-09-23_pinch6_realista/barrido_pinch6_realista.csv    falla N2 -0.633889  NO_CONVERGIO -0.633942  NO_CONVERGIO   0.000084        True        True   815.2  NaN
9             6000|400|470|300.033|0.85|1|0.85|0.75|0.85|0.75|0.8|303.55                                             2026-09-21_xb_industria/barrido_xb_industria.csv    falla N2 -0.194926  NO_CONVERGIO -0.194808  NO_CONVERGIO   0.000606        True        True   687.9  NaN
```
