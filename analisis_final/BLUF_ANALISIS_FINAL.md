# Análisis de resultados de la campaña final — terminado

> **Metodología ejecutada completa y revisada tres veces: 4 741 puntos en 51 partes, 76 de 78 cifras
> validadas, 30 figuras, 62 tablas y el Excel interactivo (84 hojas, con 74 gráficos nativos), que es el tablero oficial.**
> Hay 2 decisiones pendientes: fusionar a master y limpiar los worktrees.

### Estado

| Ítem | Estado | Dato clave |
|---|---|---|
| Tabla única + condiciones por parte | ✅ | 4 741 puntos, 59 partes, 51 partes; idéntica a los 33 CSV de origen |
| Validación cruzada (A4) | ✅ | 76 de 78 ✔; las 2 diferencias son de definición y están corregidas |
| Fichas por caso | ✅ | 16 fichas (17 casos), 12/12 secciones; cifras recalculadas desde los datos |
| Figuras Matplotlib | ✅ | 30 de 30, cada una con título-conclusión, condiciones y pie |
| `Excel_kalina_final_final_final.xlsx` | ✅ | 84 hojas; 74 gráficos nativos de Excel; tablas con cuadrícula; hoja Tablero interactiva (tablero oficial) |
| Tablero web | ✅ | Extra; funciona en el navegador, necesita internet (Chart.js por CDN) |
| Power BI | — | Descartado: todo queda en Excel (decisión del usuario) |
| Ejecución vía OpenCode | ⚠️ | El proveedor se cayó; Claude terminó el código y hizo la tercera revisión (autorizado) |

### Decisiones requeridas

1. ¿Se fusiona `test/barrido_final` a master local?
   **Recomiendo:** sí, después de tu revisión; push o PR solo si lo pides.
2. ¿Se borran los 5 worktrees temporales `af-*`?
   **Recomiendo:** sí, porque ya están integrados.

### Riesgos

- Que se lea mal la conclusión sobre la fuente de 623 K (→ 1)
- Las franjas angostas solo están mapeadas donde hubo malla dirigida (estudio 4.2); el borde superior de T_fuente no está medido

### Información extra

- "KALINA confiable" exige además η y ε en [0.40, 0.95]: los 14 puntos F3 de Húsavík con 0.98–0.99 ya no cuentan (estudio 6.2: 239 confiables).

---

### Desarrollo técnico

#### 1. LA FUENTE DE 623 K SÍ ADMITE KALINA

*↳ Riesgo 1: "la conclusión sobre la fuente de 623 K"*

**Qué:** con 623 K hay KALINA confiables, pero solo con x_b de 0.71 a 0.85 y presiones altas
(estudio 5.1c: 90 confiables; estudio 4.1a: 2). Con la x_b o las presiones del profesor: 0 confiables.

&nbsp;\
**Por qué importa:** decir "623 K nunca funciona" es falso. La frase correcta es "623 K no funciona con el resto del enunciado".

&nbsp;\
**Acción:** las fichas estudio 4.1, estudio 5.1 y estudio 4.3 y la metodología §3.3 ya lo dicen así.

---

*Fuente: tabla canónica y validación A4 (rama `test/barrido_final`). Tercera revisión del 2026-10-10
hecha directamente por Claude (detalle en `REPORTE_ANALISIS_FINAL.md` §4c). Tablero de Excel
recalculado con Excel 2024; tablero web revisado en el navegador integrado.*
