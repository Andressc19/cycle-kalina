"""Diagnostico del salto del solver en (x_b=0.60, P_alta=4000, T_fuente=394) — Parte B de la
tarea 2026-09-24-verificacion-motor-real-y-salto-solver. SOLO TeqpAdapter.

Barrido fino de P_baja (paso 0.25 kPa, ±5 kPa) y, en las dos P del salto, F(T1) en malla de
1 K con `evaluar`, raices por brentq, la eleccion de _bracketear y clasificacion de cada
raiz con evaluar_ciclo(T_amb_diseno=283.15); escanea otros saltos en evaluaciones_margen.csv.
No modifica src/ ni archivos: salidas salto_barrido_fino.csv, salto_F_T1.csv, run_B.log y la
seccion B del reporte (B4 se anade a mano tras la corrida).
"""
from __future__ import annotations
import csv, sys, time
from pathlib import Path
from scipy.optimize import brentq
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "scripts"))
from calibracion_elsayed_malla import ETA_P, ETA_T, M_B, T_SUMIDERO  # noqa: E402
from src._cycle_loops import CicloNoConvergeError, _bracketear, evaluar  # noqa: E402
from src.cycle_solver import resolver_ciclo  # noqa: E402
from src.properties.adapter import PropertyRangeError  # noqa: E402
from src.properties.teqp_adapter import TeqpAdapter  # noqa: E402
from src.restricciones import evaluar_ciclo  # noqa: E402

OUT_DIR = REPO / "resultados" / "2026-09-24_verificacion"
EVALS_CSV = REPO / "resultados" / "2026-09-24_margen2k" / "evaluaciones_margen.csv"
REPO_MD = OUT_DIR / "REPORTE_VERIFICACION.md"
X_B, P_ALTA, T_FUENTE = 0.60, 4000.0, 394.0
EPS = (0.85, 0.80, 0.85)                   # eps_hrvg, eps_reg, eps_cond FIJOS
T_AMB_DISENO, PASO, RADIO, XTOL = 283.15, 0.25, 5.0, 1e-4
EXC_CATCH = (CicloNoConvergeError, PropertyRangeError, ValueError, RuntimeError,
             NotImplementedError)
FINO_COLS = ("P_baja", "T1", "T2", "q2", "fase2", "m3", "eta", "Wnet", "T9", "error")
F_COLS = ("P_baja", "T1", "F", "error")
KW = dict(P_alta=P_ALTA, T_fuente=T_FUENTE, T_sumidero=T_SUMIDERO, x_b=X_B,
          m_b=M_B, eta_t=ETA_T, eta_p=ETA_P, eps_hrvg=EPS[0], eps_reg=EPS[1],
          eps_cond=EPS[2], tol_T10=1e-3, max_iter_frio=300)
log = lambda m: print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)  # noqa: E731

def puntos_salto():
    filas = []
    for f in csv.DictReader(open(EVALS_CSV, encoding="utf-8")):
        try:
            if (float(f["x_b"]) == X_B and float(f["P_alta"]) == P_ALTA
                    and float(f["T_fuente"]) == T_FUENTE and f.get("eta")):
                filas.append((float(f["P_baja"]), float(f["eta"]),
                              float(f["T9_amb"]), float(f["Wnet"])))
        except (KeyError, ValueError):
            continue
    filas.sort()
    pares = []
    for (p1, e1, t1, _w1), (p2, e2, t2, _w2) in zip(filas, filas[1:]):
        if abs(e1 - e2) > 0.02:
            pares.append((abs(p1 - p2), p1, e1, t1, p2, e2, t2))
    if not pares:
        raise RuntimeError("no se encontro el salto de eta en evaluaciones_margen.csv")
    return min(pares, key=lambda r: r[0])

def construir_F(backend, P_baja):
    ultimo_T10 = [None]

    def F(T1):
        T1_nuevo, estados, _ = evaluar(T1, backend, P_baja=P_baja, **KW,
                                       T10_inicial=ultimo_T10[0])
        ultimo_T10[0] = estados["e10"].T
        return T1_nuevo - T1
    return F

def clasificar_raiz(backend, T1_sol, P_baja):
    _, estados, energias = evaluar(T1_sol, backend, P_baja=P_baja, **KW)
    Wnet = energias["Wt"] - energias["Wp"]
    res = dict(estados=estados, **energias, Wnet=Wnet, eta=Wnet / energias["Qi"])
    val = evaluar_ciclo(backend, res, P_alta=P_ALTA, P_baja=P_baja,
                        T_fuente=T_FUENTE, T_sumidero=T_SUMIDERO, x_b=X_B,
                        m_b=M_B, eps_hrvg=EPS[0], eps_reg=EPS[1],
                        eps_cond=EPS[2], T_amb_diseno=T_AMB_DISENO)
    return res, val

