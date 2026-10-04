---
project: ciclo_kalina_tercero
task_id: 2026-10-01-rangos-motor-modo-A
delegated_to: executor
model: opencode/big-pickle
created: 2026-10-01
---

# TASK_CONTEXT — Marca de "fuera de rango confiable" (modo A: extrapolar y marcar)

Rama: `feature/rango_motores` (worktree `.claude/worktrees/rango-motores`, creada desde master 07b9a4c con el bracket MA; no hacer merge ni tocar master).

## Objetivo
Cuando un punto usa parámetros fuera del rango confiable de un motor (`real` = `AmmoniaWaterAdapter`,
`teqp` = `TeqpAdapter`/`TeqpVerificado`), **calcular igual** y dejar una marca explícita y trazable,
**separada de la clasificación** (KALINA/CORREGIBLE/INVIABLE/NO_CONVERGIO). Ejes independientes:
la clase dice qué pasó con el ciclo; `fuera_rango` dice qué tan confiable es el número. Un punto
puede ser `KALINA` + `fuera_rango=True` (el caso más peligroso: parece válido y no lo es).

## Restricciones (obligatorias)
- NO modificar nada en `src/properties/`. El chequeo envuelve por fuera, no toca los motores.
- NO tocar la UI (`app.py`, `ui_*.py`). Solo código, scripts y tests.
- Cada `.py` ≤ 200 líneas. Python 3.13. Sin borrado recursivo.
- Valores dentro de rango: comportamiento idéntico al actual (los tests existentes deben seguir
  verdes sin modificarse; si alguno exige cambiarse, repórtalo en UNRESOLVED).
- No inventar límites: usar SOLO los de la sección "Límites" (vienen de `CONTEXT.md`, IAPWS G4-01).
- Solo modo A. Parámetro `modo` con único valor aceptado `"extrapolar_marcar"`; cualquier otro valor
  (incl. `"bloquear"`) lanza `NotImplementedError("modo reservado, no implementado")`. Dejar la
  estructura lista para añadir el bloqueo luego sin rehacer nada.

## Procedencia de los límites (verificada por Claude el 2026-10-01 — repetir en el paso 0)
- Ambos motores implementan el MISMO modelo: Tillner-Roth & Friend, J. Phys. Chem. Ref. Data 27, 63
  (1998) = IAPWS G4-01. `real` = `iapws.ammonia.H2ONH3` 1.5.5 + 2 correcciones (`_nh3h2o_engine.py`);
  `teqp` = `teqp.AmmoniaWaterTillnerRoth` 0.23.2 (NIST) + CoolProp para el gas ideal de los puros.
  teqp NO declara límites de validez propios: los del paper aplican a los dos.
- Fuente primaria local: `reference/IAPWS_G4-01_nh3h2o.pdf`, §6 "Range of Validity" (PyMuPDF/`fitz`
  está instalado). Confirmado contra ese PDF: coeficientes c11..c42 de la Tabla 5, los 4 tramos de la
  ec. (9), "líquido < 420 K y 40 MPa", "vapor < 10 MPa", "válido hasta 40 MPa a temperaturas
  subcríticas", supercrítico = "precisión desconocida".
- LÍMITE NO VIGILADO (declararlo en `docs/rangos_motor.md`): el techo real del modelo es el lugar
  crítico de la mezcla; la propia guía avisa que calcularlo da problemas de convergencia y que su
  ubicación es incierta. NO implementar un sustituto aproximado; solo documentarlo.

## Límites (centralizar en UN solo lugar: `src/rangos_motor.py`, como datos, no dispersos)
Cada límite lleva: `parametro`, `motor(s)`, `tipo` (`modelo` | `respaldo_experimental` | `envoltorio`),
`valor`, `fuente`. Estados del ciclo: T [K], P [kPa], x másica de NH3 (convertir a molar con la
función `w2m` de los motores cuando la fórmula lo pida).

| Parámetro | Límite | Tipo | Motores | Fuente |
|---|---|---|---|---|
| P | ≤ 40 MPa (40000 kPa) | modelo | real, teqp | G4-01 §6 |
| T (piso) | línea sólido-líquido-vapor T_tr(x), ec. (9) de G4-01 (ver `CONTEXT.md`, coeficientes c11..c42 y tramos por x molar). Valores de control (x_b másica → T_tr): 0.05→267 K, 0.20→236, 0.35→175, 0.55→190, 0.65→194, 0.75→188, 0.95→192 | modelo | real, teqp | G4-01 ec. (9) |
| T (techo) | > 420 K en líquido | respaldo_experimental | real, teqp | G4-01 §6 |
| P en vapor | > 10 MPa (10000 kPa) en vapor | respaldo_experimental | real, teqp | G4-01 §6 |

DECISIÓN (usuario, 2026-10-01): los límites son SOLO los declarados por Tillner-Roth & Friend /
IAPWS G4-01 (las 4 filas de arriba), iguales para `real` y `teqp`. NO incluir límites de envoltorio
(bracket 230–650 K de teqp, piso 233 K del flash real, constante 2500): son fallos del motor que se
tratan aparte (p. ej. protección A+B) y no se mezclan aquí. El campo `tipo` queda en
`modelo` | `respaldo_experimental`; `motor` sigue en la estructura para poder diferenciar luego.

