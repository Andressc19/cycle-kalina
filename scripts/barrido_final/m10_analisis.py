"""M10 — Parte C: `m10_catalogo.csv` y `m10_ofat_rangos.csv`.

El catálogo tiene una fila por familia (F3-A…F3-E, B1-<variable> y B2) con su
origen, variables movidas, piso de O2, n y los conteos de clase antes y ahora;
en las familias de la Fase 3 también el n de coincidencias de clase y el d_eta_pp
(medio y máximo, en valor absoluto). Los rangos de B1 dan, por variable, el tramo
KALINA y el criterio que lo rompe a cada lado. Llama a `m10_figuras` y a
`m10_reporte`. Todas las cifras salen de los CSV.
"""
from __future__ import annotations

import csv, statistics, sys  # noqa: E401,E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

import m10_datos as d  # noqa: E402
import m10_figuras  # noqa: E402
import m10_reporte  # noqa: E402

CAT = ["familia", "origen", "variables_movidas", "piso_O2", "n", "KALINA_sept",
       "KALINA_ahora", "confiables_ahora", "coincide", "d_eta_pp_medio_abs",
       "d_eta_pp_max_abs"]
RAN = ["variable", "min_kalina", "max_kalina", "criterio_bajo", "criterio_alto",
       "eta_min", "eta_max", "n_kalina"]


def _d_eta(sub: list):
    """(medio, máximo) de |d_eta_pp|, o (None, None) si no hay ninguno."""
    v = [abs(f["d_eta_pp"]) for f in sub if f.get("d_eta_pp") is not None]
    return (None, None) if not v else (statistics.fmean(v), max(v))


def fila_cat(fam, origen, mov, piso, sub, con_sept) -> dict:
    """Una fila del catálogo para la familia `fam`."""
    med, mx = _d_eta(sub) if con_sept else (None, None)
    return dict(familia=fam, origen=origen, variables_movidas=mov, piso_O2=piso,
                n=len(sub),
                KALINA_sept=(sum(1 for f in sub if f.get("clase_sept") == "KALINA")
                             if con_sept else None),
                KALINA_ahora=sum(1 for f in sub if d.es_kalina(f)),
                confiables_ahora=sum(1 for f in sub if d.confiable(f)),
                coincide=(sum(1 for f in sub if f.get("coincide_clase"))
                          if con_sept else None),
                d_eta_pp_medio_abs=med, d_eta_pp_max_abs=mx)


def catalogo() -> list:
    """F3-A…F3-E + B1-<variable> + B2."""
    f3 = d.leer(d.OUT / "m10_recorrida_fase3.csv")
    of = d.leer(d.OUT / "m10_ofat.csv")
    ma = d.leer(d.OUT / "m10_malla_xb_pbaja.csv")
    out = [fila_cat(fam, "sept", mov, piso, [f for f in f3 if f["familia"] == fam],
                    True) for fam, _a, piso, mov in d.FAMILIAS]
    out += [fila_cat(f"B1-{var}", "nuevo", var, d.PISO_B,
                     [f for f in of if f["variable"] == var], False)
            for var, _lo, _hi in d.OFAT]
    out.append(fila_cat("B2", "nuevo", "x_b x P_baja", d.PISO_B, ma, False))
    return out


def _crit(f) -> str:
    """Criterio que clasifica la fila: clase y códigos de falla."""
    cod = (f.get("codigos_falla") or "").replace(",", "+")
    return f'{f.get("clasificacion")}{f" ({cod})" if cod else ""}'


def rangos() -> list:
    """Una fila por variable de B1: tramo KALINA y criterio a cada lado."""
    of = d.leer(d.OUT / "m10_ofat.csv")
    out = []
    for var, _lo, _hi in d.OFAT:
        sub = sorted((f for f in of if f["variable"] == var),
                     key=lambda f: f["valor"])
        kal = [f for f in sub if d.es_kalina(f)]
        if not kal:
            out.append(dict.fromkeys(RAN, None, variable=var, n_kalina=0))
            continue
        vmin, vmax = min(f["valor"] for f in kal), max(f["valor"] for f in kal)
        abajo = [f for f in sub if not d.es_kalina(f) and f["valor"] < vmin]
        arriba = [f for f in sub if not d.es_kalina(f) and f["valor"] > vmax]
        etas = [f["eta"] for f in kal if f.get("eta") is not None]
        out.append(dict(
            variable=var, min_kalina=vmin, max_kalina=vmax,
            criterio_bajo=(_crit(max(abajo, key=lambda f: f["valor"]))
                           if abajo else None),
            criterio_alto=(_crit(min(arriba, key=lambda f: f["valor"]))
                           if arriba else None),
            eta_min=min(etas) if etas else None,
            eta_max=max(etas) if etas else None, n_kalina=len(kal)))
    return out


def _escribir(nombre, cols, filas) -> None:
    with open(d.OUT / nombre, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows({c: f.get(c) for c in cols} for f in filas)
        fh.flush()


def main() -> None:
    d.OUT.mkdir(parents=True, exist_ok=True)
    cat, ran = catalogo(), rangos()
    _escribir("m10_catalogo.csv", CAT, cat)
    _escribir("m10_ofat_rangos.csv", RAN, ran)
    print(f"m10_catalogo.csv: {len(cat)} filas", flush=True)
    print(f"m10_ofat_rangos.csv: {len(ran)} filas", flush=True)
    m10_figuras.main()
    print(f"REPORTE_M10.md: {m10_reporte.escribir(cat, ran)} líneas", flush=True)


if __name__ == "__main__":
    main()
