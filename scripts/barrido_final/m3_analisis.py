"""M3 — análisis sobre `m3_ofat.csv`: resumen, cruces y figuras.
`REPORTE_M3.md` lo escribe `m3_reporte.py`; ambos se re-ejecutan sobre el CSV
sin recalcular el ciclo (TASK_CONTEXT final_M3, pasos 1 y 3)."""
from __future__ import annotations

import csv, sys  # noqa: E401,E402
from collections import Counter
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

import m3_ofat as ofat

OUT = ofat.OUT
GENU = frozenset({"KALINA", "CORREGIBLE", "INVIABLE"})
MARG = ("m_O1", "m_O2", "m_O5")
COLOR = {"KALINA": "#2ca02c", "CORREGIBLE": "#ff7f0e", "INVIABLE": "#ffd400", "NO_CONVERGIO": "#d62728"}
CRES = ["variable", "valor_ancla", "a", "b", "E_eta", "motivo_E", "delta_eta", "eta_min",
        "eta_max", "n_genuinos", "n_kalina", "valor_eta_max_kalina", "kalina_desde",
        "kalina_hasta", "criterios_bloqueantes"]
CCRU = ["variable", "tipo", "criterio", "v_j", "v_j1", "v_cruce", "clase_j", "clase_j1"]


def num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def genu(f):
    return f["clasificacion"] in GENU


def leer():
    with open(OUT / "m3_ofat.csv", encoding="utf-8", newline="") as fh:
        filas = list(csv.DictReader(fh))
    for f in filas:
        f["valor"], f["eta"] = num(f["valor"]), num(f["eta"])
    return filas


def agrupar(filas):
    """`(ancla, {variable: (a, b, malla ordenada, vecinos)})`."""
    ancla = next(f for f in filas if f["tipo_punto"] == "ancla")
    g = {}
    for nom, a, b in ofat.RANGOS:
        m = sorted([f for f in filas if f["variable"] == nom
                    and f["tipo_punto"] == "malla"], key=lambda f: f["valor"])
        v = [f for f in filas if f["variable"] == nom and f["tipo_punto"] == "vecino"]
        g[nom] = (a, b, m, v)
    return ancla, g


def elasticidad(nom, a, b, vec, ancla):
    """E = [η(v+h) − η(v−h)]/(2h)·v/η(A*); vacía + motivo si falta alguno."""
    h = 0.01 * (b - a)
    if not genu(ancla):
        return None, f'A* no es genuino ({ancla["clasificacion"]})'
    if len(vec) != 2:
        return None, "faltan los dos vecinos"
    menos, mas = sorted(vec, key=lambda f: f["valor"])
    if not genu(menos):
        return None, f'vecino -h no genuino ({menos["clasificacion"]})'
    if not genu(mas):
        return None, f'vecino +h no genuino ({mas["clasificacion"]})'
    if None in (ancla["eta"], menos["eta"], mas["eta"]):
        return None, "falta eta en A* o en un vecino"
    if ancla["eta"] == 0:
        return None, "eta(A*) = 0"
    return (mas["eta"] - menos["eta"]) / (2 * h) * ofat.ANCHOR[nom] / ancla["eta"], ""


def zona(nom, m, v, ancla):
    """`(kalina_desde, kalina_hasta)`: malla dentro de la zona KALINA contigua a A*."""
    A = dict(ancla, valor=ofat.ANCHOR[nom])
    if A["clasificacion"] != "KALINA":
        return None, None
    pts = sorted(m + v + [A], key=lambda f: f["valor"])
    i0 = i1 = pts.index(A)
    while i0 and pts[i0 - 1]["clasificacion"] == "KALINA":
        i0 -= 1
    while i1 + 1 < len(pts) and pts[i1 + 1]["clasificacion"] == "KALINA":
        i1 += 1
    val = [f["valor"] for f in pts[i0:i1 + 1] if f["tipo_punto"] == "malla"]
    return (min(val), max(val)) if val else (None, None)


def bloqueos(puntos):
    c = Counter(k for f in puntos for k in (f["codigos_falla"] or "").split(",") if k)
    return " · ".join(f"{k}({n})" for k, n in c.most_common())


def fila_resumen(nom, a, b, m, v, ancla):
    gen = [f for f in m if genu(f)]
    ets = [f["eta"] for f in gen if f["eta"] is not None]
    kal = [f for f in gen if f["clasificacion"] == "KALINA" and f["eta"] is not None]
    E, mot = elasticidad(nom, a, b, v, ancla)
    d0, d1 = zona(nom, m, v, ancla)
    fuera = [f for f in gen if d0 is None or not (d0 <= f["valor"] <= d1)]
    return dict(variable=nom, valor_ancla=ofat.ANCHOR[nom], a=a, b=b, E_eta=E,
                motivo_E=mot, delta_eta=(max(ets) - min(ets)) if len(ets) > 1 else None,
                eta_min=min(ets) if ets else None, eta_max=max(ets) if ets else None,
                n_genuinos=len(gen), n_kalina=len(kal), kalina_desde=d0,
                kalina_hasta=d1, criterios_bloqueantes=bloqueos(fuera),
                valor_eta_max_kalina=(max(kal, key=lambda f: f["eta"])["valor"]
                                      if kal else None))


