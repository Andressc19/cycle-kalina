# FICHA KF-M01 — Reproducibilidad del caso del profesor

> **Antes de leer**
> - **Punto del profesor (PP):** los datos del enunciado. P_alta = 3000 kPa, P_baja = 400 kPa,
>   x_b = 0.50, T_fuente = 623.15 K, T_sumidero = 300.03 K, η_t = 0.85, η_p = 0.75,
>   ε_HRVG = 0.85, ε_reg = 0.75, ε_cond = 0.80.
> - **NO_CONVERGIO:** el modelo no encuentra un ciclo que cierre los balances; no hay ciclo que evaluar.
> - **Fase 1 (F1):** la primera corrida del caso del profesor, hecha el 2026-09-19 con el código de entonces.

### ID del caso:
`KF-M01` · bloque **B01**, con subcasos por grupo: base, P_alta, x_b y T_amb. Familia **R**
(reproducibilidad), diseño: una variable a la vez sobre PP. Fecha 2026-10-06, commit `1b01096`.

### Nombre del caso:
¿El código actual reproduce la Fase 1 del profesor?

### Objetivo del barrido:
Comprobar que el código actualizado da la misma clase que la corrida del 2026-09-19 en los puntos
del profesor. El código actual incluye el bracket tolerante, la protección A+B, la marca de rango y
el piso de O2 en 300.03 K.

### ¿Qué se barrió?
Los mismos 41 puntos de la F1: el punto base, P_alta, x_b y la temperatura ambiente hora por hora.

### ¿Por qué se barrió?
Antes de sacar conclusiones nuevas había que asegurar que los cambios del código no alteraban los
resultados ya conocidos. Si el código hubiera cambiado una clase, todo lo demás quedaría en duda.

### Datos o variables barridas:

| Subcaso | Variable barrida | Rango | n | Unidad |
|---|---|---|---|---|
| KF-M01-base | ninguna (PP, con motor teqp y con motor real) | — | 2 | — |
| KF-M01-P_alta | P_alta | 2000 – 4000 | 9 | kPa |
| KF-M01-x_b | x_b | 0.40 – 0.70 | 7 | – |
| KF-M01-T_amb | T_sumidero (perfil horario del enunciado) | 297.95 – 303.55 | 24 | K |

### Datos modificados:
Ninguno respecto al profesor. En cada subcaso solo se mueve su variable; todo lo demás queda en PP.
Lo único que cambia es el código: bracket tolerante (MA), protección A+B y piso de O2 = 300.03 K.

### Métodos aplicados:
Repetición punto a punto y comparación de la clase antes/después (MATEMATICA §3). Se usaron 6
procesos y 300 s por punto.

### Resultados obtenidos:
- **42 corridas, 0 genuinas: las 42 son NO_CONVERGIO** (validado por A4, V01).
- Coincidencia de clase con la F1: **41 de 41 (100 %)**. El punto base se corrió dos veces (teqp y real).
- Tiempo: 603 s en total; mediana de 76 s por punto.
- Tablas: TAB-M01-00 (condiciones), TAB-M01-01 (conteo) y TAB-M01-02 (antes/después).
  No lleva figura: no hay nada que graficar.

### Conclusiones del caso:
1. El código actual **reproduce exactamente** el resultado del profesor: con sus datos, el ciclo no converge.
2. Mover solo P_alta (2000–4000 kPa), solo x_b (0.40–0.70) o solo la temperatura ambiente no
   cambia nada: los 41 puntos siguen sin converger.
3. Eso indica que el bloqueo no está en esas variables. Está en el lado caliente: la fuente a 623 K
   (lo confirman M2 y M9).

### Advertencias, supuestos y limitaciones:
- No se puede separar el efecto del bracket tolerante del resto de cambios: no se corrió el
  contraexperimento sin MA.
- La F1 de septiembre usó otro piso de O2 (303.55 K). No importa aquí: O2 solo se evalúa en puntos
  que convergen, y ninguno convergió.

### Recomendaciones:
Usar M1 como garantía de reproducibilidad en el informe y pasar directo a M2. Para entender por qué
el punto del profesor no funciona, ver la ficha de M2.

**Fuentes:** `resultados/2026-10-06_final_M1/REPORTE_M1.md`, `m1_filas.csv`, `m1_comparacion.csv`; validación A4 (V01).
