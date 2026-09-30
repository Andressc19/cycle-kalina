"""Excel consolidado de todas las iteraciones de barrido (Fase 1/2/3).

Lee los CSV ya generados bajo resultados/barridos_2026-09-19/ (NO corre ningun
punto del ciclo) y escribe un .xlsx fuera del repo, en la raiz del proyecto.

Task: 2026-09-21-excel-iteraciones-3-fases
"""
from __future__ import annotations

import os
from pathlib import Path
from collections import Counter

import pandas as pd
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

# --- Rutas -------------------------------------------------------------
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = os.path.join(REPO, "resultados", "barridos_2026-09-19")
OUT = str(Path(__file__).resolve().parents[2] / "datos" / "primeros_barridos_e_iteraciones_kalina.xlsx")

MAX_SHEET = 31  # limite de Excel para nombres de hoja
ANCLA = {"ancla_estados.csv", "ancla_balance.csv"}  # tabla del ancla, no iteraciones
PREFIJOS_ITERACION = ("busqueda_", "sensibilidad_", "mapa_2d_", "prescan_", "ronda")

# Nota de una linea por fase (reutilizada de los MD documentados, no inventada).
NOTAS = {
    1: "T_fuente=623.15 K (350 C) alto rompe la campana bifasica NH3-H2O a P_alta "
       "razonable: el estado 2 del HRVG queda fuera del dominio del separador en todo el "
       "rango pedido por el enunciado; NO_CONVERGIO en todo el barrido, causa estructural.",
    2: "Base libre con T_fuente corregido a 470 K: KALINA con eta 0.1243; el bloqueo pasa "
       "al criterio O2 (cavitacion) y luego O1 (calidad de turbina, margen +0.0013 al filo); "
       "eps_cond es la variable mas influyente (por debajo de ~0.93 todo el plano "
       "P_baja x eps_cond cae a CORREGIBLE).",
    3: "Caso real Husavik (121 C, Islandia): ancla KALINA con eta 0.1273; corregir "
       "T_amb_diseno de 30.4 C a 10 C bajo el P_baja necesario de 1200 a 690 kPa y subio "
       "eta de 0.088 a 0.127 (+44 %); frontera O2 confirmada 1:1 con motor real (10/10).",
}


def archivos_fase(fase: int) -> tuple[list[str], list[str]]:
    """Devuelve (csv_iteracion, csv_ancla) ordenados para una fase."""
    carpeta = os.path.join(BASE, f"fase{fase}_profesor" if fase == 1 else
                           f"fase{fase}_{'real' if fase == 3 else 'libre'}")
    csvs = sorted(f for f in os.listdir(carpeta) if f.endswith(".csv"))
    if fase == 1:  # los 3 archivos de Fase 1 son barridos del profesor
        return csvs, []
    iteracion = [f for f in csvs if f.startswith(PREFIJOS_ITERACION)]
    ancla = [f for f in csvs if f in ANCLA]
    return iteracion, ancla


def nombre_hoja(fase: int, archivo: str) -> str:
    return f"Fase{fase}_{archivo[:-4]}"[:MAX_SHEET]


def aplicar_estilo(ws, mensaje: bool = False) -> None:
    bold = Font(bold=True)
    for celda in ws[1]:
        celda.font = bold
    ws.freeze_panes = "A2"
    ancho = 26 if mensaje else 16
    for col in ws.columns:
        letra = get_column_letter(col[0].column)
        ws.column_dimensions[letra].width = ancho
    for fila in ws.iter_rows(min_row=2):
        for celda in fila:
            celda.alignment = Alignment(wrap_text=mensaje, vertical="top")


