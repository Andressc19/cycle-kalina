"""M9 — paso 4: `m9_escalera.png` y `m9_plano_presiones.png`.

La escalera dibuja cada conjunto evaluado como un nodo (x = orden de la
escalera, y = D mínima) con su n KALINA / n KALINA confiable, y resalta el
camino elegido. El plano de presiones pone los KALINA de M4b en gris, los KALINA
de M9 coloreados por escenario, el punto del profesor (3000/400) con una X y
Húsavík (3300/690) con una estrella. Todo se lee de los CSV.
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

import m9_datos as m9  # noqa: E402

M4B = _RAIZ / "resultados" / "2026-10-07_final_M4b" / "m4b_lhs.csv"
COL = {"KALINA": "#2ca02c", "CORREGIBLE": "#ff7f0e", "INVIABLE": "#e8d500"}
GRIS = "#9e9e9e"


def escalera() -> None:
    """Diagrama de la escalera con el camino elegido resaltado."""
    rows = m9.leer(m9.OUT / "m9_escalera.csv")
    rows.sort(key=lambda r: (r["ronda"], r["conservados"]))
    x = np.arange(len(rows))
    fig, ax = plt.subplots(figsize=(max(9, 0.55 * len(rows)), 5.4))
    for i, r in enumerate(rows):
        if r["D_min"] is None:
            continue
        k = (r["n_kalina"] or 0) > 0
        ax.scatter(i, r["D_min"], s=110 if r["elegido"] else 45,
                   marker="*" if r["elegido"] else "o",
                   c=COL["KALINA"] if k else GRIS,
                   edgecolors="black" if r["elegido"] else "none",
                   zorder=3, alpha=0.95)
        ax.annotate(f'{r["n_kalina"] or 0}/{r["n_kalina_confiable"] or 0}',
                    (i, r["D_min"]), textcoords="offset points", xytext=(0, 8),
                    ha="center", fontsize=7)
    cam = [(i, r["D_min"]) for i, r in enumerate(rows)
           if r["elegido"] and r["D_min"] is not None]
    if cam:
        ax.plot([c[0] for c in cam], [c[1] for c in cam], "-", color="#d62728",
                lw=1.8, zorder=2, label="camino elegido")
    ax.set_yscale("symlog", linthresh=0.1)
    ax.set_xticks(x)
    ax.set_xticklabels([f'{int(r["ronda"])}:{r["conservados"]}' for r in rows],
                       rotation=60, ha="right", fontsize=7)
    ax.set_ylabel("D mínima (violación normalizada)")
    ax.set_title("M9 — escalera de conservación (n KALINA / n KALINA confiable)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(m9.OUT / "m9_escalera.png", dpi=150)
    plt.close(fig)
    print("m9_escalera.png", flush=True)


def _puntos_m9() -> dict:
    """`{escenario: [(P_baja, P_alta)]}` de los KALINA de paso 1, paso 2 y Húsavík."""
    d: dict = {}

    def add(key, rows, x, y):
        for f in rows:
            if m9.es_kalina(f) and f.get(x) is not None and f.get(y) is not None:
                d.setdefault(key, []).append((f[x], f[y]))
    add("paso1", m9.leer(m9.OUT / "m9_paso1.csv"), "P_baja", "P_alta")
    add("paso2", m9.leer(m9.OUT / "m9_paso2.csv"), "P_baja", "P_alta")
    add("Húsavík", m9.leer(m9.OUT / "m9_husavik.csv"), "P_baja_test", "P_alta")
    return d


def plano_presiones() -> None:
    """P_alta contra P_baja: M4b gris, M9 por escenario, profesor X, Húsavík ★."""
    fig, ax = plt.subplots(figsize=(9.4, 6.4))
    if M4B.exists():
        gray = [f for f in m9.leer(M4B) if m9.es_kalina(f)]
        ax.scatter([f["P_baja"] for f in gray], [f["P_alta"] for f in gray],
                   s=17, c=GRIS, alpha=0.75, edgecolors="none",
                   label=f"M4b KALINA (n={len(gray)})")
    col = plt.get_cmap("tab20")
    for i, (k, pts) in enumerate(sorted(_puntos_m9().items())):
        ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=30,
                   c=[col(i % 20)], alpha=0.9, edgecolors="none",
                   label=f"{k} (n={len(pts)})")
    ax.scatter([400], [3000], marker="X", s=170, c="black", zorder=5,
               label="profesor (3000/400)")
    ax.scatter([690], [3300], marker="*", s=220, c="#d62728", zorder=5,
               label="Húsavík (3300/690)")
    xs = np.linspace(300, 1500, 50)
    for r in (2, 3, 4, 5):
        ax.plot(xs, r * xs, "--", lw=0.9, color="#555555")
        ax.text(1450, min(r * 1450, 5000), f" rP={r}", fontsize=8, va="top")
    ax.set_xlim(300, 1500)
    ax.set_ylim(1800, 5200)
    ax.set_xlabel("P_baja (kPa)")
    ax.set_ylabel("P_alta (kPa)")
    ax.set_title("M9 — plano de presiones: KALINA de M4b (gris) y de M9 por escenario")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7, loc="upper left", ncol=2)
    fig.tight_layout()
    fig.savefig(m9.OUT / "m9_plano_presiones.png", dpi=150)
    plt.close(fig)
    print("m9_plano_presiones.png", flush=True)


def main() -> None:
    escalera()
    plano_presiones()


if __name__ == "__main__":
    main()
