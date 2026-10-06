"""M2R — verificación de la salida (TASK_CONTEXT final_M2R): exige cabeceras y conteos
de la malla (60/60/48/21), la retícula completa de las 4 partes, fronteras coherentes
con sus filas, `m2r_kalina.csv` sin duplicados con `d`/`n_cambios` recalculados,
`m2r_resumen.csv` recomputado desde la malla y la bisección, y el reporte contra los CSV."""
from __future__ import annotations

import csv, sys
from collections import Counter
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]
import m2r_corrida as c  # noqa: E402
import m2r_reporte as rep  # noqa: E402
from comun import PROFESOR  # noqa: E402

FLOT = ("val1", "val2", "eta", "Wnet", "m_O1", "m_O2", "t_s", "d")
BOOL = ("convergio", "fuera_rango", "B_verificado")
TEXTO = ("parte", "var1", "var2", "clasificacion", "codigos_falla")
fallos = []

def ck(ok, msg, det=""):
    print(("ok    " if ok else "FALLA ") + msg + ("" if ok else f"  [{det}]"), flush=True)
    if not ok:
        fallos.append(msg)

def tipar(f: dict) -> dict:
    """Las cadenas del CSV vuelven a su tipo (numérico, bool, texto)."""
    g = dict(f)
    for k in FLOT:
        g[k] = None if f.get(k) in (None, "") else float(f[k])
    for k in BOOL:
        g[k] = None if f.get(k) in (None, "") else f[k] == "True"
    for k in TEXTO:
        v = f.get(k) or ""
        g[k] = v if k == "var2" else (v or None)
    return g

def leer(nombre: str, cab: list) -> list:
    """Lee un CSV de la salida y exige la cabecera exacta."""
    with open(c.OUT / nombre, encoding="utf-8", newline="") as fh:
        r = csv.reader(fh)
        hdr = next(r, None)
        filas = [dict(zip(hdr, fila)) for fila in r]
    ck(hdr == cab, f"{nombre}: cabecera", f"esperado {cab}; leído {hdr}")
    return filas

def cerca(a, b, tol=1e-9) -> bool:
    if a is None or b is None:
        return a is None and b is None
    return abs(float(a) - float(b)) <= tol

def clave11(x: dict) -> tuple:
    return tuple(round(x[k], 9) for k in PROFESOR)

def tabla(txt: str, desde: str, hasta: str, cabecera: str) -> list:
    """Filas de dato (sin la de cabecera) de una tabla del reporte."""
    trozo = txt.split(desde)[1].split(hasta)[0]
    return [l for l in trozo.splitlines() if l.startswith("| ") and not l.startswith(cabecera)]

