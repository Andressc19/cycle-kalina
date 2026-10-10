# TAB-M04b-01 · Corridas por subcaso del caso M04b

**Caso(s):** KF-M04b · **Bloque(s):** B07  
**Punto base:** caja M4 = las 10 variables barridas dentro de su caja (ver TAB-M04-00)  
**Datos fijos: m_b = 1 kg/s; motor de propiedades = teqp.**  
**Datos barridos: T_fuente [380.29–499.53] K (200 valores); T_sumidero [278.18–303.47] K (200 valores); P_alta [2009.9–4986.6] kPa (200 valores); P_baja [304.74–1497.2] kPa (200 valores); x_b [0.50012–0.84879] (200 valores); η_t [0.75036–0.91969] (200 valores); η_p [0.65092–0.89886] (200 valores); ε_HRVG [0.60061–0.94834] (200 valores); ε_reg [0.60167–0.94916] (200 valores); ε_cond [0.70052–0.94921] (200 valores); piso de O2 [278.18–303.47] K (200 valores).**  

| Subcaso | Corridas | Omitidos | Genuinos | KALINA | KALINA confiables | Corregibles | Inviables | No convergidos | Falsos convergidos (N2) | Fuera de rango |
|---|---|---|---|---|---|---|---|---|---|---|
| KF-M04b | 200 | 0 | 186 | 45 | 26 | 127 | 14 | 8 | 6 | 94 |

**Notas:** Filtro: conteo_por_subcaso. n = 1. † = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido (N2). Fuente: analisis_final/00_inventario/conteo_por_subcaso.csv.
