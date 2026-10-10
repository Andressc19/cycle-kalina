# -*- coding: utf-8 -*-
# A1 · Condiciones por subcaso (af-A1 secc. 3; af-A1b 1 y 3).
# Detecta desde los datos que variables quedaron fijas y cuales se barrieron.
# Salidas en analisis_final/00_inventario/.
import os
from collections import Counter

import pandas as pd

from a1_fuentes import (ENTRADAS, NOMBRES_CONTEO, PROFESOR, UNIDAD, conteos, fmtg,
                        sig6, vacio)

CANONICA = "analisis_final/01_datos/todos_los_puntos.csv"
SALIDA = "analisis_final/00_inventario"
COLS_COND = ["id_caso", "id_subcaso", "bloque_director", "variable", "estado",
             "valor_fijo", "min", "max", "n_valores", "igual_al_profesor", "unidad",
             "es_oat", "valor_base"]
COLS_OAT = ["id_subcaso", "variable_movida", "variable", "estado", "valor_fijo",
            "min", "max", "n_valores"]
TOL = 1e-6
def _valores(serie, var):
    """Valores no vacios de una entrada: (crudos, clave de distincion)."""
    serie = serie.dropna()
    if var == "motor":
        crudos = [str(v) for v in serie if str(v).strip() != ""]
        return crudos, crudos
    nums = pd.to_numeric(serie, errors="coerce").dropna().tolist()
    return nums, [sig6(v) for v in nums]
def _estado_vals(g, var):
    """(estado, valor_fijo, min, max, n_valores) de una entrada en un grupo."""
    crudos, claves = _valores(g[var], var)
    if not claves:
        return "sin_dato", "", "", "", ""
    if len(set(claves)) == 1:
        return "fijo", crudos[0], "", "", ""
    if var == "motor":
        return "barrido", "", "", "", len(set(claves))
    nums = [float(x) for x in crudos]
    return "barrido", "", min(nums), max(nums), len(set(claves))
def _subcasos_oat(tabla):
    """id_subcaso con la columna 'variable' no vacia (barridos de a una variable)."""
    if "variable" not in tabla.columns:
        return set()
    v = tabla["variable"]
    return set(tabla.loc[v.notna() & (v.astype(str).str.strip() != ""), "id_subcaso"])
def _moda(claves):
    """Valor mas frecuente (empates -> el menor); claves ya en 6 cifras."""
    cuenta = Counter(claves)
    tope = max(cuenta.values())
    return min(k for k, n in cuenta.items() if n == tope)
def _condiciones(tabla):
    oat = _subcasos_oat(tabla)
    filas = []
    for sub, g in tabla.groupby("id_subcaso", sort=False):
        caso, blq = g["id_caso"].iloc[0], g["bloque_director"].iloc[0]
        es_oat = "sí" if sub in oat else "no"
        for var in ENTRADAS:
            est, vf, mn, mx, nv = _estado_vals(g, var)
            claves = _valores(g[var], var)[1]
            base = _moda(claves) if (es_oat == "sí" and var != "motor"
                                     and claves) else ""
            ig = ""
            if est == "fijo" and var in PROFESOR and var != "motor":
                ref = PROFESOR[var]
                ig = "sí" if abs(float(vf) - ref) <= TOL * abs(ref) else "no"
            filas.append([caso, sub, blq, var, est, vf, mn, mx, nv, ig,
                          UNIDAD[var], es_oat, base])
    return pd.DataFrame(filas, columns=COLS_COND)
def _oat(tabla):
    """Una fila por (id_subcaso, variable_movida, variable), con su estado."""
    if "variable" not in tabla.columns:
        return pd.DataFrame(columns=COLS_OAT)
    v = tabla["variable"]
    oat = tabla[v.notna() & (v.astype(str).str.strip() != "")]
    filas = []
    for (sub, vm), g in oat.groupby(["id_subcaso", "variable"], sort=False):
        for var in ENTRADAS:
            filas.append([sub, vm, var] + list(_estado_vals(g, var)))
    return pd.DataFrame(filas, columns=COLS_OAT)
def _firma(g_sub):
    """Firma de un subcaso: fijos ordenados + lista de barridos."""
    fijos, barr = [], []
    for _, r in g_sub.iterrows():
        if r["estado"] == "fijo":
            fijos.append(f"{r['variable']}={fmtg(r['valor_fijo'])}")
        elif r["estado"] == "barrido":
            if pd.isna(r["min"]) or str(r["min"]) == "":
                barr.append(f"{r['variable']} n={r['n_valores']}")
            else:
                barr.append(f"{r['variable']} [{fmtg(r['min'])}, {fmtg(r['max'])}]"
                            f" n={r['n_valores']}")
    return ("fijos: " + ("; ".join(fijos) if fijos else "ninguno")
            + " | barridos: " + ("; ".join(barr) if barr else "ninguno"))
