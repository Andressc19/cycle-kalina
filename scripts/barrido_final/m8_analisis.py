"""M8 (ANECDÓTICO) — análisis: curvas, bloques del reporte y verificación.

Dibuja `m8_curvas.png` (2 x 5 paneles de η vs valor, coloreados por clase, franja
realista sombreada y línea en el valor de la base), imprime los bloques con cifras
para `REPORTE_M8.md` y comprueba conteos (160 filas = 2 bases x 5 variables x 16
valores, 9 realistas por grupo, resto en su base, piso de O2 por base) y que cada
línea de los bloques esté en el reporte si existe. Sale con 1 si algo falla.
FUERA DE [0.40, 0.95] NO ES REALISTAS: es ANECDÓTICO."""
import csv, os, sys, time  # noqa: E401,E402
from collections import Counter
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]
import matplotlib; matplotlib.use("Agg")  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from m4_tablas import gf, nf  # noqa: E402
from m8_corrida import bases  # noqa: E402

HUMO = os.environ.get("M8_HUMO") == "1"
OUT = _RAIZ / "resultados" / ("2026-10-07_final_M8_anecdotico/humo" if HUMO else "2026-10-07_final_M8_anecdotico")
VARIABLES = ("eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond")
VARS10 = ("T_fuente", "T_sumidero", "P_alta", "P_baja", "x_b", *VARIABLES)
VALORES = (0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.93, 0.95, 0.97, 0.98, 0.99)
HUMO_VAL, REAL = (0.20, 0.60, 0.99), (0.40, 0.95)
NUM = ("valor", "eta", "Wnet", "D", "m_O1", "m_O2", "m_O3", "m_O5", "T_amb_diseno", "t_s", *VARS10)
COLOR = {"KALINA": "#1a9850", "CORREGIBLE": "#f4a300", "INVIABLE": "#d73027", "NO_CONVERGIO": "#4d4d4d"}
FAL = 0

def chk(ok: bool, msg: str) -> None:
    global FAL
    FAL += 0 if ok else 1
    print(("OK    " if ok else "FALLO ") + msg, flush=True)

