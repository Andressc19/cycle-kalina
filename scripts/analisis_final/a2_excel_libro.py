# -*- coding: utf-8 -*-
"""A2 · Arma datos/Excel_kalina_final_final_final.xlsx (§6.3). Se puede volver a correr.

Escrito por el director (Claude) el 2026-10-10 (OpenCode sin modelo disponible).
No abre para escribir datos/Excel_final_kalina.xlsx: comprueba su hash antes y después.
"""
import hashlib
import os

import pandas as pd
from openpyxl import Workbook

import pies
from a2_comun import EXCEL_VIEJO, INV, LIBRO, MNN, leer_canon, registro
from a2_excel_hojas import (hoja_df, hoja_figuras, hoja_leeme, hoja_profesor, hoja_tabla,
                            nombre_hoja)
from a2_excel_tablero import construir

COLS_DATOS = ["id_punto", "id_caso", "id_subcaso", "bloque_director", "tipo_punto", "clase_trazo",
              "clasificacion", "genuino", "kalina_confiable", "fuera_rango", "omitido", "T_fuente",
              "T_sumidero", "P_alta", "P_baja", "x_b", "eta_t", "eta_p", "eps_hrvg", "eps_reg",
              "eps_cond", "T_amb_diseno", "eta_pct", "Wnet", "dP", "rP", "codigos_falla", "variable"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    h0 = sha(EXCEL_VIEJO)
    reg = registro()
    cond = pd.read_csv(os.path.join(INV, "condiciones_por_subcaso.csv"))
    d = leer_canon()
    wb = Workbook()
    hoja_leeme(wb)                                   # 1
    indice = []                                      # (hoja, caso, bloque, qué muestra)
    hoja_profesor(wb)
    indice.append(("Punto_profesor", "—", "—", "Datos del profesor y punto ancla A*"))
    for _, m in reg[reg["carpeta"] == "G"].sort_values("tabla").iterrows():
        indice.append((hoja_tabla(wb, m, ""), "síntesis", "uno por fila", m["titulo"]))
    indice.append((hoja_figuras(wb, "G", "Figuras de síntesis"), "síntesis", "—", "FIG-G01, FIG-G02"))
    for mnn in MNN:
        filas = reg[reg["tabla"].str.startswith(f"TAB-{mnn}-")].sort_values("tabla")
        for _, m in filas.iterrows():
            subs = [s for s in str(m["subcasos"]).split("; ") if s]
            indice.append((hoja_tabla(wb, m, pies.condiciones_texto(subs)), m["casos"],
                           m["bloques"], m["titulo"]))
        if mnn != "M04b":
            indice.append((hoja_figuras(wb, mnn, f"Figuras del caso KF-{mnn}"), f"KF-{mnn}", "—",
                           "figuras con su pie"))
    ws = wb.create_sheet("X_M08_anecdotico")
    ws["A1"] = "ANECDÓTICO — fuera del rango realista"
    from openpyxl.styles import Font, PatternFill
    ws["A1"].fill = PatternFill("solid", fgColor="F8B4B4"); ws["A1"].font = Font(bold=True, size=14)
    m8 = d[d["id_caso"] == "KF-M08"]["clase_trazo"].value_counts()
    ws["A3"] = "KF-M08: η y ε fuera de [0.40, 0.95]. No es un resultado de diseño ni entra en conclusiones."
    for i, (k, v) in enumerate(m8.items(), 5):
        ws.cell(i, 1, k); ws.cell(i, 2, int(v))
    datos = d[d["id_caso"] != "KF-M08"][COLS_DATOS]
    hoja_df(wb, "Datos", datos)
    hoja_df(wb, "Condiciones", cond)
    hoja_df(wb, "Bloques", pd.read_csv(os.path.join(INV, "bloques.csv")))
    bloques = [b for b in dict.fromkeys(datos["bloque_director"]) if b != "BX"]
    construir(wb, datos.assign(viol_O1=d["viol_O1"], viol_O2=d["viol_O2"], viol_O3=d["viol_O3"],
                               viol_O5=d["viol_O5"]), cond[cond["bloque_director"] != "BX"], bloques)
    wi = wb.create_sheet("Indice", 2)
    wi.append(["Hoja", "Caso", "Bloque(s)", "Qué muestra"])
    for h, c, b, q in indice:
        wi.append([h, c, b, q])
        wi.cell(wi.max_row, 1).hyperlink = f"#'{h}'!A1"
        wi.cell(wi.max_row, 1).style = "Hyperlink"
    for col, w in zip("ABCD", (34, 22, 40, 70)):
        wi.column_dimensions[col].width = w
    os.makedirs(os.path.dirname(LIBRO), exist_ok=True)
    wb.save(LIBRO)
    h1 = sha(EXCEL_VIEJO)
    print(f"Libro: {LIBRO} · {len(wb.sheetnames)} hojas")
    print(f"Excel_final_kalina.xlsx sin cambios: {'OK' if h0 == h1 else 'FALLA'} ({h0[:12]})")


if __name__ == "__main__":
    main()
