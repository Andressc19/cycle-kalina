"""M5c+M4c — verificación final (TASK_CONTEXT final_M5c_M4c, paso «Verificación»).

Recalcula todo desde los CSV y de los dos reportes: (1) la malla de M5c tiene
las 165 celdas de la malla 11×5×3 con exactamente el combo esperado, cada fila
con su clase; (2) `m4c_muestra.csv` tiene los 150 ids 500–649 y el LHS se
regenera con la semilla 20261008 —idéntico y una vez por franja de cada
variable— y `m4c_lhs.csv` concuerda fila a fila (variables y `omitido`) con la
muestra; (3) los conteos: 165 + 150 evaluados de M4c = 315 filas; (4) los
números de los reportes contra los CSV reconstruidos con los mismos helpers;
(5) que existan todos los archivos de salida. Sale con código 1 si algo falla.
"""
from __future__ import annotations

import csv, re, sys  # noqa: E401,E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

import numpy as np  # noqa: E402

from m4_datos import CAJA, VARS10, GENU  # noqa: E402
from m4_tablas import gf, nf  # noqa: E402
from m4b_datos import leer_de, leer_union  # noqa: E402
from m5c_m4c_corrida import (ID0_C, N_M4C, OUT_M4C, OUT_M5C, PB_C,  # noqa: E402
                             muestra_m4c, puntos_m5c)
from m5c_analisis import frontera as fr_m5c  # noqa: E402
from m5c_analisis import fila_md  # noqa: E402
from m4c_analisis import CIELOS, PISOS, franja, techo_palta  # noqa: E402

FALLOS: list = []
ARCHIVOS = ("m5c_malla.csv", "m5c_frontera.csv", "m5c_mapa.png",
            "REPORTE_M5c.md") + (
    "m4c_muestra.csv", "m4c_lhs.csv", "m4c_techo.csv",
    "m4c_techo_por_palta.csv", "m4c_techo.png", "REPORTE_M4c.md")


def ck(ok, desc: str, det: str = "") -> bool:
    """Imprime `OK`/`FALLO` y acumula los fallos (patrón de `m4b_verificar.py`)."""
    print(("OK    " if ok else "FALLO ") + desc + (f" :: {det}" if det else ""),
          flush=True)
    if not ok:
        FALLOS.append(desc)
    return bool(ok)


def _check_m5c() -> tuple:
    """Malla de M5c: ids, celdas completas y combos exactos de la malla."""
    filas = leer_de(OUT_M5C, "m5c_malla.csv")
    for f in filas:
        f["id"] = int(f["id"])
    esperado = {p["id"]: p["combo"] for p in puntos_m5c()}
    ck(len(filas) == len(esperado), f"M5c: {len(esperado)} filas",
       f"hay {len(filas)}")
    ids = sorted(f["id"] for f in filas)
    ck(ids == sorted(esperado), "M5c: ids exactos de la malla",
       f"{ids[:3]}…{ids[-3:]}")
    mal = []
    for f in filas:
        c = esperado[f["id"]]
        if any(abs(f[v] - c[v]) > 1e-12 for v in ("T_fuente", "T_sumidero",
                                                  "P_alta", "P_baja",
                                                  "eps_cond")) or \
           any(abs(f[v] - c[v]) > 1e-12 for v in ("x_b", "m_b", "eta_t",
                                                  "eta_p", "eps_hrvg",
                                                  "eps_reg")):
            mal.append(f["id"])
    ck(not mal, "M5c: cada fila es exactamente una celda de la malla "
                "(16 variables x_b/m_b/η/ε incluidas)", str(mal[:5]))
    ck(all(f["motor"] == "teqp" for f in filas), "M5c: motor teqp en todo")
    nk = sum(1 for f in filas if f["clasificacion"] == "KALINA")
    okc = (None, "", "NO_CONVERGIO")
    ck(all(f["clasificacion"] in GENU or f["clasificacion"] in okc
           for f in filas),
       "M5c: clasificación ∈ {KALINA, CORREGIBLE, INVIABLE, NO_CONVERGIO}",
       f"no genuinos={sum(1 for f in filas if f['clasificacion'] not in GENU)}")
    return filas, nk


