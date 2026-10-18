# -*- coding: utf-8 -*-
"""Sens2 - s2_verificar: 9 controles obligatorios de la parte 1. Imprime OK/FALLA por control."""
import os
import sys

from openpyxl import load_workbook

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(RAIZ, "scripts", "sens1"))

from s2_cargar import conclusiones, dataset_dedup  # noqa: E402
from s2_cargar import distancia_resumen, violaciones  # noqa: E402
from x8b_graficos import _cref, _num, _parse, _titulo, _vref, control5, x8b_textos  # noqa: E402

from s2_construir import SALIDA  # noqa: E402

ERRORES = []
ORDEN = ["LEEME", "Conclusion consolidada", "F1 Existencia", "F1 Reglas y zonas grises",
         "F1 Margenes de operacion", "F2 CORREGIBLE vs KALINA", "F2 Distancia y rescate", "F3 Indices globales",
         "F3 Interacciones", "F3 Elasticidades", "F4 Turbina", "F4 Regenerador y condensador",
         "F4 Preseleccion", "F4 Regenerador vs T_fuente", "F5 Superficies de respuesta", "F5 Incertidumbre", "D1 Datos puntos", "D2 Datos fronteras", "D3 Datos zonas grises",
         "D4 Datos distancia", "D5 Datos indices", "D6 Datos equipos"]
PROHIBIDOS = ["confiable", "no citable", "fuera de rango del motor", "sin respaldo", "indicio",
              "extrapol"]


def ok(msg):
    print("OK:", msg)


def fail(msg):
    print("FALLA:", msg)
    ERRORES.append(msg)


try:
    wb = load_workbook(SALIDA)
except Exception as e:
    print("FALLA: 1. no abre:", e)
    sys.exit(1)

# 1. hojas de la parte 1 presentes y en orden
idx = [wb.sheetnames.index(s) if s in wb.sheetnames else -1 for s in ORDEN]
if any(i < 0 for i in idx):
    fail("1. faltan hojas: %s" % [s for s, i in zip(ORDEN, idx) if i < 0])
elif idx != sorted(idx):
    fail("1. hojas fuera de orden: %s" % wb.sheetnames)
else:
    ok("1. las 10 hojas de la parte 1 existen y en orden")

# 2 y 3. graficos: series con >= 2 valores numericos y tablas de grafico sin celdas vacias
n_graf = 0
for s in wb.sheetnames:
    for ch in wb[s]._charts:
        n_graf += 1
        tit = _titulo(ch)
        largos = []
        for k, se in enumerate(ch.series):
            ref = _vref(se)
            if ref is None:
                fail("2. %s [%s]: serie %d sin referencia de valores" % (s, tit, k))
                continue
            _, c1, r1, c2, r2 = _parse(ref)
            vals = [wb[s].cell(rr, cc).value for rr in range(r1, r2 + 1) for cc in range(c1, c2 + 1)]
            if sum(1 for v in vals if _num(v)) < 2:
                fail("2. %s [%s]: serie %d con menos de 2 valores numericos" % (s, tit, k))
            if any(v is None or v == "" for v in vals):
                fail("3. %s [%s]: serie %d con celdas vacias" % (s, tit, k))
            largos.append(r2 - r1 + 1)
            cref = _cref(se)
            if cref is not None:
                _, cc1, cr1, cc2, cr2 = _parse(cref)
                cat = [wb[s].cell(rr, cc).value for rr in range(cr1, cr2 + 1)
                       for cc in range(cc1, cc2 + 1)]
                if any(v is None or v == "" for v in cat):
                    fail("3. %s [%s]: categorias de la serie %d con celdas vacias" % (s, tit, k))
                if len(cat) != (r2 - r1 + 1) * (c2 - c1 + 1):
                    fail("2. %s [%s]: serie %d con %d valores y %d valores de x" % (
                        s, tit, k, (r2 - r1 + 1) * (c2 - c1 + 1), len(cat)))
        if len(set(largos)) > 1 and type(ch).__name__ != "ScatterChart":
            fail("2. %s [%s]: series con distinto numero de puntos %s" % (s, tit, largos))
