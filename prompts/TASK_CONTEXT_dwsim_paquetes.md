---
project: ciclo_kalina_tercero
task_id: 2026-10-03-dwsim-paquetes-nh3h2o
delegated_to: executor
created: 2026-10-03
---

# TASK_CONTEXT — Sonda: ¿qué paquete de propiedades de DWSIM reproduce mejor la mezcla NH3-H2O? SOLO medir, NO construir el ciclo. SIN tocar `src/`

## Task ID

2026-10-03-dwsim-paquetes-nh3h2o

## Project

`ciclo_kalina_tercero`. **Nota:** los demás `TASK_CONTEXT_*.md` son OTRAS tareas: no los ejecutes ni los modifiques.

## Contexto

El director va a recrear el KCS11 en DWSIM (punto de diseño: caso Elsayed 2013, ver `PLANTEAMIENTO_MATEMATICO.md` §7: P_alta=1500 kPa, P_baja=273.55 kPa, x_b=0.55 **másica**, T2=369 K, T9=287 K). DWSIM no trae la EOS de referencia Tillner-Roth & Friend (IAPWS G4-01) que usa el motor del proyecto. Antes de construir nada hay que medir qué paquete de DWSIM se desvía menos. **Tú solo mides y reportas; la elección la hace el director.**

DWSIM está instalado en `D:\DWSIM` (ruta de instalación del programa: se permite cargar sus DLL desde ahí; no explores otras rutas fuera del proyecto). Ya está comprobado cómo cargarlo desde Python (ver `scripts/dwsim/rankine_dwsim.py`, úsalo como plantilla de arranque):

- Python **global** `python` (3.13, tiene `pythonnet` 3.2.0). El `.venv` del proyecto NO tiene pythonnet: **no lo instales ahí**.
- `from pythonnet import load; load("netfx")` **antes** de `import clr` (con `coreclr`, el runtime por defecto, falla por `System.Windows.Forms`). `os.chdir(r"D:\DWSIM")` y añadir `D:\DWSIM` a `sys.path`/`PATH`.
- `clr.AddReference` de: DWSIM.Interfaces, DWSIM.GlobalSettings, DWSIM.SharedClasses, DWSIM.Thermodynamics, DWSIM.UnitOperations, DWSIM.Automation. Luego `Automation3()`, `CreateFlowsheet()`, `AddCompound(...)`, `CreateAndAddPropertyPackage(nombre)`, `AddObject(ObjectType.MaterialStream, x, y, nombre)`, `CalculateFlowsheet2(fs)`.
- Lo que NO está comprobado (descúbrelo y documenta cómo lo hiciste): nombres exactos de los compuestos (¿"Ammonia"? ¿"Water"?), lista de paquetes disponibles, cómo fijar la composición global de una corriente, cómo hacer flash con fracción de vapor especificada (P-VF / T-VF), cómo leer composiciones de las fases y cómo saber si un paquete tiene parámetros de interacción binaria (BIP) para el par NH3-H2O.

## Objective

1. **Inventario** (`scripts/dwsim/sonda_paquetes_dwsim.py`, Python global): listar todos los paquetes de propiedades disponibles en esta instalación. Para cada uno que acepte Agua+Amoníaco: indicar si tiene BIP no nulos para el par (valores encontrados y de dónde salen) o si usa ceros/estimación. Excluye explícitamente los de agua pura (Steam Tables, etc.) y anota por qué.
2. **Medición** con cada paquete candidato, en estos puntos (convierte másica ↔ molar con M_NH3 = 17.03052 g/mol, M_H2O = 18.015268 g/mol; deja escrita la conversión):
   - **G4-01 Tabla 7** (fracción **molar** de líquido x_L, T en K → p_bub en MPa, x_v): (0.2, 300) → 0.040710, 0.9360; (0.4, 400) → 2.5545, 0.9363; (0.6, 500) → 16.698, 0.7844.
   - **G4-01 Tabla 8** (fracción **molar** de vapor x_v, T → p_dew en MPa, x_L): (0.2, 300) → 0.00437062, 0.010672; (0.4, 400) → 0.394694, 0.051541; (0.6, 500) → 6.52607, 0.22135.
   - **Puntos del ciclo** (w = 0.55 másica): (a) T_burbuja a 273.55 kPa; (b) T_burbuja y T_rocío a 1500 kPa; (c) flash T-P a 1500 kPa y 369 K: fracción de vapor, composición de líquido y de vapor; (d) Δh = h(1500 kPa, 369 K) − h(1500 kPa, 300 K) en kJ/kg (diferencia: el estado de referencia de cada modelo se cancela).
   Si una magnitud no se puede obtener con un paquete (no converge, excepción, no expuesta), anótalo con el mensaje real; **no la aproximes**.
