# -*- coding: utf-8 -*-
"""A1 · Esquema estrella para Power BI (TASK_CONTEXT af-A1, seccion 6).

Salida: analisis_final/07_powerbi/
"""
import os
import shutil

import pandas as pd

from nombres import ETIQUETA_CLASE, NOMBRE

CANONICA = "analisis_final/01_datos/todos_los_puntos.csv"
INVENTARIO = "analisis_final/00_inventario"
DESTINO = "analisis_final/07_powerbi"

COLORES = {"KALINA": "#2E7D32", "CORREGIBLE": "#EF8A17", "INVIABLE": "#C9A227",
           "NO_CONVERGIO": "#C62828", "N2": "#9E9E9E", "OMITIDO": "#BDBDBD"}


def _unidad(nombre):
    """Unidad entre corchetes del nombre de presentacion ('' si no tiene)."""
    if "[" in nombre and "]" in nombre:
        return nombre.split("[", 1)[1].split("]", 1)[0]
    return ""


def main():
    os.makedirs(DESTINO, exist_ok=True)

    # 1. hechos: la tabla canonica completa (copia textual, sin reparsear).
    shutil.copyfile(CANONICA, os.path.join(DESTINO, "hechos_puntos.csv"))

    # 2. dim_caso: casos.csv + bloque_director (todos los bloques del caso).
    casos = pd.read_csv(os.path.join(INVENTARIO, "casos.csv"))
    puntos = pd.read_csv(CANONICA, usecols=["id_caso", "bloque_director"])
    bloques = (puntos.drop_duplicates().groupby("id_caso", sort=False)["bloque_director"]
               .apply(lambda s: "; ".join(s)))
    casos["bloque_director"] = casos["id_caso"].map(bloques)
    casos.to_csv(os.path.join(DESTINO, "dim_caso.csv"), index=False)

    # 3. dim_condiciones: copia del inventario.
    shutil.copyfile(os.path.join(INVENTARIO, "condiciones_por_subcaso.csv"),
                    os.path.join(DESTINO, "dim_condiciones.csv"))

    # 4. dim_variable: nombre de presentacion y unidad desde NOMBRE.
    var = pd.DataFrame([{"variable": k, "nombre_presentacion": v,
                         "unidad": _unidad(v)} for k, v in NOMBRE.items()])
    var.to_csv(os.path.join(DESTINO, "dim_variable.csv"), index=False)

    # 5. dim_clase: etiqueta, color y orden.
    clase = pd.DataFrame([{"clase": k, "etiqueta": ETIQUETA_CLASE[k],
                           "color": COLORES[k], "orden": i}
                          for i, k in enumerate(COLORES, start=1)])
    clase.to_csv(os.path.join(DESTINO, "dim_clase.csv"), index=False)

    print(f"{DESTINO}: hechos_puntos={len(puntos)} filas, dim_caso={len(casos)}, "
          f"dim_variable={len(var)}, dim_clase={len(clase)}")


if __name__ == "__main__":
    main()
