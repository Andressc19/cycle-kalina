"""M4b — verificación de M4b (TASK_CONTEXT final_M4b, paso «Verificación»).

Recalcula todo desde los CSV y del `REPORTE_M4b.md`: (1) `m4b_muestra.csv` y
`m4b_lhs.csv` con los mismos puntos y los mismos valores; (2) la muestra como
LHS con la semilla 20261007 —regeneración determinista y una vez por franja en
cada variable—; (3) la unión de 500 filas con ids 0–499 sin huecos; (4) dos
valores de la tabla (b) hechos a mano con numpy; (5) que las tres tablas de
franjas sumen N y los KALINA; (6) que el bloqueo por rP sume los genuinos no
KALINA; (7) las cifras del reporte (§3, §6, §8 y §13) contra los CSV; (8) que
existan todos los archivos de salida. Sale con código 1 si algo falla.
"""
from __future__ import annotations

import csv, re, sys  # noqa: E401,E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

import numpy as np  # noqa: E402

from m4_analisis import resumen  # noqa: E402
from m4_datos import CAJA, GENU, VARS10, genu  # noqa: E402
from m4_tablas import gf, nf  # noqa: E402
from m4b_datos import ID0, N_M4B, OUT, leer_union  # noqa: E402
from m4b_corrida import muestra as regenerada  # noqa: E402

ARCHIVOS = ("m4b_rsa.csv", "m4b_pawn.csv", "m4b_prcc.csv", "m4b_top_kalina.csv",
            "m4b_convergencia.csv", "m4b_rangos_presiones.csv",
            "m4b_bloqueo_por_rP.csv", "m4b_cart.txt", "REPORTE_M4b.md",
            "m4b_plano_presiones.png", "m4b_hist_dP_rP.png", "m4b_cdf_kalina.png",
            "m4b_prcc_eta.png", "m4b_rsa_ks.png", "m4b_cart.png")
FALLOS: list = []


def ck(ok, desc: str, det: str = "") -> bool:
    """Imprime `OK`/`FALLO` y acumula los fallos (patrón de `m4_verificar.py`)."""
    print(("OK    " if ok else "FALLO ") + desc + (f" :: {det}" if det else ""),
          flush=True)
    if not ok:
        FALLOS.append(desc)
    return bool(ok)


