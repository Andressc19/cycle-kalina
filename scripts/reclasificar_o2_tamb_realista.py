"""Reclasificacion de O2 (cavitacion) con piso realista: misma malla de 60
puntos de `barrido_literatura_kcs11` (Elsayed 2013), un solo resolve por
punto y DOS llamadas a `evaluar_ciclo` sobre el mismo resultado ya resuelto:
T_amb_diseno=303.55 K (tropical, col `clasificacion_tropical`) vs 283.15 K
(= `T_sumidero`, 10 C, Fase 3 de `test/fases-sensibilidad`, col
`clasificacion_realista`). Reanudable por CSV; ningun punto se descarta; NO
modifica archivos. Escribe: resultados/2026-09-22_o2_tamb_realista/.
"""
from __future__ import annotations

import csv
import sys
import time
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from calibracion_elsayed_malla import (  # noqa: E402
    M_B, T_SUMIDERO, calibrar_P_baja, calibrar_eps)
from src._cycle_loops import CicloNoConvergeError  # noqa: E402
from src.properties.adapter import PropertyRangeError  # noqa: E402
from src.properties.teqp_adapter import TeqpAdapter  # noqa: E402
from src.restricciones import Clasificacion, evaluar_ciclo  # noqa: E402

OUT_DIR = REPO / "resultados" / "2026-09-22_o2_tamb_realista"
CSV_PATH = OUT_DIR / "reclasificacion_o2.csv"
REPORTE_PATH = OUT_DIR / "REPORTE_O2_TAMB_REALISTA.md"
XBS = (0.55, 0.60, 0.65, 0.70)
P_ALTAS = (1000.0, 1500.0, 2000.0, 3000.0, 5000.0)
T_FUENTES = (373.0, 423.0, 463.0)
T_TROP, T_REAL = 303.55, 283.15   # piso heredado 30.4 C vs T_sumidero 10 C
COLS = ("x_b", "P_alta", "T_fuente", "P_baja", "eps_hrvg", "eps_reg", "eps_cond", "convergio", "eta", "Wnet", "clasificacion_tropical", "fallas_tropical", "clasificacion_realista", "fallas_realista", "detalle_error")
EXC_CATCH = (CicloNoConvergeError, PropertyRangeError, ValueError,
             RuntimeError, NotImplementedError)
NOCONV = Clasificacion.NO_CONVERGIO.value


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def evaluar_piso(backend, res, *, T_amb_diseno, **kw):
    """evaluar_ciclo con un piso dado; devuelve (validacion|None, detalle)."""
    try:
        return evaluar_ciclo(backend, res, T_sumidero=T_SUMIDERO,
                             T_amb_diseno=T_amb_diseno, **kw), ""
    except EXC_CATCH as exc:
        return None, f"{type(exc).__name__}: {exc}"


