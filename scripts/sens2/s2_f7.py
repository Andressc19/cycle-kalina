# -*- coding: utf-8 -*-
"""Sens2 - s2_f7: hoja `F7 Rigor estadistico` (NO_CONVERGIO, cuartiles, pareado, envolventes,
fronteras con intervalo, validacion cruzada de las superficies y potencia entre lotes)."""
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

R = os.path.join(RAIZ, "resultados", "2026-10-18_sens2_F1")
CORTO = {"C1 Husavik": "C1", "C2 ancla A*": "C2", "C3 caliente 150 C": "C3", "C4 frio 110 C": "C4"}
AMB = ["todos", "C1 Husavik", "C2 ancla A*", "C3 caliente 150 C", "C4 frio 110 C"]
VARS = ["T_sumidero", "P_baja", "x_b", "eps_cond"]


def _l(nombre):
    return pd.read_csv(os.path.join(R, nombre))


def _bl(bloque):
    return bloque.split()[1]


def _txt(v):
    return "sin barrido" if (v is None or (isinstance(v, float) and v != v)) else v


def _bloque_firmado(ws, fila, *, titulo, encabezados, filas, x, y, nota_txt, n_series=None, errores=None, ancho=18.0):
    """Como `bloque`, pero con barras TODAS negativas: replica con `escala(desde_cero=False)`.

    `x5_graficos._barras` fija `desde_cero=True` y con una serie negativa `escala` falla.
    """
    from openpyxl.chart import BarChart, Reference
    from openpyxl.chart.series import SeriesLabel
    from a2_graf_estilo import escala
    from x2_formato import encabezado, fila_datos
    from x5_graficos import COLORES, COL_GRAF, FILAS_GRAF, _acabado, _barras_error, celda_grafico
    encabezado(ws, fila, list(encabezados))
    for i, f_ in enumerate(filas):
        fila_datos(ws, fila + 1 + i, list(f_))
    ultima = fila + len(filas)
    ch = BarChart()
    ch.type, ch.title, ch.style = "col", titulo, 10
    ch.x_axis.title, ch.y_axis.title = x, y
    for k in range(n_series if n_series is not None else len(encabezados) - 1):
        col = 2 + k
        ch.add_data(Reference(ws, min_col=col, min_row=fila + 1, max_col=col, max_row=ultima), titles_from_data=False)
        ser = ch.series[-1]
        c = COLORES[k % len(COLORES)]
        ser.graphicalProperties.solidFill = c
        ser.graphicalProperties.line.solidFill = c
        ser.invertIfNegative = False
        ser.tx = SeriesLabel(v=encabezados[k + 1])
        if errores and k in errores:
            cm, cn = errores[k]
            _barras_error(ws, ser, {"mas": (cm + 1, fila + 1, cm + 1, ultima), "menos": (cn + 1, fila + 1, cn + 1, ultima)})
    ch.set_categories(Reference(ws, min_col=1, min_row=fila + 1, max_col=1, max_row=ultima))
    escala(ch.y_axis, [v for f_ in filas for v in f_[1:] if v is not None], desde_cero=False)
    ch.legend.position = "b"
    _acabado(ch, {"ancho": ancho, "alto": 8.0, "series": ch.series, "apiladas": False})
    ws.add_chart(ch, celda_grafico(ws.title, fila, COL_GRAF))
    fila_nota = max(ultima + 2, fila + FILAS_GRAF)
    nota(ws, fila_nota, nota_txt)
    return fila_nota + 2


