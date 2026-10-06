"""Comprobación final de M2 nivel 1 (TASK_CONTEXT, Pasos 6) — escrito con `write`.
Verifica (a) filas/columnas de cada CSV, (b) hojas/filas del xlsx y (c) que cada número
del `REPORTE_M2_N1.md` sale de los CSV. rc=1 si algo falla."""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR), str(_DIR.parent)]

import pandas as pd  # noqa: E402
from openpyxl import load_workbook  # noqa: E402

import m2_nivel1 as m2  # noqa: E402
from comun import PROFESOR  # noqa: E402

OUT = _RAIZ / "resultados" / "2026-10-06_final_M2"
XLSX = _RAIZ / "datos" / "Excel_final_kalina.xlsx"
HOJAS = ("M2_N1_malla", "M2_N1_biseccion", "M2_N1_fronteras", "M2_N1_resumen")
LIBRO = ("M0_protocolo", "M1_profesor_P_alta", "M1_profesor_x_b", "M1_profesor_T_amb",
         "M1_profesor_base", "M1_comparacion", "Resumen") + HOJAS
CLASES = ("KALINA", "CORREGIBLE", "INVIABLE", "NO_CONVERGIO")
FALLOS: list[str] = []


def ck(ok: bool, msg: str, det: str = "") -> bool:
    print(f"OK   {msg}" if ok else f"FALLO {msg} :: {det}")
    if not ok:
        FALLOS.append(f"{msg} :: {det}")
    return bool(ok)


def cuerpo(ws) -> list:
    out = []
    for r in range(2, ws.max_row + 1):
        if ws.cell(r, 1).value in (None, ""):
            break
        out.append([ws.cell(r, j).value for j in range(1, ws.max_column + 1)])
    return out


def s(x) -> str:
    return "" if x is None or (isinstance(x, float) and pd.isna(x)) else str(x)


def num(x):
    return None if x is None or (isinstance(x, float) and pd.isna(x)) else float(x)


def conteos(df) -> list:
    if "clasificacion" in df:
        n, err = df["clasificacion"].value_counts(), int(df["error_inesperado"].notna().sum())
    elif "clase_lado_si" in df:
        n, err = df["clase_lado_si"].value_counts(), 0
    else:
        n, err = {c: int(df["n_" + c.lower()].fillna(0).sum()) for c in CLASES}, 0
    return [int(n.get(c, 0)) for c in CLASES] + [err]


def pares(d: dict) -> list:
    return list(zip(HOJAS, (d["malla"], d["biseccion"], d["fronteras"], d["resumen"])))


def multiset(cad: str) -> frozenset:
    """'C3(10) · N2(13)' -> frozenset de pares (conteo, código); el orden de empates no importa."""
    return frozenset((int(n), k) for c in cad.split(" · ") if c for k, n in [c[:-1].rsplit("(", 1)])


def csvs() -> dict:
    return {k: pd.read_csv(OUT / f"m2n1_{k}.csv", float_precision="round_trip") for k in ("malla", "biseccion", "fronteras", "resumen")}


def parte_a(d: dict) -> None:
    """(a) columnas y número de filas de cada CSV."""
    m, b, f, r = d["malla"], d["biseccion"], d["fronteras"], d["resumen"]
    ck(list(m.columns) == m2.CMALLA and len(m) == 100, "malla: 100 filas x CMALLA", f"filas={len(m)}")
    ck(list(b.columns) == m2.CBISE, "biseccion columnas == CBISE", str(list(b.columns)[:5]))
    ck(list(f.columns) == m2.CFRON and list(r.columns) == m2.CREST and len(r) == 10,
       "fronteras/resumen columnas y 10 filas", f"filas={len(r)}")
    for v in f.variable.unique():
        k = int(f.loc[f.variable == v, "iteraciones"].sum())
        ck(int((b.variable == v).sum()) == k, f"biseccion de {v}: filas == Σ iteraciones ({k})")


