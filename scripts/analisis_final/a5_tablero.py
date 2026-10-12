# -*- coding: utf-8 -*-
"""A5 · Construye el tablero HTML interactivo `tablero_kalina.html`."""
import json, os, pandas as pd

import codigos
from nombres import ETIQUETA_CLASE, GLOSARIO, NOMBRE

CANONICA = "analisis_final/01_datos/todos_los_puntos.csv"
CONDICIONES = "analisis_final/00_inventario/condiciones_por_subcaso.csv"
BLOQUES = "analisis_final/00_inventario/bloques.csv"
CASOS = "analisis_final/00_inventario/casos.csv"
PLANTILLA = "scripts/analisis_final/a5_plantilla.html"
CSS = "scripts/analisis_final/a5_estilos.css"
JS = ["scripts/analisis_final/a5_graficos.js",  # primero: define pinta/activarSec
      "scripts/analisis_final/a5_app.js"]
SALIDA = "analisis_final/06_tablero/tablero_kalina.html"

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
DESCRIPCION_BLOQUE = {
    "B01": "reproducción del caso del profesor",
    "B02": "un solo cambio sobre el profesor",
    "B03-A": "dos cambios, ruta A: ε_HRVG y P_baja",
    "B03-B": "dos cambios, ruta B: T_fuente y P_baja",
    "B04": "η y ε en [0.40, 0.95], parte {sufijo}",
    "B05": "sumidero frío, base {sufijo}",
    "B06": "sensibilidad local alrededor de A*",
    "B07": "muestreo LHS de 500 puntos",
    "B08": "LHS con P_baja de 1500 a 2500 kPa",
    "B09": "conservando datos del profesor, escenario S{sufijo}",
    "B10": "presiones del profesor: franja T_fuente × ε_cond",
    "B11": "búsqueda de η máxima, arranque {sufijo}",
    "B12": "puntos de control (verificación)",
    "B13": "escalera de conservación: {sufijo}",
    "B14-F3": "Húsavík: re-evaluación de la Fase 3",
    "B14-MALLA": "Húsavík: malla x_b × P_baja",
    "B14-OFAT": "Húsavík: una variable a la vez",
    "B14-OFATb": "Húsavík: x_b bajo (0.30–0.70)",
}
PUNTO_BASE = {
    "B01": "PP = datos del enunciado del profesor",
    "B02": "PP = datos del enunciado del profesor",
    "B03": "PP = datos del enunciado del profesor",
    "B04": "PP = datos del enunciado del profesor",
    "B05-B1": "PP con T_fuente = 403 K (la fuente de A*)",
    "B05-B2": "PP con T_fuente = 420 K",
    "B05-B3": "PP con ε_HRVG = 0.40",
    "B05-B4": "PP exacto",
    "B06": "A* = punto del profesor con T_fuente = 403 K y P_baja = 563.64 kPa (KALINA, η = 8.48 %)",
    "B14": "Ancla de Húsavík: P_alta 3300 kPa, P_baja 690 kPa, T_fuente 394.15 K, T_sumidero 278.15 K",
}
PUNTO_BASE_DEFAULT = "Sin punto base: las variables barridas se sortean dentro de su rango"

def nulo(v):
    if v is None: return True
    try: return bool(pd.isna(v))
    except (TypeError, ValueError): return False

def verdadero(v):
    if isinstance(v, str): return v.strip().lower() in ("true", "1", "verdadero", "si", "sí")
    return bool(v)

def num5(v): return float(f"{float(v):.5g}")

def valor_punto(col, v):
    if col in BOOL: return None if nulo(v) else verdadero(v)
    if col in TEXTO: return None if (nulo(v) or str(v).strip() == "") else str(v)
    return None if nulo(v) else num5(v)

def valor_simple(col, v):
    if nulo(v) or (isinstance(v, str) and v.strip() == ""): return None
    if col == "n_valores": return int(v)
    if col in MIXTO:
        try: return num5(v)
        except (TypeError, ValueError): return str(v)
    if col in SIMPLES: return str(v)
    try: return num5(v)
    except (TypeError, ValueError): return str(v)

