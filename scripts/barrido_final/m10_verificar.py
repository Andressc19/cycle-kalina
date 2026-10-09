"""M10 — verificador: recalcula las cifras de `m10_catalogo.csv` y
`m10_ofat_rangos.csv` desde los CSV crudos y comprueba que coincidan.

No escribe nada: imprime OK/FALLA por cada cifra y sale con código 1 si algo
falla. Cualquier FALLA invalida el reporte.
"""
from __future__ import annotations

import sys  # noqa: E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

import m10_datos as d  # noqa: E402

TOL = 1e-6
NOMBRES = {f[0] for f in d.FAMILIAS}
_falla = 0


def chk(nombre, ok, detalle="") -> None:
    global _falla
    if not ok:
        _falla += 1
    print(f'{"OK  " if ok else "FALLA"} {nombre}{" — " + detalle if detalle else ""}',
          flush=True)


def _cerca(a, b) -> bool:
    return (a is None and b is None) or (
        a is not None and b is not None and abs(a - b) < TOL)


def _fuentes() -> dict:
    return {"fase3": d.leer(d.OUT / "m10_recorrida_fase3.csv"),
            "ofat": d.leer(d.OUT / "m10_ofat.csv"),
            "malla": d.leer(d.OUT / "m10_malla_xb_pbaja.csv")}


def verifica_catalogo(fu: dict) -> None:
    cats = d.leer(d.OUT / "m10_catalogo.csv")
    chk("catálogo: n filas", len(cats) == len(d.FAMILIAS) + len(d.OFAT) + 1,
        f"{len(cats)}")
    for c in cats:
        fam = c["familia"]
        if fam in NOMBRES:
            sub = [f for f in fu["fase3"] if f["familia"] == fam]
        elif fam.startswith("B1-"):
            sub = [f for f in fu["ofat"] if f["variable"] == fam[3:]]
        else:
            sub = fu["malla"]
        chk(f'catálogo {fam}: n', c["n"] == len(sub), f'{c["n"]} vs {len(sub)}')
        chk(f'catálogo {fam}: KALINA ahora',
            c["KALINA_ahora"] == sum(1 for f in sub if d.es_kalina(f)))
        chk(f'catálogo {fam}: confiables',
            c["confiables_ahora"] == sum(1 for f in sub if d.confiable(f)))
        if fam in NOMBRES:
            chk(f'catálogo {fam}: coincide',
                c["coincide"] == sum(1 for f in sub if f["coincide_clase"]))
            v = [abs(f["d_eta_pp"]) for f in sub if f.get("d_eta_pp") is not None]
            chk(f'catálogo {fam}: d_eta_pp máx',
                _cerca(c["d_eta_pp_max_abs"], max(v) if v else None))


def verifica_rangos(fu: dict) -> None:
    ran = {r["variable"]: r for r in d.leer(d.OUT / "m10_ofat_rangos.csv")}
    chk("rangos: n filas", len(ran) == len(d.OFAT), f"{len(ran)}")
    for var, _lo, _hi in d.OFAT:
        sub = [f for f in fu["ofat"] if f["variable"] == var]
        kal = [f for f in sub if d.es_kalina(f)]
        r = ran.get(var)
        if not kal:
            chk(f"rangos {var}: sin KALINA", r is None or r["n_kalina"] == 0)
            continue
        etas = [f["eta"] for f in kal if f.get("eta") is not None]
        chk(f"rangos {var}: n KALINA", r["n_kalina"] == len(kal))
        chk(f"rangos {var}: mín/máx",
            _cerca(r["min_kalina"], min(f["valor"] for f in kal))
            and _cerca(r["max_kalina"], max(f["valor"] for f in kal)))
        chk(f"rangos {var}: η mín/máx",
            _cerca(r["eta_min"], min(etas)) and _cerca(r["eta_max"], max(etas)))


def verifica_malla(fu: dict) -> None:
    for xb in d.XB_MALLA:
        sub = [f for f in fu["malla"] if f["x_b"] == xb]
        kal = [f for f in sub if d.es_kalina(f)]
        chk(f"malla x_b={xb:.2f}: n", len(sub) == len(d.PB_MALLA))
        chk(f"malla x_b={xb:.2f}: n KALINA",
            len(kal) == sum(1 for f in sub if d.es_kalina(f)))
        if kal:
            lo = min(f["P_baja"] for f in kal)
            chk(f"malla x_b={xb:.2f}: P_baja mín KALINA",
                lo in {f["P_baja"] for f in kal})


def main() -> None:
    if not d.OUT.exists():
        raise SystemExit(f"No existe {d.OUT}")
    fu = _fuentes()
    verifica_catalogo(fu)
    verifica_rangos(fu)
    verifica_malla(fu)
    chk("figuras: xb_pbaja", (d.OUT / "m10_xb_pbaja.png").exists())
    chk("figuras: ofat", (d.OUT / "m10_ofat.png").exists())
    chk("reporte", (d.OUT / "REPORTE_M10.md").exists())
    print(f"\n{'TODO OK' if _falla == 0 else str(_falla) + ' FALLAS'}", flush=True)
    sys.exit(1 if _falla else 0)


if __name__ == "__main__":
    main()
