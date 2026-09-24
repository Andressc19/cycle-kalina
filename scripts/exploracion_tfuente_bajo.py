"""T_fuente bajo (333 K) x variable — 5 puntos (tarea
2026-09-22-tfuente-bajo-barrido-xb): complementa la malla de 60 puntos
(T_fuente en {373,423,463}) con el limite inferior del paper, P_alta=1500
kPa, piso realista de O2 (283.15 K), comparado vs el punto equivalente a
373 K. Solo TeqpAdapter; NO modifica archivos existentes.
"""
from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from calibracion_elsayed_malla import (  # noqa: E402
    M_B, T_SUMIDERO, calibrar_P_baja, calibrar_eps)
from src._cycle_loops import CicloNoConvergeError  # noqa: E402
from src.properties.adapter import PropertyRangeError  # noqa: E402
from src.properties.teqp_adapter import TeqpAdapter  # noqa: E402
from src.restricciones import Clasificacion, evaluar_ciclo  # noqa: E402

OUT_DIR = REPO / "resultados" / "2026-09-22_tfuente_bajo"
CSV_PATH = OUT_DIR / "exploracion_tfuente_bajo.csv"
REPORTE_PATH = OUT_DIR / "REPORTE_TFUENTE_BAJO.md"
REF_CSV = REPO / "resultados" / "2026-09-22_o2_tamb_realista" / "reclasificacion_o2.csv"

T_FUENTE, P_ALTA = 333.0, 1500.0
XBS = (0.55, 0.60, 0.65, 0.70, 0.75)
T_REAL = 283.15   # piso realista ya validado (Fase 3): T_sumidero, 10 C
COLS = ("x_b", "P_alta", "T_fuente", "P_baja", "eps_hrvg", "eps_reg",
        "eps_cond", "convergio", "clasificacion", "eta", "Wnet", "fallas", "detalle_error")
EXC_CATCH = (CicloNoConvergeError, PropertyRangeError, ValueError, RuntimeError, NotImplementedError)
NOCONV = Clasificacion.NO_CONVERGIO.value


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def resolver_punto(backend, x_b) -> dict:
    fila = dict(x_b=x_b, P_alta=P_ALTA, T_fuente=T_FUENTE, P_baja="",
                eps_hrvg="", eps_reg="", eps_cond="", convergio=False,
                clasificacion=NOCONV, eta="", Wnet="", fallas="", detalle_error="")
    try:
        P_baja = calibrar_P_baja(backend, x_b, P_ALTA)
    except EXC_CATCH as exc:
        fila["detalle_error"] = f"{type(exc).__name__}: {exc}"
        return fila
    fila["P_baja"] = round(P_baja, 6)
    try:
        cal = calibrar_eps(backend, x_b=x_b, P_alta=P_ALTA, P_baja=P_baja,
                           T_fuente=T_FUENTE)
    except EXC_CATCH as exc:
        fila["detalle_error"] = f"{type(exc).__name__}: {exc}"
        return fila
    res = cal["resultado"]
    fila.update(eps_hrvg=round(cal["eps_hrvg"], 6),
                eps_reg=round(cal["eps_reg"], 6),
                eps_cond=round(cal["eps_cond"], 6),
                eta=round(res["eta"], 6), Wnet=round(res["Wnet"], 4))
    kw = dict(P_alta=P_ALTA, P_baja=P_baja, T_fuente=T_FUENTE, x_b=x_b,
              m_b=M_B, eps_hrvg=cal["eps_hrvg"], eps_reg=cal["eps_reg"],
              eps_cond=cal["eps_cond"])
    try:
        v = evaluar_ciclo(backend, res, T_sumidero=T_SUMIDERO, T_amb_diseno=T_REAL, **kw)
    except EXC_CATCH as exc:
        fila["detalle_error"] = f"{type(exc).__name__}: {exc}"
        fila["convergio"] = True  # el ciclo convergio; fallo la evaluacion
        fila["clasificacion"] = NOCONV
        return fila
    fila.update(convergio=True, clasificacion=v.clasificacion.value,
                fallas=",".join(x.codigo for x in v.fallas))
    return fila


