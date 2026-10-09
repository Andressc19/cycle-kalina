"""M9 — paso 4: `m9_rangos.csv` (rangos por escenario con KALINA).

Junta las filas del paso 1 y del paso 2, y por cada conjunto con KALINA calcula
mín, p5, mediana, p95 y máx de cada variable libre más `dP` y `rP`, dentro de los
KALINA y dentro de los KALINA confiables, y el KS (RSA) contra los no KALINA
genuinos cuando hay ≥ 10 KALINA. Llama a `m9_reporte.py` para `REPORTE_M9.md`.
Las figuras van en `m9_figuras.py`. Todas las cifras salen de los CSV.
"""
from __future__ import annotations

import csv, sys  # noqa: E401,E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

import numpy as np  # noqa: E402
from scipy.stats import ks_2samp  # noqa: E402

import m9_datos as m9  # noqa: E402
import m9_reporte  # noqa: E402

CRAN = ["conjunto", "ambito", "variable", "n", "min", "p05", "mediana", "p95",
        "max", "ks_estadistico", "ks_p"]
AMB = ("todos los KALINA", "KALINA confiable")


def stats(vals: list) -> dict:
    """n, mín, p5, mediana, p95 y máx de `vals` (vacío -> `None`)."""
    if not vals:
        return dict(n=0, min=None, p05=None, mediana=None, p95=None, max=None)
    a = np.array(vals, dtype=float)
    p05, med, p95 = np.percentile(a, [5, 50, 95])
    return dict(n=len(vals), min=float(a.min()), p05=float(p05),
                mediana=float(med), p95=float(p95), max=float(a.max()))


def ks(b: list, bb: list):
    """`(KS, p)` de `scipy.stats.ks_2samp`; `(None, None)` sin ambos grupos."""
    if not b or not bb:
        return None, None
    r = ks_2samp(b, bb)
    return float(r.statistic), float(r.pvalue)


def escenarios() -> dict:
    """`{conservados: (codes, filas)}` del paso 1 y del paso 2."""
    out: dict = {}

    def add(f):
        key = f["conservados"]
        if key not in out:
            out[key] = (key.split("+"), [])
        out[key][1].append(f)
    for f in m9.leer(m9.OUT / "m9_paso1.csv"):
        add(f)
    for f in m9.leer(m9.OUT / "m9_paso2.csv"):
        add(f)
    return out


def rangos(esc: dict) -> list:
    """Una fila por (conjunto, ámbito, variable) para los conjuntos con KALINA."""
    out = []
    for key, (codes, rows) in esc.items():
        kal = [f for f in rows if m9.es_kalina(f)]
        if not kal:
            continue
        lib = m9.libres(codes) + ["dP", "rP"]
        nog = [f for f in rows if m9.genu(f) and not m9.es_kalina(f)]
        for amb in AMB:
            sel = kal if amb == AMB[0] else [f for f in kal if m9.confiable(f)]
            if not sel:
                continue
            for v in lib:
                vals = [f[v] for f in sel if f.get(v) is not None]
                ks_v = ks_p = None
                if amb == AMB[0] and len(kal) >= 10:
                    ks_v, ks_p = ks(
                        [f[v] for f in kal if f.get(v) is not None],
                        [f[v] for f in nog if f.get(v) is not None])
                out.append(dict(conjunto=key, ambito=amb, variable=v,
                                **stats(vals), ks_estadistico=ks_v,
                                ks_p=ks_p))
    return out


def main() -> None:
    m9.OUT.mkdir(parents=True, exist_ok=True)
    esc = escenarios()
    ran = rangos(esc)
    with open(m9.OUT / "m9_rangos.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CRAN)
        w.writeheader()
        w.writerows({c: r.get(c) for c in CRAN} for r in ran)
        fh.flush()
    esc_rows = m9.leer(m9.OUT / "m9_escalera.csv")
    n = m9_reporte.escribir(ran, esc_rows, esc)
    print(f"m9_rangos.csv: {len(ran)} filas", flush=True)
    print(f"REPORTE_M9.md: {n} líneas", flush=True)


if __name__ == "__main__":
    main()
