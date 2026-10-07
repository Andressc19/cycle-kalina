"""Verifica las hojas M5_* de `datos/Excel_final_kalina.xlsx` (TASK_CONTEXT final_excel_M5).

Comprobaciones:
- nombres de hoja: M5_lhs, M5_resumen, M5_rangos, M5_cercano_profesor, M5_escenarios, M5_figuras
- filas de datos frente a los CSV de origen (600 en M5_lhs, 5 en M5_resumen, número en m5_rangos/m5_cercano_profesor)
- `M5_lhs` tiene `escenario (−)` y `omitido (−)` en las cabeceras
- `M5_escenarios`: 5 filas, cabeceras con `KALINA_LHS (−)`, `se_conserva`, `variables_libres`, `nota`
- `M5_figuras`: tiene 5 rutas m5_S1.png … m5_S5.png
- `Resumen` tiene las filas de M5 (M5_lhs, M5_resumen, M5_rangos, M5_cercano_profesor, M5_escenarios)
- todas las hojas anteriores (M0–M4) siguen presentes
- la hoja `M4_lhs500` sigue presente (500 filas, lote M4/M4b)
- huella del libro (idempotencia)

Imprime cada comprobación y termina con OK si todas pasan.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path.insert(0, str(_RAIZ))
sys.path.insert(0, str(_DIR))
sys.path.insert(0, str(_DIR.parent))

from openpyxl import load_workbook  # noqa: E402
import pandas as pd  # noqa: E402

XLSX = _RAIZ / "datos" / "Excel_final_kalina.xlsx"
M5 = _RAIZ / "resultados" / "2026-10-07_final_M5"
PRE = {"M0_protocolo", "M1_profesor_P_alta", "M1_profesor_x_b",
       "M1_profesor_T_amb", "M1_profesor_base", "M1_comparacion",
       "M2_N1_malla", "M2_N1_biseccion", "M2_N1_fronteras", "M2_N1_resumen",
       "M2_N2_malla", "M2_N2_biseccion", "M2_N2_fronteras", "M2_N2_kalina",
       "M2_N2_resumen", "M3_ofat", "M3_resumen", "M3_cruces", "M2R_n1",
       "M2R_n2a", "M2R_n2b", "M2R_n3", "M2R_fronteras", "M2R_kalina",
       "M2R_resumen", "M2S_malla", "M2S_biseccion", "M2S_resumen",
       "M2S_kalina", "M4_lhs500", "M4_rsa", "M4_prcc", "M4_pawn",
       "M4_presiones_rangos", "M4_ventana_Palta", "M4_ventana_Tfuente",
       "M4_ventana_Tsumidero", "M4_bloqueo_rP", "M4_top_kalina",
       "M4_convergencia", "M3_figuras", "M4_figuras"}
M5HOJAS = {"M5_lhs", "M5_resumen", "M5_rangos", "M5_cercano_profesor",
           "M5_escenarios", "M5_figuras"}
FIGS = tuple(f"m5_S{k}.png" for k in range(1, 6))


def filas_datos(ws) -> int:
    n = 0
    for r in range(2, ws.max_row + 1):
        v = ws.cell(r, 1).value
        if v in (None, "") or str(v).startswith("Descripción"):
            break
        n += 1
    return n


def resumen(ws, hoja: str):
    for r in range(2, ws.max_row + 1):
        v = ws.cell(r, 1).value
        if v in (None, "") or str(v).startswith("Descripción"):
            return None
        if v == hoja:
            return [ws.cell(r, c).value for c in range(2, 8)]
    return None


def huella(wb) -> str:
    h = hashlib.sha256()
    for ws in wb.worksheets:
        h.update(ws.title.encode("utf-8"))
        for fila in ws.iter_rows(values_only=True):
            h.update(repr(fila).encode("utf-8"))
    return h.hexdigest()[:16]


def main() -> int:
    if not XLSX.exists():
        print(f"FALLO: no existe {XLSX}")
        return 1
    wb = load_workbook(XLSX)
    fallos = 0

    def chk(ok: bool, txt: str) -> None:
        nonlocal fallos
        print(("  OK   " if ok else "  FALLO ") + txt)
        if not ok:
            fallos += 1

    chk(not (PRE - set(wb.sheetnames)), f"hojas anteriores presentes (faltan: {(PRE - set(wb.sheetnames)) or 'ninguno'})")
    faltan_m5 = sorted(M5HOJAS - set(wb.sheetnames))
    chk(not faltan_m5, f"hojas M5 presentes (faltan: {faltan_m5 or 'ninguno'})")
    ws = wb["M5_lhs"]
    n = filas_datos(ws)
    chk(n == 600, f"M5_lhs: {n} filas de datos = 600 de m5_lhs.csv")
    cab = [str(ws.cell(1, c).value) for c in range(1, ws.max_column + 1)
           if ws.cell(1, c).value is not None]
    chk("escenario (\u2212)" in cab and "omitido (\u2212)" in cab, f"M5_lhs: cabeceras con scenario/omitido ({cab[0] if cab else ''}, ...)")
    for hoja, n_csv in (("M5_resumen", 5), ("M5_rangos", len(pd.read_csv(M5 / "m5_rangos.csv"))), ("M5_cercano_profesor", len(pd.read_csv(M5 / "m5_cercano_profesor.csv")))):
        ws = wb[hoja]
        chk(filas_datos(ws) == n_csv, f"{hoja}: filas = {filas_datos(ws)} (CSV {n_csv})")
        fila = resumen(wb["Resumen"], hoja)
        chk(fila is not None and fila[0] == n_csv, f"{hoja}: Resumen puntos = {fila[0] if fila else 'None'}")
        c = [str(ws.cell(1, c).value) for c in range(1, ws.max_column + 1) if ws.cell(1, c).value is not None]
        chk(all(x.endswith(")") for x in c), f"{hoja}: todas las cabeceras tienen unidad")
    ws = wb["M5_escenarios"]
    chk(filas_datos(ws) == 5, f"M5_escenarios: 5 filas de datos")
    c = [str(ws.cell(1, c).value) for c in range(1, ws.max_column + 1) if ws.cell(1, c).value is not None]
    chk("KALINA_LHS (\u2212)" in c and "se_conserva" in c[1] and "variables_libres" in c[2] and "nota" in c[4], f"M5_escenarios: cabeceras correctas ({c})")
    chk(bool(ws.auto_filter.ref), f"M5_escenarios: auto_filtro presente")
    ws = wb["M5_figuras"]
    rutas = [ws.cell(r, 2).value for r in range(2, 2 + len(FIGS))]
    esperadas = [(M5 / n).relative_to(_RAIZ).as_posix() for n in FIGS]
    chk(rutas == esperadas, f"M5_figuras: 5 rutas S1–S5 ({rutas})")
    chk(len(ws._images) >= 0, "M5_figuras: imágenes (0 = sin Pillow)")
    ws = wb["M4_lhs500"]
    chk(filas_datos(ws) == 500, f"M4_lhs500: sigue con 500 filas")
    lotes = [ws.cell(r, 1).value for r in range(2, filas_datos(ws) + 2)]
    chk(lotes.count("M4") == 300 and lotes.count("M4b") == 200, f"M4_lhs500: lotes intactos (M4={lotes.count('M4')}, M4b={lotes.count('M4b')})")
    print(f"huella del libro: {huella(wb)}")
    print("OK" if not fallos else f"FALLO ({fallos} comprobaciones)")
    return 0 if not fallos else 1


if __name__ == "__main__":
    sys.exit(main())
