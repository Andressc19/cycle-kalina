# -*- coding: utf-8 -*-
r"""Sens2 etapa B - eta maxima frente a T_fuente con busqueda local de P_alta, P_baja y x_b (pregunta 3 del profesor).

Para cada banda de T_fuente (353.15 a 573.15 K, cada 20 K) se busca el maximo de eta entre los puntos KALINA con una busqueda
coordenada a coordenada (paso inicial 600 kPa en P_alta, 100 kPa en P_baja, 0.03 en x_b; el paso se divide a la mitad tras un
ciclo sin mejora; tope de MAX_EVAL evaluaciones por banda). El resto de variables quedan fijas en los valores de abajo (SUPUESTO de
escenario, los del centro C1 salvo T_sumidero). Solo cuentan como factibles los puntos clasificados KALINA. Arranque: el mejor KALINA
del conjunto original a menos de 10 K de la banda; si no hay, el primer factible de una diagonal de 9 arranques.
Cada banda escribe en su propio archivo (`s2b_opt_<K>.csv`) y reanuda desde el (cache por combo). Uso:
    ..\\..\\..\\.venv\\Scripts\\python.exe scripts\\sens2\\s2b_opt_T.py [N_PROCESOS]
"""
import csv
import os
import sys
from multiprocessing import get_context
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR), str(_DIR.parents[0] / "barrido_final")]

OUT = _RAIZ / "resultados" / "2026-10-18_sens2_B"
BANDAS = [353.15 + 20.0 * i for i in range(12)]
FIJAS = dict(T_sumidero=280.5, eta_t=0.85, eta_p=0.80, eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.95, m_b=1.0)
LIM = dict(P_alta=(1500.0, 9000.0), P_baja=(300.0, 2500.0), x_b=(0.50, 0.95))
PASO0 = dict(P_alta=600.0, P_baja=100.0, x_b=0.03)
BASE = dict(P_alta=3300.0, P_baja=900.0, x_b=0.85)
MAX_EVAL = 30
DEDUP = _RAIZ / "resultados" / "2026-10-17_sens2_P2" / "p2_dataset_dedup.csv"


def _clave(c):
    return (round(c["P_alta"], 1), round(c["P_baja"], 1), round(c["x_b"], 4))


def _inicio(T):
    import pandas as pd
    d = pd.read_csv(DEDUP)
    g = d[(d["clasificacion"] == "KALINA") & ((d["T_fuente"] - T).abs() <= 10.0)]
    if len(g):
        r = g.sort_values("eta_pct", ascending=False).iloc[0]
        return dict(P_alta=float(r["P_alta"]), P_baja=float(r["P_baja"]), x_b=float(r["x_b"])), True
    return dict(BASE), False


def _ok(c):
    return all(LIM[k][0] <= c[k] <= LIM[k][1] for k in LIM) and c["P_alta"] >= 1.3 * c["P_baja"]


def banda(T):
    """Optimiza una banda (corre en un hijo); escribe fila a fila y devuelve el mejor (eta, combo)."""
    import comun
    cols = ["id_punto", "banda", "n_eval", "paso"] + list(comun.COLS) + list(comun.COLS_EXTRA)
    ruta = OUT / ("s2b_opt_%d.csv" % round(T))
    OUT.mkdir(parents=True, exist_ok=True)
    cache = {}
    if ruta.exists():
        with open(ruta, encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                cache[(round(float(r["P_alta"]), 1), round(float(r["P_baja"]), 1), round(float(r["x_b"]), 4))] = r
    nuevo = not ruta.exists()
    fh = open(ruta, "a", encoding="utf-8", newline="")
    esc = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
    if nuevo:
        esc.writeheader()
    n = [len(cache)]

    def evalua(c, paso):
        k = _clave(c)
        if k in cache:
            r = cache[k]
        else:
            combo = dict(c, T_fuente=T, **FIJAS)
            n[0] += 1
            r = comun.evaluar_punto(combo, motor="teqp", tag="OT-%d-%03d" % (round(T), n[0]), t_amb_diseno=FIJAS["T_sumidero"], extra=True)
            r.update(id_punto="OT-%d-%03d" % (round(T), n[0]), banda=T, n_eval=n[0], paso=paso)
            esc.writerow({k2: r.get(k2) for k2 in cols})
            fh.flush()
            cache[k] = r
            print("[%d K] %d %s eta=%s t=%.0fs" % (round(T), n[0], r.get("clasificacion"), r.get("eta"), float(r.get("t_s") or 0)), flush=True)
        ok = r.get("clasificacion") == "KALINA"
        return (float(r["eta"]) if ok and r.get("eta") not in (None, "") else None)

    c, hay = _inicio(T)
    eta = evalua(c, 0) if _ok(c) else None
    if eta is None:                                             # diagonal de arranques
        for pa, pb, xb in ((3300, 900, .85), (2500, 700, .75), (4500, 1200, .92), (3300, 700, .80), (4000, 900, .85), (2500, 900, .90),
                           (5500, 1200, .88), (3300, 1100, .70), (6500, 1500, .90)):
            cand = dict(P_alta=float(pa), P_baja=float(pb), x_b=float(xb))
            e = evalua(cand, 0) if _ok(cand) else None
            if e is not None:
                c, eta = cand, e
                break
    if eta is None:
        fh.close()
        return T, None, None
    paso = dict(PASO0)
    while n[0] < MAX_EVAL and max(paso["P_alta"] / PASO0["P_alta"], 0) > 0.2:
        mejoro = False
        for v in ("P_alta", "P_baja", "x_b"):
            for s in (1.0, -1.0):
                cand = dict(c)
                cand[v] = round(c[v] + s * paso[v], 4)
                if not _ok(cand) or _clave(cand) in cache and cache[_clave(cand)] is None:
                    continue
                e = evalua(cand, paso[v])
                if e is not None and e > eta + 1e-9:
                    c, eta, mejoro = cand, e, True
                    break
            if n[0] >= MAX_EVAL:
                break
        if not mejoro:
            paso = {k: x / 2.0 for k, x in paso.items()}
    fh.close()
    return T, eta, c


def main(argv):
    n = int(argv[1]) if len(argv) > 1 else 5
    ctx = get_context("spawn")
    with ctx.Pool(n) as p:
        for T, eta, c in p.imap_unordered(banda, BANDAS):
            print("FIN banda %d K: eta max %s en %s" % (round(T), eta, c), flush=True)
    print("fin [OPT_T]: todas las bandas", flush=True)


if __name__ == "__main__":
    main(sys.argv)
