# -*- coding: utf-8 -*-
"""A1 · Verificacion (TASK_CONTEXT af-A1, seccion 7).

Imprime OK/FALLA por check y escribe analisis_final/05_validacion/checks_A1.md.
"""
import os

import pandas as pd

from a1_fuentes import FUENTES, RAIZ, conteos, ruta_origen

CANONICA = "analisis_final/01_datos/todos_los_puntos.csv"
INVENTARIO = "analisis_final/00_inventario"
SALIDA = "analisis_final/05_validacion/checks_A1.md"

ENCABEZADO = ["id_caso", "n_puntos", "genuinos", "KALINA", "KALINA_confiables",
              "CORREGIBLE", "INVIABLE", "NO_CONVERGIO_sin_N2", "N2", "omitidos",
              "fuera_rango"]


def _tabla_casos(tabla):
    filas = []
    for caso, g in tabla.groupby("id_caso", sort=False):
        filas.append([caso] + conteos(g))
    return pd.DataFrame(filas, columns=ENCABEZADO)


def _md(df):
    """Tabla Markdown sin depender de tabulate."""
    cols = list(df.columns)
    lineas = ["| " + " | ".join(str(c) for c in cols) + " |",
              "|" + "|".join([" --- "] * len(cols)) + "|"]
    for _, fila in df.iterrows():
        lineas.append("| " + " | ".join(str(v) for v in fila.tolist()) + " |")
    return lineas


def main():
    tabla = pd.read_csv(CANONICA)
    md, fallas = ["# Checks A1 — tabla canónica y condiciones", ""], 0

    def check(ok, texto, md_texto=None):
        nonlocal fallas
        estado = "OK" if ok else "FALLA"
        if not ok:
            fallas += 1
        print(f"[{estado}] {texto}")
        md.append(f"- **{estado}** — {texto if md_texto is None else md_texto}")

    # 1. Filas por archivo: pandas == filas con ese origen_csv.
    md += ["## 1. Filas leídas = filas en la tabla canónica", ""]
    total_esperado = 0
    for f in FUENTES:
        origen = ruta_origen(f["archivo"])
        n = len(pd.read_csv(os.path.join(RAIZ, f["archivo"])))
        m = int(tabla["origen_csv"].eq(origen).sum())
        total_esperado += n
        check(n == m, f"{origen}: {n} leídas vs {m} en la tabla")
    check(total_esperado == len(tabla),
          f"total {total_esperado} filas de FUENTES vs {len(tabla)} en la tabla")

    # 2. Identificadores completos.
    md += ["", "## 2. Identificadores completos", ""]
    vacios = {c: int(tabla[c].isna().sum() + tabla[c].astype(str).str.strip().eq("").sum())
              for c in ["id_caso", "id_subcaso", "bloque_director"]}
    check(sum(vacios.values()) == 0, f"campos vacíos: {vacios}")

    # 3. id_punto único.
    md += ["", "## 3. id_punto único", ""]
    dup = int(tabla["id_punto"].duplicated().sum())
    check(dup == 0, f"id_punto duplicados = {dup} (n = {len(tabla)})")

    # 4. Conteo por id_caso y clase.
    md += ["", "## 4. Conteo por caso y clase", ""]
    casos = _tabla_casos(tabla)
    print("\n".join(_md(casos)) + "\n")
    md += _md(casos)
    check(True, "conteo por caso y clase (tabla Markdown)")

    # 5. Bloques con firma inconsistente: información, no falla.
    md += ["", "## 5. Bloques con firma inconsistente (INFORMACIÓN)", ""]
    bloques = pd.read_csv(os.path.join(INVENTARIO, "bloques.csv"))
    inconsistentes = bloques[bloques["consistente"] == "no"]
    if inconsistentes.empty:
        print("[INFORMACIÓN] todos los bloques tienen firma consistente")
        md.append("- Todos los bloques tienen firma consistente.")
    else:
        for _, r in inconsistentes.iterrows():
            texto = (f"bloque {r['bloque_director']} (subcasos: {r['id_subcasos']}): "
                     f"{r['diferencias']}")
            print(f"[INFORMACIÓN] {texto}")
            md.append(f"- {texto}")

    # 5b. OAT: variables no movidas que resultan barridas (INFORMACIÓN, no FALLA).
    md += ["", "## 5b. OAT: variables no movidas barridas por grupo (INFORMACIÓN)", ""]
    oat = pd.read_csv(os.path.join(INVENTARIO, "condiciones_oat.csv"))
    anom = oat[(oat["variable"] != oat["variable_movida"]) & (oat["estado"] == "barrido")]
    if anom.empty:
        print("[INFORMACIÓN] ningún grupo OAT tiene variables no movidas barridas")
        md.append("- Ninguno.")
    for (sub, vm), g in anom.groupby(["id_subcaso", "variable_movida"], sort=False):
        texto = f"subcaso {sub}, movida {vm}: {', '.join(g['variable'])}"
        print(f"[INFORMACIÓN] {texto}")
        md.append(f"- {texto}")

    # 6. Conteo de N2 por caso.
    md += ["", "## 6. Conteo de N2 por caso", ""]
    n2 = casos[["id_caso", "N2"]]
    print("\n".join(_md(n2)) + "\n")
    md += _md(n2)
    check(True, "N2 por caso: total = " + str(int(casos["N2"].sum())))

    md += ["", f"**Resultado: {'TODO OK' if fallas == 0 else str(fallas) + ' FALLA(S)'}**"]
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    print(f"\n{SALIDA} escrito. Falls: {fallas}")
    if fallas:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
