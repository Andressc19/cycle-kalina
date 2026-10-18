# -*- coding: utf-8 -*-
"""Sens2 F1 - A7k, Parte 2: hoja `F4 Equipos por kW` (todo leido de p6_equipos_kw.csv).

Copia el patron de `s2_f6.py`. Contenido: tabla del ambito `todos` (magnitud, unidad, n, P5,
P50, P95) con nota del ejemplo de 100 kW netos; grafico de barras con las categorias de
ambito (todos, C1..C4) y las series P50 de Qi_kW, Qout_kW y Qreg_kW; grafico de barras con
una serie P50 de m_b_kW; y una tabla de todos los ambitos para UA_kW. El bloque `__main__`
es la prueba de la hoja en un proceso nuevo.
"""
import os
import sys

import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))
sys.path.insert(0, AQUI)
from x2_formato import condiciones, descripcion, nota, subtitulo, tabla, titulo  # noqa: E402
from x5_graficos import bloque  # noqa: E402
from s2_comun import numero  # noqa: E402

F1 = os.path.join(RAIZ, "resultados", "2026-10-18_sens2_F1")
CSV = os.path.join(F1, "p6_equipos_kw.csv")
CORTO = {"C1 Husavik": "C1", "C2 ancla A*": "C2", "C3 caliente 150 C": "C3", "C4 frio 110 C": "C4"}
AMB_GRAF = ["todos", "C1 Husavik", "C2 ancla A*", "C3 caliente 150 C", "C4 frio 110 C"]
AMB_TABLA = AMB_GRAF + ["solo LHS", "10 % de mayor eta"]
SERIES = ["Qi_kW", "Qout_kW", "Qreg_kW"]
NOM = {"Qi_kW": "Q_i (calor de entrada)", "Qout_kW": "Q_out (calor rechazado)",
       "Qreg_kW": "Q_reg (regenerador)", "Wt_kW": "W_t (turbina)", "Wp_kW": "W_p (bomba)",
       "UA_kW": "UA regenerador", "m_b_kW": "m_b (fluido de trabajo)"}
UNIDAD_100 = {"Qi_kW": "kW", "Qout_kW": "kW", "Qreg_kW": "kW", "Wt_kW": "kW",
              "Wp_kW": "kW", "UA_kW": "kW/K", "m_b_kW": "kg/s"}
PROHIBIDAS = ["confiable", "citable", "fuera de rango del motor", "indicio", "extrapol",
              "sin respaldo"]


def _l():
    return pd.read_csv(CSV)


def _etq(a):
    return CORTO.get(a, a)


def _fila(t, ambito, mag):
    return t[(t["ambito"] == ambito) & (t["magnitud"] == mag)].iloc[0]


def _ejemplo(todos):
    """Texto del ejemplo de 100 kW netos (magnitudes del ambito `todos` por 100)."""
    partes = []
    for _, x in todos.iterrows():
        m = x["magnitud"]
        partes.append("%s P5 %s, P50 %s, P95 %s (%s)" % (
            NOM[m], numero(100.0 * x["p5"], 2), numero(100.0 * x["p50"], 2),
            numero(100.0 * x["p95"], 2), UNIDAD_100[m]))
    return "Ejemplo para 100 kW netos: " + "; ".join(partes) + "."