def _csv(nombre: str) -> list:
    with open(OUT / nombre, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _grupos(filas: list):
    """`(KALINA, genuinos que no son KALINA)` — la misma definición que M4."""
    kal = [f for f in filas if f["clasificacion"] == "KALINA"]
    nok = [f for f in filas if genu(f) and f["clasificacion"] != "KALINA"]
    return kal, nok


def _check_muestra() -> None:
    """La muestra guardada, la corrida y el LHS regenerado tienen que coincidir."""
    mue, lhs = _csv("m4b_muestra.csv"), _csv("m4b_lhs.csv")
    if not ck(len(mue) == N_M4B, f"muestra: {N_M4B} filas", f"hay {len(mue)}"):
        return
    im = sorted(int(r["id_muestra"]) for r in mue)
    il = sorted(int(r["id_muestra"]) for r in lhs)
    ck(im == il == list(range(ID0, ID0 + N_M4B)),
       f"muestra y corrida con los mismos ids {ID0}–{ID0 + N_M4B - 1}",
       f"muestra={len(im)} corrida={len(il)}")
    d = {int(r["id_muestra"]): r for r in lhs}
    dif = max((abs(float(m[v]) - float(d[int(m["id_muestra"])][v]))
               for m in mue for v in VARS10 if int(m["id_muestra"]) in d),
              default=0.0)
    ck(dif <= 1e-9, "las 10 variables son idénticas en muestra y corrida",
       f"dif máx={dif:g}")
    reg = regenerada()
    dr = max((abs(reg[i][v] - float(mue[i][v]))
              for i in range(len(mue)) for v in VARS10), default=0.0)
    ck(dr <= 1e-9, "LHS regenerado con semilla 20261007", f"dif máx={dr:g}")
    n = len(mue)
    mal = []
    for v in VARS10:
        lo, hi = CAJA[v]
        x = sorted(float(r[v]) for r in mue)
        estr = [min(int((z - lo) / (hi - lo) * n), n - 1) for z in x]
        if sorted(estr) != list(range(n)):
            mal.append(v)
    ck(not mal, "LHS: cada variable cae una vez por franja (estratos)", str(mal))


def _check_union() -> list:
    """La unión de los 300 de M4 con los 200 de M4b, sin huecos ni duplicados."""
    filas = leer_union()
    n = 300 + N_M4B
    ck(len(filas) == n, f"unión: {n} filas", f"hay {len(filas)}")
    ids = sorted(int(f["id_muestra"]) for f in filas)
    ck(ids == list(range(n)), "unión: ids 0–" + str(n - 1) + " sin huecos",
       f"{len(set(ids))} únicos")
    return filas


def _check_tabla_b(filas, kal, nok) -> dict:
    """Dos valores de la tabla (b) hechos a mano, más el rP que usa §6."""
    rang = _csv("m4b_rangos_presiones.csv")
    ck(len(rang) == 8, "tabla (b): 8 filas (4 variables × 2 grupos)",
       f"hay {len(rang)}")
    casos = (("P_alta", "KALINA", kal, 5), ("dP", "no_KALINA_genuino", nok, 50),
             ("dP", "KALINA", kal, 50), ("rP", "no_KALINA_genuino", nok, 5))
    for var, grupo, grupo_f, pct in casos:
        r = next((x for x in rang if x["variable"] == var
                  and x["grupo"] == grupo), None)
        if not ck(r is not None, f"tabla (b): fila {var}/{grupo}"):
            continue
        clave = {5: "p05", 50: "mediana"}[pct]
        v = np.array([f[var] for f in grupo_f], float)
        mano = float(np.percentile(v, pct))
        ck(abs(mano - float(r[clave])) <= 1e-6 * max(1.0, abs(mano)),
           f"tabla (b) {var}/{grupo} {clave} a mano",
           f"mano={mano} csv={r[clave]}")
        ck(int(r["n"]) == len(grupo_f), f"tabla (b) {var}/{grupo}: n",
           f"{r['n']} vs {len(grupo_f)}")
    return {x["variable"] + "/" + x["grupo"]: x for x in rang}


def _check_franjas(n, nk) -> None:
    """Las tres tablas de franjas suman N filas y los KALINA del §3."""
    for nom in ("m4b_ventana_por_palta.csv", "m4b_ventana_por_tfuente.csv",
                "m4b_ventana_por_tsumidero.csv"):
        rows = _csv(nom)
        sn = sum(int(r["n"]) for r in rows)
        sk = sum(int(r["n_kalina"]) for r in rows)
        ck(sn == n and sk == nk, f"{nom}: Σn={n} y Σn_kalina={nk}",
           f"Σn={sn} Σnk={sk}")
        mal = [r for r in rows if round(100 * int(r["n_kalina"])
                                        / int(r["n"]), 1) != float(r["pct_kalina"])]
        ck(not mal, f"{nom}: % KALINA = round(100·nk/n, 1)", str(mal[:2]))


def _check_bloqueo(nok) -> None:
    rows = _csv("m4b_bloqueo_por_rP.csv")
    sn = sum(int(r["n"]) for r in rows)
    ck(sn == len(nok), f"bloqueo (g): Σn == genuinos no KALINA ({len(nok)})",
       f"Σn={sn}")


def _check_reporte(filas, rang, nk) -> None:
    txt = (OUT / "REPORTE_M4b.md").read_text(encoding="utf-8")
    ck(all(f"## {i}." in txt for i in range(1, 16)), "reporte: 15 secciones")
    m = re.search(r"De \*\*(\d+)\*\* puntos: \*\*(\d+) KALINA\*\*", txt)
    ck(bool(m) and int(m.group(1)) == len(filas) and int(m.group(2)) == nk,
       "§3: conteos N y KALINA del reporte", m.group(0) if m else "sin frase")
    for var in ("P_alta", "P_baja", "dP", "rP"):
        r = rang[var + "/KALINA"]
        esp = (f"- **{var}:** [{gf(float(r['p05']))}, {gf(float(r['p95']))}]"
               + (" kPa" if var != "rP" else ""))
        ck(esp in txt, f"§13: rango de {var} = p5–p95 KALINA", esp)
    ck(f"p5 de KALINA ({gf(float(rang['rP/KALINA']['p05']))})" in txt,
       "§6: p5 de rP KALINA", rang["rP/KALINA"]["p05"])
    conv = _csv("m4b_convergencia.csv")
    for metrica, etiqueta in (("KS_KALINA", "KS (KALINA)"),
                              ("PRCC_eta", "PRCC(η)")):
        rr = [x for x in conv if x["metrica"] == metrica]
        rho = rr[-1]["rho_spearman"] if rr else ""
        val = "n/d" if rho in ("", None) else nf(float(rho), 4)
        cumple = bool(rr) and rr[-1]["cumple_09"] == "True"
        esp = (f"**{etiqueta} = {val}** "
               f"({'cumple' if cumple else 'NO cumple'} el criterio ρ ≥ 0.9)")
        ck(esp in txt, f"§8: {etiqueta}", esp)


def main() -> int:
    print(f"m4b_verificar | OUT={OUT}", flush=True)
    _check_muestra()
    filas = _check_union()
    res = resumen(filas)
    kal, nok = _grupos(filas)
    nk = res["conteos"].get("KALINA", 0)
    ck(len(kal) == nk and len(kal) + len(nok) == res["n_genuinos"],
       "genuinos == KALINA + CORREGIBLE + INVIABLE del resumen",
       f"kal={len(kal)} nok={len(nok)} res={res['n_genuinos']}")
    rang = _check_tabla_b(filas, kal, nok)
    _check_franjas(len(filas), nk)
    _check_bloqueo(nok)
    _check_reporte(filas, rang, nk)
    for nom in ARCHIVOS:
        ck((OUT / nom).exists(), f"existe {nom}")
    print(f"\n{len(FALLOS)} fallos" if FALLOS else "\nTODO OK", flush=True)
    return 1 if FALLOS else 0


if __name__ == "__main__":
    raise SystemExit(main())
