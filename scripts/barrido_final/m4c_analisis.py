"""M4c — techo de P_baja con el LHS de 150 puntos (TASK_CONTEXT final_M5c_M4c §Parte 2).

Lee `m4c_lhs.csv` (150 puntos con P_baja ∈ [1500, 2500] kPa, sin recalcular
el ciclo) y lo concatena con `m4b_datos.leer_union()` (los 500 de M4 + M4b)
para escribir `m4c_techo.csv` (franjas de 100 kPa de P_baja: 1500–2500 desde
M4c, 1300–1500 desde la unión), `m4c_techo_por_palta.csv` (P_baja máximo
KALINA por las 6 franjas de P_alta de M4b, sobre M4+M4b+M4c),
`m4c_techo.png` (% KALINA contra P_baja de 300 a 2500, con todos los puntos)
y `REPORTE_M4c.md`.
"""
from __future__ import annotations

import sys, time  # noqa: E401,E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from m4_datos import GENU  # noqa: E402
from m4_tablas import gf, nf  # noqa: E402
from m4b_datos import escribir, leer_de, leer_union  # noqa: E402
from m4b_presiones import FRANJAS  # noqa: E402
from m4b_presiones_fig import COLORES, GRIS  # noqa: E402
from m5c_m4c_corrida import ID0_C, N_M4C, OUT_M4C, PB_C  # noqa: E402

CTECHO = ["fuente", "franja", "lo", "hi", "n", "n_kalina", "pct_kalina",
          "P_baja_max_kalina"]
CTPALT = ["franja", "lo", "hi", "n", "n_kalina", "pct_kalina",
          "P_baja_max_kalina"]
PISOS = ((1300.0, 1400.0), (1400.0, 1500.0))
CIELOS = tuple((PB_C[0] + 100.0 * i, PB_C[0] + 100.0 * (i + 1))
               for i in range(10))


def leer_c() -> list:
    """`m4c_lhs.csv` tipado, sin las filas omitidas (no se evaluaron)."""
    return [dict(f, id=int(f["id"])) for f in leer_de(OUT_M4C, "m4c_lhs.csv")
            if f.get("omitido") != "True"]


def franja(filas: list, lo: float, hi: float, fuente: str, ultima: bool,
           campo: str = "P_baja") -> dict:
    """Una fila de 100 kPa: `n`, `n_kalina`, % y P_baja máx de los KALINA."""
    sel = [f for f in filas if f.get(campo) is not None
           and (lo <= f[campo] <= hi if ultima else lo <= f[campo] < hi)]
    kal = [f for f in sel if f["clasificacion"] == "KALINA"]
    pb = [f["P_baja"] for f in kal if f.get("P_baja") is not None]
    return dict(fuente=fuente, franja=f"{lo:.0f}–{hi:.0f}", lo=lo, hi=hi,
                n=len(sel), n_kalina=len(kal),
                pct_kalina=round(100.0 * len(kal) / len(sel), 1) if sel
                else None,
                P_baja_max_kalina=max(pb) if pb else None)


def techo_palta(filas: list) -> list:
    """P_baja máximo KALINA por las 6 franjas de P_alta de `m4b_presiones`."""
    lo, hi, k = FRANJAS["P_alta"]
    return [franja(filas, lo + (hi - lo) * i / k, lo + (hi - lo) * (i + 1) / k,
                   "M4+M4b+M4c", i == k - 1, campo="P_alta")
            for i in range(k)]


