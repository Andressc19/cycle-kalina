# -*- coding: utf-8 -*-
"""A2 · Tablas de síntesis TAB-G01 … TAB-G05 (cada fila es un caso con SUS datos fijos).

Escrito por el director (Claude) el 2026-10-10: OpenCode quedó sin modelo disponible.
Nombres, familias y diseños: tabla §2.1 de docs/METODOLOGIA_ANALISIS_RESULTADOS.md.
"""
import numpy as np
import pandas as pd

import pies
from a2_comun import (INV, leer, leer_canon, escribir_tabla, guardar_registro, renombrar)
from nombres import NOMBRE

CASOS = {  # id_caso: (nombre, familia, diseño, punto base)
    "KF-M01": ("Reproducción del caso del profesor", "R", "una variable a la vez sobre PP", "PP"),
    "KF-M02-N1": ("Un solo cambio sobre el profesor", "F", "malla 10 + bisección", "PP"),
    "KF-M02-N2": ("Dos cambios sobre el profesor", "F", "malla 2D + bisección", "PP"),
    "KF-M02R": ("M2 con η y ε en [0.40, 0.95]", "F", "mallas + bisección", "PP"),
    "KF-M02S": ("Sumidero frío con P_baja libre", "F", "malla 2D + bisección", "4 bases"),
    "KF-M03": ("Sensibilidad local alrededor de A*", "L", "OAT 15 + A* ± 1 %", "A*"),
    "KF-M04": ("Sensibilidad global, LHS 300", "G", "LHS", "caja"),
    "KF-M04b": ("Sensibilidad global, LHS 200 (unión 500)", "G", "LHS", "caja"),
    "KF-M04c": ("Techo de P_baja (1500–2500 kPa)", "G", "LHS", "caja"),
    "KF-M05": ("Escenarios de conservación del profesor", "C", "LHS por escenario", "PP parcial"),
    "KF-M05c": ("Franja KALINA con las presiones del profesor", "C", "malla 11×5×3", "PP con PA y PB"),
    "KF-M06": ("Verificación con el motor real", "V", "puntos de control", "puntos clave"),
    "KF-M07": ("Máxima η dentro de KALINA", "O", "búsqueda por patrones", "5 arranques"),
    "KF-M09": ("Escalera de conservación del profesor", "C", "selección hacia adelante + LHS", "PP parcial"),
    "KF-M10": ("Húsavík revisitado", "H", "recorrida + OFAT + malla", "ancla de Húsavík"),
    "KF-M10b": ("Húsavík con x_b bajo", "H", "OFAT + malla", "ancla de Húsavík"),
}
CRIT = ["O1", "O2", "O3", "O5"]


def _meta(num, titulo, filtro, fuente, n, subcasos, notas=""):
    return {"tabla": f"TAB-G{num}", "carpeta": "G", "hoja": f"G{num}_{titulo.split()[0].lower()}",
            "titulo": titulo, "casos": "todos (síntesis)", "bloques": "uno por fila",
            "subcasos": subcasos, "punto_base": "el de cada fila (columna 'Punto base' o 'Datos fijos')",
            "filtro": filtro, "fuente": fuente, "n": n, "notas": notas}


def _dominante(g):
    nok = g[(g["genuino"].astype(bool)) & (g["clasificacion"] != "KALINA")]
    cuenta = {c: int((pd.to_numeric(nok[f"viol_{c}"], errors="coerce") > 0).sum()) for c in CRIT}
    c = max(cuenta, key=cuenta.get)
    return f"{c} ({cuenta[c]} de {len(nok)})" if cuenta[c] else "—"


def _bloques(g):
    b = list(dict.fromkeys(g["bloque_director"]))
    return ", ".join(b) if len(b) <= 5 else f"{b[0].split('-')[0]}-* ({len(b)} conjuntos)"


def g01(d, bloques):
    filas = []
    for idc, (nom, fam, dis, base) in CASOS.items():
        g = d[d["id_caso"] == idc]
        filas.append({"ID": idc, "Nombre": nom, "Familia": fam,
                      "Bloque(s)": _bloques(g),
                      "Punto base": base, "Diseño": dis, "Corridas": len(g),
                      "Genuinas": int(g["genuino"].astype(bool).sum()),
                      "KALINA": int((g["clasificacion"] == "KALINA").sum()),
                      "KALINA confiables": int(g["kalina_confiable"].astype(bool).sum()),
                      "Falsos convergidos (N2)": int(g["es_N2"].astype(bool).sum()),
                      "Criterio que más bloquea": _dominante(g)})
    df = pd.DataFrame(filas)
    tipos = {c: ("int" if df[c].dtype != object else "txt") for c in df.columns}
    escribir_tabla(_meta("01", "Resumen de casos", "todos los puntos (sin KF-M08)",
                         "todos_los_puntos.csv", len(df), list(d["id_subcaso"].unique()),
                         "Familias: R reproducibilidad, F factibilidad, L local, G global, "
                         "C conservación, O optimización, V verificación, H Húsavík."), df, tipos)