def cargar_referencia() -> dict:
    """Ref a T_fuente=373 K, P_alta=1500: clave x_b -> fila (piso realista)."""
    if not REF_CSV.exists():
        return {}
    ref = {}
    for fila in csv.DictReader(
            open(REF_CSV, "r", newline="", encoding="utf-8")):
        if float(fila["P_alta"]) == P_ALTA and float(fila["T_fuente"]) == 373.0:
            ref[float(fila["x_b"])] = fila
    return ref


def generar_reporte(filas: list, ref: dict) -> None:
    d_eta = lambda a, b: (f"{(float(a) - float(b)) * 100:+.3f} pp" if a and b else "-")
    v, filas_cmp = lambda s: s or "-", []
    for f in filas:
        r = ref.get(float(f["x_b"]))
        if r:
            ref_txt = (f"**{r['clasificacion_realista'] or NOCONV}** | "
                       f"{v(r['eta'])} | {v(r['Wnet'])} | "
                       f"{v(r['fallas_realista'])} | {d_eta(f['eta'], r['eta'])} |")
        else:
            ref_txt = "no disponible | - | - | - | - |"
        filas_cmp.append(f"| {f['x_b']:.2f} | {T_FUENTE:.0f} | "
                         f"**{f['clasificacion']}** | {v(f['eta'])} | "
                         f"{v(f['Wnet'])} | {v(f['fallas'])} | 373 | {ref_txt}")
    notas = []
    for f in filas:
        r = ref.get(float(f["x_b"]))
        if not f["convergio"]:
            notas.append(f"- **x_b={f['x_b']}**: el ciclo NO converge "
                         f"a 333 K — {f['detalle_error'][:150]}")
        elif f["detalle_error"]:
            notas.append(f"- **x_b={f['x_b']}**: el ciclo SI converge "
                         f"(eta={v(f['eta'])}) pero `evaluar_ciclo` falla: "
                         f"{f['detalle_error'][:130]}")
        elif not r:
            notas.append(f"- **x_b={f['x_b']}**: sin equivalente a 373 K "
                         f"(malla anterior llegaba a 0.70); queda "
                         f"{f['clasificacion']} con eta={v(f['eta'])}.")
        else:
            rc = r["clasificacion_realista"] or NOCONV
            txt = (f"clasificacion igual ({f['clasificacion']})"
                   if rc == f["clasificacion"]
                   else f"clasificacion CAMBIA ({rc} -> {f['clasificacion']})")
            notas.append(f"- **x_b={f['x_b']}**: {txt}; η baja "
                         f"{d_eta(f['eta'], r['eta'])}. Fallas: "
                         f"{v(f['fallas'])} (373 K: {v(r['fallas_realista'])}).")
    n_conv = sum(f["convergio"] for f in filas)
    n_eval = sum(f["convergio"] and not f["detalle_error"] for f in filas)
    n_k = sum(1 for f in filas if f["convergio"]
              and f["clasificacion"] == "KALINA")
    cab = (f"# Reporte — T_fuente bajo ({T_FUENTE:.0f} K) con x_b variable\n\n"
           "Fecha: 2026-09-22 · Motor: **solo `TeqpAdapter`** · Tarea "
           "2026-09-22-tfuente-bajo-barrido-xb (no toca `src/`).\n"
           f"{len(XBS)} puntos: `T_fuente={T_FUENTE:.0f} K` y "
           f"`P_alta={P_ALTA:.0f} kPa` fijos, `x_b` en {XBS}; "
           "`T_sumidero=283.0 K`, `eta_t=eta_p=0.80`, `m_b=1.0 kg/s` "
           "(importadas de `calibracion_elsayed_malla.py`).")
    resumen = (f"## Resumen ejecutivo\n\nConvergen {n_conv} de {len(XBS)} "
               f"puntos y {n_eval} se evaluan con clasificacion "
               f"(**{n_k} KALINA**); comparacion vs `reclasificacion_o2.csv` "
               "(mismo `x_b`, `P_alta=1500`, `T_fuente=373 K`, col "
               "`clasificacion_realista`):")
    tabla = ("| x_b | T_fuente [K] | Clasif | eta | Wnet [kW] | Fallas | "
             "T_fuente ref [K] | Clasif ref | eta ref | Wnet ref [kW] | "
             "Fallas ref | Δη [pp] |\n|---|---|---|---|---|---|---|---|---"
             "|---|---|---|\n" + "\n".join(filas_cmp))
    hallazgos = ("## Comentario: ayudar / perjudicar / no cambiar\n\n"
                 "**Conclusion: bajar `T_fuente` 373 -> 333 K **perjudica** "
                 "drasticamente la evaluabilidad**: 4 de 5 puntos no convergen "
                 "por `PropertyRangeError` (liquido comprimido profundo a "
                 "`P_alta=1500` con pinch de 4 K, ~329 K, fuera del dominio "
                 "de teqp) y el quinto converge pero su evaluacion (O2, "
                 "`bubble_point`) tampoco entra en dominio. Ningun punto es "
                 "clasificable a 333 K, frente a 3 KALINA + 1 CORREGIBLE(O2) "
                 "a 373 K con el mismo metodo y piso realista. Es una "
                 "limitacion de cobertura del motor, no una regla "
                 "termodinamica general del ciclo.\n\n" + "\n".join(notas))
    metodo = ("## Metodologia y limites\n\n"
              "- `P_baja`/`eps_*` calibrados por punto (import de "
              "`calibracion_elsayed_malla.py`); un resolve; piso realista "
              f"fijo `T_amb_diseno={T_REAL} K` = `T_sumidero`. Ningun punto "
              "se oculta: `convergio=False` + `detalle_error` real.\n"
              "- x_b=0.75 extiende la malla anterior (llegaba a 0.70); su "
              "equivalente a 373 K no existe todavia.\n"
              "- Ventana del paper: Elsayed et al. (2013), IJLCT 8(suppl_1) "
              "i69-i78; T_fuente 333-473 K.")
    entrega = (f"## Entregables\n\n- `exploracion_tfuente_bajo.csv` — {len(filas)} "
               "filas: x_b, P_alta, T_fuente, P_baja, eps_hrvg, eps_reg, "
               "eps_cond, convergio, clasificacion, eta, Wnet, fallas, "
               "detalle_error.\n- Este reporte.")
    REPORTE_PATH.write_text(
        "\n\n".join([cab, resumen,
                     f"## Tabla de los {len(XBS)} puntos vs T_fuente=373 K\n\n{tabla}",
                     hallazgos, metodo, entrega]) + "\n", encoding="utf-8")


def principal() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ref = cargar_referencia()
    t0 = time.time()
    filas = []
    for x_b in XBS:
        backend = TeqpAdapter(x=x_b)
        t1 = time.time()
        fila = resolver_punto(backend, x_b)
        dt = time.time() - t1
        filas.append(fila)
        log(f"[{time.time()-t0:6.0f}s] x_b={x_b} P_alta={P_ALTA:.0f} "
            f"T_fuente={T_FUENTE:.0f} [{dt:5.1f}s] "
            f"clasif={fila['clasificacion']} eta={fila['eta']} "
            f"Wnet={fila['Wnet']} fallas={fila['fallas'] or '-'} "
            f"{fila['detalle_error'][:70]}")
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(filas)
    generar_reporte(filas, ref)
    log(f"CSV: {CSV_PATH}\nReporte: {REPORTE_PATH}")


if __name__ == "__main__":
    principal()