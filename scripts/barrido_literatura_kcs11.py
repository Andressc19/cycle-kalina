"""Barrido acotado a la ventana validada por Elsayed et al. (2013) — KCS11.

Tarea 2026-09-22-barrido-literatura-kcs11. NO modifica ningun archivo
existente: barrido rapido (solo TeqpAdapter), mismo espiritu que
resultados/2026-09-21_xb_industria/barrido_xb_industria.py, pero dentro de
la ventana del paper (x_b 0.55-0.70, P_alta 1000-5000 kPa, T_fuente
373-463 K, T_sumidero=283 K fijo) y con P_baja + eps_* calibrados POR
PUNTO con el metodo de validacion_elsayed2013.py generalizado a la malla
(ver `calibracion_elsayed_malla.py`). Reanudable por CSV; ningun punto se
descarta (`convergio=False` + `detalle_error` real). Escribe:
    resultados/2026-09-22_literatura_kcs11/barrido_literatura_kcs11.csv
    resultados/2026-09-22_literatura_kcs11/REPORTE_LITERATURA_KCS11.md

Uso: python scripts/barrido_literatura_kcs11.py
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
    T_SUMIDERO, calibrar_P_baja, calibrar_eps)
from src._cycle_loops import CicloNoConvergeError  # noqa: E402
from src.properties.adapter import PropertyRangeError  # noqa: E402
from src.properties.teqp_adapter import TeqpAdapter  # noqa: E402
from src.restricciones import Clasificacion, evaluar_ciclo  # noqa: E402

OUT_DIR = REPO / "resultados" / "2026-09-22_literatura_kcs11"
CSV_PATH = OUT_DIR / "barrido_literatura_kcs11.csv"
REPORTE_PATH = OUT_DIR / "REPORTE_LITERATURA_KCS11.md"

XBS = (0.55, 0.60, 0.65, 0.70)
P_ALTAS = (1000.0, 1500.0, 2000.0, 3000.0, 5000.0)
T_FUENTES = (373.0, 423.0, 463.0)

COLS = ("x_b", "P_alta", "T_fuente", "P_baja", "eps_hrvg", "eps_reg",
        "eps_cond", "convergio", "clasificacion", "eta", "Wnet", "fallas",
        "detalle_error")
EXC_CATCH = (CicloNoConvergeError, PropertyRangeError, ValueError,
             RuntimeError, NotImplementedError)


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def resolver_punto(backend, x_b, P_alta, T_fuente) -> dict:
    fila = dict(x_b=x_b, P_alta=P_alta, T_fuente=T_fuente, P_baja="",
                eps_hrvg="", eps_reg="", eps_cond="", convergio=False,
                clasificacion=Clasificacion.NO_CONVERGIO.value, eta="",
                Wnet="", fallas="", detalle_error="")
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
    fila.update(eps_hrvg=round(cal["eps_hrvg"], 6),
                eps_reg=round(cal["eps_reg"], 6),
                eps_cond=round(cal["eps_cond"], 6))
    resultado = cal["resultado"]
    validacion = evaluar_ciclo(
        backend, resultado, P_alta=P_alta, P_baja=P_baja,
        T_fuente=T_fuente, T_sumidero=T_SUMIDERO, x_b=x_b, m_b=1.0,
        eps_hrvg=cal["eps_hrvg"], eps_reg=cal["eps_reg"],
        eps_cond=cal["eps_cond"])
    fila.update(
        convergio=True, clasificacion=validacion.clasificacion.value,
        eta=round(resultado["eta"], 6), Wnet=round(resultado["Wnet"], 4),
        fallas=",".join(f.codigo for f in validacion.fallas))
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
        writer = csv.DictWriter(f, fieldnames=COLS)
        if nuevo:
            writer.writeheader()
        for fila in filas:
            writer.writerow(fila)
            done.add((fila["x_b"], fila["P_alta"], fila["T_fuente"]))
    return done


def mejor_punto(filas: list) -> tuple[dict, str]:
    """Mejor punto: KALINA (mayor eta); si no, mayor eta; si no, el primero."""
    conv = [f for f in filas if f["convergio"] == "True"]
    if not conv:
        return filas[0], "sin puntos convergentes"
    kalina = [f for f in conv if f["clasificacion"] == "KALINA"]
    pool = sorted(kalina if kalina else conv,
                  key=lambda f: float(f["eta"]), reverse=True)
    motivo = "KALINA" if kalina else "mejor eta (ningun punto KALINA)"
    return pool[0], motivo


def generar_reporte(todas: list) -> None:
    """Escribe REPORTE_LITERATURA_KCS11.md a partir del CSV completo."""
    conteo = Counter(f["clasificacion"] for f in todas)
    n_kalina = conteo.get("KALINA", 0)
    v = lambda x: x or "-"
    filas = []
    for x_b in XBS:
        grupo = [f for f in todas if float(f["x_b"]) == x_b]
        if not grupo:
            continue
        m, motivo = mejor_punto(grupo)
        fallas = m["fallas"] or ("-" if m["convergio"] == "True"
                                 else f"no converge: {m['detalle_error'][:60] or 's/n'}")
        filas.append(
            f"| {x_b:.2f} | {motivo} | {m['clasificacion']} | {v(m['eta'])} "
            f"| {m['P_alta']} / {m['T_fuente']} | {v(m['P_baja'])} | {v(m['Wnet'])} | {fallas} |")
    hoyos = [f"x_b={xb:.2f}, P_alta={Pa:.0f}" for xb in XBS for Pa in P_ALTAS
             if (pts := [f for f in todas if float(f["x_b"]) == xb
                         and float(f["P_alta"]) == Pa])
             and not any(f["convergio"] == "True" for f in pts)]
    bloqueo = Counter()
    for f in todas:
        if f["convergio"] == "True" and f["fallas"]:
            bloqueo.update(f["fallas"].split(","))
    top = ", ".join(f"{c} ({n})" for c, n in bloqueo.most_common(4))
    hallazgos = []
    if n_kalina == 0:
        hallazgos.append("Ningun punto clasifica KALINA."
                         + (f" Criterios bloqueando: {top}." if top else ""))
    if hoyos:
        hallazgos.append("Hoyo de convergencia (ningun T_fuente converge): "
                         + "; ".join(hoyos) + ".")
    errs = sorted({f["detalle_error"][:80] for f in todas if f["detalle_error"]})
    if errs:
        hallazgos.append("Errores registrados (nunca ocultados): "
                         + "; ".join(errs[:4]) + ".")
    hallazgos = hallazgos or ["Ninguno detectado por los criterios automaticos."]
    cuerpo = [
        "# Reporte — Barrido dentro de la ventana validada por Elsayed et al. (2013) — KCS11",
        "",
        "Fecha: 2026-09-22 · Motor: **solo `TeqpAdapter`** (nada toca "
        "`src/`).",
        f"Grid: {len(todas)} puntos — x_b x P_alta x T_fuente = {len(XBS)} "
        f"x {len(P_ALTAS)} x {len(T_FUENTES)}; `T_sumidero=283.0 K` fijo, "
        "`eta_t=eta_p=0.80` (valores del paper), `m_b=1.0 kg/s`.",
        "",
        "## Resumen ejecutivo",
        "",
        f"**{n_kalina} punto(s) KALINA** de {len(todas)}. Conteo por clasificacion: "
        + ", ".join(f"{k}={v}" for k, v in sorted(conteo.items())),
        "",
        "## Tabla resumen por x_b",
        "",
        "| x_b | Motivo mejor punto | Clasificacion | Mejor η | Punto "
        "(P_alta/T_fuente) | P_baja [kPa] | Wnet [kW] | Fallas |",
        "|---|---|---|---|---|---|---|---|",
        *filas,
        "",
        "## Conteo total por clasificacion",
        "",
        "| Clasificacion | Puntos |",
        "|---|---|",
        *(f"| {k} | {conteo.get(k, 0)} |" for k in
          ("KALINA", "VALIDO_ADVERTENCIA", "CORREGIBLE", "DEGENERADO",
           "INVIABLE", "NO_CONVERGIO")),
        "",
        "## Hallazgos inesperados",
        "",
        *(f"- {h}" for h in hallazgos),
        "",
        "## Metodologia y limites",
        "",
        "- `P_baja` calibrada por punto (burbuja a `T_sumidero+4 K`, mismo "
        "metodo que `scripts/validacion_elsayed2013.py`); `eps_*` calibrados "
        "por punto (paso base 0.85/0.75/0.80, despeje en forma cerrada para "
        "T2/T6/T9, re-resolucion, clamp [0.01, 0.999]). Todo queda en el CSV "
        "para auditar que la calibracion es por punto.",
        "- Unicamente `TeqpAdapter` (motor rapido; verificado <0.5 % en h/s "
        "contra el motor real). Sin reintentos con otro motor.",
        "- Todo punto probado —converja o no— esta en el CSV con su "
        "`detalle_error` real; ventana del paper: Elsayed et al. (2013), "
        "IJLCT 8(suppl_1) i69-i78.",
        "",
        "## Entregables",
        "",
        "- `barrido_literatura_kcs11.csv` — 60 filas: x_b, P_alta, T_fuente, "
        "P_baja, eps_hrvg, eps_reg, eps_cond, convergio, clasificacion, eta, Wnet, fallas, detalle_error.",
        "- Este reporte.",
    ]
    REPORTE_PATH.write_text("\n".join(cuerpo) + "\n", encoding="utf-8")


def principal() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    done, record = cargar_hechas()
    t0_total = time.time()
    filas_nuevas = []
    anom = []
    for x_b in XBS:
        backend = TeqpAdapter(x=x_b)
        for T_fuente in T_FUENTES:
            for P_alta in P_ALTAS:
                if (x_b, P_alta, T_fuente) in done:
                    continue
                t0 = time.time()
                fila = resolver_punto(backend, x_b, P_alta, T_fuente)
                dt = time.time() - t0
                filas_nuevas.append(fila)
                if dt > 120:
                    anom.append((x_b, P_alta, T_fuente, round(dt)))
                log(f"[{time.time()-t0_total:6.0f}s] x_b={x_b} "
                    f"P_alta={P_alta} T_fuente={T_fuente} [{dt:5.1f}s] "
                    f"{fila['clasificacion']} eta={fila['eta']} "
                    f"fallas={fila['fallas'] or '-'} {fila['detalle_error'][:60]}")
        done = escribir_filas(filas_nuevas, done)
        filas_nuevas.clear()
    log(f"Barrido completo en {time.time()-t0_total:.0f}s; anomalias (>120s): {anom or 'ninguna'}")
    todas = list(cargar_hechas()[1].values())
    generar_reporte(todas)
    log(f"CSV: {CSV_PATH}")
    log(f"Reporte: {REPORTE_PATH}")


if __name__ == "__main__":
    principal()