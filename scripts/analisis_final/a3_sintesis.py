# -*- coding: utf-8 -*-
"""A3 · Figuras de síntesis FIG-G01, FIG-G02 y FIG-M09-01 (cada barra/fila es un caso;
excepción de la regla 1). Pies con el formato de pies.armar_pie."""
import matplotlib
matplotlib.use("Agg")
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

from estilo import (COLOR_CLASE, ORDEN_CLASE, ETIQUETA_CLASE, aplicar_estilo,
                    recuadro_condiciones)
from a3_comun import cargar, guardar_fig, guardar_clases, titulo_fig, contar_clases
from nombres import NOMBRE, grupo_legible

aplicar_estilo()

PUNTOS = cargar()
ORDEN_CASOS = ["KF-M01", "KF-M02-N1", "KF-M02-N2", "KF-M02R", "KF-M02S", "KF-M03",
               "KF-M04", "KF-M04b", "KF-M04c", "KF-M05", "KF-M05c", "KF-M06",
               "KF-M07", "KF-M09", "KF-M10", "KF-M10b"]
FUENTE = "todos_los_puntos.csv"

# ---------------------------------------------------------------- FIG-G01
def fig_g01():
    df, casos = PUNTOS[PUNTOS["id_caso"] != "KF-M08"].copy(), list(ORDEN_CASOS)
    n_por_clase = {c: [] for c in ORDEN_CLASE}
    omitidos = []
    for c in casos:
        sub = df[df["id_caso"] == c]
        nc = contar_clases(sub)
        for k in ORDEN_CLASE:
            n_por_clase[k].append(nc.get(k, 0))
        omitidos.append(nc.get("OMITIDO", 0))
    total = sum(sum(v) for v in zip(*n_por_clase.values()))

    fig, ax = plt.subplots()
    izq = np.zeros(len(casos))
    for k in ORDEN_CLASE:
        v = np.array(n_por_clase[k])
        ax.barh(range(len(casos)), v, left=izq, height=0.62,
                color=COLOR_CLASE[k], label=f"{ETIQUETA_CLASE[k]} (n = {v.sum()})")
        izq += v
    ax.set_yticks(range(len(casos)))
    ax.set_yticklabels([c[3:] if c.startswith("KF-") else c for c in casos])
    ax.invert_yaxis()
    ax.set_xlabel("n de puntos")
    titulo_fig(fig, "Resultado de cada barrido: puntos por clase",
               "Síntesis: un caso por barra, M01 – M10b (sin KF-M08)")
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=8, frameon=False)
    pie = ("Figura FIG-G01. Resultado de cada barrido: puntos por clase.\n"
           "Caso(s): todos los casos M01–M10b (figura de síntesis: una barra por "
           "caso, rotulada con su id_caso), sin KF-M08.\n"
           "Datos fijos: no aplica (figura de síntesis).\n"
           f"Filtro: todos los puntos menos los de KF-M08.\n"
           f"n = {total}. Fuente: {FUENTE}.")
    guardar_fig(fig, "G", "FIG-G01_resultado_por_barrido", pie)
    guardar_clases("G", "FIG-G01_resultado_por_barrido",
                   {k: sum(n_por_clase[k]) for k in ORDEN_CLASE})
    print(f"FIG-G01: {total} puntos; omitidos por caso: {dict(zip(casos, omitidos))}")

# ---------------------------------------------------------------- FIG-G02
CEL_BARRIDO, CEL_PP, CEL_FIJO, CEL_NADA = 3, 2, 1, 0
COLOR_CELDA = {CEL_BARRIDO: "#90CAF9", CEL_PP: "#E0E0E0", CEL_FIJO: "#FFB74D",  # azul: no se confunde con KALINA
               CEL_NADA: "white"}
VARS_CXV = ["T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", "m_b",
            "eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond",
            "T_amb_diseno", "motor"]