def escribir_resumen(wb: Workbook, datos_fases: dict) -> None:
    ws = wb.create_sheet("Resumen", 0)
    ws["A1"] = "Barridos e iteraciones del ciclo Kalina - Fase 1 / 2 / 3"
    ws["A1"].font = Font(bold=True, size=13)
    ws["A2"] = ("Consolidacion de CSVs ya corridos (sin re-ejecutar el ciclo). "
                "Fuente: resultados/barridos_2026-09-19/")
    fila = 4
    cabeceras = ["Fase", "CSVs (iteraciones)", "Filas iteraciones", "KALINA",
                 "CORREGIBLE", "NO_CONVERGIO", "INVIABLE", "Otras", "Nota (1 linea)"]
    for i, c in enumerate(cabeceras, start=1):
        ws.cell(row=fila, column=i, value=c).font = Font(bold=True)
    fila += 1
    for fase, (archivos, filas, conteo) in sorted(datos_fases.items()):
        vals = [f"Fase {fase}", len(archivos), filas,
                conteo.get("KALINA", 0), conteo.get("CORREGIBLE", 0),
                conteo.get("NO_CONVERGIO", 0), conteo.get("INVIABLE", 0)]
        otras = {k: v for k, v in conteo.items()
                 if k not in ("KALINA", "CORREGIBLE", "NO_CONVERGIO", "INVIABLE")}
        vals.append(", ".join(f"{k}={v}" for k, v in otras.items()) or "-")
        vals.append(NOTAS[fase])
        for i, v in enumerate(vals, start=1):
            celda = ws.cell(row=fila, column=i, value=v)
            celda.alignment = Alignment(wrap_text=True, vertical="top")
        fila += 1
    fila += 1
    ws.cell(row=fila, column=1, value="Notas:").font = Font(bold=True)
    fila += 1
    ws.cell(row=fila, column=1, value=("- Las hojas 'Fase2_ancla_*' y 'Fase3_ancla_*' son la "
                                       "tabla del punto ancla (ancla_estados / ancla_balance), "
                                       "NO iteraciones de barrido; se incluyen aparte. "
                                       "El conteo de filas de arriba NO las incluye."))
    fila += 1
    ws.cell(row=fila, column=1, value=("- En fase3_real/ hay nombres casi iguales por "
                                       "mayusculas/version (sensibilidad_palta y "
                                       "sensibilidad_P_baja; sensibilidad_pbaja y P_baja; "
                                       "sensibilidad_xb y x_b): son rondas distintas y cada "
                                       "una tiene su propia hoja, no se fusionaron."))
    fila += 1
    ws.cell(row=fila, column=1, value=("- Catalogo de clasificacion vigente: remapeo de "
                                       "etiquetas del 2026-09-29 (sin recalcular ningun punto "
                                       "del ciclo). Las dos etiquetas retiradas del catalogo "
                                       "anterior quedaron fusionadas en las actuales "
                                       "(las que avisaban sin bloquear -> CORREGIBLE; la que "
                                       "ya no operaba como Kalina -> INVIABLE). eta / Wnet / "
                                       "convergencia de cada fila son los mismos de siempre; "
                                       "solo cambio el nombre de la etiqueta."))
    fila += 1
    ws.cell(row=fila, column=1, value=("- ronda5_diagnostico y ronda6_diagnostico son barridos "
                                       "de diagnostico de las rondas 5 y 6 de fase2_libre; "
                                       "estan en sus propias hojas y si cuentan en el resumen."))
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 18
    ws.column_dimensions["C"].width = 18
    for letra in "DEFG":
        ws.column_dimensions[letra].width = 16
    ws.column_dimensions["H"].width = 26
    ws.column_dimensions["I"].width = 100


def main() -> None:
    datos_fases = {}
    with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
        for fase in (1, 2, 3):
            iteracion, ancla = archivos_fase(fase)
            carpeta = os.path.join(BASE, f"fase{fase}_profesor" if fase == 1 else
                                   f"fase{fase}_{'real' if fase == 3 else 'libre'}")
            filas = 0
            conteo: Counter = Counter()
            for archivo in iteracion + ancla:
                df = pd.read_csv(os.path.join(carpeta, archivo))
                hoja = nombre_hoja(fase, archivo)
                df.to_excel(writer, sheet_name=hoja, index=False)
                aplicar_estilo(writer.sheets[hoja], mensaje=("mensaje" in df.columns))
                if archivo not in ancla:
                    filas += len(df)
                    if "clasificacion" in df.columns:
                        conteo.update(df["clasificacion"].fillna("<NaN>").astype(str).tolist())
            datos_fases[fase] = (iteracion, filas, conteo)
    from openpyxl import load_workbook
    wb = load_workbook(OUT)
    escribir_resumen(wb, datos_fases)
    wb.save(OUT)
    wb.close()
    print(f"OK -> {OUT}")
    for fase, (arc, filas, con) in sorted(datos_fases.items()):
        print(f"Fase {fase}: {len(arc)} csv, {filas} filas, clasificacion={dict(con)}")


if __name__ == "__main__":
    main()