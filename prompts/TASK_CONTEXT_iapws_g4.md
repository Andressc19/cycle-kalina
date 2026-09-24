---
project: ciclo_kalina_tercero
task_id: 2026-09-23-verificacion-iapws-g4
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-23
---

# TASK_CONTEXT — Verificación de los dos motores NH3-H2O contra las Tablas 6–8 de IAPWS G4-01

## Task ID

2026-09-23-verificacion-iapws-g4

## Project

`ciclo_kalina_tercero`, rama `test/teqp-con-validacion`. Para la actividad académica hace
falta evidencia **dentro de este repo** de que los motores de propiedades reproducen los
valores oficiales de verificación de la guía IAPWS G4-01 (Tillner-Roth & Friend 1998). Hoy
solo hay una mención en docstrings de que `_nh3h2o_engine.py` se validó "en el proyecto
hermano" — no hay prueba aquí — y `TeqpAdapter` nunca se comparó contra la guía.

La guía está copiada en `reference/IAPWS_G4-01_nh3h2o.pdf` (§8, Tablas 6, 7, 8). Los valores
ya están transcritos abajo: **úsalos tal cual, no los reescribas de memoria**. En toda la
tarea `x` = fracción **MOLAR** de NH3 (así la usa la guía).

## Valores de referencia (transcritos de IAPWS G4-01 §8)

**Tabla 6 — región monofásica** (entrada: x, T [K], ρ [mol/dm³]; salida: f [J/mol],
p [MPa], Cv [J/(mol·K)], w [m/s]):

| x | T | ρ | f | p | Cv | w |
|---|---|---|---|---|---|---|
| 0.1 | 600 | 35 | -13734.1763 | 32.1221333 | 53.3159544 | 883.925596 |
| 0.1 | 600 | 4 | -16991.6697 | 12.7721090 | 52.7644553 | 471.762394 |
| 0.5 | 500 | 32 | -12109.5369 | 21.3208159 | 58.0077346 | 830.295833 |
| 0.5 | 500 | 1 | -18281.3020 | 3.6423080 | 36.8228098 | 510.258362 |
| 0.9 | 400 | 30 | -6986.4869 | 22.2830797 | 51.8072415 | 895.748711 |
| 0.9 | 400 | 0.5 | -13790.6278 | 1.5499708 | 32.9703870 | 478.608147 |

**Tabla 7 — puntos de burbuja** (entrada: x_L, T; salida: p_BUB [MPa], x_v, ρ_L, ρ_v [mol/dm³]):

| x_L | T | p_BUB | x_v | ρ_L | ρ_v |
|---|---|---|---|---|---|
| 0.2 | 300 | 0.040710 | 0.9360 | 51.941 | 0.01640 |
| 0.4 | 400 | 2.5545 | 0.9363 | 43.318 | 0.8608 |
| 0.6 | 500 | 16.698 | 0.7844 | 25.459 | 8.86 |

**Tabla 8 — puntos de rocío** (entrada: x_v, T; salida: p_DEW [MPa], x_L, ρ_L, ρ_v [mol/dm³]):

| x_v | T | p_DEW | x_L | ρ_L | ρ_v |
|---|---|---|---|---|---|
| 0.2 | 300 | 0.00437062 | 0.010672 | 55.16434 | 0.00175506 |
| 0.4 | 400 | 0.394694 | 0.051541 | 50.83187 | 0.122658 |
| 0.6 | 500 | 6.52607 | 0.22135 | 39.93714 | 2.00730 |

## Objective

Crear `scripts/verificacion_iapws_g4.py` que evalúe **los dos motores** en esos 12 puntos y
compare contra la tabla. Solo lectura de `src/`.

### Motor de referencia (`src/properties/_nh3h2o_engine.py`, unidades MPa, mol/dm³)

- Tabla 6: `prop(rho_mol, T, x)` → usa `P`, y los campos de Cv, w y f/energía libre que
  exponga el dict (lee el código de `prop` y de `iapws.ammonia.H2ONH3._prop` para ver los
  nombres y unidades exactos; convierte a J/mol, J/(mol·K), m/s con `Mm(x)`). Si algún campo
  (p. ej. f) no está disponible, repórtalo en el CSV como `no_disponible`, no lo derives con
  una fórmula propia salvo la de abajo.
- Tablas 7/8: `bubbleP(T, x)` / `dewP(T, x)` → (P, composición de la otra fase, ok);
  densidades con `rho_TPx(T, P, x, "l")` y `rho_TPx(T, P, y, "v")` (y al revés en rocío).

### Motor teqp (`src/properties/_teqp_engine.py` y `_teqp_flash.py`, unidades Pa, mol/m³)