def cruces_var(nom, m):
    """Cruces de margen (interpolados) y cambios de clase entre vecinos de la malla."""
    out = []
    for p, q in zip(m, m[1:]):
        if genu(p) and genu(q):
            for k in MARG:
                mp, mq = num(p[k]), num(q[k])
                if mp is None or mq is None or mp * mq >= 0:
                    continue
                out.append(dict(variable=nom, tipo="margen", criterio=k, v_j=p["valor"],
                                v_j1=q["valor"], clase_j=p["clasificacion"],
                                clase_j1=q["clasificacion"],
                                v_cruce=p["valor"] - mp * (q["valor"] - p["valor"]) / (mq - mp)))
        if p["clasificacion"] != q["clasificacion"]:
            out.append(dict(variable=nom, tipo="clase", criterio="clase", v_j=p["valor"],
                            v_j1=q["valor"], v_cruce=None, clase_j=p["clasificacion"],
                            clase_j1=q["clasificacion"]))
    return out


def escribir(nombre, cab, filas):
    with open(OUT / nombre, "w", encoding="utf-8", newline="") as fh:
        esc = csv.DictWriter(fh, fieldnames=cab)
        esc.writeheader()
        for f in filas:
            esc.writerow({c: f.get(c) for c in cab})
    print(f"{nombre}: {len(filas)} filas", flush=True)


def figuras(res, g, ancla):
    d = sorted([(r["variable"], r["delta_eta"] * 100) for r in res
                if r["delta_eta"] is not None], key=lambda t: t[1])
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.barh([x[0] for x in d], [x[1] for x in d], color="#d62728")
    for i, (_, v) in enumerate(d):
        ax.text(v, i, f" {v:.2f}", va="center", fontsize=8)
    ax.set_xlabel("Δη dentro del rango (puntos porcentuales)"); ax.set_title("M3 tornado — efecto de cada variable sobre η (OAT)")
    fig.tight_layout(); fig.savefig(OUT / "m3_tornado.png", dpi=150); plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 4.6))
    for i, r in enumerate(res):
        if r["E_eta"] is None:
            ax.text(i, 0, "n/d", rotation=90, ha="center", va="center", fontsize=8)
        else:
            ax.bar(i, r["E_eta"], color="#1f77b4")
            ax.text(i, r["E_eta"], f'{r["E_eta"]:.3f}', ha="center", va="bottom", fontsize=8)
    ax.set_xticks(range(len(res))); ax.set_xticklabels([r["variable"] for r in res], rotation=30, ha="right")
    ax.axhline(0, color="#333333", lw=0.8)
    ax.set_ylabel("E en A* (−)"); ax.set_title("M3 elasticidad de η en A*")
    fig.tight_layout(); fig.savefig(OUT / "m3_elasticidad.png", dpi=150); plt.close(fig)
    fig, axs = plt.subplots(2, 5, figsize=(18, 7))
    for k, (nom, (a, b, m, v)) in enumerate(g.items()):
        ax = axs.ravel()[k]
        for f in m + v + [dict(ancla, valor=ofat.ANCHOR[nom])]:
            col = COLOR.get(f["clasificacion"], "#888888")
            ax.plot([f["valor"]], [0 if f["eta"] is None else f["eta"] * 100],
                    "x" if f["eta"] is None else "o",
                    ms=5 if f["eta"] is None else 4, color=col, mew=1.4, ls="none")
        ax.axvline(ofat.ANCHOR[nom], color="#444444", ls="--", lw=1)
        ax.set_title(nom); ax.set_xlabel(nom); ax.set_ylabel("η (%)")
    fig.legend(handles=[Patch(color=c, label=n) for n, c in COLOR.items()],
               loc="lower center", ncol=4)
    fig.tight_layout(rect=(0, 0.06, 1, 1)); fig.savefig(OUT / "m3_curvas.png", dpi=150); plt.close(fig)
    print("figuras: m3_tornado.png, m3_elasticidad.png, m3_curvas.png", flush=True)


def main() -> None:
    filas = leer()
    ancla, g = agrupar(filas)
    res = [fila_resumen(nom, *g[nom], ancla) for nom, *_ in ofat.RANGOS]
    cruces = [c for nom, *_ in ofat.RANGOS for c in cruces_var(nom, g[nom][2])]
    escribir("m3_resumen.csv", CRES, res)
    escribir("m3_cruces.csv", CCRU, cruces)
    figuras(res, g, ancla)
    import m3_reporte as rep  # noqa: E402
    rep.generar(res, cruces, filas, ancla, g)
    print(f"m3_analisis listo -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
