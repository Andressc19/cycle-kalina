# Reporte — Rama de la turbina y estabilidad de puntos KALINA

Fecha: 2026-09-24 · Motor: TeqpAdapter (cálculo) + AmmoniaWaterAdapter (referencia real, IAPWS G4-01) · Tarea 2026-09-24-rama-turbina-y-estabilidad.
No se modificó ningún archivo de `src/` ni existente. Resultados en `resultados/2026-09-24_rama_turbina/`: `expansion_P.csv`, `s_de_T.csv`, `motor_real.csv`, `solucion_dos_puntos.csv`, `estabilidad_kalina.csv`, `run_1.log`, `run_2.log`.
Constantes: T_sumidero=283.0 K, eta_t=eta_p=0.80, m_b=1.0 kg/s, eps fijos 0.85/0.80/0.85, T_amb_diseno=283.15 K (idénticas a `calibracion_elsayed_malla.py` y a la tarea margen2k).

---

## 1. Rama física de la expansión isentrópica de la turbina

### 1.1 Fenómeno reproducido

En (x_b=0.60, P_alta=4000, T_fuente=394) la expansión `h4s = backend.h(P_baja, s=s3, x=x3)`
(`src/components/turbina.py:35`) salta entre dos ramas al mover P_baja 0.25 kPa
(`solucion_dos_puntos.csv`):

| P_baja [kPa] | s3 [kJ/kg·K] | x3 | h4s [kJ/kg] | T4s [K] | fase | q4s | h4 [kJ/kg] | T4 [K] | η |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 423.914831 | 5.704153 | 0.974965 | **1625.686** | **272.816** | liquido | 0.000 | 1659.492 | 313.942 | 0.033594 |
| 424.169832 | 5.704109 | 0.974970 | **1486.031** | **282.180** | bifasico | 0.903 | 1547.764 | 290.415 | 0.080412 |

### 1.2 Barrido de la expansión aislada (`expansion_P.csv`, P de 419.0 a 429.0 cada 0.25 kPa)

| P [kPa] | h4s [kJ/kg] | T4s [K] | fase | salto Δh4s [kJ/kg] |
|---|---:|---:|---|---:|
| 419.00 | 1484.594 | 281.757 | bifasico | — |
| 419.25 | 1625.395 | 272.521 | liquido | **+140.80** |
| 424.00 | 1625.687 | 272.821 | liquido | 0.015 |
| 424.17 (P_ref) | 1486.031 | 282.180 | bifasico | −139.63 |
| 424.25 | 1486.053 | 282.186 | bifasico | — |
| 429.00 | 1487.359 | 282.572 | bifasico | 0.069 |

Hay **dos discontinuidades**: P≈419.1 (rama B → A, +140.8 kJ/kg) y P≈424.1 (rama A → B, −139.6 kJ/kg).
**Rama A** (T≈272.5–272.8 K, h≈1625–1626 kJ/kg, clasificada "liquido") es la que devuelve teqp en
P ∈ (≈419.1, ≈424.1]; **rama B** (T≈281.8–282.6 K, h≈1484–1487 kJ/kg, bifásica, q≈0.903) fuera de ese
intervalo. El par `evaluaciones_margen.csv` (423.914831 ↔ 424.169832) está a caballo del borde superior.

### 1.3 Causa raíz: s(T) no monótona por un estado espurio del flash

`src/properties/_teqp_flash.py` (clasificación de fase en `estado`/`_fase_monofasica`) devuelve un estado
espurio tipo-vapor justo en el punto de burbuja de la mezcla a 424 kPa y x=x3 (`s_de_T.csv`, paso 0.5 K):

| T [K] | s [kJ/kg·K] | h [kJ/kg] | fase reportada | ¿crece? |
|---|---:|---:|---:|---|
| 272.5 | 1.437 | 313.86 | liquido | sí |
| 273.0 | **6.153** | **1626.18** | liquido | sí (acantilado) |
| 273.5 | **1.535** | 340.67 | bifasico | **NO** |
| 274.0 | 3.450 | 864.73 | bifasico | sí |
| 282.2 | ≈5.704 | ≈1486 | bifasico | sí (cruce de s3) |

`s(T,x3)` NO es estrictamente creciente (única violación en T∈(273.0, 273.5)): el estado a T=273.0 tiene
valores de vapor (s=6.153, h=1626.18) pero la fase reportada es "liquido" — inconsistencia interna del
estado espurio. Ese acantilado produce **3 raíces** de s(T,x3)=s3 (dos sobre el espolón + la física en
T≈282.2), de modo que `TeqpAdapter._T_de` (inversión con brentq sobre [230, 650], `src/properties/teqp_adapter.py`)
cae en una raíz u otra según la presión. La rama A es, por tanto, un **artefacto de inversión** sobre el
espolón espurio, no un estado termodinámico real.

