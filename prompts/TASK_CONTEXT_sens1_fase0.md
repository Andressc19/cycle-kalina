# TASK_CONTEXT — Sensibilidad 1, Fase 0 (columnas nuevas + punto H* + escalado con m_b)

**Fecha:** 2026-10-14 · **Rama:** `test/sensibilidad_1`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree). TODO se
crea y se ejecuta aquí; no se escribe nada fuera de él.
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y modifican SOLO con las herramientas `write` y `edit`. NUNCA desde la terminal
  (nada de `cat <<`, here-strings, `Set-Content`, `python -c` que escriba archivos).
- La terminal es Windows PowerShell 5.1: solo para EJECUTAR. No existe `tee` (usa
  `... 2>&1 | Tee-Object -FilePath <ruta>`) ni `&&` (usa `;`).
- **El paso de corrida tarda ~5–10 min. Al ejecutarlo con la herramienta de shell, pasa
  `timeout=7200000` (por defecto es 120 s y corta la corrida). Espera a que termine; no lo relances.**
- Ejecuta en primer plano. No uses `Start-Process`.

## Objetivo

1. Hacer que el script de barridos **guarde** las energías y entalpías que el motor ya calcula y hoy se
   descartan (sin tocar `src/`).
2. Correr un punto de referencia **H\*** (Húsavík con ε_cond = 0.90) y comprobar si es KALINA.
3. Comprobar si, al variar el caudal m_b, η y la clase se mantienen y las potencias escalan con m_b.

## Restricciones

- **NO modificar nada en `src/`, `app.py`, `ui_*.py`.** `src/` es solo librería.
- Cada `.py` nuevo o modificado: máximo 200 líneas.
- No inventes valores. Si algo falta, repórtalo en UNRESOLVED.
- **Cada número del reporte debe salir de un archivo generado en esta tarea.** Si algo falla, STATUS
  `partial` o `failed` y se dice cuál.
- El comportamiento por defecto de `evaluar_punto` NO debe cambiar (otros scripts lo usan).

## Paso 1 — Modificar `scripts/barrido_final/comun.py`

Añade a `evaluar_punto` un parámetro por palabra clave `extra: bool = False`. Con `extra=False` el
resultado es EXACTAMENTE el de hoy (mismas columnas, mismos valores). Con `extra=True`, cuando el punto
converge (rama `else` tras `resolver_ciclo`), añade a la fila estas columnas, tomadas del dict `res`
(que ya trae `estados` y las energías, ver `src/cycle_solver.py` y `src/_cycle_loops.py`):

| Columna | Origen |
|---|---|
| `Qi`, `Qout`, `Wt`, `Wp`, `Qreg` | `res["Qi"]`, `res["Qout"]`, `res["Wt"]`, `res["Wp"]`, `res["Qreg"]` [kW] |
| `m_v`, `m_l` | `res["estados"]["e3"].m`, `res["estados"]["e5"].m` [kg/s] (e3 = vapor a turbina, e5 = líquido del separador) |
| `dh_turb` | `res["estados"]["e3"].h − res["estados"]["e4"].h` [kJ/kg] (salto de entalpía real de la turbina, e3→e4) |
| `T_e1` … `T_e10` | `res["estados"][f"e{i}"].T` [K] |
| `h_e1` … `h_e10` | `res["estados"][f"e{i}"].h` [kJ/kg] |

Añade los nombres a una tupla `COLS_EXTRA` y exporta `COLS_EXTRA` en `__all__`. Si el punto no converge,
esas columnas quedan en `None`. Con `extra=True` las claves faltantes de la fila deben inicializarse en
`None` para que el CSV tenga siempre las mismas columnas.

## Paso 2 — Crear `scripts/sens1/fase0_corrida.py` (≤ 200 líneas)

**Copia el patrón de `scripts/barrido_final/m3_ofat.py`** (líneas 12–25): `sys.path[:0] = [str(_RAIZ),
str(_DIR_COMUN)]` apuntando a `scripts/barrido_final`, y `from comun import COLS, COLS_EXTRA,
evaluar_punto`; `ProcessPoolExecutor` con 5 procesos y bloque `if __name__ == "__main__":`. Motor
`teqp`. Se ejecuta como script, no como módulo.

**Puntos a evaluar (11 en total), con `t_amb_diseno=283.15` en todos:**

Base H\* (valores fijos, tomados de la Fase 3 de Húsavík, estudio 6.2 de la campaña previa; solo
`eps_cond` cambia de 0.95 a 0.90 por el nuevo tope):

```
T_fuente=394.15, T_sumidero=278.15, P_alta=3300.0, P_baja=690.0, x_b=0.82, m_b=1.0,
eta_t=0.85, eta_p=0.80, eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.90
```

| Id | Cambio respecto a H\* |
|---|---|
| `H0` | ninguno (m_b = 1.0) |
| `H0_noextra` | ninguno, pero evaluado con `extra=False` (control de no-regresión) |
| `M5`, `M10`, `M15`, `M20` | `m_b` = 5, 10, 15, 20 |
| `E95` | `eps_cond` = 0.95 (reproduce Húsavík tal cual) |
| `E85`, `E80` | `eps_cond` = 0.85 y 0.80 |
| `P600`, `P800` | `P_baja` = 600 y 800 (por si H\* cae al borde de O2) |

Salidas en `resultados/2026-10-14_sens1_fase0/`:
- `fase0_filas.csv`: una fila por punto, con `id_punto` + columnas de `COLS` + `COLS_EXTRA`.
- `fase0_log.txt`.

## Paso 3 — Crear `scripts/sens1/fase0_reporte.py` (≤ 200 líneas)

Lee `fase0_filas.csv` y escribe `resultados/2026-10-14_sens1_fase0/fase0_resumen.md` con:

1. Tabla de los 11 puntos: `id_punto`, `clasificacion`, `convergio`, `eta` [%], `Wnet`, `m_O2`, `Qi`,
   `Qreg`, `dh_turb`, `t_s`.
2. **Control de no-regresión:** `H0` vs `H0_noextra` — `eta`, `Wnet` y `clasificacion` iguales
   (diferencia absoluta de η < 1e-9). Imprime las diferencias.
3. **Escalado con m_b** (`H0`, `M5`, `M10`, `M15`, `M20`): para cada uno, `|η − η_H0|`, ¿misma
   clasificación?, y `Wnet/m_b`, `Qi/m_b`, `Qreg/m_b` relativos a `H0` (razón; debe ser ≈ 1 si escala).
   Reporta el valor máximo de cada desviación y di "ESCALA" si todas las razones están dentro de 1e-4 y
   η coincide a 1e-6 con la misma clase; si no, "NO ESCALA" y en qué.
4. **Un punto genuino** es `convergio=True` y `clasificacion != "NO_CONVERGIO"`. Cuenta cuántos de los 11
   lo son (los N2 espurios no cuentan).

## Paso 4 — Ejecutar (en este orden, desde el directorio de trabajo)

```
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\sens1\fase0_corrida.py 2>&1 | Tee-Object -FilePath resultados\2026-10-14_sens1_fase0\fase0_log.txt
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\sens1\fase0_reporte.py
```

Crea la carpeta `resultados\2026-10-14_sens1_fase0` antes de correr (el script puede crearla con
`Path.mkdir(parents=True, exist_ok=True)`).

## Paso 5 — Reporte final

Usa el formato obligatorio de `AGENTS.md`. En RESULTS pega la tabla del punto 1 y las conclusiones 2 y 3
de `fase0_resumen.md` TAL CUAL salieron del archivo.
