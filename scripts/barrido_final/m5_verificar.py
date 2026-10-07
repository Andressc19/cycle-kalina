"""M5 — verificación de la campaña M5 (TASK_CONTEXT final_M5 §Pasos 4).

Comprueba, SIN recalcular el ciclo: (1) `m5_muestra.csv` ↔ `m5_lhs.csv`;
(2) que cada escenario conserve EXACTAMENTE los valores del profesor que
declara — con la transcripción INDEPENDIENTE `ESC_SPEC`/`RANG_SPEC` escrita a
mano desde el TASK_CONTEXT —; (3) la propiedad LHS (un punto por franja) y la
semilla `20261007 + k`; y (4) que los números de `REPORTE_M5.md` y de los 3
CSV coincidan con `m5_lhs.csv`. Código de salida 1 si algo falla.
"""
from __future__ import annotations
import csv, math, re, sys
from pathlib import Path
_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]
import numpy as np
from scipy.stats import ks_2samp, qmc
from comun import PROFESOR
from m4_datos import GENU
from m4_tablas import gf
from m4b_datos import leer_de
from m5_corrida import FIJOS, LIBRES, N_POR_ESC, OUT, RANGOS, SEED0
import m5_reporte as rep
# Transcripción INDEPENDIENTE de TASK_CONTEXT final_M5 (§Escenarios y §rangos).
ESC_SPEC = {1: ("T_fuente", "T_sumidero"), 2: ("P_alta", "P_baja"),
            3: ("P_alta", "P_baja", "T_sumidero"),
            4: ("P_alta", "T_fuente", "T_sumidero"), 5: ("T_fuente", "x_b")}
RANG_SPEC = {"P_alta": (2000.0, 5000.0), "P_baja": (200.0, 2000.0),
             "T_fuente": (380.0, 623.15), "T_sumidero": (278.15, 303.55),
             "x_b": (0.50, 0.85), "eta_t": (0.40, 0.95), "eta_p": (0.40, 0.95),
             "eps_hrvg": (0.40, 0.95), "eps_reg": (0.40, 0.95),
             "eps_cond": (0.40, 0.95)}
G = ("min", "p05", "mediana", "p95", "max")           # estadísticos
RES_ENT = ("escenario", "n", "omitidos", "evaluados", "KALINA", "genuinos",
           "N2", "fuera_rango", "bloqueante_n", "mejor_D_id", "cercano_id",
           "mejor_eta_id")
RES_FLT = ("mejor_D", "cercano_d", "cercano_eta", "mejor_eta", "suma_t_s")
CER_FLT = ("d", "D", "eta") + tuple(RANGOS)
FAL = 0

def chk(ok: bool, msg: str) -> None:
    """Imprime `OK`/`FALLO` y acumula los fallos para el código de salida."""
    global FAL
    FAL += 0 if ok else 1
    print(("OK    " if ok else "FALLO ") + msg, flush=True)

def _ig(a, b) -> bool:
    """Igualdad con tolerancia de 1e-12; `None` solo es igual a `None`."""
    if a is None or b is None:
        return a is None and b is None
    if isinstance(a, str) or isinstance(b, str):
        return a == b
    return math.isclose(float(a), float(b), rel_tol=1e-12, abs_tol=1e-12)

def _num(c):
    """Cadena del CSV a `float`; vacío o inconvertible → `None`."""
    if c in (None, ""):
        return None
    try:
        return float(c)
    except (TypeError, ValueError):
        return None

