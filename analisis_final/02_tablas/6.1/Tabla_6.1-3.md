# Tabla 6.1-3 · Paridad teqp contra el motor real

**Estudio 6.1** · Verificación con el motor de referencia · **Partes:** 6.1a  
**Punto base:** puntos clave del ciclo con teqp y con el motor real  
**Puntos de control: cada punto conserva los datos de su caso de origen (ver la columna de origen); no hay datos fijos ni barridos comunes.**  

| Identificador | Origen | Clase con teqp | Clase con el motor real | Coincide la clase | η con teqp [%] | η con el motor real [%] | Δη [pp] | Dentro de la banda | Margen O1 con teqp [–] | Margen O1 con el motor real [–] | Margen O2 con teqp [K] | Margen O2 con el motor real [K] | Fuera de rango | B verificado |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P01 | Ancla A* | KALINA | NO_CONVERGIO | no | 8.48 |  |  |  | 0.035 |  | 0.3 |  | no | sí |
| P02 | estudios 2.1 y 2.2, mayor η | KALINA | NO_CONVERGIO | no | 9.15 |  |  |  | 0.035 |  | 0.0 |  | no | sí |
| P03 | estudio 4.2, presiones del profesor, techo | KALINA | KALINA | sí | 10.81 | 10.81 | 9.14566e-05 | sí | 0.022 | 0.022 | 0.4 | 0.4 | no | sí |
| P04 | estudio 4.2, presiones del profesor, ε_cond mínima | KALINA | NO_CONVERGIO | no | 2.54 |  |  |  | 0.036 |  | 0.1 |  | no | sí |
| P05 | estudio 5.1, óptimo A1 | KALINA | NO_CONVERGIO | no | 14.98 |  |  |  | 0.018 |  | 0.4 |  | no | sí |
| P06 | estudio 5.1, óptimo A2 | KALINA | NO_CONVERGIO | no | 15.48 |  |  |  | 0.005 |  | 3.8 |  | no | sí |
| P07 | estudio 5.1, óptimo A3 | KALINA | NO_CONVERGIO | no | 12.74 |  |  |  | 0.031 |  | 3.8 |  | no | sí |
| P08 | estudio 5.1, óptimo A4 | KALINA | KALINA | sí | 15.60 | 15.60 | 0.000278372 | sí | 0.006 | 0.006 | 0.1 | 0.1 | no | sí |
| P09 | estudio 5.1, óptimo A5 | KALINA | NO_CONVERGIO | no | 11.09 |  |  |  | 0.001 |  | 5.7 |  | sí | sí |
| P10 | estudio 3.2, top 1 | KALINA | NO_CONVERGIO | no | 12.30 |  |  |  | 0.027 |  | 5.5 |  | no | sí |
| P11 | estudio 3.3, mayor P_baja KALINA | KALINA | NO_CONVERGIO | no | 2.67 |  |  |  | 0.077 |  | 49.4 |  | sí | no |
| P12 | estudio 2.3, fuente del profesor | KALINA | NO_CONVERGIO | no | 6.27 |  |  |  | 0.052 |  | 0.2 |  | sí | sí |

**Notas:** Filtro: puntos emparejados teqp y motor real. n = 12 filas en la tabla. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido. Fuente: resultados/2026-10-08_final_M6/m6_comparacion.csv.
