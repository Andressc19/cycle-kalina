"""M2 — hojas de nivel 1 en `datos/Excel_final_kalina.xlsx` (TASK_CONTEXT §4).

Abre el libro que ya escribió `excel_final.py`, crea o reemplaza las hojas
`M2_N1_malla`, `M2_N1_biseccion`, `M2_N1_fronteras` y `M2_N1_resumen` a partir
de los CSV de `resultados/2026-10-06_final_M2/`, reutilizando
`excel_final.escribir_tabla` (mismo formato y descripción), y añade o actualiza
las filas de esas hojas en `Resumen`. Es idempotente: al correrlo dos veces el
libro queda igual. Se corre SIEMPRE después de `excel_final.py`, que
reconstruye el libro desde cero y por eso borra estas hojas.
"""
from __future__ import annotations

import sys
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
for _p in (str(_RAIZ), str(_DIR), str(_DIR.parent)):   # parent = scripts/
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pandas as pd  # noqa: E402
from openpyxl import load_workbook  # noqa: E402
from openpyxl.utils import get_column_letter  # noqa: E402

import excel_final as ef  # noqa: E402

CAMPA = _RAIZ / "resultados" / "2026-10-06_final_M2"
XLSX = ef.XLSX
# hoja -> (csv de origen, descripción que va al pie de la tabla)
HOJAS = (
    ("M2_N1_malla", "m2n1_malla.csv",
     "M2 nivel 1 · Fase A: una sola variable cambia por fila sobre el punto del "
     "profesor (10 valores equiespaciados por variable; las demás, fijas)."),
    ("M2_N1_biseccion", "m2n1_biseccion.csv",
     "M2 nivel 1 · Fase B: puntos medios de la bisección; `iteracion` es la ronda "
     "y `frontera` el criterio que se acota (convergencia o KALINA)."),
    ("M2_N1_fronteras", "m2n1_fronteras.csv",
     "M2 nivel 1: una fila por frontera; `lado_si` es el extremo que cumple el "
     "criterio, `lado_no` el que no, y `ancho_final` = hi − lo tras la bisección."),
    ("M2_N1_resumen", "m2n1_resumen.csv",
     "M2 nivel 1: una fila por variable; los conteos suman malla + bisección y "
     "`d_normalizada` = |v − v_prof|/(b − a) del valor KALINA más cercano."),
)
# Unidades nuevas (TASK §4). `valor`, `ancho_final`, `lado_si` y `lado_no`
# mezclan kPa/K/(−) según la variable y en una sola columna no pueden variar,
# por eso van sin unidad: la columna `variable` de la misma fila la dice.
UNIDADES = {"valor": "\u2212", "ancho_final": "\u2212", "lado_si": "\u2212",
            "lado_no": "\u2212", "d_normalizada": "\u2212"}


def _fila_resumen(hoja: str, df) -> list:
    """Fila de `Resumen`: [hoja, filas, KALINA, CORREGIBLE, INVIABLE,
    NO_CONVERGIO, errores_inesperados], con el conteo por clase de esa hoja."""
    if "clasificacion" in df:
        n = df["clasificacion"].value_counts()
        err = int(df["error_inesperado"].notna().sum())
    elif "clase_lado_si" in df:
        n, err = df["clase_lado_si"].value_counts(), 0
    else:   # M2_N1_resumen: sin columna de clase propia; suma sus n_* (malla+bisección)
        n = {c: int(df["n_" + c.lower()].fillna(0).sum()) for c in ef.CLASES}
        err = 0
    return [hoja, len(df)] + [int(n.get(c, 0)) for c in ef.CLASES] + [err]


def _ultima_fila(ws) -> int:
    """Última fila de datos de `Resumen` (deja fuera las 2 vacías y la descripción)."""
    ult = 1
    for r in range(2, ws.max_row + 1):
        v = ws.cell(r, 1).value
        if v in (None, "") or str(v).startswith("Descripción"):
            break
        ult = r
    return ult


def _reescribir_resumen(ws, filas: list) -> None:
    """Actualiza las filas M2_N1_ de `Resumen`: quita las viejas y reinserta."""
    for r in range(ws.max_row, 1, -1):
        if str(ws.cell(r, 1).value or "").startswith("M2_N1_"):
            ws.delete_rows(r)
    pos = _ultima_fila(ws) + 1
    ws.insert_rows(pos, len(filas))
    for k, fila in enumerate(filas):
        for j, v in enumerate(fila, 1):
            ws.cell(pos + k, j, v)
    j = 1
    while ws.cell(1, j + 1).value is not None:
        j += 1
    ws.auto_filter.ref = f"A1:{get_column_letter(j)}{pos + len(filas) - 1}"


def main() -> None:
    faltan = [c for _h, c, _e in HOJAS if not (CAMPA / c).exists()]
    if not XLSX.exists():
        raise SystemExit(f"No existe {XLSX}: correr antes scripts/barrido_final/excel_final.py")
    if faltan:
        raise SystemExit(f"Faltan en {CAMPA}: {', '.join(faltan)} (correr m2_nivel1.py)")
    ef.UNIDAD.update(UNIDADES)
    wb = load_workbook(XLSX)
    if "Resumen" not in wb.sheetnames:
        raise SystemExit("El libro no tiene la hoja Resumen: correr antes excel_final.py")
    for hoja in [h for h, _c, _e in HOJAS if h in wb.sheetnames]:
        del wb[hoja]
    filas_resumen = []
    for hoja, csv, extra in HOJAS:
        df = pd.read_csv(CAMPA / csv)
        ef.escribir_tabla(wb, hoja, list(df.columns), df.values.tolist(), extra=[extra])
        filas_resumen.append(_fila_resumen(hoja, df))
    _reescribir_resumen(wb["Resumen"], filas_resumen)
    wb.save(XLSX)
    print(f"escrito {XLSX}")
    print("hojas:", wb.sheetnames)


if __name__ == "__main__":
    main()