def parte_b(d: dict) -> None:
    """(b) `m2n1_resumen.csv` recalculado desde malla + bisección."""
    todo = pd.concat([d["malla"], d["biseccion"]], ignore_index=True)
    for _, r in d["resumen"].iterrows():
        sub = todo[todo.variable == r.variable]
        conv = sub[sub.convergio.fillna(False)]
        kal = sub[sub.clasificacion == "KALINA"]
        a, b, _t = m2.RANGOS[r.variable][1:]
        vm = conv.loc[(conv.valor - PROFESOR[r.variable]).abs().idxmin(), "valor"] if len(conv) else None
        vk = kal.loc[(kal.valor - PROFESOR[r.variable]).abs().idxmin(), "valor"] if len(kal) else None
        cd = sub[sub.D.notna()]
        i = cd.D.idxmin() if len(cd) else None
        cods = Counter(x for t in conv[conv.clasificacion != "KALINA"].codigos_falla.fillna("") for x in str(t).split(",") if x)
        esp = (len(conv), len(kal), *((int((sub.clasificacion == c).sum()) for c in CLASES[1:])),
               num(vm), num(vk), None if vk is None else abs(vk - PROFESOR[r.variable]) / (b - a),
               None if i is None else float(cd.loc[i, "D"]), None if i is None else float(cd.loc[i, "valor"]),
               " · ".join(f"{k}({v})" for k, v in cods.most_common()))
        got = (int(r.n_converge), int(r.n_kalina), int(r.n_corregible), int(r.n_inviable), int(r.n_no_convergio),
               num(r.valor_conv_mas_cercano_prof), num(r.valor_kalina_mas_cercano_prof), num(r.d_normalizada),
               num(r.D_minimo), num(r.valor_D_minimo), s(r.criterios_bloqueantes_frecuentes))
        ck(esp[:10] == got[:10] and multiset(esp[10]) == multiset(got[10]),
           f"resumen recalculado: {r.variable}", f"esperado={esp}\n                 obtenido={got}")


def parte_c(d: dict) -> None:
    """(c) hojas del xlsx, filas de datos y las 4 filas de `Resumen`."""
    wb = load_workbook(XLSX)
    ck(list(wb.sheetnames) == list(LIBRO), "xlsx: hojas en orden", str(wb.sheetnames))
    for nombre, df in pares(d):
        if not ck(nombre in wb.sheetnames, f"{nombre}: existe"):
            continue
        ws = wb[nombre]
        cab = [re.sub(r"\s*\(.+\)$", "", str(ws.cell(1, j).value)) for j in range(1, ws.max_column + 1)]
        filas = cuerpo(ws)
        ck(cab == list(df.columns), f"{nombre}: cabecera == CSV", str(cab[:4]))
        ck(len(filas) == len(df), f"{nombre}: {len(filas)} filas de datos == {len(df)} del CSV")
    m2filas = [f for f in cuerpo(wb["Resumen"]) if str(f[0]).startswith("M2_N1_")]
    ck(len(m2filas) == 4, "Resumen: 4 filas M2_N1_", f"hay {len(m2filas)}")
    for nombre, df in pares(d):
        fila = next((f for f in m2filas if f[0] == nombre), None)
        if fila:
            esp, got = [len(df)] + conteos(df), [int(fila[1])] + [int(x) for x in fila[2:7]]
            ck(esp == got, f"Resumen {nombre}: puntos y conteos == CSV", f"esperado={esp} obtenido={got}")


