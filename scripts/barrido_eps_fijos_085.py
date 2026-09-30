"""Barrido 30 puntos, efectividades FIJAS 0.85/0.80/0.85 y P_baja por punto para O2
(tarea 2026-09-23-barrido-eps-fijos-085): con eps_cond<=0.85 el liquido sale mas
caliente del condensador y O2 falla; se sube P_baja por punto fijo (burbuja a T9+2 K,
tol 1 kPa, max 4 iters). Misma malla que barrido_pinch6_realista.py para comparar 1:1.
Solo TeqpAdapter; reanudable por CSV; ningun punto se oculta. No modifica archivos existentes.
"""
from __future__ import annotations

import csv
import sys
import time
from collections import Counter
from pathlib import Path

from scipy.optimize import brentq

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "scripts"))

from calibracion_elsayed_malla import ETA_P, ETA_T, M_B, T_SUMIDERO  # noqa: E402
from calibracion_pinch import calibrar_P_baja  # noqa: E402
from src._cycle_loops import CicloNoConvergeError  # noqa: E402
from src.cycle_solver import resolver_ciclo  # noqa: E402
from src.properties.adapter import PropertyRangeError  # noqa: E402
from src.properties.teqp_adapter import TeqpAdapter  # noqa: E402
from src.restricciones import Clasificacion, evaluar_ciclo  # noqa: E402

OUT_DIR = REPO / "resultados" / "2026-09-23_eps_fijos_085"
CSV_PATH = OUT_DIR / "barrido_eps_fijos_085.csv"
REPORTE_PATH = OUT_DIR / "REPORTE_EPS_FIJOS_085.md"
OLD_CSV = REPO / "resultados" / "2026-09-23_pinch6_realista" / "barrido_pinch6_realista.csv"

PINCH = 6.0                 # solo para P_0 (misma base que el barrido pinch 6 K)
EPS = (0.85, 0.80, 0.85)    # eps_hrvg, eps_reg, eps_cond FIJOS en todos los puntos
MARGEN_O2, TOL_PBAJA, MAX_ITER_PBAJA = 2.0, 1.0, 4
T_AMB_REAL = 283.15
XBS, P_ALTAS, T_FUENTES = (0.60, 0.65, 0.70, 0.75, 0.80), (3000.0, 4000.0, 5000.0), (394.0, 423.0)

COLS = ("x_b", "P_alta", "T_fuente", "eps_hrvg", "eps_reg", "eps_cond", "P_baja",
        "iteraciones_pbaja", "pbaja_convergio", "T9", "T_burbuja", "margen_O2",
        "convergio", "clasificacion", "eta", "Wnet", "fallas", "detalle_error")
EXC_CATCH = (CicloNoConvergeError, PropertyRangeError, ValueError, RuntimeError, NotImplementedError)
NOCONV = Clasificacion.NO_CONVERGIO.value
CLAVE = lambda f: (float(f["x_b"]), float(f["P_alta"]), float(f["T_fuente"]))  # noqa: E731
CONV = lambda f: str(f.get("convergio")) == "True"  # noqa: E731
KAL = lambda f: f.get("clasificacion") == "KALINA"  # noqa: E731
ES = lambda f, c: float(f[c]) if f.get(c) not in ("", None) else None  # noqa: E731
v = lambda x: "-" if x is None else f"{x:g}"  # noqa: E731


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def _burbuja_en(backend, x_b: float, P_alta: float, T_objetivo: float) -> float:
    f = lambda P: backend.bubble_point(P, x_b) - T_objetivo  # noqa: E731
    return brentq(f, 50.0, P_alta - 10.0, xtol=1e-4)