NOMBRE_CORTO = dict(T_fuente="T_fuente", T_sumidero="T_sumidero", P_alta="P_alta",
                    P_baja="P_baja", x_b="x_b", m_b="m_b", eta_t="η_t", eta_p="η_p",
                    eps_hrvg="ε_HRVG", eps_reg="ε_reg", eps_cond="ε_cond",
                    T_amb_diseno="T_amb_diseño", motor="motor")


def _celda(v):
    """(codigo_color, etiqueta) de una celda de casos_x_variables."""
    s = str(v)
    if s.startswith("barrido:"):
        et = s[len("barrido:"):]
        return CEL_BARRIDO, ("n = 2" if et == "n=2" else et)
    if s == "=PP":
        return CEL_PP, "PP"
    if s.startswith("fijo:teqp"):
        return CEL_PP, "teqp"
    if s.startswith("fijo:real"):
        return CEL_FIJO, "real"
    if s.startswith("fijo:"):
        return CEL_FIJO, s[len("fijo:"):]
    return CEL_NADA, ""


def fig_g02():
    cxv = pd.read_csv("analisis_final/00_inventario/casos_x_variables.csv")
    cxv = cxv[~cxv["id_subcaso"].str.startswith("KF-M08")].reset_index(drop=True)
    sub = cxv["id_subcaso"].tolist()
    nrows, ncols = len(sub), len(VARS_CXV)
    codes = np.zeros((nrows, ncols), dtype=int)
    labels = [[""] * ncols for _ in range(nrows)]
    for i, s in enumerate(sub):
        for j, v in enumerate(VARS_CXV):
            codes[i, j], labels[i][j] = _celda(cxv.loc[i, v])
    x = np.arange(ncols + 1)
    y = np.arange(nrows + 1)
    cmap = np.array([COLOR_CELDA[k] for k in (CEL_NADA, CEL_FIJO, CEL_PP,
                                              CEL_BARRIDO)])
    fig, ax = plt.subplots(figsize=(13, 0.24 * nrows + 2.5))
    ax.pcolormesh(x, y, codes.astype(float)[::-1], cmap=matplotlib.colors
                  .ListedColormap(cmap),
                  vmin=0, vmax=len(cmap) - 1)
    for i in range(nrows):
        for j in range(ncols):
            if labels[i][j] and codes[i, j] == CEL_FIJO:   # solo el valor fijo distinto del profesor
                ax.text(j + 0.5, nrows - i - 0.5, labels[i][j], ha="center",
                        va="center", fontsize=6.5, color="#111111")
    ax.set_xticks(np.arange(ncols) + 0.5)
    ax.set_xticklabels([NOMBRE_CORTO[v] for v in VARS_CXV], fontsize=8)
    ax.set_yticks(np.arange(nrows) + 0.5)
    ax.set_yticklabels(sub[::-1], fontsize=7)   # la matriz se dibuja invertida (codes[::-1])
    ax.set_xlim(0, ncols)
    ax.set_ylim(0, nrows)
    ax.set_facecolor("white"); fig._rect = (0, 0.03, 1, 0.95)   # figura alta: menos hueco arriba
    titulo_fig(fig, "Qué variables se movieron y cuáles quedaron fijas en cada barrido",
               "Síntesis: una fila por barrido, sin KF-M08; los rangos están en TAB-G02")
    ax.legend(handles=[Patch(color=COLOR_CELDA[CEL_BARRIDO], label="Barrido"),
                       Patch(color=COLOR_CELDA[CEL_PP],
                             label="Fijo: valor del profesor (PP / teqp)"),
                       Patch(color=COLOR_CELDA[CEL_FIJO],
                             label="Fijo: valor distinto del profesor"),
                       Patch(fc="white", ec="0.6", label="Sin dato en la fuente")],
              loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=4,
              frameon=False, fontsize=8)
    pie = ("Figura FIG-G02. Qué variables se movieron y cuáles quedaron fijas en "
           "cada barrido.\nCaso(s): los barridos de la campaña (sin KF-M08) (figura de síntesis: "
           "una fila por id_subcaso).\n"
           "Datos fijos: celda gris (PP/teqp), naranja (valor fijo distinto del "
           "profesor) o vacía (no aplica).\n"
           "Datos barridos: celdas azules (rango en TAB-G02); antes: celdas con el rango [mín, máx] o 'n = 2'.\n"
           "Filtro: casos_x_variables.csv, una fila por barrido.\n"
           f"n = {nrows} barridos. Fuente: 00_inventario/casos_x_variables.csv.")
    guardar_fig(fig, "G", "FIG-G02_matriz_variables_por_barrido", pie)
    print(f"FIG-G02: {nrows} barridos x {ncols} variables")

