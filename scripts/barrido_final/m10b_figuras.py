"""M10b — `m10b_xb.png`: η contra x_b y mapa de clase x_b × P_baja.

Une las dos campañas: M10 (OFAT x_b 0.60–0.95; malla 0.70–0.91 × 500–1200 kPa)
y M10b (OFAT x_b 0.30–0.70; malla 0.30–0.70 × 200–700 kPa). Todo se lee de los
CSV; el marcador distingue campaña y el color, la clase. La etiqueta "x_b bajo"
(< 0.55) se marca con una línea vertical azul.
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

import m10_datos as d10  # noqa: E402
import m10b_datos as d  # noqa: E402

COL = {"KALINA": "#2ca02c", "CORREGIBLE": "#ff7f0e", "INVIABLE": "#e8d500",
       "NO_CONVERGIO": "#9e9e9e"}
MARCA = {"M10b": "o", "M10": "^"}


def _ofat() -> list:
    """(x_b, η, clase, campaña) del OFAT de x_b de M10b y de M10."""
    out = [(f["x_b"], f.get("eta"), f.get("clasificacion"), "M10b")
           for f in d10.leer(d.OUT / "m10b_ofat_xb.csv")]
    out += [(f["x_b"], f.get("eta"), f.get("clasificacion"), "M10")
            for f in d10.leer(d.M10_OUT / "m10_ofat.csv")
            if f.get("variable") == "x_b"]
    return out


def _malla() -> list:
    """(x_b, P_baja, clase, campaña) de las dos mallas."""
    out = [(f["x_b"], f["P_baja"], f.get("clasificacion"), "M10b")
           for f in d10.leer(d.OUT / "m10b_malla_xb_pbaja.csv")]
    out += [(f["x_b"], f["P_baja"], f.get("clasificacion"), "M10")
            for f in d10.leer(d.M10_OUT / "m10_malla_xb_pbaja.csv")]
    return out


def _marca_bajo(ax) -> None:
    ax.axvline(d.XB_BAJO, color="#1f77b4", lw=1.3, ls="--", zorder=1)


def figura() -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.5, 6.4))
    of, ma = _ofat(), _malla()
    for camp, mk in MARCA.items():
        for clase, col in COL.items():
            s = [(x, y) for x, y, c, cp in of
                 if cp == camp and c == clase and y is not None]
            if s:
                ax1.scatter([a for a, _b in s], [b for _a, b in s], s=46, c=col,
                            marker=mk, edgecolors="black", linewidths=0.4,
                            zorder=3, label=f"{clase} ({camp})")
    _marca_bajo(ax1)
    ax1.text(d.XB_BAJO + 0.005, 0.55, "x_b bajo (<0.55)\nfuera de lo habitual",
             color="#1f77b4", fontsize=8, va="center")
    ax1.set_xlabel("x_b (fracción NH3)")
    ax1.set_ylabel("η")
    ax1.set_title("η contra x_b — M10 (0.60–0.95) + M10b (0.30–0.70)")
    ax1.grid(alpha=0.3)
    ax1.legend(fontsize=7, ncol=2, loc="best")
    for camp, mk in MARCA.items():
        for clase, col in COL.items():
            s = [(x, y) for x, y, c, cp in ma if cp == camp and c == clase]
            if s:
                ax2.scatter([a for a, _b in s], [b for _a, b in s], s=58, c=col,
                            marker=mk, edgecolors="black", linewidths=0.4,
                            zorder=3, label=f"{clase} ({camp})")
    _marca_bajo(ax2)
    ax2.set_xlabel("x_b (fracción NH3)")
    ax2.set_ylabel("P_baja (kPa)")
    ax2.set_title("Clase en la malla x_b × P_baja — M10b + M10")
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=7, ncol=2, loc="best")
    fig.tight_layout()
    fig.savefig(d.OUT / "m10b_xb.png", dpi=150)
    plt.close(fig)
    print("m10b_xb.png", flush=True)


def main() -> None:
    d.OUT.mkdir(parents=True, exist_ok=True)
    figura()


if __name__ == "__main__":
    main()
