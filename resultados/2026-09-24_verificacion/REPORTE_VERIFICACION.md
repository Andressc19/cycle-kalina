# Reporte — Verificacion del salto del solver y del motor real (2026-09-24)

## Parte B — Diagnostico del salto en (x_b=0.60, P_alta=4000, T_fuente=394)

Par del salto (evaluaciones_margen.csv): P=423.914831 kPa (eta=0.0336) ↔ P=424.169832 kPa (eta=0.0804); dP=0.2550 kPa, deta=0.0468; T9_amb salta 291.9492 -> 291.5392 K.

### B1. Barrido fino de P_baja (±5 kPa, paso 0.25 kPa)

| P_baja | T1 | T2 | q2 | fase2 | m3 | eta | Wnet | T9 |
|---|---|---|---|---|---|---|---|---|
| 419.04 | 364.218155 | 391.64661 | 0.101884 | bifasico | 0.101884 | 0.080856 | 19.6217 | 291.408586 |
| 419.29 | 364.32693 | 391.651007 | 0.101943 | bifasico | 0.101943 | 0.033659 | 8.1525 | 291.821923 |
| 419.54 | 364.326956 | 391.651009 | 0.101943 | bifasico | 0.101943 | 0.033656 | 8.1516 | 291.821958 |
| 419.79 | 364.326954 | 391.651008 | 0.101943 | bifasico | 0.101943 | 0.033652 | 8.1508 | 291.821992 |
| 420.04 | 364.326951 | 391.651008 | 0.101943 | bifasico | 0.101943 | 0.033648 | 8.1499 | 291.822025 |
| 420.29 | 364.326949 | 391.651008 | 0.101943 | bifasico | 0.101943 | 0.033645 | 8.149 | 291.822059 |
| 420.54 | 364.326947 | 391.651008 | 0.101943 | bifasico | 0.101943 | 0.033641 | 8.1482 | 291.822093 |
| 420.79 | 364.326945 | 391.651008 | 0.101943 | bifasico | 0.101943 | 0.033638 | 8.1473 | 291.822127 |
| 421.04 | 364.326942 | 391.651008 | 0.101943 | bifasico | 0.101943 | 0.033634 | 8.1465 | 291.822161 |
| 421.29 | 364.32694 | 391.651008 | 0.101943 | bifasico | 0.101943 | 0.033631 | 8.1456 | 291.822194 |
| 421.54 | 364.326944 | 391.651008 | 0.101943 | bifasico | 0.101943 | 0.033627 | 8.1447 | 291.822228 |
| 421.79 | 364.326941 | 391.651008 | 0.101943 | bifasico | 0.101943 | 0.033624 | 8.1439 | 291.822262 |
| 422.04 | 364.326939 | 391.651008 | 0.101943 | bifasico | 0.101943 | 0.03362 | 8.143 | 291.822295 |
| 422.29 | 364.326937 | 391.651008 | 0.101943 | bifasico | 0.101943 | 0.033617 | 8.1422 | 291.822329 |
| 422.54 | 364.326934 | 391.651008 | 0.101943 | bifasico | 0.101943 | 0.033613 | 8.1413 | 291.822362 |
| 422.79 | 364.326932 | 391.651008 | 0.101943 | bifasico | 0.101943 | 0.033609 | 8.1405 | 291.822396 |
| 423.04 | 364.32693 | 391.651007 | 0.101943 | bifasico | 0.101943 | 0.033606 | 8.1396 | 291.822429 |
| 423.29 | 364.326927 | 391.651007 | 0.101943 | bifasico | 0.101943 | 0.033602 | 8.1387 | 291.822463 |
| 423.54 | 364.326925 | 391.651007 | 0.101943 | bifasico | 0.101943 | 0.033599 | 8.1379 | 291.822496 |
| 423.79 | 364.326922 | 391.651007 | 0.101943 | bifasico | 0.101943 | 0.033595 | 8.137 | 291.82253 |
| 424.04 | 364.266676 | 391.648571 | 0.101911 | bifasico | 0.101911 | 0.080519 | 19.523 | 291.413626 |
| 424.29 | 364.218984 | 391.646643 | 0.101885 | bifasico | 0.101885 | 0.080402 | 19.5112 | 291.412626 |
| 424.54 | 364.219023 | 391.646645 | 0.101885 | bifasico | 0.101885 | 0.08038 | 19.5059 | 291.412817 |
| 424.79 | 364.219062 | 391.646646 | 0.101885 | bifasico | 0.101885 | 0.080359 | 19.5007 | 291.413009 |
| 425.04 | 364.219101 | 391.646648 | 0.101885 | bifasico | 0.101885 | 0.080337 | 19.4955 | 291.4132 |
| 425.29 | 364.21914 | 391.646649 | 0.101885 | bifasico | 0.101885 | 0.080316 | 19.4902 | 291.41339 |
| 425.54 | 364.219179 | 391.646651 | 0.101885 | bifasico | 0.101885 | 0.080295 | 19.485 | 291.413581 |
| 425.79 | 364.219218 | 391.646653 | 0.101885 | bifasico | 0.101885 | 0.080273 | 19.4798 | 291.413772 |
| 426.04 | 364.219257 | 391.646654 | 0.101885 | bifasico | 0.101885 | 0.080252 | 19.4746 | 291.413963 |
| 426.29 | 364.219296 | 391.646656 | 0.101885 | bifasico | 0.101885 | 0.08023 | 19.4694 | 291.414153 |
| 426.54 | 364.219335 | 391.646657 | 0.101885 | bifasico | 0.101885 | 0.080209 | 19.4642 | 291.414344 |
| 426.79 | 364.219374 | 391.646659 | 0.101885 | bifasico | 0.101885 | 0.080187 | 19.459 | 291.414534 |
| 427.04 | 364.219413 | 391.64666 | 0.101885 | bifasico | 0.101885 | 0.080166 | 19.4538 | 291.414724 |
| 427.29 | 364.219452 | 391.646662 | 0.101885 | bifasico | 0.101885 | 0.080145 | 19.4486 | 291.414914 |
| 427.54 | 364.219491 | 391.646664 | 0.101885 | bifasico | 0.101885 | 0.080123 | 19.4434 | 291.415104 |
| 427.79 | 364.219529 | 391.646665 | 0.101885 | bifasico | 0.101885 | 0.080102 | 19.4382 | 291.415294 |
| 428.04 | 364.219568 | 391.646667 | 0.101885 | bifasico | 0.101885 | 0.080081 | 19.433 | 291.415484 |
| 428.29 | 364.219607 | 391.646668 | 0.101885 | bifasico | 0.101885 | 0.080059 | 19.4278 | 291.415674 |
| 428.54 | 364.219646 | 391.64667 | 0.101885 | bifasico | 0.101885 | 0.080038 | 19.4226 | 291.415863 |
| 428.79 | 364.219684 | 391.646671 | 0.101885 | bifasico | 0.101885 | 0.080017 | 19.4174 | 291.416053 |
| 429.04 | 364.219723 | 391.646673 | 0.101885 | bifasico | 0.101885 | 0.079995 | 19.4122 | 291.416242 |

