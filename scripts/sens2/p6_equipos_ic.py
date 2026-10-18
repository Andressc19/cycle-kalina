# -*- coding: utf-8 -*-
"""Sens2 F1 (ampliacion del director) - intervalos bootstrap de las cifras de turbina que citan E1 y E2.

Con los KALINA (total) de los 4 bloques de p4_comun.cargar(): pendiente de dh_turb sobre rp en el muestreo LHS (estudios 3 y 14)
con IC 95 % y R2; P5, P50 y P95 de rp y dh_turb con IC 95 % (1 000 remuestreos por fila, semilla 20261018) para todos los KALINA
y solo para el LHS. Salidas: p6_equipos_ic.csv y p6_equipos_ic.md.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4_comun as c  # noqa: E402
import p6_comun as K  # noqa: E402

B = 1000


def pendiente(x, y):
    A = np.column_stack([np.ones(len(x)), x])
    b = np.linalg.lstsq(A, y, rcond=None)[0]
    r = y - A @ b
    return b[1], 1 - (r @ r) / ((y - y.mean()) ** 2).sum()


def main():
    d = c.cargar()
    k = d[c.mascara(d, c.REF_TOTAL)]
    lhs = k[k["estudio"].isin([3, 14])]
    rng = np.random.default_rng(K.SEMILLA)
    filas = []
    x, y = lhs["rp"].to_numpy(float), lhs["dh_turb"].to_numpy(float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    b0, r2 = pendiente(x, y)
    bs = []
    for _ in range(B):
        i = rng.integers(0, len(x), len(x))
        bs.append(pendiente(x[i], y[i])[0])
    filas.append(["pendiente dh_turb sobre rp (LHS)", "kJ/kg por unidad de r_P", len(x), b0, np.percentile(bs, 2.5), np.percentile(bs, 97.5), r2])
    for nombre, g in (("todos los KALINA", k), ("solo LHS", lhs)):
        for q in ("rp", "dh_turb"):
            v = g[q].to_numpy(float)
            v = v[np.isfinite(v)]
            for p in (5, 50, 95):
                est = np.percentile(v, p)
                bb = [np.percentile(v[rng.integers(0, len(v), len(v))], p) for _ in range(B)]
                filas.append(["%s P%d (%s)" % (q, p, nombre), "-", len(v), est, np.percentile(bb, 2.5), np.percentile(bb, 97.5), np.nan])
    t = pd.DataFrame(filas, columns=["cantidad", "unidad", "n", "estimador", "ic_lo", "ic_hi", "r2"])
    os.makedirs(K.OUT, exist_ok=True)
    t.to_csv(os.path.join(K.OUT, "p6_equipos_ic.csv"), index=False)
    md = ["# Sens2 F1 - intervalos bootstrap de las cifras de turbina", "",
          "IC 95 %% por bootstrap percentil (%d remuestreos, semilla %d)." % (B, K.SEMILLA), "",
          "| cantidad | n | estimador | IC 95 % |", "|---|---|---|---|"]
    md += ["| %s | %d | %.3f | [%.3f, %.3f] |" % (r.cantidad, r.n, r.estimador, r.ic_lo, r.ic_hi) for r in t.itertuples()]
    with open(os.path.join(K.OUT, "p6_equipos_ic.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
