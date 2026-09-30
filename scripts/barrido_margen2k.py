"""P_baja por BUSQUEDA DE RAIZ del margen O2 = 2 K (tarea 2026-09-24-pbaja-margen-2k):
brentq sobre margen(P) = T_bur(P,x_b) - T9_amb(P), T9_amb = re-solucion del condensador tal cual
el criterio O2 (operativos.py); identico en malla/eps/parametros a barrido_eps_fijos_085.
Solo TeqpAdapter; reanudable por CSV; todas las evaluaciones de margen(P) van a
evaluaciones_margen.csv. No modifica archivos existentes."""
from __future__ import annotations
import csv, sys, time
from collections import Counter
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "scripts"))
from calibracion_elsayed_malla import ETA_P, ETA_T, M_B, T_SUMIDERO  # noqa: E402
from calibracion_pinch import calibrar_P_baja  # noqa: E402
from src._cycle_loops import CicloNoConvergeError  # noqa: E402
from src.components import condensador  # noqa: E402
from src.cycle_solver import resolver_ciclo  # noqa: E402
from src.properties.adapter import PropertyRangeError  # noqa: E402
from src.properties.teqp_adapter import TeqpAdapter  # noqa: E402
from src.restricciones import Clasificacion, evaluar_ciclo  # noqa: E402
OUT_DIR = REPO / "resultados" / "2026-09-24_margen2k"
CSV_PATH = OUT_DIR / "barrido_margen2k.csv"
EVAL_PATH = OUT_DIR / "evaluaciones_margen.csv"
REPORTE_PATH = OUT_DIR / "REPORTE_MARGEN2K.md"
OLD_PATH = REPO / "resultados" / "2026-09-23_eps_fijos_085" / "barrido_eps_fijos_085.csv"
PINCH, T_AMB_DISENO = 6.0, 283.15          # P_0 (viejos NO_CONV/sin P_baja); piso del criterio O2
EPS = (0.85, 0.80, 0.85)                   # eps_hrvg, eps_reg, eps_cond FIJOS
MARGEN_OBJ, XTOL, PASO, MAX_PASOS = 2.0, 0.5, 40.0, 10
P_MIN = 50.0                               # kPa; limite superior = 0.5 * P_alta
T_AMB_EVAL = max(T_SUMIDERO, T_AMB_DISENO)
XBS, P_ALTAS, T_FUENTES = (0.60, 0.65, 0.70, 0.75, 0.80), (3000.0, 4000.0, 5000.0), (394.0, 423.0)
COLS = ("x_b", "P_alta", "T_fuente", "P_baja", "pbaja_encontrada", "n_evaluaciones", "T9_amb", "T_bur", "margen_O2", "convergio", "clasificacion", "eta", "Wnet", "fallas", "detalle_error")
EVAL_COLS = ("x_b", "P_alta", "T_fuente", "P_baja", "T9_amb", "T_bur", "margen", "eta", "Wnet", "error")
EXC_CATCH = (CicloNoConvergeError, PropertyRangeError, ValueError, RuntimeError, NotImplementedError)
NOCONV = Clasificacion.NO_CONVERGIO.value
CLAVE = lambda f: (float(f["x_b"]), float(f["P_alta"]), float(f["T_fuente"]))  # noqa: E731
ES = lambda f, c: float(f[c]) if f.get(c) not in ("", None) else None  # noqa: E731
v = lambda x: "-" if x is None else f"{x:g}"  # noqa: E731

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def evaluar_margen(backend, x_b, P_alta, T_fuente, P):
    ev = dict(x_b=x_b, P_alta=P_alta, T_fuente=T_fuente, P_baja=round(P, 6), T9_amb="", T_bur="",
              margen="", eta="", Wnet="", error="")
    try:
        res = resolver_ciclo(backend, P_alta=P_alta, P_baja=P, T_fuente=T_fuente, T_sumidero=T_SUMIDERO,
                             x_b=x_b, m_b=M_B, eta_t=ETA_T, eta_p=ETA_P, eps_hrvg=EPS[0],
                             eps_reg=EPS[1], eps_cond=EPS[2])
        T9_amb = condensador.resolver(res["estados"]["e8"], backend, T_sumidero=T_AMB_EVAL, eps=EPS[2], m=M_B)[0].T
        T_bur = backend.bubble_point(P, x_b)
    except EXC_CATCH as exc:
        ev["error"] = f"{type(exc).__name__}: {exc}"
        return ev, None
    ev.update(T9_amb=round(T9_amb, 6), T_bur=round(T_bur, 6), margen=round(T_bur - T9_amb, 6),
              eta=round(res["eta"], 6), Wnet=round(res["Wnet"], 4))
    return ev, res