### B2. F(T1) por malla (paso 1 K) y raices

Rango de T1: 284 a 393 K. Malla completa en salto_F_T1.csv; las raices detectadas por cambio de signo y su clasificacion quedan en run_B.log. Raiz que elegiria resolver_ciclo via _bracketear: [364.326921273679, 364.21888238096756].

### B3. Otros saltos |deta|>0.02 con |dP|<5 kPa en evaluaciones_margen.csv

| x_b | P_alta | T_fuente | P1 | eta1 | P2 | eta2 | dP | deta |
|---|---|---|---|---|---|---|---|---|
| 0.6 | 4000 | 394 | 423.914831 | 0.0336 | 424.169832 | 0.0804 | 0.255 | 0.0468 |

### B4. Diagnostico y mecanismo

**No es una seleccion entre multiples raices de F(T1).** La malla gruesa (paso 1 K,
salto_F_T1.csv) y un micro-barrido de F(T1) con paso 0.01 K en T1 ∈ [364.0, 364.7]
(microescaneo.log) muestran **exactamente UNA raiz** en cada lado del salto:
P=423.95 → cruce en (364.32, 364.33); P=424.04 → cruce en (364.26, 364.27). La raiz T1
se mueve de forma continua (364.33 → 364.27 K) al cruzar la ventana del salto; brentq con
el bracket de _bracketear converge siempre a esa unica raiz.

**El salto es una conmutacion interna de rama del modelo de ciclo.** Con T1 practicamente
fijo (~364.3 K), mismo e3 (h3=1794.71 kJ/kg, x3=0.97496, m3=0.10194) y P_baja que solo
cambia 0.25 kPa, el estado de salida de turbina salta: e4 h=1659.49→1547.74 kJ/kg,
T4=313.94→290.41 K. Resultado: Wt=13.79→25.17 kW, Wnet=8.14→19.52 kW, eta=0.0336→0.0805;
T9_amb pasa de 291.82→291.41 K. Puntos de control: P=424.02 aun entrega rama baja
(eta=0.0335) y P=424.04 ya entrega rama alta (eta=0.0805): la conmutacion ocurre en una
ventana de P de solo ~0.02-0.25 kPa alrededor de P≈424.03.

