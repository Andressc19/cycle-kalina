# FICHA KF-M03 — Sensibilidad local alrededor de A\* (ficha piloto)

> Ficha piloto para validar el formato. Las cifras vienen de `resultados/2026-10-06_final_M3/REPORTE_M3.md`
> (incluida la nota del director del 2026-10-06). El agente A4 las vuelve a calcular desde
> `m3_ofat.csv`; hasta entonces van marcadas como **pendientes de validación cruzada**.

> **Antes de leer: qué son el punto del profesor y el punto ancla A\***
>
> - **Punto del profesor (PP):** los datos del enunciado. P_alta = 3000 kPa, P_baja = 400 kPa,
>   x_b = 0.50, T_fuente = 623.15 K, T_sumidero = 300.03 K, η_t = 0.85, η_p = 0.75,
>   ε_HRVG = 0.85, ε_reg = 0.75, ε_cond = 0.80. **Con estos datos el ciclo no converge:** M1 lo
>   confirmó 41 de 41 veces.
> - **Punto ancla A\* ("A estrella"):** es el punto del profesor con **solo dos cambios**:
>   T_fuente baja de 623.15 K a **403 K** y P_baja sube de 400 kPa a **563.64 kPa**. Todo lo demás
>   queda igual. Con eso el ciclo **sí funciona y es KALINA** (η = 8.48 %).
> - **De dónde sale:** en M2 se buscó el menor cambio posible sobre los datos del profesor que
>   produjera un KALINA. Aparecieron varias opciones y se eligió la intermedia, entre la de mayor
>   eficiencia (420 K) y la más parecida al profesor (390 K). A esa opción se le llamó A\*.
> - **Para qué se usa:** como no se puede estudiar la sensibilidad alrededor del punto del profesor
>   (porque ahí no converge), M3 la estudia alrededor de A\*, que es el punto funcional más cercano
>   al enunciado.

### ID del caso:
`KF-M03` · bloque **B06** (todo fijo en A\*, piso de O2 = 300.03 K) · familia **L** (sensibilidad local) ·
diseño **OAT** · fecha 2026-10-06 · commit `ef30e9f`.
Los resultados de esta ficha **no se comparan punto a punto** con los de M4 en adelante, porque esos
barridos tienen otros datos fijos y otra regla para el piso de O2.

### Nombre del caso:
Sensibilidad local, una variable a la vez, alrededor del punto ancla A\* (el punto del profesor con
T_fuente = 403 K y P_baja = 563.64 kPa).

### Objetivo del barrido:
Saber qué variables mueven más la eficiencia η y la clase del ciclo cerca de A\*, y a qué distancia
está cada frontera de clase. De ahí sale un ranking de qué dato conviene cuidar más.

### ¿Qué se barrió?
Las 10 variables de entrada, de a una, con las otras nueve fijas en A\*.

### ¿Por qué se barrió?
- Con los datos del profesor (T_fuente 623 K) el ciclo no converge. Por eso el análisis local se hace
  alrededor de un punto que sí es KALINA (A\*, elegido en M2), y no alrededor del punto del profesor.
- El protocolo (METODOLOGIA_BARRIDOS_FINAL §M3) pide un ranking local antes del análisis global (M4).

### Datos o variables barridas:

| Variable | Rango [a, b] | n valores | Paso | Unidad |
|---|---|---|---|---|
| T_fuente | 340 – 623.15 | 15 | 20.22 | K |
| T_sumidero | 283.15 – 303.55 | 15 | 1.457 | K |
| P_alta | 1000 – 10000 | 15 | 642.9 | kPa |
| P_baja | 150 – 1500 | 15 | 96.43 | kPa |
| x_b | 0.30 – 0.90 | 15 | 0.0429 | – |
| η_t, η_p, ε_HRVG, ε_reg, ε_cond | 0.40 – 0.95 | 15 c/u | 0.0393 | – |

Además, A\* ± h con h = 1 % del rango, para la elasticidad (20 corridas), y el ancla sola (1).
**Total: 171 corridas** (motor teqp, 5 procesos, 5822 s; mediana de 153 s por punto).

### Datos modificados:

