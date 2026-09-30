---
project: ciclo_kalina_tercero
task_id: 2026-09-27-rama-pr-master
delegated_to: executor
model: opencode/big-pickle
created: 2026-09-27
---

# TASK_CONTEXT — Preparar una rama desde `origin/master` con los 2 commits locales (sin push)

## Task ID

2026-09-27-rama-pr-master

## Contexto

Repo en `D:\Desktop\ciclo_kalina_tercero`, remoto `origin` =
`https://github.com/Andressc19/cycle-kalina.git`. La rama local
`test/teqp-con-validacion` tiene 2 commits que NO están en ninguna rama remota:

1. `9c40f64` — test(v&v): verificación IAPWS G4-01, límites de teqp y validación por
   tendencias vs Elsayed (23 puntos).
2. `aba754a` — feat(propiedades): protección A+B del motor teqp contra raíces
   espurias en la zona de fase.

`origin/master` avanzó por otro camino (19 commits que la rama local no tiene, varios
con el mismo contenido que commits locales pero como copias distintas). Además en
`master`: `TASK_CONTEXT_*.md` y `Kalina_ksc_11_tercero.md` se movieron a `prompts/`,
los `.log` dejaron de versionarse (están en `.gitignore`), existe `src/ui_campos.py`,
y `requirements.txt` quedó con versiones fijas.

Objetivo: dejar lista, **en local y sin push**, una rama nueva basada en
`origin/master` con esos 2 commits aplicados, respetando las convenciones de `master`,
y con la suite corrida. Claude revisa después y hace el push y el pull request.

**No ejecutes ni modifiques ningún otro `TASK_CONTEXT*.md`.**

## Pasos

### 1. Rama y worktree nuevos (no tocar la carpeta principal ni sus ramas)

```
cd D:/Desktop/ciclo_kalina_tercero
git fetch origin
git worktree add .claude/worktrees/pr-proteccion-teqp -b feat/proteccion-teqp-AB origin/master
```
Todo lo demás se hace DENTRO de `.claude/worktrees/pr-proteccion-teqp`. No cambies la
rama de la carpeta principal ni hagas checkout ahí.

### 2. Aplicar los 2 commits, en este orden

```
git cherry-pick 9c40f64
git cherry-pick aba754a
```
Si hay conflictos, resuélvelos a mano con este criterio y luego `git cherry-pick
--continue` (conservando el mensaje original del commit):
- Documentación (`CONTEXT.md`, `README.md`, etc.): **conservar el contenido de ambos
  lados** (lo de `master` + lo nuevo del commit). No borres secciones de `master`.
- Archivos que `master` movió a `prompts/` (`TASK_CONTEXT_*.md`,
  `Kalina_ksc_11_tercero.md`, `VALIDACION_ELSAYED2013.md`): si el commit los añade o
  modifica en la raíz, ponlos en `prompts/` como hace `master`.
- `.log`: `master` no los versiona. Si un commit añade archivos `.log`, sácalos del
  índice (`git rm --cached <archivo>`) en ese mismo paso de resolución, o, si el
  cherry-pick entró sin conflicto, en un commit aparte
  `chore: deja de trackear .log de resultados (convención de master)` — solo ese
  cambio.
- Código (`src/`, `tests/`, `scripts/`): si hay conflicto, NO inventes una
  resolución: aborta ese cherry-pick (`git cherry-pick --abort`), describe el
  conflicto exacto en UNRESOLVED y detente.
No hagas ningún otro commit ni cambio de código fuera de lo anterior.

### 3. Verificar

Con `D:/Desktop/ciclo_kalina_tercero/.venv/Scripts/python.exe` y cwd en el worktree
(el worktree no tiene `.venv` propio):
- `python -u -m pytest -q -p no:cacheprovider --ignore=tests/test_validacion_elsayed2013.py --ignore=tests/test_ammonia_water_adapter.py`
  con salida a `pytest_pr.txt` **dentro del worktree** (nunca `/tmp`, y NO lo
  agregues a git).
- Esperado: los 2 fallos de `test_restricciones_convenciones.py` por `src/ui_campos.py`
  deberían DESAPARECER (en `master` ese archivo existe). Los 6 fallos de
  `tests/test_verificacion_iapws_g4.py` (Cv y w de teqp vs guía IAPWS, error
  ~0.1-0.4 %) vienen del commit 1 y son conocidos. Cualquier otro fallo: repórtalo con
  la línea del error.
- `python -m py_compile app.py` (comprobar que la app al menos compila).
- Verificar que `src/properties/teqp_verificado.py`, `src/verificacion_motor_real.py`
  y los tests `test_teqp_verificado.py`, `test_verificacion_motor_real.py`,
  `test_sensitivity_verificacion.py` existen y pasan.

## Prohibido

- `git push`, crear PR, tocar remotos.
- Modificar la carpeta principal o sus ramas.
- Cambios de interfaz (`app.py`, `src/ui_*.py`) más allá de lo que traigan los
  cherry-picks/`master`.

## Salida

RESULTS con: `git log --oneline origin/master..HEAD`, la lista de conflictos que hubo
y cómo se resolvió cada uno, `git status --short`, y el resumen de la suite
(pasados/fallados/omitidos, lista de fallados).
