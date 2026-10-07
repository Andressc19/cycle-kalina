"""M4b — rutas de salida y lectura/escritura de los CSV de M4b (final_M4b §Diseño).

La carpeta de salida es `resultados/2026-10-07_final_M4b` (con `M4B_HUMO=1`,
`.../humo`). Reutiliza la caja, las columnas y el tipado de `m4_datos.py` sin
tocarlo: `leer_de()` lee un CSV de cualquier carpeta (los 300 de M4 viven en
`resultados/2026-10-06_final_M4/`), `leer_union()` concatena los 300 de M4 con
los 200 de M4b —la unión de dos LHS, no un LHS estricto de 500— y
`redirigir()` apunta la ruta fija `OUT` de los módulos M4 que escriben archivos
(`m4_datos`, `m4_arbol`, `m4_figuras`) hacia la carpeta de M4b, para reutilizar
esos módulos sin modificar ningún `m4_*.py` existente.
"""
from __future__ import annotations

import csv, os, sys  # noqa: E401,E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

import m4_datos as m4  # noqa: E402
from m4_datos import BOOL, CAJA, DERIV, FLOT, GENU, VARS10, VARS13  # noqa: E402,F401

HUMO = os.environ.get("M4B_HUMO") == "1"
OUT4 = Path(m4.OUT)                                     # los 300 de M4
OUT = _RAIZ / "resultados" / ("2026-10-07_final_M4b/humo" if HUMO
                              else "2026-10-07_final_M4b")
N_M4B = 4 if HUMO else 200          # puntos nuevos (TASK_CONTEXT final_M4b §1)
ID0 = 300                           # `id_muestra` de 300 a 499
SEED_B = 20261007                   # semilla del LHS nuevo (TASK_CONTEXT §1)


def leer_de(d, nombre: str) -> list:
    """Filas de `d/nombre` con números, booleanos y derivadas ya tipados."""
    with open(Path(d) / nombre, encoding="utf-8", newline="") as fh:
        filas = list(csv.DictReader(fh))
    for f in filas:
        for k in FLOT:
            f[k] = m4.num(f.get(k))
        for k in BOOL:
            v = f.get(k)
            f[k] = None if v in (None, "") else v == "True"
        f["clasificacion"] = f.get("clasificacion") or None
        m4.derivar(f)
    return filas


def leer_union() -> list:
    """Los 300 de M4 más los 200 de M4b (500 filas)."""
    return leer_de(OUT4, "m4_lhs.csv") + leer_de(OUT, "m4b_lhs.csv")


def escribir(d, nombre: str, cab: list, filas: list) -> None:
    """CSV de salida del análisis, en la carpeta `d` (una fila por dict)."""
    with open(Path(d) / nombre, "w", encoding="utf-8", newline="") as fh:
        esc = csv.DictWriter(fh, fieldnames=cab)
        esc.writeheader()
        for f in filas:
            esc.writerow({c: f.get(c) for c in cab})
    print(f"{nombre}: {len(filas)} filas", flush=True)


def leer_plano(d, nombre: str) -> list:
    """CSV crudo (sin tipar) de `d/nombre`, p. ej. `m4_rsa.csv` de M4."""
    with open(Path(d) / nombre, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def redirigir() -> None:
    """Apunta el `OUT` fijo de los módulos M4 hacia la carpeta de M4b."""
    import m4_arbol, m4_figuras  # noqa: E402
    m4.OUT, m4_arbol.OUT, m4_figuras.OUT = OUT, OUT, OUT
    print(f"OUT redirigido -> {OUT}", flush=True)
