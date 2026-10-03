"""Orquestador del CIERRE del benchmark de tiempos (tarea
`2026-10-01-benchmark-cierre-topes`): barrido de TOPES corregido (A2), control
contra V2, elección de configuración (A4) y mini-barrido corregido (B2).

NO modifica `src/`, `tests/`, ni los scripts/CSV existentes. Los modos y la
carga de items están en `benchmark_cierre_modos.py`; aquí solo se mide, se
controla y se decide con el criterio EXACTO del director.

Escribe solo en `resultados/2026-10-01_benchmark_reintento/`:
`benchmark_filas_topes.csv`, `benchmark_minibarrido_mb_corregido.csv` y
`progreso_cierre.log`.

Uso:  python scripts/benchmark_cierre_topes.py [a2|control|b2|todo]
"""
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_RAIZ))
sys.path.insert(0, str(_RAIZ / "scripts"))

import pandas as pd                                                    # noqa: E402
from benchmark_cierre_modos import (CFGS_NUEVAS, CSV_A, CSV_ABL, CSV_MINI,  # noqa: E402
                                    CSV_MINI_MB, CSV_TOPES, OUT, TOPE_DE,
                                    cfg_nombre, control_kw, items_a1, items_mini, medir)

LOG = OUT / "progreso_cierre.log"
N_WORKERS = 6


def log(msg):
    """Una línea por fila terminada, con flush (el director la lee en vivo)."""
    OUT.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(msg + "\n")
        fh.flush()


def pool(tareas, etiqueta):
    """6 workers; una línea de log por fila terminada."""
    filas, t0 = [], time.perf_counter()
    log(f"{etiqueta}: inicio — {len(tareas)} mediciones con {N_WORKERS} workers")
    with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
        for n, fut in enumerate(as_completed([ex.submit(medir, t) for t in tareas]), 1):
            filas.append(fut.result())
            log(f"  {etiqueta} {n}/{len(tareas)} ({time.perf_counter() - t0:.0f} s) "
                f"t_s={filas[-1]['t_s']:.1f} nF={filas[-1]['nF']}")
    log(f"{etiqueta}: fin — {len(filas)} filas en {time.perf_counter() - t0:.0f} s de pared")
    return filas


def parte_a2():
    """Las 4 configuraciones nuevas x las 40 filas que M0 no resuelve."""
    items, _ = items_a1()
    control_kw(items, pd.read_csv(CSV_A).query("etapa == 'A1'"), "A2/40", log)
    filas = pool([dict(etapa="A2", item=i, cfg=c) for c in CFGS_NUEVAS for i in items], "A2")
    df = pd.DataFrame(filas).sort_values(["config", "csv_origen", "fila_csv"])
    df.to_csv(CSV_TOPES, index=False)
    log(f"A2: {len(df)} filas -> {CSV_TOPES.name}")
    return df


def control_v2(df):
    """Control pedido: MB sin tope contra las 28 filas que rescata V2. Se exige que
    recupere las mismas filas y |Δη| < 1e-6 en las comunes."""
    v2 = pd.read_csv(CSV_ABL).query("V0 != 'convergio'").set_index(["csv_origen", "fila_csv"])
    mb = df[df.config == cfg_nombre(("MB", None, False))].set_index(["csv_origen", "fila_csv"])
    resc_v2 = {k for k in v2.index if v2.loc[k, "V2"] == "convergio"}
    resc_mb = {k for k in mb.index if mb.loc[k, "convergio"]}
    comunes = sorted(resc_v2 & resc_mb)
    deta = [abs(float(mb.loc[k, "eta"]) - float(v2.loc[k, "V2_eta"])) for k in comunes]
    solo_v2, solo_mb = sorted(resc_v2 - resc_mb), sorted(resc_mb - resc_v2)
    log(f"CONTROL V2: V2 rescata {len(resc_v2)}/40, MB sin tope {len(resc_mb)}/40, "
        f"comunes {len(comunes)}, max|d eta| = {(max(deta) if deta else float('nan')):.3e}, "
        f"solo V2 = {solo_v2}, solo MB = {solo_mb}")
    return dict(n_v2=len(resc_v2), n_mb=len(resc_mb), n_comunes=len(comunes),
                max_deta=max(deta) if deta else float("nan"), solo_v2=solo_v2,
                solo_mb=solo_mb)


