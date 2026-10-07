"""M4b — convergencia del ranking: 300 vs 500 puntos (final_M4b §Diseño 3).

Misma métrica que la convergencia de M4 (`m4_arbol.convergencia`), pero el
corte es el ranking con los **300** puntos de M4 (`id_muestra < 300`) contra el
de los **500** de la unión: KS del RSA-KALINA (13 variables) y PRCC sobre η (10
variables), con el ρ de Spearman entre los dos rankings y el criterio
**ρ ≥ 0.9** del TASK_CONTEXT (`cumple_09`).
"""
from __future__ import annotations

from m4_arbol import _rangos, _rho  # reutiliza los dos auxiliares de M4
from m4_datos import VARS10, VARS13
from m4_pawn_prcc import filas_prcc
from m4_rsa import ks_de

CUMPLE = 0.9
CCONV = ["metrica", "variable", "valor_300", "valor_500", "rango_300",
         "rango_500", "rho_spearman", "cumple_09"]


def convergencia(filas: list, n_corte: int = 300) -> list:
    """KS (RSA KALINA) y PRCC(η) con los primeros `n_corte` y con todos."""
    sub = [f for f in filas
           if f["id_muestra"] is not None and f["id_muestra"] < n_corte]
    p500 = {r["variable"]: r["prcc"] for r in filas_prcc(filas)
            if r["salida"] == "eta"}
    p300 = {r["variable"]: r["prcc"] for r in filas_prcc(sub)
            if r["salida"] == "eta"}
    bloques = []
    pares = (("KS_KALINA", VARS13,
              [ks_de(sub, "KALINA", v) for v in VARS13],
              [ks_de(filas, "KALINA", v) for v in VARS13]),
             ("PRCC_eta", VARS10, [p300.get(v) for v in VARS10],
              [p500.get(v) for v in VARS10]))
    for metrica, vars_, v300, v500 in pares:
        rho, r300, r500 = _rho(v300, v500), _rangos(v300), _rangos(v500)
        cumple = rho is not None and rho >= CUMPLE
        for v, a, b, ra, rb in zip(vars_, v300, v500, r300, r500):
            bloques.append(dict(metrica=metrica, variable=v, valor_300=a,
                                valor_500=b, rango_300=ra, rango_500=rb,
                                rho_spearman=rho, cumple_09=cumple))
    return bloques
