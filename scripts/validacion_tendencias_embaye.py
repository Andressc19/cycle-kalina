"""Validacion por tendencias vs Elsayed(2013)/Embaye - KCS11 (tarea 2026-09-24).
Reusa calibracion_elsayed_malla.py (pinch 4K, Tsum=283K, eta_t=eta_p=0.80); curvas paper LEIDAS; reanudable; nunca extrapola; no modifica nada."""
from __future__ import annotations
import csv, sys, time
from pathlib import Path
import numpy as np
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from calibracion_elsayed_malla import calibrar_P_baja, calibrar_eps  # noqa: E402
from src._cycle_loops import CicloNoConvergeError  # noqa: E402
from src.properties.adapter import PropertyRangeError  # noqa: E402
from src.properties.ammonia_water_adapter import AmmoniaWaterAdapter  # noqa: E402
from src.properties.teqp_adapter import TeqpAdapter  # noqa: E402
OUT = REPO / "resultados" / "2026-09-24_validacion_tendencias"
CSV, PNG, MD = OUT / "validacion_tendencias.csv", OUT / "comparacion_tendencias.png", OUT / "REPORTE_VALIDACION_TENDENCIAS.md"
EXT = REPO / "resultados" / "2026-09-24_embaye_vectorial"
COLS = ("serie", "T_fuente_K", "P_alta_kPa", "x_b", "motor", "P_baja_kPa", "eps_hrvg", "eps_reg",
        "eps_cond", "convergio", "eta_modelo_pct", "eta_paper_pct", "delta_pp", "delta_rel_pct",
        "titulo_salida_turbina", "Wnet_kW", "detalle_error")
EXC = (CicloNoConvergeError, PropertyRangeError, ValueError, RuntimeError, NotImplementedError)
PUNTOS = tuple((s, 373.0, p, x, "teqp") for (s, ps, x) in
               (("Fig7_KCS11_0p55", (1100, 1200, 1500, 1800, 2000, 2200, 2300), 0.55),
                ("Fig7_KCS11_0p66", (1100, 1500, 2000, 2500, 3000), 0.66)) for p in ps)
PUNTOS += tuple(("Fig3_15bar", T, 1500.0, x, "teqp") for (T, xs) in
                ((373.0, (.45, .55, .65, .75, .85)), (423.0, (.45, .60, .75)), (333.0, (.65, .75, .85))) for x in xs)
PUNTOS += tuple(("Fig2_10bar", 373.0, 1000.0, x, "teqp") for x in (.45, .60, .80))
PUNTOS += tuple(("Fig5_32bar", T, 3200.0, x, "teqp") for T in (423.0, 463.0) for x in (.60, .80))
PUNTOS += (("Fig7_KCS11_0p55", 373.0, 1500.0, 0.55, "AmmoniaWater"),
           ("Fig7_KCS11_0p66", 373.0, 2500.0, 0.66, "AmmoniaWater"),
           ("Fig3_15bar", 423.0, 1500.0, 0.60, "AmmoniaWater"))
