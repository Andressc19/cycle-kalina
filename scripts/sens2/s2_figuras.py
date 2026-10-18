# -*- coding: utf-8 -*-
"""Sens2 - s2_figuras: figuras del informe (PNG en docs/figuras_sens2/), paleta apta para daltonismo (Okabe-Ito)."""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
import s2_calc as C  # noqa: E402
from s2_cargar import dataset_dedup  # noqa: E402

OUT = os.path.join(RAIZ, "docs", "figuras_sens2")
COL = ["#0072B2", "#D55E00", "#009E73", "#CC79A7"]
CORTO = {"C1 Husavik": "C1 Húsavík", "C2 ancla A*": "C2 ancla A*", "C3 caliente 150 C": "C3 150 °C", "C4 frio 110 C": "C4 110 °C"}
plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": 0.3, "figure.dpi": 130})


def _guardar(fig, nombre):
    os.makedirs(OUT, exist_ok=True)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, nombre), dpi=130)
    plt.close(fig)
    return nombre


def fig_piso():
    fig, ax = plt.subplots(figsize=(6.5, 4))
    for k, b in enumerate(C.BLOQUES):
        e, c, av, bv = C.malla_clases(b, "B2")
        xs, ys = [], []
        for j, x in enumerate(bv):
            col = np.where(c[:, j] == "K")[0]
            if len(col):
                xs.append(float(x))
                ys.append(float(av[col.min()]))
        ax.plot(xs, ys, "o-", color=COL[k], label=CORTO[b])
    ax.set_xlabel("x_b (-)")
    ax.set_ylabel("Menor P_baja con KALINA en la malla (kPa)")
    ax.set_title("El piso de P_baja sube con la fracción de amoníaco")
    ax.legend()
    return _guardar(fig, "f1_piso_pbaja.png")


def fig_eta_pbaja():
    fig, axs = plt.subplots(2, 2, figsize=(9, 6.5), sharey=False)
    for ax, b in zip(axs.ravel(), C.BLOQUES):
        e, c, av, bv = C.malla_clases(b, "B2")
        cm = plt.cm.viridis(np.linspace(0, 0.9, len(bv)))
        for j, x in enumerate(bv):
            m = np.isfinite(e[:, j])
            if m.sum() >= 2:
                ax.plot(av[m], e[m, j], "o-", ms=3, color=cm[j], label="x_b %g" % x)
        ax.set_title(CORTO[b])
        ax.set_xlabel("P_baja (kPa)")
        ax.set_ylabel("η (%)")
        ax.legend(fontsize=6, ncol=2)
    fig.suptitle("η frente a P_baja por nivel de x_b (solo celdas KALINA)")
    return _guardar(fig, "f2_eta_pbaja.png")


def fig_regenerador():
    o = C.barrido_fuente()
    k = o[o["kalina"]]
    fig, ax = plt.subplots(figsize=(6.5, 4))
    for i, b in enumerate(C.BLOQUES):
        s = k[k["centro"] == b].sort_values("t_c")
        ax.plot(s["t_c"], s["qreg_qi2"], "o-", ms=3, color=COL[i], label=CORTO[b])
    ax.set_xlabel("T_fuente (°C)")
    ax.set_ylabel("Q_reg / Q_i (-)")
    ax.set_title("El regenerador pierde peso al subir la temperatura de la fuente")
    ax.legend()
    return _guardar(fig, "f3_regenerador.png")


def fig_margenes():
    m = C.margenes_ofat()
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
    for ax, b in zip(axs, ["C1 Husavik", "C4 frio 110 C"]):
        s = m[m["bloque"] == b]
        x = np.arange(len(s))
        ax.bar(x - 0.2, s["marg_abajo"], 0.4, color=COL[1], label="hacia abajo")
        ax.bar(x + 0.2, s["marg_arriba"], 0.4, color=COL[0], label="hacia arriba")
        ax.set_xticks(x)
        ax.set_xticklabels(s["variable"], rotation=45, ha="right")
        ax.set_title(CORTO[b])
    axs[0].set_ylabel("Margen (% del rango probado)")
    axs[0].legend()
    fig.suptitle("Cuánto se puede mover cada variable desde el centro KALINA")
    return _guardar(fig, "f4_margenes.png")