def main() -> int:
    esperado = {p: (1 if c.HUMO else n) for p, n in
                zip(c.PARTES_MALLA, (60, 60, 48, 21))}
    malla, bise = [], []
    for p in c.PARTES_MALLA:
        fil = [tipar(f) for f in leer(f"m2r_{p}_malla.csv", c.CMALLA)]
        ck(len(fil) == esperado[p], f"malla {p}: {len(fil)} filas (esperado {esperado[p]})")
        malla += fil
    for p in c.PARTES_BISE:
        bise += [tipar(f) for f in leer(f"m2r_{p}_biseccion.csv", c.CBISE)]
    todo = malla + bise
    dup = [k for k, n in Counter((f["parte"], f["var1"], f["val1"], f["var2"], f["val2"])
                                 for f in malla).items() if n > 1]
    ck(not dup, "malla: ninguna celda repetida", str(dup[:3]))
    if not c.HUMO:                                    # la retícula, parte por parte
        for v in c.V5:
            got = [f["val1"] for f in malla if f["parte"] == "n1" and f["var1"] == v]
            ck(len(got) == 12 and set(got) == set(c.EPS), f"n1 {v}: 12 valores de [0.40,0.95]")
        for parte, rejilla, val2 in (("n2a", c.HRVG_A, c.EPS), ("n2b", c.HRVG_B, c.PBAJA)):
            ck({f["val1"] for f in malla if f["parte"] == parte} == set(rejilla),
               f"{parte}: eps_hrvg {rejilla[0]:g}..{rejilla[-1]:g}")
            for h in rejilla:
                got = {f["val2"] for f in malla if f["parte"] == parte and f["val1"] == h}
                ck(got == set(val2), f"{parte} eps_hrvg={h:g}: {len(val2)} valores de la 2ª variable")
        ck({f["val1"] for f in malla if f["parte"] == "n3"} == set(c.TF3), "n3: 7 valores de T_fuente")
        ck({f["val2"] for f in malla if f["parte"] == "n3"} == set(c.EC3), "n3: 3 valores de eps_cond")
    fr = leer("m2r_fronteras.csv", rep.CFRON)
    for f in fr:
        f["lo"], f["hi"] = float(f["lo"]), float(f["hi"])
        f["ancho_final"], f["iteraciones"] = float(f["ancho_final"]), int(f["iteraciones"])
        f["lado_si"] = float(f["lado_si"]) if f["lado_si"] not in (None, "") else None
        f["val1f"] = float(f["val1"]) if f["val1"] not in (None, "") else None
    ck(all(f["lo"] < f["hi"] for f in fr), "fronteras: lo < hi")
    ck(all(cerca(f["hi"] - f["lo"], f["ancho_final"]) for f in fr), "fronteras: ancho = hi − lo")
    ck(all(f["iteraciones"] <= c.MAX_IT for f in fr), f"fronteras: ≤ {c.MAX_IT} iteraciones")
    ck(all(f["frontera"] in ("genuino", "kalina", "o2") for f in fr), "fronteras: criterio con nombre válido")
    n_it = sum(f["iteraciones"] for f in fr)
    ck(n_it == len(bise), f"iteraciones de todas las fronteras ({n_it}) = filas de bisección ({len(bise)})")

    def lado_si_clase(f: dict) -> bool:
        """La fila evaluada en `lado_si` tiene la `clase_si` que dice la frontera."""
        if f["parte"] == "n1":
            m = [g for g in todo if g["parte"] == "n1" and g["var1"] == f["var_refinada"]
                 and cerca(g["val1"], f["lado_si"], 1e-12)]
        else:
            m = [g for g in todo if g["parte"] == f["parte"] and g["var2"] == f["var_refinada"]
                 and cerca(g["val1"], f["val1f"], 1e-12) and cerca(g["val2"], f["lado_si"], 1e-12)]
        return bool(m) and m[0]["clasificacion"] == f["clase_si"]
    ck(all(lado_si_clase(f) for f in fr), "fronteras: clase_si coincide con su fila lado_si")
    kal = [tipar(f) for f in leer("m2r_kalina.csv", rep.CKAL)]
    for f in kal:
        f["n_cambios"] = int(f["n_cambios"]) if f["n_cambios"] else None
    ck(len({clave11(rep.combo_de(f)) for f in kal}) == len(kal), "m2r_kalina.csv: sin duplicados por los 11 valores")
    reales = {clave11(rep.combo_de(f)) for f in todo if f["clasificacion"] == "KALINA"}
    ck({clave11(rep.combo_de(f)) for f in kal} == reales,
       f"m2r_kalina.csv: {len(kal)} filas = los {len(reales)} KALINA distintos de la corrida")
    mal = [f["val1"] for f in kal if not cerca(f["d"], rep.d_de(rep.combo_de(f)), 1e-9)
           or f["n_cambios"] != rep.n_cambios(rep.combo_de(f))]
    ck(not mal, f"m2r_kalina.csv: d y n_cambios recalculados en las {len(kal)} filas", str(mal[:3]))
    res = leer("m2r_resumen.csv", rep.CREST)
    grupos = {}
    for f in todo:
        grupos.setdefault(rep._clave(f), []).append(f)
    ck(len(res) == len(grupos), f"m2r_resumen.csv: {len(res)} filas = {len(grupos)} grupos")
    for r in res:
        k = (r["parte"], r["var1"], None if r["parte"] == "n1" else float(r["val1"]))
        g = rep._unicas(grupos.get(k, []))
        gen = [f for f in g if c.genuina(f)]
        kg = [f for f in g if f["clasificacion"] == "KALINA"]
        n2g = [f for f in g if f["convergio"] and f["clasificacion"] == "NO_CONVERGIO"]
        ok = (int(r["n_genuinos"]) == len(gen) and int(r["n_kalina"]) == len(kg)
              and int(r["n_N2"]) == len(n2g)
              and r["var2"] == ("" if r["parte"] == "n1" else (g[0]["var2"] if g else "")))
        dmap = {(f["val1"], f["val2"]): rep.d_de(rep.combo_de(f)) for f in kg}
        emap = {(f["val1"], f["val2"]): f["eta"] for f in kg if f["eta"] is not None}
        if r["menor_d"] and dmap:
            md = float(r["menor_d"])
            kc = (float(r["menor_d_val1"]) if r["menor_d_val1"] else None,
                  float(r["menor_d_val2"]) if r["menor_d_val2"] else None)
            ok = ok and cerca(md, min(dmap.values())) and kc in dmap and cerca(dmap[kc], md)
            ok = ok and (not r["menor_d_eta"] or (kc in emap and cerca(emap[kc], float(r["menor_d_eta"]))))
        if r["mayor_eta"] and emap:
            me = float(r["mayor_eta"])
            km = (float(r["mayor_eta_val1"]) if r["mayor_eta_val1"] else None,
                  float(r["mayor_eta_val2"]) if r["mayor_eta_val2"] else None)
            ok = ok and cerca(me, max(emap.values())) and km in emap and cerca(emap[km], me)
        ok = ok and bool(r["menor_d"]) == bool(dmap) and bool(r["mayor_eta"]) == bool(emap)
        cods = Counter(x for f in gen if f["clasificacion"] != "KALINA"
                       for x in (f["codigos_falla"] or "").split(",") if x)
        ok = ok and sorted(f"{a}({b})" for a, b in cods.items()) == (
            sorted(r["bloqueantes"].split(" · ")) if r["bloqueantes"] else [])
        ck(ok, f'resumen {r["parte"]} {r["var1"]}={r["val1"] or "—"}: conteos, menor_d, mayor_eta y bloqueantes',
            f"CSV={r}")
    txt = (c.OUT / "REPORTE_M2R.md").read_text(encoding="utf-8")
    for n in range(1, 11):
        ck(f"## {n}." in txt, f"REPORTE: sección ## {n}.")
    nk = {p: sum(int(r["n_kalina"]) for r in res if r["parte"] in (("n2a", "n2b") if p == 2 else
         (("n3",) if p == 3 else ("n1",)))) for p in (1, 2, 3)}
    ck(f"la parte 1 da {nk[1]} KALINA con un solo cambio, la parte 2 {nk[2]} conservando la fuente del profesor y la parte 3 {nk[3]}" in txt,
       "REPORTE §8: los tres conteos coinciden con m2r_resumen.csv", f"nk={nk}")
    ck(f"M2R: {len(kal)} KALINA distintos" in txt, "REPORTE §6: nº de KALINA vs m2r_kalina.csv")
    r1 = [r for r in res if r["parte"] == "n1"]
    r2 = [r for r in res if r["parte"] in ("n2a", "n2b")]
    r3 = [r for r in res if r["parte"] == "n3"]
    ck(len(tabla(txt, "## 3.", "## 4.", "| Variable")) == len(r1), f"REPORTE §3: {len(r1)} filas de tabla")
    ck(len(tabla(txt, "## 4.", "## 5.", "| Parte")) == len(r2), f"REPORTE §4: {len(r2)} filas de tabla")
    ck(len(tabla(txt, "## 5.", "## 6.", "| Parte")) == len(r3), f"REPORTE §5: {len(r3)} filas de tabla")
    ck(all(not r["menor_d"] or f'{float(r["menor_d"]):.4f}' in txt for r in res),
       "REPORTE: cada menor_d de m2r_resumen.csv aparece escrito")
    print(("\nTODO OK" if not fallos else f"\n{len(fallos)} FALLAS: " + " | ".join(fallos)), flush=True)
    return 1 if fallos else 0

if __name__ == "__main__":
    raise SystemExit(main())