if n_graf == 0:
    fail("2. el libro no tiene ningun grafico")
else:
    ok("2. %d graficos, cada uno con >= 1 serie de >= 2 valores numericos" % n_graf)
    ok("3. ninguna celda de las tablas de grafico esta vacia")

# 4. graficos sin solapes entre si ni con celdas con datos
control5(wb, ok, fail)

# 5. sin paneles inmovilizados
malos = [s for s in wb.sheetnames if wb[s].freeze_panes]
if malos:
    fail("5. paneles inmovilizados en %s" % malos)
else:
    ok("5. ninguna hoja tiene paneles inmovilizados")

# 6. terminologia prohibida
malos = []
for s in wb.sheetnames:
    for row in wb[s].iter_rows():
        for c in row:
            if isinstance(c.value, str) and any(p in c.value.lower() for p in PROHIBIDOS):
                malos.append((s, c.coordinate, c.value[:40]))
    for ch in wb[s]._charts:
        for t in x8b_textos(ch):
            if any(p in str(t).lower() for p in PROHIBIDOS):
                malos.append((s, "grafico", str(t)[:40]))
if malos:
    fail("6. %d textos con palabras prohibidas: %s" % (len(malos), malos[:8]))
else:
    ok("6. ningun texto con palabras prohibidas")

# 7. cifras del BLUF contra los CSV
d = dataset_dedup()
v = violaciones()
u = distancia_resumen()
n = len(d)
pct = round(100.0 * int(d["kalina"].sum()) / n, 1)
_k = d[d["clasificacion"] == "KALINA"]
eta_in = round(float(_k[_k["fuera_rango"] == False]["eta_pct"].max()), 2)  # noqa: E712
eta_out = round(float(_k[_k["fuera_rango"] == True]["eta_pct"].max()), 2)  # noqa: E712
_m1 = conclusiones()
_m1 = _m1[_m1["id"] == "M1"].iloc[0]["afirmacion"]
if not ("%.2f" % eta_out in _m1 and "%.2f" % eta_in in _m1):
    fail("7. la eta maxima del BLUF (%s / %s) no aparece en la conclusion M1" % (eta_in, eta_out))
else:
    ok("7b. la eta maxima del BLUF coincide con la conclusion M1 (%s / %s)" % (eta_in, eta_out))
sel = v[(v["seccion"] == "dominante") & (v["centro"] == "todos") & (v["clave"] == "viol_O2")]
pct_o2 = round(100.0 * float(sel.iloc[0]["fraccion"]), 1)
uu = u[(u["seccion"] == "univariado") & (u["centro"] == "todos")]
b = uu.loc[uu["valor"].idxmax()]
esperado = {
    "n de puntos (sin duplicados)": n,
    "% KALINA (total)": pct,
    "eta maxima dentro / fuera del rango experimental (%)": "%s / %s" % (eta_in, eta_out),
    "% de CORREGIBLE por cavitacion (viol_O2 dominante)": pct_o2,
    "variable que mas rescata": "%s (%s %%)" % (b["clave"], round(100.0 * float(b["valor"]), 1)),
}
ws = wb["Conclusion consolidada"]
hallado = {}
for row in ws.iter_rows(max_col=3):
    et = row[0].value
    if isinstance(et, str) and et in esperado:
        hallado[et] = row[1].value
for et, val in esperado.items():
    if et not in hallado:
        fail("7. no se hallo la cifra del BLUF: %s" % et)
    elif str(hallado[et]) != str(val):
        fail("7. BLUF '%s': libro %s != CSV %s" % (et, hallado[et], val))
if all(et in hallado and str(hallado[et]) == str(val) for et, val in esperado.items()):
    ok("7. las 5 cifras del BLUF coinciden con los CSV")

