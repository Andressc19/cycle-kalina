"""Mapa 2D alternativo (opcion 2 discutida con el usuario): heatmap CONTINUO
del margen del criterio O2 (T_sat_L - T9_amb) en vez de un mosaico categorico
de clasificacion, con la linea de nivel margen=0 (la frontera KALINA/CORREGIBLE
exacta) superpuesta. Reusa los CSV ya generados por las tareas de barrido
final de Fase 2 y Fase 3 -- no vuelve a resolver ningun punto del ciclo.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.figure import Figure

RAIZ = Path(__file__).resolve().parents[2]
RES = RAIZ / "resultados" / "barridos_2026-09-19"
FIGURAS = RES / "figuras"


def _grafico_margen(df: pd.DataFrame, col_x: str, col_y: str, col_margen: str,
                    titulo: str, etiqueta_x: str, etiqueta_y: str,
                    salida: Path) -> None:
    piv = df.pivot(index=col_y, columns=col_x, values=col_margen)
    x = piv.columns.to_numpy(dtype=float)
    y = piv.index.to_numpy(dtype=float)
    z = piv.to_numpy(dtype=float)

    fig = Figure(figsize=(7.5, 5.5))
    ax = fig.subplots()
    limite = float(np.nanmax(np.abs(z)))
    malla = ax.pcolormesh(x, y, z, cmap="RdYlGn", vmin=-limite, vmax=limite,
                          shading="nearest")
    cbar = fig.colorbar(malla, ax=ax)
    cbar.set_label("Margen O2 = T_sat_L - T9_amb [K] (>0 => KALINA)")
    try:
        cs = ax.contour(x, y, z, levels=[0.0], colors="black", linewidths=2.0)
        ax.clabel(cs, fmt="frontera (margen=0)", fontsize=8)
    except ValueError:
        pass  # todo el plano de un solo signo: no hay frontera que dibujar
    ax.set_title(titulo)
    ax.set_xlabel(etiqueta_x)
    ax.set_ylabel(etiqueta_y)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(salida, dpi=150)
    print(f"  guardado {salida.name}")


def main() -> None:
    df2 = pd.read_csv(RES / "fase2_libre" / "mapa_2d_pbaja_epscond.csv")
    _grafico_margen(
        df2, "P_baja", "eps_cond", "O2_margen",
        "Fase 2 (libre) — margen del criterio O2 en el plano P_baja x eps_cond",
        "P_baja [kPa]", "eps_cond [-]",
        FIGURAS / "fase2_mapa_2d_pbaja_epscond_margen.png")

    df3 = pd.read_csv(RES / "fase3_real" / "mapa_2d_pbaja_epsreg.csv")
    _grafico_margen(
        df3, "P_baja", "eps_reg", "margen_O2",
        "Fase 3 (Húsavík) — margen del criterio O2 en el plano P_baja x eps_reg",
        "P_baja [kPa]", "eps_reg [-]",
        FIGURAS / "fase3_mapa_2d_pbaja_epsreg_margen.png")


if __name__ == "__main__":
    main()
