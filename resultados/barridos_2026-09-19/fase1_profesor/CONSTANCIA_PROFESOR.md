# CONSTANCIA — Fase 1: datos EXACTOS del profesor corridos tal cual

- **Tarea**: `2026-09-19-fase1-profesor` (rama `test/vv-strategy` ya mergeada).
- **Fecha de corrida**: 2026-09-19.
- **Objetivo de la fase**: transcribir literalmente el enunciado real del profesor
  (Word "5 CICLO KALINA", datos transcritos por el director en
  `TASK_CONTEXT_fase1_profesor.md`) al solver de este repo, correr el punto base y
  los 3 barridos de sensibilidad pedidos, y **dejar constancia del resultado real,
  converja o no** — este NO es un ejercicio de optimización.

## 1. Valores usados (exactos, sin ajustes)

| Parámetro | Valor | Fuente |
|---|---|---|
| Fluido | NH3-H2O, `m_b` = 1.0 kg/s, `x_b` = 0.50 | Enunciado |
| `T_fuente` | 623.15 K (350 °C) — fija en todo el ejercicio | Enunciado |
| `T_sumidero` base | 300.032917 K = **promedio** de `tamb_profesor.csv` | Tabla horaria real del enunciado (24 valores) |
| `eps_hrvg` | 0.85 | Enunciado |
| `eps_cond` | 0.80 | Enunciado |
| `P_alta` | 3000 kPa (puntos 1,2,3,5,6,10) | Enunciado |
| `P_baja` | 400 kPa (puntos 4,7,8,9) | Enunciado |
| `eps_reg` | 0.75 | Enunciado |
| `eta_t` / `eta_p` | 0.85 / 0.75 | Enunciado |
| Válvula | isoentálpica (ya implementada en `src/components/valvula.py`, no tocada) | Enunciado |

**Decisión documentada (opción autorizada por el TASK_CONTEXT, punto 1 del Approach):**
para el punto base se usó `T_sumidero` = 300.032917 K (promedio de la tabla horaria,
que coincide exactamente con el default de `CONTEXT.md`). La tabla horaria completa se
barró en el 3er barrido. `T_fuente` se mantuvo siempre en 623.15 K — la tabla de
T_ambiente es el sumidero/ambiente, no la fuente (el enunciado las fija por separado).

## 2. Punto base — motor real (`AmmoniaWaterAdapter`, IAPWS G4-01)

- Parámetros: `P_alta=3000, P_baja=400, x_b=0.50, T_fuente=623.15,
  T_sumidero=300.032917, m_b=1.0, eta_t=0.85, eta_p=0.75, eps_hrvg=0.85,
  eps_reg=0.75, eps_cond=0.80`.
- **Resultado: `NO_CONVERGIO`** (104.5 s).
- Mensaje:
  `equilibrio_liquido_vapor(P=3000.0 kPa, T=623.000001690135 K): no existe
  equilibrio bifásico para ninguna composición (T fuera de la campana binaria a esa P,
  motor IAPWS G4-01).`
- Nota observada: el motor real emitió `RuntimeWarning` internos de iapws
  (overflow en `exp` de fugacidad y `divide by zero` en `log` del flash) al intentar
  resolver el estado fuera de la campana. No alteran el resultado: el punto se clasifica
  `NO_CONVERGIO` con el mensaje esperado.

## 3. Barridos de sensibilidad pedidos por el enunciado (motor `TeqpAdapter`, rápido)

Cada punto, converja o no, quedó registrado en un CSV propio con la variable barrida,
el resto de parámetros fijos, `convergio`, `clasificacion`, `eta`, `Wnet` y `mensaje`
(columnas de `tabla_barrido` de `src/sensitivity.py`).

### 3.1 `P_alta` — 2000 a 4000 kPa, paso 250 kPa (9 puntos), resto base

| Clasificación | Conteo |
|---|---|
| NO_CONVERGIO | 9 |
| **KALINA** | **0** |
| Convergencias | 0 |

Mecanismo en todos los puntos: `equilibrio_liquido_vapor(P_alta, T≈623.0 K)` — el
estado 2 del HRVG queda sobrecalentado fuera de la campana bifásica (rocio ≈ 465-510 K
según P_alta) y el separador no puede flashear una corriente monofásica.

