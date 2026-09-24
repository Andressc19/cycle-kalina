"""Grafica validacion por tendencias v2 - KCS11 (tarea 2026-09-24-grafica-tendencias).
Solo lee CSVs (no recalcula el ciclo): hace comparacion_tendencias_v2.png (4 paneles 2x2) e imprime n=23 y conteos por panel."""
from __future__ import annotations
from pathlib import Path
import csv, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = Path(__file__).resolve().parents[1]
OUT = R / "resultados" / "2026-09-24_validacion_tendencias"
EXT = R / "resultados" / "2026-09-24_embaye_vectorial"
PNG = OUT / "comparacion_tendencias_v2.png"
COLOR = {"Fig7_0p55": "#1f77b4", "Fig7_0p66": "#d62728", "Fig3_T333": "#ff7f0e", "Fig3_T373": "#2ca02c", "Fig3_T423": "#9467bd", "Fig2_10bar": "#8c564b", "Fig5_T423": "#e377c2", "Fig5_T463": "#17becf"}
NOM = {"Fig7_0p55": "Fig7 x_b=0.55", "Fig7_0p66": "Fig7 x_b=0.66", "Fig3_T333": "Fig3 15 bar, 333 K", "Fig3_T373": "Fig3 15 bar, 373 K", "Fig3_T423": "Fig3 15 bar, 423 K", "Fig2_10bar": "Fig2 10 bar, 373 K", "Fig5_T423": "Fig5 32 bar, 423 K", "Fig5_T463": "Fig5 32 bar, 463 K"}


def leer(ruta):
    return list(csv.DictReader(open(ruta, newline="", encoding="utf-8")))


def serie(f):
    s = f["serie"]
    if s.startswith("Fig7"):
        return "Fig7_0p55" if f["x_b"] == "0.55" else "Fig7_0p66"
    if s == "Fig2_10bar":
        return "Fig2_10bar"
    p = "Fig3" if s == "Fig3_15bar" else "Fig5"
    return f"{p}_T{int(round(float(f['T_fuente_K'])))}"


def papel(xb, fig, Pb, Ts):
    return [(float(r["x_b_masica"]), float(r["eta_pct"])) for r in xb
            if r["figura"] == fig and abs(float(r["P_evap_bar"]) - Pb) < 1e-6
            and abs(float(r["T_fuente_K"]) - Ts) < 1e-6]


def panel_fig7(ax, mod, f7, c):
    c["paper"] = 0
    for k in ("Fig7_0p55", "Fig7_0p66"):
        crv = "KCS11(Con.=0.55)" if k.endswith("0p55") else "KCS11(Con.=0.66)"
        q = [(float(r["P_evap_bar"]), float(r["eta_pct"])) for r in f7 if r["curva"] == crv]
        ax.plot(*zip(*q), color=COLOR[k], lw=1.6, label=f"Paper {NOM[k]}")
        pts = [f for f in mod if f["serie"].startswith("Fig7") and serie(f) == k
               and f["convergio"] == "True" and f["motor"] == "teqp"]
        ax.scatter([float(f["P_alta_kPa"]) / 100 for f in pts],
                   [float(f["eta_modelo_pct"]) for f in pts], s=40, color=COLOR[k],
                   edgecolor="k", lw=0.4, zorder=3, label=f"Modelo {NOM[k]}")
        c["paper"] += 1
        c[k] = len(pts)
    ctrl = [f for f in mod if f["motor"] == "AmmoniaWater" and f["convergio"] == "True"]
    ax.scatter([float(f["P_alta_kPa"]) / 100 for f in ctrl],
               [float(f["eta_modelo_pct"]) for f in ctrl], marker="x", color="k",
               s=60, zorder=4, label="control motor iapws")
    c["control"] = len(ctrl)
    ax.legend(fontsize=7.5, loc="best")
    ax.set(xlabel="P_alta [bar]", ylabel="η [%]", title="Fig. 7 — η vs P_alta [bar], T_fuente=373 K")


def panel_fig3(ax, mod, xb, c):
    c["paper"] = 0
    for k in ("Fig3_T333", "Fig3_T373", "Fig3_T423"):
        q = papel(xb, "Fig3", 15.0, float(k.split("_T")[1]))
        ax.plot(*zip(*q), color=COLOR[k], lw=1.6, label=f"Paper {NOM[k]}")
        c["paper"] += 1
    for f in mod:
        if f["serie"] != "Fig3_15bar" or f["convergio"] != "True" or f["motor"] != "teqp":
            continue
        hueco = f["titulo_salida_turbina"] == ""
        k = serie(f)
        ax.scatter(float(f["x_b"]), float(f["eta_modelo_pct"]), s=42,
                   facecolor="none" if hueco else COLOR[k], edgecolor=COLOR[k],
                   lw=1.0, zorder=3, label=("no comparable (título no calculado)" if hueco
                                            else f"Modelo {NOM[k]}"))
        c[k] = c.get(k, 0) + 1
        c["huecos"] = c.get("huecos", 0) + (1 if hueco else 0)
    ax.legend(fontsize=7.5, loc="best")
    ax.set(xlabel="x_b [-]", ylabel="η [%]", title="Fig. 3 — η vs x_b (P=15 bar)")