def g02():
    m = leer(f"{INV}/casos_x_variables.csv")
    m = m[~m["id_subcaso"].str.startswith("KF-M08")]
    m = m.rename(columns={c: NOMBRE.get(c, c) for c in m.columns}).rename(columns={"id_subcaso": "Subcaso"})
    escribir_tabla(_meta("02", "Qué se movió en cada barrido", "todos los subcasos (sin KF-M08)",
                         "casos_x_variables.csv", len(m), list(m["Subcaso"]),
                         "=PP: igual al profesor; fijo:<valor>: fijo en otro valor; barrido:[a, b]: barrida."),
                 m, {c: "txt" for c in m.columns})


def g03(d):
    grupos = [("KF-M04 + KF-M04b", ["B07"])] + \
             [(f"KF-M05 escenario S{k}", [f"B09-{k}"]) for k in "12345"] + \
             [("KF-M05c", ["B10"]), ("KF-M09 conjunto final XB+PA+EF+PB", ["B13-XB_PA_EF_PB"]),
              ("KF-M10 + KF-M10b malla", ["B14-MALLA"])]
    filas = []
    for nombre, bl in grupos:
        g = d[d["bloque_director"].isin(bl) & d["kalina_confiable"].astype(bool)]
        subs = list(d[d["bloque_director"].isin(bl)]["id_subcaso"].unique())
        fijos = pies.condiciones_texto(subs).splitlines()[0]
        for v in ["P_alta", "P_baja", "dP", "rP", "T_fuente", "x_b"]:
            x = pd.to_numeric(g[v], errors="coerce").dropna()
            fila = {"Caso": nombre, "Bloque": ", ".join(bl), "Datos fijos": fijos,
                    "Variable": NOMBRE.get(v, v), "n KALINA confiables": len(x)}
            for etq, q in (("p5", 5), ("Mediana", 50), ("p95", 95)):
                fila[etq] = float(np.percentile(x, q)) if len(x) else None
            filas.append(fila)
    df = pd.DataFrame(filas)
    tipos = {c: "txt" for c in df.columns} | {"n KALINA confiables": "int", "p5": "gen",
                                               "Mediana": "gen", "p95": "gen"}
    escribir_tabla(_meta("03", "Rangos KALINA comparados", "solo KALINA confiables",
                         "todos_los_puntos.csv", len(df), [],
                         "Cada caso tiene datos fijos distintos: comparar rangos entre filas, no puntos. "
                         "Percentiles con numpy (método lineal)."), df, tipos)


def g04():
    datos = [("P_alta", "3000 kPa", "sí", "M9 (XB+PA+EF+PB), M5c"),
             ("P_baja", "400 kPa", "sí", "M9; con su clima de 300 K exige ε_cond ≥ 0.875 (M5c)"),
             ("x_b", "0.50", "sí", "M9; es el límite inferior útil (M10b)"),
             ("η_t", "0.85", "sí", "M9 (grupo EF)"), ("η_p", "0.75", "sí", "M9 (grupo EF)"),
             ("ε_HRVG", "0.85", "sí", "M9 (grupo EF)"), ("ε_reg", "0.75", "sí", "M9 (grupo EF)"),
             ("ε_cond", "0.80", "sí, si el sitio es más frío (≤ ~293 K)", "M9; con 300 K hace falta ≥ 0.875 (M5c)"),
             ("T_sumidero", "300.03 K", "con condiciones: o se baja a 280–293 K, o se sube ε_cond", "M9, M5c"),
             ("T_fuente", "623.15 K", "no (bloqueo estructural)", "M1, M2, M9 (0 confiables con TF)"),
             ("m_b", "1 kg/s", "sí (base de cálculo)", "todas")]
    df = pd.DataFrame(datos, columns=["Dato", "Valor del profesor", "¿Se conserva con KALINA?", "Respaldo"])
    escribir_tabla(_meta("04", "Datos del profesor conservables", "conclusiones validadas por A4",
                         "fichas KF-M05c y KF-M09; validación A4", len(df), []), df,
                   {c: "txt" for c in df.columns})


def g05(d):
    filas = []
    for idc in CASOS:
        g = d[d["id_caso"] == idc]
        nok = g[g["genuino"].astype(bool) & (g["clasificacion"] != "KALINA")]
        fila = {"ID": idc, "Genuinos no KALINA": len(nok)}
        for c in CRIT:
            k = int((pd.to_numeric(nok[f"viol_{c}"], errors="coerce") > 0).sum())
            fila[f"{c} (n)"] = k
            fila[f"{c} [%]"] = 100 * k / len(nok) if len(nok) else None
        filas.append(fila)
    df = pd.DataFrame(filas)
    tipos = {c: ("pct1" if "[%]" in c else "int") for c in df.columns} | {"ID": "txt"}
    escribir_tabla(_meta("05", "Criterios de bloqueo por caso", "genuinos que no son KALINA",
                         "todos_los_puntos.csv", len(df), [],
                         "Un punto puede violar varios criterios: los % no suman 100. O1 título, "
                         "O2 cavitación, O3 trabajo neto, O5 separador."), df, tipos)


if __name__ == "__main__":
    d = leer_canon()
    d = d[d["id_caso"] != "KF-M08"]
    g01(d, None); g02(); g03(d); g04(); g05(d)
    print("Tablas de síntesis escritas (TAB-G01 … TAB-G05).")