def _tipar(nombre: str, ent: tuple, flt: tuple) -> list:
    """`OUT/nombre` tipado: enteros en `ent`, flotables en `flt`."""
    out = []
    with open(OUT / nombre, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            d = dict(r)
            for k in ent:
                d[k] = None if r[k] in (None, "") else int(r[k])
            for k in flt:
                d[k] = _num(r[k])
            out.append(d)
    return out
def _mue() -> dict:
    filas = _tipar("m5_muestra.csv", ("escenario", "id"), tuple(RANGOS))
    return {(f["escenario"], f["id"]): {v: f[v] for v in RANGOS} for f in filas}


def _lhs() -> tuple:
    filas = leer_de(OUT, "m5_lhs.csv")
    for f in filas:
        f["escenario"], f["id"] = int(f["escenario"]), int(f["id"])
        f["omitido"] = f.get("omitido") == "True"
    return filas, {(f["escenario"], f["id"]): f for f in filas}

def _stats(vals: list) -> dict:
    """n, mín, p5, mediana, p95 y máx, calculados AQUÍ (no importados)."""
    if not vals:
        return dict(n=0, min=None, p05=None, mediana=None, p95=None, max=None)
    a = np.array(vals, dtype=float)
    p05, med, p95 = np.percentile(a, [5, 50, 95])
    return dict(n=len(vals), min=float(a.min()), p05=float(p05),
                mediana=float(med), p95=float(p95), max=float(a.max()))

def _d(f: dict, lib: list) -> float:
    """d = Σ |v − v_prof|/(b − a) sobre las libres, RECALCULADO aquí."""
    return sum(abs(f[v] - PROFESOR[v]) / (RANG_SPEC[v][1] - RANG_SPEC[v][0])
               for v in lib)

def _checa_rangos(k: int, filas: list, rng: list) -> None:
    """`m5_rangos.csv` recalculado desde `m5_lhs.csv` (estadísticos y KS/p)."""
    mal, sel = [], [f for f in filas if not f["omitido"] and f["escenario"] == k]
    for r in [x for x in rng if x["escenario"] == k]:
        v = r["variable"]
        kv = [f[v] for f in sel if f["clasificacion"] == "KALINA" and f[v] is not None]
        nv = [f[v] for f in sel if f["clasificacion"] != "KALINA" and f[v] is not None]
        st = _stats(kv if r["grupo"] == "KALINA" else nv)
        if any(not _ig(st[c], r[c]) for c in ("n",) + G):
            mal.append(f'{v}/{r["grupo"]} estadísticos')
        if r["grupo"] == "KALINA" and r["n"] >= 10 and nv:
            st2, p2 = ks_2samp(kv, nv)
            if not (_ig(st2, r["KS"]) and _ig(p2, r["p_valor"])):
                mal.append(f"{v} KS/p")
    n = len([x for x in rng if x["escenario"] == k])
    chk(not mal, f"S{k}: los {n} renglones de m5_rangos == recalculados desde m5_lhs" + (f" -> {mal}" if mal else ""))

def _checa_cercano(k: int, filas: list, cer: list) -> None:
    """`m5_cercano_profesor.csv` recalculado desde `m5_lhs.csv`."""
    lib = [v for v in RANG_SPEC if v not in ESC_SPEC[k]]
    ev = [f for f in filas if f["escenario"] == k and not f["omitido"]]
    kal = [f for f in ev if f["clasificacion"] == "KALINA"]
    fil = [x for x in cer if x["escenario"] == k]
    c = next((x for x in fil if x["tipo"] == "cercano"), None)
    if kal:
        esp = min(kal, key=lambda f: (_d(f, lib), f["id"]))
        eta = max((f for f in kal if f["eta"] is not None),
                  key=lambda f: (f["eta"], -f["id"]), default=None)
        tip = ["cercano"] + (["mejor_eta"] if eta else [])
        chk(sorted(x["tipo"] for x in fil) == tip and c["id"] == esp["id"]
            and _ig(c["d"], _d(esp, lib)) and _ig(c["eta"], esp["eta"])
            and all(_ig(c[v], esp[v]) for v in RANGOS),
            f"S{k}: cercano = id {esp['id']} (d = {gf(_d(esp, lib))}); mayor η = id {eta['id'] if eta else 'n/d'}")
    else:
        gen = [f for f in ev if f["clasificacion"] in GENU and f["D"] is not None]
        esp = min(gen, key=lambda f: (f["D"], f["id"]), default=None)
        md = next((x for x in fil if x["tipo"] == "genuino_mD"), None)
        chk(len(fil) == (1 if esp else 0) and (md is None) == (esp is None)
            and (esp is None or (md["id"] == esp["id"] and _ig(md["D"], esp["D"])
                                 and all(_ig(md[v], esp[v]) for v in RANGOS))),
            f"S{k}: genuino de menor D = id {esp['id'] if esp else 'n/d'} (D = {gf(esp['D']) if esp else 'n/d'})")

def main() -> None:
    print(f"m5_verificar | OUT={OUT}", flush=True)
    chk(set(RANGOS) == set(RANG_SPEC) and all(RANGOS[v] == RANG_SPEC[v] for v in RANG_SPEC),
        "la caja de m5_corrida == los rangos del TASK_CONTEXT")
    for k in sorted(ESC_SPEC):
        chk(set(FIJOS[k]) == set(ESC_SPEC[k]) and set(LIBRES[k]) == set(RANG_SPEC) - set(ESC_SPEC[k]),
            f"S{k}: conserva {', '.join(ESC_SPEC[k])} y deja el resto libre")
    faltan = [n for n in ("m5_muestra.csv", "m5_lhs.csv", "m5_resumen.csv", "m5_rangos.csv",
                          "m5_cercano_profesor.csv", "REPORTE_M5.md") if not (OUT / n).exists()]
    chk(not faltan, f"están los 6 archivos de salida (faltan: {faltan})")
    if faltan: print(f"FIN: {FAL} fallo(s)", flush=True); sys.exit(1)
    mue, filas, idx = _mue(), *_lhs()
    chk(set(mue) == set(idx), f"muestra y corrida cubren los mismos (escenario, id): {len(mue)} vs {len(idx)}")
    dif = [k for k in set(mue) & set(idx) if any(mue[k][v] != idx[k][v] for v in RANGOS)]
    chk(not dif, f"las 10 variables de cada punto son idénticas en las dos ({len(dif)} distintos)")
    mal = [k for k, f in idx.items() if f["omitido"] != (f["P_baja"] >= f["P_alta"] - 300.0) or (f["omitido"] and f["clasificacion"] is not None)]
    chk(not mal, f"omitido=True ⇔ P_baja ≥ P_alta − 300 y los omitidos no se evaluaron ({len(mal)} mal)")
    for k in sorted(ESC_SPEC):
        n = sum(1 for (kk, _) in mue if kk == k)
        fil2, lib = [mue[k, i] for i in range(n)], [v for v in RANG_SPEC if v not in ESC_SPEC[k]]
        chk(n == N_POR_ESC and all(m[v] == PROFESOR[v] for m in fil2 for v in ESC_SPEC[k]), f"S{k}: {n} puntos y lo conservado vale EXACTAMENTE lo del profesor")
        chk(all(RANG_SPEC[v][0] <= m[v] <= RANG_SPEC[v][1] for m in fil2 for v in lib), f"S{k}: las {len(lib)} libres caen dentro de la caja de M5")
        mal = [v for v in lib if sorted(min(n - 1, int(np.floor((m[v] - RANG_SPEC[v][0]) / (RANG_SPEC[v][1] - RANG_SPEC[v][0]) * n + 1e-9))) for m in fil2) != list(range(n))]
        chk(not mal, f"S{k}: propiedad LHS, un punto por cada una de las {n} franjas" + (f" -> falla {mal}" if mal else ""))
        X = qmc.scale(qmc.LatinHypercube(d=len(lib), seed=SEED0 + k).random(n), [RANG_SPEC[v][0] for v in lib], [RANG_SPEC[v][1] for v in lib])
        dmax = max(abs(float(X[i][j]) - fil2[i][v]) for i in range(n) for j, v in enumerate(lib))
        chk(dmax < 1e-9, f"S{k}: la muestra se regenera con seed={SEED0}+{k} (dif. máx {dmax:.1e})")
    res = _tipar("m5_resumen.csv", RES_ENT, RES_FLT)
    for r in res: r["factible"] = r["factible"] == "True"; r["bloqueante"] = r["bloqueante"] or None
    rng = _tipar("m5_rangos.csv", ("escenario", "n"), G + ("KS", "p_valor"))
    cer = _tipar("m5_cercano_profesor.csv", ("escenario", "id"), CER_FLT)
    for c in cer: c["fuera_rango"] = None if c["fuera_rango"] in (None, "") else c["fuera_rango"] == "True"; c["B_verificado"] = c["B_verificado"] or None
    txt = (OUT / "REPORTE_M5.md").read_text(encoding="utf-8")
    doc = rep._doc(res, cer, rng)
    chk(doc == txt, "REPORTE_M5.md idéntico al texto reconstruido desde los 3 CSV")
    if doc != txt:
        i = next((j for j, (a, b) in enumerate(zip(doc.splitlines(), txt.splitlines()), 1) if a != b), 0)
        print(f"      1a diferencia en la línea {i}", flush=True)
    for k in sorted(ESC_SPEC):
        f2 = [f for f in filas if f["escenario"] == k]
        ev = [f for f in f2 if not f["omitido"]]
        c = dict(n=len(f2), omitidos=len(f2) - len(ev), evaluados=len(ev),
                 KALINA=sum(f["clasificacion"] == "KALINA" for f in ev),
                 genuinos=sum(f["clasificacion"] in GENU for f in ev),
                 N2=sum(f["convergio"] is True and f["clasificacion"] == "NO_CONVERGIO" for f in ev),
                 fuera_rango=sum(f["fuera_rango"] is True for f in ev))
        r = next(x for x in res if x["escenario"] == k)
        mal = [q for q, v in c.items() if r[q] != v] + ([] if r["factible"] == (c["KALINA"] > 0) else ["factible"])
        chk(not mal, f"S{k}: m5_resumen == cuentas recalculadas desde m5_lhs" + (f" -> {mal}" if mal else ""))
        _checa_rangos(k, filas, rng)
        _checa_cercano(k, filas, cer)
    print(f"FIN: {FAL} fallo(s)", flush=True)
    sys.exit(1 if FAL else 0)


if __name__ == "__main__":
    main()