def f_margen(backend, x_b, P_alta, T_fuente, evals, P):
    ev, _ = evaluar_margen(backend, x_b, P_alta, T_fuente, P)
    evals.append(ev)
    if ev["error"]:
        raise RuntimeError(f"evaluacion de margen abortada: {ev['error']}")
    return float(ev["margen"]) - MARGEN_OBJ

def buscar_P_estrella(backend, x_b, P_alta, T_fuente, P_a, evals):
    f = lambda P: f_margen(backend, x_b, P_alta, T_fuente, evals, P)  # noqa: E731
    fa = f(P_a)
    if fa == 0.0:
        return P_a
    P_lo, P_hi = P_MIN, 0.5 * P_alta
    subir = fa < 0                              # margen<2 -> subir; margen>2 -> bajar
    a, b, fb = P_a, P_a, fa
    for _ in range(MAX_PASOS):
        b = min(b + PASO, P_hi) if subir else max(b - PASO, P_lo)
        fb = f(b)
        if (fb > 0 and subir) or (fb < 0 and not subir) or b in (P_hi, P_lo):
            break
    if (fb < 0) == subir:                       # mismo signo: sin cruce del margen 2 K
        d_, val = ("llega a", "max") if subir else ("baja a", "min")
        raise RuntimeError(f"margen no {d_} 2 K hasta P={b:g} (margen {val} {fb + MARGEN_OBJ:.3g} K)")
    return b if fb == 0.0 else brentq(f, min(a, b), max(a, b), xtol=XTOL)

def resolver_punto(backend, x_b, P_alta, T_fuente, viejo):
    fila = dict(x_b=x_b, P_alta=P_alta, T_fuente=T_fuente, P_baja="", pbaja_encontrada=False,
                n_evaluaciones=0, T9_amb="", T_bur="", margen_O2="", convergio=False,
                clasificacion=NOCONV, eta="", Wnet="", fallas="", detalle_error="")
    evals, P_star = [], None
    try:
        if viejo is not None and viejo.get("clasificacion") != NOCONV and ES(viejo, "P_baja") is not None:
            P_a = ES(viejo, "P_baja")
        else:
            P_a = calibrar_P_baja(backend, x_b, P_alta, PINCH)
        P_star = buscar_P_estrella(backend, x_b, P_alta, T_fuente, P_a, evals)
        fila.update(pbaja_encontrada=True, P_baja=round(P_star, 6))
        ev_f, res = evaluar_margen(backend, x_b, P_alta, T_fuente, P_star)
        evals.append(ev_f)
        if ev_f["error"]:
            fila["detalle_error"] = ev_f["error"]
        else:
            fila.update(T9_amb=ev_f["T9_amb"], T_bur=ev_f["T_bur"], margen_O2=ev_f["margen"],
                        eta=ev_f["eta"], Wnet=ev_f["Wnet"])
            try:
                val = evaluar_ciclo(backend, res, P_alta=P_alta, P_baja=P_star,
                                    T_fuente=T_fuente, T_sumidero=T_SUMIDERO, x_b=x_b,
                                    m_b=M_B, eps_hrvg=EPS[0], eps_reg=EPS[1],
                                    eps_cond=EPS[2], T_amb_diseno=T_AMB_DISENO)
                fila.update(convergio=True, clasificacion=val.clasificacion.value,
                            fallas=",".join(x.codigo for x in val.fallas))
            except EXC_CATCH as exc:
                fila["detalle_error"] = f"{type(exc).__name__}: {exc}"
    except EXC_CATCH as exc:
        fila["detalle_error"] = (f"{type(exc).__name__}: {exc}" if not fila["detalle_error"]
                                 else fila["detalle_error"] + " | " + f"{type(exc).__name__}: {exc}")
        if evals:
            ue = evals[-1]
            fila["P_baja"] = ue["P_baja"]
            if ue["margen"] != "":
                fila.update(T9_amb=ue["T9_amb"], T_bur=ue["T_bur"], margen_O2=ue["margen"])
    fila["n_evaluaciones"] = len(evals)
    return fila, evals

def _cargar(path: Path, lista: bool = False) -> dict:
    d: dict = {}
    if path.exists():
        for fila in csv.DictReader(open(path, "r", newline="", encoding="utf-8")):
            try:
                if lista:
                    d.setdefault(CLAVE(fila), []).append(fila)
                else:
                    d[CLAVE(fila)] = fila
            except (KeyError, ValueError):
                continue
    return d

def cargar_todas():
    d = _cargar(CSV_PATH)
    return set(d), list(d.values())

