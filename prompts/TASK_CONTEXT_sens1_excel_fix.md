# TASK_CONTEXT — Excel Sensibilidad 1: corregir tablas, completar la síntesis y añadir hojas de regenerador, turbina y equipos

**Fecha:** 2026-10-16 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree).
**Intérprete (ruta relativa desde aquí):** `..\..\..\.venv\Scripts\python.exe`
**Código existente:** `scripts/sens1/x1_cargar.py` … `x8_verificar.py`, `x5b/x5c/x8b`, `conclusiones.py`.
**Contexto:** el director (Claude) verificó el libro `datos/Kalina_anal_sensible_1.xlsx` de forma
independiente contra los CSV. Las 12 hojas de datos coinciden con los CSV (valores redondeados), pero
el resto tiene los defectos de abajo, que el verificador `x8` no detectaba. Tu trabajo: corregirlos,
completar lo que falta y **endurecer `x8`** para que los detecte.

## Notas de entorno (OBLIGATORIAS)

- **NUNCA uses `cd`, `cd /d` ni rutas absolutas en la terminal** (el sandbox las rechaza y aborta toda la
  ejecución). Usa rutas relativas e intérprete `..\..\..\.venv\Scripts\python.exe`.
- Archivos SOLO con las herramientas `write` y `edit`. NUNCA desde la terminal (nada de `cat <<`,
  here-strings, `Set-Content`, `python -c` que escriba archivos).
- PowerShell 5.1, sin `&&` (usa `;`). Solo ASCII en los `print`. `timeout=1800000` en la shell.
  **NO ejecutes `pytest`.** El libro no debe estar abierto en Excel.

## Restricciones

- NO modificar `src/`, `app.py`, `ui_*.py`, `scripts/barrido_final/comun.py`, los CSV de `resultados/` ni
  otros libros. Cada `.py`: máximo 200 líneas (divide en módulos nuevos si hace falta).
- No cambies las hojas de datos (`E{n} Datos …`): están bien.
- Reglas de formato vigentes: gráficos nativos con datos visibles junto a su tabla, cuadrícula, sin freeze
  panes, español, unidades, terminología «KALINA (total) / dentro / fuera del rango experimental»
  (sin «confiable», «fuera de rango», «sin respaldo», «no citable», «indicio», «extrapol»).
- Registra todo estudio en un único registro (`ESTUDIOS` de `x1_cargar.py`) y haz que las hojas E12 y E13
  y la síntesis lean de ese registro: más adelante se añadirán los estudios 12, 13 y 14 y deben entrar
  solos al reconstruir.

## Defectos a corregir (verificados por el director)

**D1. La tabla de clases por centro es global.** En las 12 hojas de resumen (`E0`…`E11`) la primera tabla
(«Centro | KALINA (total) | dentro | fuera | CORREGIBLE | NO_CONVERGIO | INVIABLE | Total») suma 4 911
puntos (todos los estudios juntos) y es idéntica en todas. Debe contar **solo los puntos del estudio de su
hoja**, y su columna Total debe sumar exactamente los puntos del estudio (11, 273, 542, 500, 343, 192, 98,
144, 360, 54, 279, 361). La fila con centro vacío se rotula «Sin centro (muestreo o malla)».

**D2. S1 de `Conclusion consolidada` tiene la columna Total mal.** Suma KALINA (total) + dentro + fuera +
las otras clases (cuenta dos veces). Total = KALINA (total) + CORREGIBLE + NO_CONVERGIO + INVIABLE, igual
a los puntos del estudio (estudio 1 debe dar 273, no 459). Revisa que el gráfico de S1 use las 4 clases
sin duplicar KALINA.

**D3. Tablas por variable y por par sin etiqueta de centro y sin el punto base.**
- En `E1` y `E10`, las dos tablas «Variable barrida | KALINA (total)…» no dicen a qué centro
  corresponden (la primera es C1 / C3, la segunda C2 / C4). Añade un título sobre cada tabla.
- Cuenta el **punto base dentro del barrido de cada variable** (el base de un centro es un punto de
  todos sus barridos) y deja de mostrarlo como fila aparte: por ejemplo ε_cond en C1 debe dar 1 KALINA
  (el base, ε_cond = 0.95), no 0; ε_cond en C4 debe dar 1.
- En `E2` y `E11`, las tablas por par deben incluir también el punto base (C1 B4 = 3 de 49; C3 B4 = 8 de
  49; C4 B4 = 5 de 49), para que coincidan con las conclusiones escritas.
- En `E1` y `E10`, la tabla de ventanas «Variable | Unidad | Centro | Valor mínimo | medio | máximo | n»
  hoy usa todos los KALINA del centro; debe usar **solo los puntos del barrido de esa variable (más el
  base)**. Así «n» es el número de valores de la variable con KALINA.