| Variable | Profesor (PP) | A\* (base de M3) |
|---|---|---|
| T_fuente | 623.15 K | **403.0 K** |
| P_baja | 400 kPa | **563.64 kPa** |
| P_alta, x_b, T_sumidero, η_t, η_p, ε (×3), m_b | — | igual que el profesor |
| Piso de O2 (`T_amb_diseno`) | 300.032917 K | 300.032917 K (fijo; en M3 todavía no sigue a T_sumidero) |
| Rango de η/ε | — | [0.40, 0.95] |

### Métodos aplicados:
- OAT con 15 puntos equiespaciados por variable (MATEMATICA §5).
- Elasticidad local E = (Δη/η)/(Δv/v) en A\*, por diferencia central con ±1 % del rango.
- Δη = η máx. − η mín. sobre la malla. **Se usa la versión del director: solo con puntos genuinos y W_net > 0.**
- Las fronteras se interpolan linealmente entre los vecinos donde un margen (m_O1, m_O2, m_O5) cambia de signo.
- Zona KALINA = el tramo contiguo a A\* en el que la clase sigue siendo KALINA.
- Punto genuino = KALINA, CORREGIBLE o INVIABLE. N2 no cuenta.

### Resultados obtenidos:

**Conteo:** 171 corridas, 148 genuinas y 86 KALINA; 8 fuera de rango (líquido por encima de 420 K).
*(pendiente de validación cruzada)*

**Ranking local (TAB-M03-02).** El conteo por clase es TAB-M03-01 y las condiciones son TAB-M03-00:
las tablas de "Datos barridos" y "Datos modificados" de esta ficha.

| Variable | E en A\* | Δη [pp] (W_net>0) | η KALINA máx. en la malla | Falla al bajar | Falla al subir | Distancia a la frontera O2 (fracción del rango) |
|---|---|---|---|---|---|---|
| T_fuente | 10.871 | 3.67 | 7.90 % (400.7 K) | NO_CONVERGIO | O2 | 0.024 |
| x_b | 3.402 | 10.78 | 6.42 % (0.471) | O3 | O2 | 0.018 |
| T_sumidero | 1.614 | 0.85 | 8.44 % (299.2 K) | — | O2 | 0.022 |
| P_alta | −1.165 | 5.14 | 4.66 % (3571 kPa) | O2 | NO_CONVERGIO | **0.007** |
| η_t | 1.146 | 6.32 | 9.62 % (0.95) | O2 | — | 0.343 |
| ε_reg | 0.860 | 4.99 | **10.96 % (0.95)** | O2 | — | 0.057 |
| ε_HRVG | 0.644 | 6.69 | 8.36 % (0.832) | — | O2 | 0.039 |
| P_baja | −0.581 | 6.80 | 7.91 % (632 kPa) | O2 | — | 0.016 |
| ε_cond | −0.406 | 0.82 | 8.35 % (0.832) | O2 | — | 0.012 |
| η_p | 0.149 | 1.38 | 8.75 % (0.95) | — | — | n/a |

*Tabla TAB-M03-02. Ranking local de las 10 variables alrededor de A\*. Caso KF-M03 (bloque B06).
Datos fijos: los de A\* (ver "Datos modificados") salvo la variable de la fila. Filtro: puntos genuinos;
Δη solo con trabajo neto > 0. n = 171 corridas. Fuente: `m3_resumen.csv`, `m3_cruces.csv` y la nota
del director del REPORTE_M3 §11.*

**Figuras del caso** (las genera A3 con las reglas del §3A.4; estos son sus pies):

- *Figura FIG-M03-01. Cuánto varía η al recorrer el rango completo de cada variable, con las demás
  fijas en A\* (tornado). Caso KF-M03 (bloque B06). Datos fijos: T_fuente = 403.0 K; P_baja =
  563.6 kPa; P_alta = 3000 kPa; x_b = 0.50; T_sumidero = 300.03 K; η_t = 0.85; η_p = 0.75;
  ε_HRVG = 0.85; ε_reg = 0.75; ε_cond = 0.80; piso de O2 = 300.03 K; motor teqp. Cada barra mueve
  solo su variable (15 valores). Filtro: genuinos con W_net > 0. Fuente: `m3_ofat.csv`.*