def registros(df, columnas, valor):
    return [{c: valor(c, fila[c]) for c in columnas} for _, fila in df.iterrows()]

def buscar_prefijo(codigo, tabla, defecto=None):
    partes = codigo.split("-")
    while partes:
        pref = "-".join(partes)
        if pref in tabla:
            resto = codigo[len(pref):].lstrip("-")
            return tabla[pref].format(sufijo=resto)
        partes.pop()
    return defecto

def _nomenclatura(puntos, condiciones, bloques):
    """Estudio (3.2), parte (4.1c) y etiquetas en palabras en lugar de KF-M…, B… (2026-10-12)."""
    for r in puntos:                                   # 4.1c-0042 en lugar de KF-M05-3-0042
        sub = str(r.get("id_subcaso"))
        r["id_punto"] = f"{codigos.parte(sub)[0]}-{str(r.get('id_punto'))[-4:]}"
    for r in puntos + condiciones:
        r["id_caso"] = codigos.estudio(r.get("id_caso"))
        r["id_subcaso"] = codigos.etiqueta(r.get("id_subcaso"))
        if "bloque_director" in r:
            r["bloque_director"] = codigos.bloque(r["bloque_director"])
    for b in bloques:
        b["descripcion"] = codigos.etiqueta_bloque(b["bloque_director"]).split(" · ", 1)[1]
        b["bloque_director"] = codigos.bloque(b["bloque_director"])
        b["id_subcasos"] = "; ".join(codigos.etiqueta(s.strip()) for s in str(b["id_subcasos"]).split(";"))
        b["id_casos"] = " + ".join(dict.fromkeys(codigos.estudio(c) for c in str(b["id_casos"]).split(" + ")))
    orden = lambda b: [float(x) if x.replace(".", "").isdigit() else 0 for x in   # noqa: E731
                       b["bloque_director"].split(" ")[0].rstrip("abcde").split(".")]
    bloques.sort(key=orden)


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
    casos_b = (canonica.groupby("bloque_director")["id_caso"]
               .apply(lambda s: " + ".join(sorted(set(s)))) .to_dict())
    for b in bloques:
        cod = b["bloque_director"]
        b["id_casos"] = casos_b.get(cod, "")
        b["descripcion"] = buscar_prefijo(cod, DESCRIPCION_BLOQUE, cod)
        b["punto_base"] = buscar_prefijo(cod, PUNTO_BASE, PUNTO_BASE_DEFAULT)

    cas = pd.read_csv(CASOS)
    cas = cas[cas["id_caso"] != "KF-M08"]
    cas = cas.assign(id_caso=cas["id_caso"].map(codigos.estudio)).groupby("id_caso", sort=False,
                                                                          as_index=False).sum()
    cas = cas.sort_values("id_caso", key=lambda c: c.map(lambda x: [int(t) for t in x.split(".")]))
    casos = registros(cas, list(cas.columns), valor_simple)
    _nomenclatura(puntos, condiciones, bloques)       # códigos nuevos en todo lo que se muestra

    datos = {"PUNTOS": puntos, "CONDICIONES": condiciones, "BLOQUES": bloques,
             "CASOS": casos, "NOMBRE": NOMBRE, "ETIQUETA_CLASE": ETIQUETA_CLASE,
             "GLOSARIO": GLOSARIO, "COLOR_CLASE": COLOR_CLASE,
             "FORMA_CLASE": FORMA_CLASE}

    with open(PLANTILLA, encoding="utf-8") as f: html = f.read()
    with open(CSS, encoding="utf-8") as f: css = f.read()
    js = "\n".join(open(p, encoding="utf-8").read() for p in JS)

    html = html.replace("__CSS__", css)
    html = html.replace("__DATOS__", json.dumps(datos, ensure_ascii=False))
    html = html.replace("__JS__", js)

    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as f: f.write(html)

    mb = os.path.getsize(SALIDA) / (1024 * 1024)
    print(f"OK: {SALIDA} ({mb:.2f} MB)")
    print(f"PUNTOS={len(puntos)} CONDICIONES={len(condiciones)} "
          f"BLOQUES={len(bloques)} CASOS={len(casos)}")

if __name__ == "__main__": main()