Notas: (1) "vapor"/"líquido" (límites de 420 K y 10 MPa): usar `estado.fase` si no es `None`; si es
`None`, calcularla con `backend.fase_de(P, T, x)` (método ya existente de `PropertyBackend`; decisión
del usuario 2026-10-03). Bifásico → aplicar ambos límites (hay líquido y vapor). Si `fase_de` lanza
`PropertyRangeError`, no adivinar: la violación se registra con `parametro="fase"` y el mensaje real.
Con `motor_rango=None` NO se llama a `fase_de` (cero costo extra). (2) La constante 2500
de Psat de NH3 sobre 405.3 K existe en ambos motores pero solo en el valor inicial del flash: NO la
conviertas en límite; menciónala en RECOMMENDATIONS. (3) Verifica los valores de control de T_tr con
tu implementación de la ec. (9); si no reproducen (±1 K), repórtalo en UNRESOLVED, no ajustes.

## Paso 0 — verificación previa (antes de escribir código)
a) Releer §6 de `reference/IAPWS_G4-01_nh3h2o.pdf` y confirmar uno por uno los valores de la tabla
   "Límites"; cualquier diferencia → UNRESOLVED y NO continuar con ese límite.
b) NO correr `pytest` completo (tarda > 2 min y tu shell lo corta; ya pasó dos veces). Claude ya
   corrió la línea base completa (`resultados/2026-10-03_ejemplo_fuera_rango/baseline_pytest_completo.txt`,
   NO la toques) y correrá la comparación final completa él mismo. Tú corre SOLO, antes y después de
   tus cambios, este subconjunto rápido y guarda ambos resúmenes en
   `resultados/2026-10-03_ejemplo_fuera_rango/subset_antes.txt` y `subset_despues.txt`:
   `python -m pytest -q tests/test_sensitivity.py tests/test_sensitivity_verificacion.py
   tests/test_export.py tests/test_restricciones.py tests/test_restricciones_convenciones.py`
   más tus tests nuevos (`tests/test_rangos_motor.py`). Si un comando supera ~100 s, pártelo por
   archivo en vez de reintentar entero.

## Diseño pedido
1. `src/rangos_motor.py`: `LIMITES` (datos), `Violacion` (dataclass: `parametro`, `estado`
   (etiqueta "1".."10" o "entrada"), `valor`, `limite`, `motor`, `tipo`, `columna`) y
   `evaluar_rango(motor, resultado_ciclo)` → lista de `Violacion`. Y `evaluar_rango_entradas(motor,
   combo)` para filas NO_CONVERGIO, donde no hay estados: chequear solo las entradas
   (`P_alta`, `P_baja` vs P; `T_fuente`, `T_sumidero` vs T; `x_b` con el piso de T) — así
   `fuera_rango=True` explica por qué no convergió.
   Cada violación emite `warnings.warn` (clase propia `RangoMotorWarning`) y `logging.warning`
   con parámetro, valor, límite y motor.
2. `src/sensitivity.py`: keyword nuevo `motor_rango: str | None = None` en `ejecutar_barrido`
   (+ `modo_rango="extrapolar_marcar"`). `None` → comportamiento y tabla EXACTAMENTE como hoy.
   Con valor: cada fila gana `fuera_rango` (bool), `detalle_rango` (texto, ej.
   `"T4=431.2 K > 420 K (respaldo_experimental) [motor: teqp]; P2=..."`) y `columnas_rango`
   (nombres de columna separados por `;`, ej. `"T4;P_alta"`). `tabla_barrido` añade las tres al
   final solo si alguna fila las tiene (mismo patrón que COLUMNAS_A/B). NO cambiar `clasificacion`.
   `sensitivity.py` ya tiene exactamente 200 líneas: TODA la lógica nueva va en
   `src/_rango_barrido.py`; en `sensitivity.py` solo el keyword y la llamada, compensando líneas
   (p. ej. compactando un docstring) para no pasar de 200.
3. `scripts/formatear_excel_barridos.py` y `src/export_excel.py`: celdas listadas en
   `columnas_rango` con relleno gris `BFBFBF` (el gris gana sobre el color de clase solo en esas
   celdas) y comentario de celda con `detalle_rango`. Hoja Resumen/descripción: una línea que
   explica el gris. Sin esas columnas, la salida es idéntica a hoy.
4. Tests en `tests/test_rangos_motor.py` (backend mockeado, sin motor real salvo un humo): dentro de
   rango → sin violaciones y tabla idéntica; cada límite de la tabla genera su violación con
   parámetro/valor/límite/motor correctos; los valores de control de T_tr; KALINA + fuera_rango
   conviven; NO_CONVERGIO usa chequeo de entradas; `modo="bloquear"` → NotImplementedError;
   Excel: la celda correcta queda `BFBFBF` y tiene comentario.
5. Ejemplo: generar `resultados/2026-10-03_ejemplo_fuera_rango/ejemplo_fuera_rango.xlsx` con ≥6 filas
   (mezcla de dentro/fuera de rango, ≥1 KALINA marcada, ≥1 NO_CONVERGIO marcada) construidas con
   estados sintéticos/mock (NO correr barridos reales de 30 s/punto).
6. `docs/rangos_motor.md` (≤ 1 página): tabla de límites con fuente, decisión (ejes independientes,
   modo A), cómo activar, cómo leer el Excel, y qué queda pendiente (modo bloquear, UI).

## Criterios de aceptación
`pytest` completo verde (los previos no se tocan); cobertura del módulo nuevo > 80 %; sin
modificaciones en `src/properties/`; ejemplo Excel abre con celdas grises + comentarios.

## Formato de salida
El de `AGENTS.md` (STATUS … RECOMMENDATIONS). No leer nada fuera de este directorio.