def resolver_punto(backend, x_b, P_alta, T_fuente) -> dict:
    fila = dict(x_b=x_b, P_alta=P_alta, T_fuente=T_fuente, P_baja="",
                eps_hrvg="", eps_reg="", eps_cond="", convergio=False,
                eta="", Wnet="", clasificacion_tropical=NOCONV,
                fallas_tropical="", clasificacion_realista=NOCONV,
                fallas_realista="", detalle_error="")
    try:
        P_baja = calibrar_P_baja(backend, x_b, P_alta)
    except EXC_CATCH as exc:
        fila["detalle_error"] = f"{type(exc).__name__}: {exc}"
        return fila
    fila["P_baja"] = round(P_baja, 6)
    try:
        cal = calibrar_eps(backend, x_b=x_b, P_alta=P_alta, P_baja=P_baja,
                           T_fuente=T_fuente)
    except EXC_CATCH as exc:
        fila["detalle_error"] = f"{type(exc).__name__}: {exc}"
        return fila
    res = cal["resultado"]
    fila.update(eps_hrvg=round(cal["eps_hrvg"], 6),
                eps_reg=round(cal["eps_reg"], 6),
                eps_cond=round(cal["eps_cond"], 6))
    kw = dict(P_alta=P_alta, P_baja=P_baja, T_fuente=T_fuente, x_b=x_b,
              m_b=M_B, eps_hrvg=cal["eps_hrvg"], eps_reg=cal["eps_reg"],
              eps_cond=cal["eps_cond"])
    vt, et = evaluar_piso(backend, res, T_amb_diseno=T_TROP, **kw)
    vr, er = evaluar_piso(backend, res, T_amb_diseno=T_REAL, **kw)
    for x in (vr.fallas if vr else []):
        if x.codigo == "O2":
            log(f"  O2 residual realista x_b={x_b} P_alta={P_alta} "
                f"T_fuente={T_fuente}: T9_amb={x.valor_medido:.5f} K vs "
                f"esperado {x.valor_esperado}")
            break
    fila.update(convergio=True, eta=round(res["eta"], 6),
                Wnet=round(res["Wnet"], 4),
                clasificacion_tropical=vt.clasificacion.value if vt else NOCONV,
                fallas_tropical=",".join(x.codigo for x in vt.fallas) if vt else "",
                clasificacion_realista=vr.clasificacion.value if vr else NOCONV,
                fallas_realista=",".join(x.codigo for x in vr.fallas) if vr else "",
                detalle_error=et or er)
    return fila


