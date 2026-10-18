# -*- coding: utf-8 -*-
"""Sens2 - s2_f6: hoja `F6 Respaldo libro viejo` (contraste fuera de muestra con la campaña M1-M10b)."""
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

R1 = os.path.join(RAIZ, "resultados", "2026-10-18_sens2_R1")
CORTO = {"C1 Husavik": "C1", "C2 ancla A*": "C2", "C3 caliente 150 C": "C3", "C4 frio 110 C": "C4"}


def _l(nombre):
    return pd.read_csv(os.path.join(R1, nombre))


def _acuerdo(c):
    """Acuerdo (aciertos / evaluaciones) de las filas con n >= 5, por centro y global."""
    ok = c[c["n"] >= 5]
    out = {k: (g["aciertos"].sum() / g["n"].sum(), int(g["n"].sum())) for k, g in ok.groupby("centro")}
    out["todos"] = (ok["aciertos"].sum() / ok["n"].sum(), int(ok["n"].sum()))
    return out


def hoja_f6_respaldo(wb, datos):
    ws = wb.create_sheet("F6 Respaldo libro viejo")
    cas, rng, v1, v2 = _l("r1_cascada.csv"), _l("r1_rangos_fraccion.csv"), _l("r1_fronteras_contraste.csv"), _l("r2_fronteras_eficiencias.csv")
    vec, cob, fuera, agr = _l("r2_vecinos_resumen.csv"), _l("r1_cobertura.csv"), _l("r1_fuera_de_rango_sens2.csv"), _l("r2_acuerdo_agregado.csv")
    f = titulo(ws, 1, "F6 Respaldo con el libro de la campaña anterior (M1-M10b)", ancho=10)
    f = condiciones(ws, f, [
        "Base: %d puntos del libro viejo (Excel_kalina_final_final_final, hoja Datos) que cumplen el dominio de Sens2 y que Sens2 no tenia." % int(cas["n_unicos"].iloc[-1]),
        "Filtro: sin omitidos, con las 10 variables, piso de O2 igual a T_sumidero (como Sens2), dentro de los rangos de Sens2 y sin repetir entradas.",
        "Cerca de un centro = distancia (norma infinito, 5 variables normalizadas por el rango de Sens2) menor o igual que 0.15.",
        "Uso: contraste fuera de muestra de las conclusiones de Sens2 y busqueda de corridas que Sens2 no tiene. No se mezclan con los 3 663 puntos en los estadisticos.",
        "Fuente: resultados/2026-10-18_sens2_R1 (r1_*.csv y r2_*.csv)."])
    f = subtitulo(ws, f, "1. Que puntos del libro viejo se pueden usar")
    _, f, _ = tabla(ws, f, ["Paso", "Filas", "Entradas unicas", "KALINA unicas"],
                    [[str(x["paso"]), int(x["n_filas"]), int(x["n_unicos"]), int(x["n_kalina"])] for _, x in cas.iterrows()],
                    anchos=[60, 10, 16, 14])
    f += 1
    f = subtitulo(ws, f, "2. Rangos: los KALINA viejos y los rangos KALINA de Sens2")
    t = rng[rng["variable"] == "(las 10 a la vez)"]
    _, f, _ = tabla(ws, f, ["Bloque", "KALINA viejos", "Dentro de las 10 variables", "Fraccion dentro (%)"],
                    [[CORTO[x["centro"]], int(x["n"]), int(x["n_dentro"]), numero(100 * x["fraccion"], 1)] for _, x in t.iterrows()],
                    anchos=[10, 16, 24, 18])
    f += 1
    f = bloque(ws, f, titulo="Fraccion de KALINA viejos dentro de los rangos de Sens2 (10 variables), por bloque",
               encabezados=["Bloque", "Fraccion dentro (%)"],
               filas=[[CORTO[x["centro"]], numero(100 * x["fraccion"], 1)] for _, x in t.iterrows()],
               x="Bloque", y="Fraccion (%)",
               nota_txt="Fuente: r1_rangos_fraccion.csv. C2 domina el total; C1 (7) y C4 (1) tienen muy pocos KALINA: no concluyente.")
    f = subtitulo(ws, f, "3. Aportes: KALINA viejos fuera del rango KALINA de Sens2")
    ag = fuera.groupby(["centro", "variable"]).agg(n=("id_punto", "nunique"), valor_min=("valor", "min"), valor_max=("valor", "max"),
                                                  lim_min=("min_kalina", "first"), lim_max=("max_kalina", "first")).reset_index()
    _, f, _ = tabla(ws, f, ["Bloque", "Variable", "Puntos", "Valor minimo", "Valor maximo", "Limite inferior de Sens2",
                            "Limite superior de Sens2"],
                    [[CORTO[x["centro"]], x["variable"], int(x["n"]), numero(x["valor_min"], 4), numero(x["valor_max"], 4),
                      numero(x["lim_min"], 4), numero(x["lim_max"], 4)] for _, x in ag.iterrows()], anchos=[10, 14, 10, 14, 14, 20, 20])
    f += 1
    f = nota(ws, f, "Los aportes son una extension minima del rango: en C2 la T_fuente baja hasta 3.2 K bajo el minimo y en C3 es un solo valor "
                    "de eps_cond (0.8418) repetido, a 0.008 del minimo. No definen un rango nuevo. La comprobacion solo mira KALINA dentro del minimo-maximo.")
    f = subtitulo(ws, f, "4. Fronteras de una variable sobre los puntos viejos")
    a1, a2 = _acuerdo(v1), _acuerdo(v2)
    u1, u2 = agr.iloc[0], agr.iloc[1]
    r2 = v2[v2["n"] >= 5]
    may = (r2["acuerdo_clase_mayoritaria"].astype(float) * r2["n"]).sum() / r2["n"].sum()
    claves = [k for k in ("C1 Husavik", "C2 ancla A*", "C3 caliente 150 C", "C4 frio 110 C", "todos") if k in a1]

    def nom(k):
        return k if k == "todos" else CORTO[k]
    _, f, _ = tabla(ws, f, ["Bloque", "Evaluaciones (otras variables libres)", "Evaluaciones (eficiencias a +-0.10)"],
                    [[nom(k), a1[k][1], a2[k][1] if k in a2 else 0] for k in claves], anchos=[10, 34, 34])
    f += 1
    f = bloque(ws, f, titulo="Acuerdo de las fronteras de Sens2 con la clase real de los puntos viejos",
               encabezados=["Bloque", "Acuerdo (otras variables libres)", "Acuerdo (eficiencias a +-0.10 del centro)"],
               filas=[[nom(k), numero(a1[k][0], 3), numero(a2[k][0], 3) if k in a2 else 0.0] for k in claves],
               x="Bloque", y="Acuerdo (-)",
               nota_txt="Fuente: r1_fronteras_contraste.csv y r2_fronteras_eficiencias.csv. Filas con n >= 5; cada ventana cuenta dos veces (dos bordes). "
                        "Con las eficiencias cerca del centro, predecir siempre la clase mayoritaria da %.3f." % may)
    f = nota(ws, f, "Contando cada ventana una vez: %d fronteras y %d evaluaciones con acuerdo %.3f (otras variables libres); con eficiencias cerca del "
                    "centro %d fronteras, %d evaluaciones, acuerdo %.3f frente a %.3f de la clase mayoritaria. Las evaluaciones reutilizan puntos y no son "
                    "independientes, y el resultado depende sobre todo de C2 (C3 y C4 tienen n <= 9 con eficiencias fijas)."
                    % (u1["predictores_ventanas_una_vez"], u1["evaluaciones_ventanas_una_vez"], u1["acuerdo_ventanas_una_vez"],
                       u2["predictores_ventanas_una_vez"], u2["evaluaciones_ventanas_una_vez"], u2["acuerdo_ventanas_una_vez"],
                       u2["mayoritaria_ventanas_una_vez"]))
    f = subtitulo(ws, f, "5. Prediccion de la clase con los vecinos de Sens2 (k = 5, 10 variables)")
    sel = ["todos", "cerca (dist <= 0.15)", "vecino cercano (L1 <= P25)", "vecino lejano (L1 > P75)"]
    vs = vec[vec["grupo"].isin(sel)]
    _, f, _ = tabla(ws, f, ["Grupo", "Puntos"], [[x["grupo"], int(x["n"])] for _, x in vs.iterrows()], anchos=[34, 10])
    f += 1
    f = bloque(ws, f, titulo="Exactitud de los vecinos de Sens2 frente a la clase mayoritaria, por tipo de punto viejo",
               encabezados=["Grupo", "Exactitud vecinos", "Exactitud clase mayoritaria", "Precision KALINA", "Exhaustividad KALINA"],
               filas=[[x["grupo"], numero(x["exactitud"], 3), numero(x["exactitud_clase_mayoritaria"], 3), numero(x["precision_kalina"], 3),
                       numero(x["exhaustividad_kalina"], 3)] for _, x in vs.iterrows()],
               x="Grupo", y="Valor (-)",
               nota_txt="Fuente: r2_vecinos_resumen.csv. Los vecinos superan a la clase mayoritaria donde hay un punto de Sens2 cercano (primer cuartil de la "
                        "distancia L1) y la pierden lejos; 11 puntos viejos tienen un vecino a L1 < 0.01, asi que parte del acierto cercano es interpolacion local.")
    f = subtitulo(ws, f, "6. Cobertura: puntos viejos por bloque y distancia")
    c = cob[cob["tipo"] == "conteo"]
    fl = [[CORTO[ce], int(g["n_015"].sum()), int(g["n_025"].sum()), int(g[g["clasificacion"] == "KALINA"]["n_015"].sum()),
           int(g[g["clasificacion"] == "KALINA"]["n_025"].sum())] for ce, g in c.groupby("centro", sort=False)]
    f = bloque(ws, f, titulo="Puntos viejos por bloque a distancia <= 0.15 y <= 0.25 del centro",
               encabezados=["Bloque", "Puntos (<= 0.15)", "Puntos (<= 0.25)", "KALINA (<= 0.15)", "KALINA (<= 0.25)"], filas=fl,
               x="Bloque", y="Puntos", nota_txt="Fuente: r1_cobertura.csv. C4 casi no tiene apoyo en la campaña anterior.")
    descripcion(ws, f + 1, ["Contraste fuera de muestra con la campaña M1-M10b: rangos, fronteras de una variable, vecinos y cobertura.",
                            "Los rangos se respaldan en C2 y no en C3; las fronteras de una variable no se reproducen con claridad cuando las otras cambian."])
    return ws


HOJAS_F6 = [hoja_f6_respaldo]