### 1.4 Veredicto contra el motor real (`motor_real.csv`)

Referencia independiente: `AmmoniaWaterAdapter` (motor real IAPWS G4-01 portado), 3 llamadas
(P ∈ {420.0, 422.0, 424.169832}, mismas s3, x3 de teqp):

| P [kPa] | Rama A (teqp) | Rama B (teqp) | Motor real | ¿A coincide? | ¿B coincide? |
|---|---:|---:|---:|---:|---|
| 420.0 | h=1626.27, T=272.87 | h=1484.87, T=281.84 | h=1485.617, T=282.143 | no | **sí** |
| 422.0 | h=1626.40, T=273.00 | h=1485.43, T=282.00 | h=1486.175, T=282.309 | no | **sí** |
| 424.169832 | h=1626.53, T=273.13 | h=1486.03, T=282.18 | h=1486.779, T=282.487 | no | **sí** |

**VEREDICTO: la rama B (bifásica, T4s≈282 K, h4s≈1486 kJ/kg) es la física.** Coincide con el motor real
en las 3 presiones dentro de ±0.75 kJ/kg en h y ±0.31 K en T (umbrales: ±2 kJ/kg, ±0.5 K). La rama A
dista ~140.7 kJ/kg y ~9.3 K del motor real. La desviación sistemática leve de la rama B (teqp ~0.7 kJ/kg y
~0.3 K por debajo del real) es consistente con el offset teqp↔iapws ya documentado en el proyecto
(~1.3 kJ/kg en h, ~0.006 kJ/kg·K en s). Coste: la rama B tarda ~4.6 s por llamada `h` y ~2.6 s por `T_from_Ps`.

**Consecuencia**: la "ganancia de η" por subir P_baja 0.25 kPa (0.0336 → 0.0804) no es física: es la
conmutación de la inversión a la rama espuria. En P=423.914831 el ciclo entero se resuelve sobre el
artefacto (h4s de vapor-espurio → h4=1659.5, T4=313.9, η baja).

---

## 2. Estabilidad de los 22 puntos KALINA (P* ± 0.5 kPa)

Definición (TASK_CONTEXT): un punto es **estable** si |max−min(η)| ≤ 0.01, |max−min(h4)| ≤ 10 kJ/kg y la
clasificación no cambia entre P*−0.5, P* y P*+0.5 kPa. Excepciones por evaluación capturadas y reportadas
(`estabilidad_kalina.csv`, 22 filas formato ancho; `run_2.log`).

### 2.1 Resumen

- **21 de 22 puntos estables.** En los estables: dEta ≤ 1.05×10⁻⁴ (umbral 0.01, margen >95×), dH4 ≤ 0.20 kJ/kg
  (umbral 10, margen >50×), clasificación KALINA constante en las 3 evaluaciones, margen O2 ≈ 2.00 ± 0.03 K
  (consistente con que P* es la raíz de margen=2 K de la tarea margen2k).
- **1 punto inestable**: (x_b=0.60, P_alta=4000, T_fuente=394), P*=424.169832 — el punto del par del salto.
- Ninguna evaluación falló (err_* vacíos en las 66); el criterio de clasificación no absorbe la inestabilidad:
  el punto inestable clasifica KALINA en las 3 evaluaciones (la clase informa del régimen, no de la rama).

### 2.2 El punto inestable (Sección 1 aplicada)

| P [kPa] | η | h4 [kJ/kg] | T4 [K] | margen O2 [K] | clasif |
|---|---:|---:|---:|---:|---|
| 423.669832 (P*−0.5) | 0.033597 | **1659.480** | 313.930 | 1.695 | KALINA |
| 424.169832 (P*) | 0.080412 | **1547.764** | 290.415 | 2.139 | KALINA |
| 424.669832 (P*+0.5) | 0.080369 | 1547.875 | 290.459 | 2.174 | KALINA |

dEta = 0.0468 (4.7× el umbral), dH4 = 111.7 kJ/kg (11× el umbral). La evaluación en P*−0.5 cae en la
**rama espuria A** (Sección 1): P*=424.169832 queda a menos de 0.04 kPa del borde superior de la franja de
conmutación (~424.1). Es el único de los 22 puntos cuyo P* está dentro de una franja espuria; en el resto,
±0.5 kPa están lejos de cualquier discontinuidad.

### 2.3 Tabla completa (22 puntos)

