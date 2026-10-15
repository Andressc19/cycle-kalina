"""Sensibilidad 1, Fase C — REANUDAR la corrida LHS con tope duro por punto.

La corrida de `faseC_corrida.py` se atasco tras 124 puntos (todos C1): el tope
interno `PRESUPUESTO_S=300` no cubre todos los lazos del solver, y 5 puntos
quedaron mas de 15 min sin cerrar. Aqui se reanuda SIN perder nada:

- Se regenera EXACTAMENTE la misma muestra LHS (`faseC_corrida.tareas()`): misma
  semilla 20261014, mismas cajas, mismo redondeo, mismos `id_punto`.
- Verificacion de consistencia: los 124 `id_punto` ya escritos en
  `faseC_filas.csv` deben coincidir en sus 9 variables con la muestra. Si no,
  se detiene sin correr.
- Se evaluan solo los faltantes (~376). Cada punto va en su PROPIO
  `multiprocessing.Process` (contexto `spawn`), 5 simultaneos. NO se usa
  `ProcessPoolExecutor` porque no puede matar un worker atascado.
- Tope DURO por punto: 600 s. Si vence, el padre hace `terminate()` + `join()` y
  registra la fila como NO_CONVERGIO con `mensaje="tiempo_agotado_600s"`.
- Escritura incremental en modo `a` (solo se anaden filas), `flush` por fila,
  con el encabezado leido del archivo existente. Log por stdout (Tee-Object).
  Se ejecuta como script, no como modulo.
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
import faseC_corrida as fc  # noqa: E402

OUT = _RAIZ / "resultados" / "2026-10-14_sens1_faseC"
FILAS = OUT / "faseC_filas.csv"
N_WORKERS = 5
LIMITE_S = 600.0
CM = list(COLS) + list(COLS_EXTRA) + ["id_punto", "centro", "tipo"]


def leer_encabezado() -> list:
    """Encabezado real de `faseC_filas.csv` (columnas y orden existentes)."""
    with open(FILAS, encoding="utf-8", newline="") as fh:
        return next(csv.reader(fh))


def leer_presentes() -> dict:
    """`id_punto` -> fila ya escrita (para saltarlos y verificar consistencia)."""
    with open(FILAS, encoding="utf-8", newline="") as fh:
        return {r["id_punto"]: r for r in csv.DictReader(fh)}


def verificar(presentes: dict, idx: dict) -> list:
    """Lista de discrepancias entre los ids ya escritos y la muestra regenerada."""
    problemas = []
    for idp, fila in presentes.items():
        t = idx.get(idp)
        if t is None:
            problemas.append(f"{idp}: no esta en la muestra regenerada")
            continue
        for v in fc.VARIABLES:
            try:
                a, b = float(fila[v]), float(t["combo"][v])
            except (TypeError, ValueError):
                problemas.append(f"{idp}.{v}: valor no numerico en el CSV")
                continue
            if abs(a - b) > 1e-6:
                problemas.append(f"{idp}.{v}: csv={a} muestra={b}")
    return problemas


def fila_base(id_punto: str, centro: str, combo: dict) -> dict:
    """Fila vacia con los campos fijos + las 9 variables del punto."""
    f = dict.fromkeys(CM)
    f.update(id_punto=id_punto, centro=centro, tipo="lhs")
    for v in fc.VARIABLES:
        f[v] = combo[v]
    return f


def fila_timeout(t: dict) -> dict:
    """Fila de un punto que agoto el tope duro de 600 s."""
    f = fila_base(t["id_punto"], t["centro"], t["combo"])
    f.update(convergio=False, clasificacion="NO_CONVERGIO",
             mensaje="tiempo_agotado_600s", t_s=LIMITE_S)
    return f


def _worker(conn, combo, id_punto, centro) -> None:
    """UN punto; corre en un hijo. Devuelve la fila por la tuberia."""
    try:
        f = evaluar_punto(combo, motor="teqp", tag=id_punto,
                          t_amb_diseno=combo["T_sumidero"], extra=True)
        f.update(id_punto=id_punto, centro=centro, tipo="lhs")
    except BaseException as exc:                       # noqa: BLE001
        f = fila_base(id_punto, centro, combo)
        f["mensaje"] = f"error_worker: {type(exc).__name__}: {exc}"[:300]
        f["error_inesperado"] = f["mensaje"]
    try:
        conn.send(f)
    finally:
        conn.close()


def _lanzar(ctx, t: dict, activos: dict) -> None:
    """Arranca el proceso de un punto y lo registra en `activos`."""
    padre, hijo = ctx.Pipe(duplex=False)
    proc = ctx.Process(target=_worker,
                       args=(hijo, t["combo"], t["id_punto"], t["centro"]))
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


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    header = leer_encabezado()
    todos = fc.tareas()
    idx = {t["id_punto"]: t for t in todos}
    presentes = leer_presentes()
    problemas = verificar(presentes, idx)
    if problemas:
        print("CONSISTENCIA FALLIDA: no se corre nada.", flush=True)
        for p in problemas[:40]:
            print("  " + p, flush=True)
        return
    faltan = [t for t in todos if t["id_punto"] not in presentes]
    total = len(faltan)
    print(f"consistencia OK: {len(presentes)} ids ya escritos coinciden con la "
          f"muestra regenerada.", flush=True)
    print(f"Fase C reanuda | {len(presentes)} saltados | {total} a evaluar | "
          f"{N_WORKERS} procesos | tope {LIMITE_S:.0f}s -> {FILAS}", flush=True)
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
                    f = fila_base(t["id_punto"], t["centro"], t["combo"])
                    f.update(convergio=False, clasificacion="NO_CONVERGIO",
                             mensaje="proceso_terminado_sin_resultado")
                    f["t_s"] = time.monotonic() - ini
                conn.close()
                proc.join(timeout=15)
                n += 1
                _escribir(esc, fh, header, f, n, total)
            ahora = time.monotonic()
            for conn, (proc, t, ini) in list(activos.items()):
                if ahora - ini < LIMITE_S:
                    continue
                _matar(proc)
                conn.close()
                del activos[conn]
                n += 1
                agotados += 1
                _escribir(esc, fh, header, fila_timeout(t), n, total)
    print(f"fin: {n} puntos nuevos en {time.monotonic() - t0:.0f} s; "
          f"{agotados} agotaron {LIMITE_S:.0f}s -> {FILAS}", flush=True)


if __name__ == "__main__":
    main()
