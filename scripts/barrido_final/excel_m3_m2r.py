"""M3/M2R — hojas de las campañas M3 (sensibilidad local) y M2R (ε/η en [0.40, 0.95])
en `datos/Excel_final_kalina.xlsx` (TASK_CONTEXT).

Abre el libro que ya escribieron `excel_final.py` y `excel_m2.py`, crea o
reemplaza las hojas M3_* y M2R_* con los CSV de `resultados/2026-10-06_final_M3/`
y `resultados/2026-10-06_final_M2R/` vía `excel_final.escribir_tabla` (mismo
formato, unidades, colores de clase, filtro y descripción al pie), y añade o
actualiza sus filas en `Resumen`. Las M2R_n* juntan malla y bisección con la
columna `fase`; `M3_figuras` lleva el tornado de Δη. Es idempotente y se corre
SIEMPRE después de `excel_final.py` (que reconstruye el libro) y de `excel_m2.py`.
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
from formatear_excel_barridos import estilo_titulo  # noqa: E402

M3 = _RAIZ / "resultados" / "2026-10-06_final_M3"
M2R = _RAIZ / "resultados" / "2026-10-06_final_M2R"
XLSX = ef.XLSX
FIGURA = "M3_figuras"
# hoja -> (carpeta, [csv de origen], descripción que va al pie de la tabla)
HOJAS = (
    ("M3_ofat", M3, ["m3_ofat.csv"],
     "M3 · malla OAT alrededor del ancla A*: cada fila cambia UNA variable "
     "(15 valores entre a y b; las demás, en A*) más el ancla y los dos "
     "vecinos ±h = 0.01·(b − a) de cada variable, para la elasticidad."),
    ("M3_resumen", M3, ["m3_resumen.csv"],
     "M3: una fila por variable; `E_eta` es la elasticidad de η en A* (vacía "
     "con el motivo en `motivo_E`), `delta_eta` = máx η − min η de la malla "
     "y `kalina_desde/hasta` el tramo de la malla con clase KALINA."),
    ("M3_cruces", M3, ["m3_cruces.csv"],
     "M3: una fila por frontera; `tipo` = margen (cambio de signo de "
     "m_O1/m_O2/m_O5, con `v_cruce` interpolado) o clase (cambio de clase "
     "entre dos vecinos de la malla, con `v_cruce` vacío)."),
    ("M2R_n1", M2R, ["m2r_n1_malla.csv", "m2r_n1_biseccion.csv"],
     "M2R nivel 1: malla de 12 valores de la variable en [0.40, 0.95] (las "
     "demás, en el punto del profesor) y bisección donde cambie \"es genuino\" "
     "o \"es KALINA\"; `fase` distingue unas filas de otras."),
    ("M2R_n2a", M2R, ["m2r_n2a_malla.csv", "m2r_n2a_biseccion.csv"],
     "M2R nivel 2, ruta (eps_hrvg, eps_cond): malla 5 × 12 con P_baja = 400 "
     "kPa y bisección sobre eps_cond (tolerancia 0.005); `fase` distingue "
     "unas filas de otras."),
    ("M2R_n2b", M2R, ["m2r_n2b_malla.csv", "m2r_n2b_biseccion.csv"],
     "M2R nivel 2, ruta (eps_hrvg, P_baja): malla 4 × 12 con P_baja de 400 "
     "a 2000 kPa y bisección sobre P_baja (tolerancia 10 kPa); `fase` "
     "distingue unas filas de otras."),
    ("M2R_n3", M2R, ["m2r_n3_malla.csv"],
     "M2R nivel 3: malla (T_fuente, eps_cond) con P_baja del profesor; sin bisección."),
    ("M2R_fronteras", M2R, ["m2r_fronteras.csv"],
     "M2R: una fila por frontera; `lado_si` es el extremo que cumple el criterio, "
     "`lado_no` el que no, y `ancho_final` = hi − lo tras la bisección."),
    ("M2R_kalina", M2R, ["m2r_kalina.csv"],
     "M2R: los puntos KALINA de las tres partes; `n_cambios` = cuántas "
     "variables difieren del punto del profesor y `d` = Σ |v − v_prof|/"
     "(b − a) con los rangos de M3."),
    ("M2R_resumen", M2R, ["m2r_resumen.csv"],
     "M2R: una fila por (parte, var1); `n_genuinos`, `n_kalina` y `n_N2` "
     "suman malla + bisección, y `menor_d`/`mayor_eta` son los KALINA de "
     "menor distancia al profesor y de mayor η de la fila."),
)
# Unidades que las reglas no cubren: los conteos van en "n"; el resto, en "-" (mezcla kPa/K/(−)).
UNIDADES = {"n_genuinos": "n", "n_kalina": "n", "n_N2": "n", "n_cambios": "n",
            "iteracion": "n", "iteraciones": "n", "repliegues_lo": "n",
            "repliegues_hi": "n"}


def _leer(hoja: str, carpeta: Path, csvs: list) -> pd.DataFrame:
    """CSV de una hoja; las M2R_n* juntan malla y bisección con columna `fase`."""
    dfs = [pd.read_csv(carpeta / c) for c in csvs]
    if not hoja.startswith("M2R_n"):
        return dfs[0]
    fases = ["biseccion" if "biseccion" in c else "malla" for c in csvs]
    ref = max(dfs, key=lambda d: d.shape[1])   # la bisección: trae más columnas
    orden = ["fase"] + list(ref.columns) + [c for d in dfs for c in d.columns
                                            if c not in ref.columns]
    return pd.concat([d.assign(fase=f) for f, d in zip(fases, dfs)],
                     ignore_index=True)[orden]


def _fila_resumen(hoja: str, df, todo=None) -> list:
    """Fila de `Resumen`: [hoja, filas, KALINA, CORREGIBLE, INVIABLE, NO_CONVERGIO,
    errores_inesperados]; el conteo de clase es el de la propia hoja."""
    n, err = {}, 0
    if "clasificacion" in df:
        n = df["clasificacion"].value_counts()
        err = int(df["error_inesperado"].notna().sum())
    elif "clase_si" in df:      # M2R_fronteras: la clase del lado que cumple
        n = df["clase_si"].value_counts()
    elif "clase_j1" in df:      # M3_cruces: la clase del punto j+1 de cada cruce
        n = df["clase_j1"].value_counts()
    elif "d" in df:             # M2R_kalina: todas sus filas son KALINA
        n = {"KALINA": len(df)}
    else:                       # M3_resumen / M2R_resumen: puntos de la campaña
        if todo is None:
            raise SystemExit(f"{hoja} necesita los puntos de la campaña")
        n = todo["clasificacion"].value_counts()
        err = int(todo["error_inesperado"].notna().sum())
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
    """Actualiza las filas M3_/M2R_ de `Resumen`: quita las viejas y reinserta."""
    for r in range(ws.max_row, 1, -1):
        if str(ws.cell(r, 1).value or "").startswith(("M3_", "M2R_")):
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


def _figuras(wb) -> str:
    """Hoja `M3_figuras` con el tornado de Δη; sin Pillow o sin el PNG solo la ruta."""
    ruta = M3 / "m3_tornado.png"
    rel = ruta.relative_to(_RAIZ).as_posix()
    ws = wb.create_sheet(FIGURA)
    for j, t in enumerate(("figura", "ruta"), 1):
        estilo_titulo(ws.cell(1, j, t), "texto")
    ws.cell(2, 1, ruta.name)
    ws.cell(2, 2, rel)
    ws.cell(3, 1, "Tornado de Δη de M3: barras horizontales de Δη_i por variable, de mayor a menor.")
    ws.freeze_panes = "A2"
    ws.column_dimensions["A"].width = 24
    ws.column_dimensions["B"].width = 64
    try:
        from openpyxl.drawing.image import Image as XLImage
    except ImportError:
        ws.cell(5, 1, "Pillow no disponible: la imagen no se insertó; la ruta está arriba.")
        return f"{FIGURA}: sin Pillow, solo la ruta {rel}"
    if not ruta.exists():
        ws.cell(5, 1, f"No existe {rel}: la imagen no se insertó.")
        return f"{FIGURA}: falta {rel}"
    ws.add_image(XLImage(str(ruta)), "A6")
    return f"imagen insertada en {FIGURA} ({rel})"


def main() -> None:
    faltan = [c for _h, _p, cs, _e in HOJAS for c in cs if not (_p / c).exists()]
    if not XLSX.exists():
        raise SystemExit(f"No existe {XLSX}: correr antes scripts/barrido_final/excel_final.py")
    if faltan:
        raise SystemExit(f"Faltan CSV: {', '.join(faltan)}")
    ef.UNIDAD.update(UNIDADES)
    wb = load_workbook(XLSX)
    if "Resumen" not in wb.sheetnames:
        raise SystemExit("El libro no tiene la hoja Resumen: correr antes excel_final.py y excel_m2.py")
    viejas = [h for h, _p, _c, _e in HOJAS if h in wb.sheetnames]
    for hoja in viejas + ([FIGURA] if FIGURA in wb.sheetnames else []):
        del wb[hoja]
    # puntos de la campaña: cuentan las clases de las dos hojas-resumen
    puntos: dict = {}
    for _h, c, cs, _e in HOJAS:
        if not _h.endswith(("_resumen", "_cruces", "_fronteras", "_kalina")):
            puntos.setdefault(c, []).extend(pd.read_csv(c / x) for x in cs)
    todo = {c: pd.concat(v, ignore_index=True) for c, v in puntos.items()}
    filas = []
    for hoja, carpeta, csvs, desc in HOJAS:
        df = _leer(hoja, carpeta, csvs)
        ef.escribir_tabla(wb, hoja, list(df.columns), df.values.tolist(), extra=[desc])
        filas.append(_fila_resumen(hoja, df, todo.get(carpeta)))
    msg = _figuras(wb)
    _reescribir_resumen(wb["Resumen"], filas)
    wb.save(XLSX)
    print(f"escrito {XLSX}")
    print("hojas:", wb.sheetnames)
    print(msg)


if __name__ == "__main__":
    main()
