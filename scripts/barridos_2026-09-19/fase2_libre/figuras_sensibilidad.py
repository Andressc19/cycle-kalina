"""Fase 2 (tarea 2026-09-20-fase2-sensibilidad-final) — figuras + resumen.

Partes B/C/D: graficos PNG en resultados/barridos_2026-09-19/figuras/ con
prefijo `fase2_` y el resumen resumen_fase2.json. Figuras:

- fase2_sensibilidad_<var>.png (5): eta vs la variable barrida, puntos
  coloreados por clasificacion (KALINA=#2ca02c, CORREGIBLE=#ff7f0e, otras
  [INVIABLE/DEGENERADO/NO_CONVERGIO/VALIDO_ADVERTENCIA]=#d62728), leyenda.
- fase2_mapa_2d_pbaja_epscond.png: heatmap categorico de la clasificacion en
  el plano P_baja × eps_cond con la frontera KALINA/CORREGIBLE visible.

Estilo consistente con src/plots.py: matplotlib.figure.Figure directa (sin
pyplot global), titulo y ejes en espanol con unidades, grid alpha 0.3.

NO toca codigo de produccion; NO toca fase3_real/ ni fase1_profesor/.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.figure import Figure
from matplotlib.patches import Patch

_RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_RAIZ))

_CARPETA = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location(
    "comun_sensibilidad", _CARPETA / "comun_sensibilidad.py")
comun = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(comun)

FASE2 = _RAIZ / "resultados" / "barridos_2026-09-19" / "fase2_libre"
FIGURAS = _RAIZ / "resultados" / "barridos_2026-09-19" / "figuras"
COL_KALINA, COL_CORREGIBLE, COL_OTRO = "#2ca02c", "#ff7f0e", "#d62728"
ETIQUETAS = {
    "x_b": ("Composición global de NH3", "-"),
    "P_baja": ("Presión baja", "kPa"),
    "eps_cond": ("Efectividad del condensador", "-"),
    "eta_t": ("Eficiencia isentrópica de la turbina", "-"),
    "eps_hrvg": ("Efectividad del HRVG", "-"),
}


def color_clasificacion(clas: str) -> str:
    if clas == "KALINA":
        return COL_KALINA
    if clas == "CORREGIBLE":
        return COL_CORREGIBLE
    return COL_OTRO


def fig_sensibilidad_ofat(df: pd.DataFrame, var: str) -> Figure:
    """η vs la variable barrida, puntos coloreados por clasificacion."""
    etiqueta, unidad = ETIQUETAS[var]
    fig = Figure(figsize=(8, 5))
    ax = fig.subplots()
    for grupo in ("KALINA", "CORREGIBLE", "OTRO"):
        if grupo == "OTRO":
            sub = df[~df["clasificacion"].isin(("KALINA", "CORREGIBLE"))]
            nombre = "Otras (INVIABLE/DEGENERADO/NO_CONVERGIO)"
        else:
            sub = df[df["clasificacion"] == grupo]
            nombre = grupo
        if sub.empty:
            continue
        ax.scatter(sub[var], sub["eta"], s=48, zorder=3,
                   color=color_clasificacion(grupo), label=nombre)
    ax.set_xlabel(f"{etiqueta} [{unidad}]")
    ax.set_ylabel("Eficiencia térmica η [-]")
    ax.set_title(f"Sensibilidad de η frente a {etiqueta} (Fase 2)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    return fig


def fig_mapa_2d(df: pd.DataFrame) -> Figure:
    """Heatmap de la clasificacion en el plano P_baja × eps_cond."""
    pb = sorted(df["P_baja"].unique())
    ec = sorted(df["eps_cond"].unique())
    codigo = df.pivot(index="P_baja", columns="eps_cond",
                      values="clasificacion").map(
        lambda c: 0 if c == "KALINA" else (1 if c == "CORREGIBLE" else 2))
    Z = codigo.values.astype(float)
    cmap = ListedColormap([COL_KALINA, COL_CORREGIBLE, COL_OTRO])
    fig = Figure(figsize=(8, 5.5))
    ax = fig.subplots()
    im = ax.imshow(Z, origin="lower", aspect="auto",
                   extent=(min(ec) - 0.01, max(ec) + 0.01,
                           min(pb) - 10, max(pb) + 10),
                   cmap=cmap, vmin=0, vmax=2, interpolation="nearest")
    ax.contour(np.asarray(ec), np.asarray(pb), Z, levels=[0.5, 1.5],
               colors="k", linewidths=0.9)
    for i, p in enumerate(pb):
        for j, e in enumerate(ec):
            val = df[(df["P_baja"] == p) & (df["eps_cond"] == e)]
            if val.empty or pd.isna(val["eta"].iloc[0]):
                texto = "NC"
            else:
                cl = val["clasificacion"].iloc[0]
                texto = "K" if cl == "KALINA" else (
                    "C" if cl == "CORREGIBLE" else cl[:2])
            ax.text(j, i, texto, ha="center", va="center", fontsize=8,
                    color="white" if texto in ("K", "C") else "black",
                    fontweight="bold")
    ax.set_xticks(range(len(ec)))
    ax.set_yticks(range(len(pb)))
    ax.set_xticklabels([f"{e:.2f}" for e in ec])
    ax.set_yticklabels([f"{p:.0f}" for p in pb])
    ax.set_xlabel("Efectividad del condensador ε_cond [-]")
    ax.set_ylabel("Presión baja P_baja [kPa]")
    ax.set_title("Clasificación en el plano P_baja × ε_cond (Fase 2)")
    cbar = fig.colorbar(im, ax=ax, ticks=[0, 1, 2], fraction=0.046)
    cbar.ax.set_yticklabels(["KALINA", "CORREGIBLE", "Otras"])
    fig.tight_layout()
    return fig


def main() -> None:
    FIGURAS.mkdir(parents=True, exist_ok=True)
    for var in ETIQUETAS:
        csv = FASE2 / f"sensibilidad_{var}.csv"
        if not csv.exists():
            print(f"  AVISO: falta {csv.name}, se omite {var}", flush=True)
            continue
        df = pd.read_csv(csv)
        fig = fig_sensibilidad_ofat(df, var)
        out = FIGURAS / f"fase2_sensibilidad_{var}.png"
        fig.savefig(out, dpi=150)
        print(f"  {out.name}: {len(df)} puntos", flush=True)

    csv_malla = FASE2 / "mapa_2d_pbaja_epscond.csv"
    if csv_malla.exists():
        fig = fig_mapa_2d(pd.read_csv(csv_malla))
        out = FIGURAS / "fase2_mapa_2d_pbaja_epscond.png"
        fig.savefig(out, dpi=150)
        print(f"  {out.name}", flush=True)
    else:
        print("  AVISO: falta la malla 2D, se omite el mapa", flush=True)

    leccion = ("El KALINA del ancla se sostiene con O2 comodo (+3.91 K) y S5 "
               "lejos, pero la frontera real del entorno es O1 (q4=0.9013, "
               "margen +0.0013, sin cruzar). La sensibilidad dominante es "
               "eps_cond: por debajo de ~0.93 todo el plano "
               "P_baja×eps_cond cae a CORREGIBLE por O2. En la frontera O1 "
               "el motor real IAPWS es numericamente fragil (no-convergencias "
               "no deterministas, ver spotcheck_motor_real_fase2.json).")
    resumen = {"fase": "2_libre", "clasificacion_ancla": "KALINA",
               "eta_ancla": 0.124296, "leccion_aprendida": leccion}
    with open(FASE2 / "resumen_fase2.json", "w", encoding="utf-8") as fh:
        json.dump(resumen, fh, indent=2, ensure_ascii=False)
    print("resumen_fase2.json guardado")


if __name__ == "__main__":
    main()