"""Orquestador del benchmark de tiempos del "reintento tolerante" (Tarea
`2026-10-01-benchmark-reintento-tolerante`).

NO modifica `src/`, `tests/` ni scripts/CSV existentes. Escribe solo en
`resultados/2026-10-01_benchmark_reintento/`.

  Parte A (calibración): 40 filas que M0 no resuelve x 6 configs de MB
      (+ M0 como referencia) y 30 filas sanas x (M0, MB t6 STno) para verificar
      que MB da exactamente el mismo resultado y nF que M0.
  Parte B (validación): mini-barrido de 60 puntos con la mezcla real de
      resultado, de extremo a extremo, en M0 / MB(mejor de A) / MA, midiendo
      el TIEMPO DE PARED de cada modo.

Los modos viven en `scripts/benchmark_modos.py` (M0/MA/MB, topes y ST).

Uso:  python scripts/benchmark_reintento_tolerante.py [a|b|todo]
"""
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_RAIZ))
sys.path.insert(0, str(_RAIZ / "scripts"))

import pandas as pd                                                       # noqa: E402
import sonda_arranque_solver as P                                         # noqa: E402
from benchmark_modos import CFGS, cfg_nombre, medir, parse_cfg            # noqa: E402

OUT = _RAIZ / "resultados" / "2026-10-01_benchmark_reintento"
LOG = OUT / "progreso.log"
CSV_A = OUT / "benchmark_filas.csv"
CSV_B = OUT / "benchmark_minibarrido.csv"
CSV_ABL = _RAIZ / "resultados" / "2026-10-01_ablacion_tiempos" / "ablacion_filas.csv"
N_WORKERS = 6
MB_A2 = ("MB", 6, False)          # MB usado en las filas sanas (debe igualar a M0)


def paso_uniforme(n, k):
    """k índices repartidos con paso uniforme sobre n (NO los k primeros)."""
    if k <= 1:
        return [0]
    if n <= k:
        return list(range(n))
    return sorted({round(i * (n - 1) / (k - 1)) for i in range(k)})


def log(msg):
    """Una línea por fila terminada, con flush: lo usa el verificador del director."""
    OUT.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(msg + "\n")
        fh.flush()


def filas_m0_falla():
    """Las 40 filas que M0 (V0) no resuelve, leídas del CSV de la ablación."""
    abl = pd.read_csv(CSV_ABL)
    return {(r.csv_origen, int(r.fila_csv)) for r in abl.itertuples() if r.V0 != "convergio"}


def convergentes(n_por_csv):
    """Filas `convergio=True` de los dos CSV que `muestra()` sabe reconstruir,
    con paso uniforme (coste real de un punto sano)."""
    d2 = pd.read_csv(_RAIZ / "resultados/barridos_2026-09-19/fase2_libre/busqueda_libre_v2.csv")
    dl = pd.read_csv(_RAIZ / "resultados/2026-09-22_literatura_kcs11/barrido_literatura_kcs11.csv")
    out = []
    specs = (("busqueda_libre_v2", d2[d2.convergio == True], P._kw_f2, 0.5),
             ("barrido_literatura_kcs11", dl[dl.convergio == True], P._kw_lt, "xb"))
    for src, df, mk, xb in specs:
        for i in paso_uniforme(df.shape[0], n_por_csv):
            r = df.iloc[i]
            kw = mk(r)
            out.append(dict(csv_origen=src, fila_csv=int(df.index[i]), grupo="sana", kw=kw,
                            x_backend=kw["x_b"] if xb == "xb" else xb,
                            clasif=r.clasificacion, eta_orig=float(r.eta),
                            exc_orig=str(r.fallas if "fallas" in df.columns else "")[:200]))
    return out


