# -*- coding: utf-8 -*-
"""A1 · Tabla canónica de todos los puntos (TASK_CONTEXT af-A1, seccion 2).

Una fila por cada fila de cada archivo de FUENTES (sin deduplicar).
Salida: analisis_final/01_datos/todos_los_puntos.csv
"""
import os

import pandas as pd

from a1_fuentes import (CALCULADAS, CLASES_GENUINAS, COLUMNAS_TABLA,
                        ENTRADAS, FUENTES, PROPIAS, RAIZ, SALIDAS, columnas_de,
                        es_verdadero, ruta_origen, sanea)

SALIDA = "analisis_final/01_datos/todos_los_puntos.csv"


def _plantilla(texto, fila, contexto):
    """Sustituye {col} por el valor de la fila (saneado para el identificador)."""
    valores = {}
    for col in columnas_de(texto):
        if col not in fila.index:
            raise SystemExit(f"FALTA COLUMNA '{col}' en {contexto}")
        v = fila[col]
        if pd.isna(v):
            raise SystemExit(f"VALOR VACIO en columna '{col}' de {contexto}")
        valores[col] = sanea(v)
    return texto.format(**valores)


def main():
    marcos = []
    for fuente in FUENTES:
        contexto = fuente["archivo"]
        df = pd.read_csv(os.path.join(RAIZ, fuente["archivo"]))
        requeridas = columnas_de(fuente["subcaso"]) + columnas_de(fuente["bloque"])
        if isinstance(fuente["tipo_punto"], dict):
            requeridas += [fuente["tipo_punto"]["columna"]]
        faltan = [c for c in requeridas if c not in df.columns]
        if faltan:
            raise SystemExit(f"FALTA COLUMNA en {contexto}: {faltan}")

        ident = pd.DataFrame(index=df.index)
        ident["id_caso"] = fuente["id_caso"]
        if len(df):
            ident["id_subcaso"] = df.apply(
                lambda f: _plantilla(fuente["subcaso"], f, contexto), axis=1)
            ident["bloque_director"] = df.apply(
                lambda f: _plantilla(fuente["bloque"], f, contexto), axis=1)
        else:                      # archivo válido con 0 filas (p. ej. M2R n2a bisec.)
            ident["id_subcaso"] = pd.Series(index=df.index, dtype=object)
            ident["bloque_director"] = pd.Series(index=df.index, dtype=object)
        tp = fuente["tipo_punto"]
        ident["tipo_punto"] = (df[tp["columna"]] if isinstance(tp, dict)
                               else tp)
        ident["origen_csv"] = ruta_origen(fuente["archivo"])
        ident["fila_origen"] = list(range(len(df)))

        conservar = [c for c in ENTRADAS + SALIDAS + PROPIAS if c in df.columns]
        bloque = pd.concat([ident, df[conservar]], axis=1)
        bloque["omitido"] = (df["omitido"] if "omitido" in df.columns else False)
        marcos.append(bloque)
        print(f"{contexto}: {len(df)} filas -> {ident['id_subcaso'].nunique()} subcaso(s)")

    tabla = pd.concat(marcos, ignore_index=True, sort=False)

    # id_punto: contador de 4 digitos por subcaso en orden de lectura.
    n = tabla.groupby("id_subcaso", sort=False).cumcount()
    tabla["id_punto"] = tabla["id_subcaso"] + "-" + n.map("{:04d}".format)

    # Calculadas.
    clase = tabla["clasificacion"]
    convergio = tabla["convergio"].map(es_verdadero)
    fuera = tabla["fuera_rango"].map(es_verdadero)
    tabla["genuino"] = clase.isin(CLASES_GENUINAS)
    tabla["es_N2"] = convergio & clase.eq("NO_CONVERGIO")
    # Confiable = KALINA, dentro del rango del modelo y con η/ε en [0.40, 0.95] (regla del proyecto;
    # excluye los 14 puntos F3 de Húsavík con η_t o ε_cond > 0.95 y los extremos de M8).
    efs = tabla[["eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond"]].apply(pd.to_numeric, errors="coerce")
    realista = ~((efs < 0.40 - 1e-9) | (efs > 0.95 + 1e-9)).any(axis=1)
    tabla["kalina_confiable"] = clase.eq("KALINA") & ~fuera & realista
    tabla["omitido"] = tabla["omitido"].map(es_verdadero)
    wnet = pd.to_numeric(tabla["Wnet"], errors="coerce")
    eta = pd.to_numeric(tabla["eta"], errors="coerce")
    # Sin W_net en la fuente (m6_subenfriamiento_evals) vale η > 0: η = W_net/Q_in con Q_in > 0.
    tabla["wnet_pos"] = (wnet > 0) | (wnet.isna() & (eta > 0))
    tabla["eta_pct"] = pd.to_numeric(tabla["eta"], errors="coerce") * 100
    pa = pd.to_numeric(tabla["P_alta"], errors="coerce")
    pb = pd.to_numeric(tabla["P_baja"], errors="coerce")
    tabla["dP"] = pa - pb
    tabla["rP"] = pa / pb
    tabla["dT_fs"] = (pd.to_numeric(tabla["T_fuente"], errors="coerce")
                      - pd.to_numeric(tabla["T_sumidero"], errors="coerce"))
    trazo = pd.Series(tabla["clasificacion"], dtype=object)
    trazo = trazo.where(~tabla["omitido"], "OMITIDO")
    tabla["clase_trazo"] = trazo.where(~tabla["es_N2"], "N2")

    tabla = tabla.reindex(columns=COLUMNAS_TABLA)
    tabla["fila_origen"] = tabla["fila_origen"].astype(int)
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    tabla.to_csv(SALIDA, index=False)
    print(f"\n{SALIDA}: {len(tabla)} filas, {len(tabla.columns)} columnas, "
          f"{tabla['id_subcaso'].nunique()} subcasos, "
          f"{tabla['id_caso'].nunique()} casos, "
          f"{tabla['bloque_director'].nunique()} bloques")


if __name__ == "__main__":
    main()
