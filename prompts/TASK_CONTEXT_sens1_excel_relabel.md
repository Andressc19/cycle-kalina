# TASK_CONTEXT — Excel Sensibilidad 1: terminología neutra («rango experimental») y reconstrucción

**Fecha:** 2026-10-16 · **Rama:** `test/anal_terremoto`
**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\sens-1` (worktree).
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`
**Contexto:** el libro `datos/Kalina_anal_sensible_1.xlsx` ya existe y pasa `x8_verificar.py`, pero fue
construido con una redacción que el usuario rechazó: llamar «confiables» a unos KALINA y «fuera de rango
del motor» o «sin respaldo experimental» a otros es una **discriminación indebida**. Los puntos que superan
el rango experimental de la ecuación son resultados válidos del modelo. Esta tarea **solo cambia la
redacción y reconstruye el libro**; los datos y los cálculos no cambian.

## Notas de entorno (OBLIGATORIAS)

- Archivos SOLO con las herramientas `write` y `edit`. NUNCA desde la terminal (nada de `cat <<`,
  here-strings, `Set-Content`, `python -c` que escriba archivos).
- Terminal = Windows PowerShell 5.1, solo para EJECUTAR. Sin `&&` (usa `;`). Solo ASCII en los `print`.
- `timeout=1800000` en la shell. **NO ejecutes `pytest`.** El libro no debe estar abierto en Excel.

## Restricciones

- NO modificar `src/`, `app.py`, `ui_*.py`, `scripts/barrido_final/comun.py`, los CSV de `resultados/` ni
  otros libros Excel. Cada `.py`: máximo 200 líneas.
- No cambies cifras ni cálculos: el verificador `x8_verificar.py` debe seguir en OK (filas y conteos por
  clase iguales). Los nombres internos de columnas del DataFrame y de los CSV (`fuera_rango`,
  `kalina_confiable`) **pueden quedarse**; lo que cambia es **todo texto visible del libro**.

## Terminología nueva (la única permitida en el libro)

| Antes (prohibido en el libro) | Ahora |
|---|---|
| KALINA confiable(s) / confiables | **KALINA dentro del rango experimental** |
| KALINA fuera de rango (del motor) / sin respaldo experimental | **KALINA fuera del rango experimental (líquido > 420 K)** |
| «no citable», «indicio(s)», «extrapolación del motor», «el motor extrapola», «no son fiables» | (se eliminan; ver texto explicativo abajo) |
| Columna «Fuera de rango del motor (sí/no)» | **«Fuera del rango experimental (sí/no)»** |
| Columna «KALINA confiable (sí/no)» | **«KALINA dentro del rango experimental (sí/no)»** |
| En tablas resumen y gráficos | tres cifras lado a lado: **KALINA (total)**, **de ellos dentro del rango experimental**, **de ellos fuera del rango experimental** |

La cifra principal de toda tabla y de toda conclusión es **KALINA (total)**; las otras dos son detalle.
Los puntos fuera del rango experimental **forman parte de los resultados y de las conclusiones** (no se
tratan aparte ni se descartan). Busca y reemplaza en `x1_cargar.py`, `x2_formato.py`, `x3_hojas_datos.py`,
`x4_resumenes.py`, `x5_graficos.py` (nombres de series), `x6_sintesis.py`, `x7_construir.py`,
`x8_verificar.py` y `conclusiones.py`. Después de reconstruir, **recorre todas las celdas del libro** y
confirma que ninguna contiene «confiable», «fuera de rango», «sin respaldo», «no citable», «indicio» ni
«extrapol» (ignora los nombres de columna del CSV `fuera_rango`, que no se escriben en celdas de texto de
las hojas de resumen). Agrega esa comprobación como control 7 de `x8_verificar.py`.

## Texto explicativo (añádelo en `LEEME` como sección «¿Qué es el rango experimental?»)

> La ecuación del motor (IAPWS G4-01, §6) fue contrastada con datos experimentales de líquido hasta 420 K
> y de vapor hasta 10 MPa. Un punto queda «fuera del rango experimental» cuando alguno de sus estados de
> líquido o bifásico supera 420 K (en esta campaña, T2 o T5; ocurre desde unos 150 °C de fuente). El motor
> lo calcula y lo clasifica igual, y la guía declara la ecuación válida hasta el lugar crítico; la marca
> solo informa que en esa zona no hay datos experimentales con que contrastar el cálculo. Estos puntos
> forman parte de los resultados y de las conclusiones. El lugar crítico no se vigila en el motor (la guía
> advierte que su ubicación es incierta); con P_alta ≤ 5 MPa en esta campaña no se espera cruzarlo, pero no
> se comprobó punto por punto.

Debajo, una **tabla por banda de T_fuente** calculada desde los datos: nº de KALINA, nº fuera del rango
experimental y porcentaje (bandas °C: 60–120, 120–130, 130–140, 140–150, 150–160, 160–170, 170–180,
180–200, 200–250, 250–300). Valores esperados (verifica): 0, 0, 0, ~1, ~31, ~76, ~93, ~97, ~98, 100 %.
Cifra global a verificar: 275 de 1 753 KALINA (estudios 1–11, sin el estudio 0) están fuera del rango
experimental.

## Conclusiones: reescribe estos textos (en `conclusiones.py`)

- **Apéndice B, punto 1:** «Hay KALINA en todo el rango de fuente de 70 a 300 °C. Hasta ~150 °C todos están
  dentro del rango experimental de la ecuación; entre 150 y 170 °C una parte (≈31–76 %) queda fuera de él, y
  por encima de 170 °C casi todos (≈93–100 %). Los resultados fuera del rango experimental forman parte de
  las conclusiones.»
- **Estudio 4:** sustituye «A 70 °C aparece el primer KALINA confiable…» por «A 70 °C aparece el primer
  KALINA (2 puntos…)» y la frase sobre «170 °C» por la de arriba. Donde el texto diga «η máxima confiable
  13.6 % a 150 °C», escribe «η máxima entre los KALINA dentro del rango experimental: 13.6 % a 150 °C» y
  **añade** «η máxima entre todos los KALINA de este estudio: X % a Y °C», con X e Y **calculados desde los
  datos** (no inventes: tómalos del DataFrame al construir el texto).
- **Estudios 5, 6, 7, 8, 10, 11 y consolidada (puntos 5 y 6):** donde se cite una η máxima «confiable»
  (13.1, 14.4, 13.2, 10.5 %…), reescribe como «η máxima entre los KALINA dentro del rango experimental» y
  añade a cada una la η máxima entre todos los KALINA del estudio, calculada desde los datos.
- Quita toda alusión a «unos pocos confiables», «solo X confiables» o «ninguno confiable»: di «dentro del
  rango experimental» / «fuera del rango experimental».
- Mantén todas las demás cifras.

## Pasos

1. Aplica el reemplazo de terminología en los módulos y reescribe `conclusiones.py`.
2. Añade la sección y la tabla de bandas en `LEEME` (módulo `x7_construir.py` o `x4_resumenes.py`, el que
   corresponda; respeta el límite de 200 líneas, divide si hace falta).
3. Reconstruye y verifica:

```
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\sens1\x7_construir.py
D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe scripts\sens1\x8_verificar.py
```

4. **No des `done` si algún control está en FALLA.** Reporta en formato `AGENTS.md`; en RESULTS: salida
   completa de `x8_verificar.py`, el nº de celdas del libro con términos prohibidos (debe ser 0) y la tabla
   por banda de T_fuente tal como salió.
