# -*- coding: utf-8 -*-
"""A2 · Partes 1 y 2: tablas de condiciones (TAB-<Mnn>-00), de conteo (TAB-<Mnn>-01)
y tablas de resultados (TAB-<Mnn>-02...) a partir de resultados/**.
"""
import os

import pandas as pd

from a2_comun import (RAIZ, RES, TABLAS, MNN, PROFESOR, bloques_de, leer, leer_canon,
                      leer_conteo, nombre_es, tipo_de, formatear, escribir_tabla,
                      subcasos_de, renombrar)

PUNTO_BASE = {
    "M01": "PP = punto del profesor (los 11 datos del enunciado; ver GLOSARIO)",
    "M02-N1": "PP = punto del profesor; se mueve una variable a la vez",
    "M02-N2": "PP = punto del profesor salvo el par movido",
    "M02R": "PP = punto del profesor con η/ε dentro de [0.40, 0.95]",
    "M02S": "B1 a B4 = cuatro bases distintas (una por subcaso)",
    "M03": "A* = punto del profesor con T_fuente = 403 K y P_baja = 563.64 kPa",
    "M04": "caja M4 = las 10 variables barridas dentro de su caja (ver TAB-M04-00)",
    "M04b": "caja M4 = las 10 variables barridas dentro de su caja (ver TAB-M04-00)",
    "M04c": "caja M4 con P_baja dentro de 1500 a 2500 kPa",
    "M05": "PP parcial según escenario S1 a S5",
    "M05c": "PP = punto del profesor con P_alta y P_baja fijas",
    "M06": "puntos clave del ciclo con teqp y con el motor real",
    "M07": "mejores KALINA de cada arranque",
    "M09": "PP parcial según el conjunto de datos conservado",
    "M10": "Húsavík (reproducción de la Fase 3)",
    "M10b": "Húsavík con x_b bajo",
}


def carpeta_de(mnn):
    return "M02" if mnn.startswith("M02-N") else mnn


def _sub(*casos):
    fuera = []
    for c in casos:
        fuera += subcasos_de("KF-" + c)
    return fuera


def _meta(mnn, num, slug, titulo, casos, subcasos, filtro, fuente, n, notas=""):
    return {"tabla": f"TAB-{mnn}-{num}", "carpeta": carpeta_de(mnn),
            "hoja": f"{mnn}_{num}_{slug}", "titulo": titulo, "casos": casos,
            "bloques": ", ".join(bloques_de(subcasos)) or "n/d", "subcasos": subcasos,
            "punto_base": PUNTO_BASE[mnn], "filtro": filtro, "fuente": fuente,
            "n": n, "notas": notas}


def tabla_condiciones(mnn):
    """TAB-<Mnn>-00: variable por variable, estado y valor o rango."""
    c = leer(os.path.join(RAIZ, "analisis_final", "00_inventario",
                          "condiciones_por_subcaso.csv"))
    c = c[c["id_caso"] == "KF-" + mnn]
    filas = []
    for _, r in c.iterrows():
        tipo = tipo_de(r["variable"])
        if r["estado"] == "fijo":
            val = formatear(tipo, r["valor_fijo"])
        elif r["estado"] == "barrido":
            val = f"{formatear(tipo, r['min'])} – {formatear(tipo, r['max'])}"
        else:
            val = ""
        oat = r.get("es_oat") == "sí"
        estado = {"fijo": "Fija", "barrido": "Barrida", "sin_dato": "Sin dato"}[r["estado"]]
        if oat and r["estado"] == "barrido":
            estado = "Una a la vez"
        filas.append({"Subcaso": r["id_subcaso"], "Variable": nombre_es(r["variable"]) or r["variable"],
                      "Estado": estado,
                      "Valor en el punto base": formatear(tipo, r["valor_base"]) if oat and pd.notna(r.get("valor_base")) else "",
                      "Valor o rango": val, "n valores": r["n_valores"],
                      "¿Igual al profesor?": r["igual_al_profesor"] if pd.notna(r["igual_al_profesor"]) else "",
                      "Unidad": r["unidad"] if pd.notna(r["unidad"]) else "–"})
    df = pd.DataFrame(filas)
    if not (df["Valor en el punto base"] != "").any():
        df = df.drop(columns="Valor en el punto base")
    tipos = {"Subcaso": "txt", "Variable": "txt", "Estado": "txt", "Valor o rango": "txt",
             "Valor en el punto base": "txt",
             "n valores": "int", "¿Igual al profesor?": "txt", "Unidad": "txt"}
    meta = _meta(mnn, "00", "condiciones", f"Condiciones del caso {mnn}", "KF-" + mnn,
                 subcasos_de("KF-" + mnn), "condiciones_por_subcaso (cada subcaso y variable)",
                 "analisis_final/00_inventario/condiciones_por_subcaso.csv", len(df))
    escribir_tabla(meta, df, tipos)


