# -*- coding: utf-8 -*-
"""A2 · Utilidades comunes: rutas, lecturas, formato en español y escritura de tablas.

Cada tabla va en CSV y en Markdown (§3A.5: encabezado, cuerpo, notas); el registro
02_tablas/registro_tablas.csv alimenta los encabezados del libro Excel.
"""
import os
import sys

import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
if AQUI not in sys.path:
    sys.path.insert(0, AQUI)

from a2_columnas import ETA_FRAC, PROPIAS, tipo_por_unidad  # noqa: E402
from nombres import NOMBRE  # noqa: E402
import pies  # noqa: E402

TABLAS = os.path.join(RAIZ, "analisis_final", "02_tablas")
INV = os.path.join(RAIZ, "analisis_final", "00_inventario")
CANON = os.path.join(RAIZ, "analisis_final", "01_datos", "todos_los_puntos.csv")
RES = os.path.join(RAIZ, "resultados")
LIBRO = os.path.join(RAIZ, "datos", "Excel_kalina_final_final_final.xlsx")
EXCEL_VIEJO = os.path.join(RAIZ, "datos", "Excel_final_kalina.xlsx")
REGISTRO = os.path.join(TABLAS, "registro_tablas.csv")
TRADUCCIONES = os.path.join(TABLAS, "traducciones_columnas.csv")

MNN = ["M01", "M02-N1", "M02-N2", "M02R", "M02S", "M03", "M04", "M04b", "M04c",
       "M05", "M05c", "M06", "M07", "M09", "M10", "M10b"]

PROFESOR = {"P_alta": 3000.0, "P_baja": 400.0, "x_b": 0.50, "T_fuente": 623.15,
            "T_sumidero": 300.032917, "m_b": 1.0, "eta_t": 0.85, "eta_p": 0.75,
            "eps_hrvg": 0.85, "eps_reg": 0.75, "eps_cond": 0.80}

COLOR_CLASE = {"KALINA": "C6EFCE", "CORREGIBLE": "FFD9A0", "NO_CONVERGIO": "F8B4B4",
               "INVIABLE": "FFF2A8", "N2": "D9D9D9"}

_trad_pend = {}


def leer(ruta): return pd.read_csv(ruta)
def leer_canon(): return leer(CANON)
def leer_conteo(): return leer(os.path.join(INV, "conteo_por_subcaso.csv"))
def leer_condiciones(): return leer(os.path.join(INV, "condiciones_por_subcaso.csv"))
def leer_bloques(): return leer(os.path.join(INV, "bloques.csv"))


def subcasos_de(id_caso):
    """Lista de id_subcaso de un caso, en orden de aparición."""
    c = leer_condiciones()
    return list(dict.fromkeys(c.loc[c["id_caso"] == id_caso, "id_subcaso"]))


def bloques_de(subcasos):
    """Conjunto ordenado de bloque_director de una lista de subcasos."""
    c = leer_condiciones()
    vistos = c[c["id_subcaso"].isin(subcasos)]["bloque_director"]
    return list(dict.fromkeys(vistos))


def nombre_es(col):
    """Nombre en español de una columna (NOMBRE tiene prioridad; si no, PROPIAS)."""
    if col in NOMBRE:
        return NOMBRE[col]
    if col in PROPIAS:
        return PROPIAS[col][0]
    return None


def tipo_de(col):
    if col in NOMBRE:
        return tipo_por_unidad(NOMBRE[col])
    if col in PROPIAS:
        return PROPIAS[col][1]
    return "gen"


def anotar_traduccion(tabla, col, nombre, unidad):
    if col in NOMBRE:
        return
    _trad_pend[(tabla, col)] = (nombre, unidad)


def renombrar(df, tabla):
    """Devuelve (df con encabezados en español, dict nombre_es -> tipo)."""
    salida, tipos = {}, {}
    for col in df.columns:
        es = nombre_es(col)
        if es is None:
            es = col
            print(f"  AVISO: columna sin nombre propuesto en {tabla}: {col}")
        tipo = tipo_de(col)
        if col in ETA_FRAC:
            df[col] = pd.to_numeric(df[col], errors="coerce") * 100.0
        nombre = es if es not in salida else f"{es} ({col})"
        salida[nombre] = df[col].values
        tipos[nombre] = tipo
        unidad = nombre.split("[")[-1].rstrip("]") if "[" in nombre else "–"
        anotar_traduccion(tabla, col, es, unidad)
    return pd.DataFrame(salida), tipos


