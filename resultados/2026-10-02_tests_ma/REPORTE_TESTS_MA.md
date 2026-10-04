# REPORTE — Tests PRIMERO del bracket tolerante MA (`2026-10-02-tests-primero-ma`)

Rama: `feature/rango_motores` · Fecha: 2026-10-02 · Python: `.venv\Scripts\python`
`src/` **sin tocar** (`git status --short src` vacío al inicio y al final).

## La pregunta

¿Podemos exigirle al resolutor del ciclo que **nunca se rindas ante un estado no
evaluable**, sin romper el caso sano ni los ~11 min de la suite? La pregunta no es
"¿funciona?", sino: **¿sabemos escribir los tests queSerialization fallen hoy y que
pasarán mañana cuando alguien implemente la mejora?**

## Qué se especificó (la API de MA en lenguaje llano)

```
resolver_ciclo(..., bracket_tolerante=False, paso_repliegue=5.0,
                           max_repliegues=None, presupuesto_s=None)
```

- **Sin el flag** (por defecto): el comportamiento **debe quedar idéntico bit a bit**,
  con las mismas claves de salida y las mismas llamadas al motor de propiedades. Los
  otros tres parámetros se ignoran.
- **Con el flag (MA = "V2 desde el primer intento")**: desde la *primera* evaluación, si
  un extremo del intervalo de temperatures no es evaluable, se **repliega hacia dentro**
  `paso_repliegue` kelvin por intento (por defecto 5 K) en lugar de abandonar; **sin tope
  de intentos** salvo que se pida uno (`max_repliegues`); con `presupuesto_s` se rinde
  solo si se pasa el tiempo, y **nunca a mitad de una evaluación**.
- Solo se tolera el error de rango de propiedades: cualquier otro error sube intacto.
- La salida lleva una clave extra `bracket` **solo** con el flag, que dice qué
  intervalo quedó, cuántos repliegues hubo por lado y cuántas evaluaciones se hicieron.

## Cómo se hizo

1. **Tests primero, sin tocar `src/`.** `tests/test_bracket_tolerante.py` (200 líneas)
   fija los 15 casos contra un *fake* del motor de propiedades heredado de
   `tests/test_cycle_solver.py`, extendido con una subclase que cuenta llamadas y
   lanza `PropertyRangeError` en temperaturas elegidas. El andamiaje (tolerancias
   justas, base ancha y estrecha, temperaturas de fallo) se heredó del diseño MB ya
   retirado, que quedó en `resultados/2026-10-02_tests_ma/OBSOLETO_test_reintento_tolerante_MB.py`.
2. **Se demuestra que los tests miden algo, en dos direcciones**:
   - contra el código de hoy deben fallar **por la API inexistente**, no por un error
     del fake (salida en `pytest_rojo.txt`);
   - contra un **prototipo escrito fuera del repo**
     (`C:\Users\Usuario\AppData\Local\Temp\opencode\proto_ma.py`, que sustituye
     `resolver_ciclo` por monkeypatch) deben pasar los 16 tests: prueba de que los 15
     casos son **satisfacibles** y no una lista de deseos contradictoria (salida en
     `pytest_prototipo_verde.txt`).
3. **Verificación lenta con el motor real**, fuera de la suite:
   `scripts/verificar_controles_ma.py` (124 líneas) llama a
   `resolver_ciclo(..., bracket_tolerante=True)` con `TeqpVerificado` sobre 10 filas de
   control y 8 filas rescatadas por V2, y compara `eta` y clasificación contra las
   columnas `V2_eta`/`V2_clas` de la ablación. Reutiliza la carga de parámetros por
   fila del script MB importándolo, no reescribiéndolo.
4. **El diseño anterior se retira sin borrar evidencia**: los dos archivos MB se movieron
   (con `mv`, sin borrado recursivo) a `resultados/2026-10-02_tests_ma/OBSOLETO_*_MB.py`.

## Qué se probó

Glosario de una línea: **F** = residuo de la ecuación de balance en la temperatura
`T1`; **nF** = número de evaluaciones de F (la última, con `T1` ya resuelto, no cuenta);
**repliegue** = mover un extremo del intervalo hacia dentro; **bracket** = intervalo de
temperaturas que se busca en `F`; **`PropertyRangeError`** = "este estado (P, T, x) no es
evaluable con este motor"; **`CicloNoConvergeError`** = el resolutor se rinde;
**fila rescatada** = fila que el solver actual no resuelve pero V2 sí; **HRVG** =
hiperrefrigerante de vapor; **`h1`** = entalpía a la **entrada** del HRVG, es decir a la
**salida fría del regenerador** (no la del condensador).

