# Sens2 etapa B - reintento de NO_CONVERGIO con mayor presupuesto

Presupuesto 900 s y tope 1100 s (el original era 300 s y 600 s). El motor es determinista: si el grupo de control cambia de clase, el reintento no es comparable.

| grupo | puntos | siguen NO_CONVERGIO | ahora KALINA | ahora CORREGIBLE | ahora INVIABLE | error del motor |
|---|---|---|---|---|---|---|
| lento | 75 | 73 | 0 | 0 | 0 | 2 |
| control | 15 | 15 | 0 | 0 | 0 | 0 |

## Causas de los que siguen sin converger

| causa (primeros 60 caracteres) | n |
|---|---|
| sin dos extremos evaluables en el rango físico de T1 (replie | 38 |
| N2: el balance global de energía no cierra dentro de la tole | 30 |
| lazo interior (frio) no convergio tras max_iter_frio | 12 |
| extremos [342.0000, 358.0000] K sin cambio de signo de F (F( | 1 |
| extremos [360.5000, 362.0000] K sin cambio de signo de F (F( | 1 |
| extremos [301.5000, 347.5000] K sin cambio de signo de F (F( | 1 |
| extremos [291.5000, 360.0000] K sin cambio de signo de F (F( | 1 |
| extremos [304.1500, 382.1500] K sin cambio de signo de F (F( | 1 |
| extremos [283.5000, 382.1500] K sin cambio de signo de F (F( | 1 |
| punto interior no evaluable durante brentq (T=310.977387 K) | 1 |
| punto interior no evaluable durante brentq (T=304.276038 K) | 1 |
