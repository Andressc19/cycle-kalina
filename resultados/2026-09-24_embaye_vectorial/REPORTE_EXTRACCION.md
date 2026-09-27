# Reporte de extraccion vectorial - Embaye et al. (KCS11)

Metodo: curvas como bandas de relleno (trazo) en get_drawings(); linea central por emparejamiento simetrico de cada contorno cerrado (en discontinuas: centroide de cada trazo). Calibracion pdf->dato con las marcas EXTREMAS de las etiquetas de ticks de cada eje, error max contra las etiquetas intermedias (reportado). Series por leyenda: Figs 2-3 azul/rojo/verde = 333/373/423 K; Figs 4-5 rojo/verde/negro = 373/423/463 K (463 K es banda negra; cajas de leyenda/anotaciones <=20 items se excluyen, bandas de datos >=40). Fig 7: rombos grises (n=3) de la cola de KCS11 0.55 son duplicados sombra de los negros y se excluyen; los marcadores solo corroboran (conteo y separacion).

## Fig2 (P_evap=10 bar, eje y 0-16)
  x: 5 etiquetas, max err 0.0003126
  y: 9 etiquetas, max err 0.01033
  - T=333 K: n=30, x [0.563, 0.991], eta [3.180, 6.855] % (max en x=0.602)
  - T=373 K: n=42, x [0.352, 0.991], eta [3.407, 12.429] % (max en x=0.390)
  - T=423 K: n=45, x [0.319, 0.982], eta [3.449, 15.340] % (max en x=0.319)
## Fig3 (P_evap=15 bar, eje y 0-18)
  x: 5 etiquetas, max err 0.000235
  y: 10 etiquetas, max err 0.02063
  - T=333 K: n=23, x [0.687, 0.992], eta [3.358, 7.376] % (max en x=0.760)
  - T=373 K: n=38, x [0.439, 0.991], eta [6.830, 12.125] % (max en x=0.478)
  - T=423 K: n=37, x [0.372, 0.991], eta [7.027, 16.039] % (max en x=0.372)
## Fig4 (P_evap=23.5 bar, eje y 0-18)
  x: 5 etiquetas, max err 0.0002343
  y: 10 etiquetas, max err 0.02064
  - T=373 K: n=32, x [0.545, 0.991], eta [7.933, 11.962] % (max en x=0.628)
  - T=423 K: n=35, x [0.425, 0.991], eta [10.453, 16.933] % (max en x=0.425)
  - T=463 K: n=31, x [0.495, 0.991], eta [10.476, 14.424] % (max en x=0.495)
## Fig5 (P_evap=32 bar, eje y 0-18)
  x: 5 etiquetas, max err 0.0002352
  y: 10 etiquetas, max err 0.01033
  - T=373 K: n=25, x [0.652, 0.991], eta [8.467, 12.241] % (max en x=0.768)
  - T=423 K: n=34, x [0.459, 0.991], eta [12.671, 17.084] % (max en x=0.459)
  - T=463 K: n=28, x [0.566, 0.991], eta [12.590, 15.029] % (max en x=0.566)
## Fig7 (eta vs P_evap 0-35 bar, eje y 0-20, T_fuente 373 K)
  x: 8 etiquetas, max err 0.007406
  y: 5 etiquetas, max err 0.009775
  - KCS11(Con.=0.66): n=15, P [10.185, 31.477], eta [6.882, 12.018] % (max en 27.028 bar)
  - KCS11(Con.=0.55): n=19, P [10.198, 24.094], eta [5.479, 12.007] % (max en 19.096 bar)
  - ORC(R134a): n=17, P [9.944, 30.041], eta [6.322, 13.526] % (max en 30.041 bar)
  - ORC(Ammonia): n=17, P [9.944, 30.062], eta [3.419, 11.630] % (max en 30.062 bar)
    marcadores: 41, max sep 5.643 pt
    marcadores: 37, max sep 2.899 pt
    marcadores: 28, max sep 4.365 pt
    marcadores: 18, max sep 1.97 pt
## Controles (informativos)
  - KCS11 Con.=0.55 a 15 bar: extraido 11.432 %, texto del paper 11.38 % (dif 0.052 pp)
  - ORC(Ammonia) a 15 bar: extraido 6.755 % (texto ~7 %)
  - ORC(R134a) a 15 bar: extraido 9.263 % (texto ~9.2 %)

Cita: Embaye, M., AL-Dadah, R., Mahmoud, S., Elsayed, A., & Rezk, A., "Performance of Kalina Cycle System 11 (KCS11) using low temperature heat sources", University of Birmingham (version de congreso; modelo de Elsayed et al. 2013, IJLCT 8(suppl_1) i69-i78).
