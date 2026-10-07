"""M5 — análisis por escenario sobre `m5_lhs.csv` (TASK_CONTEXT final_M5).

Por cada escenario: conteos (n, KALINA, genuinos, N2, omitidos y fuera de
rango); ¿es posible?; si lo es, los rangos (mín, p5, mediana, p95 y máx) de
cada variable libre dentro de KALINA —más dP y rP cuando las presiones no
están fijas— con el KS (RSA) de KALINA contra no KALINA cuando hay ≥ 10
KALINA; la figura de la ventana de presiones (`m5_S{k}.png`); el KALINA más
parecido al profesor (d = Σ |v − v_prof|/(b − a) sobre las libres); y, por
último y como dato secundario, el KALINA de mayor η. Escribe
`m5_resumen.csv`, `m5_rangos.csv` y `m5_cercano_profesor.csv`, y llama a
`m5_reporte` para `REPORTE_M5.md`. Todo se re-ejecuta sobre el CSV, sin
recalcular el ciclo.
"""
from __future__ import annotations

import sys, time  # noqa: E401,E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from comun import PROFESOR  # noqa: E402
from m4_analisis import resumen  # noqa: E402
from m4_datos import genu  # noqa: E402
from m4b_datos import escribir, leer_de  # noqa: E402
from m4b_presiones import CRANGOS, _stats  # noqa: E402
from m4b_presiones_fig import COLORES, GRIS  # noqa: E402
from m4_rsa import ks_ic, valores  # noqa: E402
from m5_corrida import FIJOS, LIBRES, OUT, RANGOS  # noqa: E402
import m5_reporte as rep  # noqa: E402

CRESUM = ["escenario", "n", "omitidos", "evaluados", "KALINA", "genuinos",
          "N2", "fuera_rango", "factible", "bloqueante", "bloqueante_n",
          "mejor_D", "mejor_D_id", "cercano_id", "cercano_d", "cercano_eta",
          "mejor_eta_id", "mejor_eta", "suma_t_s"]
CCERC = ["escenario", "tipo", "id", "d", "D", "eta", "fuera_rango",
         "B_verificado"] + list(RANGOS)
CRANGOS5 = ["escenario"] + list(CRANGOS)
ORDEN = ("KALINA", "CORREGIBLE", "INVIABLE", "no genuino")  # orden de la leyenda
# Ejes de la figura de cada escenario (TASK_CONTEXT §4 de las salidas).
EJES = {1: ("P_baja", "P_alta"), 2: ("T_fuente", "x_b"),
        3: ("T_fuente", "x_b"), 4: ("P_baja", "x_b"), 5: ("P_baja", "P_alta")}
UNI = {"P_alta": "kPa", "P_baja": "kPa", "dP": "kPa",
       "T_fuente": "K", "T_sumidero": "K"}


def leer() -> list:
    """`m5_lhs.csv` tipado (incluye escenario, id y omitido)."""
    filas = leer_de(OUT, "m5_lhs.csv")
    for f in filas:
        f["escenario"] = int(f["escenario"])
        f["id"] = int(f["id"])
        f["omitido"] = f.get("omitido") == "True"
    return filas


def bloqueante(ev: list) -> tuple:
    """`(código dominante, n)` entre los genuinos NO KALINA de `ev`."""
    cuenta: dict = {}
    for f in ev:
        if not genu(f) or f["clasificacion"] == "KALINA":
            continue
        cods = [c for c in (f["codigos_falla"] or "").split(",") if c]
        for c in cods or ["(sin codigos)"]:
            cuenta[c] = cuenta.get(c, 0) + 1
    if not cuenta:
        return None, 0
    c = max(cuenta, key=lambda k: (cuenta[k], k))   # empate: el mayor alfabét.
    return c, cuenta[c]


def d_punto(f: dict, lib: list) -> float:
    """d = Σ |v − v_prof|/(b − a) sobre las variables libres (§5 del diseño)."""
    return sum(abs(f[v] - PROFESOR[v]) / (RANGOS[v][1] - RANGOS[v][0])
               for v in lib)


def rangos_esc(k: int, todo: list) -> list:
    """Filas de `m5_rangos.csv` del escenario: libres + dP y rP si hay libres."""
    vars_ = list(LIBRES[k])
    if "P_alta" in vars_ or "P_baja" in vars_:
        vars_ += ["dP", "rP"]
    out = []
    for v in vars_:
        b, bb, _ = valores(todo, "KALINA", v)
        ks, p, _, _ = ks_ic(b, bb) if len(b) >= 10 else (None,) * 4
        for grupo, vals in (("KALINA", b), ("no_KALINA", bb)):
            out.append(dict(escenario=k, variable=v, grupo=grupo,
                            **_stats(vals), KS=ks, p_valor=p))
    return out


