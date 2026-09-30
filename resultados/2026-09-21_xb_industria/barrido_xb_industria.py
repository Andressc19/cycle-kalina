"""Barrido x_b industrial (0.78-0.85) variando P_alta, solo TeqpAdapter.

Tarea 2026-09-21_xb_industria (ver scratchpad del director). NO toca src/;
escribe resultados/2026-09-21_xb_industria/barrido_xb_industria.csv.

Fases por x_b:
  1. Ventana: P_alta 6000..10000 kPa, paso 250 (P_baja=400 fija).
  2. Diagnóstico de borde si la ventana queda sin puntos convergentes:
     P_alta en {5000,5250,5500,5750,10500} para localizar el borde real.
  3. Barrido de P_baja (500..1500, paso 100) en el primer P_alta convergente
     de ese x_b (el mínimo encontrado), para ver si O2 se cierra con la
     presión de baja a composición alta.
"""

from __future__ import annotations

import csv
import os
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from src._cycle_loops import CicloNoConvergeError
from src.components import condensador
from src.cycle_solver import resolver_ciclo
from src.properties.adapter import PropertyRangeError
from src.properties.teqp_adapter import TeqpAdapter
from src.restricciones import Clasificacion, evaluar_ciclo
from src.restricciones.operativos import T_AMB_CAVITACION

OUT_DIR = Path(__file__).resolve().parent
CSV_PATH = OUT_DIR / "barrido_xb_industria.csv"

XBS = (0.78, 0.80, 0.82, 0.85)
P_ALTA_VENTANA = list(range(6000, 10001, 250))          # 17 valores
P_ALTA_BORDE = (5000.0, 5250.0, 5500.0, 5750.0, 10500.0)  # diagnóstico
P_BAJA_FIJA = 400.0
P_BAJA_SWEEP = list(range(500, 1501, 100))                # 11 valores

CICLO = dict(
    T_fuente=470.0, T_sumidero=300.032917, m_b=1.0, eta_t=0.85, eta_p=0.75,
    eps_hrvg=0.85, eps_reg=0.75, eps_cond=0.80)

COLS = ("x_b", "P_alta", "P_baja", "etiqueta_punto", "convergio",
        "clasificacion", "eta", "Wnet", "fallas", "detalle_error",
        "T2", "q2", "O2_margen_K")

EXC_CATCH = (CicloNoConvergeError, PropertyRangeError, ValueError,
             RuntimeError, NotImplementedError)


def margen_o2(backend, resultado, x_b, P_baja) -> float:
    """Subenfriamiento de bomba T_sat(P_baja,x_b) - T9_amb (K), peor caso."""
    e = resultado["estados"]
    T_amb = max(CICLO["T_sumidero"], T_AMB_CAVITACION)
    estado9_amb, _ = condensador.resolver(
        e["e8"], backend, T_sumidero=T_amb, eps=CICLO["eps_cond"],
        m=CICLO["m_b"])
    T_sat = backend.bubble_point(P_baja, x_b)
    return T_sat - estado9_amb.T


def resolver_punto(backend, x_b, P_alta, P_baja, etiqueta) -> dict:
    fila = {
        "x_b": x_b, "P_alta": P_alta, "P_baja": P_baja,
        "etiqueta_punto": etiqueta, "convergio": False,
        "clasificacion": Clasificacion.NO_CONVERGIO.value, "eta": "",
        "Wnet": "", "fallas": "", "detalle_error": "",
        "T2": "", "q2": "", "O2_margen_K": "",
    }
    try:
        resultado = resolver_ciclo(
            backend, P_alta=P_alta, P_baja=P_baja, x_b=x_b, **CICLO)
    except EXC_CATCH as exc:
        fila["detalle_error"] = f"{type(exc).__name__}: {exc}"
        return fila
    except Exception as exc:  # noqa: BLE001 — registrar todo, nunca ocultar
        fila["detalle_error"] = f"{type(exc).__name__}: {exc}"
        return fila

    validacion = evaluar_ciclo(
        backend, resultado, P_alta=P_alta, P_baja=P_baja, T_fuente=CICLO["T_fuente"],
        T_sumidero=CICLO["T_sumidero"], x_b=x_b, m_b=CICLO["m_b"],
        eps_hrvg=CICLO["eps_hrvg"], eps_reg=CICLO["eps_reg"],
        eps_cond=CICLO["eps_cond"])
    e2 = resultado["estados"]["e2"]
    _, q2 = backend.fase_de(P_alta, e2.T, x_b)
    fila.update(
        convergio=True, clasificacion=validacion.clasificacion.value,
        eta=round(resultado["eta"], 6), Wnet=round(resultado["Wnet"], 4),
        fallas=",".join(f.codigo for f in validacion.fallas),
        T2=round(e2.T, 3), q2=round(q2, 4),
        O2_margen_K=round(margen_o2(backend, resultado, x_b, P_baja), 4))
    return fila


