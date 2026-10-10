# -*- coding: utf-8 -*-
"""A5 · Construye el tablero HTML interactivo `tablero_kalina.html`.

Lee la tabla canónica y los inventarios, arma los JSON y une CSS + JSON + JS en
la plantilla. Escribe SOLO en analisis_final/06_tablero/tablero_kalina.html.
"""
import json
import os

import pandas as pd

from nombres import ETIQUETA_CLASE, GLOSARIO, NOMBRE

CANONICA = "analisis_final/01_datos/todos_los_puntos.csv"
CONDICIONES = "analisis_final/00_inventario/condiciones_por_subcaso.csv"
BLOQUES = "analisis_final/00_inventario/bloques.csv"
CASOS = "analisis_final/00_inventario/casos.csv"
PLANTILLA = "scripts/analisis_final/a5_plantilla.html"
CSS = "scripts/analisis_final/a5_estilos.css"
JS = "scripts/analisis_final/a5_app.js"
SALIDA = "analisis_final/06_tablero/tablero_kalina.html"

# Columnas pedidas por el TASK_CONTEXT (31). EXTRA se añade a propósito: el filtro
# OAT del eje X necesita saber qué variable mueve cada punto (desviación documentada).
COLUMNAS = ["id_punto", "id_caso", "id_subcaso", "bloque_director", "tipo_punto",
            "clase_trazo", "genuino", "kalina_confiable", "fuera_rango", "omitido",
            "wnet_pos", "T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "eta_t",
            "eta_p", "eps_hrvg", "eps_reg", "eps_cond", "T_amb_diseno", "eta_pct",
            "Wnet", "dP", "rP", "D", "viol_O1", "viol_O2", "viol_O3", "viol_O5"]
EXTRA = "variable"
BOOL = ["genuino", "kalina_confiable", "fuera_rango", "omitido", "wnet_pos"]
TEXTO = ["id_punto", "id_caso", "id_subcaso", "bloque_director", "tipo_punto",
         "clase_trazo", "variable"]
MIXTO = ["valor_fijo", "valor_base", "min", "max"]
SIMPLES = ["id_caso", "id_subcaso", "bloque_director", "variable", "estado",
           "igual_al_profesor", "unidad", "es_oat", "firma", "consistente",
           "diferencias", "diferencias_barrido", "id_subcasos"]
COLOR_CLASE = {"KALINA": "#2E7D32", "CORREGIBLE": "#EF8A17", "INVIABLE": "#C9A227",
               "NO_CONVERGIO": "#C62828", "N2": "#9E9E9E", "OMITIDO": "#BDBDBD"}
FORMA_CLASE = {"KALINA": "circle", "CORREGIBLE": "triangle", "INVIABLE": "rect",
               "NO_CONVERGIO": "crossRot", "N2": "crossRot", "OMITIDO": "rect"}


def nulo(v):
    """True si v es None o NaN."""
    if v is None:
        return True
    try:
        return bool(pd.isna(v))
    except (TypeError, ValueError):
        return False


def verdadero(v):
    """True solo para verdaderos; NaN/None/'' cuentan falso."""
    if isinstance(v, str):
        return v.strip().lower() in ("true", "1", "verdadero", "si", "sí")
    return bool(v)


def num5(v):
    """Redondeo a 5 cifras significativas."""
    return float(f"{float(v):.5g}")


def valor_punto(col, v):
    """Convierte una celda de PUNTOS a JSON seguro."""
    if col in BOOL:
        return None if nulo(v) else verdadero(v)
    if col in TEXTO:
        return None if (nulo(v) or str(v).strip() == "") else str(v)
    return None if nulo(v) else num5(v)


def valor_simple(col, v):
    """Convierte una celda de CONDICIONES/BLOQUES/CASOS a JSON seguro."""
    if nulo(v) or (isinstance(v, str) and v.strip() == ""):
        return None
    if col == "n_valores":
        return int(v)
    if col in MIXTO:
        try:
            return num5(v)
        except (TypeError, ValueError):
            return str(v)
    if col in SIMPLES:
        return str(v)
    try:
        return num5(v)
    except (TypeError, ValueError):
        return str(v)


def registros(df, columnas, valor):
    """Lista de diccionarios JSON-seguros para las columnas dadas."""
    return [{c: valor(c, fila[c]) for c in columnas} for _, fila in df.iterrows()]


def main():
    canonica = pd.read_csv(CANONICA)
    canonica = canonica[canonica["id_caso"] != "KF-M08"]
    cols = COLUMNAS + [EXTRA]
    puntos = registros(canonica[cols], cols, valor_punto)

    cond = pd.read_csv(CONDICIONES)
    cond = cond[cond["id_caso"] != "KF-M08"]
    condiciones = registros(cond, list(cond.columns), valor_simple)

    blo = pd.read_csv(BLOQUES)
    blo = blo[blo["bloque_director"] != "BX"]
    bloques = registros(blo, list(blo.columns), valor_simple)

    cas = pd.read_csv(CASOS)
    cas = cas[cas["id_caso"] != "KF-M08"]
    casos = registros(cas, list(cas.columns), valor_simple)

    datos = {"PUNTOS": puntos, "CONDICIONES": condiciones, "BLOQUES": bloques,
             "CASOS": casos, "NOMBRE": NOMBRE, "ETIQUETA_CLASE": ETIQUETA_CLASE,
             "GLOSARIO": GLOSARIO, "COLOR_CLASE": COLOR_CLASE,
             "FORMA_CLASE": FORMA_CLASE}

    with open(PLANTILLA, encoding="utf-8") as f:
        html = f.read()
    with open(CSS, encoding="utf-8") as f:
        css = f.read()
    with open(JS, encoding="utf-8") as f:
        js = f.read()

    html = html.replace("__CSS__", css)
    html = html.replace("__DATOS__", json.dumps(datos, ensure_ascii=False))
    html = html.replace("__JS__", js)

    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write(html)

    mb = os.path.getsize(SALIDA) / (1024 * 1024)
    print(f"OK: {SALIDA} ({mb:.2f} MB)")
    print(f"PUNTOS={len(puntos)} CONDICIONES={len(condiciones)} "
          f"BLOQUES={len(bloques)} CASOS={len(casos)}")


if __name__ == "__main__":
    main()