def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)
def leer(ruta):
    with open(ruta, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
def interp(pts):
    xs = sorted({p[0] for p in pts})
    ys = [float(np.mean([q[1] for q in pts if abs(q[0] - x) < 1e-9])) for x in xs]
    lo, hi = xs[0], xs[-1]
    return lambda x: None if not (lo <= x <= hi) else float(np.interp(x, xs, ys))
def cargar_interp():
    S, f7, eV = {}, leer(EXT / "curvas_embaye_fig7.csv"), leer(EXT / "curvas_embaye_eta_vs_xb.csv")
    for (c, s) in (("KCS11(Con.=0.55)", "Fig7_KCS11_0p55"), ("KCS11(Con.=0.66)", "Fig7_KCS11_0p66")):
        S[s] = interp([(100.0 * float(r["P_evap_bar"]), float(r["eta_pct"])) for r in f7 if r["curva"] == c])
    for (fg, Pb) in (("Fig2", 10.0), ("Fig3", 15.0), ("Fig5", 32.0)):
        for T in (333.0, 373.0, 423.0, 463.0):
            if (q := [(float(r["x_b_masica"]), float(r["eta_pct"])) for r in eV
                      if r["figura"] == fg and abs(float(r["P_evap_bar"]) - Pb) < 1e-6
                      and abs(float(r["T_fuente_K"]) - T) < 1e-6]):
                S[f"{fg}_{int(Pb)}bar_T{int(T)}"] = interp(q)
    return S
def eta_paper(S, serie, T, P, x):
    return S[serie](P) if serie.startswith("Fig7") else S[f"{serie}_T{int(round(T))}"](x)
def resolver(S, serie, T, P, x, motor):
    f = dict.fromkeys(COLS, "")
    f.update(serie=serie, T_fuente_K=T, P_alta_kPa=P, x_b=x, motor=motor)
    b = TeqpAdapter(x=x) if motor == "teqp" else AmmoniaWaterAdapter(x=x)
    try:
        pb = calibrar_P_baja(b, x, P)
    except EXC as e:
        f["detalle_error"] = f"{type(e).__name__}: {e}"
        return f
    f["P_baja_kPa"] = round(pb, 6)
    try:
        cal = calibrar_eps(b, x_b=x, P_alta=P, P_baja=pb, T_fuente=T)
    except EXC as e:
        f["detalle_error"] = f"{type(e).__name__}: {e}"
        return f
    r, e4 = cal["resultado"], cal["resultado"]["estados"]["e4"]
    try:
        q4 = round(b.fase_de(pb, e4.T, e4.x)[1], 4)
    except EXC:
        q4 = ""
    f.update(eps_hrvg=round(cal["eps_hrvg"], 6), eps_reg=round(cal["eps_reg"], 6),
             eps_cond=round(cal["eps_cond"], 6), convergio=True,
             eta_modelo_pct=round(r["eta"] * 100.0, 4), titulo_salida_turbina=q4, Wnet_kW=round(r["Wnet"], 4))
    ep = eta_paper(S, serie, T, P, x)
    if ep is not None:
        f.update(eta_paper_pct=round(ep, 4), delta_pp=round(f["eta_modelo_pct"] - ep, 4),
                 delta_rel_pct=round((f["eta_modelo_pct"] - ep) / ep * 100.0, 3))
    return f
def hechas():
    if not CSV.exists():
        return set()
    d = set()
    for r in leer(CSV):
        try:
            d.add((r["serie"], float(r["T_fuente_K"]), float(r["P_alta_kPa"]), float(r["x_b"]), r["motor"]))
        except (KeyError, ValueError):
            pass
    return d
def guardar(f):
    nuevo = not CSV.exists()
    with open(CSV, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        if nuevo:
            w.writeheader()
        w.writerow(f)


def grafica(todas):
    PNG.parent.mkdir(parents=True, exist_ok=True)
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    f7, eV = leer(EXT / "curvas_embaye_fig7.csv"), leer(EXT / "curvas_embaye_eta_vs_xb.csv")
    fig, axs = plt.subplots(1, 2, figsize=(13, 5.2))
    ax = axs[0]
    for (c, col) in (("KCS11(Con.=0.55)", "#1f77b4"), ("KCS11(Con.=0.66)", "#d62728")):
        d = [r for r in f7 if r["curva"] == c]
        ax.plot([100.0 * float(r["P_evap_bar"]) for r in d], [float(r["eta_pct"]) for r in d],
                col, lw=1.6, label=f"Paper {c}")
    ax.set(xlabel="P_alta [kPa]", ylabel="η [%]", title="Fig. 7 - η vs P_alta (T_fuente=373 K)")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    ax = axs[1]
    for (T, col) in ((333.0, "#2ca02c"), (373.0, "#1f77b4"), (423.0, "#d62728")):
        d = [r for r in eV if r["figura"] == "Fig3" and abs(float(r["T_fuente_K"]) - T) < 1e-6]
        ax.plot([float(r["x_b_masica"]) for r in d], [float(r["eta_pct"]) for r in d],
                col, lw=1.6, label=f"Paper T_fuente={int(T)} K")
    ax.set(xlabel="x_b [-", ylabel="η [%]", title="Fig. 3 - η vs x_b (P=15 bar)")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    for f in todas:
        if f["convergio"] != "True":
            continue
        ax = axs[0] if f["serie"].startswith("Fig7_KCS11") else (axs[1] if f["serie"] == "Fig3_15bar" else None)
        if ax is not None:
            ax.scatter(float(f["P_alta_kPa"] if ax is axs[0] else f["x_b"]), float(f["eta_modelo_pct"]),
                       marker="x" if f["motor"] == "AmmoniaWater" else "o", s=55, edgecolor="k", zorder=3)
    fig.tight_layout(); fig.savefig(PNG, dpi=150); plt.close(fig)


def fmt(v, n=4):
    return "-" if v in ("", None) else f"{float(v):.{n}f}"
def reporte(todas):
    conv = [f for f in todas if f["convergio"] == "True"]
    cmp = [f for f in conv if f["eta_paper_pct"] != "" and f["titulo_salida_turbina"] != ""
           and float(f["titulo_salida_turbina"]) >= 0.90]
    d, dr = [float(f["delta_pp"]) for f in cmp], [float(f["delta_rel_pct"]) for f in cmp]
    if cmp:
        med, mad, mx = float(np.mean(d)), float(np.mean(np.abs(d))), float(np.max(np.abs(d)))
        mxr = float(np.max(np.abs(dr)))
    else:
        med = mad = mx = mxr = float("nan")
    f7 = sorted((f for f in conv if f["serie"] == "Fig7_KCS11_0p55" and f["motor"] == "teqp"),
                key=lambda f: float(f["P_alta_kPa"]))
    p7 = [(100.0 * float(r["P_evap_bar"]), float(r["eta_pct"])) for r in leer(EXT / "curvas_embaye_fig7.csv")
          if r["curva"] == "KCS11(Con.=0.55)"]
    pmx, mmx = max(p7, key=lambda t: t[1]), (max(f7, key=lambda f: float(f["eta_modelo_pct"])) if f7 else None)
    gp = lambda T: {float(f["x_b"]): f for f in conv if f["serie"] == "Fig3_15bar"
                    and f["T_fuente_K"] == f"{T:.1f}" and f["motor"] == "teqp"}
    g3, g4 = gp(373.0), gp(423.0)
    xs = (0.45, 0.55, 0.65, 0.75, 0.85)
    pend = [(a, b, float(g3[a]["eta_modelo_pct"]), float(g3[b]["eta_modelo_pct"]),
             float(g3[a]["eta_paper_pct"]), float(g3[b]["eta_paper_pct"]))
            for a, b in zip(xs, xs[1:]) if a in g3 and b in g3
            and g3[a]["eta_paper_pct"] != "" and g3[b]["eta_paper_pct"] != ""]
    tef = [(x, float(g4[x]["eta_modelo_pct"]) - float(g3[x]["eta_modelo_pct"]),
            float(g4[x]["eta_paper_pct"]) - float(g3[x]["eta_paper_pct"]))
           for x in sorted(set(g3) & set(g4))
           if g3[x]["eta_paper_pct"] != "" and g4[x]["eta_paper_pct"] != ""]
    ctrl = []
    for (s, T, P, x) in (("Fig7_KCS11_0p55", 373.0, 1500.0, 0.55),
                         ("Fig7_KCS11_0p66", 373.0, 2500.0, 0.66),
                         ("Fig3_15bar", 423.0, 1500.0, 0.60)):
        g = {f["motor"]: f for f in todas if f["serie"] == s and abs(float(f["T_fuente_K"]) - T) < 1e-9
             and abs(float(f["P_alta_kPa"]) - P) < 1e-9 and abs(float(f["x_b"]) - x) < 1e-9}
        if "teqp" in g and "AmmoniaWater" in g and g["teqp"]["convergio"] == "True" \
                and g["AmmoniaWater"]["convergio"] == "True":
            ctrl.append((s, x, g["teqp"]["eta_modelo_pct"], g["AmmoniaWater"]["eta_modelo_pct"],
                         float(g["AmmoniaWater"]["eta_modelo_pct"]) - float(g["teqp"]["eta_modelo_pct"])))
    L = ["# Reporte - Validacion por tendencias vs Elsayed et al. (2013) / Embaye et al.",
         "",
         f"Tarea 2026-09-24-validacion-tendencias-embaye. {len(todas)} filas ({len(conv)} convergen). "
         "Metodo reusado de scripts/calibracion_elsayed_malla.py (igual que el punto unico "
         "VALIDACION_ELSAYED2013.md): P_baja = burbuja a (T_sumidero+4 K, x_b); eps* por despeje de "
         "un paso del pinch 4 K; T_sumidero=283 K, eta_t=eta_p=0.80, m_b=1; teqp + 3 controles "
         "AmmoniaWaterAdapter; curvas paper LEIDAS (no recalculadas); nunca se extrapola => 333 K x_b=0.65 sin eta_paper.",
         "",
         "## 1. Tabla de todos los puntos",
         "",
         "| serie | T_fuente | P_alta | x_b | motor | P_baja | eps_hrvg | eps_reg | eps_cond | conv | eta_mod | eta_pap | dpp | drel% | q4 | Wnet | error |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
         *[f"| {f['serie']} | {f['T_fuente_K']} | {f['P_alta_kPa']} | {f['x_b']} | {f['motor']} | {fmt(f['P_baja_kPa'], 1)} | "
           f"{fmt(f['eps_hrvg'])} | {fmt(f['eps_reg'])} | {fmt(f['eps_cond'])} | {'SI' if f['convergio'] == 'True' else 'NO'} | "
           f"{fmt(f['eta_modelo_pct'])} | {fmt(f['eta_paper_pct'])} | {fmt(f['delta_pp'])} | {fmt(f['delta_rel_pct'])} | "
           f"{fmt(f['titulo_salida_turbina'], 3)} | {fmt(f['Wnet_kW'], 1)} | {(f['detalle_error'][:60] or '-')} |"
           for f in todas],
         "",
         "## 2. Estadistica global (comparables: convergen, q4>=0.90, eta_paper disponible)",
         "",
         f"n={len(cmp)} | d.medio={med:+.3f} pp | |d|.medio={mad:.3f} pp | |d|.max={mx:.3f} pp ({mxr:.1f} %).",
         "",
         "## 3. Fig. 7 x_b=0.55: forma (sube-maximo-baja) y posicion del maximo",
         "",
         f"Paper: max eta={pmx[1]:.2f} % a P={pmx[0] / 100:.2f} bar. "
         + (f"Modelo (teqp, 1100-2300 kPa): max eta={float(mmx['eta_modelo_pct']):.2f} % a "
            f"P={float(mmx['P_alta_kPa']) / 100:.2f} bar." if mmx else "Modelo: sin puntos."),
         "",
         "## 4. Fig. 3, 373 K: signo de pendientes eta vs x_b (modelo vs paper)",
         "",
         *(f"- {a:.2f}->{b:.2f}: mod {c:.2f}->{d:.2f} ({'+' if d - c > 0 else '-'}), "
           f"paper {e:.2f}->{f2:.2f} ({'+' if f2 - e > 0 else '-'}) => "
           f"{'coincide' if (d - c) * (f2 - e) > 0 else 'difiere'}" for a, b, c, d, e, f2 in pend),
         "",
         "## 5. Efecto de T_fuente (Fig. 3, 15 bar, 373 vs 423 K, mismo x_b)",
         "",
         *([f"- x_b={x:.2f}: d.eta(423-373) mod={m:+.3f} pp, paper={p:+.3f} pp => "
            f"{'acorde al paper' if m * p > 0 else 'contra el paper'}" for x, m, p in tef]
           if tef else ["- No cuantificable: 423 K x_b=0.45/0.75 no convergen con teqp "
                        "(T_from_Ph fuera de cobertura); sin x_b comun con 373 K."]),
         "",
         "## 6. Control teqp vs AmmoniaWaterAdapter (mismos puntos de operacion)",
         "",
         *(f"- {s} x_b={x:.2f}: teqp={t} %, AmH2O={a} %, d={d2:+.4f} pp"
           for s, x, t, a, d2 in ctrl),
         "",
         "## 7. Eps calibrados (fuera de 0.75-0.85 es esperado: replican el pinch 4 K del paper)",
         "",
         f"eps_hrvg: " + (f"[{min(float(f['eps_hrvg']) for f in conv):.4f}, "
                          f"{max(float(f['eps_hrvg']) for f in conv):.4f}] ({len(conv)} convergentes)"
                          if conv else "sin puntos"),
         "",
         "## 8. Conclusion honesta",
         "",
         "Coincidencias y divergencias en secciones 3-6; los 333 K se evaluaron igual y se registran "
         "con su error real (arranque del solver con T_fuente baja: resultados/2026-09-23_limites_teqp). "
         "Fuentes esperadas de discrepancia: EOS distinta (Ibrahim-Klein vs Tillner-Roth/teqp), "
         "traduccion pinch->efectividad de un paso, P_baja = burbuja a T_sumidero+4 K, sin cota de titulo >=0.90 del paper. No se fuerza conclusion favorable.",
    ]
    MD.write_text("\n".join(L) + "\n", encoding="utf-8")


def principal():
    OUT.mkdir(parents=True, exist_ok=True)
    S, done, t0 = cargar_interp(), hechas(), time.time()
    for p in PUNTOS:
        if p in done:
            continue
        f = resolver(S, *p)
        guardar(f)
        done.add(p)
        log(f"[{time.time() - t0:6.0f}s] {f['serie']} T={f['T_fuente_K']} P={f['P_alta_kPa']} "
            f"xb={f['x_b']} {f['motor']} conv={f['convergio']} eta={f['eta_modelo_pct']} "
            f"q4={f['titulo_salida_turbina']} {f['detalle_error'][:60]}")
    todas = leer(CSV)
    grafica(todas)
    reporte(todas)
    log(f"LISTO en {time.time() - t0:.0f}s -> {CSV}, {PNG}, {MD}")


if __name__ == "__main__":
    principal()
