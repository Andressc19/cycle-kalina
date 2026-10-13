# -*- coding: utf-8 -*-
"""A2 · Hojas "N.M-R Resultados por barrido" del libro Excel (Claude, 2026-10-12).

Pedido del usuario: en cada estudio, la tabla de cada barrido (valor de la variable barrida y su
resultado), visible como en el tablero HTML. Cada fila es un punto calculado; las columnas son
las del HTML (id_punto, clase, variables barridas, η, W_net, ΔP, r_P, fuera de rango) más los
criterios que falla. Si una parte barre una variable a la vez, va un bloque por variable.
"""
import re

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill

from a2_comun import COLOR_CLASE
from a2_excel_hojas import GRIS, TITULO, cuadricula, nombre_hoja
from codigos import ESTUDIO
from codigos_texto import traducir
from nombres import ETIQUETA_CLASE, NOMBRE
from pies import SIMBOLO

VARS = ["T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "eta_t", "eta_p", "eps_hrvg",
        "eps_reg", "eps_cond"]
NOMBRES_EST = {e: n for e, n in ESTUDIO.values()}
FMT = {"T_fuente": "0.0", "T_sumidero": "0.0", "P_alta": "0", "P_baja": "0.0", "x_b": "0.000",
       "eta_t": "0.000", "eta_p": "0.000", "eps_hrvg": "0.000", "eps_reg": "0.000",
       "eps_cond": "0.000", "eta_pct": "0.00", "Wnet": "0.0", "dP": "0", "rP": "0.00"}
AZUL = PatternFill("solid", fgColor="1F4E79")
CLARO = PatternFill("solid", fgColor="BDD7EE")
TIPO = {"malla": "malla", "vecino": "vecino de A*", "ancla": "ancla A*", "biseccion": "bisección"}
NOTA_GRAF = {"3.1": "Los gráficos de este estudio dibujan la malla y los vecinos de A*; el ancla va aparte."}
ANCLAS = {}      # estudio → {"ws", "top", "partes": {parte: fila}, "var": {(parte, variable): fila}}


def _enc(v):
    """Encabezado de una variable: símbolo y unidad ('T_fuente [K]')."""
    u = re.search(r"\[([^\]]*)\]\s*(?:\(.*\))?$", NOMBRE.get(v, ""))
    return f"{SIMBOLO.get(v, v)} [{u.group(1)}]" if u else SIMBOLO.get(v, v)


