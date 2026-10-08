"""M5c — análisis de la malla de 165 puntos (TASK_CONTEXT final_M5c_M4c §Parte 1).

Lee `m5c_malla.csv` (sin recalcular el ciclo) y escribe `m5c_frontera.csv` (por
cada (T_sumidero, eps_cond), el rango de T_fuente que es KALINA y la η en cada
extremo), `m5c_mapa.png` (un panel por T_sumidero, eps_cond vs T_fuente con el
color de la clase) y `REPORTE_M5c.md` (la franja en tabla y en palabras, el
criterio que bloquea a cada lado y la mejor η dentro de la franja).
`fila_md()` arma la fila de la tabla del reporte; la vuelve a usar
`m5c_m4c_verificar.py` para contrastarla contra el CSV.
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
from m4b_datos import escribir, leer_de  # noqa: E402
from m4b_presiones_fig import COLORES, GRIS  # noqa: E402
from m5c_m4c_corrida import EPS_COND, OUT_M5C, T_SUM  # noqa: E402

CFRON = ["T_sumidero", "eps_cond", "n_kalina", "T_fuente_min", "T_fuente_max",
         "eta_en_Tmin", "eta_en_Tmax"]
CAB = ("| T_sumidero (K) | ε_cond | celdas KALINA | T_fuente mín (K) | "
       "T_fuente máx (K) | η en el mínimo | η en el máximo |")
SEP = "|---|---|---|---|---|---|---|"
ORDEN = ("KALINA", "CORREGIBLE", "INVIABLE", "no genuino")


def leer() -> list:
    """`m5c_malla.csv` tipado (el `id` entero; el resto lo tipa `leer_de`)."""
    filas = leer_de(OUT_M5C, "m5c_malla.csv")
    for f in filas:
        f["id"] = int(f["id"])
    return filas

def frontera(filas: list) -> list:
    """Una fila por (T_sumidero, eps_cond) con el rango KALINA de T_fuente."""
    out = []
    for ts in T_SUM:
        for ec in EPS_COND:
            kal = sorted((f for f in filas
                          if f["T_sumidero"] == ts and f["eps_cond"] == ec
                          and f["clasificacion"] == "KALINA"),
                         key=lambda f: f["T_fuente"])
            a, b = (kal[0], kal[-1]) if kal else (None, None)
            out.append(dict(T_sumidero=ts, eps_cond=ec, n_kalina=len(kal),
                            T_fuente_min=None if a is None else a["T_fuente"],
                            T_fuente_max=None if b is None else b["T_fuente"],
                            eta_en_Tmin=None if a is None else a["eta"],
                            eta_en_Tmax=None if b is None else b["eta"]))
    return out


def fila_md(r: dict) -> str:
    """La fila de `r` como línea de la tabla del reporte."""
    return (f"| {gf(r['T_sumidero'])} | {gf(r['eps_cond'])} | {r['n_kalina']} | "
            f"{gf(r['T_fuente_min'])} | {gf(r['T_fuente_max'])} | "
            f"{nf(r['eta_en_Tmin'], 4)} | {nf(r['eta_en_Tmax'], 4)} |")


def bloqueante(filas: list) -> tuple:
    """`(código dominante, n del código, n de genuinos no KALINA)`."""
    cuenta, nb = {}, 0
    for f in filas:
        if f["clasificacion"] not in GENU or f["clasificacion"] == "KALINA":
            continue
        nb += 1
        cods = [c for c in (f["codigos_falla"] or "").split(",") if c]
        for c in cods or ["(sin codigos)"]:
            cuenta[c] = cuenta.get(c, 0) + 1
    if not cuenta:
        return None, 0, nb
    c = max(cuenta, key=lambda k: (cuenta[k], k))    # empate: el mayor alfabét.
    return c, cuenta[c], nb


def mapa(filas: list) -> None:
    """`m5c_mapa.png`: un panel por T_sumidero, eps_cond (x) vs T_fuente (y)."""
    fig, axs = plt.subplots(1, len(T_SUM), figsize=(14.5, 5.4), sharex=True,
                            sharey=True)
    for ax, ts in zip(axs, T_SUM):
        vistos = set()
        for f in filas:
            if f["T_sumidero"] != ts:
                continue
            cls = (f["clasificacion"] if f["clasificacion"] in COLORES
                   else "no genuino")
            ax.scatter(f["eps_cond"], f["T_fuente"], s=48, edgecolors="k",
                       linewidths=0.3, alpha=0.88, c=COLORES.get(cls, GRIS),
                       label=cls if cls not in vistos else None)
            vistos.add(cls)
        ax.set_title(f"T_sumidero = {gf(ts)} K", fontsize=10)
        ax.set_xticks(list(EPS_COND))
        ax.set_xlabel("ε_cond (−)", fontsize=9)
        ax.grid(alpha=0.3)
        hs = [plt.Line2D([], [], marker="o", ls="", markeredgecolor="k",
                         color=COLORES.get(c, GRIS), label=c)
              for c in ORDEN if c in vistos]
        ax.legend(handles=hs, fontsize=7, loc="lower right")
    axs[0].set_ylabel("T_fuente (K)", fontsize=9)
    fig.suptitle("M5c — malla de 165 puntos con P_alta = 3000 y P_baja = 400 kPa, "
                 "color = clase", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT_M5C / "m5c_mapa.png", dpi=150)
    plt.close(fig)
    print("m5c_mapa.png", flush=True)


def _doc(filas: list, fron: list) -> str:
    kal = [f for f in filas if f["clasificacion"] == "KALINA"]
    nk, ne = len(kal), len(filas)
    tabla = "\n".join([CAB, SEP] + [fila_md(r) for r in fron])
    nvacia = sum(1 for r in fron if r["n_kalina"] == 0)
    ts_ok = sorted({r["T_sumidero"] for r in fron if r["n_kalina"]})
    ec_ok = sorted({r["eps_cond"] for r in fron if r["n_kalina"]})
    tmin = min((f["T_fuente"] for f in kal), default=None)
    tmax = max((f["T_fuente"] for f in kal), default=None)
    bajo = [f for f in filas if tmin is not None and f["T_fuente"] < tmin]
    alto = [f for f in filas if tmax is not None and f["T_fuente"] > tmax]
    b1, n1, N1 = bloqueante(bajo)
    b2, n2, N2 = bloqueante(alto)
    mejor = max((f for f in kal if f["eta"] is not None),
                key=lambda f: (f["eta"], -f["id"]), default=None)
    filas_ts = []
    for ts in T_SUM:
        if all(r["n_kalina"] == 0 for r in fron if r["T_sumidero"] == ts):
            c, n, N = bloqueante([f for f in filas if f["T_sumidero"] == ts])
            filas_ts.append(f"- T_sumidero = {gf(ts)} K: ningún punto KALINA; "
                            f"el criterio que más se rompe es `{c}` ({n}/{N}).")
    ts_txt = (f"{gf(ts_ok[0])} K … {gf(ts_ok[-1])} K ({len(ts_ok)} de los 3 "
              "valores; los que no aparecen no tienen ningún KALINA)"
              if ts_ok else "ningún T_sumidero de la malla da KALINA")
    ec_txt = (f"{gf(ec_ok[0])} … {gf(ec_ok[-1])} ({len(ec_ok)} de los 5 "
              "valores)") if ec_ok else "ningún ε_cond de la malla da KALINA"
    vr = "ninguno" if mejor is None else ("sí" if mejor["fuera_rango"]
                                          else "no")
    mejor_txt = ("Ningún punto de la malla quedó KALINA." if mejor is None else
                 f"El KALINA de mayor η es el id {mejor['id']}: **η = "
                 f"{nf(mejor['eta'], 4)}** (T_fuente = {gf(mejor['T_fuente'])} K, "
                 f"ε_cond = {gf(mejor['eps_cond'])}, T_sumidero = "
                 f"{gf(mejor['T_sumidero'])} K, D = {nf(mejor['D'])}, fuera de "
                 f"rango = {vr}, B_verificado = {mejor.get('B_verificado')}).")
    return f"""# REPORTE M5c — la franja KALINA con las presiones del profesor
