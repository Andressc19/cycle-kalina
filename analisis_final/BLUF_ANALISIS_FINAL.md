# Análisis de resultados de la campaña M1–M10b — terminado

> **Metodología ejecutada completa: 4 741 puntos organizados en 51 bloques, 76 de 78 cifras validadas,
> 30 figuras, 63 tablas, Excel interactivo (89 hojas) y tablero web.** Hay 2 decisiones pendientes:
> publicar el tablero y fusionar a master.

### Estado

| Ítem | Estado | Dato clave |
|---|---|---|
| Tabla única + condiciones por subcaso | ✅ | 4 741 puntos, 59 subcasos, 51 bloques |
| Validación cruzada (A4) | ✅ | 76 de 78 ✔; 2 diferencias de definición corregidas |
| Fichas por caso | ✅ | 16 fichas (17 casos), cada una con su recuadro "Antes de leer" |
| Figuras Matplotlib | ✅ | 30 de 30, cada una con título-conclusión, condiciones y pie |
| `Excel_kalina_final_final_final.xlsx` | ✅ | 89 hojas; Tablero recalculado y verificado en Excel |
| Tablero web | ✅ | Revisado en el navegador: cifras resumen correctas, sin errores |
| Power BI | — | Descartado: todo queda en Excel (decisión del usuario) |
| Ejecución vía OpenCode | ⚠️ | El proveedor se cayó; Claude terminó el código (autorizado) |

### Decisiones requeridas

1. ¿Se publica el tablero web como enlace privado para el profesor?
   **Recomiendo:** sí, porque se abre sin instalar nada y no mezcla bloques.
2. ¿Se fusiona `test/barrido_final` a master local?
   **Recomiendo:** sí, después de tu revisión; push o PR solo si lo pides.

### Riesgos

- Que se lea mal la conclusión sobre la fuente de 623 K (→ 1)
- Las franjas angostas solo están mapeadas donde hubo malla dirigida (M5c); el borde superior de T_fuente no está medido

### Información extra

- El modelo gratuito de OpenCode no soportó 3 agentes en paralelo; en adelante conviene lanzarlos de a uno.

---

### Desarrollo técnico

#### 1. LA FUENTE DE 623 K SÍ ADMITE KALINA

*↳ Riesgo 1: "la conclusión sobre la fuente de 623 K"*

**Qué:** con 623 K hay KALINA confiables, pero solo con x_b ≈ 0.7–0.85 y presiones altas
(M7-A3: 90 confiables; M5-S1: 2). Con la x_b o las presiones del profesor: 0 confiables.

&nbsp;\
**Por qué importa:** decir "623 K nunca funciona" es falso. La frase correcta es "623 K no funciona con el resto del enunciado".

&nbsp;\
**Acción:** las fichas M05, M07 y M09 y la metodología §3.3 ya lo dicen así.

---

*Fuente: tabla canónica y validación A4 (rama `test/barrido_final`, commit c7dffb2 en adelante). Tablero
Excel recalculado con Excel 2024; tablero web revisado en el navegador integrado.*