def resolver_punto(backend, x_b, P_alta, T_fuente) -> dict:
    fila = dict(x_b=x_b, P_alta=P_alta, T_fuente=T_fuente,
                eps_hrvg=EPS[0], eps_reg=EPS[1], eps_cond=EPS[2],
                P_baja="", iteraciones_pbaja=0, pbaja_convergio=False,
                T9="", T_burbuja="", margen_O2="", convergio=False,
                clasificacion=NOCONV, eta="", Wnet="", fallas="", detalle_error="")
    def resolver(P_baja):
        return resolver_ciclo(backend, P_alta=P_alta, P_baja=P_baja,
                              T_fuente=T_fuente, T_sumidero=T_SUMIDERO,
                              x_b=x_b, m_b=M_B, eta_t=ETA_T, eta_p=ETA_P,
                              eps_hrvg=EPS[0], eps_reg=EPS[1], eps_cond=EPS[2])

    try:
        P = calibrar_P_baja(backend, x_b, P_alta, PINCH)   # P_0
    except EXC_CATCH as exc:
        fila["detalle_error"] = f"{type(exc).__name__}: {exc}"
        return fila
    fila["P_baja"] = round(P, 6)
    conv, n = False, 0
    try:
        for n in range(1, MAX_ITER_PBAJA + 1):
            res = resolver(P)
            P_next = _burbuja_en(backend, x_b, P_alta, res["estados"]["e9"].T + MARGEN_O2)
            if abs(P_next - P) < TOL_PBAJA:
                P = P_next
                conv = True
                break
            P = P_next
    except EXC_CATCH as exc:
        fila.update(P_baja=round(P, 6), iteraciones_pbaja=n,
                    detalle_error=f"{type(exc).__name__}: {exc}")
        return fila
    fila.update(iteraciones_pbaja=n, pbaja_convergio=conv, P_baja=round(P, 6))
    try:  # resolver una ultima vez con el P_baja final
        res = resolver(P)
    except EXC_CATCH as exc:
        fila["detalle_error"] = f"{type(exc).__name__}: {exc}"
        return fila
    T9 = res["estados"]["e9"].T
    T_burb = backend.bubble_point(P, x_b)
    fila.update(T9=round(T9, 6), T_burbuja=round(T_burb, 6), margen_O2=round(T_burb - T9, 6))
    try:
        val = evaluar_ciclo(backend, res, P_alta=P_alta, P_baja=P, T_fuente=T_fuente,
                           T_sumidero=T_SUMIDERO, x_b=x_b, m_b=M_B, eps_hrvg=EPS[0],
                           eps_reg=EPS[1], eps_cond=EPS[2], T_amb_diseno=T_AMB_REAL)
    except EXC_CATCH as exc:
        fila.update(detalle_error=f"{type(exc).__name__}: {exc}", convergio=True)
        return fila
    fila.update(convergio=True, clasificacion=val.clasificacion.value,
                eta=round(res["eta"], 6), Wnet=round(res["Wnet"], 4),
                fallas=",".join(x.codigo for x in val.fallas))
    return fila


