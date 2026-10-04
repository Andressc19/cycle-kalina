# Rango confiable de los motores NH3-H2O — modo A (extrapolar y marcar)

Rama `feature/rango_motores`, 2026-10-03.

## Decisión
- Los dos motores (`real` = `AmmoniaWaterAdapter`, `teqp` = `TeqpAdapter`/`TeqpVerificado`)
  implementan el mismo modelo, **Tillner-Roth & Friend (1998) = IAPWS G4-01**. Los límites son
  los que declara la guía en §6 (`reference/IAPWS_G4-01_nh3h2o.pdf`) y valen para ambos.
  teqp no declara límites propios.
- Los fallos del envoltorio numérico de cada motor (bracket 230–650 K de teqp, piso 233 K del
  flash real, constante 2500 de Psat) **no** entran aquí: se tratan aparte (p. ej. A+B).
- **Modo A:** el punto se calcula igual, se avisa (`RangoMotorWarning` + `logging`) y se marca.
  El modo "bloquear" está reservado (`NotImplementedError`).
- La marca va **aparte de la clasificación**. Un punto puede ser `KALINA` y `fuera_rango` a la
  vez: es el caso más peligroso, porque parece válido y su número sale de una extrapolación.

## Límites vigilados (`src/rangos_motor.py`)
| Parámetro | Límite | Tipo | Fuente |
|---|---|---|---|
| P | ≤ 40 MPa | modelo | G4-01 §6 |
| T | ≥ T_tr(x), línea sólido-líquido-vapor | modelo | G4-01 ec. (9), Tabla 5 |
| T en líquido (o bifásico) | ≤ 420 K | respaldo experimental | G4-01 §6 |
| P en vapor (o bifásico) | ≤ 10 MPa | respaldo experimental | G4-01 §6 |

**Techo del modelo — decisión (usuario, 2026-10-03):** el techo real del modelo es el lugar
crítico de la mezcla, y **no lo conocemos**: la guía avisa que calcularlo da problemas de
convergencia y que su ubicación es incierta por datos escasos e inconsistentes. Por eso no se
aproxima ni se inventa un sustituto. **Los límites de trabajo del proyecto son los que declara
IAPWS G4-01 §6** (la tabla de arriba), y nada más. Cualquier límite adicional (lugar crítico o
fallos propios de cada motor) se añadirá solo si sale de una fuente documentada o de lo que
encontremos al iterar, en una tarea aparte.

La fase de cada estado sale de `estado.fase`; si es `None`, de `backend.fase_de`. Si la fase no
se puede determinar, se registra una violación `parametro="fase"` en lugar de adivinarla.

## Cómo se usa
```python
filas = ejecutar_barrido(backend, variables, motor_rango="teqp")   # o "real"
violaciones = evaluar_rango("teqp", resultado_ciclo, backend=backend)  # un solo ciclo
generar_excel(res, exe, parametros, "teqp", violaciones_rango=violaciones)
```
Con `motor_rango=None` (por defecto) la tabla y el Excel salen exactamente como antes.

Columnas nuevas: `fuera_rango` (V/F), `detalle_rango` (ej. `T2=431 K > 420 K
(respaldo_experimental) [motor: teqp]`) y `columnas_rango` (celdas a marcar).

## Cómo leer el Excel
- Celda **gris `BFBFBF`** con un comentario que dice el parámetro, el valor, el límite y el motor.
- En barridos la tabla no tiene columnas por estado. Si sale de rango un estado interno, se
  marcan `eta` y `Wnet`; si sale de rango una entrada (`P_alta`, ...), se marca esa celda.
- En `export_excel` (un ciclo) se marca la celda T o P del estado en la hoja `Estados`.
- Ejemplo: `resultados/2026-10-03_ejemplo_fuera_rango/ejemplo_fuera_rango.xlsx`
  (`scripts/ejemplo_excel_fuera_rango.py`).

## Pendiente
Modo bloquear, conexión con la UI y los límites del envoltorio de cada motor (tarea aparte).