def malla_F(backend, P_baja):
    """F(T1) en malla de 1 K; reutiliza filas previas salto_F_T1.csv (reanudacion)."""
    path = OUT_DIR / "salto_F_T1.csv"
    if path.exists():
        viejas = [f for f in csv.DictReader(open(path, encoding="utf-8"))
                  if abs(float(f["P_baja"]) - P_baja) < 1e-9]
        if viejas:
            F = construir_F(backend, P_baja)
            brackets, prev, punta = [], None, 0.0
            for f in viejas:
                if f["error"]:
                    prev, punta = None, float(f["T1"])
                    continue
                v = float(f["F"])
                if prev is not None and prev * v < 0.0:
                    brackets.append((punta, float(f["T1"])))
                punta, prev = float(f["T1"]), v
            log(f"F(T1) P_baja={P_baja}: reutilizando {len(viejas)} pts de {path.name}, "
                f"{len(brackets)} cambios de signo {brackets}")
            return F, brackets
    F = construir_F(backend, P_baja)
    filas, T1 = [], round(T_SUMIDERO + 1.0, 1)
    while T1 <= T_FUENTE - 1.0 + 1e-9:
        f = dict(P_baja=P_baja, T1=T1, F="", error="")
        try:
            f["F"] = round(F(T1), 6)
        except EXC_CATCH as exc:
            f["error"] = f"{type(exc).__name__}: {exc}"
        filas.append(f)
        T1 = round(T1 + 1.0, 1)
    with open(OUT_DIR / "salto_F_T1.csv", "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=F_COLS)
        fh.tell() == 0 and w.writeheader()
        w.writerows(filas)
    brackets, prev, punta = [], None, 0.0
    for f in filas:
        if f["error"]:
            prev, punta = None, float(f["T1"])
            continue
        v = float(f["F"])
        if prev is not None and prev * v < 0.0:
            brackets.append((punta, float(f["T1"])))
        punta, prev = float(f["T1"]), v
    log(f"F(T1) P_baja={P_baja}: {len(filas)} pts, {sum(1 for f in filas if f['error'])} "
        f"errores, {len(brackets)} cambios de signo {brackets}")
    return F, brackets

def analizar_p(backend, P_baja):
    F, brackets = malla_F(backend, P_baja)
    try:
        lo, hi = _bracketear(F, T_SUMIDERO, T_FUENTE)
        brent_elige = brentq(F, lo, hi, xtol=XTOL)
        log(f"  _bracketear -> [{lo:.1f}, {hi:.1f}] K; brentq (como resolver_ciclo) "
            f"elige T1={brent_elige:.4f} K")
    except EXC_CATCH as exc:
        brent_elige = None
        log(f"  _bracketear no cierra bracket: {type(exc).__name__}: {exc}")
    for a, b in brackets:
        try:
            T1_sol = brentq(F, a, b, xtol=XTOL) if a != b else a
            res, val = clasificar_raiz(backend, T1_sol, P_baja)
            e = res["estados"]
            print(f"  raiz T1={T1_sol:.4f} K  eta={res['eta']:.6f} Wnet={res['Wnet']:.2f} "
                  f"T2={e['e2'].T:.3f} m3={e['e3'].m:.4f} "
                  f"clasif={val.clasificacion.value} "
                  f"fallas={','.join(x.codigo for x in val.fallas) or '-'}", flush=True)
        except EXC_CATCH as exc:
            print(f"  raiz [{a}, {b}]: {type(exc).__name__}: {exc}", flush=True)
    return brent_elige

def barrido_fino(backend):
    _, plo, _elo, _tlo, phi, _ehi, _thi = puntos_salto()
    path = OUT_DIR / "salto_barrido_fino.csv"
    if path.exists():
        filas = list(csv.DictReader(open(path, encoding="utf-8")))
        log(f"barrido fino: reutilizando {len(filas)} pts de {path.name}")
        return filas
    mid, filas = (plo + phi) / 2.0, []
    P = round(mid - RADIO, 2)
    while P <= mid + RADIO + 1e-9:
        f = dict(P_baja=round(P, 6), T1="", T2="", q2="", fase2="", m3="",
                 eta="", Wnet="", T9="", error="")
        try:
            res = resolver_ciclo(backend, P_alta=P_ALTA, P_baja=P,
                                 T_fuente=T_FUENTE, T_sumidero=T_SUMIDERO,
                                 x_b=X_B, m_b=M_B, eta_t=ETA_T, eta_p=ETA_P,
                                 eps_hrvg=EPS[0], eps_reg=EPS[1], eps_cond=EPS[2])
            e = res["estados"]
            fase2, q2 = backend.fase_de(P_ALTA, e["e2"].T, X_B)
            f.update(T1=round(e["e1"].T, 6), T2=round(e["e2"].T, 6),
                     q2=round(q2, 6), fase2=fase2, m3=round(e["e3"].m, 6),
                     eta=round(res["eta"], 6), Wnet=round(res["Wnet"], 4),
                     T9=round(e["e9"].T, 6))
        except EXC_CATCH as exc:
            f["error"] = f"{type(exc).__name__}: {exc}"
        filas.append(f)
        P = round(P + PASO, 2)
    with open(OUT_DIR / "salto_barrido_fino.csv", "w", newline="",
              encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FINO_COLS)
        w.writeheader(); w.writerows(filas)
    log(f"barrido fino: {len(filas)} pts, "
        f"{sum(1 for f in filas if not f['error'])} resueltos, "
        f"rango [{filas[0]['P_baja']}, {filas[-1]['P_baja']}]")
    return filas

def otros_saltos():
    por = {}
    for f in csv.DictReader(open(EVALS_CSV, encoding="utf-8")):
        try:
            if not f.get("eta"):
                continue
            k = (float(f["x_b"]), float(f["P_alta"]), float(f["T_fuente"]))
            por.setdefault(k, []).append((float(f["P_baja"]), float(f["eta"])))
        except (KeyError, ValueError):
            continue
    saltos = []
    for (xb, pa, tf), filas in sorted(por.items()):
        filas.sort()
        for (p1, e1), (p2, e2) in zip(filas, filas[1:]):
            if abs(p2 - p1) < 5.0 and abs(e1 - e2) > 0.02:
                saltos.append((xb, pa, tf, p1, e1, p2, e2, p2 - p1, e2 - e1))
    log(f"otros saltos |dP|<5 kPa y |deta|>0.02 en evaluaciones_margen: {len(saltos)}")
    for s in saltos:
        log(f"  ({s[0]},{s[1]:.0f},{s[2]:.0f}) P {s[3]:.3f}->{s[5]:.3f} "
            f"eta {s[4]:.4f}->{s[6]:.4f}")
    return saltos

def generar_reporte(finos, brent_elige, saltos_otros):
    _, plo, elo, tlo, phi, ehi, thi = puntos_salto()
    T = lambda hd, filas: ("| " + " | ".join(hd) + " |\n" + "|" + "---|" * len(hd)
                           + "\n" + ("\n".join("| " + " | ".join(f) + " |"
                                               for f in filas) if filas else "—"))  # noqa: E731
    v_ = lambda x: "-" if x in ("", None) else str(x)  # noqa: E731
    f_ = lambda f: (str(f["P_baja"]), v_(f["T1"]), v_(f["T2"]), v_(f["q2"]),
                    v_(f["fase2"]), v_(f["m3"]), v_(f["eta"]), v_(f["Wnet"]),
                    v_(f["T9"]))  # noqa: E731
    sec = [
        "# Reporte — Verificacion del salto del solver y del motor real (2026-09-24)",
        "## Parte B — Diagnostico del salto en (x_b=0.60, P_alta=4000, T_fuente=394)",
        f"Par del salto (evaluaciones_margen.csv): P={plo:.6f} kPa (eta={elo:.4f}) ↔ "
        f"P={phi:.6f} kPa (eta={ehi:.4f}); dP={phi - plo:.4f} kPa, deta={ehi - elo:.4f}; "
        f"T9_amb salta {tlo:.4f} -> {thi:.4f} K.",
        f"### B1. Barrido fino de P_baja (±{RADIO:.0f} kPa, paso {PASO} kPa)",
        T(("P_baja", "T1", "T2", "q2", "fase2", "m3", "eta", "Wnet", "T9"),
          [f_(f) for f in finos]),
        "### B2. F(T1) por malla (paso 1 K) y raices",
        f"Rango de T1: {T_SUMIDERO + 1.0:.0f} a {T_FUENTE - 1.0:.0f} K. Malla completa en "
        "salto_F_T1.csv; las raices detectadas por cambio de signo y su clasificacion "
        "quedan en run_B.log. Raiz que elegiria resolver_ciclo via _bracketear: "
        f"{brent_elige}.",
        "### B3. Otros saltos |deta|>0.02 con |dP|<5 kPa en evaluaciones_margen.csv",
        T(("x_b", "P_alta", "T_fuente", "P1", "eta1", "P2", "eta2", "dP", "deta"),
          [(f"{s[0]}", f"{s[1]:.0f}", f"{s[2]:.0f}", f"{s[3]:.6f}", f"{s[4]:.4f}",
            f"{s[5]:.6f}", f"{s[6]:.4f}", f"{s[7]:.3f}", f"{s[8]:.4f}")
           for s in saltos_otros]),
        "<!-- SECCION_A -->",
    ]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPO_MD.write_text("\n\n".join(sec) + "\n", encoding="utf-8")

def principal():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    plo, phi = puntos_salto()[1], puntos_salto()[4]  # indices: (dP, P_lo, eta_lo, T9lo, P_hi, eta_hi, T9hi)
    log(f"Parte B: x_b={X_B} P_alta={P_ALTA:.0f} T_fuente={T_FUENTE:.0f}; "
        f"salto P {plo:.3f} <-> {phi:.3f}")
    t0, backend = time.time(), TeqpAdapter(x=X_B)
    finos = barrido_fino(backend)
    eliges = [analizar_p(backend, P) for P in (plo, phi)]
    saltos_otros = otros_saltos()
    generar_reporte(finos, eliges, saltos_otros)
    log(f"Parte B completa en {time.time() - t0:.0f}s")

if __name__ == "__main__":
    principal()