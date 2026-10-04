---
project: ciclo_kalina_tercero
task_id: 2026-10-03-validacion-dwsim-efectividad
delegated_to: executor
created: 2026-10-03
---

# TASK_CONTEXT — Validación cruzada: solver del proyecto (motor real y teqp) vs DWSIM (Peng-Robinson) con el MISMO cierre por efectividad. SIN tocar `src/`

## Task ID

2026-10-03-validacion-dwsim-efectividad

## Project

`ciclo_kalina_tercero`. Los demás `TASK_CONTEXT_*.md` son OTRAS tareas: no los ejecutes ni los modifiques.

## Contexto (decisión del director)

DWSIM ya tiene el KCS11 del caso Elsayed cerrado por **pinch** (`scripts/dwsim/kcs11_elsayed_dwsim.py`, η=12.20 %, todos los balances por equipo cuadran) y una sonda de paquetes (`resultados/2026-10-03_dwsim_paquetes/REPORTE_PAQUETES_DWSIM.md`): **se usa Peng-Robinson (PR)**, el único con BIP NH3-H2O. Ahora se quiere que DWSIM resuelva **exactamente las mismas ecuaciones de cierre por efectividad** que el solver del proyecto (`CONTEXT.md`, `PLANTEAMIENTO_MATEMATICO.md` §2), para que la única diferencia entre ambos sea el modelo de propiedades, y medir la tolerancia: (a) motor real vs teqp del proyecto, (b) proyecto vs DWSIM.

## Cómo cargar DWSIM (ya comprobado; usa `scripts/dwsim/kcs11_elsayed_dwsim.py` como plantilla y reutiliza su topología, conexiones de puertos y AJUSTES del flash)

- Python **global** `python` (tiene pythonnet). El `.venv` NO tiene pythonnet: no lo instales.
- `load("netfx")` antes de `import clr`. Las DLL se cargan desde `D:\DWSIM`.
- **AJUSTES del flash obligatorios** (los del script plantilla: iteraciones P-H 1000, P-T 2000, tolerancias 1e-8). Con los de fábrica la válvula falla; con `NL_FastMode=False` la turbina da una FALSA convergencia (40 kW de desbalance sin error). No cambies esos ajustes.
- Para h de un estado con PR: `pp.CalculateEquilibrium(FlashCalculationType.PressureTemperature, P_Pa, T_K, [1-x, x], [0.0, 0.0], 1.0).CalculatedEnthalpy` (kJ/kg, fracciones **molares** en orden Water, Ammonia; M_NH3=17.03052, M_H2O=18.015268). Para T desde (P,h): `FlashCalculationType.PressureEnthalpy`. **Verifica** al inicio que `CalculatedEnthalpy` coincide con `Phases[0].Properties.enthalpy` de una corriente en el mismo estado (misma base); si no coincide, PARA y repórtalo.

## Objective

**Etapa 1 — DWSIM con cierre por efectividad** (`scripts/dwsim/kcs11_efectividad_dwsim.py`, ≤200 líneas, puede apoyarse en un módulo `scripts/dwsim/_kcs11_dwsim_base.py` ≤200 líneas que construya el diagrama; NO modifiques `kcs11_elsayed_dwsim.py`). Función `resolver_dwsim(P_alta, P_baja, T_fuente, T_sumidero, x_b, m_b, eta_t, eta_p, eps_hrvg, eps_reg, eps_cond) -> dict`. Misma topología que la plantilla, pero las tres especificaciones de intercambio se imponen por efectividad, con las h de referencia calculadas con el MISMO PR:
- HRVG: `h2 = h1 + eps_hrvg·(h(T_fuente, P_alta, x_b) − h1)` → calentador en modo de calor añadido, `Q = m_b·(h2 − h1)`.
- Regenerador: `h6 = h5 − eps_reg·(h5 − h(T10, P_alta, x5))` → intercambiador en modo temperatura de salida caliente, con `T6` = flash P-H(P_alta, h6, x5).
- Condensador: `h9 = h8 − eps_cond·(h8 − h(T_sumidero, P_baja, x_b))` → enfriador en modo calor retirado, `Q = m8·(h8 − h9)`.
- Lazo externo en Python (sustitución sucesiva): resolver el diagrama, recalcular las tres h de referencia y las especificaciones, actualizar la corriente de entrada de la bomba S9 con la salida del condensador, repetir hasta que T1, T6 y T9 cambien < 1e-3 K entre iteraciones (máx. 100; si no converge, devolver `convergio=False`, no inventar).
- Devuelve: `convergio`, `iteraciones`, `eta`, `Wt`, `Wp`, `Qi`, `Qout`, `T1..T10`, `x3`, `x5` (másicas), `m3`, `m5`, y la **verificación por equipo** (energía del equipo vs cambio de entalpía de corrientes, como imprime la plantilla) más el cierre global `Qi + Wp − Qout − Wt`. Además, comprueba que las efectividades RESULTANTES (recalculadas con las h finales) coinciden con las pedidas (|Δε| < 1e-4).
- Prueba de humo obligatoria antes de seguir: caso Elsayed con los eps calibrados (abajo). Guarda la salida.