def _sub_bloque(c_blq, subs, var):
    """(tipos, valores, barridos) de una variable; la base OAT cuenta como fija."""
    cv = c_blq[c_blq["variable"] == var].set_index("id_subcaso")
    tipos, vals, barr = {}, {}, {}
    for s in subs:
        r = cv.loc[s]
        if r["estado"] == "fijo":
            tipos[s] = "fijo"
            vals[s] = str(r["valor_fijo"]) if var == "motor" else sig6(r["valor_fijo"])
        elif r["estado"] == "barrido" and r.get("es_oat") == "sí" and not vacio(
                r.get("valor_base")):
            tipos[s], vals[s] = "fijo", sig6(r["valor_base"])
        elif r["estado"] == "barrido":
            tipos[s] = "barrido"
            barr[s] = (r["min"], r["max"], r["n_valores"])
        else:
            tipos[s] = "sin_dato"
    return tipos, vals, barr
def _desc(tipo, valor, br):
    """Texto del estado de una variable en un subcaso (para 'diferencias')."""
    if tipo == "fijo":
        return "fijo " + (valor if isinstance(valor, str) else fmtg(valor))
    if tipo == "barrido":
        if br is None or br[0] is None or pd.isna(br[0]) or str(br[0]).strip() == "":
            return "barrido" if br is None else f"barrido n={br[2]}"
        return f"barrido [{fmtg(br[0])}, {fmtg(br[1])}] n={br[2]}"
    return "sin_dato"
def _bloques(cond, tabla):
    """'consistente' solo compara fijos (estado/valor); la base OAT por valor_base."""
    filas = []
    for blq in sorted(dict.fromkeys(cond["bloque_director"])):
        c_blq = cond[cond["bloque_director"] == blq]
        subs = list(dict.fromkeys(c_blq["id_subcaso"]))
        firmas = {s: _firma(c_blq[c_blq["id_subcaso"] == s]) for s in subs}
        difs, difs_b = [], []
        for var in ENTRADAS:
            tipos, vals, barr = _sub_bloque(c_blq, subs, var)
            inc = ("fijo" in tipos.values() and "barrido" in tipos.values()
                   or len(set(vals.values())) > 1)
            if inc:
                difs.append(var + ": " + "; ".join(
                    f"{s}={_desc(tipos[s], vals.get(s), barr.get(s))}" for s in subs))
            elif len(barr) == len(subs) and len(set(barr.values())) > 1:
                difs_b.append(var + ": " + "; ".join(
                    f"{s}=[{fmtg(barr[s][0])}, {fmtg(barr[s][1])}] n={barr[s][2]}"
                    for s in subs))
        n_puntos = int(tabla["bloque_director"].eq(blq).sum())
        filas.append([blq, "; ".join(subs), n_puntos, firmas[subs[0]],
                      "no" if difs else "sí", " || ".join(difs), " || ".join(difs_b)])
    return pd.DataFrame(filas, columns=["bloque_director", "id_subcasos", "n_puntos",
                                        "firma", "consistente", "diferencias",
                                        "diferencias_barrido"])
def _conteo(tabla, clave):
    filas = []
    for valor, g in tabla.groupby(clave, sort=False):
        inicio = [valor] if clave == "id_caso" else [g["id_caso"].iloc[0], valor]
        filas.append(inicio + conteos(g))
    cols = (["id_caso"] if clave == "id_caso" else ["id_caso", clave]) + NOMBRES_CONTEO
    return pd.DataFrame(filas, columns=cols)
def _matriz(cond):
    idx = list(dict.fromkeys(cond["id_subcaso"]))
    celda = {}
    for _, r in cond.iterrows():
        if r["estado"] == "fijo":
            txt = (f"=PP" if r["igual_al_profesor"] == "sí"
                   else f"fijo:{fmtg(r['valor_fijo'])}")
        elif r["estado"] == "barrido":
            txt = (f"barrido:n={r['n_valores']}" if pd.isna(r["min"]) or str(r["min"]) == ""
                   else f"barrido:[{fmtg(r['min'])}, {fmtg(r['max'])}]")
        else:
            txt = ""
        celda[(r["id_subcaso"], r["variable"])] = txt
    filas = [{"id_subcaso": s, **{v: celda.get((s, v), "") for v in ENTRADAS}}
             for s in idx]
    return pd.DataFrame(filas, columns=["id_subcaso"] + ENTRADAS)
def main():
    tabla = pd.read_csv(CANONICA)
    os.makedirs(SALIDA, exist_ok=True)
    cond = _condiciones(tabla)
    cond.to_csv(os.path.join(SALIDA, "condiciones_por_subcaso.csv"), index=False)
    oat = _oat(tabla)
    oat.to_csv(os.path.join(SALIDA, "condiciones_oat.csv"), index=False)
    _bloques(cond, tabla).to_csv(os.path.join(SALIDA, "bloques.csv"), index=False)
    _conteo(tabla, "id_caso").to_csv(os.path.join(SALIDA, "casos.csv"), index=False)
    _conteo(tabla, "id_subcaso").to_csv(
        os.path.join(SALIDA, "conteo_por_subcaso.csv"), index=False)
    _matriz(cond).to_csv(os.path.join(SALIDA, "casos_x_variables.csv"), index=False)
    print(f"{SALIDA}: {len(cond)} filas de condiciones "
          f"({tabla['id_subcaso'].nunique()} subcasos x {len(ENTRADAS)} variables); "
          f"condiciones_oat.csv: {len(oat)} filas")
if __name__ == "__main__":
    main()
