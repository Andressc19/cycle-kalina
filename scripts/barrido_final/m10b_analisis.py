"""M10b — parte de análisis: figura y reporte a partir de los CSV de la corrida.

Llama a `m10b_figuras` y a `m10b_reporte`. Las cifras salen de
`m10b_ofat_xb.csv` y `m10b_malla_xb_pbaja.csv`.
"""
from __future__ import annotations

import sys  # noqa: E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

import m10_datos as d10  # noqa: E402
import m10b_datos as d  # noqa: E402
import m10b_figuras  # noqa: E402
import m10b_reporte  # noqa: E402


def main() -> None:
    faltan = [str(d.OUT / n) for n in ("m10b_ofat_xb.csv",
                                       "m10b_malla_xb_pbaja.csv")
              if not (d.OUT / n).exists()]
    if faltan:
        raise SystemExit("Faltan: " + ", ".join(faltan))
    m10b_figuras.main()
    n = m10b_reporte.escribir()
    ma = d10.leer(d.OUT / "m10b_malla_xb_pbaja.csv")
    kal = sum(1 for f in ma if d10.es_kalina(f))
    print(f"REPORTE_M10b.md: {n} líneas", flush=True)
    print(f"malla: {len(ma)} filas, {kal} KALINA", flush=True)


if __name__ == "__main__":
    main()