**D4. Faltan S2, S3 y S4 en `Conclusion consolidada`** (solo existen S1 y S5). Añádelas, cada una con título,
encabezado de condiciones y gráfico nativo al lado cuando tenga sentido:
- **S2. Ventanas KALINA por variable y centro** (C1, C2 del estudio 1; C3, C4 del estudio 10): por cada
  variable y centro, valor mínimo y máximo con KALINA (barrido propio más el base) y n de valores; tabla
  4 centros × 10 variables.
- **S3. Fronteras**: (a) P_baja mínima con KALINA por ε_cond × T_sumidero (estudio 5) y (b) por T_fuente ×
  T_sumidero (estudio 8). Pueden ser los mismos valores de `E5` y `E8` copiados con referencia al origen.
- **S4. Rangos de equipos por kg/s de caudal**, por estudio y centro, entre los KALINA (total): mínimo,
  mediana y máximo de Δh de turbina (kJ/kg), Wnet (kW por kg/s), Qi, Qreg, Qout (kW por kg/s), Qreg/Qi y
  r_P = P_alta/P_baja. Con un gráfico de barras de la mediana de Wnet por estudio.

## Hojas nuevas (con los datos que ya existen)

**`E12 Regenerador y turbina`** — responde al pedido del profesor «ver el comportamiento del regenerador
y del ciclo». Tablas y gráficos nativos junto a cada una:
1. **Regenerador frente a ε_reg** (barrido de una variable de los 4 centros: estudios 1 y 10): por cada
   valor de ε_reg (0.40–0.95): Qreg (kW por kg/s), Qreg/Qi, η (%) y la clase, una columna por centro; con
   gráfico de líneas de Qreg/Qi y otro de η frente a ε_reg (4 líneas).
2. **Turbina frente a η_t** (mismos estudios): Δh de turbina (kJ/kg), Wnet (kW por kg/s) y η (%) por
   valor de η_t, por centro; con gráfico de líneas de Wnet y de η.
3. **Turbina frente al cociente de presiones r_P = P_alta/P_baja**: sobre **todos** los KALINA (total) de
   todos los estudios, agrupa r_P en bandas (1–2, 2–3, …, 8–9, > 9) y da n, mínimo/mediana/máximo de Δh de
   turbina y de Wnet por kg/s, y η mediana; gráfico de barras de la mediana de Δh por banda. Rotula que
   r_P grande sin salto de presión útil (p. ej. P_alta 1000 kPa) da η de ~0.4 % (puntos triviales).

**`E13 Preseleccion de equipos`** — responde «con un diferencial de presión podría subirnos tal turbina,
nos serviría tal regenerador, un condensador con esta efectividad nos sirve»:
1. **Diseños de referencia**: los 5 KALINA de mayor η de cada uno de los 4 centros (de todos los estudios
   del centro) con sus 10 variables de entrada, η (%), Δh de turbina, r_P, Qreg/Qi, y por kg/s: Wnet, Qi,
   Qreg, Qout, y los caudales internos m_v y m_l (kg/s por kg/s de m_b); y si están dentro o fuera del
   rango experimental.
2. **Escalado con el caudal**: para los 4 mejores diseños (uno por centro), Wnet, Qi, Qreg y Qout para
   m_b = 1, 5, 10, 15 y 20 kg/s (multiplicación exacta; la Fase 0 comprobó que η y la clase no cambian con
   m_b). Gráfico de barras agrupadas de Wnet por m_b.
3. **Efectividad mínima por equipo** (mínimos con KALINA, de los estudios de una variable y de pares):
   ε_cond mínima que sirve por centro y a qué P_baja (estudios 5 y 8), ε_reg y ε_HRVG mínimas con KALINA y
   η_t mínima con KALINA, por centro.

## Verificación (endurece `x8_verificar.py`; añade los controles nuevos, no quites los anteriores)

8. En cada hoja `E0`…`E11` de resumen, la tabla de clases por centro suma los puntos del estudio y cada
   fila coincide con el recuento desde los CSV.
9. S1: columna Total = suma de las 4 clases = puntos del estudio.
10. Existen S2, S3 y S4 con las filas indicadas y valores numéricos; S2 tiene 40 filas (10 variables × 4
    centros).
11. Las tablas por variable de E1/E10 y las de pares de E2/E11 incluyen el base y tienen título con el
    centro; comprobar: ε_cond C1 = 1, ε_cond C4 = 1, B4 C1 = 3, B4 C3 = 8, B4 C4 = 5.
12. Existen `E12` y `E13` con ≥ 6 gráficos nuevos en total, cada uno con ≥ 1 serie con valores numéricos.
13. Que el libro tenga ≥ 26 gráficos en total (20 anteriores + los nuevos) y sin solapes.
Todos los controles anteriores (1–7) siguen en OK.

## Ejecución

```
..\..\..\.venv\Scripts\python.exe scripts\sens1\x7_construir.py
..\..\..\.venv\Scripts\python.exe scripts\sens1\x8_verificar.py
```

No des `done` con algún control en FALLA. Reporte en el formato de `AGENTS.md`; en RESULTS: salida completa de
`x8_verificar.py` (sin la lista larga de gráficos) y el nº de hojas y de gráficos.