def panel_fig2_fig5(ax, mod, xb, c):
    c["paper"] = 0
    for (fig, Pb, Ts, ls, k) in (("Fig2", 10.0, 373.0, "-", "Fig2_10bar"),
                                 ("Fig5", 32.0, 423.0, "--", "Fig5_T423"),
                                 ("Fig5", 32.0, 463.0, "--", "Fig5_T463")):
        q = papel(xb, fig, Pb, Ts)
        ax.plot(*zip(*q), color=COLOR[k], ls=ls, lw=1.6,
                label=f"Paper {NOM[k]} ({'continua' if ls == '-' else 'discontinua'})")
        c["paper"] += 1
    for f in mod:
        if f["serie"] not in ("Fig2_10bar", "Fig5_32bar") or f["convergio"] != "True" or f["motor"] != "teqp":
            continue
        k = serie(f)
        ax.scatter(float(f["x_b"]), float(f["eta_modelo_pct"]), s=42, color=COLOR[k],
                   edgecolor="k", lw=0.4, zorder=3, label=f"Modelo {NOM[k]}")
        c[k] = c.get(k, 0) + 1
    ax.legend(fontsize=7.5, loc="best")
    ax.set(xlabel="x_b [-]", ylabel="η [%]", title="Fig. 2 (10 bar) + Fig. 5 (32 bar) — η vs x_b")


def panel_paridad(ax, cmp_, d_med, mad, mx):
    xs = [float(f["eta_paper_pct"]) for f in cmp_]
    ys = [float(f["eta_modelo_pct"]) for f in cmp_]
    ax.scatter(xs, ys, c=[COLOR[serie(f)] for f in cmp_], s=42, edgecolor="k", lw=0.4, zorder=3)
    lo, hi = min(min(xs), min(ys)), max(max(xs), max(ys))
    m = [lo - 1.0, hi + 1.0]
    ax.plot(m, m, "k-", lw=0.9, zorder=1)
    ax.fill_between(m, [v - 0.5 for v in m], [v + 0.5 for v in m], color="0.75",
                    alpha=0.4, zorder=0)
    ax.text(0.03, 0.97,
            f"n={len(cmp_)}\nΔ medio={d_med:+.4f} pp\n|Δ| medio={mad:.4f} pp\n|Δ| máx={mx:.4f} pp",
            transform=ax.transAxes, va="top", fontsize=8.5, family="monospace",
            bbox=dict(fc="white", ec="0.5", alpha=0.85))
    hs = [plt.Line2D([0], [0], marker="o", ls="", mfc=COLOR[k], mec="k", label=NOM[k])
          for k in COLOR if any(serie(f) == k for f in cmp_)]
    hs.append(plt.Line2D([0], [0], color="0.75", lw=6, label="banda ±0.5 pp"))
    ax.legend(handles=hs, fontsize=7, loc="best", framealpha=0.9)
    ax.set(xlabel="η_paper [%]", ylabel="η_modelo [%]", title="Paridad η_modelo vs η_paper")


def principal():
    mod = leer(OUT / "validacion_tendencias.csv")
    xb = leer(EXT / "curvas_embaye_eta_vs_xb.csv")
    f7 = leer(EXT / "curvas_embaye_fig7.csv")
    cmp_ = [f for f in mod if f["convergio"] == "True" and f["motor"] == "teqp"
            and f["eta_paper_pct"] != "" and f["titulo_salida_turbina"] != ""
            and float(f["titulo_salida_turbina"]) >= 0.90]
    d, dr = np.array([float(f["delta_pp"]) for f in cmp_]), np.array([float(f["delta_rel_pct"]) for f in cmp_])
    d_med, mad = float(d.mean()), float(np.abs(d).mean())
    mx, med_rel = float(np.abs(d).max()), float(np.median(np.abs(dr)))
    n_noconv = sum(1 for f in mod if f["convergio"] != "True")
    fig, axs = plt.subplots(2, 2, figsize=(13, 10))
    c1, c2, c3 = {}, {}, {}
    panel_fig7(axs[0, 0], mod, f7, c1)
    panel_fig3(axs[0, 1], mod, xb, c2)
    panel_fig2_fig5(axs[1, 0], mod, xb, c3)
    panel_paridad(axs[1, 1], cmp_, d_med, mad, mx)
    [ax.grid(alpha=0.3) for ax in axs.flat]
    fig.text(0.5, 0.005, f"{n_noconv} de {len(mod)} puntos no convergieron; ver CSV", ha="center", fontsize=8.5, style="italic")
    fig.tight_layout(rect=(0, 0.015, 1, 1))
    fig.savefig(PNG, dpi=200)
    plt.close(fig)
    print(f"ESTADISTICA n={len(cmp_)} | d.medio={d_med:+.4f} pp | |d|.medio={mad:.4f} pp | |d|.max={mx:.4f} pp | mediana|drel|={med_rel:.3f} % | no conv: {n_noconv}/{len(mod)}")
    print(f"panel1: paper={c1['paper']} | teqp {c1['Fig7_0p55']}+{c1['Fig7_0p66']} pts | iapws={c1['control']} | panel2: paper={c2['paper']} | rellenos {c2['Fig3_T373']}+{c2['Fig3_T423']} | huecos={c2['huecos']} | panel3: paper={c3['paper']} | Fig2={c3['Fig2_10bar']} | F5_423={c3['Fig5_T423']} | F5_463={c3['Fig5_T463']} | panel4: {len(cmp_)} pts -> {PNG.name}")


if __name__ == "__main__":
    principal()