def leer() -> list:
    """Filas de `m8_oat.csv` con números y la marca realista tipados."""
    with open(OUT / "m8_oat.csv", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r.update({k: (float(r[k]) if r.get(k) not in (None, "") else None) for k in NUM})
        r["realista"] = r.get("realista") == "True"
    return rows

def claves(g: dict) -> list:
    """`(base, variable)` en orden B1..B2 y orden de VARIABLES."""
    nb = ("B1",) if HUMO else ("B1", "B2")
    return [(b, v) for b in nb for v in (VARIABLES[:1] if HUMO else VARIABLES) if (b, v) in g]

def grupos(rows: list) -> dict:
    """`(base, variable)` -> filas ordenadas por valor."""
    g = {}
    for r in rows:
        g.setdefault((r["base"], r["variable"]), []).append(r)
    for k in g:
        g[k].sort(key=lambda r: r["valor"])
    return g

def cuenta(filas: list, campo: str) -> str:
    """Conteo de una columna de etiquetas/códigos (clase o criterio)."""
    c = Counter()
    for r in filas:
        c.update(x for x in str(r.get(campo) or "").split(",") if x)
    return ", ".join(f"{k} x{n}" for k, n in sorted(c.items())) or "ninguno"

def zona(filas: list) -> str:
    """Extremos de η + clases + criterios + no convergencias de UNA zona."""
    if not filas:
        return "sin puntos"
    a, z = filas[0], filas[-1]
    nc = ", ".join(f'{r["valor"]:g}' for r in filas if r["clasificacion"] == "NO_CONVERGIO")
    return (f'η({a["valor"]:g})={nf(a["eta"], 4)}, η({z["valor"]:g})={nf(z["eta"], 4)}'
            f' | clases: {cuenta(filas, "clasificacion")} | criterios: '
            f'{cuenta(filas, "codigos_falla")} | NO_CONVERGIO: {nc or "ninguno"}')

def monotonia(filas: list) -> str:
    """Tramos con η creciente y detalle de cada bajada al subir el valor."""
    p = [(x, y) for x, y in zip(filas, filas[1:]) if x["eta"] is not None and y["eta"] is not None]
    if not p:
        return "sin pares evaluables"
    baj = [(x, y) for x, y in p if y["eta"] < x["eta"]]
    txt = f"{sum(1 for x, y in p if y['eta'] > x['eta'])}/{len(p)} tramos con η creciente"
    if not baj:
        return txt + "; ninguna bajada al subir el valor"
    det = "; ".join(f'{x["valor"]:g}→{y["valor"]:g} ({nf(x["eta"], 4)}→{nf(y["eta"], 4)})' for x, y in baj)
    return txt + f"; bajadas: {det}"

def conteos(rows: list, g: dict, bs: dict) -> None:
    """(1) Conteos y estructura del TASK_CONTEXT, derecho del CSV."""
    vals = list(HUMO_VAL if HUMO else VALORES)
    nb, nv = (1, 1) if HUMO else (2, 5)
    nreal = sum(1 for v in vals if REAL[0] <= v <= REAL[1])
    ok_g = all(len(v) == len(vals) and [r["valor"] for r in v] == vals and sum(r["realista"] for r in v) == nreal
               and all(r["realista"] == (REAL[0] <= r["valor"] <= REAL[1]) for r in v) for v in g.values())
    ok_b = all(abs(r[v] - (r["valor"] if v == r["variable"] else bs[r["base"]]["combo"][v])) <= 1e-9
               for r in rows for v in VARS10) and all(abs(r["T_amb_diseno"] - bs[r["base"]]["piso"]) <= 1e-9 for r in rows)
    chk(len(rows) == nb * nv * len(vals), f"filas: {len(rows)} == {nb} bases x {nv} variables x {len(vals)} valores")
    chk(len(g) == nb * nv and ok_g, f"{len(g)} grupos con {len(vals)} filas en orden y {nreal} realistas cada uno")
    chk(ok_b, f"en las {len(rows)} filas: la barrida vale su valor, el resto en la base y su piso de O2")

def bloques(rows: list, g: dict, bs: dict) -> list:
    """Las líneas con cifras listas para `REPORTE_M8.md` (§1 a §4)."""
    vals = list(HUMO_VAL if HUMO else VALORES)
    nreal = sum(1 for v in vals if REAL[0] <= v <= REAL[1])
    lin = ["=== §1 conteos y diseño ===",
           f'- {len(rows)} filas = {"1 base" if HUMO else "2 bases"} x {"1" if HUMO else "5"} variables x {len(vals)} '
           f'valores; {sum(r["realista"] for r in rows)} realistas y {sum(not r["realista"] for r in rows)} fuera de [0.40, 0.95].',
           f'- Por grupo: {len(vals)} puntos = {nreal} en [0.40, 0.95] + {sum(1 for v in vals if v < REAL[0])} por debajo '
           f'(0.20–0.35) + {sum(1 for v in vals if v > REAL[1])} por encima (0.97–0.99).',
           "- Clases en las filas: " + cuenta(rows, "clasificacion") + "."]
    for b in (("B1",) if HUMO else ("B1", "B2")):
        c = bs[b]["combo"]
        lin.append(f'- {b}: T_fuente={gf(c["T_fuente"], 6)} K, P_baja={gf(c["P_baja"], 6)} kPa, '
                   f'T_sumidero={gf(c["T_sumidero"], 6)} K, piso_O2={gf(bs[b]["piso"], 6)} K; bases '
                   + ", ".join(f'{v}={gf(c[v], 6)}' for v in VARIABLES) + ".")
    lin += ["", "=== §2 por base y variable ==="]
    for b, v in claves(g):
        f = g[(b, v)]
        lin += [f'- **{b} · {v}** — valor de la base {gf(bs[b]["combo"][v], 6)}',
                "  - dentro [0.40, 0.95]: " + zona([r for r in f if REAL[0] <= r["valor"] <= REAL[1]]),
                "  - fuera: " + zona([r for r in f if r["valor"] < REAL[0]]) + " | "
                + zona([r for r in f if r["valor"] > REAL[1]]),
                "  - monotonía: " + monotonia(f)]
    lin += ["", "=== §3 η y clase por punto (NC = sin convergencia) ===",
            "| base | variable | " + " | ".join(f"{v:g}" for v in vals) + " |", "|---|---|" + "---|" * len(vals)]
    for k in claves(g):
        m = {r["valor"]: r for r in g[k]}
        lin.append(f'| {k[0]} | {k[1]} | ' + " | ".join(("NC" if m[v]["eta"] is None else nf(m[v]["eta"], 4))
                   + "[" + m[v]["clasificacion"] + "]" for v in vals) + " |")
    lin += ["", "=== §4 comportamientos no monótonos o inesperados ==="]
    nc = [f'{b}·{v}: ' + ", ".join(f'{r["valor"]:g}' for r in g[(b, v)] if r["clasificacion"] == "NO_CONVERGIO") for b, v in claves(g) if any(r["clasificacion"] == "NO_CONVERGIO" for r in g[(b, v)])]
    lin.append("- Sin convergencia: " + ("; ".join(nc) if nc else "ninguna"))
    baj = [f'{b}·{v}: ' + monotonia(g[(b, v)]).split("; ", 1)[1] for b, v in claves(g) if "; bajadas:" in monotonia(g[(b, v)])]
    lin.append("- η que baja al subir el valor: " + ("; ".join(baj) if baj else "ninguna"))
    cam = [f'{b}·{v} ({cuenta(g[(b, v)], "clasificacion")})' for b, v in claves(g) if len({r["clasificacion"] for r in g[(b, v)]}) > 1]
    den = [f'{b}·{v} ({cuenta([r for r in g[(b, v)] if r["realista"]], "clasificacion")})' for b, v in claves(g)
           if len({r["clasificacion"] for r in g[(b, v)] if r["realista"]}) > 1]
    lin.append("- Clases: por serie " + ("; ".join(cam) if cam else "ningún cambio")
               + " | DENTRO de [0.40, 0.95] " + ("; ".join(den) if den else "ningún cambio"))
    fuera, esp = sum(not r["realista"] for r in rows), sum(1 for r in rows if not r["realista"] and r["clasificacion"] == "KALINA")
    lin.append(f"- KALINA con valor fuera de [0.40, 0.95] (parámetro irreal): {esp} de {fuera} filas")
    sup = []
    for b, v in claves(g):
        d = [r["eta"] for r in g[(b, v)] if r["realista"] and r["eta"] is not None]
        e = [(r["eta"], r["valor"]) for r in g[(b, v)] if not r["realista"] and r["eta"] is not None]
        if d and e and max(e)[0] > max(d):
            sup.append(f'{b}·{v}: η={nf(max(e)[0], 4)} en v={max(e)[1]:g} > máx dentro {nf(max(d), 4)}')
    lin.append("- η fuera de rango por encima del máximo de [0.40, 0.95]: " + ("; ".join(sup) if sup else "ninguna"))
    return lin

def figura(g: dict, bs: dict) -> None:
    """`m8_curvas.png` — 2 x 5 paneles: η vs valor, clase, franja y base."""
    fig, axs = plt.subplots(2, 5, figsize=(21, 8), sharex=True)
    for i, b in enumerate(("B1", "B2")):
        for j, v in enumerate(VARIABLES):
            ax, f = axs[i][j], g.get((b, v), [])
            ax.axvspan(*REAL, color="#bbbbbb", alpha=0.30, lw=0, zorder=0)
            ok = [(r["valor"], r["eta"]) for r in f if r["eta"] is not None]
            lo, amp = min((y for _, y in ok), default=0.0), (max((y for _, y in ok), default=1.0)
                          - min((y for _, y in ok), default=0.0)) or 1.0
            if ok:
                ax.plot([x for x, _ in ok], [y for _, y in ok], color="#999999", lw=1.0)
            for r in f:
                s = r["eta"] is None
                ax.plot(r["valor"], lo - 0.12 * amp if s else r["eta"], marker="x" if s else "o",
                        ms=7 if s else 5, mew=2 if s else 1, zorder=3, color=COLOR.get(r["clasificacion"], "#000000"))
            ax.axvline(bs[b]["combo"][v], color="#1f3864", ls="--", lw=1.2)
            ax.set_title(f"{b} · {v}", fontsize=10); ax.grid(alpha=0.3)
            if j == 0: ax.set_ylabel("η")
            if i == 1: ax.set_xlabel("valor")
    h = [plt.Line2D([], [], marker="o", ls="", color=c, label=k) for k, c in COLOR.items()]
    fig.legend(handles=h, loc="lower center", ncol=4)
    fig.suptitle("M8 ANECDÓTICO — η vs eficiencias y efectividades (fuera de [0.40, 0.95] NO es realista)", fontsize=13)
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    fig.savefig(OUT / "m8_curvas.png", dpi=150)
    plt.close(fig)

def main() -> None:
    t0 = time.perf_counter()
    rows = leer()
    if not rows: raise SystemExit(f"sin filas: falta {OUT / 'm8_oat.csv'}")
    g, bs = grupos(rows), bases()
    figura(g, bs)
    bqs = bloques(rows, g, bs)
    print("\n".join(bqs), flush=True)
    print("\n=== verificación (TASK_CONTEXT §Pasos 4) ===", flush=True)
    conteos(rows, g, bs)
    p = OUT / "REPORTE_M8.md"
    if p.exists():
        txt = p.read_text(encoding="utf-8", errors="replace")
        mal = [l for l in bqs if l.strip() and l not in txt]
        chk(not mal, f"las {sum(1 for l in bqs if l.strip())} líneas con cifras de los bloques "
            f"están en REPORTE_M8.md" + (f" -> {mal[:2]}" if mal else ""))
    else:
        print(f"SKIP    {p.name} no existe todavía (repetir tras escribirlo)", flush=True)
    print(f"FIN: {FAL} fallo(s); análisis en {time.perf_counter() - t0:.0f} s -> {OUT}", flush=True)
    sys.exit(1 if FAL else 0)

if __name__ == "__main__":
    main()