def cargar_hechas() -> tuple[set[tuple], dict]:
    """Devuelve (done, record): done = puntos ya en el CSV; record mapea cada
    punto a su fila (para recuperar `convergio` en un re-arranque)."""
    if not CSV_PATH.exists():
        return set(), {}
    done: set[tuple] = set()
    record: dict[tuple, dict] = {}
    with open(CSV_PATH, "r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                clave = (float(row["x_b"]), float(row["P_alta"]),
                         float(row["P_baja"]))
            except (KeyError, ValueError):
                continue
            done.add(clave)
            record.setdefault(clave, row)
    return done, record


def convergio_en(record: dict, x_b, P_alta, P_baja) -> bool:
    fila = record.get((float(x_b), float(P_alta), float(P_baja)))
    return bool(fila) and fila.get("convergio") == "True"


def escribir_filas(filas: list[dict], done: set[tuple]) -> set[tuple]:
    archivo_nuevo = not CSV_PATH.exists()
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLS)
        if archivo_nuevo:
            writer.writeheader()
        for fila in filas:
            writer.writerow(fila)
            done.add((fila["x_b"], fila["P_alta"], fila["P_baja"]))
    return done


def principal() -> None:
    done, record = cargar_hechas()
    resumen = []
    t0_total = time.time()

    for x_b in XBS:
        backend = TeqpAdapter(x=x_b)
        min_convergente = None
        filas_xb = []
        for P_alta in P_ALTA_VENTANA:
            key = (x_b, P_alta, P_BAJA_FIJA)
            if key in done:
                if min_convergente is None and convergio_en(
                        record, x_b, P_alta, P_BAJA_FIJA):
                    min_convergente = P_alta
                continue
            t0 = time.time()
            fila = resolver_punto(backend, x_b, P_alta, P_BAJA_FIJA,
                                  "ventana")
            filas_xb.append(fila)
            print(f"[{time.time()-t0_total:.0f}s] x_b={x_b} P_alta={P_alta} "
                  f"[{time.time()-t0:.0f}s] {fila['clasificacion']} "
                  f"{fila['detalle_error'][:60] if fila['detalle_error'] else ''}",
                  flush=True)
            if fila["convergio"] and min_convergente is None:
                min_convergente = P_alta
        done = escribir_filas(filas_xb, done)
        filas_xb.clear()

        if min_convergente is None:
            for P_alta in P_ALTA_BORDE:
                key = (x_b, P_alta, 400.0)
                if key in done:
                    if (min_convergente is None and convergio_en(
                            record, x_b, P_alta, P_BAJA_FIJA)):
                        min_convergente = P_alta
                    continue
                t0 = time.time()
                fila = resolver_punto(backend, x_b, P_alta, P_BAJA_FIJA,
                                      "diagnostico_borde")
                filas_xb.append(fila)
                print(f"[{time.time()-t0_total:.0f}s] x_b={x_b} "
                      f"P_alta={P_alta} (borde) [{time.time()-t0:.0f}s] "
                      f"{fila['clasificacion']} "
                      f"{fila['detalle_error'][:60] if fila['detalle_error'] else ''}",
                      flush=True)
                if fila["convergio"] and min_convergente is None:
                    min_convergente = P_alta
            done = escribir_filas(filas_xb, done)
        filas_xb.clear()

        if min_convergente is None:
            resumen.append((x_b, "ninguno", None))
            print(f"== x_b={x_b}: sin ningun P_alta convergente (ventana+"
                  f"borde). P_baja NO barrida.", flush=True)
            continue

        for P_baja in P_BAJA_SWEEP:
            key = (x_b, min_convergente, P_baja)
            if key in done:
                continue
            t0 = time.time()
            fila = resolver_punto(backend, x_b, min_convergente, P_baja,
                                  "barrido_pbaja")
            filas_xb.append(fila)
            print(f"[{time.time()-t0_total:.0f}s] x_b={x_b} "
                  f"P_alta={min_convergente} P_baja={P_baja} "
                  f"[{time.time()-t0:.0f}s] {fila['clasificacion']} "
                  f"{fila['detalle_error'][:60] if fila['detalle_error'] else ''}",
                  flush=True)
        done = escribir_filas(filas_xb, done)
        filas_xb.clear()
        resumen.append((x_b, min_convergente, None))
        print(f"== x_b={x_b}: min P_alta convergente = {min_convergente} kPa; "
              f"barrido P_baja 500-1500 registrado.", flush=True)

    print(f"TOTAL {time.time()-t0_total:.0f}s. Resumen: {resumen}")
    print(f"CSV: {CSV_PATH}")


if __name__ == "__main__":
    principal()