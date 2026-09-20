"""Fase 3 (Husavik) — figuras del barrido de sensibilidad FINAL.

Tarea 2026-09-20-fase3-sensibilidad-final. Lee los CSVs generados por
sensibilidad_fase3_ofat.py / _2d.py y produce:
  - fase3_sensibilidad_<var>.png (5): eta vs variable, puntos coloreados por
    clasificacion (KALINA=verde #2ca02c, CORREGIBLE=ambar #ff7f0e, otra=rojo
    #d62728) + linea de tendencia sobre los convergentes.
  - fase3_mapa_2d_pbaja_epsreg.png: heatmap categorico de la clasificacion en
    el plano P_baja x eps_reg (frontera KALINA/CORREGIBLE visible).

Estilo de src/plots.py: matplotlib.figure.Figure directa (sin pyplot global),
titulo y ejes en espanol, grid alpha 0.3, savefig dpi=150.
NO modifica codigo de produccion.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import pandas as pd
from matplotlib.colors import ListedColormap
from matplotlib.figure import Figure

_RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_RAIZ))

RESULTADOS = _RAIZ / "resultados" / "barridos_2026-09-19" / "fase3_real"
FIGURAS = _RAIZ / "resultados" / "barridos_2026-09-19" / "figuras"
DPI = 150

COLORES = {"KALINA": "#2ca02c", "CORREGIBLE": "#ff7f0e"}
TITULOS = {"P_baja": "P_baja [kPa]", "eps_cond": "eps_cond [-]",
           "eps_reg": "eps_reg [-]", "x_b": "x_b (fracción NH3) [-]",
           "eta_t": "η_turbina [-]"}
ORDEN_MAPA = "KALINA", "CORREGIBLE", "INVIABLE", "DEGENERADO", \
             "NO_CONVERGIO", "VALIDO_ADVERTENCIA"


def figura_sensibilidad(df: pd.DataFrame, var: str) -> Figure:
    """eta vs variable, coloreado por clasificacion (convergentes)."""
    fig = Figure(figsize=(8, 5))
    ax = fig.subplots()
    conv = df[df["convergio"] == True].sort_values(var)  # noqa: E712
    ax.plot(conv[var], conv["eta"], color="0.55", linewidth=1.0, alpha=0.5,
            zorder=1)
    presentes = [c for c in ORDEN_MAPA if c in set(df["clasificacion"])]
    for c in presentes:
        grupo = df[df["clasificacion"] == c]
        grupo = grupo[grupo["convergio"] == True]  # noqa: E712
        ax.scatter(grupo[var], grupo["eta"], color=COLORES.get(c, "#d62728"),
                   label=c, s=48, zorder=3, edgecolors="white", linewidths=0.6)
    ax.set_xlabel(TITULOS[var])
    ax.set_ylabel("η [-]")
    ax.set_title(f"Sensibilidad de η vs {TITULOS[var]} "
                 f"(ancla Húsavík, TeqpAdapter)")
    ax.grid(alpha=0.3)
    ax.legend(title="Clasificación")
    fig.tight_layout()
    return fig


def figura_mapa_2d(df: pd.DataFrame) -> Figure:
    """Heatmap categorico de clasificacion en P_baja x eps_reg (6x6)."""
    codigo = {"KALINA": 2.0, "CORREGIBLE": 1.0}
    pbs = sorted(df["P_baja"].unique())
    epr = sorted(df["eps_reg"].unique())
    z = [[codigo.get(df[(df["P_baja"] == pb) & (df["eps_reg"] == er)]
                     ["clasificacion"].iloc[0], 0.0)
          for er in epr] for pb in pbs]
    pbs_e = list(pbs) + [pbs[-1] + (pbs[1] - pbs[0])]
    epr_e = list(epr) + [epr[-1] + (epr[1] - epr[0])]

    fig = Figure(figsize=(8.5, 6.5))
    ax = fig.subplots()
    m = ax.pcolormesh(epr_e, pbs_e, z, cmap=ListedColormap(
        ["#d62728", "#ff7f0e", "#2ca02c"]), shading="flat")
    for i, pb in enumerate(pbs):
        for j, er in enumerate(epr):
            fila = df[(df["P_baja"] == pb) & (df["eps_reg"] == er)].iloc[0]
            texto = f"{fila['eta']:.4f}" if fila["convergio"] else "NC"
            ax.text(er + (epr[1] - epr[0]) / 2, pb, texto, ha="center",
                    va="center", fontsize=8, color="black")
    cbar = fig.colorbar(m, ax=ax, ticks=[1 / 3, 1.0, 5 / 3])
    cbar.ax.set_yticklabels(["otra", "CORREGIBLE", "KALINA"])
    cbar.set_label("Clasificación")
    ax.set_xlabel("eps_reg [-]")
    ax.set_ylabel("P_baja [kPa]")
    ax.set_title("Mapa 2D P_baja × eps_reg — clasificación (ancla Húsavík)")
    fig.tight_layout()
    return fig


def main() -> None:
    FIGURAS.mkdir(parents=True, exist_ok=True)
    for var in ("P_baja", "eps_cond", "eps_reg", "x_b", "eta_t"):
        df = pd.read_csv(RESULTADOS / f"sensibilidad_{var}.csv")
        fig = figura_sensibilidad(df, var)
        ruta = FIGURAS / f"fase3_sensibilidad_{var}.png"
        fig.savefig(ruta, dpi=DPI)
        print(f"  guardado {ruta}", flush=True)

    df2d = pd.read_csv(RESULTADOS / "mapa_2d_pbaja_epsreg.csv")
    fig = figura_mapa_2d(df2d)
    ruta = FIGURAS / "fase3_mapa_2d_pbaja_epsreg.png"
    fig.savefig(ruta, dpi=DPI)
    print(f"  guardado {ruta}", flush=True)
    print("Figuras generadas sin error.", flush=True)


if __name__ == "__main__":
    main()