**Etapa 2 — Solver del proyecto en los mismos puntos** (`scripts/dwsim/motor_puntos_validacion.py`, `.venv/Scripts/python`, ≤200 líneas): `resolver_ciclo` de `src/cycle_solver.py` con `AmmoniaWaterAdapter` (motor real) **y** con `TeqpVerificado` (`src/properties/teqp_verificado.py`). Lee las firmas en `src/` (solo leer) y la forma de uso en `scripts/regresion_teqp_verificado.py` y `tests/test_validacion_elsayed2013.py`. El motor real tarda ~5 min/punto: desacopla la corrida (`nohup ... &` o equivalente) y consulta con comandos cortos. Escribe una fila por punto y motor en `resultados/2026-10-03_validacion_dwsim/motor_puntos.csv` con `flush` tras cada fila, para poder retomar si se corta (si el CSV ya tiene la fila, no la recalcules).

**Etapa 3 — Comparación** (`scripts/dwsim/comparar_validacion.py`, ≤200 líneas): tabla por punto con η, Wnet, Qi, Wt, Wp, Qout, T1..T10, x3, x5, m3 de: motor real, teqp, DWSIM-efectividad (y DWSIM-pinch solo para Elsayed, de la plantilla). Deltas: teqp − real y DWSIM − real (absoluto y relativo). **No compares entalpías absolutas** (cada modelo tiene su estado de referencia); sí trabajos, calores, T, composiciones y caudales.

## Puntos (todos con m_b = 1 kg/s, eta_t = eta_p = 0.80)

| Etiqueta | x_b | P_alta [kPa] | T_fuente [K] | P_baja [kPa] | T_sumidero [K] | eps_hrvg / eps_reg / eps_cond |
|---|---|---|---|---|---|---|
| ELSAYED | 0.55 | 1500 | 373 | 273.5454214157179 | 283 | 0.8882023116022899 / 0.9380325550010874 / 0.9625029043677631 |
| KALINA-11 | 0.65 | 5000 | 423 | 704.644595 | 283 | 0.85 / 0.80 / 0.85 |
| KALINA-22 | 0.80 | 5000 | 394 | 952.892781 | 283 | 0.85 / 0.80 / 0.85 |
| KALINA-21 | 0.80 | 4000 | 394 | 1101.510788 | 283 | 0.85 / 0.80 / 0.85 |
| KALINA-01 | 0.60 | 3000 | 394 | 523.749936 | 283 | 0.85 / 0.80 / 0.85 |
| KALINA-16 | 0.70 | 5000 | 423 | 890.811268 | 283 | 0.85 / 0.80 / 0.85 |

Valores de referencia ya existentes para contrastar tu Etapa 2 (si tu resultado difiere en η más de 1e-4, repórtalo, no lo ajustes): KALINA-11/22/21 en `resultados/2026-09-24_verificacion/verificacion_motor_real.csv` (filas `real` y `teqp`); los 6 KALINA en `resultados/2026-09-27_teqp_verificado/regresion_22.csv` (`eta_verif`); ELSAYED real ≈ 0.11054 (`PLANTEAMIENTO_MATEMATICO.md` §7). Confirma en `scripts/regresion_teqp_verificado.py` que los parámetros fijos de esos CSV son los de la tabla (eps 0.85/0.80/0.85, T_sumidero=283, eta 0.80); si no lo son, repórtalo en UNRESOLVED.