def fig_corregibles():
    d = dataset_dedup()
    g = d[d["clasificacion"].isin(["KALINA", "CORREGIBLE"]) & d["eta_pct"].notna()]
    fig, ax = plt.subplots(figsize=(6.5, 4))
    for i, b in enumerate(C.BLOQUES):
        for j, (cl, col) in enumerate((("KALINA", COL[0]), ("CORREGIBLE", COL[1]))):
            v = g[(g["centro"] == b) & (g["clasificacion"] == cl)]["eta_pct"]
            ax.bar(i + (j - 0.5) * 0.38, v.median(), 0.36, color=col, label=cl if i == 0 else None)
    ax.set_xticks(range(len(C.BLOQUES)))
    ax.set_xticklabels([CORTO[b] for b in C.BLOQUES])
    ax.set_ylabel("η mediana (%)")
    ax.set_title("Los CORREGIBLE aparentan más eficiencia porque incumplen la cavitación")
    ax.legend()
    return _guardar(fig, "f5_corregibles.png")


def fig_margen_o2():
    sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))
    d = C.todo()
    k = d[d["kalina"] & d["m_O2"].notna()]
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.hist(k["m_O2"].clip(upper=30), bins=60, color=COL[0])
    for t, c in ((1, COL[1]), (3, COL[2]), (5, COL[3])):
        ax.axvline(t, color=c, ls="--", label="m_O2 = %d K (%.1f %% de los KALINA por debajo)" % (t, 100 * (k["m_O2"] < t).mean()))
    ax.set_xlabel("m_O2 = T_burbuja - T9 (K), recortado en 30 K")
    ax.set_ylabel("Puntos KALINA")
    ax.set_title("Margen de cavitación de los KALINA (el criterio exige m_O2 >= 0)")
    ax.legend(fontsize=8)
    return _guardar(fig, "f6_margen_o2.png")


def fig_incertidumbre():
    r = pd.read_csv(os.path.join(RAIZ, "resultados", "2026-10-17_sens2_U1", "u1_resumen.csv"))
    esc = [("U1Ap", "A (n = 96)"), ("U1B", "B (doble)"), ("U1C", "A sin perturbar ε_cond")]
    fig, ax = plt.subplots(figsize=(7.5, 4))
    for j, (e, nom) in enumerate(esc):
        s = r[r["escenario"] == e].set_index("centro")
        if not len(s):
            continue
        x = np.arange(4) + (j - 1) * 0.27
        p = [s.loc[c, "p_kalina"] for c in ("C1", "C2", "C3", "C4")]
        err = [[s.loc[c, "p_kalina"] - s.loc[c, "p_lo"] for c in ("C1", "C2", "C3", "C4")],
               [s.loc[c, "p_hi"] - s.loc[c, "p_kalina"] for c in ("C1", "C2", "C3", "C4")]]
        ax.bar(x, p, 0.25, yerr=err, capsize=3, color=COL[j], label=nom)
    ax.set_xticks(range(4))
    ax.set_xticklabels(["C1 Húsavík", "C2 ancla A*", "C3 150 °C", "C4 110 °C"])
    ax.set_ylabel("P(KALINA)")
    ax.set_ylim(0, 1.05)
    ax.set_title("Probabilidad de seguir siendo KALINA al perturbar las 10 variables (IC 95 %)")
    ax.legend(fontsize=8)
    return _guardar(fig, "f7_incertidumbre.png")


def fig_scan():
    s = pd.read_csv(os.path.join(RAIZ, "resultados", "2026-10-17_sens2_U1", "u1_scan_eps_cond.csv"))
    fig, ax = plt.subplots(figsize=(6.5, 4))
    for i, c in enumerate(("C1", "C2", "C3", "C4")):
        g = s[(s["centro"] == c) & s["m_O2"].notna()].sort_values("eps_cond")
        ax.plot(g["eps_cond"], g["m_O2"], "o-", ms=3, color=COL[i], label=c)
    ax.axhline(0, color="k", lw=1)
    ax.set_xlabel("ε_cond (-)")
    ax.set_ylabel("m_O2 (K)")
    ax.set_title("Margen de cavitación frente a la efectividad del condensador")
    ax.legend()
    return _guardar(fig, "f8_scan_epscond.png")


def main(todas=True):
    out = [fig_piso(), fig_eta_pbaja(), fig_regenerador(), fig_margenes(), fig_corregibles(), fig_margen_o2()]
    if todas:
        out += [fig_incertidumbre(), fig_scan()]
    print("figuras:", out)


if __name__ == "__main__":
    main(todas=len(sys.argv) < 2 or sys.argv[1] != "sin_u1")
