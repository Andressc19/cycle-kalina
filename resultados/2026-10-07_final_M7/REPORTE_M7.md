# REPORTE M7 — La máxima η dentro de la región KALINA

Campaña final · rama `test/barrido_final` · motor **teqp** · salidas en `resultados/2026-10-07_final_M7/`
(m7_evaluaciones.csv, m7_trayectorias.csv, m7_optimos.csv, m7_convergencia.png).

## 1. La pregunta

Ya tenemos acotada la región KALINA (M4b, M5, M5c). Dentro de esa región ya determinada,
**¿cuál es la máxima η alcanzable?**

1. Sin restricciones adicionales.
2. Conservando datos del profesor: con sus temperaturas (S1), con sus presiones (S2/S3) y con
   su fuente + x_b (S5).

## 2. El método, en simple

Búsqueda por patrones (MATEMATICA §7.2) con **objetivo lexicográfico**: minimizar `(D, −η)` —
primero llegar a D = 0 (KALINA genuino) y, entre los KALINA, maximizar η. Un punto no
genuino (p. ej. N2) nunca gana una comparación.

- **5 arranques** (A1 a A5), corren en secuencia; cada uno arranca de un punto existente y
  conserva las variables fijas de la tabla §3. Ninguna arranca de cero.
- Cada variable libre se normaliza a `u = (v − a)/(b − a)` dentro de su caja:
  T_fuente 380–500 K, T_sumidero 278.15–303.55 K, P_alta 2000–5000 kPa, P_baja 300–2500 kPa,
  x_b 0.50–0.85, y η_t, η_p, ε_HRVG, ε_reg, ε_cond en 0.40–0.95.
- Por iteración: candidatos `u ± 0.10·e_i` recortados a [0, 1], **todos evaluados en paralelo**
  (pool de 7), y se acepta el de menor (D, −η). Si alguien mejora, se mantiene el paso; si
  nadie mejora, el paso se divide entre 2. Corte a `paso < 0.01` o a 120 evaluaciones por
  arranque.
- Un candidato con `P_baja ≥ P_alta − 300 kPa` se descarta sin evaluarse.
- Piso de O2 de cada punto = su propia T_sumidero (`t_amb_diseno = combo["T_sumidero"]`).
- Solo motor teqp, un punto por evaluación, con presupuesto de 300 s.

## 3. Tabla de óptimos

=== §3 tabla de óptimos ===
| Arranque | Qué conserva del profesor | η inicial | η óptima | P_alta (kPa) | P_baja (kPa) | dP (kPa) | rP | T_fuente (K) | T_sumidero (K) | x_b | η_t | η_p | ε_HRVG | ε_reg | ε_cond |
|---||---||---||---||---||---||---||---||---||---||---||---||---||---||---||---|
| A1 | nada (libre total; parte del mejor KALINA de M4b) | 0.1230 | 0.1498 | 4381.8 | 808.3 | 3573.5 | 5.421 | 436.10 | 279.10 | 0.7047 | 0.950 | 0.746 | 0.678 | 0.942 | 0.842 |
| A2 | nada (libre total; parte del mejor KALINA de M2S, B2 a 278.15 K) | 0.1191 | 0.1548 | 3000.0 | 393.8 | 2606.2 | 7.619 | 420.00 | 278.15 | 0.5000 | 0.950 | 0.750 | 0.850 | 0.950 | 0.800 |
| A3 | sus temperaturas: T_fuente 623.15 K y T_sumidero 300.032917 K | 0.0929 | 0.1274 | 5000.0 | 1359.6 | 3640.4 | 3.678 | 623.15 | 300.03 | 0.8500 | 0.946 | 0.838 | 0.496 | 0.917 | 0.946 |
| A4 | sus presiones: P_alta 3000 kPa, P_baja 400 kPa, más T_sumidero | 0.0950 | 0.1560 | 3000.0 | 400.0 | 2600.0 | 7.500 | 415.00 | 300.03 | 0.5000 | 0.950 | 0.805 | 0.950 | 0.950 | 0.950 |
| A5 | su fuente y su x_b: T_fuente 623.15 K y x_b 0.50 | 0.0846 | 0.1109 | 4808.3 | 1022.3 | 3786.1 | 4.704 | 623.15 | 302.58 | 0.5000 | 0.922 | 0.576 | 0.462 | 0.685 | 0.878 |