def _cargar(path: Path) -> dict:
    if not path.exists():
        return {}
    d = {}
    with open(path, "r", newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            try:
                d[CLAVE(fila)] = fila
            except (KeyError, ValueError):
                continue
    return d

def cargar_todas() -> tuple[set, list]:
    d = _cargar(CSV_PATH)
    return set(d), list(d.values())

def escribir_fila(fila: dict, done: set) -> set:
    nuevo = not CSV_PATH.exists()
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        if nuevo:
            w.writeheader()
        w.writerow(fila)
    done.add(CLAVE(fila))
    return done

def generar_reporte(todas: list) -> None:
    n = len(todas)
    conv = [f for f in todas if CONV(f)]
    c_clas = Counter(f["clasificacion"] for f in todas)
    k = sorted((f for f in conv if KAL(f)), key=lambda f: -float(f["eta"]))
    bloqueos = Counter()
    for f in todas:
        if f.get("fallas"):
            for cod in f["fallas"].split(","):
                bloqueos[cod] += 1
    bloqueos[NOCONV] = sum(1 for f in todas if f["clasificacion"] == NOCONV)
    no_fix = sum(1 for f in todas if str(f.get("pbaja_convergio")) == "False" and f.get("P_baja"))
    o2_all = sum(1 for f in conv if "O2" in (f.get("fallas") or "").split(","))
    o1_all = sum(1 for f in conv if "O1" in (f.get("fallas") or "").split(","))
    marg_med = sum(ES(f, "margen_O2") or 0.0 for f in conv) / max(len(conv), 1)
    iter_med = sum(int(f["iteraciones_pbaja"]) for f in todas if str(f.get("iteraciones_pbaja")) not in ("", "None")) / max(n, 1)
    kr = ("| x_b | P_alta | T_fuente | P_baja | T9 | margen_O2 | eta | Wnet [kW] |\n"
          "|---|---|---|---|---|---|---|---|\n" + "\n".join(
          f"| {f['x_b']} | {f['P_alta']} | {f['T_fuente']} | {f['P_baja']} | {f['T9']} | "
          f"{f['margen_O2']} | {f['eta']} | {f['Wnet']} |" for f in k)
          if k else "Ningun punto KALINA.")
    old = _cargar(OLD_CSV)
    comunes = [(o, f) for f in todas if (o := old.get(CLAVE(f)))]
    comp, dpbs, e_old, e_new = [], [], [], []
    for o, f in comunes:
        pb_o, pb_f = ES(o, "P_baja"), ES(f, "P_baja")
        et_o, et_f = ES(o, "eta"), ES(f, "eta")
        if pb_o is not None and pb_f is not None:
            dpbs.append(pb_f - pb_o)
        if et_o is not None and et_f is not None:
            e_old.append(et_o)
            e_new.append(et_f)
        d_pb = f"{pb_f - pb_o:+.1f}" if (pb_o is not None and pb_f is not None) else "-"
        d_et = f"{(et_f - et_o) * 100:+.2f}" if (et_o is not None and et_f is not None) else "-"
        comp.append(f"| {o['x_b']} | {o['P_alta']} | {o['T_fuente']} | {v(pb_o)} | {v(pb_f)} | {d_pb} | "
                    f"{v(et_o)} | {v(et_f)} | {d_et} | {o.get('clasificacion') or '-'} | {f.get('clasificacion') or '-'} |")
    comp_rows = ("| x_b | P_alta | T_fuente | P_baja 6K | P_baja fijos | dP_baja [kPa] | eta 6K | "
                 "eta fijos | deta [pp] | clasif 6K | clasif fijos |\n|---|---|---|---|---|---|---|---|---|---|---|\n"
                 + "\n".join(comp))
    sub_pb = sum(dpbs) / len(dpbs) if dpbs else 0.0
    perd_eta = (sum(e_old) / len(e_old) - sum(e_new) / len(e_new)) * 100 if e_old else 0.0
    dom = f"{bloqueos.most_common(1)[0][0]} ({bloqueos.most_common(1)[0][1]})" if bloqueos else "ninguno"
    cls = ("KALINA", "VALIDO_ADVERTENCIA", "CORREGIBLE", "DEGENERADO", "INVIABLE", "NO_CONVERGIO")
    ct = ("| Clasificacion | Puntos |\n|---|---|\n" + "\n".join(f"| {c} | {c_clas.get(c, 0)} |" for c in cls)
          + f"\n| **Total** | **{n}** |\n| **KALINA** | **{len(k)}** |")
    bk = ("| Criterio | Puntos |\n|---|---|\n" + "\n".join(
          f"| {cod} | {cnt} |" for cod, cnt in sorted(bloqueos.items(), key=lambda kv: -kv[1])))
    hal = [
        f"**KALINA = {len(k)} de {n}**" + (" (tabla arriba)." if k else
            " — no aparece ninguno: la tabla de bloqueos muestra el criterio que lo impide."),
        f"**Subida de P_baja**: promedio {sub_pb:.1f} kPa, maximo {max(dpbs) if dpbs else 0.0:.1f} kPa "
        f"vs pinch 6 K (eps calibrados) en {len(dpbs)} puntos con par; punto fijo sin cerrar en {no_fix}.",
        f"**Costo de eta**: se pierden {perd_eta:.2f} pp de eta media (fijos vs calibrados 6 K) en {len(e_new)} "
        f"puntos comunes." if e_new else "**Costo de eta**: sin pares con valor para comparar.",
        f"**Bloqueo dominante**: {dom}; O2 en {o2_all} convergente(s), O1 en {o1_all}.",
        f"**Margen O2 medio** en convergentes: {marg_med:.2f} K; iteraciones del punto fijo: "
        f"media {iter_med:.2f} de {MAX_ITER_PBAJA}.",
    ]
    cab = (f"# Reporte — Barrido efectividades fijas 0.85/0.80/0.85 (30 puntos)\n\n"
           "Fecha: 2026-09-23 · Motor: **solo `TeqpAdapter`** · Tarea 2026-09-23-barrido-eps-fijos-085 "
           "(no toca `src/` ni archivos existentes).\n"
           f"Grid: {len(XBS)} x {len(P_ALTAS)} x {len(T_FUENTES)} = {len(XBS) * len(P_ALTAS) * len(T_FUENTES)} puntos; "
           "`T_sumidero=283.0 K`, `eta_t=eta_p=0.80`, `m_b=1.0 kg/s` (de `calibracion_elsayed_malla.py`); "
           "efectividades **fijas** `eps_hrvg=0.85, eps_reg=0.80, eps_cond=0.85`. P_baja: P_0 = burbuja a "
           f"(`T_sumidero`+6 K, x_b) + punto fijo (margen O2 {MARGEN_O2} K, tol {TOL_PBAJA} kPa, "
           f"max {MAX_ITER_PBAJA} iters). Clasificacion con `T_amb_diseno=283.15 K`.")
    resumen = (f"## Resumen ejecutivo\n\n**KALINA: {len(k)} de {n} puntos** con eps fijos 0.85/0.80/0.85. "
               f"Convergen {len(conv)}; los demas estan en el CSV con `detalle_error`. P_baja subio "
               f"{sub_pb:.1f} kPa de media vs pinch 6 K; eta media baja {perd_eta:.2f} pp.")
    metodo = ("## Metodologia y limites\n\n- `P_0` = burbuja a (`T_sumidero`+6 K, x_b) via "
              "`calibracion_pinch.calibrar_P_baja(pinch=6.0)`; en cada iteracion se resuelve el ciclo con "
              "`P_baja=P_k`, `T9=estados[e9].T` y `P_k+1` = burbuja a (`T9`+2 K, x_b); parada |dP|<1.0 kPa "
              "o 4 iters; si no cierra se registra igual con `pbaja_convergio=False`.\n- Resolucion final con "
              "el P_baja cerrado y clasificacion con `evaluar_ciclo(..., T_amb_diseno=283.15)` \\[margen real "
              "O2 = `T_burbuja(P_baja, x_b) - T9`].\n- Captura de `CicloNoConvergeError`/`PropertyRangeError`/"
              "`ValueError`/`RuntimeError`/`NotImplementedError` por punto y dentro de la iteracion de P_baja; "
              "reanudable por CSV; ningun punto se oculta.\n- Ventana: T_fuente 394 K (aprox. Husavik) y 423 K; "
              "P_alta 3000-5000 kPa; x_b 0.60-0.80.")
    entrega = ("## Entregables\n\n- `barrido_eps_fijos_085.csv` (30 filas: x_b, P_alta, T_fuente, eps_hrvg, "
               "eps_reg, eps_cond, P_baja, iteraciones_pbaja, pbaja_convergio, T9, T_burbuja, margen_O2, "
               "convergio, clasificacion, eta, Wnet, fallas, detalle_error).\n- `run.log`.\n- Este reporte.")
    secciones = [cab, resumen, f"## Conteo por clasificacion\n\n{ct}",
                 f"## KALINA con efectividades fijas, ordenados por eta\n\n{kr}",
                 f"## Criterios que bloquean a los no-KALINA\n\n{bk}",
                 f"## Comparacion 1:1 — pinch 6 K (eps calibrados) vs eps fijos 0.85/0.80/0.85 "
                 f"({len(comunes)} puntos comunes)\n\n{comp_rows}",
                 "## Hallazgos\n\n" + "\n".join(f"{i + 1}. {h}" for i, h in enumerate(hal)),
                 metodo, entrega]
    REPORTE_PATH.write_text("\n\n".join(secciones) + "\n", encoding="utf-8")

def principal() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    done, _ = cargar_todas()
    t0 = time.time()
    for x_b in XBS:
        for T_fuente in T_FUENTES:
            for P_alta in P_ALTAS:
                if (x_b, P_alta, T_fuente) in done:
                    continue
                fila = resolver_punto(TeqpAdapter(x=x_b), x_b, P_alta, T_fuente)
                dt = time.time() - t0
                done = escribir_fila(fila, done)
                log(f"[{dt:6.0f}s] x_b={x_b} P_alta={P_alta:.0f} T_fuente={T_fuente:.0f} "
                    f"Pbaja={fila['P_baja']} iter={fila['iteraciones_pbaja']} "
                    f"fix={fila['pbaja_convergio']} clasif={fila['clasificacion']} "
                    f"eta={fila['eta']} Wnet={fila['Wnet']} fallas={fila['fallas'] or '-'} "
                    f"marg={fila['margen_O2']} {fila['detalle_error'][:70]}")
    generar_reporte(cargar_todas()[1])
    log(f"Malla completa en {time.time()-t0:.0f}s; CSV: {CSV_PATH}\nReporte: {REPORTE_PATH}")

if __name__ == "__main__":
    principal()