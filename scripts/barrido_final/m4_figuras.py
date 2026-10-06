"""M4 — las cuatro figuras de TASK_CONTEXT final_M4 (§Figuras).

`m4_cdf_kalina.png` (CDF de B y de B̄ por variable, con el KS en el título),
`m4_prcc_eta.png` (barras de PRCC sobre η con su IC95 %), `m4_rsa_ks.png`
(barras de KS por variable para la separación KALINA) y `m4_cart.png` (el
árbol). Se re-ejecutan sobre los CSV del análisis, sin recalcular el ciclo.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from sklearn.tree import plot_tree  # noqa: E402

from m4_datos import OUT, VARS10, VARS13  # noqa: E402
from m4_rsa import marcador  # noqa: E402

CB, CBAR = "#1f77b4", "#d62728"
CART_K, CART_N = "#2ca02c", "#d62728"


def _ecdf(ax, vals, color, label):
    x = sorted(vals)
    ax.step(x, [i / len(x) for i in range(1, len(x) + 1)], where="post",
            color=color, label=label, lw=1.3)


def cdf_kalina(filas: list, rsa: list) -> None:
    ks = {r["variable"]: r["KS"] for r in rsa if r["separacion"] == "KALINA"}
    fig, axs = plt.subplots(4, 4, figsize=(17, 14))
    for ax, v in zip(axs.ravel(), VARS13):
        b = [f[v] for f in filas if marcador(f, "KALINA") is True]
        bb = [f[v] for f in filas if marcador(f, "KALINA") is False]
        if b:
            _ecdf(ax, b, CB, f"B (KALINA, n={len(b)})")
        if bb:
            _ecdf(ax, bb, CBAR, f"B-bar (resto, n={len(bb)})")
        k = ks.get(v)
        ax.set_title(f"{v} — KS = {'n/d' if k is None else format(k, '.3f')}",
                     fontsize=10)
        ax.set_xlabel(v, fontsize=9)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7)
    for ax in axs.ravel()[len(VARS13):]:
        ax.axis("off")
    fig.suptitle("M4 — CDF de KALINA vs resto (RSA), con KS por variable", y=0.999)
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    fig.savefig(OUT / "m4_cdf_kalina.png", dpi=150)
    plt.close(fig)
    print("m4_cdf_kalina.png", flush=True)


def prcc_eta(prcc: list) -> None:
    d = [r for r in prcc if r["salida"] == "eta"]
    d = sorted([r for r in d if r["prcc"] is not None], key=lambda r: -abs(r["prcc"]))
    fig, ax = plt.subplots(figsize=(9, 4.8))
    x = list(range(len(d)))
    ax.bar(x, [r["prcc"] for r in d], color="#1f77b4", zorder=2)
    con_ic = [(i, r) for i, r in enumerate(d) if r["ic_lo"] is not None]
    if con_ic:
        ax.errorbar([i for i, _ in con_ic], [r["prcc"] for _, r in con_ic],
                    yerr=[[r["prcc"] - r["ic_lo"] for _, r in con_ic],
                          [r["ic_hi"] - r["prcc"] for _, r in con_ic]],
                    fmt="none", ecolor="#333333", capsize=3, zorder=3)
    ax.axhline(0, color="#333333", lw=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels([r["variable"] for r in d], rotation=30, ha="right")
    ax.set_ylabel("PRCC sobre η (−)")
    ax.set_title("M4 — PRCC sobre η con IC95 % (genuinos con W_net > 0)")
    ax.grid(axis="y", alpha=0.3, zorder=0)
    fig.tight_layout()
    fig.savefig(OUT / "m4_prcc_eta.png", dpi=150)
    plt.close(fig)
    print("m4_prcc_eta.png", flush=True)


def rsa_ks(rsa: list) -> None:
    d = sorted([r for r in rsa if r["separacion"] == "KALINA"
                and r["KS"] is not None], key=lambda r: -r["KS"])
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.bar([r["variable"] for r in d], [r["KS"] for r in d], color="#d62728")
    for i, r in enumerate(d):
        ax.text(i, r["KS"], f'{r["KS"]:.3f}', ha="center", va="bottom", fontsize=8)
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    ax.set_ylabel("KS (−)")
    ax.set_title("M4 — RSA: KS por variable, separación KALINA vs resto")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "m4_rsa_ks.png", dpi=150)
    plt.close(fig)
    print("m4_rsa_ks.png", flush=True)


def arbol_fig(cart: dict) -> None:
    if not cart.get("ok"):
        print("m4_cart.png: no se dibuja (sin las dos clases)", flush=True)
        return
    tree, X, y = cart["tree"], cart["X"], cart["y"]
    fig, ax = plt.subplots(figsize=(20, 10))
    plot_tree(tree, feature_names=list(VARS10), class_names=["no", "KALINA"],
              filled=True, rounded=True, fontsize=7, ax=ax, impurity=True)
    fig.suptitle("M4 — árbol CART: KALINA vs no KALINA (max_depth=4, hoja>=5)")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(OUT / "m4_cart.png", dpi=150)
    plt.close(fig)
    print("m4_cart.png", flush=True)


def figuras(filas: list, rsa: list, prcc: list, cart: dict) -> None:
    """Las cuatro figuras de TASK_CONTEXT final_M4."""
    cdf_kalina(filas, rsa)
    prcc_eta(prcc)
    rsa_ks(rsa)
    arbol_fig(cart)
