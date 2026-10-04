# Reporte — Banda de incertidumbre de η por el modelo de propiedades

Fecha: 2026-10-03. Rama `test/verificacion_DWSIM`. Ejecutado por Claude (a pedido). `src/` sin cambios.

## La pregunta

Tu modelo de propiedades (Tillner-Roth & Friend / IAPWS G4-01) tiene una incertidumbre
publicada. ¿Cuánto mueve eso la eficiencia η del ciclo? Con esa banda, ¿las diferencias
contra Elsayed y contra DWSIM caben dentro de lo que el propio modelo no puede asegurar?

## Cómo funciona (en simple)

IAPWS G4-01 §7 dice cuánto se puede equivocar el modelo (CONTEXT.md):
- **Equilibrio líquido-vapor**: las composiciones de líquido (xL) y vapor (yV) en equilibrio,
  ±0.01 en fracción molar. Es lo que decide cuánto vapor sale del separador hacia la turbina.
- **Entalpía de exceso** (la energía que se libera o absorbe al mezclar NH₃ y agua): ±200 J/mol.

Se "empuja" el modelo dentro de esos márgenes, una cosa a la vez (xL +/−, yV +/−, entalpía
+/−), se resuelve el ciclo completo cada vez y se mira cuánto cambia η. Es como medir cuánto
se mueve el resultado de una receta si la balanza puede fallar ±1 g en cada ingrediente.

**Supuestos aprobados** (estimación de primer orden):
- Forma de la perturbación de entalpía: ±200·4·xm·(1−xm) J/mol (cero en los puros, máxima a
  mitad de composición); G4-01 solo da la cota.
- Se perturba h (y su inversa T(P,h)) pero no s.
- Las contribuciones se combinan como independientes (raíz de suma de cuadrados), aunque en
  realidad salen del mismo modelo y podrían estar correlacionadas.

## Cómo se hizo

- `scripts/incertidumbre_eta.py`: subclase de `TeqpVerificado` que desplaza el equilibrio y/o
  la entalpía (sin tocar `src/`); 21 resoluciones (3 puntos × 7 casos, ~50 s cada una). El caso
  base reproduce las η ya conocidas (ELSAYED 11.0554 %, KALINA-01 10.3716 %, KALINA-11 12.1500 %).
- Dos casos de KALINA-11 (xL−, yV−) fallaron con teqp (`PropertyRangeError`: teqp no cubre el
  estado perturbado). Se repitieron con el motor real (`scripts/incertidumbre_eta_real.py`,
  ~9 min cada uno), junto con su propio caso base, para medir la diferencia con el mismo motor.
- Salidas: `casos.csv`, `casos_motor_real.csv`, `banda_final.csv`, consolas.

## Resultados

### Cuánto mueve cada incertidumbre a η (puntos porcentuales)

| Punto | η base | xL +0.01 | xL −0.01 | yV +0.01 | yV −0.01 | h_exceso ± |
|---|---|---|---|---|---|---|
| ELSAYED (1500 kPa) | 11.055 % | −0.06 | **+0.46** | **−0.33** | −0.01 | ±0.001 |
| KALINA-01 (3000 kPa) | 10.372 % | −0.27 | **+0.59** | **−0.37** | +0.01 | ±0.003 |
| KALINA-11 (5000 kPa) | 12.150 % | −0.21 | **+0.45** ¹ | **−0.36** | −0.00 ¹ | ±0.003 |

¹ calculado con el motor real (teqp no cubre ese estado).

### Banda resultante (asimétrica: hacia arriba y hacia abajo por separado)

| Punto | η base | Banda | Rango de η | RSS simétrico |
|---|---|---|---|---|
| ELSAYED | 11.06 % | +0.46 / −0.34 pp | 10.72 – 11.51 % | ±0.57 pp |
| KALINA-01 | 10.37 % | +0.59 / −0.46 pp | 9.91 – 10.97 % | ±0.70 pp |
| KALINA-11 | 12.15 % | +0.45 / −0.42 pp | 11.73 – 12.60 % | ±0.58 pp |

### Las comparaciones externas contra la banda

| Comparación | η código | η externa | Diferencia | ¿Dentro de la banda? |
|---|---|---|---|---|
| Elsayed 2013 (paper, caso citado) | 11.05 % | 11.38 % | +0.33 pp | **Sí** (límite +0.46) |
| Elsayed/Embaye, 23 puntos (benchmark previo) | — | — | \|Δη\| medio 0.28 pp, máx 1.16 pp | **El típico sí**; el máximo no |
| DWSIM-PR, KALINA-01 | 10.37 % | 10.74 % | +0.37 pp | **Sí** (límite +0.59) |
| DWSIM-PR, ELSAYED con efectividades | 11.05 % | 11.64 % | +0.59 pp | **No, por poco** (límite +0.46) |

## Conclusión

- **La incertidumbre de η del modelo es de ~±0.4–0.7 pp** (≈ ±4–7 % relativo) en los tres puntos.
- **Casi toda viene del equilibrio líquido-vapor** (cuánto vapor manda el separador a la
  turbina). La entalpía de exceso no pesa (≤ 0.003 pp): solo entra donde cambia la
  composición (separador y absorbedor) y ahí casi se cancela.
- **La diferencia con Elsayed (caso citado, +0.33 pp) cabe dentro de la incertidumbre del
  propio modelo**, igual que la diferencia típica del benchmark de 23 puntos (0.28 pp) y la de
  DWSIM en KALINA-01. Es decir: esas discrepancias no indican un error del código; son del
  tamaño de lo que el modelo de propiedades no puede asegurar.
- La diferencia con DWSIM en el caso Elsayed (+0.59 pp) queda apenas fuera, coherente con que
  Peng-Robinson se desvía de G4-01 más que la propia incertidumbre de G4-01 (sonda de paquetes).
  El máximo del benchmark (1.16 pp) también queda fuera y merece mirarse por separado.

## Lo que no sabemos

- La forma real de la incertidumbre de la entalpía de exceso con la composición (se supuso;
  como su efecto es ≤ 0.003 pp, el supuesto no cambia la conclusión).
- Si xL y yV están correlacionados en el modelo real: sumarlos en RSS puede sobreestimar o
  subestimar la banda. Las semibandas individuales (tabla 1) no dependen de eso.
- Solo 3 puntos; no se barrió todo el dominio. Cerca del punto crítico G4-01 da hasta ±0.04
  (no ±0.01), allí la banda sería mayor.

## Qué sigue

1. Revisar el punto del benchmark Elsayed con |Δη| = 1.16 pp (fuera de banda) para ver si es
   un borde de la figura digitalizada o algo del modelo.
2. Segunda fuente independiente (punto 1): pendiente de que el usuario consiga el PDF de
   Nemati et al. (2017).