def hoja_f4_kw(wb, datos):
    ws = wb.create_sheet("F4 Equipos por kW")
    t = _l()
    todos = t[t["ambito"] == "todos"]
    f = titulo(ws, 1, "F4 Equipos por kW: requisitos por kW neto (sin motor)", ancho=10)
    f = condiciones(ws, f, [
        "Base: %d puntos KALINA (total) con trabajo neto positivo (de p6_equipos_kw.csv)." % int(todos["n"].iloc[0]),
        "Los requisitos del libro estan por kg/s de fluido de trabajo; aqui se dividen por el trabajo neto (kW por kW neto).",
        "Ambitos: todos, los cuatro centros, solo LHS (estudios 3 y 14) y el 10 % de KALINA (total) con mayor eta.",
        "Fuente: resultados/2026-10-18_sens2_F1/p6_equipos_kw.csv."])
    f = subtitulo(ws, f, "1. Ambito todos: P5, P50 y P95 por magnitud")
    filas = [[NOM[x["magnitud"]], x["unidad"], int(x["n"]), numero(x["p5"]), numero(x["p50"]),
              numero(x["p95"])] for _, x in todos.iterrows()]
    _, f, _ = tabla(ws, f, ["Magnitud", "Unidad", "n", "P5", "P50", "P95"], filas,
                    anchos=[24, 18, 8, 12, 12, 12])
    f += 1
    f = nota(ws, f, _ejemplo(todos))
    f = subtitulo(ws, f, "2. Calor de entrada, rechazado y de regenerador (P50) por ambito")
    filas = [[_etq(a)] + [numero(_fila(t, a, m)["p50"]) for m in SERIES] for a in AMB_GRAF]
    f = bloque(ws, f, titulo="P50 de Q_i, Q_out y Q_reg por ambito", encabezados=["Ambito", "Q_i (P50)",
               "Q_out (P50)", "Q_reg (P50)"], filas=filas, x="Ambito", y="kW por kW neto",
               nota_txt="Fuente: p6_equipos_kw.csv. Mismas unidades (kW por kW neto).")
    f = subtitulo(ws, f, "3. Flujo de fluido de trabajo (m_b, P50) por ambito")
    filas = [[_etq(a), numero(_fila(t, a, "m_b_kW")["p50"])] for a in AMB_GRAF]
    f = bloque(ws, f, titulo="m_b (P50) por ambito", encabezados=["Ambito", "m_b (P50)"], filas=filas,
               x="Ambito", y="kg/s por kW neto", nota_txt="Fuente: p6_equipos_kw.csv.")
    f = subtitulo(ws, f, "4. UA del regenerador por ambito")
    filas = []
    for a in AMB_TABLA:
        x = _fila(t, a, "UA_kW")
        filas.append([_etq(a), int(x["n"]), numero(x["p5"]), numero(x["p50"]), numero(x["p95"])])
    _, f, _ = tabla(ws, f, ["Ambito", "n", "P5", "P50", "P95"], filas, anchos=[20, 8, 12, 12, 12])
    f += 1
    descripcion(ws, f, ["Requisitos de equipos por kW neto, obtenidos de las columnas ya calculadas (sin motor).",
                        "Son envolventes de un muestreo numerico, por kg/s de fluido; no son especificaciones de compra."])
    return ws


HOJAS_F4K = [hoja_f4_kw]


def _celdas(ws, ref):
    from openpyxl.utils import range_boundaries
    ref = ref.replace("$", "")
    if "!" in ref:
        ref = ref.split("!", 1)[1]
    c1, r1, c2, r2 = range_boundaries(ref.replace("'", ""))
    return [ws.cell(r, cc).value for r in range(r1, r2 + 1) for cc in range(c1, c2 + 1)]


def _refs(ch):
    out = []
    for ser in ch.series:
        for attr in ("val", "cat"):
            p = getattr(ser, attr, None)
            nr = getattr(p, "numRef", None) if p is not None else None
            if nr is not None and nr.f:
                out.append(nr.f)
    return out


def _prueba():
    from openpyxl import Workbook, load_workbook
    from x5_graficos import dibujar_todos
    ruta = os.path.join(F1, "_prueba_f4k.xlsx")
    wb = Workbook()
    wb.remove(wb.active)
    hoja_f4_kw(wb, {})
    n = dibujar_todos(wb)
    wb.save(ruta)
    wb2 = load_workbook(ruta)
    ws = wb2["F4 Equipos por kW"]
    graficos = list(ws._charts)
    vacias = sum(1 for ch in graficos for ref in _refs(ch) for v in _celdas(ws, ref) if v is None)
    malas = [c[:60] for fila in ws.iter_rows(values_only=True) for c in fila
             if isinstance(c, str) and any(w in c.lower() for w in PROHIBIDAS)]
    print("hoja existe:", ws.title == "F4 Equipos por kW")
    print("graficos registrados:", n, "| graficos en la hoja:", len(graficos))
    print("celdas vacias en las tablas de los graficos:", vacias)
    print("celdas con palabras prohibidas:", len(malas))
    os.remove(ruta)
    print("prueba guardada y borrada:", not os.path.exists(ruta))
    assert len(graficos) >= 2 and vacias == 0 and not malas, (len(graficos), vacias, malas)
    print("PRUEBA OK")


if __name__ == "__main__":
    _prueba()
