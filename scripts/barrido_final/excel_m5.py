"""M5 — hojas de la campaña M5 (5 escenarios × 120 puntos LHS) en `datos/Excel_final_kalina.xlsx`.

Abre el libro que ya escribieron `excel_final.py`, `excel_m2.py`,
`excel_m3_m2r.py` y `excel_m2s_m4.py`, crea o reemplaza las hojas M5_* con los
CSV de `resultados/2026-10-07_final_M5/` vía `excel_final.escribir_tabla`
(mismo formato, unidades, colores de clase, filtro y descripción al pie), monta
la tabla fija `M5_escenarios` (5 filas; `KALINA_LHS` es el `KALINA` de la fila
del escenario en `m5_resumen.csv`) y `M5_figuras` con las cinco PNG S1…S5, y
añade o actualiza sus filas en `Resumen`. Es idempotente y se corre SIEMPRE el
último de los cinco.
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

M5 = _RAIZ / "resultados" / "2026-10-07_final_M5"
XLSX = ef.XLSX
FIGURA = "M5_figuras"
FIGS = tuple(f"m5_S{k}.png" for k in range(1, 6))
CAB_ESC = ["escenario", "se_conserva", "variables_libres", "KALINA_LHS", "nota"]
# hoja -> (csv de origen, descripción que va al pie de la tabla)
HOJAS = (
    ("M5_lhs", "m5_lhs.csv",
     "M5: los 600 puntos LHS (5 escenarios × 120); `escenario` dice de cuál sale cada fila y `omitido` marca la restricción P_baja ≥ P_alta − 300, que descarta el punto antes de evaluarlo."),
    ("M5_resumen", "m5_resumen.csv",
     "M5: una fila por escenario; `factible` = ¿hay algún KALINA?, `bloqueante`/`bloqueante_n` es el código de falla dominante entre los genuinos que no son KALINA, y `suma_t_s` suma el tiempo de los puntos evaluados."),
    ("M5_rangos", "m5_rangos.csv",
     "M5: min, p05, mediana, p95 y max de cada variable libre (más dP y rP cuando las presiones no están fijas) por grupo KALINA / no_KALINA, con el KS y su valor p cuando hay ≥ 10 KALINA; una fila por (escenario, variable, grupo)."),
    ("M5_cercano_profesor", "m5_cercano_profesor.csv",
     "M5: por escenario, el KALINA más parecido al profesor (`tipo=cercano`), el KALINA de mayor η (`tipo=mejor_eta`) y, cuando no hay KALINA, el genuino de menor D (`tipo=genuino_mD`); `d` = Σ |v − v_prof|/(b − a) sobre las variables libres y `D` = Σ viol_k / TAU_k."),
)
# Unidades nuevas del TASK: las reglas del formateador no las cubren.
UNIDADES = {"escenario": "\u2212", "omitido": "\u2212", "d": "\u2212",
            "D": "\u2212", "KALINA_LHS": "\u2212", "se_conserva": "texto",
            "variables_libres": "texto", "nota": "texto"}
# Textos fijos de `M5_escenarios` (TASK_CONTEXT); `KALINA_LHS` no va aquí.
ESCENARIOS = (
    (1, "T_fuente 623.15 K + T_sumidero 300.03 K",
     "P_alta, P_baja, x_b, eta_t, eta_p, eps_hrvg, eps_reg, eps_cond",
     "KALINA con eps_hrvg ~0.5, P_baja 1394-1953 kPa, eps_cond >= 0.86"),
    (2, "P_alta 3000 + P_baja 400 kPa",
     "T_fuente, T_sumidero, x_b, eta_t, eta_p, eps_hrvg, eps_reg, eps_cond",
     "0 KALINA en el LHS, pero factible en una franja angosta: T_fuente ~390-405 K con eps_cond >= 0.92 (KALINA de M2R: 403 K, eps_cond 0.95, eta 9.50 %)"),
    (3, "P_alta 3000 + P_baja 400 kPa + T_sumidero 300.03 K",
     "T_fuente, x_b, eta_t, eta_p, eps_hrvg, eps_reg, eps_cond",
     "0 KALINA en el LHS, pero factible en una franja angosta: T_fuente ~390-405 K con eps_cond >= 0.92 (KALINA de M2R: 403 K, eps_cond 0.95, eta 9.50 %)"),
    (4, "P_alta 3000 kPa + T_fuente 623.15 K + T_sumidero 300.03 K",
     "P_baja, x_b, eta_t, eta_p, eps_hrvg, eps_reg, eps_cond",
     "KALINA con P_baja 993-1928 kPa, eps_cond >= 0.88; todos fuera de rango confiable"),
    (5, "T_fuente 623.15 K + x_b 0.50",
     "T_sumidero, P_alta, P_baja, eta_t, eta_p, eps_hrvg, eps_reg, eps_cond",
     "KALINA con P_baja 889-1772 kPa, eps_cond >= 0.84; todos fuera de rango confiable"),
)


def _escenarios(resumen) -> list:
    """Las 5 filas de `M5_escenarios`: los textos de arriba + `KALINA_LHS` de m5_resumen."""
    kal = dict(zip(resumen["escenario"].astype(int), resumen["KALINA"].astype(int)))
    faltan = [e for e, _s, _v, _n in ESCENARIOS if e not in kal]
    if faltan:
        raise SystemExit(f"m5_resumen.csv sin los escenarios {faltan}")
    return [[e, sc, vl, kal[e], nota] for e, sc, vl, nota in ESCENARIOS]


def _fila_resumen(hoja: str, df, camp) -> list:
    """[hoja, filas, KALINA, CORREGIBLE, INVIABLE, NO_CONVERGIO, errores]; sin
    columna de clase propia, los conteos son los de la campaña (m5_lhs)."""
    if "clasificacion" in df:
        n = df["clasificacion"].value_counts()
        err = int(df["error_inesperado"].notna().sum())
    else:
        n = camp["clasificacion"].value_counts()
        err = int(camp["error_inesperado"].notna().sum())
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
    """Quita las filas M5_ viejas de `Resumen` y reinserta las nuevas."""
    for r in range(ws.max_row, 1, -1):
        if str(ws.cell(r, 1).value or "").startswith("M5_"):
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
    """Hoja `M5_figuras` con las cinco PNG de los escenarios; sin Pillow, solo rutas."""
    ws = wb.create_sheet(FIGURA)
    for j, t in enumerate(("figura", "ruta"), 1):
        estilo_titulo(ws.cell(1, j, t), "texto")
    rutas = [M5 / n for n in FIGS]
    for k, p in enumerate(rutas, 2):
        ws.cell(k, 1, p.name)
        ws.cell(k, 2, p.relative_to(_RAIZ).as_posix())
    c = len(rutas) + 3
    ws.cell(c, 1, "Figuras de M5: una por escenario (m5_S1…m5_S5), con las dos variables elegidas del escenario en los ejes, un punto por fila evaluada y el color de su clase.")
    ws.freeze_panes = "A2"
    ws.column_dimensions["A"].width = 34
    ws.column_dimensions["B"].width = 64
    faltan = [p.name for p in rutas if not p.exists()]
    try:
        from openpyxl.drawing.image import Image as XLImage
    except ImportError:
        ws.cell(c + 2, 1, "Pillow no disponible: no se insertó ninguna imagen; las rutas están arriba.")
        return f"{FIGURA}: sin Pillow, solo las rutas"
    if faltan:
        ws.cell(c + 2, 1, "Faltan: " + ", ".join(faltan))
        return f"{FIGURA}: faltan {', '.join(faltan)}"
    fila = c + 2
    for p in rutas:
        img = XLImage(str(p))
        ws.add_image(img, f"A{fila}")
        fila += -(-img.height // 20) + 1   # filas que ocupa la imagen (20 px) + 1 de aire
    return f"{len(rutas)} imágenes insertadas en {FIGURA}"


def main() -> None:
    faltan = [M5 / c for _h, c, _d in HOJAS if not (M5 / c).exists()]
    if not XLSX.exists():
        raise SystemExit(f"No existe {XLSX}: correr antes scripts/barrido_final/excel_final.py")
    if faltan:
        raise SystemExit("Faltan CSV: " + ", ".join(str(p) for p in faltan))
    ef.UNIDAD.update(UNIDADES)
    wb = load_workbook(XLSX)
    if "Resumen" not in wb.sheetnames:
        raise SystemExit("El libro no tiene la hoja Resumen: correr antes los cuatro anteriores")
    viejas = [h for h, _c, _d in HOJAS if h in wb.sheetnames]
    for h in viejas + ["M5_escenarios", FIGURA]:
        if h in wb.sheetnames:
            del wb[h]
    camp = pd.read_csv(M5 / "m5_lhs.csv")
    filas = []
    for hoja, csv, desc in HOJAS:
        df = pd.read_csv(M5 / csv)
        ef.escribir_tabla(wb, hoja, list(df.columns), df.values.tolist(), extra=[desc])
        filas.append(_fila_resumen(hoja, df, camp))
    esc = _escenarios(pd.read_csv(M5 / "m5_resumen.csv"))
    ef.escribir_tabla(wb, "M5_escenarios", CAB_ESC, esc,
                      extra=["Los cinco escenarios de M5: qué datos del profesor "
                             "conserva cada uno y sus variables libres; `KALINA_LHS` "
                             "es el conteo KALINA del escenario en m5_resumen.csv."])
    filas.append(_fila_resumen("M5_escenarios", pd.DataFrame(esc, columns=CAB_ESC), camp))
    msg = _figuras(wb)
    _reescribir_resumen(wb["Resumen"], filas)
    wb.save(XLSX)
    print(f"escrito {XLSX}")
    print("hojas:", wb.sheetnames)
    print(msg)


if __name__ == "__main__":
    main()