## 1. La pregunta
Con **P_alta = 3000 kPa y P_baja = 400 kPa** (las presiones del profesor), ¿en qué franja exacta de T_fuente, ε_cond y T_sumidero el ciclo es KALINA?
## 2. Qué se hizo
- **Malla completa:** T_fuente ∈ {{385, 387.5, …, 410}} K (11 valores), ε_cond ∈ {{0.85, 0.875, 0.90, 0.925, 0.95}} (5) y T_sumidero ∈ {{278.15, 290.65, 300.032917}} K (3): 11 × 5 × 3 = **{ne} corridas**, cada una con flush en `m5c_malla.csv`.
- **Todo lo demás igual a `comun.PROFESOR`:** x_b = 0.50, η_t = 0.85, η_p = 0.75, ε_HRVG = 0.85, ε_reg = 0.75, m_b = 1.0. Motor `teqp`, 7 procesos en el mismo pool que M4c y **piso de O2 = T_sumidero** en todo punto.
- **Punto genuino:** KALINA, CORREGIBLE o INVIABLE. Las NO_CONVERGIO no cuentan.
## 3. La franja exacta
De los {ne} puntos de la malla: **{nk} KALINA**.

{tabla}
## 4. La franja en palabras
El ciclo es KALINA solo en estas combinaciones de la malla:
- **T_sumidero:** {ts_txt}.
- **ε_cond:** {ec_txt}.
- **T_fuente:** de {gf(tmin)} a {gf(tmax)} K (los extremos exactos de la franja; entre ellos puede haber huecos, que la columna «celdas KALINA» de §3 revela).
{chr(10).join(filas_ts)}
## 5. Qué bloquea a cada lado de la franja
Criterio de conteo: entre los puntos **genuinos que NO son KALINA** con T_fuente **por debajo** de la franja ({N1} puntos) y **por encima** de ella ({N2} puntos), se cuenta cada código de `codigos_falla`.

