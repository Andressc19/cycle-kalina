"""M4b — las dos figuras de presiones de TASK_CONTEXT final_M4b §Diseño (a) y (f).

`m4b_plano_presiones.png`: dispersión de P_baja (x) contra P_alta (y), cada
punto con el color de su clase (KALINA verde, CORREGIBLE naranja, INVIABLE
amarillo y no genuino gris) y líneas de rP constante en 2, 3, 4 y 5.
`m4b_hist_dP_rP.png`: histogramas de dP y de rP, KALINA contra no KALINA (la
misma separación "KALINA vs el resto" que usa el RSA de M4).
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from m4b_datos import OUT  # noqa: E402

COLORES = {"KALINA": "#2ca02c", "CORREGIBLE": "#ff7f0e", "INVIABLE": "#e8d500"}
GRIS = "#9e9e9e"
RP_LIN = (2, 3, 4, 5)
CLASES_FIJAS = ("KALINA", "CORREGIBLE", "INVIABLE", "no genuino")


def plano_presiones(filas: list) -> None:
    """(a) P_baja (x) contra P_alta (y) coloreado por clase, con rP = 2..5."""
    fig, ax = plt.subplots(figsize=(9, 6.2))
    vistos = set()
    for f in filas:
        if f["P_baja"] is None or f["P_alta"] is None:
            continue
        cls = (f["clasificacion"] if f["clasificacion"] in COLORES
               else "no genuino")
        ax.scatter(f["P_baja"], f["P_alta"], s=16,
                   c=COLORES.get(cls, GRIS), alpha=0.85, edgecolors="none",
                   label=cls if cls not in vistos else None)
        vistos.add(cls)
    x0, x1, y1 = 300.0, 1500.0, 5000.0
    for r in RP_LIN:
        xs = np.array([x0, min(x1, y1 / r)])
        ax.plot(xs, r * xs, "--", lw=1.0, color="#333333")
        ax.text(xs[-1] * 0.99, r * xs[-1], f" rP={r}", fontsize=8,
                color="#333333", ha="right", va="bottom")
    ax.set_xlim(x0, x1)
    ax.set_ylim(1800.0, 5200.0)
    ax.set_xlabel("P_baja (kPa)")
    ax.set_ylabel("P_alta (kPa)")
    ax.set_title("M4b — plano de presiones: 500 puntos, color = clase, "
                 "líneas = rP constante")
    ax.grid(alpha=0.3)
    handles = [plt.Line2D([], [], marker="o", ls="", color=COLORES.get(c, GRIS),
                          label=c) for c in CLASES_FIJAS if c in vistos]
    ax.legend(handles=handles, fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "m4b_plano_presiones.png", dpi=150)
    plt.close(fig)
    print("m4b_plano_presiones.png", flush=True)


def hist_dP_rP(filas: list) -> None:
    """(f) histogramas de dP y de rP: KALINA contra no KALINA."""
    kal = [f for f in filas if f["clasificacion"] == "KALINA"]
    nog = [f for f in filas if f["clasificacion"] != "KALINA"]
    fig, axs = plt.subplots(1, 2, figsize=(12.5, 4.6))
    for ax, v in zip(axs, ("dP", "rP")):
        a = [f[v] for f in kal if f.get(v) is not None]
        b = [f[v] for f in nog if f.get(v) is not None]
        todo = a + b
        bins = np.linspace(min(todo), max(todo), 31) if len(set(todo)) > 1 else 20
        ax.hist(b, bins=bins, alpha=0.65, color=GRIS,
                label=f"no KALINA (n={len(b)})")
        ax.hist(a, bins=bins, alpha=0.65, color="#2ca02c",
                label=f"KALINA (n={len(a)})")
        ax.set_xlabel(f"{v} (kPa)" if v == "dP" else f"{v} (−)")
        ax.set_ylabel("número de puntos")
        ax.set_title(f"M4b — histograma de {v}: KALINA contra no KALINA")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "m4b_hist_dP_rP.png", dpi=150)
    plt.close(fig)
    print("m4b_hist_dP_rP.png", flush=True)
