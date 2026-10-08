"""M7 — análisis: óptimos por arranque, convergencia y bloques del reporte.

Lee los CSV de M7 sin recalcular el ciclo, escribe `m7_optimos.csv`, dibuja
`m7_convergencia.png` e imprime los bloques listos para `REPORTE_M7.md`.
Formatos `nf`/`gf` de `m4_tablas.py`: `m7_verificar.py` recalcula cada cifra
desde los CSV con esas mismas funciones y exige que el reporte coincida.
"""
from __future__ import annotations

import csv, os, re, sys, time  # noqa: E401,E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from m4_tablas import gf, nf  # noqa: E402

HUMO = os.environ.get("M7_HUMO") == "1"
OUT = _RAIZ / "resultados" / ("2026-10-07_final_M7/humo" if HUMO
                              else "2026-10-07_final_M7")
# Caja de TASK_CONTEXT final_M7, fijas de cada arranque y formatos.
CAJA = {"T_fuente": (380.0, 500.0), "T_sumidero": (278.15, 303.55),
        "P_alta": (2000.0, 5000.0), "P_baja": (300.0, 2500.0),
        "x_b": (0.50, 0.85), "eta_t": (0.40, 0.95), "eta_p": (0.40, 0.95),
        "eps_hrvg": (0.40, 0.95), "eps_reg": (0.40, 0.95),
        "eps_cond": (0.40, 0.95)}
VARS10 = tuple(CAJA)
FIJAS = {"A1": (), "A2": (), "A3": ("T_fuente", "T_sumidero"),
         "A4": ("P_alta", "P_baja", "T_sumidero"), "A5": ("T_fuente", "x_b")}
MARG = ("m_O1", "m_O2", "m_O5")
NUM = ("iteracion", "paso", "eta", "Wnet", "D", *MARG, "t_s", *VARS10)
BOOL = ("fuera_rango", "B_verificado")
COPT = ["arranque", "clasificacion", "D", "eta", "Wnet", *VARS10, *MARG,
        "fuera_rango", "B_verificado", "iteraciones", "evaluaciones"]
CONSERVA = {
    "A1": "nada (libre total; parte del mejor KALINA de M4b)",
    "A2": "nada (libre total; parte del mejor KALINA de M2S, B2 a 278.15 K)",
    "A3": "sus temperaturas: T_fuente 623.15 K y T_sumidero 300.032917 K",
    "A4": "sus presiones: P_alta 3000 kPa, P_baja 400 kPa, más T_sumidero",
    "A5": "su fuente y su x_b: T_fuente 623.15 K y x_b 0.50"}
CAB3 = ("| Arranque | Qué conserva del profesor | η inicial | η óptima | "
        "P_alta (kPa) | P_baja (kPa) | dP (kPa) | rP | T_fuente (K) | "
        "T_sumidero (K) | x_b | η_t | η_p | ε_HRVG | ε_reg | ε_cond |")