def escribir_fila(fila: dict, evals: list, done: set) -> set:
    for path, cols, rows in ((CSV_PATH, COLS, [fila]), (EVAL_PATH, EVAL_COLS, evals)):
        nuevo = not path.exists()
        with open(path, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            nuevo and w.writeheader()
            w.writerows(rows)
    done.add(CLAVE(fila))
    return done

def _pendiente(P, Y):
    if len(P) < 2 or len(set(P)) < 2:
        return None
    try:
        return float(np.polyfit(P, Y, 1)[0])
    except Exception:
        return None

def generar_reporte(todas: list) -> None:
    n = len(todas)
    enc = [f for f in todas if str(f.get("pbaja_encontrada")) == "True"]
    c_clas = Counter(f["clasificacion"] for f in todas)
    k = sorted((f for f in todas if f.get("clasificacion") == "KALINA"), key=lambda f: -float(f["eta"]))
    b = Counter(cod for f in todas for cod in (f.get("fallas") or "").split(",") if cod)
    b[NOCONV] = sum(1 for f in todas if f["clasificacion"] == NOCONV and str(f.get("pbaja_encontrada")) == "True")
    b["SIN_P*"] = n - len(enc)
    viejos, evs = _cargar(OLD_PATH), _cargar(EVAL_PATH, lista=True)
    comp, dpbs, d_et = [], [], []
    for f in todas:
        o = viejos.get(CLAVE(f))
        if not o:
            continue
        pb_o, pb_f, et_o, et_f = ES(o, "P_baja"), ES(f, "P_baja"), ES(o, "eta"), ES(f, "eta")
        if pb_o is not None and pb_f is not None:
            dpbs.append(pb_f - pb_o)
        if et_o is not None and et_f is not None:
            d_et.append((et_f - et_o) * 100)
        comp.append((f"{o['x_b']}", f"{float(o['P_alta']):g}", f"{float(o['T_fuente']):g}", v(pb_o), v(pb_f),
                     v(pb_f - pb_o) if pb_o is not None and pb_f is not None else "-",
                     v(ES(o, "margen_O2")), v(ES(f, "margen_O2")), v(et_o), v(et_f),
                     f"{(et_f - et_o) * 100:+.2f}" if et_o is not None and et_f is not None else "-",
                     o.get("clasificacion") or "-", f.get("clasificacion") or "-"))
    sr = []
    for f in todas:
        ep = [e for e in evs.get(CLAVE(f), []) if e.get("margen") not in ("", None)]
        if len(ep) < 2:
            continue
        Pp = [ES(e, "P_baja") for e in ep]
        sr.append((f"{f['x_b']}", f"{float(f['P_alta']):g}", f"{float(f['T_fuente']):g}", str(len(ep)),
                   v(_pendiente(Pp, [ES(e, "T_bur") for e in ep])),
                   v(_pendiente(Pp, [ES(e, "T9_amb") for e in ep])),
                   v(_pendiente(Pp, [ES(e, "margen") for e in ep]))))
    T = lambda hd, filas: ("| " + " | ".join(hd) + " |\n" + "|" + "---|" * len(hd) + "\n"
                           + ("\n".join("| " + " | ".join(r) + " |" for r in filas) if filas else "—"))  # noqa: E731
    cls = ("KALINA", "CORREGIBLE", "INVIABLE", "NO_CONVERGIO")
    ct = T(("Clasificacion", "Puntos"), [(c, str(c_clas.get(c, 0))) for c in cls]
           + [("**Total**", f"**{n}**"), ("**KALINA**", f"**{len(k)}**"), ("**P* encontrada**", f"**{len(enc)}**")])
    kr = T(("x_b", "P_alta", "T_fuente", "P*", "T9_amb", "T_bur", "margen", "eta", "Wnet [kW]"),
           [(f["x_b"], f["P_alta"], f["T_fuente"], f["P_baja"], f["T9_amb"], f["T_bur"],
             f["margen_O2"], f["eta"], f["Wnet"]) for f in k]) if k else "Ningun punto KALINA."
    bk = T(("Bloqueo", "Puntos"), [(c, str(cnt)) for c, cnt in sorted(b.items(), key=lambda kv: -kv[1])])
    ctt = T(("x_b", "P_alta", "T_fuente", "P_baja antes", "P* ahora", "dP [kPa]", "margen antes",
             "margen ahora", "eta antes", "eta ahora", "deta [pp]", "clasif antes", "clasif ahora"), comp)
    st = T(("x_b", "P_alta", "T_fuente", "n_evals", "dT_bur/dP", "dT9_amb/dP", "dmargen/dP [K/kPa]"), sr)
    sub_pb = sum(dpbs) / len(dpbs) if dpbs else 0.0
    perd = -(sum(d_et) / len(d_et)) if d_et else 0.0
    hal = [f"**P* encontrada en {len(enc)} de {n} puntos**; KALINA = {len(k)} de {n}.",
           f"**P_baja extra vs barrido anterior**: promedio {sub_pb:+.1f} kPa en {len(dpbs)} pares; eta perdida media {perd:.2f} pp en {len(d_et)} pares.",
           "**O2 ya no bloquea por construccion** (margen 2 K => T9_amb = T_bur - 2 < T_bur). Sensibilidad: ver tabla dmargen/dP.",
           "`clasificacion=NO_CONVERGIO` agrupa P* encontrada con ciclo final no convergido; `SIN_P*` separa los que nunca alcanzaron margen 2 K."]
    cab = (f"# Reporte — P_baja por busqueda de raiz, margen O2 = 2 K (30 puntos)\n\n"
           "Fecha: 2026-09-24 · Motor: **solo TeqpAdapter** · Tarea 2026-09-24-pbaja-margen-2k (no toca src/ ni "
           "archivos existentes). Grid 5x3x2=30; T_sumidero=283.0 K, eta_t=eta_p=0.80, m_b=1.0 kg/s; eps fijos "
           "0.85/0.80/0.85. Margen O2 = T_bur(P,x_b) - T9_amb, T9_amb = re-solucion del condensador a "
           "max(T_SUMIDERO,T_AMB_DISENO)=283.15 K (criterio O2 de operativos.py). P* = raiz de margen(P)-2.0: "
           "bracket 40 kPa, max 10 pasos en [50, 0.5*P_alta], brentq xtol=0.5 kPa; clasificacion con "
           "T_amb_diseno=283.15 K.")
    resumen = (f"## Resumen ejecutivo\n\n**P* encontrada en {len(enc)} de {n} puntos**; **KALINA: {len(k)} de {n}**. P_baja subio {sub_pb:+.1f} kPa de media vs el barrido anterior; eta media perdio {perd:.2f} pp.")
    metodo = ("## Metodologia y limites\n\n- P_a = P_baja final del mismo punto en barrido_eps_fijos_085.csv; si fue "
              "NO_CONVERGIO o sin P_baja: calibrar_P_baja(pinch=6.0). - Cada evaluacion de margen(P) resuelve el ciclo "
              "completo con P_baja=P y re-resuelve solo el condensador (O2); todas van a evaluaciones_margen.csv. - "
              "Captura de CicloNoConvergeError/PropertyRangeError/ValueError/RuntimeError/NotImplementedError por "
              "evaluacion; si el bracket no se cierra o una evaluacion falla, el punto se registra con "
              "pbaja_encontrada=False y el motivo, sin descartarlo. Reanudable por CSV (clave x_b/P_alta/T_fuente).")
    ent = "## Entregables\n\n- barrido_margen2k.csv (30 filas), evaluaciones_margen.csv (todas las evaluaciones de margen(P)), run.log y este reporte."
    sec = [cab, resumen, f"## Conteo por clasificacion\n\n{ct}", f"## KALINA ordenados por eta\n\n{kr}",
           f"## Criterios que bloquean a los no-KALINA\n\n{bk}",
           f"## Comparacion 1:1 — barrido_eps_fijos_085 vs margen2k\n\n{ctt}",
           f"## Sensibilidad d/dP (regresion lineal sobre las evaluaciones)\n\n{st}",
           "## Hallazgos\n\n" + "\n".join(f"{i + 1}. {h}" for i, h in enumerate(hal)), metodo, ent]
    REPORTE_PATH.write_text("\n\n".join(sec) + "\n", encoding="utf-8")

def principal() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    done, _ = cargar_todas()
    viejos = _cargar(OLD_PATH)
    t0 = time.time()
    for x_b in XBS:
        for T_fuente in T_FUENTES:
            for P_alta in P_ALTAS:
                if (x_b, P_alta, T_fuente) in done:
                    continue
                fila, evals = resolver_punto(TeqpAdapter(x=x_b), x_b, P_alta, T_fuente, viejos.get((x_b, P_alta, T_fuente)))
                done = escribir_fila(fila, evals, done)
                log(f"[{time.time() - t0:6.0f}s] x_b={x_b} P_alta={P_alta:.0f} T_fuente={T_fuente:.0f} P*={fila['P_baja']} ok={fila['pbaja_encontrada']} evals={fila['n_evaluaciones']} clasif={fila['clasificacion']} eta={fila['eta']} marg={fila['margen_O2']} {fila['detalle_error'][:80]}")
    generar_reporte(cargar_todas()[1])
    log(f"Malla completa en {time.time() - t0:.0f}s; CSV: {CSV_PATH}\nReporte: {REPORTE_PATH}\nEvals: {EVAL_PATH}")

if __name__ == "__main__":
    principal()