| # | Caso | Test | Hoy (sin MA) | Con el prototipo |
|---|------|------|--------------|------------------|
| 1 | Sin flag: idéntico bit a bit (eta, T1, claves, nº de llamadas) | `test_1` | **PASA** | pasa |
| 2 | Con flag y sin fallos: mismo eta y T1, y **mismo nº de evaluaciones de F** | `test_2` | falla (TypeError) | pasa |
| 3 | Extremo alto no evaluable: converge con el mismo eta | `test_3` | falla (TypeError) | pasa |
| 4 | Extremo bajo no evaluable; y ambos extremos con interior sano | `test_4` | falla (TypeError) | pasa |
| 5 | Todo el rango no evaluable: se rinde, con llamadas **acotadas** | `test_5` | falla (TypeError) | pasa |
| 6 | Rango sano pero sin cambio de signo de F: se rinde | `test_6` | falla (TypeError) | pasa |
| 7 | `max_repliegues`: con tope 2 y 3 fallos seguidos se rinde; con tope 3 converge | `test_7` | falla (TypeError) | pasa |
| 8 | **Por defecto no hay tope**: 12 fallos seguidos convergen; con tope 6 se rinde | `test_8` | falla (TypeError) | pasa |
| 9 | `paso_repliegue` distinto de 5 K se respeta (se comprueban las T evaluadas) | `test_9` | falla (TypeError) | pasa |
| 10 | `ValueError` se propaga sin reintento ni envoltura | `test_10` | falla (TypeError) | pasa |
| 11 | Punto **interior** no evaluable durante el buscador: se rinde con la T en el mensaje | `test_11` | falla (TypeError) | pasa |
| 12 | **Presupuesto agotado**: con reloj falso, se rinde entre evaluaciones (nunca a mitad) | `test_12` | falla (TypeError) | pasa |
| 13 | `presupuesto_s` nulo o enorme no cambia el resultado | `test_13` | falla (TypeError) | pasa |
| 14 | Sin estado compartido entre llamadas (y una fallida no contamina la siguiente) | `test_14a` / `test_14b` | **PASA** `14a` / falla `14b` | ambas pasan |
| 15 | La clave `bracket` existe solo con el flag y es coherente con las T evaluadas | `test_15` | falla (TypeError) | pasa |

Los 14 fallos de hoy son **todos** `TypeError: resolver_ciclo() got an unexpected
keyword argument 'bracket_tolerante'` — es decir, la ausencia de la API, no un error del
fake ni de importación. Los 2 que pasan (casos 1 y la parte sin flag de 14) son
precisamente los que no usan el flag: fijan que **no se puede romper lo que ya funciona**.

Verificación lenta con motor real (`scripts/verificar_controles_ma.py`, 18 filas = 10
controles + 8 rescatadas: 2 `f2_T_from_Ph`, 2 `lit_T_from_Ph`, 2 `lit_bifasico`, 1
`f2_h_Ps` + 1 de relleno): las 18 fallan hoy con el mismo `TypeError`, una línea por
fila en `progreso.log`, y ninguna fila aborta a las demás.

## Tiempos

| Qué | Cuánto |
|-----|--------|
| Suite rápida de tests MA (16 tests, sin motor real) | 1.09 s en rojo, 0.11 s en verde |
| `scripts/verificar_controles_ma.py` (18 filas) | <1 s hoy, porque todas fallan en la API |
| Comprobaciones previas para calibrar el fake (scripts temporales) | ~2 min en total |
| **Línea base de la suite completa** | `182 passed, 1 skipped, 8 xfailed` en 686 s, `resultados/2026-10-01_tests_reintento/linea_base_suite.txt` — **no se re-ejecutó** (medida con `src/` idéntico y sin el archivo MB, que ya no está en `tests/`); sigue vigente |

## Lo que no sabemos

- Si la implementación real reproducirá las columnas V2 con `|Δη| < 1e-4`. El script
  cubre 8 de las 27 filas rescatadas; el resto sigue sin comprobar con motor real.
- El caso 11 depende de que el buscador raíz visitede el mismo punto interior que el
  prototipo (`355.555093 K`). Una implementación correcta pero con otro orden de
  evaluación de `F` podría no tocar esa banda y "fallar" el test sin ser incorrecta.
- El caso 12 fija una convención de `nF` (evaluaciones de F, excluyendo la última).
  Es la lectura natural de la especificación, pero conviene que el director la confirme.
- El desbordamiento del presupuesto es como mínimo **una evaluación completa**: si una
  sola evaluación dura más que todo el presupuesto, el rebasamiento es de al menos
  una evaluación. Es lo que
  pide "comprobar entre evaluaciones", pero conviene tenerlo presente al elegir valores.
- La regla de las 8 filas rescatadas es interpretación nuestra: "2 de cada grupo, y si
  un grupo no tiene, completa con el siguiente". `f2_h_Ps` solo aporta 1 rescatada, así
  que la 8ª se tomó de `f2_T_from_Ph` (fila 907). Si el director prefiere otra regla, es
  un cambio de una línea.
- No sabemos aún el coste real del presupuesto de tiempo por punto con el motor real:
  solo está probado con reloj falso.

## Qué sigue

1. Implementar MA en `src/` (tarea siguiente, con estos tests como contrato).
2. `pytest tests/test_bracket_tolerante.py` debe dar 16/16 en verde, sin tocar los tests.
3. `scripts/verificar_controles_ma.py` completo con motor real: esperar 18 filas `OK`
   (tarda minutos: va desacoplado con `nohup`, no en la suite).
4. Solo entonces ejecutar la suite completa y comprobar que el resultado no empeora
   respecto de `182 passed, 1 skipped, 8 xfailed`.

## Archivos

- Nuevos: `tests/test_bracket_tolerante.py`, `scripts/verificar_controles_ma.py`.
- Evidencia: `pytest_rojo.txt`, `pytest_prototipo_verde.txt`, `progreso.log`,
  `OBSOLETO_test_reintento_tolerante_MB.py`, `OBSOLETO_verificar_controles_reintento_MB.py`.
- Fuera del repo: `C:\Users\Usuario\AppData\Local\Temp\opencode\proto_ma.py` (prototipo).