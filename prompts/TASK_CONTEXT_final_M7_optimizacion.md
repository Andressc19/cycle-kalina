# TASK_CONTEXT — M7: optimizar η dentro de la región KALINA ya determinada (búsqueda por patrones)

**Fecha:** 2026-10-07 · **Rama:** `test/barrido_final`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barrido-final`.
TODO se crea y se ejecuta aquí.
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`
**Leer antes de empezar:**
- `docs/MATEMATICA_ITERACIONES_SENSIBILIDAD.md` §7.2 (búsqueda por patrones con objetivo
  lexicográfico);
- `scripts/barrido_final/comun.py`;
- `resultados/2026-10-07_final_M4b/m4b_top_kalina.csv`;
- `resultados/2026-10-06_final_M2S/m2s_kalina.csv`;
- `resultados/2026-10-07_final_M5/m5_cercano_profesor.csv`;
- `resultados/2026-10-07_final_M5c/` (si existe).

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con las herramientas `write` y `edit`. NUNCA desde la
  terminal.
- PowerShell 5.1: no existen `tee` ni `&&`.
- **La corrida larga se ejecuta EN PRIMER PLANO y se espera a que termine; nada de
  `Start-Process`.** Usa la herramienta bash con el tiempo de espera máximo. Redirige con
  `*> archivo`.
- Las verificaciones van en un script escrito con `write`. La corrida larga se lanza UNA sola vez.

## Restricciones

- NO modificar `src/`, `comun.py` ni ningún script existente. Cada `.py` debe tener como máximo
  200 líneas. Solo motor teqp. No inventar valores. No hacer commit.
- **Punto genuino:** `clasificacion ∈ {KALINA, CORREGIBLE, INVIABLE}`. Los N2 son NO genuinos.
- Piso de O2 = T_sumidero (`t_amb_diseno=combo["T_sumidero"]`).

## Pregunta

Dentro de la región KALINA ya acotada, ¿cuál es la **máxima η** alcanzable?
1. Sin restricciones adicionales.
2. Conservando datos del profesor: con sus temperaturas (S1), con sus presiones (S2/S3) y con su
   fuente + x_b (S5).

## Método (MATEMATICA §7.2)

**Objetivo lexicográfico:** minimizar `(D, −η)`. Primero llegar a D = 0 (KALINA) y, entre los
KALINA, maximizar η.

**Algoritmo**, sobre las variables libres de cada arranque, en unidades normalizadas
u = (v − a)/(b − a):

```
paso_i = 0.10 (de su rango)
repetir:
  candidatos = para cada variable libre i: u ± paso_i·e_i (recortados a [0, 1])
  evaluar TODOS los candidatos en paralelo (pool de 7)
  mejor = el candidato con menor (D, −η), considerando solo KALINA/genuinos con D definido;
          un no genuino nunca es mejor
  si mejor < actual: actual = mejor   (se mantiene el paso)
  si no:             paso_i = paso_i / 2 para todas las i
hasta paso < 0.01 o 120 evaluaciones por arranque
```

**Caja de búsqueda:**

| Variable | Rango |
|---|---|
| T_fuente | 380–500 K |
| T_sumidero | 278.15–303.55 K |
| P_alta | 2000–5000 kPa |
| P_baja | 300–2500 kPa |
| x_b | 0.50–0.85 |
| η_t, η_p, ε_HRVG, ε_reg, ε_cond | 0.40–0.95 |

Si P_baja ≥ P_alta − 300, el candidato se descarta.

**Arranques** (cada uno con sus variables fijas):

| Arranque | Punto de partida | Variables FIJAS (no se mueven) |
|---|---|---|
| A1 | El KALINA de mayor η de M4b (top 1 de `m4b_top_kalina.csv`) | ninguna |
| A2 | El KALINA de mayor η de M2S (base B2, 278.15 K) | ninguna |
| A3 | El KALINA de mayor η de S1 en M5 (`m5_cercano_profesor.csv`, `tipo=mejor_eta`) | T_fuente 623.15, T_sumidero 300.032917; caja de T_fuente no aplica |
| A4 | El KALINA de M2R parte 3 (T_fuente 403, ε_cond 0.95, el resto del profesor) | P_alta 3000, P_baja 400, T_sumidero 300.032917 |
| A5 | El mejor KALINA de S5 en M5 (o, si no hay fila de S5, el de mayor η de S5 en `m5_lhs.csv`) | T_fuente 623.15, x_b 0.50 |

Los arranques corren en secuencia, y las evaluaciones de cada paso se hacen en paralelo.

## Salidas (en `resultados/2026-10-07_final_M7/`)

- `m7_evaluaciones.csv`: todas las evaluaciones, escritas con flush, con las columnas `arranque`,
  `iteracion`, `paso`, `aceptado` más las de `COLS`.
- `m7_trayectorias.csv`: el punto aceptado en cada iteración, por arranque.
- `m7_optimos.csv`: el óptimo de cada arranque, con sus 10 variables, η, W_net, los márgenes de
  O1/O2/O5, `fuera_rango` y `B_verificado`.
- `m7_convergencia.png`: η contra la iteración, una línea por arranque.

## Reporte `REPORTE_M7.md` (lenguaje llano)

1. La pregunta.
2. El método, en simple.
3. **Tabla de óptimos:** arranque | qué conserva del profesor | η inicial → η óptima | valores
   óptimos de las presiones (P_alta, P_baja, dP, rP) y de las demás variables.
4. **Hacia dónde empuja el optimizador** a cada variable (¿al borde de la caja? ¿a qué límite?) y
   qué criterio queda activo en el óptimo (el margen de O1/O2/O5 más pequeño).
5. Si algún óptimo queda en el borde de la caja, decirlo: el óptimo real podría estar fuera.
6. Los tiempos.
7. La conclusión.
8. Lo que no se sabe:
   - es un óptimo local;
   - las diferencias menores que 0.4–0.7 pp no son concluyentes;
   - los puntos fuera de rango.
9. Qué sigue.

## Pasos

1. Crear `m7_optimizar.py`, `m7_analisis.py` y `m7_verificar.py`, con como máximo 200 líneas
   cada uno.
2. Humo con `M7_HUMO=1`: 1 arranque con 1 iteración, con salida en `humo/`.
3. Corrida real EN PRIMER PLANO (≈ 1.5–2.5 h). Después el análisis y el reporte.
4. Verificación:
   - que las trayectorias sean monótonas en (D, −η);
   - que las variables fijas no cambien;
   - que se respeten los límites de la caja;
   - que los números del reporte coincidan con los CSV.

## Formato de salida

El obligatorio de `AGENTS.md`.