def hoja_f7_rigor(wb, datos):  # noqa: ARG001
    ws = wb.create_sheet("F7 Rigor estadistico")
    nc, cu = _l("p6_nc_fraccion.csv"), _l("p6_nc_cuartiles.csv")
    t3, pa = _l("p6_nc_top3.csv"), _l("p6_pareado_dist.csv")
    eq, fr = _l("p6_equipos_diseno.csv"), _l("p6_fronteras_ic.csv")
    su, po = _l("p6_superficies_cv.csv"), _l("p6_potencia_u1.csv")
    f = titulo(ws, 1, "F7 Rigor estadistico de la campana Sens2", ancho=10)
    f = condiciones(ws, f, [
        "Base: %d puntos ya corridos que forman los estudios de la campana Sens2 (resultados/2026-10-18_sens2_F1; p6_*.csv)." % int(nc["n"].sum()),
        "Clases por punto: KALINA (total), CORREGIBLE, NO_CONVERGIO e INVIABLE. El rango experimental separa el liquido a mas de 420 K "
        "(dentro) del resto (fuera del rango experimental).",
        "Intervalos de confianza al 95 % calculados en los CSV de origen; aqui solo se tabulan y se dibujan.",
        "Sin corridas nuevas del motor: ninguna cifra de esta hoja se recalcula ni se escribe a mano."])
    f = subtitulo(ws, f, "1. NO_CONVERGIO por estudio")
    g1 = nc.groupby("estudio", as_index=False).agg(n=("n", "sum"), nc=("nc", "sum")).sort_values("estudio")
    g1["frac"] = 100.0 * g1["nc"] / g1["n"]
    fil = [["E%d" % int(x["estudio"]), int(x["n"]), int(x["nc"]), numero(x["frac"], 1)] for _, x in g1.iterrows()]
    _, f, _ = tabla(ws, f, ["Estudio", "Puntos", "NO_CONVERGIO", "NO_CONVERGIO (%)"], fil, anchos=[10, 10, 14, 18])
    f += 1
    emax = int(g1.loc[g1["frac"].idxmax(), "estudio"])
    f = bloque(ws, f, titulo="Fraccion de NO_CONVERGIO por estudio",
               encabezados=["Estudio", "NO_CONVERGIO (%)"],
               filas=[["E%d" % int(x["estudio"]), numero(x["frac"], 1)] for _, x in g1.iterrows()],
               x="Estudio", y="NO_CONVERGIO (%)",
               nota_txt="Fuente: p6_nc_fraccion.csv. Suma de los centros de cada estudio; E%d tiene la mayor fraccion." % emax)
    f = subtitulo(ws, f, "2. Clase por cuartil de T_fuente")
    r2 = []
    for _, x in cu.iterrows():
        r2.append([_bl(x["bloque"]), "Q%d" % int(x["cuartil_T_fuente"]), numero(x["T_min"], 1), numero(x["T_max"], 1),
                   int(x["n"]), int(x["KALINA"]), int(x["CORREGIBLE"]), int(x["INVIABLE"]), int(x["NO_CONVERGIO"]),
                   numero(x["p_kalina_nc_cero"], 3), numero(x["p_nc"], 3), numero(x["p_kalina_si_convergio"], 3),
                   numero(x["ic_lo"], 3), numero(x["ic_hi"], 3)])
    _, f, _ = tabla(ws, f, ["Bloque", "Cuartil", "T min (K)", "T max (K)", "Puntos", "KALINA", "CORREGIBLE", "INVIABLE",
                            "NO_CONVERGIO", "P(KALINA), NC no KALINA", "P(NO_CONVERGIO)", "P(KALINA) si convergio",
                            "IC bajo", "IC alto"], r2, anchos=[8, 8, 10, 10, 8, 8, 12, 10, 14, 20, 15, 20, 10, 10])
    f += 1
    piv = [["%s Q%d" % (_bl(x["bloque"]), int(x["cuartil_T_fuente"])), numero(x["p_kalina_nc_cero"], 3),
            numero(x["p_kalina_si_convergio"], 3), numero(x["ic_hi"] - x["p_kalina_si_convergio"], 3),
            numero(x["p_kalina_si_convergio"] - x["ic_lo"], 3)] for _, x in cu.iterrows()]
    f = bloque(ws, f, titulo="P(KALINA) por cuartil de T_fuente: con NO_CONVERGIO como no KALINA y si convergio (barras: IC 95 %)",
               encabezados=["Cuartil", "P(KALINA), NC = no KALINA", "P(KALINA) si convergio", "IC alto - P", "P - IC bajo"],
               filas=piv, x="Cuartil de T_fuente", y="Probabilidad (-)", n_series=2, errores={1: (3, 4)}, ancho=20.0,
               nota_txt="Fuente: p6_nc_cuartiles.csv. La primera serie cuenta los NO_CONVERGIO como no KALINA; la segunda los excluye. "
                        "Las barras de error son el IC al 95 % de la segunda serie (columnas auxiliares a la derecha).")
    f = subtitulo(ws, f, "3. Estabilidad de los tres primeros conductores de NO_CONVERGIO")
    _, f, _ = tabla(ws, f, ["Bloque", "Top 3 con NC como no KALINA", "Top 3 sin NC", "Top 3 con NC como KALINA",
                            "Igual sin NC", "Igual con NC como KALINA"],
                    [[_bl(x["bloque"]), x["top3_nc_como_no_kalina"], x["top3_sin_nc"], x["top3_nc_como_kalina"],
                      x["igual_sin_nc"], x["igual_nc_como_kalina"]] for _, x in t3.iterrows()],
                    anchos=[8, 32, 32, 32, 12, 20])
    f += 1
    ns = int((t3["igual_sin_nc"] == "si").sum())
    nk = int((t3["igual_nc_como_kalina"] == "si").sum())
    f = nota(ws, f, "Fuente: p6_nc_top3.csv. En lenguaje llano: de los %d bloques, en %d el ranking de las tres variables casi no cambia "
                    "al quitar los NO_CONVERGIO y en %d se mantiene al contarlos como KALINA. Donde dice 'no', lo que pesa mas depende de "
                    "cuantas corridas no convergen y no de una unica fisica." % (len(t3), ns, nk))
    f = subtitulo(ws, f, "4. Comparacion pareada de eta por tramo de distancia")
    pq = pa[(pa["variante"] == "mismo_centro") & (pa["grupo"] == "todos") & (pa["calculo"].str.startswith("tramo"))]
    _, f, _ = tabla(ws, f, ["Variante", "Grupo", "Calculo", "Puntos", "L1 min", "L1 max", "Estimador (pp)", "IC bajo",
                            "IC alto", "Pendiente"],
                    [[x["variante"], x["grupo"], x["calculo"], int(x["n"]), numero(x["l1_min"], 2), numero(x["l1_max"], 2),
                      numero(x["estimador"], 3), numero(x["ic_lo"], 3), numero(x["ic_hi"], 3), numero(x["pendiente"], 3)]
                     for _, x in pq.iterrows()], anchos=[14, 8, 16, 8, 8, 8, 14, 10, 10, 10])
    f += 1
    fp = [[x["calculo"], numero(x["estimador"], 3), numero(x["ic_hi"] - x["estimador"], 3),
           numero(x["estimador"] - x["ic_lo"], 3)] for _, x in pq.iterrows()]
    f = _bloque_firmado(ws, f, titulo="Diferencia pareada de eta (mediana, puntos porcentuales) por tramo de distancia L1 (barras: IC 95 %)",
                        encabezados=["Tramo", "Estimador (pp)", "IC alto - estimador", "Estimador - IC bajo"], filas=fp,
                        x="Tramo de distancia L1", y="Diferencia de eta (pp)", n_series=1, errores={0: (2, 3)}, ancho=20.0,
                        nota_txt="Fuente: p6_pareado_dist.csv. El vecino cercano (L1 0.0 a 0.2) da la cifra defendible; las barras de error son "
                                 "el IC al 95 % (columnas auxiliares). El ajuste lineal sobre toda la distancia es inestable. Barras con eje que "
                                 "admite valores negativos (ver `_bloque_firmado`).")
    pend = pa[(pa["variante"] == "mismo_centro") & (pa["grupo"] == "todos") & (pa["calculo"] == "ajuste")]["pendiente"].iloc[0]
    f = nota(ws, f, "La pendiente del ajuste lineal (todos los tramos juntos) es %.3f pp por unidad de L1: al mezclar tramos de densidad "
                    "distinta no describe un efecto unico. La lectura defendible es la del tramo del vecino cercano." % pend)
    f = subtitulo(ws, f, "5. Envolventes de equipos segun el diseno")
    fe = [[(a if a == "todos" else CORTO[a]), int((eq[eq["ambito"] == a]["sensible"] == "si").sum()), len(eq[eq["ambito"] == a])]
          for a in AMB]
    _, f, _ = tabla(ws, f, ["Ambito", "Cantidades sensibles", "Cantidades totales"], fe, anchos=[16, 20, 20])
    f += 1
    f = bloque(ws, f, titulo="Numero de cantidades de equipo sensibles al diseno, por ambito",
               encabezados=["Ambito", "Cantidades sensibles"], filas=[[r[0], r[1]] for r in fe], x="Ambito",
               y="Cantidades sensibles",
               nota_txt="Fuente: p6_equipos_diseno.csv. `sensible` marca las cantidades cuya envolvente cambia al pasar del conjunto completo "
                        "a solo LHS y a peso igual.")
    f = subtitulo(ws, f, "6. Fronteras de la regresion logistica con intervalo")
    fq = fr[(fr["variante"] == "sin_nc") & (fr["calidad"] == "aceptable") & (fr["variable"].isin(VARS))]
    _, f, _ = tabla(ws, f, ["Bloque", "Variable", "Frontera", "IC bajo", "IC alto", "Frontera del barrido",
                            "Barrido dentro del IC"],
                    [[_bl(x["bloque"]), x["variable"], numero(x["x_frontera"], 4), numero(x["ic_lo"], 3), numero(x["ic_hi"], 3),
                      _txt(x["frontera_barrido"]), _txt(x["barrido_dentro_ic"])] for _, x in fq.iterrows()],
                    anchos=[8, 14, 12, 10, 10, 20, 18])
    f += 1
    aucs = fq.groupby("bloque", sort=False)["auc"].first()
    f = nota(ws, f, "Fuente: p6_fronteras_ic.csv (variante sin NC, calidad aceptable). AUC por bloque: "
                    + "; ".join("%s %.3f" % (_bl(b), a) for b, a in aucs.items())
                    + ". El AUC mide la separacion entre clases de cada bloque; 0.5 seria azar.")
    f = subtitulo(ws, f, "7. Validacion cruzada de las superficies")
    _, f, _ = tabla(ws, f, ["Par", "Bloque", "Celdas", "R2", "R2 CV", "RMSE", "RMSE CV", "Clase celda peor ajuste",
                            "En borde"],
                    [[x["par"], x["bloque"], int(x["n_celdas"]), numero(x["r2"], 4), numero(x["r2_cv"], 4), numero(x["rmse"], 4),
                      numero(x["rmse_cv"], 4), x["clase_celda_max_ajuste"], x["en_borde"]] for _, x in su.iterrows()],
                    anchos=[8, 18, 8, 10, 10, 10, 10, 22, 10])
    f += 1
    fs = [["%s %s" % (x["par"], CORTO[x["bloque"]]), numero(x["r2"], 4), numero(x["r2_cv"], 4)] for _, x in su.iterrows()]
    f = bloque(ws, f, titulo="Ajuste de las superficies: R2 en la muestra y con validacion cruzada, por malla",
               encabezados=["Malla", "R2 en la muestra", "R2 con validacion cruzada"], filas=fs, x="Malla", y="R2 (-)",
               nota_txt="Fuente: p6_superficies_cv.csv. La caida de R2 al dejar una celda fuera mide cuanto del ajuste es de la propia celda.")
    f = subtitulo(ws, f, "8. Potencia de la propagacion de incertidumbre")
    pe = po[po["tabla"] == "entre_lotes"]
    _, f, _ = tabla(ws, f, ["Centro", "Puntos", "P1", "P2", "Diferencia", "z", "Diferencia minima detectable",
                            "Diferencia minima detectable (peor)"],
                    [[x["centro"], int(x["n"]), numero(x["p1"], 3), numero(x["p2"], 3), numero(x["dif"], 3), numero(x["z"], 3),
                      numero(x["d_min"], 3), numero(x["d_min_peor"], 3)] for _, x in pe.iterrows()],
                    anchos=[10, 8, 10, 10, 12, 10, 28, 30])
    f += 1
    f = nota(ws, f, "Fuente: p6_potencia_u1.csv (filas entre_lotes: U1A frente a U1A2). Con 48 puntos por bloque, la diferencia minima "
                    "detectable en el peor caso es %.3f en la probabilidad de seguir siendo KALINA." % float(pe["d_min_peor"].max()))
    descripcion(ws, f + 1, [
        "Rigor estadistico de la campana Sens2: NO_CONVERGIO por estudio y por cuartil de T_fuente con IC, estabilidad del ranking de "
        "variables, comparacion pareada de eta por distancia, envolventes sensibles al diseno, fronteras de la regresion logistica con IC, "
        "validacion cruzada de las superficies y potencia del analisis entre lotes.",
        "Todas las cifras salen de los CSV ya exportados en resultados/2026-10-18_sens2_F1; la hoja solo ordena, tabula y dibuja."])
    return ws


HOJAS_F7 = [hoja_f7_rigor]
