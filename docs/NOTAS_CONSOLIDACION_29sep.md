# Consolidación a la versión base — corte 29/09/2026

Rama: `integracion/KSC_11_base_29sep`. Parte del tag `KSC_11_V.10.09.26` (rama
`test/teqp-con-validacion`, con la protección A+B del motor teqp) y le suma lo que
solo existía en otras líneas de trabajo.

## Qué se integró

| Origen | Aporta |
|---|---|
| `test/teqp-con-validacion` (base) | Protección A+B (`TeqpVerificado`, `verificar_turbina`), validación Elsayed 2013 (23 puntos), verificación IAPWS G4-01, `T_amb_diseno` configurable |
| `origin/master` | `src/ui_campos.py` (esquema de campos), 3 fases de barrido (profesor / libre / Húsavik) con sus tests, versiones fijadas en `requirements.txt`, `prompts/` |
| `test/fases-sensibilidad` | Reclasificación del histórico de barridos al catálogo de 4 niveles, rondas 5 y 6 de Fase 2 |
| `fix/clasificacion-o1-c1-o5-corregible` | Catálogo de 4 niveles en el código (`src/restricciones/`) |
| Material sin commitear (checkout principal y worktrees auxiliares) | Scripts y resultados de los barridos 21–27/09, `TASK_CONTEXT_*`, `Papers/`, Excel, entregable |

## Clasificación vigente (29/09/2026)

`NO_CONVERGIO < INVIABLE < CORREGIBLE < KALINA`. Se eliminan `VALIDO_ADVERTENCIA` y
`DEGENERADO`:

- `VALIDO_ADVERTENCIA → CORREGIBLE` (O1, título de turbina bajo 0.90; C1, banda de
  composición estrecha: ajustables en diseño).
- `DEGENERADO → INVIABLE` (O5, sobrecalentado: el ciclo degenera a Rankine).
- Ningún umbral numérico cambia.

Todo dato y script posterior a esa fecha debe usar solo estos 4 nombres.

## Conflictos resueltos al integrar

- `sensitivity.py`, `tests/test_sensitivity.py`, `CONTEXT.md`: se conserva la versión con
  A+B (la de `master` era la anterior); el docstring usa los nombres de 4 niveles.
- `ui_helpers.py`, `ui_inputs.py`, `requirements.txt`: versión de `master` (esquema
  `ui_campos`, `T_amb_diseno`, versiones fijadas). El tag no tenía cambios propios ahí.
- `.gitignore`: el patrón `.log` de `master` no ignoraba `*.log`; queda `*.log`.
- Archivos de barridos Fase 2/3: versión de `test/fases-sensibilidad` (ya reclasificada).
- Los dos `TASK_CONTEXT.md` de la raíz (límites teqp / catálogo 4 niveles) pasan a
  `prompts/` con nombre propio.

## Reclasificación de barridos y verificaciones

Solo texto, sin re-resolver ningún punto del ciclo:

- Scripts de fases 2 y 3 (`peso`, `ORDEN_MAPA`, conjuntos válidos de los tests): 4 niveles.
- `resultados/2026-09-22_o2_tamb_realista/reclasificacion_o2.csv`: 2 filas
  `VALIDO_ADVERTENCIA → CORREGIBLE` (solo fallaba O1).
- `resultados/barridos_2026-09-19/fase2_libre/spotcheck_motor_real_fase2.json`: ídem.
- Los `REPORTE_*.md`, `BASE_LIBRE.md` y `PRESCAN_EPS_HRVG.md` describen corridas pasadas y
  conservan los nombres de la época como registro histórico; no se reescriben.
- Componentes (`src/components/`) y motor de propiedades (`src/properties/`): sin cambios.

## Estructura de carpetas

```
prompts/    TASK_CONTEXT_*.md, prompt base, VALIDACION_ELSAYED2013.md (v2)
docs/       planteamiento matemático, presentación, estas notas
datos/      Excel de barridos y JSON sueltos
entregable/ .docx del Entregable 1 y sus fuentes
Papers/     PDFs de referencia y resumen de utilidad
scripts/    barridos, validaciones y diagnósticos
resultados/ una carpeta por corrida + BITACORA_BARRIDOS.md
```

Los `opencode_run_*.log` y otros `*.log` dejan de versionarse (`*.log` en `.gitignore`).
Rutas ajustadas por el movimiento: `scripts/consolidar_excel_barridos.py` y
`scripts/barridos_2026-09-19/excel_iteraciones.py` ahora leen/escriben en `datos/`.
