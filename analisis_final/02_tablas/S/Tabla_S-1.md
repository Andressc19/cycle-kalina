# Tabla S-1 · Resumen por estudio

**Síntesis de toda la campaña:** cada fila es un estudio o una parte con sus propios datos fijos.  



| Estudio | Nombre | Familia | Partes | Punto base | Diseño | Corridas | Genuinas | KALINA | KALINA confiables | Falsos convergidos | Criterio que más bloquea |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1.1 | Repetir el caso del profesor | R | 1.1a, 1.1b, 1.1c, 1.1d | PP | una variable a la vez sobre PP | 42 | 0 | 0 | 0 | 0 | — |
| 2.1 | Un solo cambio | F | 2.1 | PP | malla 10 + bisección | 132 | 15 | 0 | 0 | 21 | O2 (15 de 15) |
| 2.2 | Dos cambios | F | 2.2a, 2.2b | PP | malla 2D + bisección | 180 | 165 | 59 | 48 | 12 | O2 (106 de 106) |
| 2.3 | Dos cambios con η y ε en 0.40–0.95 | F | 2.3a, 2.3b, 2.3c, 2.3d | PP | mallas + bisección | 225 | 154 | 20 | 1 | 4 | O2 (134 de 134) |
| 2.4 | Sumidero más frío | F | 2.4a, 2.4b, 2.4c, 2.4d | 4 bases | malla 2D + bisección | 320 | 269 | 153 | 119 | 0 | O2 (116 de 116) |
| 3.1 | Sensibilidad local alrededor de A* | L | 3.1 | A* | OAT 15 + A* ± 1 % | 171 | 148 | 86 | 86 | 6 | O2 (61 de 62) |
| 3.2 | Sensibilidad global (500 puntos) | G | 3.2 | caja | LHS | 500 | 452 | 121 | 83 | 13 | O2 (324 de 331) |
| 3.3 | P_baja alta (1500–2500 kPa) | G | 3.3 | caja | LHS | 150 | 120 | 75 | 45 | 6 | O2 (44 de 45) |
| 4.1 | Escenarios de conservación | C | 4.1a, 4.1b, 4.1c, 4.1d, 4.1e | PP parcial | LHS por escenario | 600 | 382 | 20 | 2 | 12 | O2 (362 de 362) |
| 4.2 | Mapa con las presiones del profesor | C | 4.2 | PP con PA y PB | malla 11×5×3 | 165 | 149 | 104 | 104 | 15 | O2 (30 de 45) |
| 6.1 | Verificación con el motor de referencia | V | 6.1a, 6.1b, 6.1c | puntos clave | puntos de control | 167 | 151 | 142 | 137 | 0 | O2 (9 de 9) |
| 5.1 | Búsqueda de la η máxima | O | 5.1a, 5.1b, 5.1c, 5.1d, 5.1e | 5 arranques | búsqueda por patrones | 560 | 549 | 419 | 331 | 1 | O2 (114 de 130) |
| 4.3 | Escalera de conservación | C | 20 partes (ver tabla de condiciones) | PP parcial | selección hacia adelante + LHS | 987 | 806 | 181 | 118 | 29 | O2 (613 de 625) |
| 6.2 | Planta real de Húsavík | H | 6.2a, 6.2b, 6.2c, 6.2d | ancla de Húsavík | recorrida + OFAT + malla | 382 | 347 | 282 | 268 | 16 | O2 (65 de 65) |

**Notas:** Filtro: todos los puntos (sin el anexo A.1). n = 14 filas en la tabla. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido. Fuente: todos_los_puntos.csv. Familias: R reproducibilidad, F factibilidad, L local, G global, C conservación, O optimización, V verificación, H Húsavík.