def figura(todos: list, cien: list) -> None:
    """`m4c_techo.png`: % KALINA por franja de 100 kPa + todos los puntos."""
    fig, ax = plt.subplots(figsize=(12.5, 5.6))
    xs = [(r["lo"] + r["hi"]) / 2 for r in cien]
    ys = [r["pct_kalina"] or 0.0 for r in cien]
    ax.bar(xs, ys, width=92, color="#c7d9f0", edgecolor="#274c77",
           linewidth=0.7, label="% KALINA por franja de 100 kPa", zorder=1)
    vistos = set()
    for f in todos:
        cls = (f["clasificacion"] if f["clasificacion"] in COLORES
               else "no genuino")
        ax.scatter(f["P_baja"], 100.0 if cls == "KALINA" else 0.0, s=16,
                   alpha=0.65, zorder=3, color=COLORES.get(cls, GRIS),
                   linewidths=0, label=cls if cls not in vistos else None)
        vistos.add(cls)
    ax.axvline(1500, color="#555", ls="--", lw=1.2, zorder=2)
    ax.text(1500, 104, "fin M4/M4b · inicio M4c", ha="center", fontsize=8)
    ax.set_xlabel("P_baja (kPa)")
    ax.set_ylabel("% de puntos KALINA (y = 100 KALINA · 0 no KALINA)", fontsize=9)
    ax.set_xlim(280, 2540)
    ax.set_ylim(-8, 116)
    ax.grid(alpha=0.3, zorder=0)
    ax.legend(fontsize=8, loc="center left", markerscale=2)
    ax.set_title("M4c — dónde termina KALINA al subir P_baja "
                 "(M4 + M4b + M4c)", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT_M4C / "m4c_techo.png", dpi=150)
    plt.close(fig)
    print("m4c_techo.png", flush=True)


def _bloqueo(filas: list) -> str:
    """Códigos dominantes entre los genuinos no KALINA de `filas`."""
    cuenta, nb = {}, 0
    for f in filas:
        if f["clasificacion"] not in GENU or f["clasificacion"] == "KALINA":
            continue
        nb += 1
        cods = [c for c in (f["codigos_falla"] or "").split(",")
                if c] or ["(sin codigos)"]
        for c in cods:
            cuenta[c] = cuenta.get(c, 0) + 1
    if not cuenta:
        return "sin puntos no KALINA genuinos"
    return ", ".join(f"`{c}` ({n} de {nb})"
                     for c, n in sorted(cuenta.items(),
                                        key=lambda kv: (-kv[1], kv[0]))[:3])


def _tabla(rows: list) -> str:
    out = [("| franja P_baja (kPa) | fuente | n | KALINA | % KALINA | "
            "P_baja máx KALINA |"), "|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['franja']} | {r['fuente']} | {r['n']} | "
                   f"{r['n_kalina']} | {nf(r['pct_kalina'], 1)} | "
                   f"{gf(r['P_baja_max_kalina'])} |")
    return "\n".join(out)