| x_b | P_alta [kPa] | T_fuente [K] | P* [kPa] | η (P*) | dEta | dH4 [kJ/kg] | Estable |
|---|---:|---:|---:|---:|---:|---:|---|
| 0.60 | 3000 | 394 | 523.749936 | 0.103716 | 1.05e-04 | 0.200 | sí |
| 0.60 | 4000 | 394 | **424.169832** | 0.080412 | **4.68e-02** | **111.716** | **no** |
| 0.60 | 3000 | 423 | 752.471907 | 0.096152 | 8.7e-05 | 0.163 | sí |
| 0.60 | 4000 | 423 | 625.242061 | 0.116752 | 9.4e-05 | 0.180 | sí |
| 0.60 | 5000 | 423 | 535.443483 | 0.120151 | 9.4e-05 | 0.194 | sí |
| 0.65 | 3000 | 394 | 687.980370 | 0.098609 | 9.0e-05 | 0.157 | sí |
| 0.65 | 4000 | 394 | 568.014636 | 0.103673 | 8.8e-05 | 0.171 | sí |
| 0.65 | 5000 | 394 | 451.969083 | 0.009114 | 3.5e-05 | 0.197 | sí |
| 0.65 | 3000 | 423 | 967.999100 | 0.084223 | 7.3e-05 | 0.130 | sí |
| 0.65 | 4000 | 423 | 812.575464 | 0.109810 | 8.0e-05 | 0.142 | sí |
| 0.65 | 5000 | 423 | 704.644595 | 0.121500 | 8.2e-05 | 0.152 | sí |
| 0.70 | 3000 | 394 | 868.092712 | 0.090552 | 7.9e-05 | 0.128 | sí |
| 0.70 | 4000 | 394 | 731.746249 | 0.106949 | 8.0e-05 | 0.136 | sí |
| 0.70 | 5000 | 394 | 600.662419 | 0.091448 | 7.4e-05 | 0.153 | sí |
| 0.70 | 4000 | 423 | 1016.275812 | 0.101530 | 6.9e-05 | 0.116 | sí |
| 0.70 | 5000 | 423 | 890.811268 | 0.118002 | 7.2e-05 | 0.123 | sí |
| 0.75 | 3000 | 394 | 1060.024938 | 0.081356 | 7.0e-05 | 0.107 | sí |
| 0.75 | 4000 | 394 | 910.074010 | 0.103582 | 7.2e-05 | 0.112 | sí |
| 0.75 | 5000 | 394 | 767.935666 | 0.108587 | 7.3e-05 | 0.122 | sí |
| 0.75 | 5000 | 423 | 1089.670783 | 0.112369 | 6.4e-05 | 0.102 | sí |
| 0.80 | 4000 | 394 | 1101.510788 | 0.097348 | 6.4e-05 | 0.094 | sí |
| 0.80 | 5000 | 394 | 952.892781 | 0.110591 | 6.7e-05 | 0.100 | sí |

---

## 3. Recomendaciones (no aplicadas — fuera de alcance; requieren decisión)

1. **Fijar la rama física en la inversión** (`src/properties/teqp_adapter.py`, modo P-s, x): restringir el
   bracket de `_T_de` a [T_debajo_del_punto_de_burbuja(P,x), 320] o sembrar con el T4s del motor real
   (`ammonia_water_adapter.py`), de modo que `src/components/turbina.py:35` nunca caiga en la rama espuria.
2. **Corregir el estado espurio del flash** (`src/properties/_teqp_flash.py`): a T=273.0 K, P=424 kPa la
   clasificación de fase ("liquido") no corresponde a los valores devueltos (s=6.153, h=1626.18). Añadir una
   sanidad de fase consistente o de monotonía de s(T) en `estado()`.
3. **Clasificación insensible a la rama**: el criterio KALINA no detecta la conmutación (los 3 puntos
   clasifican KALINA). Si se toca `src/restricciones/`, considerar una falla de coherencia de rama.
4. **Operacional**: cualquier P* de diseño dentro de ~0.1 kPa del borde de una franja espuria es inutilizable;
   re-evaluar el punto (0.60, 4000, 394) con P* desplazada fuera de la franja (por arriba) o con el fix de la
   recomendación 1.

## 4. Entregables

- `scripts/diagnostico_rama_turbina.py` (232 líneas) y `scripts/estabilidad_kalina_margen2k.py` (151 líneas) — scripts nuevos, no modifican nada existente.
- `resultados/2026-09-24_rama_turbina/`: `solucion_dos_puntos.csv`, `expansion_P.csv`, `s_de_T.csv`, `motor_real.csv`, `estabilidad_kalina.csv`, `run_1.log`, `run_2.log`.
- Aceptación: veredicto de rama apoyado en el motor real (3 llamadas); las 22 filas KALINA evaluadas en P*±0.5 kPa; criterios de estabilidad aplicados y reportados.