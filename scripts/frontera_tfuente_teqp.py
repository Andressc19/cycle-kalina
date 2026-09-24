"""Frontera de cobertura de TeqpAdapter entre 333 K (falla) y 373 K (funciona):
malla 3x5 T_fuente={340,350,360} x x_b={0.55..0.75}, P_alta=1500 fijo, piso
realista 283.15 K. Solo TeqpAdapter; reanudable; sin ocultar errores; novedad.
"""
from __future__ import annotations

import csv, sys, time
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from calibracion_elsayed_malla import (M_B, T_SUMIDERO, calibrar_P_baja, calibrar_eps)  # noqa: E402
from src._cycle_loops import CicloNoConvergeError  # noqa: E402
from src.properties.adapter import PropertyRangeError  # noqa: E402
from src.properties.teqp_adapter import TeqpAdapter  # noqa: E402
from src.restricciones import Clasificacion, evaluar_ciclo  # noqa: E402

OUT_DIR = REPO / "resultados" / "2026-09-22_frontera_tfuente"
CSV_PATH = OUT_DIR / "frontera_tfuente_teqp.csv"
REPORTE_PATH = OUT_DIR / "REPORTE_FRONTERA_TFUENTE.md"
T_FUENTES = (340.0, 350.0, 360.0)
XBS = (0.55, 0.60, 0.65, 0.70, 0.75)
P_ALTA, T_REAL = 1500.0, 283.15
COLS = ("x_b", "P_alta", "T_fuente", "P_baja", "eps_hrvg", "eps_reg",
        "eps_cond", "convergio", "clasificacion", "eta", "Wnet", "fallas",
        "detalle_error")
EXC_CATCH = (CicloNoConvergeError, PropertyRangeError, ValueError,
             RuntimeError, NotImplementedError)
NOCONV = Clasificacion.NO_CONVERGIO.value
CLAVE = lambda f: (float(f["x_b"]), float(f["T_fuente"]))  # noqa: E731
CONV = lambda f: str(f.get("convergio")) == "True"  # noqa: E731
ERT = lambda f: (f.get("detalle_error") or "").split(":")[0] or "-"  # noqa: E731

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def resolver_punto(backend, x_b, T_fuente) -> dict:
    fila = dict(x_b=x_b, P_alta=P_ALTA, T_fuente=T_fuente, P_baja="",
                eps_hrvg="", eps_reg="", eps_cond="", convergio=False,
                clasificacion=NOCONV, eta="", Wnet="", fallas="", detalle_error="")
    try:
        P_baja = calibrar_P_baja(backend, x_b, P_ALTA)
    except EXC_CATCH as exc:
        fila["detalle_error"] = f"{type(exc).__name__}: {exc}"
        return fila
    fila["P_baja"] = round(P_baja, 6)
    try:
        cal = calibrar_eps(backend, x_b=x_b, P_alta=P_ALTA, P_baja=P_baja, T_fuente=T_fuente)
    except EXC_CATCH as exc:
        fila["detalle_error"] = f"{type(exc).__name__}: {exc}"
        return fila
    res = cal["resultado"]
    fila.update(eps_hrvg=round(cal["eps_hrvg"], 6), eps_reg=round(cal["eps_reg"], 6),
                eps_cond=round(cal["eps_cond"], 6), eta=round(res["eta"], 6),
                Wnet=round(res["Wnet"], 4))
    kw = dict(P_alta=P_ALTA, P_baja=P_baja, T_fuente=T_fuente, x_b=x_b, m_b=M_B,
              eps_hrvg=cal["eps_hrvg"], eps_reg=cal["eps_reg"], eps_cond=cal["eps_cond"])
    try:
        v = evaluar_ciclo(backend, res, T_sumidero=T_SUMIDERO, T_amb_diseno=T_REAL, **kw)
    except EXC_CATCH as exc:
        fila["detalle_error"] = f"{type(exc).__name__}: {exc}"
        fila["convergio"] = True  # el ciclo convergio; fallo la evaluacion
        return fila
    fila.update(convergio=True, clasificacion=v.clasificacion.value,
                fallas=",".join(x.codigo for x in v.fallas))
    return fila