Cada fila es el último punto aceptado de su arranque (`m7_optimos.csv`). Los cinco óptimos
son **KALINA con D = 0**, todos con verificación B verdadera (`B_verificado = True`). El
mejor W_net y la mejor η no van de la mano: A4 tiene la mayor η (0.1560) con el menor W_net
(71.38 kW), mientras que A3 tiene el mayor W_net (129.39 kW) con η = 0.1274.

## 4. Hacia dónde empuja el optimizador

=== §4 empuje de cada variable ===
| Arranque | Variable | Inicial | Óptimo | Dónde queda |
|---|---|---|---|---|
| A1 | T_fuente | 436.097 | 436.097 | dentro de la caja |
| A1 | T_sumidero | 279.098 | 279.098 | dentro de la caja |
| A1 | P_alta | 3481.82 | 4381.82 | dentro de la caja |
| A1 | P_baja | 808.34 | 808.34 | dentro de la caja |
| A1 | x_b | 0.634749 | 0.704749 | dentro de la caja |
| A1 | eta_t | 0.918483 | 0.95 | borde superior |
| A1 | eta_p | 0.746081 | 0.746081 | dentro de la caja |
| A1 | eps_hrvg | 0.677731 | 0.677731 | dentro de la caja |
| A1 | eps_reg | 0.94153 | 0.94153 | dentro de la caja |
| A1 | eps_cond | 0.841826 | 0.841826 | dentro de la caja |
| A2 | T_fuente | 420 | 420 | dentro de la caja |
| A2 | T_sumidero | 278.15 | 278.15 | borde inferior |
| A2 | P_alta | 3000 | 3000 | dentro de la caja |
| A2 | P_baja | 393.75 | 393.75 | dentro de la caja |
| A2 | x_b | 0.5 | 0.5 | borde inferior |
| A2 | eta_t | 0.85 | 0.95 | borde superior |
| A2 | eta_p | 0.75 | 0.75 | dentro de la caja |
| A2 | eps_hrvg | 0.85 | 0.85 | dentro de la caja |
| A2 | eps_reg | 0.75 | 0.95 | borde superior |
| A2 | eps_cond | 0.8 | 0.8 | dentro de la caja |
| A3 | T_fuente | 623.15 | 623.15 | fija (no se mueve) |
| A3 | T_sumidero | 300.033 | 300.033 | fija (no se mueve) |
| A3 | P_alta | 3905.95 | 5000 | borde superior |
| A3 | P_baja | 1359.56 | 1359.56 | dentro de la caja |
| A3 | x_b | 0.829478 | 0.85 | borde superior |
| A3 | eta_t | 0.836056 | 0.946056 | borde superior |
| A3 | eta_p | 0.837534 | 0.837534 | dentro de la caja |
| A3 | eps_hrvg | 0.496366 | 0.496366 | dentro de la caja |
| A3 | eps_reg | 0.916678 | 0.916678 | dentro de la caja |
| A3 | eps_cond | 0.945788 | 0.945788 | borde superior |
| A4 | T_fuente | 403 | 415 | dentro de la caja |
| A4 | T_sumidero | 300.033 | 300.033 | fija (no se mueve) |
| A4 | P_alta | 3000 | 3000 | fija (no se mueve) |
| A4 | P_baja | 400 | 400 | fija (no se mueve) |
| A4 | x_b | 0.5 | 0.5 | borde inferior |
| A4 | eta_t | 0.85 | 0.95 | borde superior |
| A4 | eta_p | 0.75 | 0.805 | dentro de la caja |
| A4 | eps_hrvg | 0.85 | 0.95 | borde superior |
| A4 | eps_reg | 0.75 | 0.95 | borde superior |
| A4 | eps_cond | 0.95 | 0.95 | borde superior |
| A5 | T_fuente | 623.15 | 623.15 | fija (no se mueve) |
| A5 | T_sumidero | 302.581 | 302.581 | dentro de la caja |
| A5 | P_alta | 4808.34 | 4808.34 | dentro de la caja |
| A5 | P_baja | 1242.27 | 1022.27 | dentro de la caja |
| A5 | x_b | 0.5 | 0.5 | fija (no se mueve) |
| A5 | eta_t | 0.922492 | 0.922492 | dentro de la caja |
| A5 | eta_p | 0.576066 | 0.576066 | dentro de la caja |
| A5 | eps_hrvg | 0.407302 | 0.462302 | dentro de la caja |
| A5 | eps_reg | 0.410115 | 0.685115 | dentro de la caja |
| A5 | eps_cond | 0.878416 | 0.878416 | dentro de la caja |

En lenguano llano, hacia dónde empuja cada arranque:

