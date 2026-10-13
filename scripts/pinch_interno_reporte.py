"""Resumen estadístico, perfiles de ejemplo y figura de la sonda de pinch interno.

Solo lee `pinch_puntos.csv` y `perfiles_todos.csv` de `OUT` (los escribe
`pinch_interno.py`). Escribe `pinch_resumen.csv`, `perfiles_ejemplo.csv` y
`pinch_regenerador.png`. No calcula nada del ciclo.
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "resultados" / "2026-10-13_pinch_interno"
BINS = [(0.40, 0.60), (0.60, 0.80), (0.80, 0.90), (0.90, 0.9501), (0.9501, 1.01)]


def num(v):
    return None if v in ("", None) else float(v)


def leer(nombre):
    with open(OUT / nombre, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def conteo(filas, corte, etiqueta, out):
    ev = [r for r in filas if r["clase_pinch"] not in ("NO_CONVERGIO", "NO_EVALUADO")]
    pk = [num(r["reg_pinch_K"]) for r in ev if num(r["reg_pinch_K"]) is not None]
    hv = [num(r["hrvg_acerc_K"]) for r in ev if num(r["hrvg_acerc_K"]) is not None]
    out.append(dict(corte=corte, categoria=etiqueta, n=len(filas), n_evaluados=len(ev),
                    cruce=sum(r["clase_pinch"] == "CRUCE" for r in ev),
                    estrecho=sum(r["clase_pinch"] == "SIN_CRUCE_ESTRECHO" for r in ev),
                    amplio=sum(r["clase_pinch"] == "SIN_CRUCE_AMPLIO" for r in ev),
                    pinch_min_K=min(pk) if pk else None,
                    pinch_mediana_K=sorted(pk)[len(pk) // 2] if pk else None,
                    hrvg_acerc_min_K=min(hv) if hv else None,
                    hrvg_hierve=sum(r["hrvg_hierve"] == "True" for r in ev)))


def main() -> None:
    filas = leer("pinch_puntos.csv")
    res = []
    conteo(filas, "todos", "todos", res)
    for m in sorted({r["motor"] for r in filas}):
        conteo([r for r in filas if r["motor"] == m], "motor", m, res)
    for g in sorted({r["grupo"] for r in filas}):
        conteo([r for r in filas if r["grupo"] == g], "grupo", g, res)
    prop = [r for r in filas if r["grupo"] != "elsayed" and r["motor"] == "teqp"]
    for var in ("eps_reg", "eps_hrvg"):
        for a, b in BINS:
            conteo([r for r in filas if r["motor"] == "teqp" and a <= float(r[var]) < b],
                   f"{var} (teqp, todos los grupos)", f"[{a:.2f}, {min(b, 0.95):.2f}]"
                   if b < 1 else "> 0.95 (calibrados Elsayed)", res)
    conteo(prop, "propios (sin Elsayed, teqp)", "todos", res)
    with open(OUT / "pinch_resumen.csv", "w", encoding="utf-8", newline="") as fh:
        esc = csv.DictWriter(fh, fieldnames=list(res[0]))
        esc.writeheader(), esc.writerows(res)
    for r in res:
        print(" | ".join(f"{k}={v:.3g}" if isinstance(v, float) else f"{k}={v}"
                         for k, v in r.items()), flush=True)
    cruces = [r for r in filas if r["clase_pinch"] == "CRUCE"]
    if cruces:
        print("eps_reg minimo con cruce:", min(float(r["eps_reg"]) for r in cruces),
              "| eps_hrvg minimo con cruce:", min(float(r["eps_hrvg"]) for r in cruces),
              flush=True)
    ev = [r for r in filas if num(r["reg_pinch_K"]) is not None]
    if not ev:
        print("sin puntos evaluados", flush=True)
        return
    por_pinch = sorted(ev, key=lambda r: num(r["reg_pinch_K"]))
    tags = []
    for r in ([x for x in ev if x["tag"] == "A*"] + por_pinch[:1] +
              [max((x for x in ev if x["motor"] == "teqp"), key=lambda x: float(x["eps_reg"]))] +
              [x for x in por_pinch if x["grupo"] == "elsayed"][:1] +
              [x for x in ev if x["grupo"] == "opt_5_1"][:1]):
        if r["tag"] not in tags:
            tags.append(r["tag"])
    perf = [p for p in leer("perfiles_todos.csv") if p["tag"] in tags]
    with open(OUT / "perfiles_ejemplo.csv", "w", encoding="utf-8", newline="") as fh:
        esc = csv.DictWriter(fh, fieldnames=list(perf[0]))
        esc.writeheader(), esc.writerows(perf)
    fig, axs = plt.subplots(1, min(len(tags), 3), figsize=(5 * min(len(tags), 3), 4),
                            squeeze=False)
    for ax, tag in zip(axs[0], tags[:3]):
        d = [p for p in perf if p["tag"] == tag and p["equipo"] == "regenerador"
             and p["T_caliente"] and p["T_frio"]]
        f = [float(p["f"]) for p in d]
        ax.plot(f, [float(p["T_caliente"]) for p in d], "r-", label="lado caliente (5→6)")
        ax.plot(f, [float(p["T_frio"]) for p in d], "b-", label="lado frío (1←10)")
        fila = next(r for r in filas if r["tag"] == tag)
        ax.set_title(f"{tag}\npinch = {num(fila['reg_pinch_K']):.2f} K, "
                     f"ε_reg = {float(fila['eps_reg']):.3f}", fontsize=9)
        ax.set_xlabel("fracción del calor del regenerador desde el extremo caliente")
        ax.set_ylabel("T [K]")
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "pinch_regenerador.png", dpi=130)
    print("ejemplos:", tags, flush=True)


if __name__ == "__main__":
    main()