# 8. todas las conclusiones presentes y sin celdas vacias
concl = conclusiones()
ws = wb["Conclusion consolidada"]
filas_id = {}
for row in ws.iter_rows(max_col=7):
    if isinstance(row[1].value, str) and row[1].value in ("A", "B", "C"):
        if isinstance(row[0].value, str):
            filas_id[row[0].value] = row
faltan = [i for i in concl["id"] if i not in filas_id]
vacias = [i for i in concl["id"] if i in filas_id and any(
    c.value is None or c.value == "" for c in filas_id[i][:7])]
if faltan or vacias or len(filas_id) != len(concl):
    fail("8. conclusiones: faltan %s; con celdas vacias %s; halladas %d de %d" % (
        faltan, vacias, len(filas_id), len(concl)))
else:
    ok("8. las %d conclusiones estan y sin celdas vacias" % len(concl))

# 9. filas de D1 Datos puntos = n del CSV
ws = wb["D1 Datos puntos"]
marca = ws.max_row + 1
for i in range(4, ws.max_row + 1):
    v0 = ws.cell(i, 1).value
    if isinstance(v0, str) and "Descripci" in v0:
        marca = i
        break
filas = 0
for i in range(4, marca):
    if any(ws.cell(i, j).value is not None and ws.cell(i, j).value != ""
           for j in range(1, len(ws[3]) + 1)):
        filas += 1
real = len(dataset_dedup())
if filas != real:
    fail("9. D1 Datos puntos: %d filas vs %d del CSV" % (filas, real))
else:
    ok("9. D1 Datos puntos tiene %d filas como el CSV" % real)

# 10-15. controles de la parte 2
import re  # noqa: E402
import pandas as pd  # noqa: E402
from s2_cargar import envolventes, indices, ranking  # noqa: E402

n_graf = sum(len(w._charts) for w in wb.worksheets)
if n_graf < 40:
    fail("10. solo %d graficos (minimo 40)" % n_graf)
else:
    ok("10. %d graficos en total (minimo 40)" % n_graf)

ws = wb["F3 Indices globales"]
tablas = 0
mal = []
for i in range(1, ws.max_row + 1):
    if ws.cell(i, 1).value == "Variable" and ws.cell(i, 2).value == "Rango medio":
        j, reales = i + 1, 0
        while ws.cell(j, 1).value not in (None, "") and not str(ws.cell(j, 1).value).startswith("Fuente"):
            if not str(ws.cell(j, 1).value).startswith("mejor dummy"):
                reales += 1
            j += 1
        tablas += 1
        if reales != 9:
            mal.append((i, reales))
if tablas != 16 or mal:
    fail("11. tablas de ranking: %d (esperadas 16), con distinto de 9 variables: %s" % (tablas, mal))
else:
    ok("11. las 16 tablas de ranking tienen las 9 variables")

env = envolventes()
env = env[env["centro"] == "todos"]
hallado, esperado = {}, {}
ws = wb["F4 Preseleccion"]
for i in range(1, ws.max_row + 1):
    hallado[(ws.cell(i, 1).value, ws.cell(i, 2).value)] = (ws.cell(i, 3).value, ws.cell(i, 4).value)
casos = [("Turbina", "r_P (-)", "rp"), ("Turbina", "dh_turb (kJ/kg)", "dh_turb"),
         ("Regenerador", "UA regenerador (kW/K por kg/s)", "UA_reg"),
         ("Condensador", "Q_out (kW por kg/s)", "Qout_mb"), ("HRVG", "Q_i (kW por kg/s)", "Qi_mb"),
         ("Bomba", "W_p/W_t (-)", "Wp_Wt")]
fallas12 = []
for eq, un, q in casos:
    a = env[(env["cantidad"] == q) & (env["conjunto"] == "KALINA (total)")].iloc[0]
    esp = "%s a %s" % (round(float(a["p5"]), 3), round(float(a["p95"]), 3))
    if hallado.get((eq, un), (None,))[0] != esp:
        fallas12.append((eq, un, hallado.get((eq, un)), esp))