def elegir(df):
    """Criterio EXACTO del director: entre las configuraciones con ST no, la de
    MENOR tope que recupera el mismo número de filas que 'sin tope'; si dos
    empatan en filas, la de menor tiempo total sobre las 40."""
    a = pd.read_csv(CSV_A).query("etapa == 'A1'")
    t = pd.concat([a, df], ignore_index=True)
    st_no = [c for c in TOPE_DE if c in set(t.config)]
    g = (t[t.config.isin(st_no)].groupby("config")
         .agg(filas_recuperadas=("convergio", "sum"), filas_medidas=("convergio", "size"),
              t_total_s=("t_s", "sum"), nF_medio=("nF", "mean")).reindex(st_no))
    g["tope"] = [TOPE_DE[c] for c in g.index]
    g["filas_por_1000s"] = (g.filas_recuperadas / (g.t_total_s / 1000.0)).round(2)
    ref = int(g.loc[cfg_nombre(("MB", None, False)), "filas_recuperadas"])
    cand = g[g.filas_recuperadas == ref].sort_values(["tope", "t_total_s"])
    elegido = cand.index[0]
    log(f"A4: 'sin tope' recupera {ref}/40; candidatas = {list(cand.index)}; "
        f"ELEGIDA = {elegido} (tope {TOPE_DE[elegido]}, "
        f"t={g.loc[elegido, 't_total_s']:.0f} s, nF medio {g.loc[elegido, 'nF_medio']:.2f})")
    for c, r in g.iterrows():
        log(f"  A4 tabla: {c:16s} tope={r.tope:>8} filas={int(r.filas_recuperadas):2d}/"
            f"{int(r.filas_medidas)} t={r.t_total_s:8.1f}s nF={r.nF_medio:5.2f} "
            f"filas/1000s={r.filas_por_1000s:.2f}")
    return elegido, g, ref


def _cfg_de(nombre):
    for c in CFGS_NUEVAS:
        if cfg_nombre(c) == nombre:
            return c
    raise SystemExit(f"'{nombre}' no es una configuración de MB con tope conocido")


def parte_b2(elegido):
    """Los mismos 93 puntos, solo MB con la configuración elegida. M0 y MA se copian
    del CSV anterior sin recalcular; la columna `origen` los distingue."""
    items, b = items_mini()
    control_kw(items, b[b.etapa == "M0"], "B2/93", log)
    t0 = time.perf_counter()
    filas = pool([dict(etapa=elegido, item=i, cfg=_cfg_de(elegido)) for i in items], "B2")
    t_pared = time.perf_counter() - t0
    nuevas = pd.DataFrame(filas)
    nuevas["origen"] = "MEDIDO en esta tarea (2026-10-01-benchmark-cierre-topes)"
    viejas = b[b.etapa.isin(["M0", "MA"])].assign(
        origen="REUTILIZADO de benchmark_minibarrido.csv (corrida del 2026-10-01)")
    df = pd.concat([nuevas, viejas], ignore_index=True).sort_values(
        ["origen", "etapa", "csv_origen", "fila_csv"])
    df.to_csv(CSV_MINI_MB, index=False)
    log(f"B2: tiempo de pared de {elegido} = {t_pared:.0f} s ({len(items)} puntos); "
        f"{len(df)} filas -> {CSV_MINI_MB.name}")
    return t_pared


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    etapa = sys.argv[1].lower() if len(sys.argv) > 1 else "todo"
    log(f"=== CIERRE TOPES {time.strftime('%Y-%m-%d %H:%M:%S')} — etapa '{etapa}' ===")
    df = parte_a2() if etapa in ("a2", "todo") else pd.read_csv(CSV_TOPES)
    if etapa in ("control", "a2", "todo"):
        control_v2(df)
    if etapa in ("b2", "todo"):
        elegido, _, _ = elegir(df)
        log(f"B2: configuracion elegida para el mini-barrido = {elegido}")
        parte_b2(elegido)
    log(f"=== FIN etapa '{etapa}' ===")


if __name__ == "__main__":
    main()