- *Figura FIG-M03-02. Elasticidad local de η en A\*, con un empuje de ±1 % del rango de cada
  variable. Mismos datos fijos que FIG-M03-01. n = 20 corridas vecinas + el ancla.*
- *Figura FIG-M03-03. η contra cada variable, un panel por variable y cada eje en sus unidades.
  Color por clase; × = no convergido o N2; línea punteada = valor en A\*. Mismos datos fijos.*
- *Figura FIG-M03-04. Distancia entre A\* y cada frontera de clase, medida como fracción del rango
  de la variable (0 = justo en A\*). Mismos datos fijos. Fuente: `m3_cruces.csv`.*

Las cuatro figuras ya están rehechas con estas reglas en `analisis_final/03_figuras/M03/` (el tornado
usa el Δη con W_net > 0).

### Conclusiones del caso:
1. **A\* está al filo de O2.** En 8 de las 9 variables con frontera medida, O2 está a menos del 6 % del
   rango. El caso más crítico es P_alta: bajarla 64 kPa (de 3000 a 2936 kPa) ya rompe O2.
2. **La variable más sensible cerca del ancla es T_fuente** (|E| ≈ 10.9), seguida por x_b (3.4).
   Son las que mueven T2 y el punto de rocío: el lado caliente.
3. **Las palancas que suben η sin perder KALINA son ε_reg y η_t.** Con 0.95 en cada una, η sube hasta
   10.96 % y 9.62 %, respectivamente, contra 8.48 % en A\*.
4. **x_b y P_alta** mueven mucho η, pero casi toda su malla cae fuera de KALINA (por O2 o O3). Para
   esas dos variables, A\* está en un pasillo angosto.
5. Fuera de la zona KALINA, el criterio que bloquea es siempre **O2** (cavitación). Eso confirma la
   regla del proyecto de cerrar O2 con P_baja.

### Advertencias, supuestos y limitaciones:
- **OAT no ve interacciones**: si dos variables se compensan, aquí no aparece. Para eso está M4.
- **Banda de η ±0.4–0.7 pp**: las diferencias de Δη entre T_sumidero (0.85), ε_cond (0.82) y η_p (1.38)
  no son concluyentes entre sí.
- El Δη original del REPORTE (50.7 pp para P_baja y 46.2 pp para x_b) incluye puntos INVIABLE con
  W_net ≤ 0. **No usarlo.**
- En M3 el piso de O2 es 300.03 K fijo. Desde M2S sigue a T_sumidero. Por eso la frontera O2 de
  T_sumidero no se puede comparar directamente con la de M4 en adelante.
- 8 puntos quedan fuera del rango confiable de G4-01: sus η se toman con pinzas.
- La malla tiene un paso de 1/14 del rango. Una zona KALINA más angosta que ese paso puede no verse
  (le pasa a T_fuente, x_b y P_alta, cuya zona medida es de un solo punto).
- M6 encontró que el motor real, con presupuesto de 300 s, marca A\* como NO_CONVERGIO. Con ~1500 s
  coincide con teqp. A\* es válido con teqp y con el motor real con presupuesto suficiente.
- [SUPUESTO] Los pasos de la tabla de variables barridas son (b − a)/14. Coinciden con "15 valores
  equiespaciados" del REPORTE; A4 los confirma contra el CSV.

### Recomendaciones:
- Para el diseño, no tomar A\* tal cual: conviene alejarse de O2 subiendo P_baja unos 70 kPa (zona
  KALINA de P_baja desde 632 kPa en la malla) o subir ε_reg.
- Usar el ranking |E| solo como lectura local. Para decidir rangos, usar el RSA de M4/M4b.
- Rehacer FIG-M03-01 con el Δη filtrado (W_net > 0) y agregar FIG-M03-04 (distancia a la frontera).

**Fuentes:** `resultados/2026-10-06_final_M3/REPORTE_M3.md` (§3, §5, §8, §9, §11), `m3_ofat.csv`,
`m3_resumen.csv`, `m3_cruces.csv`, hojas `M3_ofat`, `M3_resumen` y `M3_cruces` del Excel, commit `ef30e9f`,
`resultados/2026-10-08_final_M6/REPORTE_M6.md` (parte A).
