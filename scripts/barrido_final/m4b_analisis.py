"""M4b — análisis sobre los 500 puntos (TASK_CONTEXT final_M4b, pasos 1 y 3).

Une los 300 de M4 (`resultados/2026-10-06_final_M4/m4_lhs.csv`) con los 200
nuevos (`m4b_lhs.csv`), repite el análisis de M4 con las mismas fórmulas y
parámetros —RSA con sus 4 separaciones, PAWN, PRCC, CART, convergencia y top-10—
escribiendo todo con prefijo `m4b_` en la carpeta de M4b, y añade el análisis
de presiones (`m4b_presiones.py`). La convergencia aquí compara el ranking de
**300** con el de **500** puntos (criterio ρ ≥ 0.9). Al final llama a
`m4b_reporte` para `REPORTE_M4b.md`.
"""
from __future__ import annotations

import sys, time  # noqa: E401,E402
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

from m4_analisis import N_MINIMO, grupos_chicos, resumen  # noqa: E402
from m4_arbol import CTOP, arbol, top_kalina  # noqa: E402
from m4_figuras import figuras  # noqa: E402
from m4_pawn_prcc import CPAWN, CPRCC, filas_pawn, filas_prcc  # noqa: E402
from m4_rsa import CRSA, filas_rsa  # noqa: E402
from m4b_convergencia import CCONV, convergencia  # noqa: E402
from m4b_datos import OUT, escribir, leer_union, redirigir  # noqa: E402
import m4b_presiones as pres  # noqa: E402

# Los módulos M4 escriben con su propio nombre `m4_*`; en la carpeta de M4b
# pasan a llamarse `m4b_*`.
PARES = (("m4_cart.txt", "m4b_cart.txt"),
         ("m4_cdf_kalina.png", "m4b_cdf_kalina.png"),
         ("m4_prcc_eta.png", "m4b_prcc_eta.png"),
         ("m4_rsa_ks.png", "m4b_rsa_ks.png"),
         ("m4_cart.png", "m4b_cart.png"))


def renombrar() -> None:
    """Los archivos `m4_*` escritos en la carpeta de M4b pasan a `m4b_*`."""
    for a, b in PARES:
        if (OUT / a).exists():
            (OUT / a).replace(OUT / b)
    print("salidas m4_* renombradas a m4b_*", flush=True)


def main() -> None:
    t0 = time.perf_counter()
    redirigir()
    filas = leer_union()
    if not filas:
        raise SystemExit(f"sin filas: falta {OUT / 'm4b_lhs.csv'}")
    res = resumen(filas)
    print(f"m4b_analisis | N={len(filas)} | KALINA="
          f'{res["conteos"].get("KALINA", 0)} | OUT={OUT}', flush=True)
    rsa = filas_rsa(filas)
    escribir(OUT, "m4b_rsa.csv", CRSA, rsa)
    pawn = filas_pawn(filas)
    escribir(OUT, "m4b_pawn.csv", CPAWN, pawn)
    prcc = filas_prcc(filas)
    escribir(OUT, "m4b_prcc.csv", CPRCC, prcc)
    cart = arbol(filas)
    conv = convergencia(filas)
    escribir(OUT, "m4b_convergencia.csv", CCONV, conv)
    top = top_kalina(filas)
    escribir(OUT, "m4b_top_kalina.csv", CTOP, top)
    figuras(filas, rsa, prcc, cart)
    renombrar()
    pdat = pres.main(filas)
    chicos = grupos_chicos(rsa)
    if chicos:
        print(f"AVISO: {len(chicos)} grupos con menos de {N_MINIMO} puntos "
              "(no se amplia el muestreo):", flush=True)
        for c in chicos[:10]:
            print(f"  - {c}", flush=True)
    import m4b_reporte as rep  # noqa: E402
    rep.generar(filas, rsa, pawn, prcc, cart, conv, top, pdat, chicos)
    print(f"m4b_analisis listo en {time.perf_counter() - t0:.0f} s -> {OUT}",
          flush=True)


if __name__ == "__main__":
    main()
