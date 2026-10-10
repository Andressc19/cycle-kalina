# Guía rápida: tablero de la campaña final en Power BI (opcional)

Power BI Desktop no está instalado en este equipo. Si lo instalas (es gratuito, desde la Microsoft
Store), esta carpeta ya tiene los datos listos en **esquema estrella**, el formato que Power BI importa
directo.

## 1. Archivos

| Archivo | Qué es | Clave |
|---|---|---|
| `hechos_puntos.csv` | Un punto evaluado por fila (4 741 filas) | `id_punto`; se une por `id_caso`, `id_subcaso` y `clase_trazo` |
| `dim_caso.csv` | Un caso por fila, con sus conteos | `id_caso` |
| `dim_condiciones.csv` | Variables fijas o barridas por subcaso | `id_subcaso` |
| `dim_variable.csv` | Nombre en español y unidad de cada variable | `variable` |
| `dim_clase.csv` | Etiqueta, color y orden de cada clase | `clase` ↔ `hechos_puntos[clase_trazo]` |

## 2. Pasos

1. *Obtener datos → Texto/CSV*: importar los 5 archivos con codificación UTF-8 y punto decimal (".").
2. *Modelo*: relacionar `hechos_puntos[id_caso]` → `dim_caso[id_caso]` (varios a uno) y
   `hechos_puntos[clase_trazo]` → `dim_clase[clase]` (varios a uno). `dim_condiciones` se filtra
   con una segmentación por `id_subcaso`.
3. *Segmentaciones*: `bloque_director` primero, y después `id_subcaso`. **Regla del proyecto:**
   nunca mostrar dos bloques en el mismo gráfico.
4. *Medidas DAX*:

```DAX
Corridas = COUNTROWS ( hechos_puntos )
Genuinas = CALCULATE ( [Corridas], hechos_puntos[genuino] = TRUE () )
KALINA = CALCULATE ( [Corridas], hechos_puntos[clasificacion] = "KALINA" )
KALINA confiables = CALCULATE ( [Corridas], hechos_puntos[kalina_confiable] = TRUE () )
% KALINA = DIVIDE ( [KALINA], [Genuinas] )
η máx. KALINA = CALCULATE ( MAX ( hechos_puntos[eta_pct] ), hechos_puntos[clasificacion] = "KALINA" )
```

5. *Visuales*:
   - tarjetas con las 4 medidas;
   - un gráfico de dispersión (eje X y eje Y = variables barridas del bloque; leyenda = `clase_trazo`, con los colores de `dim_clase`);
   - una tabla con `dim_condiciones` filtrada por el bloque.

El tablero HTML (`analisis_final/06_tablero/tablero_kalina.html`) y la hoja `Tablero` del Excel ya
hacen todo esto sin instalar nada. Power BI solo agrega la posibilidad de publicarlo en Power BI Service.