def leer(nombre: str) -> list:
    """Filas de `OUT/nombre` con números y booleanos ya tipados."""
    with open(OUT / nombre, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r.update({k: float(r[k]) for k in NUM if r.get(k) not in (None, "")})
        r.update({k: None if r.get(k) in (None, "") else r[k] == "True"
                  for k in BOOL})
    return rows


def por_arranque(tray: list) -> dict:
    """`{arranque: [filas aceptadas en el orden del CSV]}`."""
    g = {}
    for r in tray:
        g.setdefault(r["arranque"], []).append(r)
    return g


def optimos(tray: list, ev: list) -> list:
    """Una fila de óptimo por arranque: su último punto aceptado."""
    n_ev = {}
    for r in ev:
        n_ev[r["arranque"]] = n_ev.get(r["arranque"], 0) + 1
    out = []
    for a, filas in por_arranque(tray).items():
        o = dict(filas[-1])
        o["iteraciones"], o["evaluaciones"] = int(max(
            f["iteracion"] for f in filas)), n_ev.get(a, 0)
        out.append(o)
    return out


def escribir_optimos(opts: list) -> None:
    """`m7_optimos.csv`: 10 variables, η, W_net, márgenes y verificación."""
    with open(OUT / "m7_optimos.csv", "w", encoding="utf-8", newline="") as fh:
        esc = csv.DictWriter(fh, fieldnames=COPT)
        esc.writeheader()
        esc.writerows({c: o.get(c) for c in COPT} for o in opts)
    print(f"m7_optimos.csv: {len(opts)} filas", flush=True)


def tabla_optimos(opts: list, ini: dict) -> str:
    """§3 — la tabla de óptimos; `ini[arranque]` es su fila de iteración 0."""
    lin = [CAB3, "|---|" * 16]
    for o in opts:
        i, pa, pb = ini[o["arranque"]], o["P_alta"], o["P_baja"]
        lin.append(
            f'| {o["arranque"]} | {CONSERVA[o["arranque"]]} | {nf(i["eta"], 4)}'
            f' | {nf(o["eta"], 4)} | {nf(pa, 1)} | {nf(pb, 1)} | '
            f'{nf(pa - pb, 1)} | {nf(pa / pb, 3)} | {nf(o["T_fuente"], 2)} | '
            f'{nf(o["T_sumidero"], 2)} | {nf(o["x_b"], 4)} | '
            + " | ".join(nf(o[v], 3) for v in
                         ("eta_t", "eta_p", "eps_hrvg", "eps_reg", "eps_cond"))
            + " |")
    return "\n".join(lin)


def donde(o: dict, v: str) -> str:
    """`fija` si el arranque la tiene fija; si no, en qué borde de la caja."""
    if v in FIJAS[o["arranque"]]:
        return "fija (no se mueve)"
    u = (o[v] - CAJA[v][0]) / (CAJA[v][1] - CAJA[v][0])
    return ("borde inferior" if u <= 0.01 else
            "borde superior" if u >= 0.99 else "dentro de la caja")


def tabla_empuje(opts: list, ini: dict) -> str:
    """§4 — de dónde viene cada variable y dónde queda su óptimo."""
    lin = ["| Arranque | Variable | Inicial | Óptimo | Dónde queda |",
           "|---|---|---|---|---|"]
    for o in opts:
        i = ini[o["arranque"]]
        for v in VARS10:
            lin.append(f'| {o["arranque"]} | {v} | {gf(i[v], 6)} | '
                       f'{gf(o[v], 6)} | {donde(o, v)} |')
    return "\n".join(lin)


def criterios(opts: list) -> list:
    """§4 — el margen de O1/O2/O5 más pequeño de cada óptimo (el que activa)."""
    out = []
    for o in opts:
        m = {k[2:]: o[k] for k in MARG}          # {"O1": m_O1, ...}
        act = min(m, key=lambda k: m[k] if m[k] is not None else float("inf"))
        out.append(f'- **{o["arranque"]}** — criterio activo en el óptimo: '
                   f'**{act}** margen {nf(m[act], 4)} (O1 {nf(m["O1"], 4)}, O2 {nf(m["O2"], 4)}, O5 {nf(m["O5"], 4)}).')
    return out


def figura(grupo: dict) -> None:
    """`m7_convergencia.png` — η contra la iteración, una línea por arranque."""
    fig, ax = plt.subplots(figsize=(9, 5))
    for a, filas in grupo.items():
        ax.plot([f["iteracion"] for f in filas], [f["eta"] for f in filas],
                marker="o", ms=4, lw=1.3, label=a)
    ax.set(xlabel="iteración", ylabel="η", title="M7 — convergencia de η")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "m7_convergencia.png", dpi=150)
    plt.close(fig)


def resumen(opts: list, ini: dict, ev: list) -> None:
    """Los bloques listos para pegar en `REPORTE_M7.md` (§3 a §8)."""
    g = {o["arranque"]: o for o in opts}
    print("\n=== §3 tabla de óptimos ===\n" + tabla_optimos(opts, ini))
    print("\n=== §4 empuje de cada variable ===\n" + tabla_empuje(opts, ini))
    print("\n=== §4 criterio activo ===\n" + "\n".join(criterios(opts)))
    bords = [f'{o["arranque"]} {v} = {gf(o[v], 6)}' for o in opts
             for v in VARS10 if donde(o, v).startswith("borde")]
    print("\n=== §5 bordes ===\n" + (", ".join(bords) or "ninguno"))
    b = (OUT / "stdout.txt").read_bytes() if (OUT / "stdout.txt").exists() else b""
    m = re.findall(r"fin: (\d+) s", b.decode("utf-8", "replace").replace("\x00", ""))
    print(f'\n=== §6 tiempos ===\npared: {m[-1] if m else "n/d"} s | total evaluaciones: {len(ev)}')
    for o in opts:
        s = sum(r["t_s"] for r in ev
                if r["arranque"] == o["arranque"] and r.get("t_s"))
        print(f'{o["arranque"]}: {o["evaluaciones"]} evaluaciones, '
              f'{o["iteraciones"]} iteraciones, {nf(s, 0)} s de suma')
    lib = [g[a] for a in ("A1", "A2") if a in g]
    best = max(opts, key=lambda o: o["eta"] if o["eta"] is not None else -1.0)
    print("\n=== §7 conclusión ===")
    if lib:
        b = max(lib, key=lambda o: o["eta"] if o["eta"] is not None else -1.0)
        print(f'1. sin restricciones: {b["arranque"]} eta={nf(b["eta"], 4)}')
    print("\n".join(f'2. {a} ({CONSERVA[a]}): eta={nf(g[a]["eta"], 4)}'
                    for a in ("A3", "A4", "A5") if a in g))
    print(f'mejor global: {best["arranque"]} eta={nf(best["eta"], 4)} ({best["clasificacion"]})')
    print("\n=== §8 fuera_rango en el óptimo ===\n"
          + (", ".join(o["arranque"] for o in opts if o["fuera_rango"]) or "ninguno"))


def main() -> None:
    t0 = time.perf_counter()
    tray, ev = leer("m7_trayectorias.csv"), leer("m7_evaluaciones.csv")
    if not tray:
        raise SystemExit(f"sin filas: falta {OUT / 'm7_trayectorias.csv'}")
    grp = por_arranque(tray)
    opts = optimos(tray, ev)
    escribir_optimos(opts)
    figura(grp)
    resumen(opts, {a: f[0] for a, f in grp.items()}, ev)
    print(f"m7_analisis listo en {time.perf_counter() - t0:.0f} s -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