def volcar_traducciones():
    filas = [{"tabla": t, "columna_original": c, "nombre_propuesto": n, "unidad": u}
             for (t, c), (n, u) in sorted(_trad_pend.items())]
    df = pd.DataFrame(filas, columns=["tabla", "columna_original", "nombre_propuesto", "unidad"])
    if os.path.exists(TRADUCCIONES):
        viejo = pd.read_csv(TRADUCCIONES)
        df = pd.concat([viejo, df]).drop_duplicates(["tabla", "columna_original"], keep="last")
    os.makedirs(TABLAS, exist_ok=True)
    df.to_csv(TRADUCCIONES, index=False, encoding="utf-8-sig")


def formatear(tipo, valor):
    if valor is None:
        return ""
    if isinstance(valor, bool):
        return "sí" if valor else "no"
    try:
        if pd.isna(valor):
            return ""
    except (TypeError, ValueError):
        pass
    if tipo == "txt":
        return str(valor)
    if isinstance(valor, str):
        return valor
    v = float(valor)
    if tipo == "pres":
        return f"{v:.1f}" if abs(v) < 1000 else f"{v:.0f}"
    if tipo == "temp":
        return f"{v:.1f}"
    if tipo in ("pct", "pp"):
        return f"{v:.2f}"
    if tipo == "pct1":
        return f"{v:.1f}"
    if tipo in ("dec3", "idx"):
        return f"{v:.3f}"
    if tipo == "int":
        return str(int(round(v)))
    return str(int(v)) if float(v).is_integer() else f"{v:g}"


def fmt_excel(tipo, valor):
    """Formato de número de Excel para una celda (None = general)."""
    if tipo == "pres":
        try:
            return "0.0" if abs(float(valor)) < 1000 else "0"
        except (TypeError, ValueError):
            return None
    return {"temp": "0.0", "pct": "0.00", "pp": "0.00", "pct1": "0.0", "dec3": "0.000",
            "idx": "0.000", "int": "0"}.get(tipo)


def _md_tabla(df, tipos):
    lineas = ["| " + " | ".join(df.columns) + " |",
              "|" + "|".join(["---"] * len(df.columns)) + "|"]
    for _, fila in df.iterrows():
        celdas = [formatear(tipos.get(c, "gen"), fila[c]).replace("|", "\\|")
                  for c in df.columns]
        lineas.append("| " + " | ".join(celdas) + " |")
    return "\n".join(lineas)


def escribir_tabla(meta, df, tipos):
    """Escribe CSV + Markdown de una tabla y anota su fila en el registro."""
    carpeta = os.path.join(TABLAS, meta["carpeta"])
    os.makedirs(carpeta, exist_ok=True)
    df.to_csv(os.path.join(carpeta, meta["tabla"] + ".csv"), index=False, encoding="utf-8-sig")
    # Síntesis (carpeta G): sin encabezado de condiciones común; cada fila trae los suyos.
    texto = "" if meta["carpeta"] == "G" else pies.condiciones_texto(meta["subcasos"])
    notas = (f"Filtro: {meta['filtro']}. n = {meta['n']}. "
             "† = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido (N2). "
             f"Fuente: {meta['fuente']}.")
    if meta.get("notas"):
        notas += " " + meta["notas"]
    md = [f"# {meta['tabla']} · {meta['titulo']}", "",
          f"**Caso(s):** {meta['casos']} · **Bloque(s):** {meta['bloques']}  ",
          f"**Punto base:** {meta['punto_base']}  ",
          ("**" + texto.replace("\n", "**  \n**") + "**  ") if texto else
          "*Tabla de síntesis: cada fila es un caso con sus propios datos fijos.*", "",
          _md_tabla(df, tipos), "", f"**Notas:** {notas}"]
    with open(os.path.join(carpeta, meta["tabla"] + ".md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    guardar_registro([dict(meta, subcasos="; ".join(meta["subcasos"]))])


def guardar_registro(filas):
    df = pd.DataFrame(filas)
    if os.path.exists(REGISTRO):
        viejo = pd.read_csv(REGISTRO)
        df = pd.concat([viejo, df]).drop_duplicates(["tabla"], keep="last")
    os.makedirs(TABLAS, exist_ok=True)
    df.to_csv(REGISTRO, index=False, encoding="utf-8-sig")


def registro():
    return pd.read_csv(REGISTRO)
