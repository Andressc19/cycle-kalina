"""Consolida en un solo Excel todas las iteraciones de barrido guardadas.

Copia las hojas de `primeros_barridos_e_iteraciones_kalina.xlsx` (fases 1-3,
sin modificar ese archivo) y agrega una hoja por cada CSV de `resultados/`,
con una hoja `Resumen` actualizada. No re-ejecuta el ciclo.

Uso: python scripts/consolidar_excel_barridos.py
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import sys

import openpyxl
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

REPO = Path(__file__).resolve().parents[1]
ORIGEN = REPO / "datos" / "primeros_barridos_e_iteraciones_kalina.xlsx"
DESTINO = REPO / "datos" / "barridos_e_iteraciones_kalina_consolidado.xlsx"
CLASES = ("KALINA", "CORREGIBLE", "INVIABLE", "NO_CONVERGIO")
_W = ""   # resultados A+B: ya en resultados/ tras traer fix/teqp-doble-verificacion
NEGRITA = Font(bold=True)
GRIS = PatternFill("solid", fgColor="DDDDDD")

# (hoja, csv, columna de clasificacion, nota de 1 linea)
NUEVOS = [
    ("0921_xb_industria", "2026-09-21_xb_industria/barrido_xb_industria.csv",
     "clasificacion",
     "x_b 0.78-0.85, P_alta 5000-10500 kPa, T_fuente 470 K, eps fijos: 0 KALINA; "
     "mejor eta ~0.16 subiendo P_baja a ~900 kPa pero bloqueado por O1/O2."),
    ("0922_literatura_KCS11", "2026-09-22_literatura_kcs11/barrido_literatura_kcs11.csv",
     "clasificacion",
     "Ventana Elsayed 2013 (x_b 0.55-0.70, P_alta 1000-5000, T_fuente 373-463), "
     "P_baja/eps calibrados por pinch 4 K: 0 KALINA, O2 bloquea los 33 convergentes."),
    ("0922_O2_Tamb_realista", "2026-09-22_o2_tamb_realista/reclasificacion_o2.csv",
     "clasificacion_realista",
     "Misma malla de 60, piso O2 283.15 K (clima real) vs 303.55 K (tropical): "
     "0 -> 16 KALINA; mejor eta 0.165 (x_b 0.60, 5000 kPa, 423 K)."),
    ("0922_Tfuente_333K", "2026-09-22_tfuente_bajo/exploracion_tfuente_bajo.csv",
     "clasificacion",
     "T_fuente 333 K, P_alta 1500, x_b 0.55-0.75: ningun punto clasificable "
     "(PropertyRangeError del motor teqp, no conclusion fisica)."),
    ("0922_frontera_Tfuente", "2026-09-22_frontera_tfuente/frontera_tfuente_teqp.csv",
     "clasificacion",
     "T_fuente 340/350/360 K x x_b 0.55-0.75: 11 KALINA; x_b alto tolera fuente "
     "mas fria; eta 0.075-0.103, eta/eta_Carnot 41-48 % (literatura: 47 %)."),
    ("0923_pinch6_realista", "2026-09-23_pinch6_realista/barrido_pinch6_realista.csv",
     "clasificacion",
     "Pinch 6 K, x_b 0.60-0.80, P_alta 3000-5000, T_fuente 394/423: 19 KALINA, 5 con "
     "los tres eps <= 0.95; sin eps recortados a 0.999; O2 bloquea 4 (antes 15)."),
    ("0923_eps_fijos_085", "2026-09-23_eps_fijos_085/barrido_eps_fijos_085.csv",
     "clasificacion",
     "eps fijos 0.85/0.80/0.85, P_baja subida por O2 (punto fijo, max 4 iters): 7 KALINA "
     "(1 con eta 0.009, degenerado); 19 CORREGIBLE por O2 a menos de 1.03 K; eta -2.5 pp vs pinch 6."),
    ("0924_margen2k", "2026-09-24_margen2k/barrido_margen2k.csv", "clasificacion",
     "eps fijos 0.85/0.80/0.85, P_baja por brentq para subenfriamiento exacto de 2 K: 22 KALINA "
     "(21 utiles); P_baja +154 kPa y eta -0.98 pp vs barrido anterior; 8 sin solucion."),
    ("0924_margen2k_evaluaciones", "2026-09-24_margen2k/evaluaciones_margen.csv", None,
     "Todas las evaluaciones de margen(P_baja) del barrido 0924 (285 filas), para sensibilidad."),
    ("0924_verif_motor_real", "2026-09-24_verificacion/verificacion_motor_real.csv",
     "clasificacion",
     "3 KALINA de 0924_margen2k con teqp y con AmmoniaWaterAdapter: los 3 confirmados, "
     "diferencia de eta < 0.02 % relativo, margen O2 real 2.02-2.03 K."),
    ("0924_estabilidad_22", "2026-09-24_rama_turbina/estabilidad_kalina.csv", "clasif_0",
     "22 KALINA en P* y P* +/- 0.5 kPa (teqp): 21 estables, 1 inestable (0.60/4000/394) "
     "por la rama espuria de la salida de turbina."),
    ("0924_rama_fisica_22", "2026-09-24_rama_22/rama_fisica_22.csv", None,
     "Salida isentropica de turbina teqp vs motor real en los 22 KALINA: los 22 en rama "
     "fisica (dh4s -0.7 a -1.6 kJ/kg; espurio seria ~139). El False de la columna es por "
     "el umbral de 0.5 K, demasiado estricto."),
    ("0927_costo_soluciones", "2026-09-27_costo_soluciones/costo_tabla.csv", None,
     "Costo por punto de teqp / A / B / motor real (prototipos). A +2.8 %, B +7 s por "
     "punto verificado, motor real ~10x. (La tabla de B de ese reporte compara h4 con "
     "h4s: ver bitacora.)"),
    ("0927_regresion_A", _W + "2026-09-27_teqp_verificado/regresion_22.csv", "clas_verif",
     "TeqpVerificado (A) vs TeqpAdapter en los 22 KALINA: 21 identicos, 1 con d_eta "
     "1.8e-7, ninguno cambia de clase; 1 recurrencia al motor real; +0.23 %."),
    ("0927_medicion_AB", _W + "2026-09-27_medicion_AB/medicion_puntos.csv", "clas_A",
     "Tiempos reales 23 puntos: teqp 31.1 s, A 31.7 s (+2 %), B +3.5 s por punto. "
     "Barrido de 30 (20 KALINA): teqp 932 s, A+B ~1023 s (+10 %)."),
    ("0927_integracion_AB_humo", _W + "2026-09-27_integracion_AB/humo.csv", "clasificacion",
     "Barrido con A+B integrado (sensitivity.ejecutar_barrido): punto normal KALINA "
     "verificado; espurio corregido por A (eta 0.0802, 6 recurrencias)."),
]


def _num(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return v
    return int(f) if f.is_integer() and "." not in str(v) else f


def _formatear(ws, fila_cab: int = 1) -> None:
    for c in ws[fila_cab]:
        if c.value is not None:
            c.font, c.fill = NEGRITA, GRIS
    for i, col in enumerate(ws.iter_cols(min_row=fila_cab), start=1):
        largo = max((len(str(c.value)) for c in col if c.value is not None), default=8)
        ws.column_dimensions[get_column_letter(i)].width = min(max(10, largo + 2), 45)
    ws.freeze_panes = ws.cell(row=fila_cab + 1, column=1)


def _copiar_hojas(wb_dest) -> list[tuple]:
    """Copia las hojas del Excel previo; devuelve las filas de su Resumen."""
    wb_src = openpyxl.load_workbook(ORIGEN)
    resumen_previo = []
    for ws_src in wb_src.worksheets:
        filas = list(ws_src.iter_rows(values_only=True))
        if ws_src.title == "Resumen":
            resumen_previo = [f for f in filas if f and str(f[0]).startswith("Fase ")]
            continue
        ws = wb_dest.create_sheet(ws_src.title)
        for f in filas:
            ws.append(list(f))
        _formatear(ws)
    return resumen_previo


def _agregar_csv(wb_dest, hoja, ruta_rel, col_clase):
    with open(REPO / "resultados" / ruta_rel, newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    ws = wb_dest.create_sheet(hoja)
    ws.append(list(filas[0].keys()))
    for fila in filas:
        ws.append([_num(v) if v != "" else None for v in fila.values()])
    _formatear(ws)
    if col_clase is None:
        return len(filas), None
    return len(filas), Counter(f[col_clase] for f in filas)


def principal() -> None:
    wb = openpyxl.Workbook()
    ws_res = wb.active
    ws_res.title = "Resumen"
    previo = _copiar_hojas(wb)

    ws_res.append(["Barridos e iteraciones del ciclo Kalina KCS-11 - consolidado"])
    ws_res["A1"].font = Font(bold=True, size=13)
    ws_res.append(["Fases 1-3: copiadas de primeros_barridos_e_iteraciones_kalina.xlsx "
                   "(resultados/barridos_2026-09-19/, rama test/fases-sensibilidad). "
                   "Barridos 0921/0922: resultados/ de la rama test/teqp-con-validacion. "
                   "Motor de todos los barridos nuevos: TeqpAdapter."])
    ws_res.append([])
    cab = ["Fase / barrido", "Hojas", "Puntos", *CLASES, "Nota (1 linea)"]
    ws_res.append(cab)
    fila_cab = ws_res.max_row
    for f in previo:
        fase, n_csv, n, kal, corr, noc, inv, _otras, nota = f
        ws_res.append([fase, n_csv, n, kal, corr, inv, noc, nota])
    for hoja, ruta, col, nota in NUEVOS:
        n, cuenta = _agregar_csv(wb, hoja, ruta, col)
        clases = (["-"] * len(CLASES) if cuenta is None
                  else [cuenta.get(c, 0) for c in CLASES])
        ws_res.append([hoja, 1, n, *clases, nota])
    for c in ws_res[fila_cab]:
        c.font, c.fill = NEGRITA, GRIS
    ws_res.append([])
    for nota in (
        "Notas:",
        "- En 0922_O2_Tamb_realista el conteo usa la columna clasificacion_realista "
        "(piso O2 = 283.15 K); la columna clasificacion_tropical (303.55 K) da 0 KALINA.",
        "- Calculo puntual (sin CSV): caso base Elsayed, P_baja=273.545 kPa, x_b=0.55 -> "
        "T_burbuja=287.00 K. Con piso 303.55 K O2 falla por 16.55 K para cualquier eps_cond; "
        "umbral exacto del piso: <= 287.0 K (13.85 C).",
        "- Barridos 0922 usan P_baja = burbuja a T_sumidero+4 K y eps calibrados por punto "
        "(pinch 4 K, un solo paso); T_sumidero=283 K, eta_t=eta_p=0.80, m_b=1 kg/s.",
        "- Resultados de TeqpAdapter sin verificar todavia con el motor real "
        "(AmmoniaWaterAdapter).",
        "- Las hojas *_ancla_* de fases 2-3 son el punto ancla, no iteraciones.",
    ):
        ws_res.append([nota])
    ws_res.column_dimensions["A"].width = 26
    for col in "BCDEFGHI":
        ws_res.column_dimensions[col].width = 13
    ws_res.column_dimensions["J"].width = 110
    ws_res.freeze_panes = ws_res.cell(row=fila_cab + 1, column=1)
    wb.save(DESTINO)
    print(f"Guardado {DESTINO} con {len(wb.sheetnames)} hojas")
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import formatear_excel_barridos
    formatear_excel_barridos.main()


if __name__ == "__main__":
    principal()
