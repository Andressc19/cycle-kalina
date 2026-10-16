# TASK_CONTEXT — Excel Sensibilidad 1: contar los KALINA de E2 y E11 por pertenencia a la malla de cada par

**Fecha:** 2026-10-16 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree).
**Intérprete (ruta relativa desde aquí):** `..\..\..\.venv\Scripts\python.exe`

## Notas de entorno (OBLIGATORIAS)

- **NUNCA uses `cd`, `cd ..`, `cd /d` ni rutas absolutas en la terminal** (el sandbox las rechaza y aborta toda
  la ejecución). Usa rutas relativas e intérprete `..\..\..\.venv\Scripts\python.exe`.
- Archivos SOLO con las herramientas `write` y `edit`. NUNCA desde la terminal (nada de `cat <<`, here-strings,
  `Set-Content`, `python -c` que escriba archivos).
- PowerShell 5.1, sin `&&` (usa `;`). Solo ASCII en los `print`. `timeout=1800000`. **NO ejecutes `pytest`.**
  El libro no debe estar abierto en Excel.

## Restricciones

- NO modificar `src/`, `app.py`, `ui_*.py`, `scripts/barrido_final/comun.py`, ningún CSV de `resultados/` ni otros
  libros. Cada `.py`: máximo 200 líneas. Mantén formato y terminología vigentes. **No cambies lo que ya está bien**
  (las hojas de datos, E15, E13, E14, E16 y la síntesis ya están verificadas por el director).

## Problema (verificado por el director)

En `E2 Pares` (centros C1 y C2) y `E11 Centros nuevos pares` (C3 y C4), la tabla «KALINA por par» cuenta los
puntos cuya **etiqueta** `par` es ese par (más el base). Pero las mallas de los pares comparten líneas
(p. ej. el punto base, las líneas de P_baja o de T_fuente), y el CSV asigna cada punto compartido solo al primer
par que lo generó. Resultado: se subcuenta. Ejemplos (hoja frente a la malla completa de 49 celdas):
`E2 B2 C1` 38 frente a **43**; `E2 B2 C2` 17 frente a **23**; `E2 B3 C1` 36 frente a **41**; `E2 B3 C2` 35 frente a
**41**; `E2 B6 C1` 40 frente a **46**; `E2 B6 C2` 34 frente a **39**; `E11 B1 C3` 41 frente a **40** (el base
etiquetado en B1 se contaba de más), `E11 B1 C4` 26 frente a **25**; `E11 B2 C3` 31 frente a **36**; `E11 B2 C4`
35 frente a **39**; `E11 B3 C3` 35 frente a **40** (de 48 celdas: se descartó una combinación con
P_alta < 1.3 × P_baja); `E11 B3 C4` 30 frente a **34**. Los demás (E2 B1, B4, B5; E11 B4; E15 todos) ya están bien.

## Corrección

Cuenta los KALINA de cada par **por pertenencia a su malla**, no por etiqueta: un punto del centro `c`
pertenece a la malla del par (variable a, variable b) si todas las variables **distintas de a y b** valen
exactamente lo del centro (redondeo a 2 decimales) y a y b toman los valores de la rejilla de ese par. Centros:

| Centro | T_fuente | T_sumidero | P_alta | P_baja | x_b | η_t | η_p | ε_HRVG | ε_reg | ε_cond |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 | 394.15 | 278.15 | 3300 | 690 | 0.82 | 0.85 | 0.80 | 0.85 | 0.75 | 0.95 |
| C2 | 403.0 | 300.15 | 3000 | 563.64 | 0.50 | 0.85 | 0.75 | 0.85 | 0.75 | 0.95 |
| C3 | 423.15 | 280.5 | 3150 | 950 | 0.75 | 0.85 | 0.80 | 0.85 | 0.75 | 0.95 |
| C4 | 383.15 | 282.5 | 3880 | 910 | 0.88 | 0.85 | 0.80 | 0.85 | 0.75 | 0.95 |

Pares: B1 T_fuente × P_baja; B2 P_baja × x_b; B3 P_alta × P_baja; B4 ε_cond × T_sumidero; B5 ε_reg × η_t;
B6 ε_HRVG × T_fuente. Ya existe lógica de reconstrucción por malla en `scripts/sens1/faseB_reporte.py` /
`faseB_reporte2.py` (Fase B) y en las matrices de `E15`: reutilízala. Aplica la nueva cuenta a:
1. la tabla «KALINA por par» de `E2` y de `E11` (y cualquier otra cifra por par de esas hojas: η mínima y máxima,
   mejor punto, si las hay);
2. los gráficos de esas hojas (que leen esas tablas);
3. los textos de `conclusiones.py` que citen cifras por par de E2 y E11 (compruébalo; las cifras «C1 3 de 49»,
   «C2 33 de 49», «C3 8 de 49», «C4 5 de 49» del par B4 ya son correctas).

Valores esperados completos (verifícalos contra los datos): E2 → C1 B1 39, B2 43, B3 41, B4 3, B5 49, B6 46;
C2 B1 35, B2 23, B3 41, B4 33, B5 49, B6 39 (calcula y reporta cualquier diferencia). E11 → C3 B1 40, B2 36,
B3 40, B4 8; C4 B1 25, B2 39, B3 34, B4 5.

## Verificación (amplía `x8_verificar.py`; no quites los controles anteriores)

26. En `E2` y `E11`, todas las cifras de KALINA por par y centro coinciden con el recuento por pertenencia a la
    malla (los valores esperados de arriba), no solo B4.
27. Los gráficos de `E2` y `E11` leen esas cifras y tienen series numéricas.
Los controles 1–25 siguen en OK (43 gráficos, sin solapes).

## Ejecución

```
..\..\..\.venv\Scripts\python.exe scripts\sens1\x7_construir.py
..\..\..\.venv\Scripts\python.exe scripts\sens1\x8_verificar.py
```

No des `done` con algún control en FALLA. Reporte en el formato de `AGENTS.md`; en RESULTS: la tabla de KALINA por
par y centro de E2 y E11 tal como quedó en el libro, y la salida de `x8_verificar.py` (sin la lista de gráficos).
