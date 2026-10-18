"""Sensibilidad 1, Ronda 2 — corredor reanudable (un proceso por punto).

Corre los puntos de `ronda2_puntos.py` (barridos N2, N5 o N6) con el mismo
patron de `faseC_reanuda.py`: un `multiprocessing.Process` (contexto spawn) por
punto, 5 simultaneos y tope DURO de 600 s (si vence: `terminate()` + fila
`NO_CONVERGIO` con `mensaje="tiempo_agotado_600s"`). Escritura incremental en
modo `a` con `flush` por fila y encabezado fijo (se crea si falta). Acepta
`N2`, `N5`, `N6` o `all` como argumento; SALTA los `id_punto` ya escritos en
`ronda2_filas.csv`. Usa `comun.evaluar_punto(..., extra=True)` con
`t_amb_diseno` = T_sumidero del punto. Se ejecuta como script, no como modulo.
"""
from __future__ import annotations

import csv
import sys
import time
from multiprocessing import get_context
from multiprocessing.connection import wait
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR.parents[0] / "barrido_final")]

from comun import COLS, COLS_EXTRA, evaluar_punto  # noqa: E402
import ronda2_puntos as rp  # noqa: E402

OUT = _RAIZ / "resultados" / "2026-10-15_sens1_ronda2"
FILAS = OUT / "ronda2_filas.csv"
N_WORKERS = 5
LIMITE_S = 600.0
CM = list(COLS) + list(COLS_EXTRA) + ["id_punto", "barrido", "centro"]


def asegurar_encabezado() -> list:
    """Crea el CSV con el encabezado si falta; devuelve el encabezado real."""
    if not FILAS.exists():
        with open(FILAS, "w", encoding="utf-8", newline="") as fh:
            csv.writer(fh).writerow(CM)
    with open(FILAS, encoding="utf-8", newline="") as fh:
        return next(csv.reader(fh))


def leer_presentes() -> set:
    """`id_punto` ya escritos (para saltarlos)."""
    with open(FILAS, encoding="utf-8", newline="") as fh:
        return {r["id_punto"] for r in csv.DictReader(fh)}


def fila_base(t: dict) -> dict:
    """Fila vacia con los campos fijos + las variables del punto."""
    f = dict.fromkeys(CM)
    f.update(id_punto=t["id_punto"], barrido=t["barrido"], centro=t["centro"])
    for v, val in t["combo"].items():
        f[v] = val
    return f


def fila_timeout(t: dict) -> dict:
    """Fila de un punto que agoto el tope duro de 600 s."""
    f = fila_base(t)
    f.update(convergio=False, clasificacion="NO_CONVERGIO",
             mensaje="tiempo_agotado_600s", t_s=LIMITE_S)
    return f


def _worker(conn, t: dict) -> None:
    """UN punto; corre en un hijo. Devuelve la fila por la tuberia."""
    try:
        f = evaluar_punto(t["combo"], motor="teqp", tag=t["id_punto"],
                          t_amb_diseno=t["combo"]["T_sumidero"], extra=True)
        f.update(id_punto=t["id_punto"], barrido=t["barrido"],
                 centro=t["centro"])
    except BaseException as exc:                       # noqa: BLE001
        f = fila_base(t)
        f["mensaje"] = f"error_worker: {type(exc).__name__}: {exc}"[:300]
        f["error_inesperado"] = f["mensaje"]
    try:
        conn.send(f)
    finally:
        conn.close()


def _lanzar(ctx, t: dict, activos: dict) -> None:
    """Arranca el proceso de un punto y lo registra en `activos`."""
    padre, hijo = ctx.Pipe(duplex=False)
    proc = ctx.Process(target=_worker, args=(hijo, t))
    proc.start()
    hijo.close()
    activos[padre] = (proc, t, time.monotonic())


def _escribir(esc, fh, header: list, f: dict, n: int, total: int) -> None:
    esc.writerow({c: f.get(c) for c in header})
    fh.flush()
    t_s = f.get("t_s")
    t_txt = f"{float(t_s):.1f}" if t_s is not None else "?"
    print(f"[{n}/{total}] {f['id_punto']} {f['clasificacion']} {t_txt}s",
          flush=True)


def _matar(proc) -> None:
    """Termina un worker atascado (TerminateProcess en Windows)."""
    proc.terminate()
    proc.join(timeout=15)
    if proc.is_alive():
        proc.kill()
        proc.join(timeout=5)


def main(argv: list) -> None:
    barrido = argv[1] if len(argv) > 1 else "all"
    if barrido not in ("N2", "N5", "N6", "all"):
        print(f"uso: ronda2_corrida.py [N2|N5|N6|all] (recibi {barrido!r})",
              flush=True)
        return
    OUT.mkdir(parents=True, exist_ok=True)
    header = asegurar_encabezado()
    todos = rp.tareas(barrido)
    presentes = leer_presentes()
    faltan = [t for t in todos if t["id_punto"] not in presentes]
    print(f"Ronda 2 [{barrido}] | {len(todos) - len(faltan)} saltados | "
          f"{len(faltan)} a evaluar | {N_WORKERS} procesos | tope "
          f"{LIMITE_S:.0f}s -> {FILAS}", flush=True)
    ctx = get_context("spawn")
    t0, n, agotados = time.monotonic(), 0, 0
    pendientes, activos = list(faltan), {}
    with open(FILAS, "a", encoding="utf-8", newline="") as fh:
        esc = csv.DictWriter(fh, fieldnames=header)
        while pendientes or activos:
            while pendientes and len(activos) < N_WORKERS:
                _lanzar(ctx, pendientes.pop(0), activos)
            if not activos:
                break
            ahora = time.monotonic()
            espera = min((ini + LIMITE_S) - ahora
                         for _, _, ini in activos.values())
            for conn in wait(list(activos), timeout=max(0.0, espera)):
                if conn not in activos:
                    continue
                proc, t, ini = activos.pop(conn)
                try:
                    f = conn.recv()
                except (EOFError, OSError):
                    f = fila_base(t)
                    f.update(convergio=False, clasificacion="NO_CONVERGIO",
                             mensaje="proceso_terminado_sin_resultado")
                    f["t_s"] = time.monotonic() - ini
                conn.close()
                proc.join(timeout=15)
                n += 1
                _escribir(esc, fh, header, f, n, len(faltan))
            ahora = time.monotonic()
            for conn, (proc, t, ini) in list(activos.items()):
                if ahora - ini < LIMITE_S:
                    continue
                _matar(proc)
                conn.close()
                del activos[conn]
                n += 1
                agotados += 1
                _escribir(esc, fh, header, fila_timeout(t), n, len(faltan))
    print(f"fin [{barrido}]: {n} puntos nuevos en "
          f"{time.monotonic() - t0:.0f} s; {agotados} agotaron "
          f"{LIMITE_S:.0f}s -> {FILAS}", flush=True)


if __name__ == "__main__":
    main(sys.argv)
