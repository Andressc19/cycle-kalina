# -*- coding: utf-8 -*-
"""A2 · Escritura de tablas con la nomenclatura nueva (codigos.py, 2026-10-12).

Archivo: 02_tablas/<estudio>/Tabla_<estudio>-<n>.csv|md (síntesis: carpeta S). El registro conserva
el identificador interno (TAB-…) para los scripts y agrega el nuevo para todo lo que se muestra.
"""
import os
import re

import codigos
from codigos_texto import traducir


def celda(v):
    """Código de origen exacto → código nuevo; cualquier otro texto se traduce."""
    if not isinstance(v, str):
        return v
    if v in codigos.ESTUDIO:
        return codigos.estudio(v)
    if v in codigos._P or v.startswith("KF-M09-R"):
        return codigos.etiqueta(v)
    if v in codigos._B or v.startswith("B13-"):
        return codigos.bloque(v)
    return traducir(v).replace("N2(", "falso convergido(")


_COLUMNAS = {"Subcaso": "Parte", "Bloque": "Parte", "ID": "Estudio", "Caso": "Estudio",
             "id_subcaso": "Parte", "id_caso": "Estudio"}


def presentar_df(df):
    df = df.rename(columns={c: _COLUMNAS.get(c, c) for c in df.columns})
    for c in df.columns:
        if df[c].dtype == object or str(df[c].dtype).startswith("str"):
            df[c] = df[c].map(celda)
    return df


def nombre_hoja(id_nuevo, titulo):
    t = re.sub(r"[\[\]:*?/\\]", "", f"{id_nuevo} {titulo}")
    return t[:31].rstrip()


def escribir(meta, df, tipos):
    from a2_comun import TABLAS, _md_tabla, guardar_registro, pies
    nuevo = codigos.tabla(meta["tabla"])
    est = nuevo.split("-")[0]
    carpeta = os.path.join(TABLAS, est)
    os.makedirs(carpeta, exist_ok=True)
    archivo = f"Tabla_{nuevo}"
    df = df.apply(lambda s: s.map(lambda v: pies.SIMBOLO.get(v, v) if isinstance(v, str) else v)
                  if s.dtype == object or str(s.dtype).startswith("str") else s)
    df = presentar_df(df)
    tipos = {_COLUMNAS.get(k, k): v for k, v in tipos.items()}
    df.to_csv(os.path.join(carpeta, archivo + ".csv"), index=False, encoding="utf-8-sig")
    titulo = traducir(meta["titulo"])
    partes = list(dict.fromkeys(codigos.parte(s)[0] for s in meta["subcasos"]))
    nombre_est = next((codigos.ESTUDIO[c][1] for c in codigos.ESTUDIO if codigos.estudio(c) == est), "")
    cab = (f"**Estudio {est}** · {nombre_est}" + (f" · **Partes:** {', '.join(partes)}"
           if len(partes) > 1 or (partes and partes[0] != est) else "")) if est != "S" else \
        "**Síntesis de toda la campaña:** cada fila es un estudio o una parte con sus propios datos fijos."
    texto = "" if est == "S" else pies.condiciones_por_bloque(meta["subcasos"])
    notas = (f"Filtro: {traducir(meta['filtro'])}. n = {meta['n']} filas en la tabla. "
             "† = fuera del rango confiable (IAPWS G4-01); ‡ = falso convergido. "
             f"Fuente: {traducir(meta['fuente'])}.")
    if meta.get("notas"):
        notas += " " + traducir(meta["notas"])
    md = [f"# Tabla {nuevo} · {titulo}", "", cab + "  ",
          f"**Punto base:** {traducir(meta['punto_base'])}  " if est != "S" else "",
          ("**" + texto.replace("\n", "**  \n**") + "**  ") if texto else "", "",
          _md_tabla(df, tipos), "", f"**Notas:** {notas}"]
    with open(os.path.join(carpeta, archivo + ".md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    guardar_registro([dict(meta, subcasos="; ".join(meta["subcasos"]), id_nuevo=nuevo,
                           carpeta_nueva=est, archivo=archivo, titulo_nuevo=titulo,
                           cabecera=cab.replace("**", ""), hoja=nombre_hoja(nuevo, titulo),
                           punto_base_nuevo=traducir(meta["punto_base"]), notas_nuevas=notas)])
