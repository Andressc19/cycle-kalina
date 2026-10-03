"""A2 y B2 del CIERRE del benchmark, INCREMENTALES y REANUDABLES.

Por qué existe este archivo: el 2026-10-01 la corrida anterior de A2 (160
mediciones, 6 workers) terminó en `RecursionError` —`benchmark_cierre_modos.medir`
parchea `BM.cfg_nombre` con una función que llamaba a `BM.cfg_nombre`— y se
perdieron ~35 min de cómputo porque el orquestador guardaba las filas en memoria y
solo escribía el CSV al final.

Aquí CADA fila terminada se añade al CSV con `flush` y se registra en
`progreso_cierre.log`, así que un fallo posterior no destruye lo anterior:

  * si el CSV ya tiene la fila (config, csv_origen, fila_csv), se OMITE;
  * una excepción en una fila se escribe como una fila más (columnas
    `convergio=False`, `causa`, `msg`) y NO aborta la corrida.

NO modifica `src/`, `tests/` ni los CSV/scripts existentes: importa
`benchmark_cierre_modos.py` (items, `medir` con los parches, control de `kw`),
`benchmark_modos.py` (`PASO`, instrumentación) y `sonda_arranque_solver.py`
(`T_AMB`) y los usa tal cual. Escribe solo en
`resultados/2026-10-01_benchmark_reintento/`.

El humo (`humo`) usa EXACTAMENTE el mismo pool/`medir`/parche que la corrida
completa y DENTRO de un worker de `ProcessPoolExecutor`; sus 8 filas son las
primeras 8 de A2 (se quedan en el CSV y la corrida completa las omite).

Uso:  python scripts/benchmark_cierre_a2.py humo
       python scripts/benchmark_cierre_a2.py a2
       python scripts/benchmark_cierre_a2.py b2 <config_elegida_en_A4>
"""
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_RAIZ))
sys.path.insert(0, str(_RAIZ / "scripts"))

import pandas as pd                                                    # noqa: E402
import sonda_arranque_solver as P                                      # noqa: E402
from benchmark_cierre_modos import (CFGS_NUEVAS, CSV_A, CSV_MINI,             # noqa: E402
                                    CSV_MINI_MB, CSV_TOPES, OUT, cfg_nombre,
                                    control_kw, items_a1, items_mini, medir)

LOG = OUT / "progreso_cierre.log"
N_WORKERS = 6
N_HUMO_FILAS = 2
ORIGEN = "MEDIDO en esta tarea (2026-10-01-benchmark-continuacion)"
#: esquema EXACTO que devuelve `medir`: el de `benchmark_filas.csv` (40 columnas). Se
#: fija aqui para que una fila que no bringa `B_verificado`/`B_dh4s` (las no KALINA no
#: los traen) no recorte el encabezado del CSV y se pierdan en las filas KALINA.
COLS_A2 = list(pd.read_csv(CSV_A, nrows=0).columns)
COLS_B2 = list(pd.read_csv(CSV_MINI, nrows=0).columns) + ["origen"]


def log(msg):
    """Una línea por fila terminada, con flush (el director la lee en vivo)."""
    OUT.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(msg + "\n")
        fh.flush()