3. **Referencia del motor del proyecto** para los puntos del ciclo (a)–(d): script aparte `scripts/dwsim/referencia_motor_ciclo.py` con el `.venv` (`.venv\Scripts\python`) usando `AmmoniaWaterAdapter` (motor real) a través de su interfaz pública (bubble_point, dew_point, equilibrio_liquido_vapor, h…; lee `src/properties/` para ver firmas y unidades — **solo leer**). Para las Tablas 7/8 la referencia son los valores de la guía de arriba (no hace falta el motor).
4. **Tabla comparativa** `resultados/2026-10-03_dwsim_paquetes/comparacion.csv` (una fila por paquete × magnitud: valor DWSIM, referencia, error absoluto y relativo, mensaje si falló) y un resumen por paquete: error relativo medio en presiones de saturación, error absoluto medio en composiciones, error en K de las T de saturación del ciclo, error relativo en Δh, nº de fallos.

## Constraints

- **No modificar `src/`**, tests, la interfaz (`app.py`, `ui_*.py`) ni `scripts/dwsim/rankine_dwsim.py`. Archivos nuevos solo: los dos scripts de `scripts/dwsim/` y `resultados/2026-10-03_dwsim_paquetes/`. Nada en la raíz del repo ni `.log` sueltos.
- **Rutas en bash (causa del aborto de la corrida 043):** tu bash es POSIX y ya arranca en la raíz del proyecto. Usa SOLO rutas relativas con `/` (p. ej. `mkdir -p scripts/dwsim resultados/2026-10-03_dwsim_paquetes`, `git status --short src`). **Nunca** escribas rutas absolutas (`D:\...`, `D:/...`, `/d/...`) ni `cd` en comandos de bash: cualquier ruta absoluta dispara `external_directory` y aborta toda la ejecución. El Python del venv se invoca como `.venv/Scripts/python`.
- No instalar ni agregar dependencias. Cada archivo ≤200 líneas.
- Fuera del proyecto solo se permite **cargar** las DLL de `D:\DWSIM` (lo exige pythonnet); no explores, listes ni leas otras rutas externas. No escribas nada en `D:\DWSIM`. **Importante (sandbox, ver AGENTS.md):** la ruta `D:\DWSIM` solo debe aparecer DENTRO de los `.py`; nunca la pongas en un comando de bash (ni `ls`, ni `python -c "..."`, ni `Get-ChildItem`), porque el sandbox lo rechaza y aborta toda la ejecución. Para explorar la API de DWSIM, escribe un script `.py` dentro de `scripts/dwsim/` (o de `resultados/2026-10-03_dwsim_paquetes/`) y ejecútalo con `python <ruta_relativa>.py`; usa `dir()`/reflexión .NET desde Python.
- Ningún comando de más de ~90 s en primer plano; si algo tarda más, desacóplalo y consulta con comandos cortos.
- Registra `git branch --show-current` y `git status --short src` al inicio y al final. No ejecutes `git checkout/switch/commit/stash`.
- No elijas el paquete ni ajustes BIP "para que cuadre": solo mide con lo que trae DWSIM.
- Sin credenciales.

## Outputs

- `scripts/dwsim/sonda_paquetes_dwsim.py`, `scripts/dwsim/referencia_motor_ciclo.py`.
- `resultados/2026-10-03_dwsim_paquetes/`: `inventario_paquetes.txt`, `comparacion.csv`, `referencia_motor.json`, salidas de consola, y `REPORTE_PAQUETES_DWSIM.md` con el formato: **La pregunta · Cómo funciona (en simple) · Cómo se hizo (incluye cómo se descubrió cada llamada de la API de DWSIM) · Resultados (tabla resumen por paquete) · Lo que no sabemos · Qué sigue**. Define cada término técnico en una línea (BIP, flash, punto de burbuja/rocío).
- Formato de salida de AGENTS.md (STATUS … RECOMMENDATIONS).

## Done criteria

- Inventario completo con el estado de BIP de cada paquete candidato y cómo se determinó.
- Las 6 filas G4-01 + los 4 puntos del ciclo medidos (o con fallo documentado) para cada candidato.
- Referencia del motor para (a)–(d) calculada con `AmmoniaWaterAdapter`.
- `git status` muestra solo los archivos permitidos; `src/` limpio.