- Tabla 6 con `ρ_SI = ρ·1000`, `z = [x, 1−x]`, `M = _te._MODEL`, `aig = _te._ideal_helmholtz()`,
  derivadas en la convención de teqp `A_nm = τⁿ δᵐ ∂ⁿ⁺ᵐ(α)/∂τⁿ∂δᵐ` (`get_Ar01`, `get_Ar10`,
  `get_Ar02`, `get_Ar11`, `get_Ar20`, `aig.get_Aig00`, `aig.get_Aig20`). Estas son
  las relaciones de la Tabla 4 de G4-01 escritas en esa convención — úsalas, no otras:
  - p = `_te.P_total(T, z·ρ_SI)` (Pa → MPa)
  - f = R·T·(Aig00 + Ar00)  [J/mol]
  - Cv = −R·(Ar20 + Aig20)
  - w² = (R·T/M_kg)·[1 + 2·Ar01 + Ar02 − (1 + Ar01 − Ar11)² / (Ar20 + Aig20)],
    con M_kg = `_te.Mm(x)`/1000 [kg/mol] y R = `_te.R`.
- Tablas 7/8: `_teqp_flash.bubbleP(T, x)` / `dewP(T, x)` (Pa); densidades con
  `_te.rho_liquido(T, P, xL)` y `_te.rho_vapor(T, P, xv)` (mol/m³ → mol/dm³).

## Criterios de aceptación por propiedad (fijados aquí, no los cambies)

- Tabla 6, **p**: error relativo < 1e-6 (es evaluación directa de la EOS, sin iteración).
- Tabla 6, **Cv, w**: error relativo < 1e-4.
- Tabla 6, **f**: el motor teqp usa el gas ideal de CoolProp, con otro estado de referencia
  que el de G4-01 (ver docstring de `_teqp_engine.py`), así que **se espera** una diferencia
  en f. Repórtala en J/mol, **no** la marques como fallo; para el motor de referencia sí
  aplica error relativo < 1e-6 si expone f.
- Tablas 7/8: p_BUB/p_DEW, ρ_L, ρ_v con error relativo < 1e-3; x_v / x_L con error absoluto
  < 1e-3. (La guía dice que sus dígitos reflejan "adequate agreement" entre
  implementaciones con distintos métodos iterativos; estas tolerancias son del orden del
  último dígito publicado.)
- Si un punto no converge (p. ej. burbuja a 500 K / 16.7 MPa, cerca del lugar crítico),
  se registra como `no_converge` con el mensaje real. No se oculta ni se reintenta con otra
  semilla distinta a la del código existente.

## Entregables

1. `scripts/verificacion_iapws_g4.py` (≤ 200 líneas).
2. `resultados/2026-09-23_verificacion_iapws_g4/verificacion_iapws_g4.csv`: una fila por
   (motor, tabla, punto, propiedad): valor_guia, valor_motor, error_abs, error_rel,
   tolerancia, cumple (sí/no/esperado_offset/no_converge), detalle.
3. `resultados/2026-09-23_verificacion_iapws_g4/REPORTE_VERIFICACION_IAPWS_G4.md`: tabla
   resumen por motor y tabla, cuántas propiedades cumplen, peor error por propiedad,
   conclusión explícita por motor (¿reproduce G4-01 dentro de tolerancia?). Cita la guía
   (IAPWS G4-01, 2001; Tillner-Roth & Friend, J. Phys. Chem. Ref. Data 27, 63, 1998).
4. `tests/test_verificacion_iapws_g4.py`: test pytest persistente que compruebe los mismos
   criterios (parametrizado por punto; si algún punto no converge en el script, márcalo
   `xfail` con la razón real, no lo borres). Que corra en < 2 min.

## Files

Crear solo los 4 archivos anteriores. **No modificar ningún archivo existente** (en particular
nada en `src/`). Otra tarea de OpenCode (`TASK_CONTEXT.md`, límites de teqp) puede estar
escribiendo en `scripts/limites_teqp.py` y `resultados/2026-09-23_limites_teqp/` en paralelo:
no los toques.

## Constraints

- Nunca leer fuera de `D:\Desktop\ciclo_kalina_tercero` (ver AGENTS.md). El paquete `iapws`
  instalado en `.venv` sí es parte del proyecto y puedes leerlo.
- No inventar fórmulas ni tolerancias fuera de las dadas aquí. Si una fórmula de arriba da
  un resultado claramente incoherente (p. ej. p correcto pero w muy lejos), repórtalo en
  UNRESOLVED con los números — no la "arregles" probando variantes.

## Verification

`python scripts/verificacion_iapws_g4.py` y `python -m pytest tests/test_verificacion_iapws_g4.py -q`
corridos; pegar en RESULTS la tabla resumen y la salida de pytest.