**La estructura de ramas no es monotona**: en el barrido fino (B1) el punto P=419.04 cae
en la rama alta (eta=0.0809), de P=419.29 a P=423.79 en la rama baja (eta≈0.034) y de
P=424.04 en adelante vuelve a la rama alta (eta≈0.080-0.081): hay al menos dos
conmutaciones en ±5 kPa alrededor de P≈424, es decir, dos atractores estables del modelo
con asentamiento dependiente del camino de convergencia interna (probablemente la raiz del
flash/expansion isoentropica de teqp en la salida de turbina dentro del domo bifasico,
P≈424 kPa, x≈0.975).

**Ambas ramas pasan todas las verificaciones** (clasificacion KALINA, sin fallas), asi que
el salto es invisible a las restricciones operativas actuales.

**Consecuencia para margen2k**: cualquier raiz P* del margen O2 que caiga a menos de
~0.25 kPa de una conmutacion es numericamente fragil: mover P_baja 0.03 kPa cambia eta un
140%. La raiz P*=424.169832 del punto (0.6, 4000, 394) queda ~0.13 kPa por encima de la
segunda conmutacion y por eso entrega consistentemente la rama alta (eta=0.0804); una grilla
ligeramente distinta habria entregado la rama baja con el mismo margen O2, es decir, ese P*
no esta definido de forma robusta.

**Recomendaciones** (no aplicadas; requieren decision del director):
1. En los barridos de margen O2, tras hallar P* evaluar eta en P* ± paso; si |Δeta| > 0.01,
   marcar el P* como "inestable (rama dual)" en vez de aceptarlo ciegamente.
2. Auditar la expansion isoentropica / flash de salida de turbina del TeqpAdapter para
   P≈424 kPa, x≈0.975 (no unicidad de la raiz dentro del domo bifasico); tarea separada.
3. Opcional: restriccion operativa de calidad a la salida de turbina (p. ej. x4 > 0.9) para
   que la rama de baja potencia (condensacion profunda en turbina) quede senalada por O1/O3.

## Parte A — Verificacion con AmmoniaWaterAdapter (motor real)

Parametros fijos: eps 0.85/0.80/0.85, T_sumidero=283 K, eta_t=eta_p=0.80, m_b=1 kg/s; P_baja exacto de barrido_margen2k.csv (sin re-optimizar); margen O2 con T9_amb a T_sumidero=283.15 K y T_bur=bubble_point(P_baja, x_b); clasificacion con evaluar_ciclo(T_amb_diseno=283.15).

### A1. Tabla completa por motor y punto

| motor | x_b | P_alta | T_fuente | P_baja | eta | Wnet | margen_O2 | clasificacion | fallas | tiempo_s | error |
|---|---|---|---|---|---|---|---|---|---|---|---|
| teqp | 0.8 | 4000.0 | 394.0 | 1101.510788 | 0.097348 | 70.1924 | 1.999934 | KALINA | - | 25.1 | - |
| real | 0.8 | 4000.0 | 394.0 | 1101.510788 | 0.097334 | 70.1814 | 2.026369 | KALINA | - | 276.6 | - |
| teqp | 0.65 | 5000.0 | 423.0 | 704.644595 | 0.1215 | 71.8618 | 2.000091 | KALINA | - | 31.8 | - |
| real | 0.65 | 5000.0 | 423.0 | 704.644595 | 0.121492 | 71.8529 | 2.019594 | KALINA | - | 334.8 | - |
| teqp | 0.8 | 5000.0 | 394.0 | 952.892781 | 0.110591 | 63.8959 | 2.000644 | KALINA | - | 30.3 | - |
| real | 0.8 | 5000.0 | 394.0 | 952.892781 | 0.110574 | 63.8856 | 2.02333 | KALINA | - | 325.7 | - |

### A2. Lado a lado por punto y veredicto

| x_b | P_alta | T_fuente | P_baja | eta_teqp | eta_real | deta_rel | Wnet_teqp | Wnet_real | dWnet_rel | marg_teqp | marg_real | dmarg_rel | clasif_teqp | clasif_real | veredicto |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.65 | 5000 | 423 | 704.644595 | 0.1215 | 0.121492 | 0.00658% | 71.8618 | 71.8529 | 0.0124% | 2.000091 | 2.019594 | 0.966% | KALINA | KALINA | confirmado |
| 0.8 | 5000 | 394 | 952.892781 | 0.110591 | 0.110574 | 0.0154% | 63.8959 | 63.8856 | 0.0161% | 2.000644 | 2.02333 | 1.12% | KALINA | KALINA | confirmado |
| 0.8 | 4000 | 394 | 1101.510788 | 0.097348 | 0.097334 | 0.0144% | 70.1924 | 70.1814 | 0.0157% | 1.999934 | 2.026369 | 1.3% | KALINA | KALINA | confirmado |

Veredictos: **confirmado** = misma clasificacion; **no confirmado** = clasificacion distinta; **no evaluable** = el motor real no convergio.

