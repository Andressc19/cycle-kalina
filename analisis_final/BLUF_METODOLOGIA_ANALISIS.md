# Metodología de análisis de resultados — campaña final campaña final

*Documento histórico (antes de ejecutar). El estado vigente está en `BLUF_ANALISIS_FINAL.md` y `REPORTE_ANALISIS_FINAL.md`.*

> **Metodología lista y ficha piloto (estudio 3.1) escrita: 17 casos, 23 figuras y 9 tablas definidas.** No se ha corrido código. Antes de lanzar el agente A1 (OpenCode) se necesitan 3 decisiones.

### Estado

| Ítem | Estado | Dato clave |
|---|---|---|
| Protocolo de análisis | ✅ | `docs/METODOLOGIA_ANALISIS_RESULTADOS.md` |
| Inventario de casos e IDs | ✅ | 17 casos `KF-Mnn`, 9 familias |
| Ficha piloto estudio 3.1 | ⚠️ | cifras tomadas del REPORTE; falta la verificación cruzada de A4 |
| Catálogo de figuras y tablas | ✅ | 23 FIG y 9 TAB, con código base |
| Agentes A1–A4 (OpenCode) | ❌ | TASK_CONTEXT sin escribir; requieren autorización |

### Decisiones requeridas

1. ¿Se aprueba el formato de la ficha piloto estudio 3.1 para las 16 restantes?
   **Recomiendo:** sí, porque cubre las 12 secciones e incorpora la nota del director.
2. ~~¿Tablas al Excel existente?~~ **Resuelto:** van a un libro nuevo, `datos/Excel_kalina_final_final_final.xlsx`, y todo en español.
3. ¿Se autoriza preparar y lanzar A1 (tabla canónica de todos los puntos)?
   **Recomiendo:** sí, porque A2, A3 y A4 dependen de esa tabla.

### Riesgos

- Algunos REPORTE_* de OpenCode contaron los N2 como convergidos; las cifras sin auditar pueden estar infladas (→ 1)
- El Δη original de estudio 3.1 incluye puntos con W_net ≤ 0 (50.7 pp en P_baja); el tornado actual engaña (→ 2)
- El piso de O2 cambió de regla en estudio 2.4; las fronteras O2 de estudio 1.1–estudio 3.1 no se comparan con las de estudio 3.2 en adelante

### Información extra

- Las skills "Data Analysis Pro", "Visualization Pro", etc. no existen en el catálogo; las cubren las `data:*` ya instaladas.

---

### Desarrollo técnico

#### 1. VALIDACIÓN CRUZADA ANTES DE CONCLUIR

*↳ Riesgo 1: "contaron los N2 como convergidos"*

**Qué:** A4 recalcula, desde la tabla canónica, cada cifra del §3.2 de la metodología y la marca con ✔ o ✘.

&nbsp;\
**Por qué importa:** un N2 es una fila con `convergio=True` y clase NO_CONVERGIO. Si se cuenta como genuino, sube el conteo de convergidos y desplaza las fronteras.

&nbsp;\
**Acción:** las conclusiones generales quedan en borrador hasta que A4 entregue `05_validacion/discrepancias.csv`.

---

#### 2. Δη SOLO CON TRABAJO POSITIVO

*↳ Riesgo 2: "El Δη original de estudio 3.1 incluye puntos"*

**Qué:** con el filtro W_net > 0, la variable con mayor Δη pasa a ser x_b (**10.8 pp**) y P_baja baja a 6.8 pp.

&nbsp;\
**Acción:** el filtro queda como regla del checklist y Figura 3.1-1 se regenera.

---

*Fuente: REPORTE_M1…estudio 6.2 y notas del director en `resultados/2026-10-0*_final_*`. No se recalculó ninguna cifra contra los CSV (pendiente de A4).*
