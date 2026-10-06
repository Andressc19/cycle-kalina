"""M4 — análisis sobre `m4_lhs.csv` (TASK_CONTEXT final_M4, paso 4).

Lee el CSV de la corrida, calcula RSA (4 separaciones × 13 variables), PAWN,
PRCC, CART, la convergencia del ranking y el top-10 KALINA, escribe sus CSV y
las cuatro figuras, y llama a `m4_reporte` para `REPORTE_M4.md`. Todo se
re-ejecuta sobre el CSV sin recalcular el ciclo. Si un grupo queda con menos
de 20 puntos NO se amplía el muestreo: se anota y se reporta (el director
decide).
"""
from __future__ import annotations

import sys, time  # noqa: E401,E402
from collections import Counter
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_RAIZ = _DIR.parents[1]
sys.path[:0] = [str(_RAIZ), str(_DIR)]

from m4_arbol import CCONV, CTOP, arbol, convergencia, top_kalina  # noqa: E402
from m4_datos import OUT, escribir, leer  # noqa: E402
from m4_figuras import figuras  # noqa: E402
from m4_pawn_prcc import CPAWN, CPRCC, filas_pawn, filas_prcc  # noqa: E402
from m4_rsa import CRSA, SEPS, filas_rsa  # noqa: E402

N_MINIMO = 20          # requisito mínimo por grupo (TASK_CONTEXT final_M4)


def resumen(filas: list) -> dict:
    """Conteos por clase, genuinos, espurios N2 y fuera de rango."""
    return dict(conteos=Counter(f["clasificacion"] for f in filas),
                n=len(filas),
                n_genuinos=sum(1 for f in filas if f["clasificacion"] in
                               ("KALINA", "CORREGIBLE", "INVIABLE")),
                n_N2=sum(1 for f in filas if f["convergio"] is True and
                         f["clasificacion"] == "NO_CONVERGIO"),
                n_fuera=sum(1 for f in filas if f["fuera_rango"] is True))


def grupos_chicos(rsa: list) -> list:
    """Los (separación, variable, grupo) con menos de N_MINIMO puntos."""
    return [f'{r["separacion"]}/{r["variable"]}: n_B={r["n_B"]}, '
            f'n_Bbar={r["n_Bbar"]}'
            for r in rsa if min(r["n_B"], r["n_Bbar"]) < N_MINIMO]


def main() -> None:
    t0 = time.perf_counter()
    filas = leer()
    if not filas:
        raise SystemExit(f"sin filas: falta {OUT / 'm4_lhs.csv'}")
    print(f"m4_analisis | N={len(filas)} | OUT={OUT}", flush=True)
    rsa = filas_rsa(filas)
    escribir("m4_rsa.csv", CRSA, rsa)
    pawn = filas_pawn(filas)
    escribir("m4_pawn.csv", CPAWN, pawn)
    prcc = filas_prcc(filas)
    escribir("m4_prcc.csv", CPRCC, prcc)
    cart = arbol(filas)
    conv = convergencia(filas)
    escribir("m4_convergencia.csv", CCONV, conv)
    top = top_kalina(filas)
    escribir("m4_top_kalina.csv", CTOP, top)
    figuras(filas, rsa, prcc, cart)
    chicos = grupos_chicos(rsa)
    if chicos:
        print(f"AVISO: {len(chicos)} grupos con menos de {N_MINIMO} puntos "
              "(no se amplia el muestreo):", flush=True)
        for c in chicos[:10]:
            print(f"  - {c}", flush=True)
    import m4_reporte as rep  # noqa: E402
    rep.generar(filas, rsa, pawn, prcc, cart, conv, top, chicos)
    print(f"m4_analisis listo en {time.perf_counter() - t0:.0f} s -> {OUT}",
          flush=True)


if __name__ == "__main__":
    main()
