# -*- coding: utf-8 -*-
"""A1 · Pies de figura (TASK_CONTEXT af-A1 sección 5; af-A1b correcciones 1 y 4).

condiciones_texto() y armar_pie() leen 00_inventario/condiciones_por_subcaso.csv
(y, para los barridos de a una variable, condiciones_oat.csv) para que ningún pie
pueda contradecir los datos.
"""
import pandas as pd

from a1_fuentes import ENTRADAS, UNIDAD, sig6

CONDICIONES = "analisis_final/00_inventario/condiciones_por_subcaso.csv"
OAT = "analisis_final/00_inventario/condiciones_oat.csv"


def _fmt4(valor):
    """Valor con 4 cifras significativas."""
    return f"{float(valor):.5g}"  # 5 cifras: 300.03 K no se lee como 300 K


def _numero(serie):
    return pd.to_numeric(serie, errors="coerce")


def _nulo(x):
    """True si x es None o NaN."""
    if x is None:
        return True
    try:
        return bool(pd.isna(x))
    except (TypeError, ValueError):
        return False


def _con_unidad(var, texto):
    """'<var> = <texto> <unidad>'; 'motor' no lleva unidad."""
    u = "" if var == "motor" or UNIDAD[var] == "–" else UNIDAD[var]
    return f"{var} = {texto}" + (f" {u}" if u else "")


def _barrido(var, lo, hi, n):
    """'<var> [min–max] <unidad> (n valores)' (o sin rango si no hay min/max)."""
    u = "" if var == "motor" or UNIDAD[var] == "–" else UNIDAD[var]
    if not _nulo(lo):
        return (f"{var} [{_fmt4(lo)}–{_fmt4(hi)}]" + (f" {u}" if u else "")
                + f" ({n} valores)")
    return f"{var} ({n} valores)"


def _texto_oat(fijos, barridos):
    """Dos líneas del barrido de una variable a la vez."""
    return ("Punto base (las demás variables quedan fijas en): "
            + ("; ".join(fijos) if fijos else "ninguno")
            + ". Cada panel o tramo mueve solo su variable.\n"
            + "Datos barridos (uno a la vez): "
            + ("; ".join(barridos) if barridos else "ninguno") + ".")


def _base_oat(c):
    """Punto base desde valor_base (variables con estado 'sin_dato' se omiten)."""
    fijos = []
    for var in ENTRADAS:
        b = c[c["variable"] == var]
        if b.empty or (b["estado"] == "sin_dato").all():
            continue
        valor = b["valor_fijo"].iloc[0] if var == "motor" else b["valor_base"].iloc[0]
        if _nulo(valor) or str(valor).strip() == "":
            continue
        fijos.append(_con_unidad(var, str(valor) if var == "motor" else _fmt4(valor)))
    return fijos


def _base_grupo(o):
    """Punto base de un grupo OAT desde condiciones_oat.csv."""
    fijos = []
    for var in ENTRADAS:
        b = o[(o["variable"] == var) & (o["estado"] == "fijo")]
        if b.empty:
            continue
        valor = b["valor_fijo"].iloc[0]
        if _nulo(valor) or str(valor).strip() == "":
            continue
        fijos.append(_con_unidad(var, str(valor) if var == "motor" else _fmt4(valor)))
    return fijos


def _barridos(df):
    """Lista de variables con estado 'barrido' en df."""
    barr = []
    for var in ENTRADAS:
        b = df[(df["variable"] == var) & (df["estado"] == "barrido")]
        if b.empty:
            continue
        lo, hi = _numero(b["min"]).min(), _numero(b["max"]).max()
        n = int(pd.to_numeric(b["n_valores"]).max())
        barr.append(_barrido(var, lo, hi, n))
    return barr


def _texto_normal(c, id_subcasos):
    """Dos líneas clásicas: datos fijos comunes y datos barridos."""
    fijos, barridos = [], []
    for var in ENTRADAS:
        bloque = c[c["variable"] == var]
        if bloque.empty:
            continue
        estados = list(bloque["estado"])
        if len(estados) == len(id_subcasos) and set(estados) == {"fijo"}:
            if var == "motor":
                claves = {str(v) for v in bloque["valor_fijo"]}
            else:
                claves = {sig6(v) for v in _numero(bloque["valor_fijo"])}
            if len(claves) == 1:
                valor = bloque["valor_fijo"].iloc[0]
                fijos.append(_con_unidad(var, valor if var == "motor"
                                         else _fmt4(valor)))
        if "barrido" in estados:
            barridos.append(_barrido(var, *_rango(bloque)))
    return ("Datos fijos: " + ("; ".join(fijos) if fijos else "ninguno") + ".\n"
            + "Datos barridos: " + ("; ".join(barridos) if barridos else "ninguno")
            + ".")


def _rango(bloque):
    """(min, max, n) de los barridos de una variable en un grupo de subcasos."""
    b = bloque[bloque["estado"] == "barrido"]
    lo, hi = _numero(b["min"]).min(), _numero(b["max"]).max()
    n = int(pd.to_numeric(b["n_valores"]).max())
    return lo, hi, n


def condiciones_texto(id_subcasos, variable_movida=None, ruta=CONDICIONES):
    """Pie de condiciones: fijos y barridos; si todos son OAT, formato OAT."""
    c = pd.read_csv(ruta)
    c = c[c["id_subcaso"].isin(id_subcasos)]
    if variable_movida is not None:
        o = pd.read_csv(OAT)
        o = o[o["id_subcaso"].isin(id_subcasos)
              & (o["variable_movida"] == variable_movida)]
        return _texto_oat(_base_grupo(o), _barridos(o))
    if len(c) and "es_oat" in c.columns and c["es_oat"].eq("sí").all():
        return _texto_oat(_base_oat(c), _barridos(c))
    return _texto_normal(c, id_subcasos)


def armar_pie(id_fig, titulo, id_subcasos, bloque, filtro, n, fuente,
              marcas="", base="", ruta=CONDICIONES):
    """Pie de figura con el formato del TASK_CONTEXT af-A1 sección 5."""
    linea_casos = f"Caso(s): {', '.join(id_subcasos)} (bloque {bloque})."
    if base:
        linea_casos += f" Punto base: {base}"
    linea_filtro = f"Filtro: {filtro}."
    if marcas:
        linea_filtro += f" Marcas: {marcas}"
    if _nulo(n):
        ultima = f"Fuente: {fuente}."
    else:
        ultima = f"n = {n}. Fuente: {fuente}."
    return "\n".join([
        f"Figura {id_fig}. {titulo}.", linea_casos,
        condiciones_texto(id_subcasos, ruta=ruta), linea_filtro, ultima,
    ])