- **η_t** es la estrella: se va al techo de la caja (0.95) en A1, A2 y A4, y queda a menos del
  1% del techo en A3 (0.9461). En A5 ni se mueve (0.9225).
- **P_alta** sube en A1 (3481.8 → 4381.8 kPa) y llega al techo de la caja en A3 (5000 kPa).
  En A2 y A5 no hace falta tocarla; en A4 está fija a 3000 kPa.
- **x_b** sube en A1 (0.6347 → 0.7047) y toca el techo 0.85 en A3. En A2 y A4 se queda en el
  piso 0.50; en A5 está fija a 0.50.
- **ε_reg** sube hasta el techo 0.95 en A2 y A4, y de 0.4101 a 0.6851 en A5. **ε_HRVG** sube
  hasta 0.95 en A4 y de 0.4073 a 0.4623 en A5.
- **T_fuente** solo se mueve en A4 (403 → 415 K); A1 y A2 no la tocan, A3 y A5 la tienen fija
  en 623.15 K.
- **P_baja** solo baja en A5 (1242.3 → 1022.3 kPa); en A4 está fija a 400 kPa y en el resto no
  conviene moverla (subir dP no ayuda).
- **T_sumidero**, **η_p** y **ε_cond** casi no se mueven: η_p y ε_cond solo cambian en A4
  (0.75 → 0.805 y 0.95 → 0.95, es decir ε_cond ya empezaba en el techo).

=== §4 criterio activo ===
- **A1** — criterio activo en el óptimo: **O1** margen 0.0179 (O1 0.0179, O2 0.4231, O5 0.4775).
- **A2** — criterio activo en el óptimo: **O1** margen 0.0047 (O1 0.0047, O2 3.8111, O5 0.2534).
- **A3** — criterio activo en el óptimo: **O1** margen 0.0307 (O1 0.0307, O2 3.8054, O5 0.2643).
- **A4** — criterio activo en el óptimo: **O1** margen 0.0058 (O1 0.0058, O2 0.1248, O5 0.2457).
- **A5** — criterio activo en el óptimo: **O1** margen 0.0006 (O1 0.0006, O2 5.6586, O5 0.4877).

El criterio que manda en los cinco óptimos es **O1** (m_O1 = q4 − 0.90): el calor de entrada al
generador está justo en su mínimo. El más apretado es A5 (margen 0.0006) y el más holgado A3
(0.0307). O2 (temperatura de burbuja contra el condensador) y O5 (calor de la fuente) quedan
con holgura en los cinco.

## 5. Los óptimos que quedan en el borde de la caja

=== §5 bordes ===
A1 eta_t = 0.95, A2 T_sumidero = 278.15, A2 x_b = 0.5, A2 eta_t = 0.95, A2 eps_reg = 0.95, A3 P_alta = 5000, A3 x_b = 0.85, A3 eta_t = 0.946056, A3 eps_cond = 0.945788, A4 x_b = 0.5, A4 eta_t = 0.95, A4 eps_hrvg = 0.95, A4 eps_reg = 0.95, A4 eps_cond = 0.95

Esto hay que decirlo claro: **casi todos los óptimos tocan un borde de la caja**, y eso
significa que **el óptimo real podría estar fuera de la caja** (la búsqueda solo puede moverse
hacia adentro). Detalle por arranque:

- **A1**: η_t en el techo exacto (0.95).
- **A2**: T_sumidero en el piso (278.15 K), x_b en el piso (0.50), η_t y ε_reg en el techo
  (0.95). Si la caja de T_sumidero bajara, A2 probablemente bajaría más el sumidero.
- **A3**: P_alta en el techo (5000 kPa) y x_b en el techo (0.85). Además η_t = 0.9461 y
  ε_cond = 0.9458 quedan a menos del 1% de su techo (0.95): no tocaron el borde, pero están
  pegados.
- **A4**: x_b en el piso (0.50) y η_t, ε_HRVG, ε_reg, ε_cond en el techo (0.95) — sus
  temperaturas y presiones, que es justo lo que conserva del profesor, están fijas.
- **A5**: ningún óptimo en el borde de la caja.

## 6. Tiempos

=== §6 tiempos ===
pared: 5758 s | total evaluaciones: 560
A1: 117 evaluaciones, 6 iteraciones, 6562 s de suma
A2: 105 evaluaciones, 6 iteraciones, 6010 s de suma
A3: 112 evaluaciones, 7 iteraciones, 7670 s de suma
A4: 113 evaluaciones, 10 iteraciones, 4939 s de suma
A5: 113 evaluaciones, 7 iteraciones, 6550 s de suma