def _doc(c: list, todos: list, filas: list, tp: list) -> str:
    n_om = N_M4C - len(c)
    nk = sum(1 for f in c if f["clasificacion"] == "KALINA")
    tm4 = max((f["P_baja"] for f in c if f["clasificacion"] == "KALINA"),
              default=None)
    kp = [f["P_baja"] for f in todos if f["clasificacion"] == "KALINA"
          and f.get("P_baja") is not None]
    techo, piso = (max(kp), min(kp)) if kp else (None, None)
    arriba = [f for f in c if tm4 is not None and f.get("P_baja")
              and f["P_baja"] > tm4 and f["clasificacion"] in GENU
              and f["clasificacion"] != "KALINA"]
    bajar = [f for f in c if tm4 is not None and f.get("P_baja")
             and f["P_baja"] <= tm4 and f["clasificacion"] in GENU
             and f["clasificacion"] != "KALINA"]
    con_kal = [r for r in filas if r["n_kalina"]]
    txt_te = ("**M4c no produjo ningún KALINA**: con P_baja ∈ "
              "[1500, 2500] el ciclo ya no es viable en ningún punto."
              if nk == 0 else
              f"El KALINA de mayor P_baja con M4c es **{gf(tm4)} kPa** "
              f"({nk} de {len(c)} puntos de M4c).")
    txt_fp = (f"- Franjas de 100 kPa con al menos un KALINA: "
              f"{con_kal[0]['franja']} … {con_kal[-1]['franja']} kPa."
              if con_kal else "- Ninguna franja de 100 kPa tiene KALINA.")
    return f"""# REPORTE M4c — dónde termina KALINA al subir P_baja
## 1. La pregunta
¿En qué P_baja se acaba el KALINA y qué criterio es el que lo corta? ¿Y cómo depende ese techo de P_alta?
## 2. Qué se hizo
- **LHS de 150 puntos** con `LatinHypercube(d=10, seed=20261008)` sobre la caja de M4 pero con **P_baja ∈ [1500, 2500] kPa** (todo lo demás: T_fuente, T_sumidero, P_alta, x_b, η_t, η_p, ε_HRVG, ε_reg, ε_cond); `id_muestra` de {ID0_C} a {ID0_C + 149}.
- Puntos con `P_baja ≥ P_alta − 300` sin evaluar (`omitido=True`): **{n_om} omitidos**, {len(c)} evaluados. Motor `teqp`, **piso de O2 = T_sumidero**, 7 procesos en el mismo pool que M5c. Punto genuino = KALINA, CORREGIBLE o INVIABLE.
- Apoyo: los 500 de **M4 + M4b** (`leer_union()`), cuya caja llega solo hasta P_baja = 1500 kPa: sirven para el piso 1300–1500 y para el techo por P_alta.
## 3. Dónde termina KALINA (franjas de 100 kPa)
{txt_te}

{_tabla(filas)}
## 4. Qué criterio la corta
Conteo de `codigos_falla` sobre los genuinos **no KALINA** de M4c ({len(arriba)} por encima de {gf(tm4)} kPa y {len(bajar)} hasta ese valor):
- **Por encima del techo:** {_bloqueo(arriba)} · **Dentro de la zona KALINA:** {_bloqueo(bajar)}.
## 5. Cómo cambia el techo con P_alta (las 6 franjas de M4b, sobre M4+M4b+M4c)
| franja P_alta (kPa) | n | KALINA | % KALINA | P_baja máx KALINA |
|---|---|---|---|---|
{chr(10).join(f"| {r['franja']} | {r['n']} | {r['n_kalina']} | {nf(r['pct_kalina'], 1)} | {gf(r['P_baja_max_kalina'])} |" for r in tp)}
{txt_fp}
## 6. La ventana completa de P_baja (300 → 2500 kPa)
- **Piso:** P_baja mínimo de cualquier KALINA de M4+M4b+M4c = **{gf(piso)} kPa**; **techo:** máximo = **{gf(techo)} kPa**.
- Franjas de 100 kPa con KALINA en algún momento: {len(con_kal)} de {len(filas)} (lista completa en `m4c_techo.csv`).
- ¿Sigue KALINA más allá de 1500 kPa? {"no: M4c no dio ningún KALINA en [1500, 2500]." if nk == 0 else f"sí: el KALINA de mayor P_baja está en {gf(tm4)} kPa."}
## 7. Lo que no se sabe
- El LHS tiene 150 puntos en una caja de 10 dimensiones: el techo está acotado por los puntos muestreados, no es una frontera calculada.
- Los {n_om} puntos omitidos no informan nada y no entran en ningún %; y la franja 1300–1500 kPa viene de M4 + M4b (dos LHS distintos), % no comparable punto a punto con M4c.
"""


def main() -> None:
    t0 = time.perf_counter()
    c, u = leer_c(), leer_union()
    if not c:
        raise SystemExit(f"sin filas: falta {OUT_M4C / 'm4c_lhs.csv'}")
    todos = u + c
    filas = ([franja(u, *b, "M4+M4b", b[1] == 1500.0) for b in PISOS]
             + [franja(c, *b, "M4c", b[1] == CIELOS[-1][1])
                for b in CIELOS])
    tp = techo_palta(todos)
    print(f"m4c_analisis | M4c={len(c)} unión={len(u)}", flush=True)
    escribir(OUT_M4C, "m4c_techo.csv", CTECHO, filas)
    escribir(OUT_M4C, "m4c_techo_por_palta.csv", CTPALT, tp)
    figura([f for f in todos if f.get("omitido") != "True"], filas)
    (OUT_M4C / "REPORTE_M4c.md").write_text(_doc(c, todos, filas, tp),
                                            encoding="utf-8")
    print(f"REPORTE_M4c.md escrito | listo en "
          f"{time.perf_counter() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
