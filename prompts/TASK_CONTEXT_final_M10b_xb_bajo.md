# TASK_CONTEXT — M10b: Húsavík con concentración de amoníaco baja (x_b 0.30–0.70) + Excel

**Directorio de trabajo:** `D:\Desktop\ciclo_kalina_tercero\.claude\worktrees\barrido-final`
**Python:** `D:\Desktop\ciclo_kalina_tercero\.venv\Scripts\python.exe`

## Notas de entorno (OBLIGATORIAS)

- Los archivos se crean y se modifican SOLO con `write` y `edit`.
- PowerShell 5.1: no existen `tee`, `tail` ni `&&`.
- **Toda corrida con el PARÁMETRO `timeout` de la herramienta shell = 7200000**, en primer plano y UNA
  sola vez. Nada de `Start-Process`, `taskkill` ni `Stop-Process`.
- `comun.py` exporta solo `PROFESOR`, `T_AMB_DISENO`, `TAU`, `PRESUPUESTO_S`, `VARS`, `COLS`,
  `margenes`, `indice_D` y `evaluar_punto`.
- Reutiliza la infraestructura de M10: `scripts/barrido_final/m10_datos.py` y `m10_corrida.py` (léelos).
  Lo nuevo va en scripts NUEVOS `m10b_*.py`, de 200 líneas como máximo cada uno. No modifiques los de
  M10, `src/` ni `comun.py`. No hacer commit.

## Pregunta

M10 barrió x_b de 0.60 a 0.95. ¿Qué pasa con Húsavík si la mezcla tiene **poco amoníaco**, entre
0.30 y 0.70? ¿Sigue habiendo KALINA? ¿Con qué P_baja? ¿Qué criterio falla?

## Diseño (ancla de Húsavík, igual que M10)

```
P_alta 3300, P_baja 690, T_fuente 394.15, T_sumidero 278.15, eta_t 0.90, eta_p 0.80,
eps_hrvg 0.85, eps_reg 0.75, eps_cond 0.95, m_b 1.0
piso O2 = 283.15
```

1. **OFAT de x_b a P_baja 690:** x_b = `numpy.linspace(0.30, 0.70, 17)` (pasos de 0.025). Son 17
   corridas.
2. **Malla x_b × P_baja:** 54 corridas.
   - x_b en {0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70};
   - P_baja en {200, 300, 400, 500, 600, 700}. Con menos amoníaco el punto de burbuja sube, así que
     hay que explorar P_baja más bajas que en M10.

En total son 71 corridas, en un solo pool de 7 procesos y con motor teqp. Las muestras se escriben
antes de correr. Humo con `M10B_HUMO=1`: 2 puntos.

## Salidas (en `resultados/2026-10-09_final_M10b_xb_bajo/`)

- `m10b_ofat_xb.csv` y `m10b_malla_xb_pbaja.csv` (columnas de `comun.COLS` más `variable`, `valor`).
- `m10b_xb.png`: a la izquierda, η contra x_b uniendo M10 (0.60–0.95) y M10b (0.30–0.70), coloreado por
  clase; a la derecha, el mapa de clase x_b × P_baja uniendo las dos mallas.
- `REPORTE_M10b.md`, en lenguaje llano:
  - una tabla por valor de x_b con clase, η, m_O1, m_O2, m_O5, códigos de falla y `fuera_rango`;
  - la P_baja mínima KALINA para cada x_b de la malla;
  - **qué criterio falla con x_b bajo** (por ejemplo, O1 título, O5 separador o O3), con las cifras;
  - lo que no se sabe.

  **Marca como "x_b bajo (< 0.55), fuera de lo habitual en Kalina"** los valores de x_b menores que
  0.55. No es un filtro: es una etiqueta. Las cifras salen todas de los CSV.
- `m10b_verificar.py`: recalcula las cifras del reporte e imprime OK o FALLA.
- `scripts/barrido_final/excel_m10b.py`, con el patrón de `excel_m10.py`. Hojas: `M10b_ofat_xb`,
  `M10b_malla` y `M10b_figura`, más sus filas en `Resumen`.
- Ejecuta en orden, cada uno con timeout=7200000: `excel_final.py`, `excel_m2.py`, `excel_m3_m2r.py`,
  `excel_m2s_m4.py`, `excel_m5.py`, `excel_m5c_m7_m8.py`, `excel_m6.py`, `excel_m9.py`, `excel_m10.py` y
  `excel_m10b.py`. Después, un verificador:
  - que las hojas M10b tengan las filas de su CSV;
  - que todas las hojas anteriores (78) sigan presentes.

## Formato de salida

El obligatorio de `AGENTS.md`.