def tabla_conteo(mnn):
    """TAB-<Mnn>-01: conteo de corridas por subcaso."""
    c = leer_conteo()
    c = c[c["id_caso"] == "KF-" + mnn].copy()
    c = c.set_index("id_subcaso").loc[subcasos_de("KF-" + mnn)].reset_index()
    cols = ["id_subcaso", "n_puntos", "omitidos", "genuinos", "kalina",
            "kalina_confiables", "corregible", "invariable", "no_convergio",
            "n2", "fuera_rango"]
    df, tipos = renombrar(c[cols], f"TAB-{mnn}-01")
    meta = _meta(mnn, "01", "conteo", f"Corridas por subcaso del caso {mnn}", "KF-" + mnn,
                 subcasos_de("KF-" + mnn), "conteo_por_subcaso",
                 "analisis_final/00_inventario/conteo_por_subcaso.csv", len(df))
    escribir_tabla(meta, df, tipos)


def tabla_resultado(mnn, num, slug, ruta, titulo, casos, subcasos, filtro, notas=""):
    """TAB-<Mnn>-0n: copia de un resumen de resultados/** con encabezados en español."""
    csv = os.path.join(RAIZ, ruta)
    if not os.path.exists(csv):
        print(f"  PENDIENTE: no existe {ruta}")
        return
    df, tipos = renombrar(leer(csv), f"TAB-{mnn}-{num}")
    meta = _meta(mnn, num, slug, titulo, casos, subcasos, filtro, ruta, len(df), notas)
    escribir_tabla(meta, df, tipos)