if fallas12:
    fail("12. F4 Preseleccion no coincide con p4_envolventes.csv: %s" % fallas12)
else:
    ok("12. 6 cifras de F4 Preseleccion coinciden con p4_envolventes.csv")
r_t = hallado.get(("Turbina", "r_P (-)"), (None,))[0]
if r_t != "1.698 a 5.508":
    fail("12b. r_P de la turbina %s != 1.698 a 5.508 (valor auditado)" % r_t)
else:
    ok("12b. r_P de la turbina 1.698 a 5.508, igual que la auditoria independiente")

ws = wb["D5 Datos indices"]
n5 = sum(1 for i in range(4, ws.max_row + 1) if ws.cell(i, 1).value not in (None, "")
         and not str(ws.cell(i, 1).value).startswith(("Fuente", "Una fila", "Incluye", "Descripci")))
if n5 != len(indices()):
    fail("13. D5 tiene %d filas vs %d de p3_indices.csv" % (n5, len(indices())))
else:
    ok("13. D5 Datos indices tiene %d filas como p3_indices.csv" % n5)

fallas14 = []
for nom in ("LEEME", "F1 Existencia", "F1 Reglas y zonas grises", "F2 CORREGIBLE vs KALINA",
            "F2 Distancia y rescate", "F3 Indices globales", "F3 Interacciones", "F3 Elasticidades",
            "F4 Turbina", "F4 Regenerador y condensador", "F1 Margenes de operacion",
            "F4 Regenerador vs T_fuente", "F5 Superficies de respuesta", "F5 Incertidumbre"):
    txt = " ".join(str(c.value) for row in wb[nom].iter_rows(max_row=40) for c in row if c.value is not None)
    if "Base" not in txt:
        fallas14.append(nom)
if fallas14:
    fail("14. sin nota de base: %s" % fallas14)
else:
    ok("14. la nota de base aparece en LEEME y en las hojas F1 a F4")

# 15. propagacion de incertidumbre: P(KALINA) y eta de la hoja contra las filas crudas
import pandas as pd  # noqa: E402,F811
_d = pd.read_csv(os.path.join(RAIZ, "resultados", "2026-10-17_sens2_U1", "u1_filas.csv"))
_k = _d[_d["clasificacion"] == "KALINA"]
ws = wb["F5 Incertidumbre"]
_hall = {}
for row in ws.iter_rows(max_col=7, values_only=True):
    if row[0] in ("U1A", "U1B") and row[1] in ("C1", "C2", "C3", "C4") and isinstance(row[2], int):
        _hall.setdefault((row[0], row[1]), (row[2], row[3], row[4]))
_mal = []
for (e, c), (n_, k_, p_) in _hall.items():
    gg = _d[(_d["barrido"] == e) & (_d["centro"] == c)]
    kk = int((gg["clasificacion"] == "KALINA").sum())
    if (n_, k_) != (len(gg), kk) or abs(p_ - round(kk / len(gg), 3)) > 1e-9:
        _mal.append((e, c, n_, k_, p_, len(gg), kk))
if len(_hall) != 8 or _mal:
    fail("15. F5 Incertidumbre no coincide con u1_filas.csv: %s (celdas halladas %d)" % (_mal, len(_hall)))
else:
    ok("15. F5 Incertidumbre: 8 celdas de P(KALINA) coinciden con las %d filas de u1_filas.csv" % len(_d))
if int(_d["convergio"].astype(str).str.lower().eq("false").sum()) > 0.05 * len(_d):
    fail("15b. mas del 5 % de los puntos de U1 no convergio")
else:
    ok("15b. puntos sin convergencia en U1: %d de %d" % (int(_d["convergio"].astype(str).str.lower().eq("false").sum()), len(_d)))
_t = ws.cell(1, 1).value

if ERRORES:
    print("== FIN FALLA ==")
    for e in ERRORES:
        print(e)
    sys.exit(1)
print("== FIN OK ==")
sys.exit(0)