Notas sobre estas cifras: **pared** es el reloj de corrida larga: 5758 s = 95,97 min ≈ 1,6 h,
dentro de lo estimado (1,5–2,5 h). **Evaluaciones** cuenta las llamadas al solver (560 en
total, incluida la evaluación base de cada arranque). **Iteraciones** cuenta las que llegaron
a evaluar candidatos: cada arranque corta en una iteración más (la imprime `stdout.txt`) que
no evalúa nada porque ya no cabía dentro de las 120 evaluaciones. **S de suma** es el tiempo
de cada evaluación sumado (CPU), y supera la pared porque las evaluaciones corren en paralelo
(pool de 7).

## 7. Conclusión

=== §7 conclusión ===
1. sin restricciones: A2 eta=0.1548
2. A3 (sus temperaturas: T_fuente 623.15 K y T_sumidero 300.032917 K): eta=0.1274
2. A4 (sus presiones: P_alta 3000 kPa, P_baja 400 kPa, más T_sumidero): eta=0.1560
2. A5 (su fuente y su x_b: T_fuente 623.15 K y x_b 0.50): eta=0.1109
mejor global: A4 eta=0.1560 (KALINA)

- **Pregunta 1 (sin restricciones):** el mejor de los dos arranques libres es **A2, η = 0.1548**
  (A1 llega a 0.1498). Los dos arrancan del mejor KALINA de sus campañas y ambos mejoran:
  A2 +3.57 pp, A1 +2.68 pp.
- **Pregunta 2 (conservando datos del profesor):** gana **A4, que conserva sus presiones
  (P_alta 3000 kPa, P_baja 400 kPa) y su T_sumidero (300.032917 K): η = 0.1560**, el mejor de
  todo el experimento. A3 (sus dos temperaturas) queda en 0.1274 y A5 (su fuente + x_b) en
  0.1109. Es llamativo: **conservar las presiones del profesor no es una traba** — con esas
  presiones fijas se consigue la η más alta de las cinco corridas.
- Todas las salidas mejoran respecto a su punto de partida: A1 +2.68 pp, A2 +3.57 pp,
  A3 +3.45 pp, A4 +6.10 pp, A5 +2.64 pp, y las cinco terminan en KALINA con D = 0.
- El precio de la η: A4 es la más eficiente pero la que menos produce (W_net = 71.38 kW);
  A3 produce casi el doble (129.39 kW) con 2,86 pp menos de η.

## 8. Lo que no se sabe

1. **Es un óptimo local.** La búsqueda por patrones solo acepta mejoras y nunca sube a una
   colina peor: si el paisaje tiene varios picos, este procedimiento se queda en el que
   alcanza desde su arranque. Cada arranque dio un resultado distinto, lo cual es la prueba
   de que el resultado depende de por dónde se entra.
2. **Las diferencias menores que 0.4–0.7 pp no son concluyentes.** A4 contra A2 difiere en
   0.117 pp y A2 contra A1 en 0.504 pp: esas dos comparaciones no permiten afirmar quién es
   mejor. Solo A1 contra A3 (2.239 pp) y A3 contra A5 (1.645 pp) superan la banda.
3. **Puntos fuera de rango:**

=== §8 fuera_rango en el óptimo ===
A5

   El óptimo de A5 tiene `fuera_rango = True`: sus T2 y T5 valen 467.125 K, por encima de los
   420 K con respaldo experimental del motor (columnas afectadas: `eta` y `Wnet`). Es decir,
   **la η de A5 (0.1109) es una extrapolación**, no una lectura con respaldo. Su punto de
   partida (S5 de M5) ya tenía esa marca, y la búsqueda no la quitó. Los otros cuatro óptimos
   están dentro de rango.

## 9. Qué sigue

- **Soltar la caja donde se quedó pegada.** Siete arranques tocaron un borde (§5). Repetir la
  búsqueda ampliando solo esas variables diría si la η sigue subiendo o si el borde ya era el
  límite físico.
- **Confirmar el empate de arriba.** A4, A2 y A1 están dentro de la banda de 0.4–0.7 pp; con
  más evaluaciones (o con un segundo criterio de desempate, p. ej. W_net) se podría separar el
  primero del segundo.
- **Recalcular A5 fuera de la extrapolación.** Su η óptima no es confiable tal como está; o se
  replantea el escenario S5 (T_fuente más baja) o se respalda el motor a 467 K.
- **Contrastar los dos mejores con otra fuente**, como se hizo en M1, antes de dar η = 0.1560
  como respuesta final.