- **Por debajo de {gf(tmin)} K:** `{b1}` rompe {n1} de {N1}.
- **Por encima de {gf(tmax)} K:** `{b2}` rompe {n2} de {N2}.
- Celdas de la malla sin ningún KALINA: {nvacia} de {len(fron)} (las verás con «celdas KALINA» = 0 en §3; los T_sumidero sin ningún KALINA, si los hay, quedan listados en §4).
## 6. La mejor η dentro de la franja
{mejor_txt}
## 7. Lo que no se sabe
- La malla tiene paso 2.5 K en T_fuente y 0.025 en ε_cond: la franja está delimitada a esa resolución, no con precisión continua.
- Los puntos **fuera de rango** del motor de propiedades (líquido > 420 K) hay que tomarlos con pinzas; aquí T_fuente ≤ 410 K, pero los estados internos pueden superar ese valor.
- Solo se variaron T_fuente, ε_cond y T_sumidero: con las demás variables fijas en `comun.PROFESOR` no se dice nada sobre otras combinaciones.
"""


def main() -> None:
    t0 = time.perf_counter()
    filas = leer()
    if not filas:
        raise SystemExit(f"sin filas: falta {OUT_M5C / 'm5c_malla.csv'}")
    print(f"m5c_analisis | N={len(filas)} | OUT={OUT_M5C}", flush=True)
    fron = frontera(filas)
    escribir(OUT_M5C, "m5c_frontera.csv", CFRON, fron)
    mapa(filas)
    (OUT_M5C / "REPORTE_M5c.md").write_text(_doc(filas, fron), encoding="utf-8")
    print("REPORTE_M5c.md escrito", flush=True)
    print(f"m5c_analisis listo en {time.perf_counter() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