class Anexador:
    """Append fila a fila con `flush`. El encabezado lo fija la primera fila; las
    siguientes se alinean a esas columnas (mismo esquema que devuelve `medir`)."""

    def __init__(self, path, cols=None):
        self.path, self.cols, self.n = path, cols, 0

    def add(self, fila: dict) -> None:
        nuevo = self.cols is None
        if nuevo:
            self.cols = list(fila.keys())
        fila = {c: fila.get(c, "") for c in self.cols}
        txt = pd.DataFrame([fila], columns=self.cols).to_csv(index=False,
                                                             header=nuevo)
        with open(self.path, "a", encoding="utf-8", newline="") as fh:
            fh.write(txt if txt.endswith("\n") else txt + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        self.n += 1


def _fila_excepcion(tarea, exc):
    """Mismo esquema que `medir`, pero con la excepción en `causa`/`msg`: una fila
    que no converge por error inesperado, no una corrida abortada."""
    it, cfg = tarea["item"], tarea["cfg"]
    return dict(etapa=tarea["etapa"], config=cfg_nombre(cfg), csv_origen=it["csv_origen"],
                fila_csv=it["fila_csv"], grupo=it["grupo"], **it["kw"],
                x_backend=it["x_backend"], T_amb_diseno=P.T_AMB,
                backend=f"TeqpVerificado(x={it['x_backend']})",
                clasificacion_original=it["clasif"], eta_original=it["eta_orig"],
                convergio=False, causa=type(exc).__name__, clasificacion="NO_CONVERGIO",
                eta=None, T1_sol=None, nF=0, msg=f"EXCEPCION EN WORKER: {exc}"[:200],
                t_s=None, nF_intento1=None, t_intento1_s=None, reintento_usado=None,
                punto_cascada="", msg_intento1="", st_disparo=False, fase_fallo="worker",
                B_verificado=None, B_dh4s=None)


def normaliza(path, cols, etiqueta):
    """Si el CSV existente no tiene el esquema completo, lo reescribe con TODAS las
    columnas (las ausentes quedan vacías) para que las filas de ahora en adelante no
    pierdan campos. PIERDE NADA: solo añade columnas vacías y las reordena."""
    if not path.exists():
        return
    d = pd.read_csv(path)
    if list(d.columns) == cols:
        return
    faltan = [c for c in cols if c not in d.columns]
    sobran = [c for c in d.columns if c not in cols]
    d.reindex(columns=cols).to_csv(path, index=False)
    log(f"{etiqueta}: {path.name} normalizado al esquema de {len(cols)} columnas "
        f"(se anaden vacias {faltan}; sobran {sobran})")


def correr(tareas, etiqueta, destino, cols=None):
    """Como `benchmark_cierre_topes.pool` pero: (a) cada fila se anexa al CSV al
    terminar, con flush+fsync; (b) una excepción en una fila NO aborta la corrida;
    (c) devuelve (n_filas, n_excepciones, s_de_pared)."""
    anex, exc_n = Anexador(destino, cols), 0
    t0 = time.perf_counter()
    log(f"{etiqueta}: inicio — {len(tareas)} mediciones con {N_WORKERS} workers "
        f"-> {destino.name} (reanudable)")
    with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
        futs = {ex.submit(medir, t): t for t in tareas}
        for n, fut in enumerate(as_completed(list(futs)), 1):
            tarea = futs[fut]
            try:
                fila = fut.result()
            except Exception as exc:                      # noqa: BLE001 — no aborta
                exc_n += 1
                fila = _fila_excepcion(tarea, exc)
            anex.add(fila)
            log(f"  {etiqueta} {n}/{len(tareas)} ({time.perf_counter() - t0:.0f} s) "
                f"{fila['config']:16s} {fila['csv_origen']}#{fila['fila_csv']} "
                f"conv={fila['convergio']} t_s={fila['t_s']} nF={fila['nF']} "
                f"causa={fila['causa'] or '-'}")
    t_pared = time.perf_counter() - t0
    log(f"{etiqueta}: fin — {anex.n} filas en {t_pared:.0f} s de pared; "
        f"excepciones de worker = {exc_n}")
    return anex.n, exc_n, t_pared


def hechos(path, etiqueta):
    """Claves (config, csv_origen, fila_csv) ya presentes en el CSV: lo reanudable."""
    if not path.exists():
        log(f"{etiqueta}: {path.name} no existe todavia — se mide todo")
        return set()
    d = pd.read_csv(path)
    k = {(r.config, r.csv_origen, int(r.fila_csv)) for r in d.itertuples()}
    log(f"{etiqueta}: {path.name} ya tiene {len(d)} filas -> se reanuda, "
        f"se omiten las ya hechas")
    return k


def tarea_de(item, cfg, etapa):
    return dict(etapa=etapa, item=item, cfg=cfg)


def etapa_humo() -> None:
    """2 filas x las 4 configuraciones nuevas, por el camino real (ProcessPool +
    `medir` con los parches DENTRO del worker). Sus filas QUEDAN en el CSV de A2."""
    items, a = items_a1()
    control_kw(items[:N_HUMO_FILAS], a.query("etapa == 'A1'"), "HUMO", log)
    normaliza(CSV_TOPES, COLS_A2, "HUMO")
    hechas = hechos(CSV_TOPES, "HUMO")
    tareas = [tarea_de(i, c, "A2") for c in CFGS_NUEVAS for i in items[:N_HUMO_FILAS]
              if (cfg_nombre(c), i["csv_origen"], i["fila_csv"]) not in hechas]
    log(f"HUMO: {len(tareas)} mediciones ({N_HUMO_FILAS} filas x "
        f"{len(CFGS_NUEVAS)} configuraciones)")
    if not tareas:
        log("HUMO: nada que hacer (ya estaban)")
        return
    n, exc_n, _ = correr(tareas, "A2humo", CSV_TOPES, COLS_A2)
    if exc_n:
        raise SystemExit(f"HUMO: {exc_n} excepciones en worker — NO lanzar la corrida "
                         f"completa hasta arreglarlo")
    log(f"HUMO: OK — {n} filas, 0 excepciones, por el camino real")


def etapa_a2() -> None:
    """Las 4 configuraciones nuevas x las 40 filas que M0 no resuelve."""
    items, a = items_a1()
    control_kw(items, a.query("etapa == 'A1'"), "A2/40", log)
    normaliza(CSV_TOPES, COLS_A2, "A2")
    hechas = hechos(CSV_TOPES, "A2")
    total = len(CFGS_NUEVAS) * len(items)
    tareas = [tarea_de(i, c, "A2") for c in CFGS_NUEVAS for i in items
              if (cfg_nombre(c), i["csv_origen"], i["fila_csv"]) not in hechas]
    log(f"A2: {len(tareas)} de {total} mediciones pendientes "
        f"({total - len(tareas)} ya en {CSV_TOPES.name})")
    if not tareas:
        log("A2: nada que hacer (las 160 filas ya estan)")
        return
    correr(tareas, "A2", CSV_TOPES, COLS_A2)


def etapa_b2(elegido) -> None:
    """Los mismos 93 puntos, solo MB con la configuración elegida. M0 y MA se copian
    del CSV anterior sin recalcular; la columna `origen` los distingue."""
    items, b = items_mini()
    control_kw(items, b[b.etapa == "M0"], "B2/93", log)
    cfg = next((c for c in CFGS_NUEVAS if cfg_nombre(c) == elegido), None)
    if cfg is None:
        raise SystemExit(f"'{elegido}' no es una configuración de MB de A2: "
                         f"{[cfg_nombre(c) for c in CFGS_NUEVAS]}")
    if not CSV_MINI_MB.exists():                          # solo la primera vez: copia
        b[b.etapa.isin(["M0", "MA"])].assign(origen=(
            "REUTILIZADO de benchmark_minibarrido.csv (corrida del 2026-10-01)")
        ).to_csv(CSV_MINI_MB, index=False)
        log(f"B2: M0/MA REUTILIZADOS de benchmark_minibarrido.csv -> {CSV_MINI_MB.name}")
    normaliza(CSV_MINI_MB, COLS_B2, "B2")
    hechas = hechos(CSV_MINI_MB, "B2")
    tareas = [tarea_de(i, cfg, elegido) for i in items
              if (elegido, i["csv_origen"], i["fila_csv"]) not in hechas]
    d = pd.read_csv(CSV_MINI_MB)
    log(f"B2: {len(tareas)} de {len(items)} mediciones pendientes "
        f"({int((d.etapa == elegido).sum())} ya en {CSV_MINI_MB.name})")
    if not tareas:
        log("B2: nada que hacer (los 93 puntos ya estan)")
        return
    # mismas columnas que el CSV de la mini-corrida (las 40 de `medir`) + `origen`
    cols = COLS_B2
    t0 = time.perf_counter()
    anex, exc_n = Anexador(CSV_MINI_MB, cols), 0
    log(f"B2: inicio — {len(tareas)} mediciones con {N_WORKERS} workers -> "
        f"{CSV_MINI_MB.name} (reanudable)")
    with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
        futs = {ex.submit(medir, t): t for t in tareas}
        for n, fut in enumerate(as_completed(list(futs)), 1):
            tarea = futs[fut]
            try:
                fila = fut.result()
            except Exception as exc:                      # noqa: BLE001 — no aborta
                exc_n += 1
                fila = _fila_excepcion(tarea, exc)
            fila["origen"] = ORIGEN
            anex.add(fila)
            log(f"  B2 {n}/{len(tareas)} ({time.perf_counter() - t0:.0f} s) "
                f"{fila['config']:16s} {fila['csv_origen']}#{fila['fila_csv']} "
                f"conv={fila['convergio']} t_s={fila['t_s']} nF={fila['nF']} "
                f"causa={fila['causa'] or '-'}")
    log(f"B2: fin — {anex.n} filas en {time.perf_counter() - t0:.0f} s de pared; "
        f"excepciones de worker = {exc_n}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    etapa = sys.argv[1].lower() if len(sys.argv) > 1 else "a2"
    elegido = sys.argv[2] if len(sys.argv) > 2 else None
    log(f"=== A2/B2 INCREMENTAL {time.strftime('%Y-%m-%d %H:%M:%S')} "
        f"— etapa '{etapa}' ===")
    if etapa == "humo":
        etapa_humo()
    elif etapa == "a2":
        etapa_a2()
    elif etapa == "b2":
        if not elegido:
            raise SystemExit("B2 necesita el nombre de la configuración elegida (A4)")
        etapa_b2(elegido)
    else:
        raise SystemExit(f"etapa '{etapa}' no valida: humo|a2|b2")


if __name__ == "__main__":
    main()
