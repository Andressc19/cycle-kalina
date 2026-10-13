# Ficha 2.1 — ¿Basta un solo cambio al enunciado para obtener KALINA?

> **Antes de leer**
> - **Punto del profesor (PP):** los datos del enunciado. P_alta = 3000 kPa, P_baja = 400 kPa,
>   x_b = 0.50, T_fuente = 623.15 K, T_sumidero = 300.03 K, η_t = 0.85, η_p = 0.75,
>   ε_HRVG = 0.85, ε_reg = 0.75, ε_cond = 0.80. Con ellos el ciclo no converge (estudio 1.1).
> - **Punto genuino:** el modelo lo resolvió de verdad (clase KALINA, CORREGIBLE o INVIABLE).
> - **N2 (falso convergido):** el solver dice que convergió, pero el clasificador lo descarta; no cuenta.
> - **O1:** título del vapor a la salida de la turbina. **O2:** cavitación, es decir, el líquido debe
>   llegar subenfriado a la bomba. **O5:** el separador debe recibir dos fases.
> - **Fuera de rango:** estados fuera del rango validado del modelo de propiedades (líquido por encima de 420 K).

### ID del caso:
**Estudio 2.1** · Un solo cambio. Responde la pregunta 2: ¿Qué es lo mínimo que hay que cambiar para que funcione?
Familia **F** · 2026-10-06 · commit `02f64b6` · código de origen: M02-N1.

### Nombre del caso:
Nivel 1: cambiar una sola variable del profesor.

### Objetivo del barrido:
Encontrar el cambio más pequeño sobre los datos del profesor que convierta el ciclo en KALINA,
empezando por cambiar una sola variable.

### ¿Qué se barrió?
Cada una de las 10 variables, de a una, con las otras 9 en el valor del profesor.

### ¿Por qué se barrió?
Para conservar la mayor cantidad posible de datos del enunciado. Si un solo cambio bastaba, era la
respuesta más fiel al profesor.

### Datos o variables barridas:
10 variables × 10 valores equiespaciados dentro de su rango, más la bisección de las fronteras
detectadas. Las eficiencias y efectividades se movieron en [0.75, 0.85] (rango de ese momento,
ampliado después en estudio 2.3). Total: **132 corridas** (100 de malla y 32 de bisección).

### Datos modificados:
Solo la variable de cada tramo. Las demás quedan en PP y el piso de O2 en 300.03 K.

### Métodos aplicados:
Malla 1D de 10 valores por variable, más bisección de cada frontera entre vecinos que cambian de
resultado. La tolerancia fue 10 kPa en presiones, 0.5 K en temperaturas y 0.005 en fracciones
(MATEMATICA §4).

### Resultados obtenidos:
- 132 corridas: **15 genuinas, 0 KALINA**, 13 CORREGIBLE, 2 INVIABLE, 96 sin converger y
  **21 N2**. Hay 32 fuera de rango.
- Solo tres variables dan puntos genuinos: T_fuente (7), ε_HRVG (7) y x_b (1: x_b = 0.30, INVIABLE).
  P_alta parecía converger, pero sus 13 "convergidos" son todos falsos (N2).
- Recontando solo los genuinos (nota del director):
  - **T_fuente 403–497 K:** CORREGIBLE; solo falla O2.
  - **T_fuente 529–560 K:** CORREGIBLE; fallan O1 y O2.
  - **T_fuente 592 K:** INVIABLE (fallan O1, O2 y O5).
  - **ε_HRVG 0.75–0.817** (con la fuente de 623 K): falla O1, al filo, y O2, con un déficit de 18 a 20 K.
- El punto más cercano es **T_fuente = 402.9 K**: solo falla O2, por 2.0 K, y tiene η = 9.86 %.
- Tablas: 2.1-1, 2.1-2, 2.1-3. Figuras: 2.1-1.

### Conclusiones del caso:
1. **Con un solo cambio no hay KALINA.**
2. El cambio que más acerca es **bajar T_fuente a ~400 K**. Con eso el ciclo converge y solo le
   falta cumplir la cavitación (O2) por unos 2 K.
3. El bloqueo dominante es O2. Como O2 se cierra subiendo P_baja (regla del proyecto), el
   siguiente paso natural es cambiar dos variables: T_fuente (o ε_HRVG) junto con P_baja.

### Advertencias, supuestos y limitaciones:
- El reporte original decía que bloqueaba "C3". Eso venía de contar los 21 N2 como convergidos;
  el director lo corrigió y aquí se usan solo los genuinos.
- Las fronteras se refinaron sobre la bandera del solver, no sobre la clase. La frontera útil de
  T_fuente (entre 371.5 y 402.9 K) quedó sin refinar.
- Malla de 10 valores: una zona KALINA más angosta que (b − a)/9 podría no verse.
- Los CORREGIBLE con T_fuente ≥ 434 K y los de ε_HRVG están fuera de rango.

### Recomendaciones:
Pasar al nivel 2 con los pares (T_fuente, P_baja) y (ε_HRVG, P_baja). Ver estudio 2.2.

**Fuentes:** `resultados/2026-10-06_final_M2/REPORTE_M2_N1.md` (§6 y §9, nota del director), `m2n1_malla.csv`, `m2n1_biseccion.csv`, `m2n1_resumen.csv`; verificación V02.
