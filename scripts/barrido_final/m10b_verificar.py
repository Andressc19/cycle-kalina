"""M10b — verificador: recalcula las cifras de `REPORTE_M10b.md` desde los CSV.

Comprueba que la malla tenga todas sus filas, que la P_baja mínima KALINA por
x_b coincida con la tabla del reporte y con un cálculo independiente, y que el
reporte y la figura existan. No escribe nada; sale con código 1 si algo falla.
"""
from __future__ import annotations

import re  # noqa: E402
import sys  # noqa: E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

import m10_datos as d10  # noqa: E402
import m10b_datos as d  # noqa: E402
import m10b_reporte as rep  # noqa: E402

TOL = 1e-6
_falla = 0
_FILA = re.compile(r"^\|\s*(0\.\d{2})\s*\|\s*([^|]+?)\s*\|")


def chk(nombre, ok, detalle="") -> None:
    global _falla
    if not ok:
        _falla += 1
    print(f'{"OK  " if ok else "FALLA"} {nombre}{" — " + detalle if detalle else ""}',
          flush=True)


def _cerca(a, b) -> bool:
    return (a is None and b is None) or (
        a is not None and b is not None and abs(a - b) < TOL)


def _pbaja_indep(ma: list) -> dict:
    """P_baja mínima KALINA por x_b, calculada aparte del reporte."""
    res = {}
    for f in ma:
        if d10.es_kalina(f) and (f["x_b"] not in res
                                 or f["P_baja"] < res[f["x_b"]]):
            res[f["x_b"]] = f["P_baja"]
    return res


def _pmin_reporte() -> dict:
    """Lee la tabla de P_baja mínima KALINA directamente del reporte."""
    res = {}
    for ln in rep.RUTA.read_text(encoding="utf-8").splitlines():
        m = _FILA.match(ln)
        if not m:
            continue
        celda = m.group(2).strip()
        res[round(float(m.group(1)), 2)] = None if celda == "—" else float(celda)
    return res


def main() -> None:
    if not d.OUT.exists():
        raise SystemExit(f"No existe {d.OUT}")
    of = d10.leer(d.OUT / "m10b_ofat_xb.csv")
    ma = d10.leer(d.OUT / "m10b_malla_xb_pbaja.csv")
    n_of = 1 if d.HUMO else 17
    n_ma = 1 if d.HUMO else 54
    chk("ofat: n filas", len(of) == n_of, f"{len(of)} vs {n_of}")
    chk("malla: n filas", len(ma) == n_ma, f"{len(ma)} vs {n_ma}")
    chk("malla: cada x_b con sus P_baja",
        all(sum(1 for f in ma if f["x_b"] == xb) == (1 if d.HUMO else len(d.PB_MALLA))
            for xb in sorted({f["x_b"] for f in ma})))
    indep = _pbaja_indep(ma)
    repf = rep.pbaja_min_kalina(ma)
    chk("pbaja mín KALINA: independiente == reporte",
        all(_cerca(indep.get(xb), repf[xb]) for xb in d.XB_MALLA))
    leido = _pmin_reporte()
    chk("tabla del reporte == independiente",
        all(_cerca(leido.get(xb), indep.get(xb)) for xb in d.XB_MALLA),
        f"{len(leido)} filas leídas")
    codigos = {c.strip() for f in ma if f["x_b"] < d.XB_BAJO
               for c in (f.get("codigos_falla") or "").split(",") if c.strip()}
    cr = rep.criterio_bajo(ma)
    chk("criterio con x_b bajo == códigos del CSV",
        set(cr) == codigos, f"reporte {sorted(cr)} vs CSV {sorted(codigos)}")
    chk("figura", (d.OUT / "m10b_xb.png").exists())
    chk("reporte", rep.RUTA.exists())
    chk("etiqueta x_b bajo en el reporte",
        "x_b bajo (< 0.55)" in rep.RUTA.read_text(encoding="utf-8"))
    print(f"\n{'TODO OK' if _falla == 0 else str(_falla) + ' FALLAS'}", flush=True)
    sys.exit(1 if _falla else 0)


if __name__ == "__main__":
    main()