def figura(k: int, ev: list) -> None:
    """`m5_S{k}.png`: solo las filas EVALUADAS, coloreadas por clase."""
    x, y = EJES[k]
    fig, ax = plt.subplots(figsize=(9, 6.2))
    vistos = set()
    for f in ev:
        if f.get(x) is None or f.get(y) is None:
            continue
        cls = (f["clasificacion"] if f["clasificacion"] in COLORES
               else "no genuino")
        ax.scatter(f[x], f[y], s=16, c=COLORES.get(cls, GRIS), alpha=0.85,
                   edgecolors="none", label=cls if cls not in vistos else None)
        vistos.add(cls)
    ax.set_xlim(*RANGOS[x])
    ax.set_ylim(*RANGOS[y])
    ax.set_xlabel(f"{x} ({UNI.get(x, '−')})")
    ax.set_ylabel(f"{y} ({UNI.get(y, '−')})")
    ax.set_title(f"M5 — S{k}: {y} contra {x}, color = clase "
                 f"({len(ev)} evaluados)")
    ax.grid(alpha=0.3)
    hs = [plt.Line2D([], [], marker="o", ls="", color=COLORES.get(c, GRIS),
                     label=c) for c in ORDEN if c in vistos]
    ax.legend(handles=hs, fontsize=8, loc="best")
    fig.tight_layout()
    fig.savefig(OUT / f"m5_S{k}.png", dpi=150)
    plt.close(fig)
    print(f"m5_S{k}.png", flush=True)


def _fila_punto(k: int, tipo: str, f: dict, lib: list) -> dict:
    """Una fila de `m5_cercano_profesor.csv` con todos los valores del punto."""
    return dict(escenario=k, tipo=tipo, id=f["id"], d=d_punto(f, lib),
                D=f["D"], eta=f["eta"], fuera_rango=f["fuera_rango"],
                B_verificado=f.get("B_verificado"),
                **{v: f[v] for v in RANGOS})


def analisis_esc(k: int, todo: list) -> tuple:
    """`(fila de resumen, filas de rangos, filas de cercano)` del escenario."""
    lib, ev = LIBRES[k], [f for f in todo if not f["omitido"]]
    gen = [f for f in ev if genu(f)]
    r = resumen(todo)
    kal = r["conteos"].get("KALINA", 0)
    om = sum(1 for f in todo if f["omitido"])
    md = min((f for f in gen if f["D"] is not None),
             key=lambda f: (f["D"], f["id"]), default=None)
    bloq, nbloq = bloqueante(ev)
    cer, rng = [], []
    kalf = [f for f in ev if f["clasificacion"] == "KALINA"]
    if kal:
        c = min(kalf, key=lambda f: (d_punto(f, lib), f["id"]))
        b = max((f for f in kalf if f["eta"] is not None),
                key=lambda f: (f["eta"], -f["id"]), default=None)
        cer = [_fila_punto(k, "cercano", c, lib)]
        cer += [_fila_punto(k, "mejor_eta", b, lib)] if b else []
        rng = rangos_esc(k, ev)
    elif md is not None:
        cer = [_fila_punto(k, "genuino_mD", md, lib)]     # punto de menor D
    c0 = next((f for f in cer if f["tipo"] == "cercano"), None)
    b0 = next((f for f in cer if f["tipo"] == "mejor_eta"), None)
    fila = dict(escenario=k, n=len(todo), omitidos=om, evaluados=len(ev),
                KALINA=kal, genuinos=r["n_genuinos"], N2=r["n_N2"],
                fuera_rango=r["n_fuera"], factible=bool(kal),
                bloqueante=bloq, bloqueante_n=nbloq,
                mejor_D=None if md is None else md["D"],
                mejor_D_id=None if md is None else md["id"],
                cercano_id=None if c0 is None else c0["id"],
                cercano_d=None if c0 is None else c0["d"],
                cercano_eta=None if c0 is None else c0["eta"],
                mejor_eta_id=None if b0 is None else b0["id"],
                mejor_eta=None if b0 is None else b0["eta"],
                suma_t_s=sum(f["t_s"] for f in ev if f["t_s"] is not None))
    return fila, rng, cer


def main() -> None:
    t0 = time.perf_counter()
    todo = leer()
    if not todo:
        raise SystemExit(f"sin filas: falta {OUT / 'm5_lhs.csv'}")
    print(f"m5_analisis | N={len(todo)} | OUT={OUT}", flush=True)
    res, rng, cer = [], [], []
    for k in sorted({f["escenario"] for f in todo}):
        filas = [f for f in todo if f["escenario"] == k]
        a, b, c = analisis_esc(k, filas)
        res.append(a), rng.extend(b), cer.extend(c)
        figura(k, [f for f in filas if not f["omitido"]])
    escribir(OUT, "m5_resumen.csv", CRESUM, res)
    escribir(OUT, "m5_rangos.csv", CRANGOS5, rng)
    escribir(OUT, "m5_cercano_profesor.csv", CCERC, cer)
    rep.generar(res, cer, rng)
    print(f"m5_analisis listo en {time.perf_counter() - t0:.0f} s -> {OUT}",
          flush=True)


if __name__ == "__main__":
    main()