def cargar_hechas() -> tuple[set, dict]:
    """(done, record): claves (x_b, P_alta, T_fuente) ya en el CSV."""
    if not CSV_PATH.exists():
        return set(), {}
    done, record = set(), {}
    with open(CSV_PATH, "r", newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            try:
                clave = (float(fila["x_b"]), float(fila["P_alta"]),
                         float(fila["T_fuente"]))
            except (KeyError, ValueError):
                continue
            done.add(clave)
            record.setdefault(clave, fila)
    return done, record


def escribir_filas(filas: list, done: set) -> set:
    nuevo = not CSV_PATH.exists()
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        if nuevo:
            w.writeheader()
        for fila in filas:
            w.writerow(fila)
            done.add((fila["x_b"], fila["P_alta"], fila["T_fuente"]))
    return done


def generar_reporte(todas: list) -> None:
    n = len(todas)
    c_t = Counter(f["clasificacion_tropical"] for f in todas)
    c_r = Counter(f["clasificacion_realista"] for f in todas)
    conv = [f for f in todas if f["convergio"] == "True"]
    cambios = [f for f in todas
               if f["clasificacion_tropical"] != f["clasificacion_realista"]]
    a_k = [f for f in cambios if f["clasificacion_realista"] == "KALINA"]
    v = lambda x: x or "-"

    def mejor(grupo, col):
        cc = [f for f in grupo if f["convergio"] == "True"]
        if not cc:
            return grupo[0], "sin convergentes"
        k = [f for f in cc if f[col] == "KALINA"]
        p = sorted(k or cc, key=lambda f: float(f["eta"]), reverse=True)
        return p[0], "KALINA" if k else "mejor eta (ningun punto KALINA)"

    def bloqueos(col):
        return Counter(c for f in conv if f[col] for c in f[col].split(","))

    filas_xb = []
    for x_b in XBS:
        g = [f for f in todas if float(f["x_b"]) == x_b]
        if not g:
            continue
        mt, mt_ = mejor(g, "clasificacion_tropical")
        mr, mr_ = mejor(g, "clasificacion_realista")
        filas_xb.append(f"| {x_b:.2f} | {mt_} | {v(mt['clasificacion_tropical'])} | {v(mt['eta'])} | {mt['P_alta']}/{mt['T_fuente']} | {mr_} | {v(mr['clasificacion_realista'])} | {v(mr['eta'])} | {mr['P_alta']}/{mr['T_fuente']} |")
    fc = [f"| {v(f['x_b'])} | {v(f['P_alta'])} | {v(f['T_fuente'])} | {v(f['eta'])} | {v(f['Wnet'])} | {f['clasificacion_tropical']} ({v(f['fallas_tropical'])}) | {f['clasificacion_realista']} ({v(f['fallas_realista'])}) |" for f in cambios]
    b_t, b_r = bloqueos("fallas_tropical"), bloqueos("fallas_realista")
    o2_r = [f for f in conv if "O2" in (f["fallas_realista"] or "").split(",")]
    nl = sum(1 for f in conv if "O2" in (f["fallas_tropical"] or "").split(",") and "O2" not in (f["fallas_realista"] or "").split(","))

    hal = []
    if a_k:
        hal.append(f"**El patron de la Fase 3 (rama `test/fases-sensibilidad`) SE REPITE**: bajar el piso de O2 de {T_TROP} K a {T_REAL} K abre {len(a_k)} punto(s) nuevo(s) a KALINA: " + "; ".join(f"x_b={f['x_b']}, P_alta={f['P_alta']}, T_fuente={f['T_fuente']} (eta={v(f['eta'])}, Wnet={v(f['Wnet'])} kW)" for f in a_k) + ".")
    else:
        hal.append(f"**El patron de la Fase 3 NO se reproduce en esta malla**: bajar el piso a {T_REAL} K deja 0 puntos nuevos KALINA.")
    if o2_r:
        hal.append(f"O2 sigue bloqueando {len(o2_r)} punto(s) incluso con el piso realista ({nl} quedan liberados de O2 sin alcanzar KALINA); margen exacto en el log de la corrida.")
    else:
        hal.append(f"O2 deja de bloquear TODOS los puntos convergentes con el piso realista (se limpia en {nl} punto(s)).")
    pers = [f for f in conv if f["clasificacion_realista"] != "KALINA" and f["fallas_realista"]]
    if pers:
        top = ", ".join(f"{c} ({b_r[c]})" for c in ("N2", "N3", "O1", "O2", "O3", "O5", "C1", "C2", "C3") if b_r.get(c))
        hal.append(f"Con el piso realista, {len(pers)} punto(s) convergente(s) siguen sin ser KALINA, bloqueados por: {top}.")
    errs = sorted({f["detalle_error"][:80] for f in todas if f["detalle_error"]})
    if errs:
        hal.append("Errores registrados (nunca ocultados): " + "; ".join(errs[:4]) + ".")

    kl = ("KALINA", "VALIDO_ADVERTENCIA", "CORREGIBLE", "DEGENERADO", "INVIABLE", "NO_CONVERGIO")
    ct = "| Clasificacion | Tropical (303.55 K) | Realista (283.15 K) |\n|---|---|---|\n" + "\n".join(f"| {k} | {c_t.get(k, 0)} | {c_r.get(k, 0)} |" for k in kl) + f"\n| **Total** | **{n}** | **{n}** |"
    fc_txt = "| x_b | P_alta [kPa] | T_fuente [K] | eta | Wnet [kW] | Tropical (fallas) | Realista (fallas) |\n|---|---|---|---|---|---|---|\n" + "\n".join(fc) if cambios else "Ninguno: todos los puntos conservan su clasificacion."
    xb_txt = "| x_b | Criterio trop | Clasif trop | eta trop | Punto trop (P_alta/T_fuente) | Criterio real | Clasif real | eta real | Punto real (P_alta/T_fuente) |\n|---|---|---|---|---|---|---|---|---|\n" + "\n".join(filas_xb)
    bl_txt = "| Criterio | Tropical | Realista |\n|---|---|---|\n" + "\n".join(f"| {c} | {b_t.get(c, 0)} | {b_r.get(c, 0)} |" for c in kl[1:] + ("C1", "C2", "C3"))
    cab = (f"# Reporte — Reclasificacion de O2 con piso realista "
           f"(T_amb_diseno={T_REAL} K vs {T_TROP} K)\n\n"
           "Fecha: 2026-09-22 · Motor: **solo `TeqpAdapter`** · Tarea "
           "2026-09-22-reclasificar-o2-tamb-realista (no toca `src/`).\n"
           f"Grid: {n} puntos — x_b x P_alta x T_fuente = {len(XBS)} x {len(P_ALTAS)} x {len(T_FUENTES)}; `T_sumidero=283.0 K` fijo, "
           "`eta_t=eta_p=0.80`, `m_b=1.0 kg/s`. Un solo resolve por punto; "
           "`evaluar_ciclo` x2 sobre el mismo resultado: "
           f"`T_amb_diseno={T_TROP} K` (tropical) y `T_amb_diseno={T_REAL} K` "
           "(= `T_sumidero` real, 10 C, criterio de la Fase 3).")
    resumen = (f"## Resumen ejecutivo\n\n**KALINA: {c_t.get('KALINA', 0)} "
               f"punto(s) con el piso tropical vs **{c_r.get('KALINA', 0)}** "
               f"con el piso realista** de {n}. Convergen {len(conv)}; "
               f"cambian {len(cambios)}; no-KALINA a KALINA: {len(a_k)}.")
    metodo = ("## Metodologia y limites\n\n"
              "- `P_baja`/`eps_*` calibrados por punto (import directo de "
              "`calibracion_elsayed_malla.py`); tropical-vs-realista solo "
              "sobre `evaluar_ciclo` (re-resuelve el condensador para O2, no "
              "el ciclo). Unicamente `TeqpAdapter`; sin reintentos.\n"
              "- Piso realista = mismo valor para toda la malla (283.15 K = "
              "`T_sumidero` fijo), no calibracion por punto. Todo punto "
              "—converja o no— esta en el CSV con su `detalle_error` real.\n"
              "- Ventana del paper: Elsayed et al. (2013), IJLCT 8(suppl_1) "
              "i69-i78.")
    entrega = ("## Entregables\n\n"
               "- `reclasificacion_o2.csv` — 60 filas: x_b, P_alta, T_fuente, "
               "P_baja, eps_hrvg, eps_reg, eps_cond, convergio, eta, Wnet, "
               "clasificacion_tropical, fallas_tropical, "
               "clasificacion_realista, fallas_realista, detalle_error.\n"
               "- Este reporte.")
    secciones = [cab, resumen, f"## Conteo por clasificacion, lado a lado\n\n{ct}",
                 f"## Puntos que cambian de clasificacion al bajar el piso de O2\n\n{fc_txt}",
                 f"## Tabla resumen por x_b — mejor punto con cada criterio\n\n{xb_txt}",
                 f"## Bloqueos por criterio (puntos convergentes)\n\n{bl_txt}",
                 "## Hallazgos\n\n" + "\n".join(f"{i + 1}. {h}" for i, h in enumerate(hal)),
                 metodo, entrega]
    REPORTE_PATH.write_text("\n\n".join(secciones) + "\n", encoding="utf-8")


def principal() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    done, _ = cargar_hechas()
    t0 = time.time()
    filas, anom = [], []
    for x_b in XBS:
        backend = TeqpAdapter(x=x_b)
        for T_fuente in T_FUENTES:
            for P_alta in P_ALTAS:
                if (x_b, P_alta, T_fuente) in done:
                    continue
                t1 = time.time()
                fila = resolver_punto(backend, x_b, P_alta, T_fuente)
                dt = time.time() - t1
                filas.append(fila)
                if dt > 120:
                    anom.append((x_b, P_alta, T_fuente, round(dt)))
                log(f"[{time.time()-t0:6.0f}s] x_b={x_b} P_alta={P_alta} "
                    f"T_fuente={T_fuente} [{dt:5.1f}s] "
                    f"trop={fila['clasificacion_tropical']} "
                    f"real={fila['clasificacion_realista']} "
                    f"eta={fila['eta']} Wnet={fila['Wnet']} "
                    f"fallas_r={fila['fallas_realista'] or '-'} "
                    f"{fila['detalle_error'][:70]}")
        done = escribir_filas(filas, done)
        filas.clear()
    log(f"Malla completa en {time.time()-t0:.0f}s; anomalias (>120s): "
        f"{anom or 'ninguna'}")
    generar_reporte(list(cargar_hechas()[1].values()))
    log(f"CSV: {CSV_PATH}\nReporte: {REPORTE_PATH}")


if __name__ == "__main__":
    principal()