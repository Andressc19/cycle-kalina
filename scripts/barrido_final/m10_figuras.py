"""M10 — Parte C: `m10_xb_pbaja.png` y `m10_ofat.png`.

El mapa de B2 pone x_b contra P_baja, colorea por clase y superpone la isolínea
de η (máscara: solo donde el punto es KALINA). El panel de B1 son 2 × 5 recuadros
de η contra el valor, coloreados por clase, con una línea vertical en el valor
del ancla. Todo se lee de los CSV.
"""
from __future__ import annotations

import sys  # noqa: E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import m10_datos as d  # noqa: E402

COL = {"KALINA": "#2ca02c", "CORREGIBLE": "#ff7f0e", "INVIABLE": "#e8d500",
       "NO_CONVERGIO": "#9e9e9e"}


def _c(f) -> str:
    return COL.get(f.get("clasificacion"), "#9e9e9e")


def malla_xb_pbaja() -> None:
    """Mapa de clase de B2 con la isolínea de η sobre los KALINA."""
    filas = d.leer(d.OUT / "m10_malla_xb_pbaja.csv")
    fig, ax = plt.subplots(figsize=(8.4, 6.2))
    for clase, col in COL.items():
        sub = [f for f in filas if f.get("clasificacion") == clase]
        if sub:
            ax.scatter([f["x_b"] for f in sub], [f["P_baja"] for f in sub],
                       s=70, c=col, edgecolors="black", linewidths=0.4,
                       zorder=3, label=f"{clase} (n={len(sub)})")
    xb = sorted({f["x_b"] for f in filas})
    pb = sorted({f["P_baja"] for f in filas})
    Z = np.full((len(pb), len(xb)), np.nan)
    for f in filas:
        if d.es_kalina(f) and f.get("eta") is not None:
            Z[pb.index(f["P_baja"]), xb.index(f["x_b"])] = f["eta"]
    if np.isfinite(Z).sum() >= 4:
        X, Y = np.meshgrid(xb, pb)
        cs = ax.contour(X, Y, np.ma.masked_invalid(Z), levels=6,
                        colors="black", linewidths=0.7, alpha=0.8)
        ax.clabel(cs, inline=True, fontsize=7, fmt="%.3f")
    ax.set_xlabel("x_b (fracción NH3)")
    ax.set_ylabel("P_baja (kPa)")
    ax.set_title("M10-B2 — clase en la malla x_b × P_baja (isolíneas de η)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(d.OUT / "m10_xb_pbaja.png", dpi=150)
    plt.close(fig)
    print("m10_xb_pbaja.png", flush=True)


def ofat() -> None:
    """2 × 5 paneles de η contra el valor, por clase, con el ancla marcada."""
    filas = d.leer(d.OUT / "m10_ofat.csv")
    fig, axes = plt.subplots(2, 5, figsize=(18, 7.4))
    for ax, (var, _lo, _hi) in zip(axes.ravel(), d.OFAT):
        sub = sorted((f for f in filas if f["variable"] == var),
                     key=lambda f: f["valor"])
        for clase, col in COL.items():
            s = [f for f in sub if f.get("clasificacion") == clase
                 and f.get("eta") is not None]
            if s:
                ax.scatter([f["valor"] for f in s], [f["eta"] for f in s],
                           s=26, c=col, edgecolors="black", linewidths=0.3,
                           zorder=3, label=clase if var == d.OFAT[0][0] else None)
        ax.axvline(d.ANCLA[var], color="#d62728", lw=1.2, ls="--",
                   label="ancla" if var == d.OFAT[0][0] else None)
        ax.set_title(var, fontsize=10)
        ax.set_xlabel(f"{var} (valor)")
        ax.set_ylabel("η")
        ax.grid(alpha=0.3)
    axes.ravel()[0].legend(fontsize=7)
    fig.suptitle("M10-B1 — η contra cada variable (ancla = línea roja)", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(d.OUT / "m10_ofat.png", dpi=150)
    plt.close(fig)
    print("m10_ofat.png", flush=True)


def main() -> None:
    malla_xb_pbaja()
    ofat()


if __name__ == "__main__":
    main()