## Constraints

- **No modificar `src/`**, tests, la interfaz (`app.py`, `ui_*.py`) ni los scripts existentes de `scripts/dwsim/`. Archivos nuevos solo: los de `scripts/dwsim/` nombrados arriba y `resultados/2026-10-03_validacion_dwsim/`. Nada en la raíz ni `.log` sueltos.
- **Rutas en bash (causa de abortos previos):** tu bash es POSIX y arranca en la raíz del proyecto. Usa SOLO rutas relativas con `/`; nunca rutas absolutas (`D:\...`, `D:/...`, `/d/...`) ni `cd` en comandos. `D:\DWSIM` solo puede aparecer DENTRO de los `.py`. El Python del venv es `.venv/Scripts/python`.
- **Nada en `/tmp` ni en el directorio temporal del sistema** (la corrida 047 se abortó por `cat > /tmp/dbg1.py`). Scripts de depuración: `resultados/2026-10-03_validacion_dwsim/_dbg_*.py`.
- **Arranque del lazo externo (diagnóstico corrida 047):** con estimados iniciales arbitrarios (T6 = media de fuente y sumidero, Q = 0) el flash P-H de T6 falla con "PR EOS: Unable to calculate compressibility factor". Arranca desde un estado físico conocido: la solución por pinch de `scripts/dwsim/kcs11_elsayed_dwsim.py` (para ELSAYED: T6 ≈ 303.8 K, T9 = 287 K, S5 ≈ 0.719 kg/s con w ≈ 0.387 a 369 K/1500 kPa, Q_hrvg ≈ 452 kW, Q_cond ≈ 397 kW); para los KALINA, desde T1..T10, x3, x5, m3 de `resultados/2026-09-24_verificacion/verificacion_motor_real.csv` (fila `real`) o, si el punto no está ahí, desde el KALINA convergido más cercano. Si aun así un flash falla, aplica sub-relajación (p. ej. 0.5) a las especificaciones nuevas y reporta; no cambies el modelo ni los eps.
- **Orden recomendado:** lanza primero la Etapa 2 (motor real, ~5 min/punto) desacoplada en segundo plano y mientras tanto trabaja la Etapa 1.
- No instalar dependencias. Cada archivo ≤200 líneas.
- Ningún comando de más de ~90 s en primer plano: desacopla y consulta con comandos cortos.
- No ajustes parámetros, eps ni el kij de PR "para que cuadre". No inventes valores: lo que falte va a UNRESOLVED.
- Registra `git branch --show-current` y `git status --short src` al inicio y al final. No ejecutes `git checkout/switch/commit/stash`.
- **No termines tras solo anunciar un paso**: trabaja con herramientas hasta cumplir los Done criteria o hasta un bloqueo real que reportes.

## Outputs

- Scripts nombrados arriba.
- `resultados/2026-10-03_validacion_dwsim/`: `humo_elsayed_dwsim.txt`, `dwsim_puntos.csv`, `motor_puntos.csv`, `comparacion.csv`, y `REPORTE_VALIDACION_DWSIM.md` con el formato: **La pregunta · Cómo funciona (en simple) · Cómo lo desarrolló OpenCode · Resultados (tabla por punto: η real / teqp / DWSIM y sus diferencias; tabla de estados del caso Elsayed) · Tiempos · Conclusión · Lo que no sabemos · Qué sigue**. Define cada término técnico en una línea. Separa lo confirmado de lo no demostrado.
- Formato de salida de AGENTS.md (STATUS … RECOMMENDATIONS).

## Done criteria

- Humo Elsayed en DWSIM-efectividad convergido, con todos los equipos cuadrando (|dif| < 0.01 kW), cierre global < 0.05 kW y efectividades resultantes = pedidas (|Δε| < 1e-4).
- Los 6 puntos resueltos en DWSIM-efectividad y con los dos motores del proyecto (o con el fallo real documentado).
- `comparacion.csv` y el reporte escritos; `src/` limpio.