def minibarrido(malas, n_fall, n_sana):
    """Mini-barrido de `n_fall + n_sana` puntos con la mezcla real de resultado
    (~30 % NO_CONVERGIO): `n_fall` filas que M0 no resuelve (paso uniforme sobre
    las 40 de la muestra) + `n_sana` filas sanas repartidas por mitades entre los
    dos CSV que `muestra()` sabe reconstruir (paso uniforme dentro de cada uno)."""
    fall = [i for i in P.muestra() if (i["csv_origen"], i["fila_csv"]) in malas]
    return [fall[j] for j in paso_uniforme(len(fall), n_fall)] + convergentes(n_sana // 2)


def pool(tareas, etiqueta):
    """Ejecuta las tareas con 6 workers; una línea de log por fila terminada."""
    filas, t0 = [], time.perf_counter()
    log(f"{etiqueta}: inicio — {len(tareas)} mediciones con {N_WORKERS} workers")
    with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
        for n, fut in enumerate(as_completed([ex.submit(medir, t) for t in tareas]), 1):
            filas.append(fut.result())
            msg = f"  {etiqueta} {n}/{len(tareas)} ({time.perf_counter() - t0:.0f} s)"
            log(msg)
            print(msg, flush=True)
    log(f"{etiqueta}: fin — {len(filas)} filas en {time.perf_counter() - t0:.0f} s de reloj de pared")
    return filas


def mejor_cfg(df):
    """Criterio del director: menor tiempo TOTAL (convergen o no) sobre las 40
    filas que M0 no resuelve, sin perder más de 2 rescates frente a
    MB(tope 6, ST no). Si ninguna cumple, MB(tope 6, ST no)."""
    a1 = df[(df.etapa == "A1") & (df.config != "M0")]
    ref = int(a1[(a1.config == "MB_t6_STno") & a1.convergio].shape[0])
    tot = a1.groupby("config").t_s.sum()
    resc = a1[a1.convergio].groupby("config").size()
    ok = [c for c in tot.index if int(resc.get(c, 0)) >= ref - 2]
    return (min(ok, key=lambda c: tot[c]) if ok else "MB_t6_STno"), ref, tot


def parte_a():
    """Calibración: 40 filas que fallan x 6 configs MB (+ M0) y 30 sanas x (M0, MB)."""
    malas = filas_m0_falla()
    items = [i for i in P.muestra() if (i["csv_origen"], i["fila_csv"]) in malas]
    sanas = convergentes(15)
    print(f"A1: {len(items)} filas que M0 no resuelve x {len(CFGS)} configs MB (+M0) | "
          f"A2: {len(sanas)} sanas x (M0, {cfg_nombre(MB_A2)})", flush=True)
    tareas = ([dict(etapa="A1", item=i, cfg=c) for i in items for c in CFGS]
              + [dict(etapa="A1", item=i, cfg="M0") for i in items]
              + [dict(etapa="A2", item=i, cfg=c) for i in sanas for c in ("M0", MB_A2)])
    filas = pool(tareas, "PARTE A")
    df = pd.DataFrame(filas).sort_values(["etapa", "config", "csv_origen", "fila_csv"])
    df.to_csv(CSV_A, index=False)
    # A2: MB debe reproducir M0 exactamente (resultado y nF).
    a2 = df[df.etapa == "A2"]
    piv = a2.pivot_table(index=["csv_origen", "fila_csv"], columns="config",
                         values=["convergio", "eta", "nF", "T1_sol"])
    mal = [k for k in piv.index
           if piv.loc[k, ("convergio", "M0")] != piv.loc[k, ("convergio", "MB_t6_STno")]
           or piv.loc[k, ("nF", "M0")] != piv.loc[k, ("nF", "MB_t6_STno")]
           or not (piv.loc[k, ("eta", "M0")] == piv.loc[k, ("eta", "MB_t6_STno")])]
    log(f"A2: MB t6 STno reproduce a M0 en {len(piv) - len(mal)}/{len(piv)} filas sanas "
        f"(discrepancias: {len(mal)})")
    print(f"A2: MB == M0 en {len(piv) - len(mal)}/{len(piv)} sanas", flush=True)
    mejor, ref, tot = mejor_cfg(df)
    log(f"A1: mejor config MB = {mejor} (rescates de referencia MB_t6_STno = {ref}); "
        f"tiempos totales " + ", ".join(f"{c}={v:.0f}s" for c, v in tot.items()))
    print(f"A1: mejor MB = {mejor} (ref {ref} rescates)", flush=True)
    return mejor


def parte_b(mejor):
    """Mini-barrido de extremo a extremo: tiempo de pared en M0 / MB(mejor) / MA."""
    n_fall = int(round(0.30 * 60))
    n_sana = 60 - n_fall
    mini = minibarrido(filas_m0_falla(), n_fall, n_sana)
    filas, t_acum = [], 0.0
    for m in ("M0", mejor, "MA"):
        t0 = time.perf_counter()
        filas += pool([dict(etapa=m, item=i, cfg=parse_cfg(m)) for i in mini], f"PARTE B {m}")
        t_modo = time.perf_counter() - t0
        t_acum += t_modo
        log(f"PARTE B: tiempo de pared de {m} = {t_modo:.0f} s ({len(mini)} puntos)")
        print(f"PARTE B {m}: {t_modo:.0f} s de pared", flush=True)
    pd.DataFrame(filas).sort_values(["etapa", "csv_origen", "fila_csv"]).to_csv(CSV_B, index=False)
    log(f"PARTE B: fin — {len(mini)} puntos x 3 modos, {t_acum:.0f} s de pared acumulados")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    etapa = sys.argv[1].lower() if len(sys.argv) > 1 else "todo"
    log(f"=== BENCHMARK {time.strftime('%Y-%m-%d %H:%M:%S')} — etapa '{etapa}' ===")
    if etapa in ("b", "todo") and not CSV_A.exists():
        sys.exit("Falta benchmark_filas.csv: corre antes la Parte A (etapa 'a').")
    if etapa in ("a", "todo"):
        parte_a()
    if etapa in ("b", "todo"):
        mejor, _, _ = mejor_cfg(pd.read_csv(CSV_A))
        log(f"Mejor configuracion MB seleccionada para la Parte B: {mejor}")
        parte_b(mejor)
    log(f"=== FIN etapa '{etapa}' ===")


if __name__ == "__main__":
    main()