def _check_m4c(filas_c) -> None:
    """Muestra (ids + LHS regenerado + estratos) y corrida contra la muestra."""
    mues = _csv("m4c_muestra.csv")
    ck(len(mues) == N_M4C, f"M4c muestra: {N_M4C} filas", f"hay {len(mues)}")
    im = sorted(int(r["id_muestra"]) for r in mues)
    ck(im == list(range(ID0_C, ID0_C + N_M4C)),
       f"M4c muestra: ids {ID0_C}–{ID0_C + N_M4C - 1} sin huecos")
    reg = muestra_m4c()
    dr = max((abs(reg[i][v] - float(mues[i][v]))
              for i in range(len(mues)) for v in VARS10), default=0.0)
    ck(dr <= 1e-9, "M4c: LHS regenerado con semilla 20261008", f"dif={dr:g}")
    lo = [CAJA[v][0] for v in VARS10]
    hi = [CAJA[v][1] for v in VARS10]
    lo[VARS10.index("P_baja")], hi[VARS10.index("P_baja")] = PB_C
    mal = []
    for v in VARS10:
        a, b = lo[VARS10.index(v)], hi[VARS10.index(v)]
        x = sorted(float(r[v]) for r in mues)
        estr = [min(int((z - a) / (b - a) * N_M4C), N_M4C - 1) for z in x]
        if sorted(estr) != list(range(N_M4C)):
            mal.append(v)
    ck(not mal, "M4c: cada variable cae una vez por franja (estratos)", str(mal))
    d = {int(r["id"]): r for r in filas_c}
    fal, omit_bien = [], 0
    for m in mues:
        r = d.get(int(m["id_muestra"]))
        if r is None:
            fal.append("sin fila"); continue
        dif = max((abs(float(m[v]) - float(r[v])) for v in VARS10), default=0.0)
        if dif > 1e-9:
            fal.append(f"vars {m['id_muestra']}")
        omit = r["omitido"] == "True"
        if omit and (r["clasificacion"] or r["convergio"] not in (None, "")):
            fal.append(f"omitido sucio {m['id_muestra']}")
        if omit == (float(m["P_baja"]) >= float(m["P_alta"]) - 300.0):
            omit_bien += 1
    ck(not fal, "M4c: corrida == muestra (variables y omitido)",
       ", ".join(fal[:5]))
    ck(omit_bien == len(mues), "M4c: criterio omitido = P_baja ≥ P_alta − 300",
       f"{omit_bien}/{len(mues)}")
    ck(len(filas_c) == N_M4C, f"M4c: la corrida tiene {N_M4C} filas "
                              "(omitidas incluidas)", f"hay {len(filas_c)}")
    ck(len(filas_c) == len(set(int(r["id"]) for r in filas_c)),
       "M4c: sin ids duplicados")
    return sum(1 for r in filas_c if r["omitido"] == "True")


def _csv(nombre: str) -> list:
    with open(OUT_M4C / nombre, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _check_reportes(filas5, nk5, filas_c, union, n_om) -> None:
    """Los números de los dos reportes contra los CSV reconstruidos."""
    txt5 = (OUT_M5C / "REPORTE_M5c.md").read_text(encoding="utf-8")
    m = re.search(r"De los (\d+) puntos de la malla: \*\*(\d+) KALINA\*\*", txt5)
    ck(bool(m) and int(m.group(1)) == len(filas5) and int(m.group(2)) == nk5,
       "reporte M5c: conteos N y KALINA", m.group(0) if m else "sin frase")
    mal5 = [r["eps_cond"] for r in fr_m5c(filas5) if fila_md(r) not in txt5]
    ck(not mal5, "reporte M5c: las 15 filas de la franja están en la tabla",
       str(mal5[:3]))
    txtc = (OUT_M4C / "REPORTE_M4c.md").read_text(encoding="utf-8")
    m = re.search(r"\*\*(\d+) omitidos\*\*, (\d+) evaluados", txtc)
    ck(bool(m) and int(m.group(1)) == n_om
       and int(m.group(2)) == len(filas_c) - n_om,
       "reporte M4c: omitidos y evaluados", m.group(0) if m else "sin frase")
    c = [f for f in filas_c if f["omitido"] != "True"]
    rows = ([franja(union, *b, "M4+M4b", b[1] == 1500.0) for b in PISOS]
            + [franja(c, *b, "M4c", b[1] == CIELOS[-1][1]) for b in CIELOS])
    mal = [r["franja"] for r in rows if
           (f"| {r['franja']} | {r['fuente']} | {r['n']} | {r['n_kalina']} | "
            f"{nf(r['pct_kalina'], 1)} | {gf(r['P_baja_max_kalina'])} |")
           not in txtc]
    ck(not mal, "reporte M4c: tabla de franjas de 100 kPa", str(mal[:3]))
    mal2 = [r["franja"] for r in techo_palta(union + c) if
            (f"| {r['franja']} | {r['n']} | {r['n_kalina']} | "
             f"{nf(r['pct_kalina'], 1)} | {gf(r['P_baja_max_kalina'])} |")
            not in txtc]
    ck(not mal2, "reporte M4c: tabla por franja de P_alta", str(mal2[:3]))


def main() -> int:
    print(f"m5c_m4c_verificar | OUT_M5C={OUT_M5C} OUT_M4C={OUT_M4C}",
          flush=True)
    filas5, nk5 = _check_m5c()
    filas_c = leer_de(OUT_M4C, "m4c_lhs.csv")
    for f in filas_c:
        f["id"] = int(f["id"])
    n_om = _check_m4c(filas_c)
    _check_reportes(filas5, nk5, filas_c, leer_union(), n_om)
    for nom in ARCHIVOS:
        d = OUT_M5C if nom.startswith("m5c") or nom.startswith("REPORTE_M5c") \
            else OUT_M4C
        ck((d / nom).exists(), f"existe {nom}")
    print(f"\n{len(FALLOS)} fallos" if FALLOS else "\nTODO OK", flush=True)
    return 1 if FALLOS else 0


if __name__ == "__main__":
    raise SystemExit(main())