# ---------------------------------------------------------------- FIG-M09-01
def fig_m09_01():
    m9 = pd.read_csv("resultados/2026-10-08_final_M9/m9_escalera.csv")
    e = m9[m9["elegido"]]
    n = int(e["n_conservadas"].iloc[-1])
    rondas = sorted(m9["ronda"].unique())
    fig, ax = plt.subplots(figsize=(11, 5.2))
    pos, etiq, x0 = [], [], 0                   # posición acumulada: rondas de distinto tamaño
    for r in rondas:
        fila = m9[m9["ronda"] == r]
        x = np.arange(len(fila)) + x0
        barras = ax.bar(x, fila["n_kalina_confiable"], width=0.7, color="#2E7D32", alpha=0.85)
        for b2, sel in zip(barras, fila["elegido"]):
            if sel:
                b2.set_edgecolor("black")
                b2.set_linewidth(1.8)
        ax.text(x.mean(), max(fila["n_kalina_confiable"]) + 1.2, f"Ronda {r}",
                fontsize=9, ha="center")
        pos += list(x); etiq += [grupo_legible(c) for c in fila["conservados"]]
        if r != rondas[-1]:
            ax.axvline(x[-1] + 1, color="0.8", lw=0.8)
        x0 = x[-1] + 2
    ax.set_xticks(pos)
    ax.set_xticklabels(etiq, fontsize=7.5, rotation=35, ha="right")
    ax.set_ylim(0, m9["n_kalina_confiable"].max() + 3)
    ax.set_ylabel("KALINA confiables")
    ax.set_xlabel("Conjunto de datos del profesor conservados")
    titulo_fig(fig,
               f"Se conservan {n} de los 10 datos de diseño del profesor y sigue "
               "habiendo KALINA",
               "Bloque B13 · KF-M09 (escalera de conservación, R0–R3)")
    ax.legend([plt.Rectangle((0, 0), 1, 1, color="#2E7D32"),
               plt.Rectangle((0, 0), 1, 1, facecolor="none", edgecolor="black",
                             linewidth=1.8)],
              ["conjunto", "elegido de la ronda"], loc="upper right", fontsize=8)
    recuadro_condiciones(ax, "Punto base: PP (datos del profesor)\nCada barra "
                             "conserva el subconjunto de su etiqueta")
    pie = ("Figura FIG-M09-01. Se conservan 8 de los 10 datos de diseño del "
           "profesor y sigue habiendo KALINA.\n"
           "Caso(s): KF-M09 (escalera de conservación; figura de síntesis: una "
           "barra por conjunto conservado). Punto base: PP = datos del enunciado "
           "del profesor (T_fuente 623.15 K, P_alta 3000 kPa, P_baja 400 kPa, "
           "x_b 0.50).\n"
           "Datos fijos: los 10 datos de diseño del profesor; cada barra conserva "
           "el subconjunto que indica su etiqueta.\n"
           "Datos barridos: 100 puntos (ronda 0) o 30 (rondas 1–3) por conjunto.\n"
           "Filtro: KALINA confiables por conjunto conservado; el elegido de cada "
           "ronda se resalta con borde negro.\n"
           f"n = {len(m9)} conjuntos. Fuente: resultados/2026-10-08_final_M9/"
           "m9_escalera.csv.")
    guardar_fig(fig, "M09", "FIG-M09-01_escalera_conservacion", pie)
    print(f"FIG-M09-01: {len(m9)} conjuntos, elegido final = {e['conservados'].iloc[-1]}")


if __name__ == "__main__":
    fig_g01()
    fig_g02()
    fig_m09_01()
    print("a3_sintesis: OK")