### 3.2 `x_b` — 0.40 a 0.70, paso 0.05 (7 puntos), resto base

| Clasificación | Conteo |
|---|---|
| NO_CONVERGIO | 7 |
| **KALINA** | **0** |
| Convergencias | 0 |

Mecanismo idéntico: `equilibrio_liquido_vapor(P=3000.0 kPa, T≈623.0 K)` fuera de la
campana para toda composición global barrida.

### 3.3 `T_ambiente` — las 24 horas de `tamb_profesor.csv` como `T_sumidero` (24 puntos), resto base

| Clasificación | Conteo |
|---|---|
| NO_CONVERGIO | 24 |
| **KALINA** | **0** |
| Convergencias | 0 |

Rango del sumidero: 297.95 K (hora 11) a 303.55 K (hora 17), promedio 300.032917 K.
Mecanismo idéntico: el fallo ocurre en el lado caliente (separador a P_alta/T2≈623 K),
independiente del valor de `T_sumidero` — por eso las 24 horas dan el mismo resultado.

### 3.4 Total de la fase

| Puntos corridos | NO_CONVERGIO | KALINA | Convergencias |
|---|---|---|---|
| 41 (1 base + 40 barrido) | 41 | **0** | **0** |

## 4. Conclusión explícita

**Los datos del profesor se corrieron tal cual — sin ajustar una sola variable — y el
resultado real obtenido es que NINGÚN punto (ni el base ni los 40 del barrido de
sensibilidad) clasifica `KALINA`; los 41 puntos son `NO_CONVERGIO`.**

El mecanismo es el síntoma ya documentado en este repo con `T_fuente` alto (ver
`CONTEXT.md` nota 2026-09-17 y el `b0_scan_cementera.csv` de la Fase B0, mismo
comportamiento con `T_fuente=583.15 K`): con `T_fuente=623.15 K`, el estado 2 a la
salida del HRVG queda **sobrecalentado muy por encima del punto de rocío** de la
campana bifásica a la presión alta, y el separador ideal (flash P,T directo a la
composición global, `CONTEXT.md` §Separador) no puede repartir una corriente
monofásica → `PropertyRangeError` del motor de propiedades → `NO_CONVERGIO`. Como el
tope del HRVG (y por tanto T2) está fijado por `T_fuente = 623.15 K` vía
`eps_hrvg = 0.85`, ninguna de las variables barridas (`P_alta`, `x_b`, `T_ambiente`)
puede mover T2 de vuelta al interior de la campana en este régimen.

**Reporte sin sesgo**: no hubo ningún punto que clasificara `KALINA` contra lo
esperado; si lo hubiera habido, se habría reportado igual. La conclusión es la
esperada por la experiencia previa del repo, y queda ahora documentada con la corrida
completa de los valores exactos del enunciado (punto base con el motor real IAPWS
G4-01 y barridos con `TeqpAdapter`).

## 5. Archivos generados

- `scripts/barridos_2026-09-19/fase1_profesor/correr_fase1_profesor.py` (corredor,
  ≤200 líneas).
- `scripts/barridos_2026-09-19/fase1_profesor/test_fase1_profesor.py` (tests de las
  piezas deterministas + la fila del punto base).
- `resultados/barridos_2026-09-19/fase1_profesor/eta_vs_Palta_profesor.csv`
  (9 puntos, 9 NO_CONVERGIO).
- `resultados/barridos_2026-09-19/fase1_profesor/eta_vs_xb_profesor.csv`
  (7 puntos, 7 NO_CONVERGIO).
- `resultados/barridos_2026-09-19/fase1_profesor/eta_vs_Tambiente_profesor.csv`
  (24 puntos, 24 NO_CONVERGIO; columna extra `hora` para trazabilidad con la tabla
  horaria del enunciado — el barrido variable es `T_sumidero`).

## 6. Notas

- Tope estimado del TASK_CONTEXT (~25 puntos con TeqpAdapter) vs. corrida real: la
  enumeración explícita del enunciado (9 + 7 + 24 = 40 puntos) prevalece para cumplir
  los 3 barridos pedidos literalmente; se documenta aquí la diferencia.
- No se modificó ningún archivo de `src/` ni de las carpetas `fase2_libre/` o
  `fase3_real/` (tareas paralelas).