def cargar_todas() -> tuple[set, list]:
    """(done, filas) desde el CSV; claves (x_b, T_fuente)."""
    if not CSV_PATH.exists():
        return set(), []
    done, filas = set(), []
    with open(CSV_PATH, "r", newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            try:
                done.add(CLAVE(fila))
            except (KeyError, ValueError):
                continue
            filas.append(fila)
    return done, filas

def escribir_filas(filas: list, done: set) -> set:
    nuevo = not CSV_PATH.exists()
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        if nuevo:
            w.writeheader()
        for fila in filas:
            w.writerow(fila)
            done.add(CLAVE(fila))
    return done

def celda(f) -> str:
    if not CONV(f):
        return f"**NO** ({ERT(f)})"
    if f.get("detalle_error"):
        return f"eval-NO ({ERT(f)})"
    return f"{f.get('clasificacion') or NOCONV} (η={f.get('eta') or '-'})"

def generar_reporte(filas: list) -> None:
    idx = {CLAVE(f): f for f in filas}
    filas_mapa, stats = [], {}
    for T in T_FUENTES:
        celdas, n_conv, n_ok = [], 0, 0
        for x_b in XBS:
            f = idx.get((x_b, T))
            celdas.append(celda(f) if f else "pendiente")
            if f and CONV(f):
                n_conv += 1
                if not f.get("detalle_error"):
                    n_ok += 1
        stats[T] = (n_conv, n_ok)
        filas_mapa.append(f"| {T:.0f} K | " + " | ".join(celdas) + f" | {n_conv}/5 | {n_ok}/5 |")
    completas = [T for T in T_FUENTES if stats[T][1] == 5]
    fr_xb = {}
    for xb in XBS:
        buenos = [T for T in T_FUENTES if (xb, T) in idx and CONV(idx[(xb, T)])
                  and not idx[(xb, T)].get("detalle_error")]
        fr_xb[xb] = min(buenos) if buenos else None
    tipos = {}
    for f in filas:
        if f.get("detalle_error"):
            t = ERT(f)
            tipos[t] = tipos.get(t, 0) + 1
    res_stats = "; ".join(f"{T:.0f} K -> {stats[T][0]}/5 convergen, {stats[T][1]}/5 evaluan"
                          for T in T_FUENTES)
    concl = []
    if completas:
        f0 = min(completas)
        menores = [T for T in T_FUENTES if T < f0]
        concl.append(f"**Frontera: T_fuente = {f0:.0f} K** — a partir de ese valor los 5 x_b "
                     "convergen y pasan `evaluar_ciclo` con el piso realista 283.15 K."
                     + (f" Por debajo no hay cobertura completa ({res_stats})." if menores else ""))
    else:
        concl.append("**No hay un T_fuente en esta ventana (340-360 K) que cubra los 5 x_b**: "
                     + res_stats + ". La frontera real queda fuera de esta malla intermedia o es "
                     "irregular; no se fuerza una frontera limpia que estos datos no muestran.")
    vals = {v for v in fr_xb.values() if v}
    det_xb = "; ".join(f"x_b={k:.2f}: {v:.0f} K" if v else f"x_b={k:.2f}: sin cobertura en 340-360 K"
                       for k, v in fr_xb.items())
    if len(vals) <= 1:
        concl.append(f"**La frontera es la misma para todos los x_b** ({det_xb}).")
    else:
        concl.append(f"**La frontera NO es uniforme: depende de x_b** ({det_xb}) — primera T "
                     f"limpia entre {min(vals):.0f} y {max(vals):.0f} K en esta ventana.")
    if tipos:
        orden = sorted(tipos.items(), key=lambda kv: -kv[1])
        mismo = any(k == "PropertyRangeError" for k, _ in orden)
        concl.append("Patron de errores (todos en el CSV): " + ", ".join(f"{k} x{v}" for k, v in orden)
                     + (". El `PropertyRangeError` dominante a 333 K (liquido comprimido fuera del "
                        "dominio de teqp cerca de T1~329 K) SIGUE PRESENTE aqui"
                        if mismo else ". Ningun `PropertyRangeError` en esta ventana: el patron "
                        "difiere del visto a 333 K") + ".")
    else:
        concl.append("Sin errores en la malla 340-360 K: ningun `detalle_error` registrado.")
    notas = []
    for f in filas:
        if not f.get("detalle_error"):
            continue
        estado = "converge pero evalua mal" if CONV(f) else "NO converge"
        notas.append(f"- **T_fuente={float(f['T_fuente']):.0f} K, x_b={float(f['x_b']):.2f}**: "
                     f"{estado} — `{(f.get('detalle_error') or '')[:150]}`")
    cab = ("# Reporte — Frontera de cobertura de teqp entre 333 K y 373 K\n\n"
           "Fecha: 2026-09-22 · Motor: **solo `TeqpAdapter`** · Tarea "
           "2026-09-22-frontera-tfuente-bajo (no toca `src/`).\n"
           f"Malla 3x5 = {len(filas)} puntos: `T_fuente` en {T_FUENTES}, `x_b` en {XBS}, "
           f"`P_alta={P_ALTA:.0f} kPa` fijo; `T_sumidero=283.0 K`, `eta_t=eta_p=0.80`, "
           f"`m_b=1.0 kg/s` (importadas de `calibracion_elsayed_malla.py`), `T_amb_diseno={T_REAL} K`.")
    resumen = ("## Resumen ejecutivo\n\nBordes ya conocidos (no recalcados): 333 K -> 4/5 fallan con "
               "`PropertyRangeError` (`2026-09-22_tfuente_bajo/exploracion_tfuente_bajo.csv`); "
               "373 K -> 3 KALINA + 1 CORREGIBLE (`2026-09-22_o2_tamb_realista/reclasificacion_o2.csv`). "
               f"Aqui: {res_stats}.")
    encab = "| T_fuente \\ x_b | " + " | ".join(f"{x:.2f}" for x in XBS) + " | converge | evaluan |"
    mapa = "## Mapa T_fuente x x_b (15 puntos)\n\n" + encab + "\n"
    mapa += "|---" * (len(XBS) + 3) + "|\n" + "\n".join(filas_mapa)
    metodo = ("## Metodologia y limites\n\n"
              "- `P_baja`/`eps_*` calibrados por punto (import directo de "
              "`calibracion_elsayed_malla.py`); un resolve; piso realista fijo "
              f"`T_amb_diseno={T_REAL} K`. Captura de `CicloNoConvergeError`/`PropertyRangeError` "
              "sin abortar la malla; ningun punto se oculta (`convergio=False` + `detalle_error` "
              "real tal cual lo reporta el motor).\n"
              "- Reanudable por CSV sobre clave `(x_b, T_fuente)`.\n"
              "- Ventana del paper: Elsayed et al. (2013), IJLCT 8(suppl_1) i69-i78; 333-473 K.")
    entrega = (f"## Entregables\n\n- `frontera_tfuente_teqp.csv` — {len(filas)} filas: x_b, P_alta, "
               "T_fuente, P_baja, eps_hrvg, eps_reg, eps_cond, convergio, clasificacion, eta, "
               "Wnet, fallas, detalle_error.\n- Este reporte.")
    secciones = [cab, resumen, mapa, "## Conclusion explicita\n\n" + "\n\n".join(concl),
                 "## Puntos con error (nunca ocultados)\n\n" + ("\n".join(notas) if notas
                 else "Ninguno: los 15 puntos convergen y se evaluan."), metodo, entrega]
    REPORTE_PATH.write_text("\n\n".join(secciones) + "\n", encoding="utf-8")

def principal() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    done, _ = cargar_todas()
    t0 = time.time()
    for T_fuente in T_FUENTES:
        for x_b in XBS:
            if (x_b, T_fuente) in done:
                continue
            backend = TeqpAdapter(x=x_b)
            t1 = time.time()
            fila = resolver_punto(backend, x_b, T_fuente)
            dt = time.time() - t1
            done = escribir_filas([fila], done)
            log(f"[{time.time()-t0:6.0f}s] T_fuente={T_fuente:.0f} x_b={x_b} [{dt:5.1f}s] "
                f"conv={fila['convergio']} clasif={fila['clasificacion']} eta={fila['eta']} "
                f"fallas={fila['fallas'] or '-'} {fila['detalle_error'][:70]}")
    generar_reporte(cargar_todas()[1])
    log(f"CSV: {CSV_PATH}\nReporte: {REPORTE_PATH}")

if __name__ == "__main__":
    principal()