def parte_d(d: dict) -> None:
    """(d) cada número del reporte, calculado otra vez desde los CSV."""
    todo = pd.concat([d["malla"], d["biseccion"]], ignore_index=True)
    rep = (OUT / "REPORTE_M2_N1.md").read_text(encoding="utf-8")
    res, fron = d["resumen"], d["fronteras"]
    l3 = [l for l in rep.split("## 3.")[1].split("## 4.")[0].splitlines() if l.startswith("| ")][1:]  # 1ª= cabecera; el separador empieza con "|-"
    ck(len(l3) == len(res), f"§3: {len(l3)} filas == resumen ({len(res)})")
    for l, (_, r) in zip(l3, res.iterrows()):
        nv = None if pd.isna(r.n_converge) else int(r.n_converge)
        vk, dm = num(r.valor_kalina_mas_cercano_prof), num(r.D_minimo)
        esp = [r.variable, "sin datos" if nv is None else (f"sí ({nv})" if nv else "no"),
               "sí" if r.n_kalina else "no", "—" if vk is None else f"{vk:g} (d = {r.d_normalizada:.4f})",
               "—" if dm is None else f"{dm:g} en {num(r.valor_D_minimo):g}",
               s(r.criterios_bloqueantes_frecuentes) or "—"]
        got = [c.strip() for c in l.strip().strip("|").split("|")]
        ck(esp == got, f"§3 {r.variable}", f"esperado={esp} obtenido={got}")
    l4 = [l for l in rep.split("## 4.")[1].split("## 5.")[0].splitlines() if l.startswith("| ")][1:]
    ck(len(l4) == len(fron), f"§4: {len(l4)} filas == fronteras ({len(fron)})")
    for l, (_, f) in zip(l4, fron.iterrows()):
        esp = (f"| {f.variable} | {f.tipo} | {f.frontera} | {f.lado_si:g} | {f.lado_no:g} | "
               f"{f.ancho_final:g} | {int(f.iteraciones)} | {f.clase_lado_si} | "
               f"{'—' if pd.isna(f.D_lado_si) else format(f.D_lado_si, 'g')} | {s(f.codigos_falla_lado_si) or '—'} |")
        ck(l.strip() == esp, f"§4 {f.variable} {f.frontera}", f"está: {l.strip()}")
    sec5 = rep.split("## 5.")[1].split("## 6.")[0]
    m = re.search(r"Malla: (\d+) s · Bisección: (\d+) s · Total: (\d+) s", sec5)
    ck(m is not None and abs(int(m.group(3)) - int(m.group(1)) - int(m.group(2))) <= 1,
       "§5: total == malla + bisección", m.group(0) if m else "sin línea")
    ts = sorted(float(x) for x in todo.t_s.dropna() if x)
    esp = (ts[0], ts[len(ts) // 2], ts[-1], sum(ts) / len(ts), float(len(ts)))
    m = re.search(r"mínimo ([\d.]+) s, mediana ([\d.]+) s, máximo ([\d.]+) s, media ([\d.]+) s \((\d+) puntos\)", sec5)
    got = tuple(float(x) for x in m.groups()) if m else ()
    ck(m is not None and all(abs(x - y) <= 0.05 for x, y in zip(esp, got)), "§5: t_s mínimo/mediana/máx/media/n",
       f"esperado={esp} obtenido={got}")
    sec6 = rep.split("## 6.")[1].split("## 7.")[0]
    kals = [r.variable for _, r in res.iterrows() if r.n_kalina]
    convs = [r.variable for _, r in res.iterrows() if r.n_converge]
    if kals:
        sub = res[res.n_kalina > 0]
        rmin = sub.loc[sub.d_normalizada.idxmin()]
        esp = (f"las variables que lo logran son {', '.join(kals)} y el cambio mínimo es "
               f"{rmin.variable} = {rmin.valor_kalina_mas_cercano_prof:g} (d = {rmin.d_normalizada:.4f})")
        ck(esp in sec6, "§6: conclusión con KALINA", esp)
    else:
        cods = Counter(x for t in todo[todo.convergio.fillna(False) & (todo.clasificacion != "KALINA")]
                       .codigos_falla.fillna("") for x in str(t).split(",") if x)
        esp = "ninguna variable sola lo logra; las que al menos hacen converger el ciclo " + \
              ("son " + ", ".join(convs) if convs else "no existen") + \
              f", y el criterio que queda bloqueando es {cods.most_common(1)[0][0] if cods else 'ninguno'}"
        ck(esp in sec6, "§6: conclusión sin KALINA", esp)
    xb = {}
    for v in todo[(todo.variable == "x_b") & (todo.valor < 0.55) & todo.convergio.fillna(False)].itertuples():
        xb.setdefault(round(v.valor, 6), set()).add(v.clasificacion)
    nota = "**Nota (x_b bajo, no preferido):** " + "; ".join(f"x_b = {v:g} → {', '.join(sorted(c))}" for v, c in sorted(xb.items())) + "." if xb else ""
    ck(nota in rep if nota else "**Nota (x_b bajo" not in rep, "nota de x_b < 0.55", nota[:100])


def main() -> int:
    d = csvs()
    for parte in (parte_a, parte_b, parte_c, parte_d):
        parte(d)
    print(f"\n{len(FALLOS)} fallos" if FALLOS else "\nTODO OK")
    for f in FALLOS: print("  -", f)
    return 1 if FALLOS else 0


if __name__ == "__main__":
    sys.exit(main())