def _clave_parte(p):
    return [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", str(p))]


def _valor(v):
    return None if (v is None or (isinstance(v, float) and pd.isna(v))) else v


def _bloque(ws, fila, sub, titulo, est=None):
    """Escribe una tabla de puntos (un barrido) desde `fila`; devuelve la fila siguiente."""
    varia = [v for v in VARS if sub[v].round(6).nunique(dropna=True) > 1]
    fijas = [v for v in VARS if v not in varia and sub[v].notna().any()]
    ws.cell(fila, 1, titulo).font = Font(bold=True, size=11)
    ws.cell(fila, 1).fill = CLARO
    fila += 1
    txt = ", ".join(f"{SIMBOLO.get(v, v)} = {float(f'{sub[v].dropna().iloc[0]:.5g}'):g}"
                    for v in fijas)
    ws.cell(fila, 1, f"Fijos en este barrido: {txt}." if txt else "Todas las variables se mueven.")
    ws.cell(fila, 1).font = Font(italic=True, size=9)
    fila += 1
    tipos = sub["tipo_punto"].value_counts() if "tipo_punto" in sub else []
    varios = len(tipos) > 1
    if varios:                       # explica por qué la tabla tiene más puntos que el gráfico
        cuenta = ", ".join(f"{TIPO.get(t, t)} {n}" for t, n in tipos.items())
        extra = " " + NOTA_GRAF[est] if est in NOTA_GRAF else ""
        ws.cell(fila, 1, f"Tipos de punto: {cuenta}.{extra}").font = Font(italic=True, size=9)
        fila += 1
    con_cod = sub["codigos_falla"].notna().any()
    cols = ([("id_punto", "id_punto")] + [(v, _enc(v)) for v in varia] +
            [("clase", "Clase"), ("eta_pct", "η [%]"), ("Wnet", "W_net [kW] (m_b = 1 kg/s)"),
             ("dP", "ΔP [kPa]"), ("rP", "r_P [–]"), ("fuera", "Fuera de rango")] +
            ([("codigos_falla", "Criterios que falla")] if con_cod else []) +
            ([("tipo", "Tipo de punto")] if varios else []))
    for j, (_, t) in enumerate(cols, 1):
        c = ws.cell(fila, j, t); c.font = Font(bold=True); c.fill = GRIS
        c.alignment = Alignment(wrap_text=True, vertical="top")
    ini = fila
    sub = sub.sort_values(varia) if 0 < len(varia) <= 2 else sub
    for _, p in sub.iterrows():
        fila += 1
        for j, (k, _t) in enumerate(cols, 1):
            if k == "clase":
                v = ETIQUETA_CLASE.get(p["clase_trazo"], p["clase_trazo"])
            elif k == "tipo":
                v = TIPO.get(p["tipo_punto"], p["tipo_punto"])
            elif k == "fuera":
                v = "—" if pd.isna(p["fuera_rango"]) else ("sí" if p["fuera_rango"] else "no")
            elif k == "codigos_falla":
                v = traducir(str(p[k])) if pd.notna(p[k]) else None
            elif k in ("eta_pct", "Wnet"):
                # falso convergido: no es un ciclo real, su η y W_net no se muestran
                v = "—" if (p["clase_trazo"] == "N2" or pd.isna(p[k])) else float(p[k])
            else:
                v = _valor(p[k])
            c = ws.cell(fila, j, v)
            if k in FMT and v is not None:
                c.number_format = FMT[k]
            if k == "clase":
                c.fill = PatternFill("solid", fgColor=COLOR_CLASE.get(p["clase_trazo"], "FFFFFF"))
    cuadricula(ws, ini, 1, fila, len(cols))
    return fila + 2, len(cols)


def hoja_estudio(wb, est, d, n_omit=0):
    nombre = nombre_hoja(f"{est}-R Resultados por barrido")
    ws = wb.create_sheet(nombre)
    ws["A1"] = f"Resultados por barrido · Estudio {est} · {NOMBRES_EST.get(est, '')}"
    ws["A1"].font = TITULO
    n = len(d)
    ws["A2"] = (f"Cada fila es un punto calculado (n = {n}); mismas columnas que la tabla del tablero HTML. "
                "Solo se comparan puntos de la misma parte.")
    ws["A4"] = ("«Falso convergido»: el solver dijo que convergió pero no es un ciclo real; su η y W_net "
                "no se muestran («—»), igual que en los gráficos.")
    if n_omit:
        ws["A5"] = (f"{n_omit} puntos omitidos (el modelo no los evaluó) no se muestran ni en la tabla ni "
                    "en los gráficos.")
    ws["A3"] = ("Los gráficos de este estudio están en la hoja de gráficos de su pregunta; "
                "los números que dibuja cada uno, en su hoja «Datos de gráficos».")
    fila, ancho = 6, 8
    anc = ANCLAS[est] = {"ws": ws, "top": 6, "partes": {}, "var": {}, "n_est": n, "n_parte": {},
                         "n_var": {}}
    partes = sorted(d["parte_estudio"].astype(str).unique(), key=_clave_parte)
    for parte in partes:
        dp = d[d["parte_estudio"].astype(str) == parte]
        nom = str(dp["parte_nombre"].dropna().iloc[0]) if dp["parte_nombre"].notna().any() else ""
        cab = ws.cell(fila, 1, traducir(f"Parte {parte} · {nom} · {len(dp)} puntos"))
        cab.font = Font(bold=True, size=12, color="FFFFFF")
        for j in range(1, 12):
            ws.cell(fila, j).fill = AZUL
        anc["partes"][parte] = fila
        anc["n_parte"][parte] = len(dp)
        fila += 2
        ev = dp["variable"]
        if ev.isna().all() and "var1" in dp and not dp.get("var2", pd.Series(dtype=float)).notna().any():
            ev = dp["var1"]                                          # M02R-n1: variable en var1
        if ev.notna().sum() >= len(dp) / 2 and ev.nunique() > 1:     # un barrido por variable
            for v in [v for v in VARS if v in set(ev.dropna())]:
                sv = dp[ev == v]
                anc["var"][(parte, v)] = fila
                anc["n_var"][(parte, v)] = len(sv)
                fila, a = _bloque(ws, fila, sv, f"Barrido de {_enc(v)} · {len(sv)} puntos", est)
                ancho = max(ancho, a)
            resto = dp[ev.isna()]
            if len(resto):
                fila, a = _bloque(ws, fila, resto, f"Puntos de referencia, sin variable barrida · "
                                                   f"{len(resto)} puntos", est)
        else:
            fila, a = _bloque(ws, fila, dp, f"Barrido de la parte {parte} · {len(dp)} puntos", est)
            ancho = max(ancho, a)
    anc["ancho"] = ancho
    ws.column_dimensions["A"].width = 26
    for col in "BCDEFGHIJKL":
        ws.column_dimensions[col].width = 17
    return ws.title, partes


def hojas_resultados(wb, d, cond):
    """Una hoja por estudio 1.1–6.2 (sin el anexo A.1). Devuelve [(hoja, estudio, partes, qué)]."""
    omit = d[d["omitido"].astype(bool)].groupby(d["estudio"].astype(str)).size().to_dict()
    d = d[~d["omitido"].astype(bool)]
    out = []
    claves = sorted({str(e) for e in d["estudio"]}, key=_clave_parte)
    for est in claves:
        h, partes = hoja_estudio(wb, est, d[d["estudio"].astype(str) == est], omit.get(est, 0))
        out.append((h, est, ", ".join(partes),
                    "tabla de cada barrido: valor de la variable y resultado de cada punto"))
    return out