# (mnn, num, slug, ruta relativa, título, casos, filtro)
RESULTADOS = [
    ("M01", "02", "comparacion", "resultados/2026-10-06_final_M1/m1_comparacion.csv",
     "Comparación antes y después de la F1", "KF-M01", "sin filtro (comparación punto a punto)"),
    ("M02-N1", "02", "resumen", "resultados/2026-10-06_final_M2/m2n1_resumen.csv",
     "Distancia al punto del profesor moviendo una variable a la vez", "KF-M02-N1",
     "todos los puntos del barrido OAT"),
    ("M02-N2", "02", "resumen", "resultados/2026-10-06_final_M2/m2n2_resumen.csv",
     "Resumen de la malla de dos cambios", "KF-M02-N2", "todos los puntos de la malla"),
    ("M02R", "02", "resumen", "resultados/2026-10-06_final_M2R/m2r_resumen.csv",
     "Malla con η y ε en [0.40, 0.95]", "KF-M02R", "todos los puntos de la malla"),
    ("M02S", "02", "resumen", "resultados/2026-10-06_final_M2S/m2s_resumen.csv",
     "Malla T_sumidero x P_baja por base", "KF-M02S", "todos los puntos de la malla"),
    ("M04", "02", "separacion", "resultados/2026-10-07_final_M4b/m4b_rsa.csv",
     "Separación KALINA / no KALINA (RSA y KS)", "KF-M04 + KF-M04b", "todos los puntos de la caja M4"),
    ("M04", "03", "prcc", "resultados/2026-10-07_final_M4b/m4b_prcc.csv",
     "Influencia de cada variable sobre η (PRCC)", "KF-M04 + KF-M04b", "todos los puntos de la caja M4"),
    ("M04", "04", "rangos_presion", "resultados/2026-10-07_final_M4b/m4b_rangos_presiones.csv",
     "Rangos de presión de los KALINA", "KF-M04 + KF-M04b", "puntos KALINA confiables"),
    ("M04", "05", "ventana_palta", "resultados/2026-10-07_final_M4b/m4b_ventana_por_palta.csv",
     "Ventana KALINA por franjas de P_alta", "KF-M04 + KF-M04b", "puntos genuinos de la caja M4"),
    ("M04", "06", "ventana_tf", "resultados/2026-10-07_final_M4b/m4b_ventana_por_tfuente.csv",
     "Ventana KALINA por franjas de T_fuente", "KF-M04 + KF-M04b", "puntos genuinos de la caja M4"),
    ("M04", "07", "ventana_ts", "resultados/2026-10-07_final_M4b/m4b_ventana_por_tsumidero.csv",
     "Ventana KALINA por franjas de T_sumidero", "KF-M04 + KF-M04b", "puntos genuinos de la caja M4"),
    ("M04c", "02", "techo", "resultados/2026-10-07_final_M4c/m4c_techo.csv",
     "Techo de P_baja antes de cortar KALINA", "KF-M04c", "todos los puntos del barrido de P_baja"),
    ("M04c", "03", "techo_palta", "resultados/2026-10-07_final_M4c/m4c_techo_por_palta.csv",
     "Techo de P_baja por franja de P_alta", "KF-M04c", "todos los puntos del barrido de P_baja"),
    ("M05", "02", "resumen", "resultados/2026-10-07_final_M5/m5_resumen.csv",
     "Resumen por escenario de conservación", "KF-M05", "todos los puntos de los escenarios S1 a S5"),
    ("M05", "03", "rangos", "resultados/2026-10-07_final_M5/m5_rangos.csv",
     "Rangos por escenario (KALINA contra no KALINA)", "KF-M05", "puntos genuinos de los escenarios"),
    ("M05c", "02", "frontera", "resultados/2026-10-07_final_M5c/m5c_frontera.csv",
     "Frontera KALINA con las presiones del profesor", "KF-M05c", "todos los puntos del barrido"),
    ("M06", "02", "comparacion", "resultados/2026-10-08_final_M6/m6_comparacion.csv",
     "Paridad teqp contra el motor real", "KF-M06", "puntos emparejados teqp y motor real"),
    ("M06", "03", "subenfriamiento", "resultados/2026-10-08_final_M6/m6_subenfriamiento.csv",
     "Costo del subenfriamiento", "KF-M06", "puntos con el subenfriamiento aplicado"),
    ("M07", "02", "optimos", "resultados/2026-10-07_final_M7/m7_optimos.csv",
     "Óptimos de η por arranque", "KF-M07", "mejores KALINA de cada arranque"),
    ("M09", "02", "escalera", "resultados/2026-10-08_final_M9/m9_escalera.csv",
     "Escalera de conservación de datos del profesor", "KF-M09", "todas las rondas de la escalera"),
    ("M09", "03", "motor_real", "resultados/2026-10-08_final_M9/m9_motor_real.csv",
     "Verificación teqp contra el motor real", "KF-M09", "puntos emparejados teqp y motor real"),
    ("M10", "02", "catalogo", "resultados/2026-10-09_final_M10_husavik/m10_catalogo.csv",
     "Catálogo Húsavík (reproducción de la Fase 3)", "KF-M10", "todos los puntos de Húsavík"),
    ("M10", "03", "ofat", "resultados/2026-10-09_final_M10_husavik/m10_ofat_rangos.csv",
     "Rangos KALINA por variable (Húsavík OFAT)", "KF-M10", "todos los puntos por variable"),
]


def main():
    for mnn in MNN:
        tabla_condiciones(mnn)
        tabla_conteo(mnn)
    casos = {"M04": _sub("M04", "M04b")}
    for mnn, num, slug, ruta, titulo, caso, filtro in RESULTADOS:
        sub = casos.get(mnn) or subcasos_de("KF-" + mnn)
        tabla_resultado(mnn, num, slug, ruta, titulo, caso, sub, filtro)
    print("Tablas de casos y de resultados escritas.")


if __name__ == "__main__":
    main()
